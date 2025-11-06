# rag.py
from langchain_core.globals import set_verbose, set_debug
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain.schema.output_parser import StrOutputParser
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_core.prompts import ChatPromptTemplate
import torch
import logging
try:
    import intel_extension_for_pytorch as ipex
    INTEL_GPU_AVAILABLE = True
except ImportError:
    INTEL_GPU_AVAILABLE = False

try:
    import torch_rocm
    AMD_GPU_AVAILABLE = True
except ImportError:
    AMD_GPU_AVAILABLE = False

set_debug(True)
set_verbose(True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatPDF:
    """A class for handling PDF ingestion and question answering using RAG."""

    def __init__(self, llm_model: str = "gemma2:2b", embedding_model: str = "mxbai-embed-large"):
        """
        Initialize the ChatPDF instance with an LLM and embedding model.
        """
        # GPU detection and setup
        self.device = self._setup_device()
        model_kwargs = self._get_model_kwargs()

        self.model = ChatOllama(
            model=llm_model,
            **model_kwargs
        )
        self.embeddings = OllamaEmbeddings(
            model=embedding_model,
            **model_kwargs
        )

        self.model = ChatOllama(model=llm_model)
        self.embeddings = OllamaEmbeddings(model=embedding_model)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=100)
        self.prompt = ChatPromptTemplate.from_template(
            """
            You are a helpful assistant answering questions based on the uploaded document.
            Context:
            {context}
            
            Question:
            {question}
            
            Answer concisely and accurately in three sentences or less.
            """
        )
        self.vector_store = None
        self.retriever = None

    def _setup_device(self):
        """Setup the appropriate device based on availability."""
        if torch.cuda.is_available():
            if 'AMD' in torch.cuda.get_device_name(0):
                logger.info("AMD GPU detected (ROCm)")
                return torch.device("cuda")
            else:
                logger.info("NVIDIA GPU detected")
                return torch.device("cuda")
        elif INTEL_GPU_AVAILABLE and torch.xpu.is_available():
            logger.info("Intel GPU detected")
            ipex.enable_onednn_fusion(True)
            return torch.device("xpu")
        else:
            logger.info("No GPU detected, using CPU")
            return torch.device("cpu")

    def _get_model_kwargs(self):
        """Get model configuration based on available hardware."""
        kwargs = {"device": str(self.device)}
        
        if str(self.device) == "xpu":
            kwargs.update({
                "use_intel_gpu": True,
                "use_ipex": True
            })
        elif str(self.device) == "cuda":
            if 'AMD' in torch.cuda.get_device_name(0):
                kwargs.update({
                    "n_gpu_layers": -1,
                    "compute_dtype": "float32",  # AMD typically performs better with float32
                    "rocm_enabled": True
                })
            else:
                kwargs.update({
                    "n_gpu_layers": -1,
                    "compute_dtype": "float16"
                })
            
        return kwargs

    def ingest(self, pdf_file_path: str):
        """
        Ingest a PDF file, split its contents, and store the embeddings in the vector store.
        """
        logger.info(f"Starting ingestion for file: {pdf_file_path}")
        docs = PyPDFLoader(file_path=pdf_file_path).load()
        chunks = self.text_splitter.split_documents(docs)
        chunks = filter_complex_metadata(chunks)

        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory="chroma_db",
        )
        logger.info("Ingestion completed. Document embeddings stored successfully.")

    def ask(self, query: str, k: int = 5, score_threshold: float = 0.2):
        """
        Answer a query using the RAG pipeline.
        """
        if not self.vector_store:
            raise ValueError("No vector store found. Please ingest a document first.")

        if not self.retriever:
            self.retriever = self.vector_store.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={"k": k, "score_threshold": score_threshold},
            )

        logger.info(f"Retrieving context for query: {query}")
        retrieved_docs = self.retriever.invoke(query)

        if not retrieved_docs:
            return "No relevant context found in the document to answer your question."

        formatted_input = {
            "context": "\n\n".join(doc.page_content for doc in retrieved_docs),
            "question": query,
        }

        # Build the RAG chain
        chain = (
            RunnablePassthrough()  # Passes the input as-is
            | self.prompt           # Formats the input for the LLM
            | self.model            # Queries the LLM
            | StrOutputParser()     # Parses the LLM's output
        )

        logger.info("Generating response using the LLM.")
        logger.info(f"Formatted input: {formatted_input}")        
        return chain.invoke(formatted_input)

    def clear(self):
        """
        Reset the vector store and retriever.
        """
        logger.info("Clearing vector store and retriever.")
        self.vector_store = None
        self.retriever = None

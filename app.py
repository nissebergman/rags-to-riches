# app.py
import os
import tempfile
import time
import random
import datetime
import streamlit as st
from streamlit_chat import message
from rag import ChatPDF

# Initialize session state
if 'visitor_count' not in st.session_state:
    st.session_state['visitor_count'] = 1337
if 'last_visitor' not in st.session_state:
    st.session_state['last_visitor'] = datetime.datetime.now()
if 'messages' not in st.session_state:
    st.session_state["messages"] = []
if 'assistant' not in st.session_state:
    st.session_state["assistant"] = ChatPDF()

st.set_page_config(
    page_title="🔥 RAGtastic Chat Machine 🔥",
    page_icon="🌟",
    layout="wide"
)

# Classic 90's CSS
st.markdown("""
<style>
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0; }
        100% { opacity: 1; }
    }
    
    @keyframes rainbow {
        0% { color: red; }
        14% { color: orange; }
        28% { color: yellow; }
        42% { color: green; }
        57% { color: blue; }
        71% { color: indigo; }
        85% { color: violet; }
        100% { color: red; }
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }

    .main {
        background: black;
        background-image: url("data:image/gif;base64,R0lGODlhCgAKAIAAAAAAAP///yH5BAEAAAEALAAAAAAKAAoAAAIRjI+py+0Po5y02ouz3rz7VgAAOw==");
    }
    
    .stApp {
        background: #000000;
    }
    
    /* File Uploader Styling */
    [data-testid="stFileUploader"] {
        border: 3px solid #00ff00 !important;
        border-radius: 10px !important;
        padding: 20px !important;
        background: #000066 !important;
    }
    
    [data-testid="stFileUploaderDropzone"] {
        background: #000033 !important;
        border: 2px dashed #ff00ff !important;
        border-radius: 8px !important;
        padding: 20px !important;
    }
    
    .st-emotion-cache-1sct1q3, .st-emotion-cache-ycmcfb {
        color: #00ff00 !important;
        font-family: "Comic Sans MS", cursive !important;
    }
    
    .st-emotion-cache-jzs692 {
        background: linear-gradient(45deg, #ff00ff, #00ffff) !important;
        color: white !important;
        border: 2px solid #00ff00 !important;
        font-family: "Comic Sans MS", cursive !important;
        text-shadow: 1px 1px #000000 !important;
        animation: blink 2s infinite !important;
    }
    
    /* Fix SVG colors in file uploader */
    [data-testid="stFileUploaderDropzone"] svg {
        fill: #00ff00 !important;
        animation: float 3s ease-in-out infinite !important;
    }

    /* Center file uploader */
    [data-testid="stFileUploader"] > section[role="presentation"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
    }
    
    .title {
        font-family: "Comic Sans MS", cursive;
        text-align: center;
        color: #00ff00;
        text-shadow: 2px 2px #ff00ff;
        animation: rainbow 5s linear infinite;
    }
    
    .counter {
        font-family: "Courier New", monospace;
        color: #ffff00;
        text-shadow: 1px 1px #ff0000;
        background: #000066;
        padding: 5px;
        border: 3px solid #00ff00;
        border-radius: 5px;
        animation: blink 2s linear infinite;
    }
    
    .spinning-image {
        animation: spin 5s linear infinite;
    }
    
    .chat-container {
        border: 3px solid #00ff00;
        border-radius: 10px;
        padding: 10px;
        background: rgba(0, 0, 0, 0.8);
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #ff00ff, #00ffff);
        color: white !important;
        border: 2px solid #00ff00 !important;
        font-family: "Comic Sans MS", cursive !important;
        text-shadow: 1px 1px #000000;
    }
    
    .stTextInput > div > div > input {
        background-color: #000066 !important;
        color: #00ff00 !important;
        border: 2px solid #00ff00 !important;
        font-family: "Courier New", monospace !important;
    }
    }
    
    div[data-testid="stMarkdownContainer"] {
        color: #00ff00 !important;
    }
</style>
""", unsafe_allow_html=True)


def display_messages():
    """Display the chat history."""
    
    # Update visitor stats
    st.session_state['visitor_count'] += 1
    st.session_state['last_visitor'] = datetime.datetime.now()
    
    # 90's style header with spinning Earth
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://web.archive.org/web/20090830055557/http://geocities.com/Pentagon/Quarters/9847/spinning_earth.gif" 
                class="spinning-image" style="width: 80px;">
            <h1 class="title">🌟 RAGtastic Chat Machine 🌟</h1>
            <div style="display: flex; justify-content: space-around; margin: 10px 0;">
                <div class="counter">
                    👥 Visitors: {st.session_state['visitor_count']}
                </div>
                <div class="counter">
                    🕒 Last Visit: {st.session_state['last_visitor'].strftime('%H:%M:%S')}
                </div>
            </div>
            <marquee scrollamount="5" style="color: #ff0000; font-weight: bold;">
                🔥 HOT! NEW! CHAT WITH YOUR DOCUMENTS USING AI! AWESOME! RADICAL! 🔥
            </marquee>
            <div style="margin: 10px 0;">
                <img src="https://web.archive.org/web/20091027143701/http://geocities.com/Hollywood/Hills/9628/line.gif" 
                    style="width: 100%; height: 10px;">
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Chat messages
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for i, (msg, is_user) in enumerate(st.session_state["messages"]):
        if is_user:
            message(f"😎 {msg}", is_user=is_user, key=str(i))
        else:
            message(f"🤖 {msg}", is_user=is_user, key=str(i))
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.session_state["thinking_spinner"] = st.empty()


def process_input():
    """Process the user input and generate an assistant response."""
    if st.session_state["user_input"] and len(st.session_state["user_input"].strip()) > 0:
        user_text = st.session_state["user_input"].strip()
        with st.session_state["thinking_spinner"], st.spinner("Thinking..."):
            try:
                agent_text = st.session_state["assistant"].ask(
                    user_text,
                    k=st.session_state["retrieval_k"],
                    score_threshold=st.session_state["retrieval_threshold"],
                )
            except ValueError as e:
                agent_text = str(e)

        st.session_state["messages"].append((user_text, True))
        st.session_state["messages"].append((agent_text, False))


def read_and_save_file():
    """Handle file upload and ingestion."""
    st.session_state["assistant"].clear()
    st.session_state["messages"] = []
    st.session_state["user_input"] = ""

    for file in st.session_state["file_uploader"]:
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tf.write(file.getbuffer())
            file_path = tf.name

        with st.session_state["ingestion_spinner"], st.spinner(f"Ingesting {file.name}..."):
            t0 = time.time()
            st.session_state["assistant"].ingest(file_path)
            t1 = time.time()

        st.session_state["messages"].append(
            (f"Ingested {file.name} in {t1 - t0:.2f} seconds", False)
        )
        os.remove(file_path)


def page():
    """Main app page layout."""
    display_messages()  # This now includes our awesome 90's header
    
    # File upload section with 90's style
    st.markdown("""
        <div style="text-align: center; margin: 20px 0;">
            <img src="https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExcTExZ3g4ZDNkZTYxa2NoOHppNzM2MDM1OGd1a2x3dmV4Y2I4OWNoMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/k1FFupJJmn8AB7Y9UO/giphy.gif"
                class="spinning-image" style="width: 50px;">
            <h2 class="title">📂 UPLOAD YOUR DOCUMENTS! 📂</h2>
            <img src="https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExcTExZ3g4ZDNkZTYxa2NoOHppNzM2MDM1OGd1a2x3dmV4Y2I4OWNoMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/k1FFupJJmn8AB7Y9UO/giphy.gif"
                class="spinning-image" style="width: 50px; transform: scaleX(-1);">
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown('<div style="display: flex; justify-content: center; width: 100%;">', unsafe_allow_html=True)
        st.file_uploader(
            "Upload a PDF document",
            type=["pdf"],
            key="file_uploader",
            on_change=read_and_save_file,
            label_visibility="collapsed",
            accept_multiple_files=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style="text-align: center;">
                <img src="https://web.archive.org/web/20090830031249/http://geocities.com/Hollywood/Lot/6085/new2.gif"
                    style="width: 100px;">
            </div>
        """, unsafe_allow_html=True)

    st.session_state["ingestion_spinner"] = st.empty()

    # Retrieval settings with 90's style
    st.markdown("""
        <div style="text-align: center; margin: 20px 0;">
            <img src="https://web.archive.org/web/20090829175830/http://geocities.com/Hollywood/Hills/9628/line.gif" 
                style="width: 100%; height: 10px;">
            <h2 class="title">🎮 CONTROL CENTER 🎮</h2>
            <marquee behavior="alternate" scrollamount="3" style="color: #ffff00;">
                Adjust your settings here! Maximum power! 🚀
            </marquee>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state["retrieval_k"] = st.slider(
        "Number of Retrieved Results (k)", min_value=1, max_value=10, value=5
    )
    with col2:
        st.session_state["retrieval_threshold"] = st.slider(
            "Similarity Score Threshold", min_value=0.0, max_value=1.0, value=0.2, step=0.05
        )
    
    # Message input with 90's style
    st.markdown("""
        <div style="text-align: center; margin: 20px 0;">
            <img src="https://web.archive.org/web/20090829175830/http://geocities.com/Hollywood/Hills/9628/line.gif" 
                style="width: 100%; height: 10px;">
            <h2 class="title">💬 START CHATTING! 💬</h2>
            <div style="display: flex; justify-content: center; gap: 10px;">
                <img src="https://web.archive.org/web/20090830031249/http://geocities.com/Hollywood/Lot/6085/flamebar.gif" 
                    style="height: 30px;">
                <img src="https://web.archive.org/web/20090830031249/http://geocities.com/Hollywood/Lot/6085/flamebar.gif" 
                    style="height: 30px; transform: scaleX(-1);">
            </div>
        </div>
    """, unsafe_allow_html=True)
    # Input and clear chat in columns
    col1, col2 = st.columns([4, 1])
    with col1:
        st.text_input("Your message here...", key="user_input", on_change=process_input)
    with col2:
        if st.button("🔄 Clear Chat 🔄"):
            st.session_state["messages"] = []
            st.session_state["assistant"].clear()
    
    # Footer with 90's style
    st.markdown("""
        <div style="text-align: center; margin-top: 30px;">
            <img src="https://web.archive.org/web/20090829175830/http://geocities.com/Hollywood/Hills/9628/line.gif" 
                style="width: 100%; height: 10px;">
            <div style="margin: 10px 0;">
                <img src="https://web.archive.org/web/20090830031249/http://geocities.com/Hollywood/Lot/6085/ie_animated.gif" 
                    style="height: 31px;">
                <span style="color: #ffff00; font-family: 'Courier New', monospace;">
                    Best viewed in Internet Explorer 4.0 or Netscape Navigator 3.0
                </span>
                <img src="https://web.archive.org/web/20090830031249/http://geocities.com/Hollywood/Lot/6085/ns_animated.gif" 
                    style="height: 31px;">
            </div>
            <marquee direction="right" scrollamount="3" style="color: #00ff00;">
                🚧 Under Construction! More awesome features coming soon! 🚧
            </marquee>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    page()

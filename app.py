import os
import streamlit as st

from src.chatbot import ask_question
from src.pdf_loader import load_pdfs
from src.vector_store import create_vector_store

# ==========================
# PAGE CONFIG
# ==========================
st.set_page_config(
    page_title="College Notes Chatbot",
    page_icon="📚",
    layout="wide"
)

# ==========================
# INITIALIZE SESSION STATE
# ==========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "vector_store_ready" not in st.session_state:
    st.session_state.vector_store_ready = False

# ==========================
# LOAD CSS
# ==========================
with open("assets/style.css") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

# ==========================
# SIDEBAR
# ==========================
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-title">
            📚 College Notes Chatbot
        </div>
        <div class="sidebar-subtitle">
            Your AI Study Companion
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### 📤 Upload Notes")
    uploaded_files = st.file_uploader(
        "Upload PDF Notes",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:
        # Only show the button if we haven't successfully processed these files yet
        if st.button("📥 Process PDFs"):
            with st.spinner("Processing and indexing PDFs..."):
                os.makedirs("uploaded_notes", exist_ok=True)
                file_paths = []

                for file in uploaded_files:
                    file_path = os.path.join("uploaded_notes", file.name)
                    with open(file_path, "wb") as f:
                        f.write(file.getbuffer())
                    file_paths.append(file_path)

                # Load and chunk documents
                docs = load_pdfs(file_paths)
                
                # Create Vector DB (Ensure this function saves locally or updates a global instance)
                create_vector_store(docs)
                
                # Flip the state flag to True
                st.session_state.vector_store_ready = True
                st.balloons()
                st.success(f"{len(file_paths)} PDFs processed successfully!")

    st.markdown("---")

    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ==========================
# HERO SECTION
# ==========================
st.markdown(
    """
    <div class="hero-card">
        <h1>🤖 College Notes Chatbot</h1>
        <p>Ask any question from your uploaded notes and get instant answers.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ==========================
# METRICS
# ==========================
pdf_count = len(uploaded_files) if uploaded_files else 0
db_status = "Ready ✅" if st.session_state.vector_store_ready else "Empty ❌"

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📚 PDFs Uploaded", pdf_count)
with col2:
    st.metric("🧠 Vector DB Status", db_status)
with col3:
    st.metric("🤖 Model", "Gemini")

# ==========================
# DISPLAY CHAT HISTORY
# ==========================
# We display old messages FIRST so the input box stays clean below it
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Re-render sources for historical assistant messages if they exist
        if message["role"] == "assistant" and "sources" in message:
            with st.expander("📄 Sources Used"):
                for src in message["sources"]:
                    st.info(f"📁 {src['filename']} | 📄 Page {src['page']}")

# ==========================
# WELCOME MESSAGE
# ==========================
if len(st.session_state.messages) == 0:
    st.info(
        """
        👋 Welcome!
        
        Upload your PDF notes on the sidebar, click **Process PDFs**, and ask questions such as:
        * • What is DBMS?
        * • Explain Deadlock
        * • What is Normalization?
        """
    )

# ==========================
# CHAT INPUT & LOGIC
# ==========================
question = st.chat_input("Ask a question from your notes...")

if question:
    # 1. Guard rail checking if DB is populated
    if not st.session_state.vector_store_ready:
        st.error("⚠️ Please upload and process your PDF notes before asking questions!")
    else:
        # 2. Append and display User Message immediately
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        # 3. Generate Assistant Response
        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching Notes..."):
                answer, docs = ask_question(question)
            
            st.markdown(answer)
            
            # Format sources to save neatly into session state
            formatted_sources = []
            if docs:
                with st.expander("📄 Sources Used"):
                    shown = set()
                    for doc in docs:
                        filename = doc.metadata.get("source", "").split("/")[-1]
                        page = doc.metadata.get("page", 0) + 1
                        key = (filename, page)
                        
                        if key not in shown:
                            shown.add(key)
                            formatted_sources.append({"filename": filename, "page": page})
                            st.info(f"📁 {filename} | 📄 Page {page}")
            
            # 4. Save Assistant Response along with its specific sources to state
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": formatted_sources
            })
            
            # Force a rerun to clean up layout artifacts and lock in history placement
            st.rerun()
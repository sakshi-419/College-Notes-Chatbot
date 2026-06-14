from dotenv import load_dotenv
import streamlit as st
import os

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings
)

load_dotenv()

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    st.secrets.get("GEMINI_API_KEY", None)
)

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found")

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=GEMINI_API_KEY
)

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.2
)


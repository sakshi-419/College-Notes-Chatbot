from dotenv import load_dotenv
import streamlit as st
import os

load_dotenv()

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    st.secrets.get("GEMINI_API_KEY", None)
)
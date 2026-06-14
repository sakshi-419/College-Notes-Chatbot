from src.pdf_loader import load_pdfs
from src.vector_store import create_vector_store

docs = load_pdfs([
    "data/dbms.pdf",
    "data/c_notes.pdf",
    "data/os-notes.pdf"
])

vectorstore = create_vector_store(docs)

print("Vector Store Created Successfully!")
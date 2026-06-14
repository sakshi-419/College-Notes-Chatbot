from langchain_community.vectorstores import FAISS
from src.config import embeddings, llm


def load_vector_store():
    return FAISS.load_local(
        "faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )


def ask_question(question):

    vectorstore = load_vector_store()

    # Retrieve chunks with scores
    results = vectorstore.similarity_search_with_score(
        question,
        k=5
    )

    docs = []

    for doc, score in results:

        # Adjust threshold if needed
        if score < 1.5:
            docs.append(doc)

    # If nothing relevant found
    if not docs:

        return (
            "I could not find this information in the uploaded notes.",
            []
        )

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    prompt = f"""
You are an AI study assistant.

Use ONLY the information present in the provided context.

Rules:
1. Answer only from the context.
2. Do not make up information.
3. If the answer is not present in the context, reply exactly:

I could not find this information in the uploaded notes.

4. Keep answers concise and student friendly.

Context:
{context}

Question:
{question}

Answer:
"""

    response = llm.invoke(prompt)

    answer = response.content.strip()

    return answer, docs
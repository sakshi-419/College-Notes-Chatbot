from src.config import llm

response = llm.invoke("Hello")
print(response.content)
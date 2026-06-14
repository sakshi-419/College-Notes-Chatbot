from src.chatbot import ask_question

while True:
    question = input("\nAsk: ")

    if question.lower() == "exit":
        break

    answer = ask_question(question)

    print("\nAnswer:")
    print(answer)
from app.rag.query import search_documents


def ask_question(question):

    docs = search_documents(question)

    response = ""

    for doc in docs:
        response += doc.page_content + "\n"

    return response
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

CHROMA_PATH = "chroma_db"


def create_vector_store(documents):

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectordb = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )

    vectordb.persist()

    return vectordb
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

all_docs = []

pdf_folder = "data/pdf"

for filename in os.listdir(pdf_folder):

    if filename.endswith(".pdf"):

        pdf_path = os.path.join(pdf_folder, filename)

        print(f"Loading: {pdf_path}")

        loader = PyPDFLoader(pdf_path)
        docs = loader.load()

        all_docs.extend(docs)

print(f"Total documents: {len(all_docs)}")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectordb = Chroma.from_documents(
    documents=all_docs,
    embedding=embeddings,
    persist_directory="chroma_db"
)

vectordb.persist()

print("Chroma DB Created")
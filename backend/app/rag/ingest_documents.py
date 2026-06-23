from app.rag.load_documents import load_documents
from app.rag.chunker import chunk_text
from app.rag.vector_store import collection
import hashlib

documents = load_documents()

chunks = []
ids = []
metadatas = []

for source_type in ["document", "faq_file"]:

    collection.delete(
        where={"source_type": source_type}
    )

for doc_index, doc in enumerate(documents):

    content = doc.page_content.strip()

    if not content:
        continue

    source_type = doc.metadata.get(
        "source_type",
        "document"
    )

    source = doc.metadata.get(
        "source",
        "uploaded_document"
    )

    for chunk_index, chunk in enumerate(chunk_text(content)):

        chunk = chunk.strip()

        if not chunk:
            continue

        chunk_id = hashlib.sha1(
            f"{source}:{doc_index}:{chunk_index}:{chunk}".encode("utf-8")
        ).hexdigest()

        chunks.append(chunk)
        ids.append(f"{source_type}:{chunk_id}")
        metadatas.append({
            **doc.metadata,
            "source_type": source_type,
            "chunk_index": chunk_index
        })

print("Chunks:", len(chunks))

if len(chunks) > 0:

    collection.upsert(
        documents=chunks,
        ids=ids,
        metadatas=metadatas
    )

    print("Documents stored successfully")

else:

    print("No documents found")

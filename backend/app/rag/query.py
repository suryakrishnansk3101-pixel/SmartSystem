from app.rag.vector_store import collection
from app.models import FAQ
import os

DISTANCE_THRESHOLD = float(
    os.getenv(
        "KNOWLEDGE_DISTANCE_THRESHOLD",
        "0.6"
    )
)
RESULT_LIMIT = 6


def _faq_document(faq):

    return (
        f"FAQ Question: {faq.question}\n"
        f"FAQ Answer: {faq.answer}"
    )


def sync_faqs_to_vector_store(db):

    faqs = db.query(FAQ).all()
    current_ids = {
        f"faq:{faq.faq_id}"
        for faq in faqs
    }

    try:
        existing = collection.get(
            where={"source_type": "faq"},
            include=[]
        )

        stale_ids = [
            faq_id
            for faq_id in existing.get("ids", [])
            if faq_id not in current_ids
        ]

        if stale_ids:
            collection.delete(ids=stale_ids)

    except Exception as exc:
        print("FAQ vector cleanup skipped:", exc)

    if not faqs:
        return

    collection.upsert(
        ids=[f"faq:{faq.faq_id}" for faq in faqs],
        documents=[_faq_document(faq) for faq in faqs],
        metadatas=[
            {
                "source_type": "faq",
                "faq_id": faq.faq_id,
                "question": faq.question,
                "answer": faq.answer,
                "category": faq.category or "",
                "department": faq.department or ""
            }
            for faq in faqs
        ]
    )


def _distance_to_confidence(distance):

    return max(
        0.0,
        min(
            1.0,
            1.0 - (distance / DISTANCE_THRESHOLD)
        )
    )


def _format_retrieved_chunks(results):

    documents = results.get("documents", [[]])[0] or []
    distances = results.get("distances", [[]])[0] or []
    metadatas = results.get("metadatas", [[]])[0] or []
    ids = results.get("ids", [[]])[0] or []

    chunks = []

    for index, document in enumerate(documents):

        distance = distances[index] if index < len(distances) else None
        metadata = metadatas[index] if index < len(metadatas) else {}

        chunks.append({
            "id": ids[index] if index < len(ids) else "",
            "text": document,
            "distance": distance,
            "confidence": (
                _distance_to_confidence(distance)
                if distance is not None
                else 0.0
            ),
            "source_type": metadata.get("source_type", "unknown"),
            "metadata": metadata
        })

    return chunks

def search_documents(question):

    results = collection.query(
        query_texts=[question],
        n_results=RESULT_LIMIT,
        include=[
            "documents",
            "distances",
            "metadatas"
        ]
    )

    print("RAG Results:", results)

    return results


def search_knowledge_base(question, db):

    sync_faqs_to_vector_store(db)

    print("AI Retrieval Debug - User Question:", question)

    results = search_documents(question)
    chunks = _format_retrieved_chunks(results)

    print("AI Retrieval Debug - Retrieved Chunks:")

    for chunk in chunks:
        print({
            "source_type": chunk["source_type"],
            "distance": chunk["distance"],
            "confidence": round(chunk["confidence"], 4),
            "text": chunk["text"][:300]
        })

    relevant_chunks = [
        chunk
        for chunk in chunks
        if (
            chunk["distance"] is not None
            and chunk["distance"] <= DISTANCE_THRESHOLD
        )
    ]

    if not relevant_chunks:
        print("AI Retrieval Debug - Final Answer Source: none")
        return {
            "found": False,
            "answer": None,
            "chunks": chunks
        }

    relevant_chunks.sort(
        key=lambda x: x["distance"]
    )

    best_chunk = relevant_chunks[0]
    metadata = best_chunk["metadata"]

    if best_chunk["source_type"] == "faq":
        answer = metadata.get("answer") or best_chunk["text"]
        source = "FAQ database"
        
    elif best_chunk["source_type"] == "faq_file":
        answer = best_chunk["text"]
        source = "FAQ file"
    else:
        answer = best_chunk["text"]
        source = "knowledge document"

    print("AI Retrieval Debug - Similarity Scores:", [
        {
            "source_type": chunk["source_type"],
            "distance": chunk["distance"],
            "confidence": round(chunk["confidence"], 4)
        }
        for chunk in chunks
    ])
    print("AI Retrieval Debug - Final Answer Source:", source)

    return {
        "found": True,
        "answer": answer,
        "source": source,
        "confidence": best_chunk["confidence"],
        "chunks": chunks
    }

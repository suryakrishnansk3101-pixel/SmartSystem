import faiss
import pickle

from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

index = faiss.read_index("faq_index.faiss")

with open("faq_data.pkl", "rb") as f:
    faq_data = pickle.load(f)


def search_faq(user_question):

    vector = model.encode([user_question])

    distances, indices = index.search(vector, k=1)

    score = distances[0][0]

    print("Question:", user_question)
    print("Distance:", score)

    if score > 0.50:

        return None

    result = faq_data.iloc[indices[0][0]]

    return {
        "question": result["question"],
        "answer": result["answer"]
    }
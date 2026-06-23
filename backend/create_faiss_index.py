import pandas as pd
import faiss
import pickle
from sentence_transformers import SentenceTransformer

df = pd.read_csv("enterprise_agent_qa.csv")

model = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = model.encode(
    df["question"].tolist(),
    convert_to_numpy=True
)

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

faiss.write_index(index, "faq_index.faiss")

with open("faq_data.pkl", "wb") as f:
    pickle.dump(df, f)

print("FAISS index created successfully!")
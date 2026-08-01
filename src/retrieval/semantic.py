# This pipeline converts a text query into an embedding using SentenceTransformer and retrieves matching descriptions from Qdrant.

import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, "../../.env"))

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
text_model = SentenceTransformer('all-MiniLM-L6-v2')

def search_semantic_text(query_text: str, top_k: int = 2):
    """
    Converts text query into a 384-d vector and searches Qdrant's 'tourism_text' collection.
    """
    # generate txt embedding vector
    query_vector = text_model.encode(query_text).tolist()

    search_results = qdrant_client.query_points(
        collection_name="tourism_text",
        query=query_vector,
        limit=top_k
    ).points

    retrieved_docs = []
    for hit in search_results:
        retrieved_docs.append({
            "attraction_id": hit.payload.get("attraction_id"),
            "text": hit.payload.get("text"),
            "similarity_score": round(hit.score, 4)
        })
    return retrieved_docs
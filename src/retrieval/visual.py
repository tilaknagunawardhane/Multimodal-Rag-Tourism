import os
from PIL import Image
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from transformers import CLIPProcessor, CLIPModel

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, "../../.env"))

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def search_visual_similarity(image_input, top_k: int = 2):
    """
    accepts a PIL Image object-> encodes it using CLIP -> and searches 'tourism_images'.
    """
    if isinstance(image_input, str):
        image = Image.open(image_input)
    else:
        image = image_input

    # Generate image vector
    inputs = clip_processor(images=image, return_tensors="pt")
    image_features = clip_model.get_image_features(**inputs)

    # Compatibility check for transformers wrapper objects
    if not hasattr(image_features, 'detach'):
        image_features = image_features.pooler_output
        if image_features.shape[-1] != 512 and hasattr(clip_model, 'visual_projection'):
            image_features = clip_model.visual_projection(image_features)

    query_vector = image_features.detach().numpy()[0].tolist()

    search_results = qdrant_client.query_points(
        collection_name="tourism_images",
        query=query_vector,
        limit=top_k
    ).points

    retrieved_images = []
    for hit in search_results:
        retrieved_images.append({
            "attraction_id": hit.payload.get("attraction_id"),
            "image_filename": hit.payload.get("image_filename"),
            "similarity_score": round(hit.score, 4)
        })
    return retrieved_images
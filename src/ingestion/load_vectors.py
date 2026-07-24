import os
import json
import uuid
from PIL import Image
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from sentence_transformers import SentenceTransformer
from transformers import CLIPProcessor, CLIPModel

# Load environment variables
load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# Dynamically construct paths relative to this script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(SCRIPT_DIR, "../../data/text_descriptions.json")
IMG_DIR = os.path.join(SCRIPT_DIR, "../../data/images")

def get_uuid(text):
    # Qdrant requires UUIDs or integers for point IDs. We generate a consistent UUID based on the string ID.
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, text))

def load_vector_data():
    print("Connecting to Qdrant Cloud...")
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

    # 1. Recreate Collections (384 dims for Text, 512 dims for Images)
    print("Creating collections...")
    client.recreate_collection(
        collection_name="tourism_text",
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )
    client.recreate_collection(
        collection_name="tourism_images",
        vectors_config=VectorParams(size=512, distance=Distance.COSINE)
    )

    # 2. Ingest Text Descriptions using SentenceTransformers
    print("Loading text embedding model (all-MiniLM-L6-v2)...")
    text_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        text_data = json.load(f)

    text_points = []
    for item in text_data:
        vector = text_model.encode(item["description"]).tolist()  #translate the English paragraph into a vector
        text_points.append(
            PointStruct( #packages the data into Qdrant's required format. It includes the UUID, the vector itself, and a payload
                id=get_uuid(item["attraction_id"]),
                vector=vector,
                payload={"attraction_id": item["attraction_id"], "text": item["description"]}
            )
        )
    
    client.upsert(collection_name="tourism_text", points=text_points)
    print(f"✅ Upserted {len(text_points)} text descriptions into 'tourism_text'.")

    # 3. Ingest Images using CLIP
    print("Loading CLIP image embedding model...")
    #map images and text into the same mathematical space
    clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    image_points = []
    for img_file in os.listdir(IMG_DIR):
        if img_file.endswith(('.jpg', '.png')):
            # The filename format is T001_1.jpg, so we split by '_' to get the attraction_id
            attraction_id = img_file.split('_')[0]
            img_path = os.path.join(IMG_DIR, img_file)
            
            # Process image and generate vector
            image = Image.open(img_path)
            inputs = clip_processor(images=image, return_tensors="pt")
            image_features = clip_model.get_image_features(**inputs)

            # If the transformers library returns a wrapper object instead of a raw tensor, extract it:
            if not hasattr(image_features, 'detach'):
                image_features = image_features.pooler_output
                # If the raw output is 768 dimensions, project it to 512 dimensions for Qdrant
                if image_features.shape[-1] != 512 and hasattr(clip_model, 'visual_projection'):
                    image_features = clip_model.visual_projection(image_features)
            # ----------------------

            vector = image_features.detach().numpy()[0].tolist()

            image_points.append(
                PointStruct(
                    id=get_uuid(img_file),
                    vector=vector,
                    payload={"attraction_id": attraction_id, "image_filename": img_file}
                )
            )

    if image_points:
        client.upsert(collection_name="tourism_images", points=image_points)
        print(f"✅ Upserted {len(image_points)} image embeddings into 'tourism_images'.")
    else:
        print("⚠️ No images found to process.")

if __name__ == "__main__":
    load_vector_data()
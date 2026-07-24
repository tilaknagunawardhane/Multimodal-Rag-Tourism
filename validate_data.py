import csv
import json
import os

# File paths
CSV_PATH = "data/tourism_data.csv"
JSON_PATH = "data/text_descriptions.json"
IMG_DIR = "data/images"

def validate_dataset():
    # 1. Read IDs from CSV
    csv_ids = set()
    with open(CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            csv_ids.add(row['attraction_id'])
            
    # 2. Read IDs from JSON
    json_ids = set()
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        text_data = json.load(f)
        for item in text_data:
            json_ids.add(item['attraction_id'])
            
    # 3. Read IDs from Images
    image_files = os.listdir(IMG_DIR)
    img_ids = set([img.split('_')[0] for img in image_files if img.endswith(('.jpg', '.png'))])

    # 4. Compare
    print(f"IDs in CSV: {csv_ids}")
    print(f"IDs in JSON: {json_ids}")
    print(f"IDs in Images: {img_ids}")
    
    if csv_ids == json_ids and csv_ids.issubset(img_ids):
        print("\n✅ Success! All data is perfectly aligned and ready for Phase 2.")
    else:
        print("\n❌ Error: Mismatched IDs detected. Please ensure every ID in the CSV has a matching text description and image.")

if __name__ == "__main__":
    validate_dataset()
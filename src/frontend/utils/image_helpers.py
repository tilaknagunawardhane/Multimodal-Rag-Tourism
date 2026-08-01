import os
import requests
from dotenv import load_dotenv

# Load environment variables
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, "../../../.env"))

SUPABASE_IMAGE_BASE_URL = os.getenv("SUPABASE_IMAGE_BASE_URL", "").rstrip("/") + "/"

def get_images_for_attractions(attraction_ids, root_dir: str = None):
    """
    Constructs and verifies public Supabase CDN URLs for the given attraction IDs.
    Does not require local file lookups or database re-ingestion.
    """
    if not SUPABASE_IMAGE_BASE_URL.startswith("http"):
        print("[Image Helper Warning]: SUPABASE_IMAGE_BASE_URL is missing or invalid in .env")
        return []

    found_image_urls = []
    
    for aid in attraction_ids:
        # Check for multiple trail numbers (e.g., M001_1, M001_2)
        for trail in ["1", "2"]:
            
            # Optimization: If we already have 4 images, stop making network requests
            if len(found_image_urls) >= 4:
                break
                
            # We check common extensions
            for ext in ["jpg", "png", "jpeg"]:
                img_url = f"{SUPABASE_IMAGE_BASE_URL}{aid}_{trail}.{ext}"
                
                try:
                    # Use a HEAD request to check if the file exists without downloading the actual image payload
                    response = requests.head(img_url, timeout=3)
                    
                    if response.status_code == 200:
                        found_image_urls.append(img_url)
                        break  # Found the correct extension for this trail number, break out of the extension loop
                        
                except requests.RequestException as e:
                    print(f"[Image Helper Error]: Failed to verify {img_url} - {e}")
                    continue

    # Debug step
    print("\nFound Valid Image URL Links:\n")
    for image_url in found_image_urls:
        print(f"{image_url}\n")
    
    return found_image_urls[:4]
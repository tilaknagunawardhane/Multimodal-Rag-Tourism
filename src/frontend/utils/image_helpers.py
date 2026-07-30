import os

def get_images_for_attractions(attraction_ids, root_dir: str):
    """
    Finds matching local image files for a set of attraction IDs.
    """
    img_dir = os.path.join(root_dir, "data", "images")
    found_images = []
    
    if os.path.exists(img_dir):
        for img_file in os.listdir(img_dir):
            if any(img_file.startswith(aid + "_") for aid in attraction_ids):
                found_images.append(os.path.join(img_dir, img_file))
                
    return found_images[:4]  # Limit to 4 images to maintain a clean layout
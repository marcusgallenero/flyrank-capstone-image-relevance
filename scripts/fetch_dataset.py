import os
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY") 
BASE_URL = "https://api.pexels.com/v1/search"
CATEGORIES = ["moose", "bear", "red fox", "wolf", "dog"]
IMAGES_PER_CATEGORY = 10
OUTPUT_DIR = Path("data/images")

def search_photos(query: str, per_page: int) -> list[dict]:
    """Call Pexels search endpoint, return list of photo objects"""
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": per_page}

    try:
        response = requests.get(BASE_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Pexels request failed for '{query}': {e}")
        return []

    data = response.json()
    return data["photos"]

def download_image(url: str, save_path: Path) -> bool:
    """Download an image from a URL and save it to disk"""
    try:    
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except requests.RequestException as e:
        print(f"Failed to download {url}: {e}")
        return False

def gather_category(category: str, num_images: int) -> int:
    """Search and download images for one category"""
    category_name = category.replace(" ", "_")

    category_dir = OUTPUT_DIR / category_name
    category_dir.mkdir(parents=True, exist_ok=True)
    photos = search_photos(category, num_images)

    success_count = 0
    for i, photo in enumerate(photos, start=1):
        url = photo["src"]["medium"]
        filename = f"{category_name}_{i:02d}.jpg"
        save_path = category_dir / filename

        if download_image(url, save_path):
            success_count += 1

    return success_count

def main():
    if not PEXELS_API_KEY:
        raise RuntimeError("PEXELS_API_KEY not set")

    results = {}

    for category in CATEGORIES:
        count = gather_category(category, IMAGES_PER_CATEGORY)
        results[category] = count
        print(f"{category}: {count}/{IMAGES_PER_CATEGORY} downloaded")

    images_saved = sum(results.values())
    total_expected = len(CATEGORIES) * IMAGES_PER_CATEGORY
    print(f"Total: {images_saved}/{total_expected} saved")

if __name__ == "__main__":
    main()
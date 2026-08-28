import time
from pathlib import Path
from app.vision import tag_image

IMAGES_DIR = Path("data/images")
MAX_RETRIES = 3

def tag_with_retries(image_path: str):
    """Try tag_images up to MAX_RETRIES times, with backoff between attempts"""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return tag_image(image_path)
        except Exception as e:
            if attempt == MAX_RETRIES:
                print(f"Failed after {MAX_RETRIES} attempts: {image_path}: {e}\n")
                return
            time.sleep(2 ** attempt)

def tag_dataset():
    """loop over every image and tag it"""
    results = []
    failures = []

    for image_path in IMAGES_DIR.rglob("*.jpg"):
        tagged_image = tag_with_retries(image_path)
        if not tagged_image:
            failures.append(image_path)
        else:
            results.append(tagged_image)
        time.sleep(5)
    return results, failures 

if __name__ == "__main__":
    results, failures = tag_dataset()
    print(f"Tagged: {len(results)}\nFailed: {len(failures)}")
import json
from pathlib import Path
from app.load_metadata import load_metadata

IMAGES_DIR = Path("data/images")
METADATA_FILE = Path("data/metadata.json")


def tag_with_fallback(image_path: Path):
    """Look up metadata for an image"""
    try:
        return load_metadata(image_path)
    except KeyError:
        print(f"No metadata found for: {image_path}")
        return None
    except Exception as e:
        print(f"Invalid metadata for {image_path}:{e}")
        return None


def tag_dataset():
    """loop over every image and tag it"""
    with open(METADATA_FILE) as f:
        metadata = json.load(f)

    results = []
    failures = []

    for relative_path in metadata:
        image_path = IMAGES_DIR / relative_path
        tagged_image = tag_with_fallback(image_path)
        if not tagged_image:
            failures.append(image_path)
        else:
            results.append((image_path, tagged_image))

    return results, failures


if __name__ == "__main__":
    results, failures = tag_dataset()
    print(f"Tagged: {len(results)}\nFailed: {len(failures)}")

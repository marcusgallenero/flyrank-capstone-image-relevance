# This is a script to create a template to store Metadata
# Intended to fix the token problem with Gemini APIs Free Tier

import json
from pathlib import Path

IMAGES_DIR = Path("data/images")
OUTPUT_FILE = Path("data/metadata_template.json")


def build_template():
    """Create a JSON template to fill in manually with Gemini"""
    template = {}
    for image in sorted(IMAGES_DIR.rglob("*.jpg")):
        # key = path relative to data/images/ (bear/bear_01.jpg)
        key = str(image.relative_to(IMAGES_DIR).as_posix())
        template[key] = {
            "subject": "",
            "category": "",
            "attributes": [],
            "caption": "",
            "confidence": 0.0
        }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(template, f, indent=2)

    print(f"Wrote {len(template)} entries to {OUTPUT_FILE}")

if __name__ == "__main__":
    build_template()
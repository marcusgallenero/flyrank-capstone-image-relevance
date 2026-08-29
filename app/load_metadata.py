import json
from pathlib import Path
from app.schemas import Metadata

METADATA_FILE = Path("data/metadata.json")

with open(METADATA_FILE) as f:
    _raw_metadata = json.load(f)

def load_metadata(image_path: Path) -> Metadata:
    """look up metadata, validate against schema"""
    key = f"{image_path.parent.name}/{image_path.name}"

    entry = _raw_metadata[key]
    return Metadata(**entry)
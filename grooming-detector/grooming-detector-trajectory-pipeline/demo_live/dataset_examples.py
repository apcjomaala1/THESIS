"""Load the locally retained PAN12 validation illustration."""

import json
from pathlib import Path

EXAMPLE_PATH = Path(__file__).resolve().parent.parent / "revised_runs" / "demo_examples" / "embedding_only_f2.json"


def load_dataset_examples() -> list[dict]:
    if not EXAMPLE_PATH.exists():
        return []
    example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
    if example["source"]["kind"] != "pan12_validation":
        raise ValueError("Demo example must come from PAN12 validation")
    if example["source"]["reference_label"] != 1:
        raise ValueError("Embedding-only demo example must have a positive reference label")
    return [example]

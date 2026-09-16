"""Load selected PAN12 validation examples from the local artifact directory."""

import json
from pathlib import Path

EXAMPLES_PATH = Path(__file__).resolve().parent.parent / "revised_runs" / "demo_examples" / "validation_scenarios.json"


def load_dataset_examples() -> list[dict]:
    if not EXAMPLES_PATH.exists():
        return []
    return json.loads(EXAMPLES_PATH.read_text(encoding="utf-8"))

"""Load selected PAN12 validation examples from the local artifact directory."""

import json
from pathlib import Path

EXAMPLES_PATH = Path(__file__).resolve().parent.parent / "revised_runs" / "demo_examples" / "validation_scenarios.json"


def load_dataset_examples() -> list[dict]:
    if not EXAMPLES_PATH.exists():
        return []
    examples = json.loads(EXAMPLES_PATH.read_text(encoding="utf-8"))
    for example in examples:
        positive = bool(example["source"]["reference_label"])
        example["title"] = (
            f"PAN12 validation: {'positive' if positive else 'negative'} "
            f"({len(example['turns'])} turns)"
        )
        example["short_note"] = (
            "A recorded validation conversation with a conversation-level author-derived "
            "reference label. Run it to see the current F2-policy decisions; an earlier "
            "saved demo description used different F0.5 cutoffs."
        )
    return examples

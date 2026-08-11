"""Generate and summarize the leakage audit for the author-disjoint split."""

import argparse
import json
from pathlib import Path

from data_loader import load_pan12_from_csv
from splitting import author_disjoint_split


def main(args):
    snapshots = load_pan12_from_csv(args.csv, require_dyadic=args.require_dyadic)
    train, validation, test = author_disjoint_split(
        snapshots,
        random_state=args.random_state,
        audit_path=args.output,
    )
    report = json.loads(Path(args.output).read_text(encoding="utf-8"))
    print(f"Saved author-disjoint audit to {Path(args.output).resolve()}")
    print(json.dumps({
        "splits": report["splits"],
        "pairwise_overlap": report["pairwise_overlap"],
        "invariants": report["invariants"],
        "snapshot_partition_check": {
            "train": len(train),
            "validation": len(validation),
            "test": len(test),
        },
    }, indent=2, allow_nan=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--csv", default="../trained_model_distillbert/pan12_final_dataset.csv"
    )
    parser.add_argument("--output", default="author_disjoint_split_audit.json")
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument(
        "--require-dyadic", action=argparse.BooleanOptionalAction, default=True
    )
    main(parser.parse_args())

"""Build the frozen author-disjoint split used by the revised Layer 1 study.

This is an audit/reproduction utility, not part of routine training.  The
checked-in manifest was generated before revised model training.  Re-running
this file must reproduce that manifest from the exact active PAN12 CSV and the
historical connected-author audit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold


SCHEMA_VERSION = 1
DATASET_NAMESPACE = "pan12"
LOCK_DATE = "2026-08-17"
SUBSPLIT_SEED = 42
SUBSPLIT_FOLDS = 8


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_eligible_rows(path: Path) -> pd.DataFrame:
    """Read only valid author-level fields; `is_suspicious` is never loaded."""
    aliases = {
        "conv_id": "conversation_id",
        "convo_id": "conversation_id",
        "author": "author_id",
        "is_predator": "author_is_predator",
    }
    wanted = {
        "conv_id",
        "convo_id",
        "conversation_id",
        "line",
        "author",
        "author_id",
        "text",
        "is_predator",
        "author_is_predator",
    }
    frame = pd.read_csv(path, usecols=lambda name: name in wanted)
    frame = frame.rename(columns=aliases)
    required = {
        "conversation_id",
        "line",
        "author_id",
        "text",
        "author_is_predator",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

    frame = frame[list(required)].copy()
    frame = frame.dropna(
        subset=[
            "text",
            "conversation_id",
            "line",
            "author_id",
            "author_is_predator",
        ]
    )
    frame["text"] = frame["text"].astype(str)
    frame = frame[frame["text"].str.strip() != ""].copy()
    frame["conversation_id"] = (
        DATASET_NAMESPACE + ":" + frame["conversation_id"].astype(str)
    )
    frame["author_id"] = frame["author_id"].astype(str)
    numeric_line = pd.to_numeric(frame["line"], errors="coerce")
    if numeric_line.isna().any() or (numeric_line % 1 != 0).any():
        raise ValueError("Every eligible row must have an integer line identifier")
    frame["line"] = numeric_line.astype(np.int64)
    labels = pd.to_numeric(frame["author_is_predator"], errors="coerce")
    if labels.isna().any() or not labels.isin([0, 1]).all():
        raise ValueError("author_is_predator must contain only binary values")
    frame["author_is_predator"] = labels.astype(np.int8)

    consistency = frame.groupby("author_id")["author_is_predator"].nunique()
    if (consistency > 1).any():
        raise ValueError("At least one author has inconsistent predator membership")

    author_counts = frame.groupby("conversation_id")["author_id"].nunique()
    dyadic_ids = set(author_counts[author_counts == 2].index)
    frame = frame[frame["conversation_id"].isin(dyadic_ids)].copy()
    frame = frame.sort_values(["conversation_id", "line"], kind="stable")

    if frame.duplicated(["conversation_id", "line"]).any():
        raise ValueError("Stable conversation/line keys are not unique")
    return frame.reset_index(drop=True)


def _split_stats(
    frame: pd.DataFrame,
    conversation_ids: set[str],
    labels_by_conversation: dict[str, int],
    components_by_conversation: dict[str, str],
) -> dict[str, Any]:
    selected = frame[frame["conversation_id"].isin(conversation_ids)]
    return {
        "conversations": len(conversation_ids),
        "rows": int(len(selected)),
        "positive_conversations": int(
            sum(labels_by_conversation[conversation_id] for conversation_id in conversation_ids)
        ),
        "negative_conversations": int(
            len(conversation_ids)
            - sum(labels_by_conversation[conversation_id] for conversation_id in conversation_ids)
        ),
        "positive_author_rows": int(selected["author_is_predator"].sum()),
        "negative_author_rows": int(
            len(selected) - selected["author_is_predator"].sum()
        ),
        "authors": int(selected["author_id"].nunique()),
        "components": len(
            {components_by_conversation[conversation_id] for conversation_id in conversation_ids}
        ),
        "conversation_ids": sorted(conversation_ids),
    }


def build_manifest(
    data_file: Path,
    historical_audit_file: Path,
) -> dict[str, Any]:
    frame = load_eligible_rows(data_file)
    historical = json.loads(historical_audit_file.read_text(encoding="utf-8"))
    assignments = historical["assignments"]

    conversation_ids = set(frame["conversation_id"].unique())
    historical_conversation_ids = set(assignments)
    unknown_conversations = conversation_ids - historical_conversation_ids
    if unknown_conversations:
        raise ValueError(
            "Eligible conversations are missing from the historical audit: "
            f"{sorted(unknown_conversations)[:5]}"
        )
    historical_rows_removed_by_strict_validation = sorted(
        historical_conversation_ids - conversation_ids
    )

    labels_by_conversation = (
        frame.groupby("conversation_id")["author_is_predator"].max().astype(int).to_dict()
    )
    components_by_conversation = {
        conversation_id: row["component_id"] for conversation_id, row in assignments.items()
    }
    for conversation_id in conversation_ids:
        if labels_by_conversation[conversation_id] != int(assignments[conversation_id]["label"]):
            raise ValueError(f"Label mismatch for {conversation_id}")

    historical_train = sorted(
        conversation_id
        for conversation_id, row in assignments.items()
        if row["split"] == "train" and conversation_id in conversation_ids
    )
    old_train_ids = np.asarray(historical_train)
    old_train_y = np.asarray(
        [labels_by_conversation[conversation_id] for conversation_id in historical_train]
    )
    old_train_groups = np.asarray(
        [components_by_conversation[conversation_id] for conversation_id in historical_train]
    )

    splitter = StratifiedGroupKFold(
        n_splits=SUBSPLIT_FOLDS,
        shuffle=True,
        random_state=SUBSPLIT_SEED,
    )
    candidate_folds: list[set[str]] = []
    candidate_stats: list[dict[str, Any]] = []
    target_conversations = len(conversation_ids) * 0.10
    target_positives = sum(labels_by_conversation.values()) * 0.10
    for fold_index, (_, held_out_indices) in enumerate(
        splitter.split(
            np.zeros(len(old_train_ids)),
            old_train_y,
            old_train_groups,
        )
    ):
        ids = set(old_train_ids[held_out_indices].tolist())
        positives = int(sum(labels_by_conversation[conversation_id] for conversation_id in ids))
        cost = (
            ((len(ids) - target_conversations) / max(target_conversations, 1.0)) ** 2
            + ((positives - target_positives) / max(target_positives, 1.0)) ** 2
        )
        candidate_folds.append(ids)
        candidate_stats.append(
            {
                "fold": fold_index,
                "conversations": len(ids),
                "positive_conversations": positives,
                "components": len(
                    {components_by_conversation[conversation_id] for conversation_id in ids}
                ),
                "metadata_balance_cost": cost,
            }
        )

    selected_fold = min(
        range(len(candidate_folds)),
        key=lambda index: (candidate_stats[index]["metadata_balance_cost"], index),
    )
    final_test_ids = candidate_folds[selected_fold]
    historical_train_ids = set(historical_train)
    train_ids = historical_train_ids - final_test_ids
    validation_ids = {
        conversation_id
        for conversation_id, row in assignments.items()
        if row["split"] == "validation" and conversation_id in conversation_ids
    }
    excluded_ids = {
        conversation_id
        for conversation_id, row in assignments.items()
        if row["split"] == "test" and conversation_id in conversation_ids
    }
    partitions = {
        "train": train_ids,
        "validation": validation_ids,
        "final_test": final_test_ids,
        "excluded_historical_test": excluded_ids,
    }

    if set().union(*partitions.values()) != conversation_ids:
        raise RuntimeError("Partition union does not cover every eligible conversation")
    names = list(partitions)
    overlaps: dict[str, dict[str, int]] = {}
    for left_index, left in enumerate(names):
        for right in names[left_index + 1 :]:
            left_ids = partitions[left]
            right_ids = partitions[right]
            left_rows = frame[frame["conversation_id"].isin(left_ids)]
            right_rows = frame[frame["conversation_id"].isin(right_ids)]
            author_overlap = set(left_rows["author_id"]) & set(right_rows["author_id"])
            component_overlap = {
                components_by_conversation[conversation_id] for conversation_id in left_ids
            } & {
                components_by_conversation[conversation_id] for conversation_id in right_ids
            }
            conversation_overlap = left_ids & right_ids
            overlaps[f"{left}_vs_{right}"] = {
                "conversations": len(conversation_overlap),
                "authors": len(author_overlap),
                "components": len(component_overlap),
            }
            if conversation_overlap or author_overlap or component_overlap:
                raise RuntimeError(f"Disjointness invariant failed for {left} and {right}")

    split_stats = {
        name: _split_stats(
            frame,
            ids,
            labels_by_conversation,
            components_by_conversation,
        )
        for name, ids in partitions.items()
    }
    manifest: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "locked_before_revised_model_training",
        "locked_on": LOCK_DATE,
        "dataset": {
            "namespace": DATASET_NAMESPACE,
            "filename": data_file.name,
            "sha256": sha256_file(data_file),
            "bytes": data_file.stat().st_size,
            "eligible_rows": int(len(frame)),
            "eligible_conversations": len(conversation_ids),
            "eligible_authors": int(frame["author_id"].nunique()),
            "positive_conversations": int(sum(labels_by_conversation.values())),
            "eligibility": (
                "non-empty PAN12 rows in conversations containing exactly two distinct authors; "
                "official is_predator is the only label"
            ),
        },
        "historical_audit": {
            "filename": historical_audit_file.name,
            "sha256": sha256_file(historical_audit_file),
            "validation_fold_reused_for_development": historical["protocol"]["validation_fold"],
            "previously_inspected_test_fold": historical["protocol"]["test_fold"],
            "previously_inspected_test_disposition": "excluded_from_revised_training_validation_and_final_test",
            "conversations_removed_by_strict_row_validation": historical_rows_removed_by_strict_validation,
        },
        "protocol": {
            "description": (
                "Retain the historical author-disjoint validation partition; exclude the "
                "previously inspected historical test; select a new final test only from "
                "former training components using metadata balance, before revised training."
            ),
            "subsplit_source": "historical_train_only",
            "subsplit_method": "StratifiedGroupKFold over connected-author component IDs",
            "subsplit_folds": SUBSPLIT_FOLDS,
            "subsplit_random_state": SUBSPLIT_SEED,
            "selected_final_fold": selected_fold,
            "selection_inputs": [
                "connected_author_component_id",
                "conversation_count",
                "conversation_label_count",
            ],
            "model_outputs_used": False,
            "candidate_folds": candidate_stats,
        },
        "splits": split_stats,
        "pairwise_overlap": overlaps,
        "invariants": {
            "all_eligible_conversations_assigned_once": True,
            "conversation_overlap_is_zero": True,
            "author_overlap_is_zero": True,
            "component_overlap_is_zero": True,
            "historical_test_is_excluded": True,
            "final_test_originates_only_from_historical_train": True,
        },
    }
    manifest["integrity"] = {
        "canonical_payload_sha256": canonical_sha256(manifest),
        "algorithm": "SHA-256 over canonical JSON before adding this integrity object",
    }
    return manifest


def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-file", type=Path, required=True)
    parser.add_argument("--historical-audit", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=here / "locked_split_manifest.json",
    )
    args = parser.parse_args()
    manifest = build_manifest(args.data_file.resolve(), args.historical_audit.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "output": str(args.output.resolve()),
        "integrity": manifest["integrity"],
        "selected_final_fold": manifest["protocol"]["selected_final_fold"],
        "splits": {
            name: {key: value for key, value in row.items() if key != "conversation_ids"}
            for name, row in manifest["splits"].items()
        },
        "invariants": manifest["invariants"],
    }, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()

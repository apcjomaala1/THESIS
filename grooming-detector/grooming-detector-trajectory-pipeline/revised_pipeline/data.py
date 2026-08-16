"""Strict PAN12 loading and locked-partition utilities for the revised path.

Only official author membership is read.  The invalid project
``is_suspicious`` field is not requested from pandas and cannot enter the
returned frame.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd


DATASET_NAMESPACE = "pan12"
CONTEXT_TURNS = 2
ALLOWED_DEVELOPMENT_SPLITS = frozenset({"train", "validation"})


def load_eligible_rows(path: Path) -> pd.DataFrame:
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
    required = [
        "conversation_id",
        "line",
        "author_id",
        "text",
        "author_is_predator",
    ]
    missing = set(required) - set(frame.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")
    frame = frame[required].dropna(subset=required).copy()
    frame["text"] = frame["text"].astype(str)
    frame = frame[frame["text"].str.strip() != ""].copy()
    frame["conversation_id"] = (
        DATASET_NAMESPACE + ":" + frame["conversation_id"].astype(str)
    )
    frame["author_id"] = frame["author_id"].astype(str)

    lines = pd.to_numeric(frame["line"], errors="coerce")
    if lines.isna().any() or (lines % 1 != 0).any():
        raise ValueError("Every eligible row must have an integer line identifier")
    frame["line"] = lines.astype(np.int64)
    labels = pd.to_numeric(frame["author_is_predator"], errors="coerce")
    if labels.isna().any() or not labels.isin([0, 1]).all():
        raise ValueError("author_is_predator must contain only binary values")
    frame["author_is_predator"] = labels.astype(np.int8)

    author_consistency = frame.groupby("author_id")["author_is_predator"].nunique()
    if (author_consistency > 1).any():
        raise ValueError("At least one author has inconsistent predator membership")
    author_counts = frame.groupby("conversation_id")["author_id"].nunique()
    dyadic_ids = set(author_counts[author_counts == 2].index)
    frame = frame[frame["conversation_id"].isin(dyadic_ids)].copy()
    frame = frame.sort_values(["conversation_id", "line"], kind="stable")
    if frame.duplicated(["conversation_id", "line"]).any():
        raise ValueError("Stable conversation/line keys are not unique")
    if "is_suspicious" in frame.columns:
        raise AssertionError("Forbidden is_suspicious field entered revised data")
    return frame.reset_index(drop=True)


def attach_locked_splits(
    frame: pd.DataFrame,
    manifest: dict[str, Any],
) -> pd.DataFrame:
    assignments: dict[str, str] = {}
    for split_name, split_record in manifest["splits"].items():
        for conversation_id in split_record["conversation_ids"]:
            if conversation_id in assignments:
                raise ValueError(f"Conversation assigned more than once: {conversation_id}")
            assignments[conversation_id] = split_name
    if set(frame["conversation_id"].unique()) != set(assignments):
        raise ValueError("Eligible conversations do not exactly match locked assignments")
    result = frame.copy()
    result["split"] = result["conversation_id"].map(assignments)
    if result["split"].isna().any():
        raise ValueError("At least one row has no locked split")

    for split_name, expected in manifest["splits"].items():
        selected = result[result["split"] == split_name]
        conversation_labels = selected.groupby("conversation_id")[
            "author_is_predator"
        ].max()
        actual = {
            "rows": len(selected),
            "conversations": selected["conversation_id"].nunique(),
            "positive_conversations": int(conversation_labels.sum()),
            "positive_author_rows": int(selected["author_is_predator"].sum()),
            "authors": selected["author_id"].nunique(),
        }
        for field, value in actual.items():
            if int(value) != int(expected[field]):
                raise ValueError(
                    f"Locked statistic mismatch for {split_name}.{field}: "
                    f"expected {expected[field]}, got {value}"
                )
    return result


def select_splits(frame: pd.DataFrame, splits: Iterable[str]) -> pd.DataFrame:
    requested = list(dict.fromkeys(str(split) for split in splits))
    unknown = set(requested) - set(frame["split"].unique())
    if unknown:
        raise ValueError(f"Unknown locked split(s): {sorted(unknown)}")
    selected = frame[frame["split"].isin(requested)].copy()
    return selected.sort_values(["split", "conversation_id", "line"], kind="stable")


def build_context_records(
    frame: pd.DataFrame,
    context_turns: int = CONTEXT_TURNS,
) -> pd.DataFrame:
    """Create prefix-only classifier input plus privacy-minimized cache metadata."""
    if context_turns != CONTEXT_TURNS:
        raise ValueError(f"Revised protocol is locked to {CONTEXT_TURNS} preceding turns")
    records: list[dict[str, Any]] = []
    for conversation_id, conversation in frame.groupby("conversation_id", sort=True):
        conversation = conversation.sort_values("line", kind="stable")
        messages = conversation["text"].astype(str).str.strip().tolist()
        authors = conversation["author_id"].astype(str).tolist()
        labels = conversation["author_is_predator"].astype(int).tolist()
        lines = conversation["line"].astype(int).tolist()
        splits = conversation["split"].astype(str).unique().tolist()
        if len(splits) != 1:
            raise ValueError(f"Conversation spans locked splits: {conversation_id}")
        conversation_label = int(max(labels))
        speaker_map: dict[str, int] = {}
        for index, (line, author, current_text, author_label) in enumerate(
            zip(lines, authors, messages, labels)
        ):
            if author not in speaker_map:
                speaker_map[author] = len(speaker_map)
            first = max(0, index - context_turns)
            records.append(
                {
                    "row_id": f"{conversation_id}:{line}",
                    "conversation_id": conversation_id,
                    "line": line,
                    "split": splits[0],
                    "component_id": None,
                    "speaker_index": speaker_map[author],
                    "author_label": author_label,
                    "conversation_label": conversation_label,
                    "context_text": " [SEP] ".join(messages[first : index + 1]),
                    "current_text": current_text,
                }
            )
        if set(speaker_map.values()) != {0, 1}:
            raise ValueError(f"Expected an eligible dyad: {conversation_id}")
    result = pd.DataFrame(records)
    if result.empty:
        raise ValueError("No context records were built")
    if result["row_id"].duplicated().any():
        raise ValueError("Stable row IDs are not unique")
    result["context_sha256"] = result["context_text"].map(
        lambda value: hashlib.sha256(value.encode("utf-8")).hexdigest()
    )
    result["current_text_sha256"] = result["current_text"].map(
        lambda value: hashlib.sha256(value.encode("utf-8")).hexdigest()
    )
    return result

"""Tests for the PAN12 data loader and simulator (no heavy deps)."""

import io
import textwrap
from pathlib import Path

import pandas as pd
import pytest

from data_loader import (
    build_conversation_snapshots,
    filter_two_author_conversations,
    load_predator_ids,
    load_suspicious_lines,
    simulate_dataset,
)


def test_load_predator_ids(tmp_path):
    p = tmp_path / "predators.txt"
    p.write_text("alice\n\nbob\ncarol\n", encoding="utf-8")
    ids = load_predator_ids(str(p))
    assert ids == {"alice", "bob", "carol"}


def test_load_suspicious_lines(tmp_path):
    p = tmp_path / "diff.txt"
    p.write_text("conv1\t3\nconv1\t7\nconv2\t1\n", encoding="utf-8")
    flagged = load_suspicious_lines(str(p))
    assert flagged == {("conv1", "3"), ("conv1", "7"), ("conv2", "1")}


def test_filter_two_author_drops_single_and_multi():
    df = pd.DataFrame([
        # solo author conv
        {"conversation_id": "c1", "author_id": "A", "text": "hi"},
        {"conversation_id": "c1", "author_id": "A", "text": "anyone here"},
        # 2-author conv (keep)
        {"conversation_id": "c2", "author_id": "A", "text": "hi"},
        {"conversation_id": "c2", "author_id": "B", "text": "hey"},
        # 3-author conv (drop)
        {"conversation_id": "c3", "author_id": "A", "text": "hi"},
        {"conversation_id": "c3", "author_id": "B", "text": "yo"},
        {"conversation_id": "c3", "author_id": "C", "text": "sup"},
    ])
    out = filter_two_author_conversations(df)
    assert set(out["conversation_id"]) == {"c2"}


def test_build_conversation_snapshots_carries_per_message_labels():
    df = pd.DataFrame([
        {"conversation_id": "c1", "line": "1", "author_id": "A", "text": "hi", "is_suspicious": 0, "author_is_predator": 0},
        {"conversation_id": "c1", "line": "2", "author_id": "B", "text": "send pic", "is_suspicious": 1, "author_is_predator": 1},
        {"conversation_id": "c1", "line": "3", "author_id": "A", "text": "no", "is_suspicious": 0, "author_is_predator": 0},
    ])
    snaps = build_conversation_snapshots(df)
    assert len(snaps) == 3
    # snapshots accumulate the history
    assert snaps[0]["messages_so_far"] == ["hi"]
    assert snaps[1]["messages_so_far"] == ["hi", "send pic"]
    assert snaps[2]["messages_so_far"] == ["hi", "send pic", "no"]
    # per-message labels follow is_suspicious column
    assert snaps[1]["label"] == 1
    assert snaps[2]["label"] == 0
    # conversation_label = 1 because at least one author is a predator
    assert all(s["conversation_label"] == 1 for s in snaps)
    assert all(s["predator_authors"] == ["B"] for s in snaps)


def test_simulate_dataset_has_expected_structure():
    snaps = simulate_dataset(n_conversations=10, seed=0)
    assert len(snaps) > 0
    sample = snaps[0]
    for key in (
        "conversation_id", "turn", "messages_so_far", "authors_so_far",
        "per_message_labels", "label", "conversation_label",
    ):
        assert key in sample, f"missing key: {key}"


def test_simulate_dataset_label_consistency():
    snaps = simulate_dataset(n_conversations=20, seed=42)
    # In each snapshot, per_message_labels[-1] should equal label.
    for s in snaps:
        assert s["per_message_labels"][-1] == s["label"]

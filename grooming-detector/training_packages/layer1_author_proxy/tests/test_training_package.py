from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT))

from build_locked_split import canonical_sha256, load_eligible_rows  # noqa: E402
from train_layer1_author_proxy import (  # noqa: E402
    build_prefix_contexts,
    downsample_training_negatives,
    select_f05_threshold,
)


def test_locked_manifest_integrity_and_splits():
    manifest = json.loads(
        (PACKAGE_ROOT / "locked_split_manifest.json").read_text(encoding="utf-8")
    )
    payload = copy.deepcopy(manifest)
    integrity = payload.pop("integrity")
    assert canonical_sha256(payload) == integrity["canonical_payload_sha256"]
    assert manifest["dataset"]["sha256"] == (
        "4131dc7b78865bbe2a48d155f770dd3743236d161b8430893328fbed5a42d408"
    )
    assert manifest["splits"]["train"]["conversations"] == 13031
    assert manifest["splits"]["validation"]["conversations"] == 1827
    assert manifest["splits"]["final_test"]["conversations"] == 1862
    assert manifest["splits"]["excluded_historical_test"]["conversations"] == 1847
    assert all(manifest["invariants"].values())


def test_package_file_hashes():
    manifest = json.loads(
        (PACKAGE_ROOT / "package_manifest.json").read_text(encoding="utf-8")
    )
    for entry in manifest["files"]:
        path = PACKAGE_ROOT / entry["path"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert path.stat().st_size == entry["bytes"]
        assert digest == entry["sha256"]


def test_csv_loader_never_requires_is_suspicious(tmp_path):
    path = tmp_path / "pan.csv"
    pd.DataFrame(
        [
            {
                "conv_id": "c1",
                "line": 1,
                "author": "author-a",
                "text": "hello",
                "is_predator": 0,
                "is_suspicious": "deliberately-invalid-and-ignored",
            },
            {
                "conv_id": "c1",
                "line": 2,
                "author": "author-b",
                "text": "hi",
                "is_predator": 1,
                "is_suspicious": "still-ignored",
            },
            {
                "conv_id": "c1",
                "line": 3,
                "author": "author-a",
                "text": "missing target must be dropped",
                "is_predator": None,
                "is_suspicious": 1,
            },
        ]
    ).to_csv(path, index=False)
    rows = load_eligible_rows(path)
    assert len(rows) == 2
    assert "is_suspicious" not in rows.columns
    assert rows["author_is_predator"].tolist() == [0, 1]


def test_context_is_prefix_only_and_contains_no_author_ids():
    frame = pd.DataFrame(
        {
            "conversation_id": ["pan12:c1"] * 4,
            "line": [1, 2, 3, 4],
            "author_id": ["secret-a", "secret-b", "secret-a", "secret-b"],
            "text": ["one", "two", "three", "four"],
            "author_is_predator": [0, 1, 0, 1],
            "split": ["train"] * 4,
        }
    )
    contexts = build_prefix_contexts(frame, "train", context_turns=2)
    assert contexts["text"].tolist() == [
        "one",
        "one [SEP] two",
        "one [SEP] two [SEP] three",
        "two [SEP] three [SEP] four",
    ]
    joined = " ".join(contexts["text"])
    assert "secret-a" not in joined
    assert "secret-b" not in joined


def test_negative_downsampling_is_deterministic_and_train_only():
    rows = pd.DataFrame(
        {
            "row_id": [f"r{i}" for i in range(12)],
            "label": [1, 1] + [0] * 10,
        }
    )
    first = downsample_training_negatives(rows, negative_ratio=3.0, seed=42)
    second = downsample_training_negatives(rows, negative_ratio=3.0, seed=42)
    assert first["row_id"].tolist() == second["row_id"].tolist()
    assert int(first["label"].sum()) == 2
    assert len(first) == 8


def test_f05_threshold_selection_returns_validation_metrics():
    labels = np.asarray([0, 0, 0, 1, 1], dtype=np.int8)
    probabilities = np.asarray([0.05, 0.10, 0.60, 0.55, 0.90])
    threshold, metrics = select_f05_threshold(labels, probabilities)
    assert 0.0 <= threshold <= 1.0
    assert metrics["f0_5"] >= 0.0
    assert metrics["tp"] + metrics["fn"] == 2
    assert metrics["tn"] + metrics["fp"] == 3

"""Smoke tests for the canonical-schema CSV loader.

These pin the column-aliasing contract used by all dataset loaders. If a new
upstream CSV drifts from the schema, one of these tests should be the first
thing to fail — and the fix is either an entry in COLUMN_ALIASES or a
preprocessing pass on the source CSV, never a code path in features/scorer.
"""

import pandas as pd
import pytest

from data_loader import (
    CANONICAL_COLUMNS,
    load_canonical_csv,
    load_datasets,
)


def _write_csv(path, rows, columns):
    pd.DataFrame(rows, columns=columns).to_csv(path, index=False)


def test_load_canonical_csv_with_pan12_style_columns(tmp_path):
    """PAN12 uses conv_id / author / is_predator — must be aliased."""
    p = tmp_path / "pan12.csv"
    _write_csv(p, [
        {"conv_id": "c1", "line": 1, "author": "alice", "text": "hi",
         "is_predator": 0, "is_suspicious": 0},
        {"conv_id": "c1", "line": 2, "author": "bob", "text": "hey",
         "is_predator": 1, "is_suspicious": 1},
    ], columns=["conv_id", "line", "author", "text", "is_predator", "is_suspicious"])

    df = load_canonical_csv(p, "pan12")
    for col in CANONICAL_COLUMNS:
        assert col in df.columns, f"missing canonical column: {col}"
    assert df["dataset_source"].unique().tolist() == ["pan12"]
    assert df["conversation_id"].iloc[0].startswith("pan12:")
    assert df["author_is_predator"].sum() == 1


def test_load_canonical_csv_with_custom_style_columns(tmp_path):
    """Roblox/YouTube/Discord CSVs use convo_id and have an extra image_type."""
    p = tmp_path / "custom.csv"
    _write_csv(p, [
        {"convo_id": "yt_01", "line": 1, "author": "user1", "text": "hello",
         "is_predator": 0, "is_suspicious": 0, "image_type": "none"},
        {"convo_id": "yt_01", "line": 2, "author": "user2", "text": "how old r u",
         "is_predator": 1, "is_suspicious": 1, "image_type": "none"},
    ], columns=["convo_id", "line", "author", "text",
                "is_predator", "is_suspicious", "image_type"])

    df = load_canonical_csv(p, "yt_dyadic")
    assert "image_type" not in df.columns  # extra column dropped
    assert df["conversation_id"].iloc[0] == "yt_dyadic:yt_01"


def test_load_canonical_tsv_with_espd_style_aliases(tmp_path):
    """eSPD exports may come as TSV with chatName / sender / message / label."""
    p = tmp_path / "panc.tsv"
    p.write_text(
        "chatName\tturn\tsender\tmessage\tlabel\tpredator\n"
        "chat_001\t1\tadult\thello\t0\t1\n"
        "chat_001\t2\tchild\thi\t0\t0\n",
        encoding="utf-8",
    )

    df = load_canonical_csv(p, "panc")
    assert list(df["conversation_id"].unique()) == ["panc:chat_001"]
    assert df["author_id"].tolist() == ["adult", "child"]
    assert df["text"].tolist() == ["hello", "hi"]
    assert df["is_suspicious"].tolist() == [0, 0]
    assert df["author_is_predator"].tolist() == [1, 0]


def test_load_canonical_csv_rejects_missing_required_column(tmp_path):
    """Friendly error when an upstream CSV is missing a required field."""
    p = tmp_path / "broken.csv"
    _write_csv(p, [
        {"conv_id": "c1", "line": 1, "author": "alice", "text": "hi"},
    ], columns=["conv_id", "line", "author", "text"])

    with pytest.raises(ValueError, match="missing required canonical column"):
        load_canonical_csv(p, "broken")


def test_load_canonical_csv_drops_empty_text_and_fills_nan_labels(tmp_path):
    p = tmp_path / "mixed.csv"
    _write_csv(p, [
        {"conv_id": "c1", "line": 1, "author": "a", "text": "hi",
         "is_predator": 0, "is_suspicious": None},
        {"conv_id": "c1", "line": 2, "author": "b", "text": "   ",
         "is_predator": None, "is_suspicious": 0},
        {"conv_id": "c1", "line": 3, "author": "a", "text": "still here",
         "is_predator": 1, "is_suspicious": 1},
    ], columns=["conv_id", "line", "author", "text", "is_predator", "is_suspicious"])

    df = load_canonical_csv(p, "src")
    assert len(df) == 2  # the blank-text row dropped
    assert df["is_suspicious"].dtype.kind in ("i", "u")
    assert df["author_is_predator"].dtype.kind in ("i", "u")


def test_load_canonical_csv_derives_line_when_missing(tmp_path):
    p = tmp_path / "no_line.csv"
    _write_csv(p, [
        {"chatId": "c1", "authorName": "a", "message": "hi", "predator": 0, "label": 0},
        {"chatId": "c1", "authorName": "b", "message": "hello", "predator": 1, "label": 1},
    ], columns=["chatId", "authorName", "message", "predator", "label"])

    df = load_canonical_csv(p, "espd")
    assert df["line"].tolist() == [1, 2]


def test_load_datasets_namespaces_conversation_ids(tmp_path):
    """Two CSVs sharing a conv_id (e.g. both have 'yt_01') must NOT collide."""
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    rows = [
        {"convo_id": "yt_01", "line": 1, "author": "u1", "text": "hi",
         "is_predator": 0, "is_suspicious": 0},
        {"convo_id": "yt_01", "line": 2, "author": "u2", "text": "hey",
         "is_predator": 0, "is_suspicious": 0},
    ]
    cols = ["convo_id", "line", "author", "text", "is_predator", "is_suspicious"]
    _write_csv(a, rows, columns=cols)
    _write_csv(b, rows, columns=cols)

    snaps = load_datasets([("alpha", str(a)), ("beta", str(b))])
    sources = {s["dataset_source"] for s in snaps}
    conv_ids = {s["conversation_id"] for s in snaps}
    assert sources == {"alpha", "beta"}
    assert conv_ids == {"alpha:yt_01", "beta:yt_01"}  # no collision


def test_load_canonical_csv_dyadic_filter(tmp_path):
    """When require_dyadic=True, drop convs that aren't exactly 2-author."""
    p = tmp_path / "mixed.csv"
    rows = [
        # dyadic conv — keep
        {"conv_id": "c_dy", "line": 1, "author": "a", "text": "hi",
         "is_predator": 0, "is_suspicious": 0},
        {"conv_id": "c_dy", "line": 2, "author": "b", "text": "hey",
         "is_predator": 0, "is_suspicious": 0},
        # 3-author conv — drop
        {"conv_id": "c_grp", "line": 1, "author": "a", "text": "hi",
         "is_predator": 0, "is_suspicious": 0},
        {"conv_id": "c_grp", "line": 2, "author": "b", "text": "yo",
         "is_predator": 0, "is_suspicious": 0},
        {"conv_id": "c_grp", "line": 3, "author": "c", "text": "sup",
         "is_predator": 0, "is_suspicious": 0},
    ]
    cols = ["conv_id", "line", "author", "text", "is_predator", "is_suspicious"]
    _write_csv(p, rows, columns=cols)

    df = load_canonical_csv(p, "src", require_dyadic=True)
    surviving = set(df["conversation_id"].unique())
    assert surviving == {"src:c_dy"}

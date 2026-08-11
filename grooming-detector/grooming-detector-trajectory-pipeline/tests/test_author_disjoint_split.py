"""Tests for connected-component author-disjoint splitting."""

import json

from splitting import author_disjoint_split


def _snapshots():
    snapshots = []
    for index in range(100):
        conversation_id = f"c{index:03d}"
        label = int(index % 5 == 0)
        # Every seventh pair is deliberately connected by a shared author.
        if index % 14 in (0, 1):
            first_author = f"linked_{index // 14}"
        else:
            first_author = f"a_{index}"
        predator = f"pred_{index}" if label else None
        second_author = predator or f"b_{index}"
        snapshots.append({
            "conversation_id": conversation_id,
            "turn": 0,
            "authors_so_far": [first_author, second_author],
            "label": label,
            "conversation_label": label,
            "predator_authors": [predator] if predator else [],
            "dataset_source": "test",
        })
    return snapshots


def test_author_disjoint_split_has_no_overlap_and_writes_manifest(tmp_path):
    audit_path = tmp_path / "split_audit.json"
    train, validation, test = author_disjoint_split(
        _snapshots(), random_state=42, audit_path=audit_path
    )

    def authors(rows):
        return {author for row in rows for author in row["authors_so_far"]}

    train_authors = authors(train)
    validation_authors = authors(validation)
    test_authors = authors(test)
    assert train_authors.isdisjoint(validation_authors)
    assert train_authors.isdisjoint(test_authors)
    assert validation_authors.isdisjoint(test_authors)
    assert {row["conversation_id"] for row in train + validation + test} == {
        row["conversation_id"] for row in _snapshots()
    }

    report = json.loads(audit_path.read_text(encoding="utf-8"))
    assert report["invariants"]["author_overlap_is_zero"] is True
    assert report["invariants"]["predator_author_overlap_is_zero"] is True
    assert len(report["assignments"]) == 100

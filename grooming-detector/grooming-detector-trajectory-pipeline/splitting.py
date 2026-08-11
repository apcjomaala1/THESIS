"""Leakage-resistant dataset splitting for conversation trajectory models.

The author-disjoint protocol treats conversations as vertices in a graph and
connects any two conversations that share an author. Every connected component
is then assigned wholesale to train, validation, or test, making author leakage
between those partitions impossible.
"""

from collections import Counter, defaultdict
from itertools import combinations
import json
from pathlib import Path

import numpy as np
from sklearn.model_selection import StratifiedGroupKFold


class _UnionFind:
    def __init__(self, values):
        self.parent = {value: value for value in values}

    def find(self, value):
        parent = self.parent[value]
        if parent != value:
            self.parent[value] = self.find(parent)
        return self.parent[value]

    def union(self, left, right):
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root != right_root:
            self.parent[right_root] = left_root


def _conversation_metadata(snapshots):
    metadata = {}
    for snapshot in snapshots:
        conversation_id = str(snapshot["conversation_id"])
        source = str(snapshot.get("dataset_source", "unknown"))
        label = int(snapshot.get("conversation_label", snapshot["label"]))
        if conversation_id not in metadata:
            metadata[conversation_id] = {
                "source": source,
                "label": label,
                "authors": set(),
                "predator_authors": set(),
                "has_predator_metadata": "predator_authors" in snapshot,
                "snapshots": 0,
            }
        row = metadata[conversation_id]
        if row["source"] != source or row["label"] != label:
            raise ValueError(f"Inconsistent metadata within conversation {conversation_id}")
        row["authors"].update(str(author) for author in snapshot.get("authors_so_far", []))
        if "predator_authors" in snapshot:
            row["predator_authors"].update(str(author) for author in snapshot["predator_authors"])
        else:
            row["has_predator_metadata"] = False
        row["snapshots"] += 1

    empty = [cid for cid, row in metadata.items() if not row["authors"]]
    if empty:
        raise ValueError(f"Cannot make an author-disjoint split: {len(empty)} conversations have no authors")
    return metadata


def _build_components(metadata):
    conversation_ids = sorted(metadata)
    union_find = _UnionFind(conversation_ids)
    first_conversation_by_author = {}

    for conversation_id in conversation_ids:
        source = metadata[conversation_id]["source"]
        for author in sorted(metadata[conversation_id]["authors"]):
            # Author identifiers are dataset-local. Namespacing prevents an
            # accidental collision from joining unrelated external corpora.
            author_key = (source, author)
            first = first_conversation_by_author.get(author_key)
            if first is None:
                first_conversation_by_author[author_key] = conversation_id
            else:
                union_find.union(conversation_id, first)

    raw_components = defaultdict(list)
    for conversation_id in conversation_ids:
        raw_components[union_find.find(conversation_id)].append(conversation_id)

    components = sorted(
        (sorted(conversations) for conversations in raw_components.values()),
        key=lambda conversations: conversations[0],
    )
    component_id_by_conversation = {}
    for index, conversations in enumerate(components):
        component_id = f"component_{index:05d}"
        for conversation_id in conversations:
            component_id_by_conversation[conversation_id] = component_id
    return components, component_id_by_conversation


def _partition_cost(conversation_ids, ratio, metadata, stratum_totals, total_conversations):
    target_size = ratio * total_conversations
    score = ((len(conversation_ids) - target_size) / max(target_size, 1.0)) ** 2
    counts = Counter(
        (metadata[cid]["source"], metadata[cid]["label"])
        for cid in conversation_ids
    )
    for stratum, total in stratum_totals.items():
        target = ratio * total
        score += ((counts[stratum] - target) / max(target, 1.0)) ** 2
    return score


def _select_held_out_folds(folds, metadata):
    all_ids = set(metadata)
    total = len(all_ids)
    stratum_totals = Counter(
        (row["source"], row["label"]) for row in metadata.values()
    )
    positive_strata = {
        stratum for stratum, count in stratum_totals.items()
        if stratum[1] == 1 and count >= len(folds)
    }

    best = None
    for val_index, test_index in combinations(range(len(folds)), 2):
        validation = folds[val_index]
        test = folds[test_index]
        train = all_ids - validation - test
        cost = (
            _partition_cost(train, 0.8, metadata, stratum_totals, total)
            + _partition_cost(validation, 0.1, metadata, stratum_totals, total)
            + _partition_cost(test, 0.1, metadata, stratum_totals, total)
        )
        for held_out in (validation, test):
            held_out_strata = Counter(
                (metadata[cid]["source"], metadata[cid]["label"])
                for cid in held_out
            )
            if any(held_out_strata[stratum] == 0 for stratum in positive_strata):
                cost += 1_000_000.0
        candidate = (cost, val_index, test_index, train, validation, test)
        if best is None or candidate[:3] < best[:3]:
            best = candidate
    return best[3], best[4], best[5], best[1], best[2]


def _namespaced_authors(conversation_ids, metadata, predator_only=False):
    authors = set()
    field = "predator_authors" if predator_only else "authors"
    for conversation_id in conversation_ids:
        source = metadata[conversation_id]["source"]
        authors.update((source, author) for author in metadata[conversation_id][field])
    return authors


def _audit_report(metadata, components, component_ids, folds, partitions, val_fold, test_fold):
    split_ids = {
        "train": set(partitions[0]),
        "validation": set(partitions[1]),
        "test": set(partitions[2]),
    }
    split_authors = {
        name: _namespaced_authors(ids, metadata) for name, ids in split_ids.items()
    }
    predator_metadata_available = all(
        row["has_predator_metadata"] for row in metadata.values()
    )
    split_predator_authors = {
        name: _namespaced_authors(ids, metadata, predator_only=True)
        for name, ids in split_ids.items()
    }

    split_stats = {}
    for name, ids in split_ids.items():
        labels = [metadata[cid]["label"] for cid in ids]
        sources = Counter(metadata[cid]["source"] for cid in ids)
        split_stats[name] = {
            "conversations": len(ids),
            "snapshots": sum(metadata[cid]["snapshots"] for cid in ids),
            "positive_conversations": int(sum(labels)),
            "negative_conversations": int(len(labels) - sum(labels)),
            "authors": len(split_authors[name]),
            "predator_authors": (
                len(split_predator_authors[name]) if predator_metadata_available else None
            ),
            "sources": dict(sorted(sources.items())),
        }

    pairwise_overlap = {}
    for left, right in combinations(("train", "validation", "test"), 2):
        key = f"{left}_vs_{right}"
        shared_conversations = split_ids[left] & split_ids[right]
        shared_authors = split_authors[left] & split_authors[right]
        shared_predators = split_predator_authors[left] & split_predator_authors[right]
        pairwise_overlap[key] = {
            "conversation_count": len(shared_conversations),
            "author_count": len(shared_authors),
            "predator_author_count": len(shared_predators),
            "conversation_ids": sorted(shared_conversations),
            "authors": sorted(f"{source}:{author}" for source, author in shared_authors),
            "predator_authors": sorted(
                f"{source}:{author}" for source, author in shared_predators
            ),
        }

    if any(
        overlap["conversation_count"] or overlap["author_count"]
        for overlap in pairwise_overlap.values()
    ):
        raise RuntimeError("Author-disjoint split invariant failed")

    component_details = []
    for conversations in components:
        authors = _namespaced_authors(conversations, metadata)
        component_details.append({
            "component_id": component_ids[conversations[0]],
            "conversations": len(conversations),
            "positive_conversations": sum(metadata[cid]["label"] for cid in conversations),
            "authors": len(authors),
        })
    component_details.sort(
        key=lambda row: (row["conversations"], row["positive_conversations"]),
        reverse=True,
    )

    fold_stats = []
    for index, ids in enumerate(folds):
        fold_stats.append({
            "fold": index,
            "conversations": len(ids),
            "positive_conversations": sum(metadata[cid]["label"] for cid in ids),
            "components": len({component_ids[cid] for cid in ids}),
        })

    assignment_by_conversation = {}
    for split_name, ids in split_ids.items():
        for conversation_id in sorted(ids):
            assignment_by_conversation[conversation_id] = {
                "split": split_name,
                "component_id": component_ids[conversation_id],
                "source": metadata[conversation_id]["source"],
                "label": metadata[conversation_id]["label"],
            }

    return {
        "protocol": {
            "name": "author-disjoint connected-component 80/10/10 split",
            "random_state": 42,
            "method": (
                "Conversations linked by any shared dataset-namespaced author are "
                "collapsed into connected components. StratifiedGroupKFold creates "
                "10 component-disjoint folds; two held-out folds are selected using "
                "only split-size and source/class-count balance."
            ),
            "validation_fold": val_fold,
            "test_fold": test_fold,
            "model_outputs_used_for_split_selection": False,
            "predator_author_metadata_available": predator_metadata_available,
        },
        "dataset": {
            "conversations": len(metadata),
            "snapshots": sum(row["snapshots"] for row in metadata.values()),
            "positive_conversations": sum(row["label"] for row in metadata.values()),
            "authors": len(_namespaced_authors(metadata.keys(), metadata)),
        },
        "components": {
            "count": len(components),
            "positive_component_count": sum(
                any(metadata[cid]["label"] for cid in conversations)
                for conversations in components
            ),
            "largest": component_details[:20],
        },
        "candidate_folds": fold_stats,
        "splits": split_stats,
        "pairwise_overlap": pairwise_overlap,
        "invariants": {
            "conversation_overlap_is_zero": True,
            "author_overlap_is_zero": True,
            "predator_author_overlap_is_zero": True,
            "predator_author_zero_basis": (
                "explicit predator-author metadata"
                if predator_metadata_available
                else "predator authors are a subset of the verified-disjoint all-author sets"
            ),
        },
        "assignments": assignment_by_conversation,
    }


def author_disjoint_split(snapshots, random_state=42, audit_path=None):
    """Return deterministic 80/10/10 snapshots with zero author overlap.

    The held-out folds are chosen before model training using only dataset
    source, conversation label, and partition size. When ``audit_path`` is
    provided, a complete machine-readable split manifest and overlap proof is
    saved there.
    """
    metadata = _conversation_metadata(snapshots)
    components, component_ids = _build_components(metadata)
    conversation_ids = np.asarray(sorted(metadata))
    strata = np.asarray([
        f"{metadata[cid]['source']}|label={metadata[cid]['label']}"
        for cid in conversation_ids
    ])
    groups = np.asarray([component_ids[cid] for cid in conversation_ids])

    splitter = StratifiedGroupKFold(
        n_splits=10,
        shuffle=True,
        random_state=random_state,
    )
    folds = []
    for _, held_out_indices in splitter.split(
        np.zeros(len(conversation_ids)), strata, groups
    ):
        folds.append(set(conversation_ids[held_out_indices].tolist()))

    train_ids, validation_ids, test_ids, val_fold, test_fold = _select_held_out_folds(
        folds, metadata
    )
    partitions = (train_ids, validation_ids, test_ids)
    report = _audit_report(
        metadata, components, component_ids, folds, partitions, val_fold, test_fold
    )
    report["protocol"]["random_state"] = random_state

    if audit_path:
        Path(audit_path).write_text(
            json.dumps(report, indent=2, allow_nan=False),
            encoding="utf-8",
        )

    def select(ids):
        return [snapshot for snapshot in snapshots if str(snapshot["conversation_id"]) in ids]

    return select(train_ids), select(validation_ids), select(test_ids)

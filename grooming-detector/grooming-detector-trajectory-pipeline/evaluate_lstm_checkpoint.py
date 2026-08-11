"""Evaluate an LSTM checkpoint without using test labels for threshold selection.

The threshold is selected from validation *conversation* labels by F0.5, then
applied once to the deterministic held-out test split. Results are saved as
JSON so they remain available outside a chat transcript.
"""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from data_loader import load_pan12_from_csv
from evaluation import evaluate_conversations
from main import (
    ablate_no_trajectory_features,
    build_per_conversation_features,
    score_with_lstm,
    score_with_weighted_scorer,
    stratified_split,
)
from message_classifier import MessageClassifier
from trajectory_model_lstm import load_trajectory_model
from weighted_scorer import WeightedScorer
from splitting import author_disjoint_split


def tune_threshold(results):
    """Maximize validation conversation F0.5, then recall, then precision."""
    max_scores = np.asarray([max(row["scores"]) if row["scores"] else 0.0 for row in results])
    candidates = np.unique(np.quantile(max_scores, np.linspace(0.01, 0.99, 199)))
    best = None
    for threshold in candidates:
        metrics = evaluate_conversations(results, threshold=float(threshold))
        key = (metrics["f0.5"], metrics["recall"], metrics["precision"])
        if best is None or key > best[0]:
            best = (key, float(threshold), metrics)
    return best[1], best[2]


def slim(metrics):
    keep = (
        "recall", "precision", "f1", "f0.5", "auc_roc",
        "avg_time_to_detection", "median_time_to_detection",
        "n_true_positives", "n_false_negatives", "n_false_positives", "n_true_negatives",
    )
    out = {}
    for key in keep:
        value = metrics[key]
        out[key] = None if isinstance(value, (float, np.floating)) and not np.isfinite(value) else value
    return out


def main(args):
    snapshots = load_pan12_from_csv(args.csv, require_dyadic=args.require_dyadic)
    if args.split_protocol == "author-disjoint":
        _, val_snaps, test_snaps = author_disjoint_split(
            snapshots,
            random_state=args.random_state,
            audit_path=args.split_audit,
        )
        audit_text = Path(args.split_audit).read_text(encoding="utf-8")
        split_description = "author-disjoint connected-component 80/10/10 split"
        split_audit = {
            "path": str(Path(args.split_audit).resolve()),
            "sha256": hashlib.sha256(audit_text.encode("utf-8")).hexdigest(),
        }
    else:
        _, val_snaps, test_snaps = stratified_split(
            snapshots, random_state=args.random_state
        )
        split_description = "deterministic conversation-level 80/10/10 split"
        split_audit = None

    classifier = MessageClassifier(model_path=args.classifier)
    # The active pipeline cache contains every PAN12 message embedding used by
    # this evaluation. Avoid constructing MessageEncoder, which would otherwise
    # attempt a network fetch even though build_per_conversation_features uses
    # the cache before it needs the encoder.
    encoder = None
    centroid = np.load(args.centroid)
    scorer = WeightedScorer.load(args.scorer_config)
    model = load_trajectory_model(args.model)

    print("Building validation features from the cached Layer 1 outputs...")
    val_features = build_per_conversation_features(
        val_snaps, classifier, encoder, centroid, scorer.spike_drop, store_embeddings=True,
    )
    val_results = score_with_lstm(
        val_features, model, classifier, encoder, centroid, scorer.spike_drop,
    )
    threshold, val_metrics = tune_threshold(val_results)
    print(f"Validation-selected LSTM threshold: {threshold:.8f}")
    print(json.dumps(slim(val_metrics), indent=2, allow_nan=False))

    print("Building held-out test features...")
    test_features = build_per_conversation_features(
        test_snaps, classifier, encoder, centroid, scorer.spike_drop, store_embeddings=True,
    )
    lstm_results = score_with_lstm(
        test_features, model, classifier, encoder, centroid, scorer.spike_drop,
    )
    weighted_results = score_with_weighted_scorer(test_features, scorer)
    classifier_only_results = ablate_no_trajectory_features(test_features, scorer)
    test_lstm = evaluate_conversations(lstm_results, threshold=threshold)
    test_weighted = evaluate_conversations(weighted_results, threshold=scorer.flagging_threshold)
    test_classifier_only = evaluate_conversations(classifier_only_results, threshold=scorer.flagging_threshold)

    report = {
        "protocol": {
            "split": split_description,
            "random_state": args.random_state,
            "split_audit": split_audit,
            "threshold_selection": "validation conversation F0.5; test labels not used for threshold selection",
            "checkpoint": str(Path(args.model).resolve()),
            "lstm_checkpoint_metadata": getattr(model, "selection_metadata", {}),
        },
        "validation_lstm": {"threshold": threshold, **slim(val_metrics)},
        "held_out_test": {
            "lstm": slim(test_lstm),
            "weighted_scorer": slim(test_weighted),
            "distilbert_current_score_only": slim(test_classifier_only),
        },
    }
    Path(args.output).write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
    print(f"Saved reproducible report to {args.output}")
    print(json.dumps(report["held_out_test"], indent=2, allow_nan=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="../trained_model_distillbert/pan12_final_dataset.csv")
    parser.add_argument("--classifier", default="../trained_model_distillbert/final_moderation_model")
    parser.add_argument("--centroid", default="benign_centroid.npy")
    parser.add_argument("--scorer-config", default="weighted_scorer.json")
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--require-dyadic", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument(
        "--split-protocol",
        choices=("conversation", "author-disjoint"),
        default="conversation",
    )
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--split-audit", default="author_disjoint_split_audit.json")
    main(parser.parse_args())

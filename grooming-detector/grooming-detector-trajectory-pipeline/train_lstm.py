"""
Train the Layer 2 LSTM trajectory model.

Steps:
  1. Load data via data_loader (same as main.py).
  2. Split into train / val / test via either the historical conversation
     split or the leakage-resistant author-disjoint component split.
  3. Run Layer 1 (DistilBERT classifier) + MessageEncoder to get
     per-message risk scores and [CLS] embeddings.
  4. Compute trajectory features per turn via features.py.
  5. Package each conversation into the format expected by
     trajectory_model_lstm.ConversationDataset:
       embeddings:           (T, 768)
       trajectory_features:  (T, 7)
       labels:               (T,)   — cumulative label per turn
  6. Train the LSTM, selecting the best checkpoint by validation conversation
     F0.5 (conversation AUC is the tie-breaker).
  7. Save best model to trajectory_model.pt.

Usage:
    python train_lstm.py \\
        --csv ../trained_model_distillbert/pan12_final_dataset.csv \\
        --centroid benign_centroid.npy \\
        --epochs 10

    # Multi-dataset:
    python train_lstm.py \\
        --datasets pan12=../trained_model_distillbert/pan12_final_dataset.csv \\
                   synth_groom=data/synthetic_grooming_data.csv \\
                   synth_safe=data/synthetic_safe_data.csv \\
        --centroid benign_centroid.npy
"""

import argparse
from collections import defaultdict
from pathlib import Path

import numpy as np

from data_loader import load_datasets, load_pan12_from_csv
from features import (
    MessageEncoder,
    compute_trajectory_features,
    TRAJECTORY_FEATURE_DIM,
)
from message_classifier import MessageClassifier
from weighted_scorer import WeightedScorer
from trajectory_model_lstm import (
    train_trajectory_model,
    save_trajectory_model,
)

# Re-use main.py's stratified split logic.
from main import stratified_split, _parse_dataset_specs
from splitting import author_disjoint_split


def build_lstm_training_data(snapshots, classifier, encoder, centroid, spike_drop, precomputed_scores=None, precomputed_embeddings=None):
    """
    Build per-conversation feature dicts suitable for ConversationDataset.

    Returns list of dicts:
        embeddings:           np.array (T, 768)
        trajectory_features:  np.array (T, 7)
        labels:               np.array (T,)  — cumulative labels
        conversation_id:      str
    """
    by_conv = defaultdict(list)
    for snap in snapshots:
        by_conv[snap["conversation_id"]].append(snap)

    out = []
    total = len(by_conv)
    for idx, (conv_id, snaps) in enumerate(by_conv.items()):
        if (idx + 1) % 500 == 0 or idx + 1 == total:
            print(f"  Processing conversation {idx + 1}/{total}")

        snaps = sorted(snaps, key=lambda s: s["turn"])
        texts = [s["messages_so_far"][-1] for s in snaps]

        # Use precomputed scores/embeddings if available, otherwise fallback to per-conversation batching
        if precomputed_scores is not None and precomputed_embeddings is not None:
            risk_scores_all = [precomputed_scores[t] for t in texts]
            embeddings_all = [precomputed_embeddings[t] for t in texts]
        else:
            risk_scores_all = classifier.score_batch(texts).tolist()
            embeddings_all = encoder.encode(texts)

        # Trajectory features per turn (incrementally computed)
        traj_features = []
        for i, snap in enumerate(snaps):
            feats = compute_trajectory_features(
                risk_scores_so_far=risk_scores_all[: i + 1],
                embeddings_so_far=[embeddings_all[j] for j in range(i + 1)],
                texts_so_far=snap["messages_so_far"],
                authors_so_far=snap["authors_so_far"],
                benign_centroid=centroid,
                spike_drop=spike_drop,
            )
            traj_features.append(feats)

        # Cumulative labels: 1 from the first predatory message onward.
        per_msg_labels = [int(s.get("label", 0)) for s in snaps]
        cumulative_labels = []
        seen_positive = False
        for lbl in per_msg_labels:
            if lbl == 1:
                seen_positive = True
            cumulative_labels.append(1.0 if seen_positive else 0.0)

        out.append({
            "conversation_id": conv_id,
            "embeddings": np.array(embeddings_all, dtype=np.float32),
            "trajectory_features": np.array(traj_features, dtype=np.float32),
            "labels": np.array(cumulative_labels, dtype=np.float32),
            "conversation_label": int(
                snaps[-1].get("conversation_label", snaps[-1]["label"])
            ),
        })
    return out


def limit_snapshots(snapshots, max_convs):
    if not max_convs:
        return snapshots
    by_conv = defaultdict(list)
    for s in snapshots:
        by_conv[s["conversation_id"]].append(s)
    selected_ids = list(by_conv.keys())[:max_convs]
    return [s for s in snapshots if s["conversation_id"] in set(selected_ids)]


def main(args):
    # -- 1. Load data --
    if args.datasets:
        sources = _parse_dataset_specs(args.datasets)
        snapshots = load_datasets(sources, require_dyadic=args.require_dyadic)
    elif args.csv:
        snapshots = load_pan12_from_csv(args.csv, require_dyadic=args.require_dyadic)
    else:
        raise ValueError("Provide --csv or --datasets")

    if args.max_convs:
        snapshots = limit_snapshots(snapshots, args.max_convs)
        print(f"[SAMPLE RUN] Limited dataset to {args.max_convs} conversations ({len(snapshots)} snapshots)")

    if args.split_protocol == "author-disjoint":
        train_snaps, val_snaps, test_snaps = author_disjoint_split(
            snapshots,
            random_state=args.random_state,
            audit_path=args.split_audit,
        )
        print(f"Author-disjoint split audit saved to {args.split_audit}")
    else:
        train_snaps, val_snaps, test_snaps = stratified_split(
            snapshots, random_state=args.random_state
        )
    n_train = len({s["conversation_id"] for s in train_snaps})
    n_val = len({s["conversation_id"] for s in val_snaps})
    n_test = len({s["conversation_id"] for s in test_snaps})
    print(f"Split: {n_train} train, {n_val} val, {n_test} test conversations")

    # -- 2. Load Layer 1 + encoder + centroid --
    classifier = MessageClassifier(model_path=args.classifier)
    encoder = None
    centroid = np.load(args.centroid)
    if centroid.shape != (768,):
        raise ValueError(f"centroid must be (768,), got {centroid.shape}")

    scorer = WeightedScorer.load(args.scorer_config) if Path(args.scorer_config).exists() else WeightedScorer()
    spike_drop = scorer.spike_drop

    # -- 2.5 Precompute all text embeddings and risk scores on GPU in large batches --
    cache_path = Path("pan12_distilbert_cache.pkl")
    if cache_path.exists():
        print(f"\n--- Loading cached DistilBERT features from {cache_path} ---")
        import pickle
        with open(cache_path, "rb") as f:
            cache_data = pickle.load(f)
            precomputed_scores = cache_data["scores"]
            precomputed_embeddings = cache_data["embeddings"]
    else:
        encoder = MessageEncoder()
        all_texts = list({snap["messages_so_far"][-1] for snap in snapshots})
        print(f"\n--- Precomputing DistilBERT features for {len(all_texts):,} unique messages on {classifier.device} ---")
        
        # Maximize GPU utilization by batching across all conversations
        risk_scores_flat = classifier.score_batch(all_texts, batch_size=128)
        embeddings_flat = encoder.encode(all_texts, batch_size=128)
        
        precomputed_scores = dict(zip(all_texts, risk_scores_flat))
        precomputed_embeddings = dict(zip(all_texts, embeddings_flat))
        
        import pickle
        with open(cache_path, "wb") as f:
            pickle.dump({"scores": precomputed_scores, "embeddings": precomputed_embeddings}, f)
        print(f"  [Cache Saved] {cache_path}")

    # -- 3. Build LSTM training data --
    print("\n--- Building LSTM training data (train) ---")
    train_convs = build_lstm_training_data(
        train_snaps, classifier, encoder, centroid, spike_drop,
        precomputed_scores, precomputed_embeddings
    )
    print(f"  {len(train_convs)} conversations")

    print("--- Building LSTM training data (val) ---")
    val_convs = build_lstm_training_data(
        val_snaps, classifier, encoder, centroid, spike_drop,
        precomputed_scores, precomputed_embeddings
    )
    print(f"  {len(val_convs)} conversations")

    # -- 4. Train LSTM --
    print(f"\n--- Training LSTM ({args.epochs} epochs) ---")
    model = train_trajectory_model(
        train_convs, val_convs,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        device=args.device,
        positive_weight=args.positive_weight,
        conversation_loss_weight=args.conversation_loss_weight,
        random_state=args.random_state,
    )

    # -- 5. Save --
    save_trajectory_model(model, path=args.output)
    print(f"\nDone. Model saved to {args.output}")

    # Also save the test snapshots for later evaluation.
    if args.save_test_snaps:
        import pickle
        with open(args.save_test_snaps, "wb") as f:
            pickle.dump(test_snaps, f)
        print(f"Saved {len(test_snaps)} test snapshots to {args.save_test_snaps}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train LSTM trajectory model (Layer 2)")
    parser.add_argument("--csv", help="PAN12 CSV path (back-compat single-source)")
    parser.add_argument(
        "--datasets", nargs="+", default=None, metavar="NAME=PATH",
        help="One or more canonical-schema CSVs, e.g. pan12=path/to/pan12.csv",
    )
    parser.add_argument("--classifier",
                        default="../trained_model_distillbert/final_moderation_model",
                        help="Path to the trained DistilBERT model directory")
    parser.add_argument("--centroid", default="benign_centroid.npy")
    parser.add_argument("--scorer-config", default="weighted_scorer.json")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument(
        "--positive-weight", type=float, default=None,
        help="Positive-turn loss multiplier; default is computed from the training split.",
    )
    parser.add_argument(
        "--conversation-loss-weight", type=float, default=1.0,
        help="Multiplier for max-over-turn conversation supervision aligned to final evaluation.",
    )
    parser.add_argument("--max-convs", type=int, default=None,
                        help="Limit number of conversations for quick testing")
    parser.add_argument("--device", default=None,
                        help="Force device (cpu/cuda). Auto-detect if omitted.")
    parser.add_argument(
        "--split-protocol",
        choices=("conversation", "author-disjoint"),
        default="conversation",
        help="Dataset split protocol. Use author-disjoint for final generalization evidence.",
    )
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument(
        "--split-audit",
        default="author_disjoint_split_audit.json",
        help="JSON split manifest written when --split-protocol=author-disjoint.",
    )
    parser.add_argument("--output", default="trajectory_model.pt",
                        help="Output path for the trained LSTM model")
    parser.add_argument(
        "--require-dyadic", action=argparse.BooleanOptionalAction, default=True,
        help="Restrict to 2-author conversations (default ON).",
    )
    parser.add_argument("--save-test-snaps", default=None,
                        help="Pickle test snapshots for later evaluation")
    args = parser.parse_args()

    if not (args.csv or args.datasets):
        parser.error("Provide --csv or --datasets.")
    main(args)

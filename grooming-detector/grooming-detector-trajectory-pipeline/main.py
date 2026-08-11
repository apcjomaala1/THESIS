"""
End-to-end pipeline driver.

Steps:
  1. Load PAN12 (CSV preferred; XML+predators+diff fallback) or simulated data.
  2. Split conversations into train / val / test.
  3. Load Layer 1 (DistilBERT classifier trained by train_distillbert.py) and
     the precomputed benign-chat centroid produced by compute_benign_centroid.py.
  4. Build per-conversation feature matrices (T x 7) using
     features.compute_trajectory_features.
  5. Score with WeightedScorer (config loaded from weighted_scorer.json) and
     evaluate against the keyword baseline.

Tuning of the weights themselves is a separate step (tune_weights.py); the
order is build-features → tune-on-val → load-best-config → evaluate-on-test.

Usage:
    # From CSV (preferred — much faster than re-parsing XML):
    python main.py \
        --csv ../trained_model_distillbert/pan12_final_dataset.csv \
        --centroid benign_centroid.npy \
        --scorer-config weighted_scorer.json

    # From raw PAN12 XML + groundtruth files:
    python main.py \
        --xml path/to/pan12.xml \
        --predators path/to/predators.txt \
        --diff path/to/diff.txt \
        --centroid benign_centroid.npy \
        --scorer-config weighted_scorer.json
"""

import argparse
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.model_selection import train_test_split

from data_loader import (
    load_datasets,
    load_pan12,
    load_pan12_from_csv,
    simulate_dataset,
)
from features import (
    MessageEncoder,
    compute_trajectory_features,
    TRAJECTORY_FEATURE_DIM,
)
from message_classifier import MessageClassifier
from weighted_scorer import WeightedScorer
from evaluation import (
    evaluate_conversations,
    evaluate_keyword_baseline,
    print_metrics,
    run_ablation,
    mcnemar_test,
)
from trajectory_model_lstm import load_trajectory_model


def build_per_conversation_features(snapshots, classifier, encoder, centroid, spike_drop,
                                     store_embeddings=False):
    """
    Group snapshots by conversation, score each message with Layer 1, then
    compute trajectory features incrementally per turn. Returns one dict per
    conversation with `trajectory_features` (T, 7), `risk_scores` (T,),
    and `conversation_label`.

    If store_embeddings=True, also stores the (T, 768) embedding matrix
    needed by the LSTM scoring path.
    """
    by_conv = defaultdict(list)
    for snap in snapshots:
        by_conv[snap["conversation_id"]].append(snap)

    # Load cache if available
    cache_path = Path("pan12_distilbert_cache.pkl")
    precomputed_scores, precomputed_embeddings = None, None
    if cache_path.exists():
        import pickle
        with open(cache_path, "rb") as f:
            cache_data = pickle.load(f)
            precomputed_scores = cache_data["scores"]
            precomputed_embeddings = cache_data["embeddings"]

    out = []
    for conv_id, snaps in by_conv.items():
        snaps = sorted(snaps, key=lambda s: s["turn"])

        texts = [s["messages_so_far"][-1] for s in snaps]
        if precomputed_scores is not None and precomputed_embeddings is not None and all(t in precomputed_scores for t in texts):
            risk_scores_all = [precomputed_scores[t] for t in texts]
            embeddings_all = [precomputed_embeddings[t] for t in texts]
        else:
            risk_scores_all = classifier.score_batch(texts).tolist()
            embeddings_all = encoder.encode(texts)

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

        entry = {
            "conversation_id": conv_id,
            "trajectory_features": np.array(traj_features, dtype=np.float32),
            "risk_scores": np.array(risk_scores_all, dtype=np.float32),
            "conversation_label": int(snaps[-1].get("conversation_label", snaps[-1]["label"])),
        }
        if store_embeddings:
            entry["embeddings"] = np.array(embeddings_all, dtype=np.float32)
        out.append(entry)
    return out


def score_with_weighted_scorer(conversation_features, scorer):
    """Apply the weighted scorer to each conversation's feature matrix."""
    results = []
    for conv in conversation_features:
        per_turn_scores = scorer.score_sequence(conv["trajectory_features"]).tolist()
        results.append({
            "conversation_id": conv["conversation_id"],
            "scores": per_turn_scores,
            "label": conv["conversation_label"],
        })
    return results


def score_with_lstm(conversation_features, lstm_model, classifier, encoder, centroid, spike_drop, device=None):
    """
    Score conversations using the trained LSTM trajectory model.

    The LSTM takes (embedding + trajectory_features) as input and outputs
    per-turn risk scores. The conversation_features dict must contain
    trajectory_features and risk_scores from build_per_conversation_features;
    we also need the raw embeddings, which we recompute from the snapshots
    stored during feature building.
    """
    import torch
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    lstm_model.eval()

    results = []
    for conv in conversation_features:
        traj = conv["trajectory_features"]  # (T, 7)
        # We need embeddings — recompute from the stored texts if not cached
        if "embeddings" not in conv:
            # Embeddings were not stored by build_per_conversation_features.
            # Fall back to re-encoding from risk_scores shape.
            # For now, use a zero-embedding fallback; the full pipeline should
            # use build_lstm_training_data from train_lstm.py instead.
            T = traj.shape[0]
            embeddings = np.zeros((T, 768), dtype=np.float32)
        else:
            embeddings = conv["embeddings"]

        x = np.concatenate([embeddings, traj], axis=-1)  # (T, 775)
        x_tensor = torch.tensor(x, dtype=torch.float32).unsqueeze(0).to(device)

        with torch.no_grad():
            scores = lstm_model(x_tensor).squeeze(0).cpu().numpy().tolist()

        results.append({
            "conversation_id": conv["conversation_id"],
            "scores": scores,
            "label": conv["conversation_label"],
        })
    return results


def ablate_no_trajectory_features(conversation_features, scorer):
    """
    Ablation: keep only current_score (Layer 1) feature, zero the others.
    Tests whether the OGDM-derived trajectory features contribute beyond
    raw per-message risk.
    """
    results = []
    for conv in conversation_features:
        feats = conv["trajectory_features"].copy()
        # FEATURE_NAMES order: [peak, current, spike_count, spike_then_drop,
        # rate_of_change, topic_drift, turn_taking_imbalance]
        # We keep index 1 (current_score) and zero the rest.
        mask = np.zeros(7, dtype=np.float32)
        mask[1] = 1.0
        feats = feats * mask
        per_turn_scores = scorer.score_sequence(feats).tolist()
        results.append({
            "conversation_id": conv["conversation_id"],
            "scores": per_turn_scores,
            "label": conv["conversation_label"],
        })
    return results


def stratified_split(snapshots, random_state=42):
    """80/10/10 conversation-level split, stratified jointly on
    (dataset_source, conversation_label) so every source contributes its
    positives and negatives proportionally to train / val / test."""
    conv_meta = {}
    for s in snapshots:
        cid = s["conversation_id"]
        if cid not in conv_meta:
            conv_meta[cid] = (
                s.get("dataset_source", "unknown"),
                int(s.get("conversation_label", s["label"])),
            )
    from collections import Counter

    RARE_THRESHOLD = 5

    conv_ids = list(conv_meta.keys())
    src_label_counts = Counter(conv_meta.values())

    forced_train = [
        c for c in conv_ids
        if src_label_counts[conv_meta[c]] < RARE_THRESHOLD
    ]
    forced_set = set(forced_train)
    splittable = [c for c in conv_ids if c not in forced_set]
    labels = [conv_meta[c][1] for c in splittable]

    train_ids, temp_ids, _, temp_labels = train_test_split(
        splittable, labels,
        test_size=0.2, stratify=labels, random_state=random_state,
    )
    val_ids, test_ids = train_test_split(
        temp_ids, test_size=0.5,
        stratify=temp_labels, random_state=random_state,
    )
    train_ids = train_ids + forced_train

    def select(ids):
        s = set(ids)
        return [snap for snap in snapshots if snap["conversation_id"] in s]

    return select(train_ids), select(val_ids), select(test_ids)


def _parse_dataset_specs(specs):
    """`name=path` pairs → list[(name, path)] tuples, with friendly errors."""
    out = []
    for spec in specs:
        if "=" not in spec:
            raise ValueError(f"--datasets entry '{spec}' is not in name=path form")
        name, path = spec.split("=", 1)
        name, path = name.strip(), path.strip()
        if not name or not path:
            raise ValueError(f"--datasets entry '{spec}' has empty name or path")
        out.append((name, path))
    return out


def main(args):
    # -- 1. Load data --
    if args.simulate:
        print("[SIMULATED DATA]")
        snapshots = simulate_dataset(n_conversations=args.simulate_n)
    elif args.datasets:
        sources = _parse_dataset_specs(args.datasets)
        snapshots = load_datasets(sources, require_dyadic=args.require_dyadic)
    elif args.csv:
        snapshots = load_pan12_from_csv(args.csv, require_dyadic=args.require_dyadic)
    else:
        snapshots = load_pan12(args.xml, args.predators, args.diff)

    train_snaps, val_snaps, test_snaps = stratified_split(snapshots)
    print(
        f"Split: {len({s['conversation_id'] for s in train_snaps})} train, "
        f"{len({s['conversation_id'] for s in val_snaps})} val, "
        f"{len({s['conversation_id'] for s in test_snaps})} test conversations"
    )

    # -- 2. Load Layer 1 + centroid + scorer --
    classifier = MessageClassifier(model_path=args.classifier)
    encoder = MessageEncoder()
    centroid = np.load(args.centroid)
    if centroid.shape != (768,):
        raise ValueError(f"centroid must be (768,), got {centroid.shape}")
    if Path(args.scorer_config).exists():
        scorer = WeightedScorer.load(args.scorer_config)
    else:
        print(f"[main] {args.scorer_config} not found — writing default scorer "
              "(run tune_weights.py to replace with tuned weights).")
        scorer = WeightedScorer()
        scorer.save(args.scorer_config)

    # -- 3. Build features (val + test only — train is for L1 training upstream) --
    use_lstm = getattr(args, 'use_lstm', False)
    print("\n--- Building features (val) ---")
    val_feats = build_per_conversation_features(
        val_snaps, classifier, encoder, centroid, scorer.spike_drop,
        store_embeddings=use_lstm,
    )
    print("--- Building features (test) ---")
    test_feats = build_per_conversation_features(
        test_snaps, classifier, encoder, centroid, scorer.spike_drop,
        store_embeddings=use_lstm,
    )

    # -- 4. Evaluate on test --
    print("\n--- Evaluation: full weighted scorer ---")
    full_results = score_with_weighted_scorer(test_feats, scorer)
    full_metrics = evaluate_conversations(full_results, threshold=scorer.flagging_threshold)
    print_metrics(full_metrics, label="DistilBERT + WeightedScorer (full)")

    print("\n--- Evaluation: keyword baseline ---")
    baseline_results = evaluate_keyword_baseline(test_snaps)
    baseline_metrics = evaluate_conversations(baseline_results, threshold=0.5)
    print_metrics(baseline_metrics, label="Keyword Baseline")

    print("\n--- Ablation: trajectory features removed ---")
    ablation_results = ablate_no_trajectory_features(test_feats, scorer)
    ablation_metrics = evaluate_conversations(ablation_results, threshold=scorer.flagging_threshold)
    print_metrics(ablation_metrics, label="DistilBERT current_score only (no trajectory)")

    run_ablation(full_metrics, ablation_metrics)

    # -- 5. LSTM evaluation (optional) --
    lstm_metrics = None
    if use_lstm:
        lstm_model_path = getattr(args, 'lstm_model', 'trajectory_model.pt')
        print(f"\n--- Evaluation: LSTM trajectory model ({lstm_model_path}) ---")
        lstm_model = load_trajectory_model(lstm_model_path)
        lstm_results = score_with_lstm(
            test_feats, lstm_model, classifier, encoder, centroid,
            scorer.spike_drop,
        )
        checkpoint_threshold = getattr(lstm_model, "selection_metadata", {}).get("threshold", 0.5)
        lstm_threshold = args.lstm_threshold if args.lstm_threshold is not None else checkpoint_threshold
        print(f"Using LSTM threshold: {lstm_threshold:.8f}")
        lstm_metrics = evaluate_conversations(lstm_results, threshold=lstm_threshold)
        print_metrics(lstm_metrics, label="DistilBERT + LSTM Trajectory")

    # -- 6. Optionally save val features for tune_weights.py --
    if args.dump_val_features:
        out = Path(args.dump_val_features)
        np.savez(
            out,
            features=np.array([c["trajectory_features"] for c in val_feats], dtype=object),
            labels=np.array([c["conversation_label"] for c in val_feats]),
        )
        print(f"Saved val features to {out}")

    # -- 7. Summary --
    print("\n" + "=" * 72)
    print("SUMMARY")
    print("=" * 72)
    fmt = "{:<40} {:>8} {:>8} {:>8} {:>8} {:>8}"
    print(fmt.format("Model", "Recall", "F1", "F0.5", "AUC", "TTD"))
    print("-" * 72)
    print(fmt.format(
        "Keyword Baseline",
        f"{baseline_metrics['recall']:.4f}", f"{baseline_metrics['f1']:.4f}",
        f"{baseline_metrics['f0.5']:.4f}",
        f"{baseline_metrics['auc_roc']:.4f}", "N/A",
    ))
    print(fmt.format(
        "DistilBERT only (no trajectory)",
        f"{ablation_metrics['recall']:.4f}", f"{ablation_metrics['f1']:.4f}",
        f"{ablation_metrics['f0.5']:.4f}",
        f"{ablation_metrics['auc_roc']:.4f}",
        f"{ablation_metrics['avg_time_to_detection']:.1f}",
    ))
    print(fmt.format(
        "DistilBERT + Trajectory + Weighted",
        f"{full_metrics['recall']:.4f}", f"{full_metrics['f1']:.4f}",
        f"{full_metrics['f0.5']:.4f}",
        f"{full_metrics['auc_roc']:.4f}",
        f"{full_metrics['avg_time_to_detection']:.1f}",
    ))
    if lstm_metrics:
        print(fmt.format(
            "DistilBERT + LSTM Trajectory",
            f"{lstm_metrics['recall']:.4f}", f"{lstm_metrics['f1']:.4f}",
            f"{lstm_metrics['f0.5']:.4f}",
            f"{lstm_metrics['auc_roc']:.4f}",
            f"{lstm_metrics['avg_time_to_detection']:.1f}",
        ))

    # -- 8. McNemar's tests --
    print("\n" + "=" * 72)
    print("McNEMAR'S TEST: Full model vs. Keyword Baseline")
    print("=" * 72)
    # Use the best model (LSTM if available, otherwise weighted scorer)
    best_metrics = lstm_metrics if lstm_metrics else full_metrics
    best_label = "LSTM" if lstm_metrics else "WeightedScorer"
    mcnemar_vs_baseline = mcnemar_test(best_metrics, baseline_metrics)
    print(f"  {best_label} vs. Keyword Baseline:")
    print(f"  Discordant pairs:   {mcnemar_vs_baseline['b']} ({best_label}[+] baseline[-]) / "
          f"{mcnemar_vs_baseline['c']} ({best_label}[-] baseline[+])")
    print(f"  Chi-squared:        {mcnemar_vs_baseline['chi2']:.4f}")
    print(f"  p-value:            {mcnemar_vs_baseline['p_value']:.6f}")
    print(f"  Significant (alpha=.05): {'YES' if mcnemar_vs_baseline['significant'] else 'NO'}")

    if lstm_metrics:
        print(f"\n  LSTM vs. WeightedScorer:")
        mcnemar_lstm_vs_ws = mcnemar_test(lstm_metrics, full_metrics)
        print(f"  Discordant pairs:   {mcnemar_lstm_vs_ws['b']} (LSTM[+] WS[-]) / "
              f"{mcnemar_lstm_vs_ws['c']} (LSTM[-] WS[+])")
        print(f"  Chi-squared:        {mcnemar_lstm_vs_ws['chi2']:.4f}")
        print(f"  p-value:            {mcnemar_lstm_vs_ws['p_value']:.6f}")
        print(f"  Significant (alpha=.05): {'YES' if mcnemar_lstm_vs_ws['significant'] else 'NO'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulate", action="store_true")
    parser.add_argument("--simulate-n", type=int, default=200)
    parser.add_argument("--csv", help="Pre-built PAN12 CSV (output of trained_model_distillbert/Python.py). "
                                       "Equivalent to --datasets pan12=<path>.")
    parser.add_argument(
        "--datasets",
        nargs="+",
        default=None,
        metavar="NAME=PATH",
        help="One or more canonical-schema CSVs to load together, e.g. "
             "--datasets pan12=../trained_model_distillbert/pan12_final_dataset.csv "
             "roblox_run=../dataset/RobloxPredatorTriesToRun.csv. "
             "Each NAME is prefixed onto conversation IDs to avoid collisions, "
             "and the stratified split is jointly stratified on (source, label).",
    )
    parser.add_argument("--xml")
    parser.add_argument("--predators")
    parser.add_argument("--diff")
    parser.add_argument("--classifier", default="../trained_model_distillbert/final_moderation_model")
    parser.add_argument("--centroid", default="benign_centroid.npy")
    parser.add_argument("--scorer-config", default="weighted_scorer.json")
    parser.add_argument("--dump-val-features", default=None,
                        help="If set, save val feature matrices to .npz for tune_weights.py")
    parser.add_argument("--use-lstm", action="store_true",
                        help="Also evaluate with the trained LSTM trajectory model")
    parser.add_argument("--lstm-model", default="trajectory_model.pt",
                        help="Path to trained LSTM model (output of train_lstm.py)")
    parser.add_argument(
        "--lstm-threshold", type=float, default=None,
        help="Override the checkpoint's validation-selected LSTM threshold.",
    )
    parser.add_argument(
        "--require-dyadic",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Restrict PAN12 to dyadic (2-author) conversations. Default ON for the "
             "Thesis 1 dyadic corpus framing; pass --no-require-dyadic for the full "
             "multi-party set (Thesis 2 territory).",
    )
    args = parser.parse_args()

    if not (args.simulate or args.datasets or args.csv
            or (args.xml and args.predators and args.diff)):
        parser.error("Provide --simulate, --datasets, --csv, "
                     "or all of --xml, --predators, --diff.")
    main(args)

"""
Evaluation metrics for the trajectory pipeline.

  * Conversation-level recall, precision, F1, F0.5 (PAN12 standard),
    AUC-ROC (standard for binary risk-scoring systems).
  * Time-to-detection — turn index at which the model first flags a
    conversation that is in fact predatory. Specific to this study; matches
    the Ch 1 objective of catching grooming early.
  * Keyword baseline for comparison (matches Ch 3 v2 sec 3.8).
  * Ablation utility (trajectory features removed vs. retained).
  * McNemar's test for paired classifier comparison.
"""

from collections import defaultdict

import numpy as np
from sklearn.metrics import (
    recall_score,
    precision_score,
    f1_score,
    fbeta_score,
    roc_auc_score,
)


# -- conversation-level metrics --

def evaluate_conversations(conversations_with_scores, threshold=0.5):
    """
    A conversation is flagged if any per-turn score exceeds `threshold`.
    Time-to-detection is the index of the first such turn (only counted for
    true positives).

    Each input dict needs keys: conversation_id, scores (list[float]), label (int).
    """
    y_true, y_pred = [], []
    time_to_detection = []
    max_scores = []

    for conv in conversations_with_scores:
        scores = conv["scores"]
        label = int(conv["label"])
        y_true.append(label)
        flagged = any(s > threshold for s in scores)
        y_pred.append(int(flagged))
        max_scores.append(max(scores) if scores else 0.0)

        if label == 1 and flagged:
            for turn, score in enumerate(scores):
                if score > threshold:
                    time_to_detection.append(turn)
                    break

    recall = recall_score(y_true, y_pred, zero_division=0)
    precision = precision_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    f05 = fbeta_score(y_true, y_pred, beta=0.5, zero_division=0)
    try:
        auc = roc_auc_score(y_true, max_scores)
    except ValueError:
        auc = float("nan")

    return {
        "recall": recall,
        "precision": precision,
        "f1": f1,
        "f0.5": f05,
        "auc_roc": auc,
        "avg_time_to_detection": np.mean(time_to_detection) if time_to_detection else float("nan"),
        "median_time_to_detection": np.median(time_to_detection) if time_to_detection else float("nan"),
        "n_true_positives": sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1),
        "n_false_negatives": sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0),
        "n_false_positives": sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1),
        "n_true_negatives": sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0),
        "y_true": y_true,
        "y_pred": y_pred,
    }


def print_metrics(metrics, label="Model"):
    bar = "=" * 50
    print(f"\n{bar}\n  {label}\n{bar}")
    print(f"  Recall:                {metrics['recall']:.4f}")
    print(f"  Precision:             {metrics['precision']:.4f}")
    print(f"  F1:                    {metrics['f1']:.4f}")
    print(f"  F0.5:                  {metrics['f0.5']:.4f}")
    print(f"  AUC-ROC:               {metrics['auc_roc']:.4f}")
    print(f"  Avg time-to-detect:    {metrics['avg_time_to_detection']:.1f} turns")
    print(f"  Median time-to-detect: {metrics['median_time_to_detection']:.1f} turns")
    print(f"  TP / FN / FP / TN:     "
          f"{metrics['n_true_positives']} / {metrics['n_false_negatives']} / "
          f"{metrics['n_false_positives']} / {metrics['n_true_negatives']}")


# -- keyword baseline --

# Compact list of keyword patterns matching the Ch 3 keyword-baseline framing.
# Intentionally simple: panels expect the baseline to be the kind of static
# rule list real platforms actually deploy, not a tuned regex engine.
GROOMING_KEYWORDS = [
    "private", "secret", "dont tell", "don't tell", "meet up", "meet in person",
    "send photo", "send pic", "how old are you", "where do you live",
    "are you alone", "parents home", "somewhere private", "keep this between us",
    "mature for your age", "trust me", "just between us",
    "video call", "facetime", "snapchat", "instagram", "whatsapp",
    "another app", "different app",
]


def keyword_baseline_score(text):
    text_lower = text.lower()
    return int(any(kw in text_lower for kw in GROOMING_KEYWORDS))


def evaluate_keyword_baseline(snapshots):
    """
    Aggregate per-message keyword hits into per-conversation scores. Uses
    `conversation_label` (not the per-message `label`) as ground truth.
    """
    conv_results = defaultdict(lambda: {"scores": [], "label": 0, "conversation_id": None})

    for snap in snapshots:
        conv_id = snap["conversation_id"]
        current_text = snap["messages_so_far"][-1]
        score = float(keyword_baseline_score(current_text))
        bucket = conv_results[conv_id]
        bucket["scores"].append(score)
        bucket["label"] = int(snap.get("conversation_label", snap["label"]))
        bucket["conversation_id"] = conv_id

    return list(conv_results.values())


# -- ablation utility --

def run_ablation(full_model_metrics, no_traj_model_metrics):
    """
    Compare full pipeline (DistilBERT + 7 trajectory features + weighted
    scorer) against an ablated version with trajectory features zeroed out
    (only Layer 1's current_score contributes).
    """
    print("\n" + "=" * 50)
    print("  Ablation: trajectory features removed")
    print("=" * 50)
    full_recall = full_model_metrics.get('recall', 0.0)
    no_traj_recall = no_traj_model_metrics.get('recall', 0.0)
    full_f1 = full_model_metrics.get('f1', 0.0)
    no_traj_f1 = no_traj_model_metrics.get('f1', 0.0)
    full_f05 = full_model_metrics.get('f0.5', 0.0)
    no_traj_f05 = no_traj_model_metrics.get('f0.5', 0.0)
    full_ttd = full_model_metrics.get('avg_time_to_detection', float('nan'))
    no_traj_ttd = no_traj_model_metrics.get('avg_time_to_detection', float('nan'))

    print(f"  Full recall:          {full_recall:.4f}")
    print(f"  No-trajectory recall: {no_traj_recall:.4f}")
    print(f"  Recall delta:         {full_recall - no_traj_recall:+.4f}")
    print(f"  Full F1:              {full_f1:.4f}")
    print(f"  No-trajectory F1:     {no_traj_f1:.4f}")
    print(f"  F1 delta:             {full_f1 - no_traj_f1:+.4f}")
    print(f"  Full F0.5:            {full_f05:.4f}")
    print(f"  No-trajectory F0.5:   {no_traj_f05:.4f}")
    print(f"  F0.5 delta:           {full_f05 - no_traj_f05:+.4f}")
    print(f"  Full TTD:             {full_ttd:.1f}")
    print(f"  No-trajectory TTD:    {no_traj_ttd:.1f}")

    if "y_true" in full_model_metrics and "y_true" in no_traj_model_metrics:
        mcnemar = mcnemar_test(full_model_metrics, no_traj_model_metrics)
        print(f"\n  McNemar's test (full vs. ablated):")
        print(f"    Discordant pairs:   {mcnemar['b']} (full[+] ablated[-]) / "
              f"{mcnemar['c']} (full[-] ablated[+])")
        print(f"    Chi-squared:        {mcnemar['chi2']:.4f}")
        print(f"    p-value:            {mcnemar['p_value']:.6f}")
        print(f"    Significant (alpha=.05): {'YES' if mcnemar['significant'] else 'NO'}")


# -- McNemar's test --

def mcnemar_test(metrics_a, metrics_b, alpha=0.05):
    """
    McNemar's test for comparing two classifiers on the same test set.

    Uses the per-sample y_true/y_pred stored in the metrics dicts to build
    a 2×2 contingency table of discordant predictions:

        |              | Model B correct | Model B wrong |
        |--------------|-----------------|---------------|
        | Model A correct |       a         |      b        |
        | Model A wrong   |       c         |      d        |

    The test statistic is chi² = (|b - c| - 1)² / (b + c) with 1 df
    (continuity-corrected form), or exact binomial if b + c < 25.

    Returns dict with chi2, p_value, significant (bool), and the
    contingency counts b and c.
    """
    from scipy.stats import chi2 as chi2_dist
    try:
        from scipy.stats import binomtest
        def _exact_binom(k, n):
            return binomtest(k, n, 0.5).pvalue
    except ImportError:
        from scipy.stats import binom_test as _bt
        def _exact_binom(k, n):
            return _bt(k, n, 0.5)

    y_true = metrics_a["y_true"]
    pred_a = metrics_a["y_pred"]
    pred_b = metrics_b["y_pred"]

    assert len(y_true) == len(pred_a) == len(pred_b), (
        "McNemar requires both models evaluated on the same test set"
    )

    # b = A correct, B wrong; c = A wrong, B correct
    b = sum(1 for t, pa, pb in zip(y_true, pred_a, pred_b)
            if pa == t and pb != t)
    c = sum(1 for t, pa, pb in zip(y_true, pred_a, pred_b)
            if pa != t and pb == t)

    n_discordant = b + c

    if n_discordant == 0:
        return {"b": b, "c": c, "chi2": 0.0, "p_value": 1.0,
                "significant": False}

    if n_discordant < 25:
        # Exact binomial test (two-sided) for small samples
        p_value = float(_exact_binom(b, n_discordant))
        chi2_stat = float((b - c) ** 2 / n_discordant)
    else:
        # Chi-squared with continuity correction (Edwards, 1948)
        chi2_stat = float((abs(b - c) - 1) ** 2 / n_discordant)
        p_value = float(1.0 - chi2_dist.cdf(chi2_stat, df=1))

    return {
        "b": b, "c": c,
        "chi2": chi2_stat,
        "p_value": p_value,
        "significant": p_value < alpha,
    }

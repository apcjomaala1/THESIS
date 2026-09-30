"""Compare recorded validation-selected F0.5/F1/F2 policies on saved test scores.

No model fitting, inference, test-threshold search, or active-policy changes.
Verify validation provenance before reading the previously evaluated test set.
"""
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNS = ROOT / "grooming-detector/grooming-detector-trajectory-pipeline/revised_runs"
SPECS = [
    ("lstm_trajectory7", "Primary LSTM", "Trajectory-Feature LSTM", "score"),
    ("lstm_enhanced775", "Enhanced LSTM", "Embedding-and-Feature LSTM", "score"),
    ("raw_layer1", "Maximum Layer 1", "Maximum Layer 1 proxy", "raw_layer1_score"),
    ("weighted", "Weighted scorer", "Weighted scorer", "weighted_score"),
    ("keyword", "Keyword rule", "Keyword rule", "score"),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def metrics(rows, column, threshold):
    result = dict(tp=0, fp=0, fn=0, tn=0)
    for row in rows:
        positive = int(row["label"]) == 1
        flagged = float(row[column]) >= threshold
        cell = ("tp" if positive else "fp") if flagged else ("fn" if positive else "tn")
        result[cell] += 1
    tp, fp, fn = (result[k] for k in ("tp", "fp", "fn"))
    def divide(a, b):
        return a / b if b else 0.0
    result.update(threshold=threshold, precision=divide(tp, tp+fp),
                  recall=divide(tp, tp+fn), f0_5=divide(1.25*tp, 1.25*tp+fp+0.25*fn),
                  f1=divide(2*tp, 2*tp+fp+fn), f2=divide(5*tp, 5*tp+fp+4*fn))
    return result


def main():
    selection_path = HERE / "validation_f1_comparison.json"
    f2_path = HERE / "f2_test_reanalysis.json"
    original_path = RUNS / "final_results/final_evaluation.json"
    predictions_path = RUNS / "final_results/per_conversation_predictions.csv"
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    assert selection["test_data_read"] is False
    selected = {row["method"]: row for row in selection["results"]}
    protected = {p: digest(p) for p in (selection_path, f2_path, original_path, predictions_path)}
    for relative, expected in selection["input_hashes"].items():
        path = ROOT / relative
        assert digest(path) == expected, relative
        protected[path] = expected

    validation_labels = None
    cutoffs = {}
    for key, historical_name, _, column in SPECS:
        record = selected[historical_name]
        rows = read_rows(ROOT / record["score_source"])
        labels = {row["conversation_id"]: int(row["label"]) for row in rows}
        assert len(labels) == len(rows) == 1827 and sum(labels.values()) == 49
        if validation_labels is None:
            validation_labels = labels
        assert labels == validation_labels
        cutoffs[key] = {}
        for policy in ("F1", "F2"):
            threshold = float(record[f"{policy.lower()}_selected_threshold"])
            reproduced = metrics(rows, column, threshold)
            for field in ("tp", "fp", "fn", "tn", "precision", "recall", "f1", "f2"):
                assert abs(reproduced[field] - record[f"{policy.lower()}_policy"][field]) < 1e-12
            cutoffs[key][policy] = threshold

    # Only now read outcomes from the previously evaluated test partition.
    original = json.loads(original_path.read_text(encoding="utf-8"))
    assert digest(predictions_path) == original["predictions_sha256"]
    rows = read_rows(predictions_path)
    test_ids = {row["conversation_id"] for row in rows}
    assert len(test_ids) == len(rows) == 1862 and sum(int(row["label"]) for row in rows) == 44
    assert not test_ids.intersection(validation_labels)
    f2 = json.loads(f2_path.read_text(encoding="utf-8"))["results"]
    results = {}
    print("| Method | Policy | Cutoff | TP | FP | FN | TN | Precision | Recall |")
    print("|---|---|---:|---:|---:|---:|---:|---:|---:|")
    for key, historical_name, display_name, _ in SPECS:
        old = original["metrics"][key]["point_estimate"]
        assert old["threshold"] == selected[historical_name]["existing_threshold"]
        cutoffs[key]["F0.5"] = old["threshold"]
        results[key] = {"name": display_name, "policies": {}}
        for policy in ("F0.5", "F1", "F2"):
            point = metrics(rows, key + "_score", cutoffs[key][policy])
            results[key]["policies"][policy] = point
            if policy != "F1":
                expected = old if policy == "F0.5" else f2[key]["test"]
                for field in ("threshold", "tp", "fp", "fn", "tn", "precision", "recall"):
                    assert abs(point[field] - expected[field]) < 1e-12
            print(f"| {display_name} | {policy} | {point['threshold']:.9f} | {point['tp']} | {point['fp']} | {point['fn']} | {point['tn']:,} | {point['precision']:.4f} | {point['recall']:.4f} |")
    assert all(digest(path) == before for path, before in protected.items())
    report = dict(created_utc=datetime.now(timezone.utc).isoformat(),
                  status="DESCRIPTIVE_POLICY_COMPARISON_ON_PREVIOUSLY_EVALUATED_TEST_SCORES",
                  main_reporting_policy="F2", policy_order=["F0.5", "F1", "F2"],
                  validation_conversations=1827, validation_positive=49,
                  test_conversations=1862, test_positive=44, test_negative=1818,
                  validation_receipt_verified_before_test_read=True,
                  test_threshold_search=False, model_training=False, model_inference=False,
                  original_inputs_unchanged=True, alternative_policy_intervals_computed=False,
                  results=results,
                  input_hashes={str(p.relative_to(ROOT)): h for p, h in protected.items()})
    (HERE / "test_threshold_policy_comparison.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

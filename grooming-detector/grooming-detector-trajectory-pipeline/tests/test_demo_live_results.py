"""Checks that the live demo reports Chapter IV without reevaluation."""

from types import SimpleNamespace

import demo_live.app as demo_app


def sample_report():
    def method(pr_auc, f0_5, precision, recall, tp=0, fp=0, fn=0, tn=0):
        return {
            "point_estimate": {
                "pr_auc": pr_auc,
                "f0_5": f0_5,
                "precision": precision,
                "recall": recall,
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "tn": tn,
            }
        }

    def difference(point, lower, upper):
        return {"point_difference": point, "lower": lower, "upper": upper}

    return {
        "audit": {
            "conversations": 1862,
            "positive_conversations": 44,
            "components": 1800,
        },
        "metrics": {
            "keyword": method(0.4451, 0.6888, 0.7105, 0.6136),
            "raw_layer1": method(0.5523, 0.5529, 0.5610, 0.5227),
            "weighted": method(0.8050, 0.7500, 0.7347, 0.8182, fp=13, fn=8),
            "lstm_trajectory7": method(
                0.9153, 0.8621, 0.8511, 0.9091, tp=40, fp=7, fn=4, tn=1811
            ),
            "lstm_enhanced775": method(0.9483, 0.8836, 0.8723, 0.9318),
        },
        "paired_component_bootstrap_differences": {
            "lstm_trajectory7_minus_weighted": {
                "differences": {
                    "pr_auc": difference(0.1103, 0.0251, 0.2254),
                    "f0_5": difference(0.1121, 0.0194, 0.2336),
                }
            },
            "lstm_trajectory7_minus_lstm_enhanced775": {
                "differences": {
                    "pr_auc": difference(-0.0330, -0.1095, 0.0326),
                    "f0_5": difference(-0.0216, -0.1008, 0.0547),
                }
            },
        },
        "canonical_payload_sha256": "accepted-final-report",
    }


def test_chapter4_summary_preserves_primary_and_matched_results():
    summary = demo_app.build_chapter4_summary(sample_report())

    assert summary["conversations"] == 1862
    assert summary["positive_conversations"] == 44
    assert summary["negative_conversations"] == 1818
    assert summary["primary"]["pr_auc"] == 0.9153
    assert summary["primary"]["f0_5"] == 0.8621
    assert summary["primary"]["tp"] == 40
    assert summary["primary"]["fp"] == 7
    assert summary["primary"]["fn"] == 4
    assert summary["matched_pr_auc"]["point_difference"] == 0.1103
    assert summary["matched_f0_5"]["point_difference"] == 0.1121
    assert summary["enhanced_comparison_inconclusive"] is True
    assert len(summary["methods"]) == 5


def test_results_api_reads_frozen_report_without_scoring(monkeypatch):
    fake_engine = SimpleNamespace(eval_report=sample_report())
    monkeypatch.setattr(demo_app, "_engine", fake_engine)
    demo_app.app.config.update(TESTING=True)

    with demo_app.app.test_client() as client:
        response = client.get("/api/results")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["primary"]["recall"] == 0.9091
    assert payload["weighted_false_positives"] == 13
    assert payload["source_hash"] == "accepted-final-report"

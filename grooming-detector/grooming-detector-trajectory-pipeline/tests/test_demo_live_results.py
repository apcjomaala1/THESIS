"""Check that the demo reports the saved F2 policy, without test inference."""

from types import SimpleNamespace

import demo_live.app as demo_app
from demo_live.scoring_engine import F2_RESULTS_PATH, FINAL_EVALUATION_PATH, _read_json


def test_chapter4_summary_reads_recorded_f2_results():
    summary = demo_app.build_chapter4_summary(
        _read_json(FINAL_EVALUATION_PATH), _read_json(F2_RESULTS_PATH)
    )
    assert summary["conversations"] == 1862
    assert summary["positive_conversations"] == 44
    assert summary["negative_conversations"] == 1818
    assert round(summary["primary"]["pr_auc"], 4) == 0.9153
    assert summary["primary"]["tp"] == 41
    assert summary["primary"]["fp"] == 21
    assert summary["primary"]["fn"] == 3
    assert summary["matched_f2"]["point_difference"] > 0
    assert summary["enhanced_comparison_inconclusive"] is True
    assert len(summary["methods"]) == 5
    methods = {row["key"]: row for row in summary["methods"]}
    assert (methods["weighted"]["fp"], methods["weighted"]["fn"]) == (24, 6)
    assert (methods["lstm_enhanced775"]["fp"], methods["lstm_enhanced775"]["fn"]) == (41, 0)
    assert methods["lstm_trajectory7"]["label"] == "Trajectory-Feature LSTM"
    assert methods["lstm_enhanced775"]["label"] == "Embedding-and-Feature LSTM"
    assert methods["lstm_trajectory7"]["is_lstm"] is True
    assert methods["lstm_enhanced775"]["is_lstm"] is True
    assert summary["embedding_model"]["tp"] == 44


def test_results_api_reads_receipt_without_scoring(monkeypatch):
    fake_engine = SimpleNamespace(
        eval_report=_read_json(FINAL_EVALUATION_PATH),
        f2_report=_read_json(F2_RESULTS_PATH),
    )
    monkeypatch.setattr(demo_app, "_engine", fake_engine)
    demo_app.app.config.update(TESTING=True)
    with demo_app.app.test_client() as client:
        response = client.get("/api/results")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["primary"]["tp"] == 41
    assert payload["weighted_false_positives"] == 24
    assert payload["source_status"] == "REVISED_F2_POLICY_ON_PREVIOUSLY_EVALUATED_TEST_SCORES"

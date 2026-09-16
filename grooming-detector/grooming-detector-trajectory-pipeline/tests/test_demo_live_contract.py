"""Regression checks for the simplified frozen-model demonstration."""

from pathlib import Path
import re

from demo_live.scenarios import SCENARIOS


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = (ROOT / "demo_live" / "static" / "app.js").read_text(encoding="utf-8")
TEMPLATE = (ROOT / "demo_live" / "templates" / "index.html").read_text(
    encoding="utf-8"
)


def test_live_demo_serializes_scoring_requests():
    assert "let requestQueue = Promise.resolve();" in SCRIPT
    assert "requestQueue.then(() => submitTurnNow" in SCRIPT
    assert "conversationEpoch += 1;" in SCRIPT
    assert "if (epoch !== conversationEpoch) return false;" in SCRIPT


def test_autoplay_waits_for_each_scored_turn():
    assert "await stepScenarioTurn();" in SCRIPT
    assert "setTimeout(runAutoplayTurn, 600)" in SCRIPT
    assert "setInterval(" not in SCRIPT


def test_interface_is_simple_and_explanatory():
    assert "Conversation Model Demo" in TEMPLATE
    assert "Chapter IV results" in TEMPLATE
    assert "What the held-out test showed" in TEMPLATE
    assert "Held-out point estimates reported in Chapter IV" in TEMPLATE
    assert "opening this demo does not rerun the final test" in TEMPLATE
    assert "Run full chat" in TEMPLATE
    assert "Add next message" in TEMPLATE
    assert "Below threshold does not mean safe" in TEMPLATE
    assert "Model Inspection Workbench" not in TEMPLATE
    assert "Multi-Model Prefix Evaluation Matrix" not in TEMPLATE
    assert "workbench-grid" not in TEMPLATE
    assert "diagnostic-card" not in TEMPLATE


def test_endpoint_score_is_not_presented_as_a_calibrated_percentage():
    assert 'id="lstm-score">--<' in TEMPLATE
    assert "textContent = score.toFixed(4);" in SCRIPT
    assert "score * 100" in SCRIPT  # visual bar only
    assert "% risk" not in TEMPLATE.lower()


def test_every_bound_id_exists_in_template():
    bound_ids = set(re.findall(r'getElementById\("([^"]+)"\)', SCRIPT))
    template_ids = set(re.findall(r'id="([^"]+)"', TEMPLATE))
    assert bound_ids <= template_ids


def test_files_have_clean_text_encoding():
    for marker in ("Ã", "Â", "â€“", "â€”"):
        assert marker not in SCRIPT
        assert marker not in TEMPLATE


def test_demo_scenarios_document_verified_expected_behavior():
    assert len(SCENARIOS) == 6
    assert {scenario["id"] for scenario in SCENARIOS} == {
        "private_meeting_pressure",
        "long_private_pressure",
        "school_project_false_alarm",
        "safety_lesson_false_alarm",
        "routine_project_chat",
        "concerning_but_below",
    }
    for scenario in SCENARIOS:
        assert isinstance(scenario["expected_lstm_flagged"], bool)
        assert "expected_first_flag_turn" in scenario
        assert len(scenario["turns"]) >= 2


def test_comparison_examples_have_explicit_reference_intent_and_baseline_contracts():
    for scenario in SCENARIOS:
        assert isinstance(scenario["intended_review"], bool)
        assert set(scenario["expected_flags"]) == {"lstm", "weighted", "raw_layer1", "keyword"}
        for baseline in scenario["comparison_methods"]:
            assert scenario["expected_flags"]["lstm"] == scenario["intended_review"]
            assert scenario["expected_flags"][baseline] != scenario["intended_review"]
    school = next(s for s in SCENARIOS if s["id"] == "school_project_false_alarm")
    assert school["expected_first_flag_turn"] == 3
    assert "briefly flag turn 3" in school["short_note"]


def test_long_example_covers_all_three_baselines():
    scenario = next(s for s in SCENARIOS if s["id"] == "long_private_pressure")
    assert len(scenario["turns"]) == 40
    assert set(scenario["comparison_methods"]) == {"weighted", "raw_layer1", "keyword"}
    assert scenario["expected_flags"] == {
        "lstm": True, "weighted": False, "raw_layer1": False, "keyword": False
    }

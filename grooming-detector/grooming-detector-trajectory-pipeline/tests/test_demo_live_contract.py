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
    assert "setTimeout(runAutoplayTurn, 450)" in SCRIPT
    assert "setInterval(" not in SCRIPT


def test_interface_is_simple_and_explanatory():
    assert "GroomShield Live Demo" in TEMPLATE
    assert "Chapter 4 result:" in TEMPLATE
    assert "Run conversation" in TEMPLATE
    assert "Next message" in TEMPLATE
    assert "What this demonstrates" in TEMPLATE
    assert "A below-cutoff result does not establish" in TEMPLATE
    for removed_section in (
        "What the held-out test showed",
        "Where the methods disagree",
        "Watch the score change",
        "Inspect the latest turn",
        "Revised F2-policy point estimates reported in Chapter IV",
    ):
        assert removed_section not in TEMPLATE


def test_endpoint_score_is_not_presented_as_a_calibrated_percentage():
    assert 'id="lstm-score">--<' in TEMPLATE
    assert "Number(trajectory.score).toFixed(4)" in SCRIPT
    assert "Number(trajectory.score) * 100" in SCRIPT  # visual bar only
    assert "% risk" not in TEMPLATE.lower()


def test_every_bound_id_exists_in_template():
    bound_ids = set(re.findall(r'getElementById\("([^"]+)"\)', SCRIPT))
    template_ids = set(re.findall(r'id="([^"]+)"', TEMPLATE))
    assert bound_ids <= template_ids


def test_model_labels_describe_inputs_without_a_preferred_variant():
    for label in ("Trajectory-Feature LSTM", "Embedding-and-Feature LSTM"):
        assert label in TEMPLATE
    assert "Trajectory-Feature is" in SCRIPT
    assert "Embedding-and-Feature is" in SCRIPT
    for old_label in ("Primary LSTM", "Enhanced LSTM", "primary-method"):
        assert old_label not in TEMPLATE
        assert old_label not in SCRIPT
    assert 'id="embedding-score-fill"' in TEMPLATE
    assert "chapter4.embedding_model" in TEMPLATE
    assert "Both below cutoff" in SCRIPT


def test_files_have_clean_text_encoding():
    for marker in ("Ã", "Â", "â€“", "â€”"):
        assert marker not in SCRIPT
        assert marker not in TEMPLATE


def test_demo_scenarios_document_verified_expected_behavior():
    assert len(SCENARIOS) == 5
    assert {scenario["id"] for scenario in SCENARIOS} == {
        "private_meeting_pressure",
        "private_platform_migration",
        "school_project_false_alarm",
        "safety_lesson_false_alarm",
        "concerning_but_below",
    }
    for scenario in SCENARIOS:
        assert isinstance(scenario["expected_lstm_flagged"], bool)
        assert "expected_first_flag_turn" in scenario
        assert len(scenario["turns"]) >= 2


def test_comparison_examples_have_explicit_reference_intent_and_baseline_contracts():
    for scenario in SCENARIOS:
        assert isinstance(scenario["intended_review"], bool)
        assert set(scenario["expected_flags"]) == {"lstm", "enhanced_lstm", "weighted", "raw_layer1", "keyword"}
        for baseline in scenario["comparison_methods"]:
            assert scenario["expected_flags"]["lstm"] == scenario["intended_review"]
            assert scenario["expected_flags"][baseline] != scenario["intended_review"]
    school = next(s for s in SCENARIOS if s["id"] == "school_project_false_alarm")
    assert school["expected_first_flag_turn"] == 1
    assert "under F2" in school["short_note"]


def test_each_example_caption_states_both_active_f2_outcomes():
    for scenario in SCENARIOS:
        assert "both lstms" in scenario["short_note"].lower()
        assert "f2" in scenario["short_note"].lower()
        assert scenario["expected_flags"]["lstm"] == scenario["expected_lstm_flagged"]

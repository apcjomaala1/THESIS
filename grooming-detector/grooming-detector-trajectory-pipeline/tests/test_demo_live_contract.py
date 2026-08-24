"""Regression checks for the frozen live demonstration interface."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = (ROOT / "demo_live" / "static" / "app.js").read_text(encoding="utf-8")
TEMPLATE = (ROOT / "demo_live" / "templates" / "index.html").read_text(
    encoding="utf-8"
)


def test_live_demo_serializes_scoring_requests():
    assert "let requestQueue = Promise.resolve();" in SCRIPT
    assert "requestQueue.then(() => submitTurnNow" in SCRIPT
    assert "conversationEpoch += 1;" in SCRIPT
    assert "if (epoch !== conversationEpoch) return;" in SCRIPT


def test_autoplay_waits_for_each_scored_turn():
    assert "await stepNextTurn();" in SCRIPT
    assert "setTimeout(runAutoPlayTurn, 1600)" in SCRIPT
    assert "setInterval(" not in SCRIPT


def test_topic_distance_uses_its_zero_to_two_scale():
    assert "f.topic_distance * 50" in SCRIPT
    assert "buildPath(curve.topic_distances, 2)" in SCRIPT
    assert "Topic Distance (0–2 scale)" in TEMPLATE


def test_endpoint_score_is_not_presented_as_a_calibrated_percentage():
    assert 'id="gauge-pct">0.0000<' in TEMPLATE
    assert "gaugePct.textContent = lstmScore.toFixed(4);" in SCRIPT
    assert "lstmPct" not in SCRIPT

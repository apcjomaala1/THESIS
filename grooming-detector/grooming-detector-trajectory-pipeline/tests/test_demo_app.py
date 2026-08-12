"""Presentation and guardrail checks for the consultation interface."""

import re
from pathlib import Path

from demo.app import app


def test_demo_page_leads_with_lstm_mechanics_and_limitations():
    app.config.update(TESTING=True)

    with app.test_client() as client:
        response = client.get("/")

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "Conversation Trajectory Lab" in page
    assert "LSTM active" in page
    assert "Development prototype - pipeline mechanics only" in page
    assert "Scores are not validated grooming classifications or safety decisions" in page
    assert "A below-threshold result does not mean the conversation is safe" in page


def test_historical_metrics_are_collapsed_and_explicitly_not_final():
    app.config.update(TESTING=True)

    with app.test_client() as client:
        response = client.get("/")

    page = response.get_data(as_text=True)
    assert '<details class="detail-panel historical-panel">' in page
    assert "Historical development result" in page
    assert "Not a fair final comparison" in page
    assert "L1 ablation (invalid threshold)" in page


def test_javascript_element_bindings_exist_in_template_and_text_is_clean():
    pipeline_root = Path(__file__).resolve().parents[1]
    template = (pipeline_root / "demo" / "templates" / "chat.html").read_text(encoding="utf-8")
    javascript = (pipeline_root / "demo" / "static" / "app.js").read_text(encoding="utf-8")

    html_ids = set(re.findall(r'id="([^"]+)"', template))
    bound_ids = set(re.findall(r'getElementById\("([^"]+)"\)', javascript))

    assert bound_ids <= html_ids
    assert not any(marker in template + javascript for marker in ("â", "Â", "Ã"))

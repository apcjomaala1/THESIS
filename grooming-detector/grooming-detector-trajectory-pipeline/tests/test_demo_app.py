"""Presentation and guardrail checks for the consultation interface."""

import re
from pathlib import Path

import demo.app as demo_app
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
    assert "Local offline simulation" in page
    assert "Direct identifiers are masked before scoring" in page
    assert "real-time deployment" not in page.lower()


def test_demo_responses_disable_caching():
    app.config.update(TESTING=True)

    with app.test_client() as client:
        response = client.get("/")

    assert response.headers["Cache-Control"] == "no-store, max-age=0"
    assert response.headers["Pragma"] == "no-cache"
    assert response.headers["Referrer-Policy"] == "no-referrer"


def test_new_conversation_uses_server_generated_opaque_id(monkeypatch):
    app.config.update(TESTING=True)
    demo_app._conversations.clear()
    monkeypatch.setattr(demo_app, "get_stack", lambda: object())
    monkeypatch.setattr(demo_app, "new_conversation", lambda stack: object())

    with app.test_client() as client:
        response = client.post("/api/new", json={"conv_id": "person@example.com"})

    assert response.status_code == 200
    conv_id = response.get_json()["conv_id"]
    assert re.fullmatch(r"local_[0-9a-f]{32}", conv_id)
    assert "person@example.com" not in demo_app._conversations
    demo_app._conversations.clear()


def test_message_rejects_unknown_user_supplied_conversation_id(monkeypatch):
    app.config.update(TESTING=True)
    demo_app._conversations.clear()
    monkeypatch.setattr(demo_app, "get_stack", lambda: object())
    monkeypatch.setattr(demo_app, "new_conversation", lambda stack: object())

    with app.test_client() as client:
        response = client.post(
            "/api/message",
            json={"conv_id": "person@example.com", "author": "user_A", "text": "hello"},
        )

    assert response.status_code == 404
    assert "person@example.com" not in demo_app._conversations


def test_reset_rejects_non_string_conversation_id():
    app.config.update(TESTING=True)

    with app.test_client() as client:
        response = client.post("/api/reset", json={"conv_id": ["not", "a", "key"]})

    assert response.status_code == 400


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

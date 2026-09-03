"""Flask application for the local frozen-model demonstration."""

from __future__ import annotations

import sys
from pathlib import Path

from flask import Flask, jsonify, render_template, request

# Add parent directories to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scoring_engine import LiveDemoEngine
from scenarios import SCENARIOS
from privacy import redact_text


app = Flask(__name__, template_folder="templates", static_folder="static")

# Initialize engine globally on server start
_engine = None


METHOD_LABELS = (
    ("keyword", "Keyword rule"),
    ("raw_layer1", "Maximum Layer 1"),
    ("weighted", "Weighted scorer"),
    ("lstm_trajectory7", "Primary LSTM"),
    ("lstm_enhanced775", "Enhanced LSTM"),
)


def build_chapter4_summary(eval_report: dict) -> dict:
    """Extract display values from the already-frozen final evaluation report."""
    audit = eval_report["audit"]
    metrics = eval_report["metrics"]
    primary = metrics["lstm_trajectory7"]["point_estimate"]
    weighted = metrics["weighted"]["point_estimate"]
    paired = eval_report["paired_component_bootstrap_differences"]
    matched = paired["lstm_trajectory7_minus_weighted"]["differences"]
    enhanced = paired["lstm_trajectory7_minus_lstm_enhanced775"]["differences"]

    methods = []
    for key, label in METHOD_LABELS:
        point = metrics[key]["point_estimate"]
        methods.append(
            {
                "key": key,
                "label": label,
                "pr_auc": point["pr_auc"],
                "f0_5": point["f0_5"],
                "precision": point["precision"],
                "recall": point["recall"],
                "primary": key == "lstm_trajectory7",
            }
        )

    return {
        "conversations": audit["conversations"],
        "positive_conversations": audit["positive_conversations"],
        "negative_conversations": audit["conversations"] - audit["positive_conversations"],
        "components": audit["components"],
        "primary": primary,
        "methods": methods,
        "matched_pr_auc": matched["pr_auc"],
        "matched_f0_5": matched["f0_5"],
        "weighted_false_positives": weighted["fp"],
        "weighted_false_negatives": weighted["fn"],
        "enhanced_comparison_inconclusive": (
            enhanced["pr_auc"]["lower"] <= 0 <= enhanced["pr_auc"]["upper"]
            and enhanced["f0_5"]["lower"] <= 0 <= enhanced["f0_5"]["upper"]
        ),
        "source_hash": eval_report["canonical_payload_sha256"],
    }


def get_engine() -> LiveDemoEngine:
    global _engine
    if _engine is None:
        _engine = LiveDemoEngine()
    return _engine


@app.after_request
def prevent_caching(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/")
def index():
    engine = get_engine()
    lstm_metrics = (
        engine.eval_report.get("metrics", {})
        .get("lstm_trajectory7", {})
        .get("point_estimate", {})
    )
    return render_template(
        "index.html",
        scenarios=SCENARIOS,
        chapter4=build_chapter4_summary(engine.eval_report),
        endpoint=engine.endpoint,
        lstm_metrics=lstm_metrics,
        keyword_term_count=len(engine.keyword_terms),
        spike_threshold=engine.spike_threshold,
        drop_threshold=engine.drop_threshold,
        lstm_threshold=engine.lstm_threshold,
        weighted_threshold=engine.weighted_threshold,
        raw_l1_threshold=engine.raw_l1_threshold,
    )


@app.route("/api/scenarios", methods=["GET"])
def api_get_scenarios():
    return jsonify(SCENARIOS)


@app.route("/api/results", methods=["GET"])
def api_get_results():
    """Return the Chapter IV summary without rerunning final-test inference."""
    return jsonify(build_chapter4_summary(get_engine().eval_report))


@app.route("/api/score", methods=["POST"])
def api_score():
    engine = get_engine()
    payload = request.get_json(silent=True) or {}
    history = payload.get("history", [])

    if not isinstance(history, list) or len(history) == 0:
        return jsonify({"error": "history must be a non-empty list of turns"}), 400

    # Validate each turn
    for turn in history:
        if not isinstance(turn, dict) or "text" not in turn or "author" not in turn:
            return jsonify({"error": "Each turn must contain 'text' and 'author'"}), 400
        if turn["author"] not in {"user_A", "user_B"}:
            return jsonify({"error": "author must be 'user_A' or 'user_B'"}), 400
        if not isinstance(turn["text"], str) or not turn["text"].strip():
            return jsonify({"error": "text must be a non-empty string"}), 400
        if len(turn["text"]) > 800:
            return jsonify({"error": "text must not exceed 800 characters"}), 400

    sanitized_history = [
        {"author": turn["author"], "text": redact_text(turn["text"].strip())}
        for turn in history
    ]
    result = engine.score_turn(sanitized_history)
    result["sanitized_history"] = sanitized_history
    return jsonify(result)


@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({
        "status": "healthy",
        "model": "Primary Trajectory LSTM (7-d)",
        "l1_backbone": "DistilBERT (Author-Proxy Fine-Tuned)",
        "endpoint": get_engine().endpoint,
        "version": "2026.09.03-chapter4-demo"
    })


def main():
    print("=" * 70)
    print("  WASD Conversation Model Demo")
    print("=" * 70)
    get_engine()
    print("\n* Web server running at: http://127.0.0.1:5000")
    print("* Open http://127.0.0.1:5000 in your browser to begin live interactive testing.")
    print("* Press Ctrl+C in this terminal to stop the server.\n")
    app.run(debug=False, host="127.0.0.1", port=5000)


if __name__ == "__main__":
    main()

"""Flask application for the local F2-policy, frozen-model demonstration."""

from __future__ import annotations

import sys
import json
from datetime import datetime
from itertools import count
from time import perf_counter
from pathlib import Path

from flask import Flask, jsonify, render_template, request

# Add parent directories to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scoring_engine import LiveDemoEngine
from scenarios import SCENARIOS as SYNTHETIC_SCENARIOS
from dataset_examples import load_dataset_examples

SCENARIOS = SYNTHETIC_SCENARIOS + load_dataset_examples()
from privacy import redact_text


app = Flask(__name__, template_folder="templates", static_folder="static")

# Initialize engine globally on server start
_engine = None
_request_numbers = count(1)


METHOD_LABELS = (
    ("keyword", "Keyword rule"),
    ("raw_layer1", "Maximum Layer 1"),
    ("weighted", "Weighted scorer"),
    ("lstm_trajectory7", "Trajectory-Feature LSTM"),
    ("lstm_enhanced775", "Embedding-and-Feature LSTM"),
)


def build_chapter4_summary(eval_report: dict, f2_report: dict) -> dict:
    """Display the recorded F2 reanalysis without re-running test inference."""
    audit = eval_report["audit"]
    metrics = f2_report["results"]
    primary = metrics["lstm_trajectory7"]["test"]
    weighted = metrics["weighted"]["test"]
    matched = f2_report["paired_differences"]["weighted"]
    enhanced = f2_report["paired_differences"]["lstm_enhanced775"]

    methods = []
    for key, label in METHOD_LABELS:
        point = metrics[key]["test"]
        methods.append(
            {
                "key": key,
                "label": label,
                "pr_auc": point["pr_auc"],
                "f2": point["f2"],
                "precision": point["precision"],
                "recall": point["recall"],
                "fp": point["fp"],
                "fn": point["fn"],
                "is_lstm": key in {"lstm_trajectory7", "lstm_enhanced775"},
            }
        )

    return {
        "conversations": audit["conversations"],
        "positive_conversations": audit["positive_conversations"],
        "negative_conversations": audit["conversations"] - audit["positive_conversations"],
        "components": audit["components"],
        "primary": primary,
        "embedding_model": metrics["lstm_enhanced775"]["test"],
        "methods": methods,
        "matched_pr_auc": matched["pr_auc"],
        "matched_f2": matched["f2"],
        "weighted_false_positives": weighted["fp"],
        "weighted_false_negatives": weighted["fn"],
        "enhanced_comparison_inconclusive": (
            enhanced["pr_auc"]["lower"] <= 0 <= enhanced["pr_auc"]["upper"]
            and enhanced["f2"]["lower"] <= 0 <= enhanced["f2"]["upper"]
        ),
        "source_status": f2_report["status"],
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
    return render_template(
        "index.html",
        scenarios=SCENARIOS,
        chapter4=build_chapter4_summary(engine.eval_report, engine.f2_report),
        endpoint=engine.endpoint,
        keyword_term_count=len(engine.keyword_terms),
        spike_threshold=engine.spike_threshold,
        drop_threshold=engine.drop_threshold,
        lstm_threshold=engine.lstm_threshold,
        enhanced_lstm_threshold=engine.enhanced_lstm_threshold,
        weighted_threshold=engine.weighted_threshold,
        raw_l1_threshold=engine.raw_l1_threshold,
    )


@app.route("/api/scenarios", methods=["GET"])
def api_get_scenarios():
    return jsonify(SCENARIOS)


@app.route("/api/results", methods=["GET"])
def api_get_results():
    """Return the Chapter IV summary without rerunning final-test inference."""
    engine = get_engine()
    return jsonify(build_chapter4_summary(engine.eval_report, engine.f2_report))


@app.route("/api/score", methods=["POST"])
def api_score():
    engine = get_engine()
    payload = request.get_json(silent=True) or {}
    history = payload.get("history", [])
    model_choice = payload.get("model", "both")
    model_choices = {
        "primary": ("lstm",),
        "enhanced": ("enhanced_lstm",),
        "both": ("lstm", "enhanced_lstm"),
    }
    if model_choice not in model_choices:
        return jsonify({"error": "model must be primary, enhanced, or both"}), 400

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
    request_number = next(_request_numbers)
    started = perf_counter()

    def report(message: str) -> None:
        if app.config.get("BENCHMARK_QUIET", False):
            return
        stamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{stamp} | request {request_number}] {message}", flush=True)

    latest = sanitized_history[-1]
    if not app.config.get("BENCHMARK_QUIET", False):
        print("\n" + "-" * 90, flush=True)
    report(f"NEW MESSAGE | turn {len(sanitized_history)} | {latest['author']}")
    report("Text: " + json.dumps(latest["text"], ensure_ascii=True))
    report("Recomputing the conversation history with the frozen models on CPU.")
    try:
        result = engine.score_turn(sanitized_history, progress=report, models=model_choices[model_choice])
    except Exception as error:
        report(f"FAILED: {type(error).__name__}: {error}")
        raise
    for key, label in (("lstm", "Trajectory-Feature LSTM"), ("enhanced_lstm", "Embedding-and-Feature LSTM"), ("weighted", "Weighted scorer"), ("raw_layer1", "Maximum Layer 1")):
        if key not in result["decision"]:
            continue
        decision = result["decision"][key]
        status = "FLAGGED" if decision["flagged"] else "below threshold"
        report(f"{label}: {decision['score']:.4f} / {decision['threshold']:.4f} -> {status}")
    keyword = result["decision"]["keyword"]
    report("Keyword rule: " + ("FLAGGED | " + ", ".join(keyword["matched_terms"]) if keyword["flagged"] else "no matches"))
    report(f"DONE | {len(sanitized_history)} turns | {perf_counter() - started:.2f}s")
    result["sanitized_history"] = sanitized_history
    return jsonify(result)


@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({
        "status": "healthy",
        "model": "Trajectory-Feature LSTM (7 inputs) and Embedding-and-Feature LSTM (775 inputs)",
        "l1_backbone": "DistilBERT (Author-Proxy Fine-Tuned)",
        "endpoint": get_engine().endpoint,
        "version": "2026.10.01-simplified-f2-demo"
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

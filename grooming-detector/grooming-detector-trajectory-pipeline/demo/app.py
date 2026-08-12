"""
Demo mode B - locally typed chat processed as offline sequential replay.

A minimal Flask app. Two roleplaying participants type messages alternately,
and each message is processed as the next turn in a local offline simulation.
The UI shows the Layer 1 input, the author-disjoint LSTM score, the weighted
comparator, trajectory features, and the first LSTM-flagged turn.

This is the panelist-facing mechanics demo. It demonstrates that a typed
conversation can flow through the two-layer software stack and that the LSTM
updates turn by turn. It is not performance evidence, a grooming probability,
or a deployment-ready safety determination.

Run:
    python -m demo.app
Then open http://127.0.0.1:5000 in a browser.
"""

import json
import sys
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from demo.scoring_core import build_scoring_stack, new_conversation


app = Flask(__name__, template_folder="templates", static_folder="static")
EVALUATION_REPORT = Path(__file__).resolve().parent.parent / "lstm_author_disjoint_evaluation.json"

# Loaded once at startup; the scoring stack is heavy.
_stack = None
_conversations = {}  # conv_id -> LiveConversation


@app.after_request
def prevent_sensitive_response_caching(response):
    """Keep locally entered demonstration text out of browser/proxy caches."""

    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


def get_stack():
    global _stack
    if _stack is None:
        _stack = build_scoring_stack()
    return _stack


@app.route("/")
def index():
    report = json.loads(EVALUATION_REPORT.read_text(encoding="utf-8"))
    return render_template("chat.html", evaluation=report["held_out_test"])


@app.route("/api/new", methods=["POST"])
def api_new_conversation():
    # Generate an opaque identifier rather than accepting user-provided names or
    # account handles as storage keys.
    conv_id = f"local_{uuid.uuid4().hex}"
    _conversations[conv_id] = new_conversation(get_stack())
    return jsonify({"conv_id": conv_id})


@app.route("/api/message", methods=["POST"])
def api_message():
    payload = request.get_json(silent=True) or {}
    conv_id = payload.get("conv_id")
    text = payload.get("text")
    author = payload.get("author", "user_A")

    if not isinstance(conv_id, str) or not isinstance(text, str):
        return jsonify({"error": "conv_id and text are required"}), 400
    if author not in {"user_A", "user_B"}:
        return jsonify({"error": "author must be user_A or user_B"}), 400
    if len(text) > 1000:
        return jsonify({"error": "message exceeds 1000 characters"}), 400

    if conv_id not in _conversations:
        return jsonify({"error": "unknown conversation; start a new local session"}), 404
    conv = _conversations[conv_id]

    result = conv.add_message(text, author)
    if result is None:
        return jsonify({"error": "empty message"}), 400
    return jsonify(result)


@app.route("/api/reset", methods=["POST"])
def api_reset():
    payload = request.get_json(silent=True) or {}
    conv_id = payload.get("conv_id")
    if not isinstance(conv_id, str):
        return jsonify({"error": "conv_id is required"}), 400
    if conv_id in _conversations:
        del _conversations[conv_id]
    return jsonify({"ok": True})


if __name__ == "__main__":
    # Warm the stack up-front so the first request isn't slow.
    print("Warming up provisional fixed-Layer-1 LSTM scoring stack...")
    get_stack()
    print("Ready.")
    app.run(debug=False, host="127.0.0.1", port=5000)

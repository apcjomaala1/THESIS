"""Frozen-artifact inference engine for the interactive thesis demonstration.

The accepted Layer 1 DistilBERT and selected seven-feature trajectory LSTM run
unchanged. All thresholds, features, comparator weights, architecture settings,
base-encoder settings, and keyword terms come from frozen experiment artifacts.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

# Ensure PyTorch avoids heavy CUDA DLL allocations when running CPU inference
os.environ["CUDA_MODULE_LOADING"] = "LAZY"

import numpy as np
import torch
from transformers import AutoModel, AutoModelForSequenceClassification, AutoTokenizer

from revised_pipeline.features import FEATURE_NAMES, compute_sequence_features
from revised_pipeline.keyword import candidate_terms
from revised_pipeline.lstm import ConversationOnlyLSTM, LSTMConfig


PIPELINE_ROOT = Path(__file__).resolve().parent.parent
REVISED_RUNS = PIPELINE_ROOT / "revised_runs"
FROZEN_PROTOCOL_PATH = REVISED_RUNS / "frozen_protocol.json"
FINAL_EVALUATION_PATH = REVISED_RUNS / "final_results" / "final_evaluation.json"


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _resolve_recorded_path(recorded_path: str) -> Path:
    """Resolve a frozen artifact if the workspace was moved after freezing."""
    path = Path(recorded_path)
    if path.exists():
        return path
    parts = list(path.parts)
    for marker, local_root in (
        ("grooming-detector-trajectory-pipeline", PIPELINE_ROOT),
        ("grooming-detector", PIPELINE_ROOT.parent),
    ):
        if marker in parts:
            relocated = local_root.joinpath(*parts[parts.index(marker) + 1 :])
            if relocated.exists():
                return relocated
    raise FileNotFoundError(f"Frozen artifact is unavailable: {recorded_path}")

class LiveDemoEngine:
    def __init__(self) -> None:
        print("=" * 60)
        print("  Loading frozen DistilBERT and trajectory artifacts...")
        print("=" * 60)
        self.device = torch.device("cpu")

        self.frozen_protocol = _read_json(FROZEN_PROTOCOL_PATH)
        if self.frozen_protocol.get("score_comparison") != ">= threshold":
            raise ValueError("Unsupported frozen score-comparison rule")
        self.endpoint = str(self.frozen_protocol["endpoint"])
        roles = self.frozen_protocol["artifact_roles"]

        layer1_run = _resolve_recorded_path(roles["layer1_run"]["path"])
        development_cache = _resolve_recorded_path(roles["development_cache"]["path"])
        centroid_dir = _resolve_recorded_path(roles["centroid"]["path"])
        comparator_dir = _resolve_recorded_path(roles["comparators"]["path"])
        keyword_dir = _resolve_recorded_path(roles["keyword"]["path"])
        lstm_run = _resolve_recorded_path(roles["lstm_trajectory7"]["path"])

        cache_config = _read_json(development_cache / "train" / "manifest.json")
        feature_config = _read_json(comparator_dir / "feature_config.json")
        weighted_config = _read_json(comparator_dir / "weighted_scorer_config.json")
        raw_config = _read_json(comparator_dir / "raw_layer1_config.json")
        keyword_config = _read_json(keyword_dir / "keyword_config.json")
        lstm_config = _read_json(lstm_run / "run_configuration.json")
        lstm_threshold_config = _read_json(lstm_run / "selected_threshold.json")

        if feature_config.get("spike_comparison") != "score > spike_threshold":
            raise ValueError("Unsupported frozen spike-comparison rule")
        if weighted_config.get("aggregation") != "max":
            raise ValueError("Unsupported frozen weighted aggregation")
        if raw_config.get("aggregation") != "max":
            raise ValueError("Unsupported frozen Layer 1 aggregation")

        self.context_turns = int(cache_config["context_turns"])
        self.max_length = int(cache_config["max_length"])
        base_model_name = str(cache_config["provenance"]["base_encoder_name"])
        layer1_model_dir = layer1_run / "best_model"

        print(f"Loading Layer 1 DistilBERT from: {layer1_model_dir}")
        self.classifier_tokenizer = AutoTokenizer.from_pretrained(
            layer1_model_dir, local_files_only=True, use_fast=True
        )
        self.l1_model = AutoModelForSequenceClassification.from_pretrained(
            layer1_model_dir, local_files_only=True
        ).to(self.device)
        self.l1_model.eval()

        print(f"Loading frozen base encoder: {base_model_name}")
        self.base_tokenizer = AutoTokenizer.from_pretrained(
            base_model_name, local_files_only=True, use_fast=True
        )
        self.base_encoder = AutoModel.from_pretrained(
            base_model_name, local_files_only=True
        ).to(self.device)
        self.base_encoder.eval()

        self.benign_centroid = np.load(centroid_dir / "benign_centroid.npy").astype(
            np.float32
        )
        self.spike_threshold = float(feature_config["spike_threshold"])
        self.drop_threshold = float(feature_config["drop_threshold"])

        self.weighted_weights = np.asarray(
            weighted_config["weights"], dtype=np.float64
        )
        self.weighted_weights /= self.weighted_weights.sum()
        self.weighted_threshold = float(weighted_config["threshold"])
        self.raw_l1_threshold = float(raw_config["threshold"])

        expected_keyword_rule = (
            "positive when any turn contains at least one frozen term"
        )
        if keyword_config.get("decision_rule") != expected_keyword_rule:
            raise ValueError("Unsupported frozen keyword decision rule")
        self.keyword_terms = frozenset(
            str(row["term"]) for row in keyword_config["lexicon"]
        )

        model_config = LSTMConfig(**lstm_config["config"])
        if model_config.input_mode != "trajectory7":
            raise ValueError("The live demo requires the selected trajectory7 model")
        self.lstm = ConversationOnlyLSTM.build(model_config).to(self.device)
        checkpoint = torch.load(
            lstm_run / "best_model.pt", map_location=self.device, weights_only=False
        )
        self.lstm.load_state_dict(checkpoint["model_state"])
        self.lstm.eval()
        self.lstm_threshold = float(lstm_threshold_config["threshold"])

        self.eval_report = (
            _read_json(FINAL_EVALUATION_PATH) if FINAL_EVALUATION_PATH.exists() else {}
        )
        if self.eval_report and self.eval_report.get("endpoint") != self.endpoint:
            raise ValueError("Frozen protocol and final evaluation endpoints disagree")

        print("  [OK] Frozen neural models and comparison artifacts loaded on CPU.")
        print("=" * 60)

    def score_turn(
        self, conversation_history: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Score the current conversation prefix with the frozen pipeline."""
        turn_count = len(conversation_history)
        if turn_count == 0:
            return {"error": "Empty conversation"}

        texts = [turn["text"].strip() for turn in conversation_history]
        authors = [turn["author"] for turn in conversation_history]
        speaker_indices = np.asarray(
            [0 if author == "user_A" else 1 for author in authors], dtype=np.int64
        )

        proxy_scores: list[float] = []
        embeddings: list[np.ndarray] = []
        contexts: list[str] = []

        with torch.inference_mode():
            for index in range(turn_count):
                first = max(0, index - self.context_turns)
                context = " [SEP] ".join(texts[first : index + 1])
                contexts.append(context)

                encoded_context = self.classifier_tokenizer(
                    context,
                    padding=True,
                    truncation=True,
                    max_length=self.max_length,
                    return_tensors="pt",
                )
                encoded_context = {
                    key: value.to(self.device)
                    for key, value in encoded_context.items()
                    if key != "token_type_ids"
                }
                logits = self.l1_model(**encoded_context).logits
                proxy_scores.append(
                    float(torch.softmax(logits.float(), dim=-1)[0, 1].item())
                )

                encoded_current = self.base_tokenizer(
                    texts[index],
                    padding=True,
                    truncation=True,
                    max_length=self.max_length,
                    return_tensors="pt",
                )
                encoded_current = {
                    key: value.to(self.device)
                    for key, value in encoded_current.items()
                    if key != "token_type_ids"
                }
                embedding = self.base_encoder(
                    **encoded_current
                ).last_hidden_state[:, 0, :]
                embeddings.append(
                    embedding.float().cpu().numpy()[0].astype(np.float32)
                )

        score_array = np.asarray(proxy_scores, dtype=np.float32)
        embedding_array = np.asarray(embeddings, dtype=np.float32)

        features = compute_sequence_features(
            score_array,
            embedding_array,
            speaker_indices,
            self.benign_centroid,
            self.spike_threshold,
            self.drop_threshold,
        )

        values = torch.from_numpy(features).unsqueeze(0).to(self.device)
        lengths = torch.tensor([turn_count], dtype=torch.long, device=self.device)
        with torch.inference_mode():
            turn_logits, _final_logits = self.lstm(values, lengths)
            lstm_scores = torch.sigmoid(turn_logits.float()).squeeze(0).cpu().numpy()

        weighted_raw = np.asarray(features, dtype=np.float64) @ self.weighted_weights
        weighted_turn_scores = 1.0 / (
            1.0 + np.exp(-np.clip(weighted_raw, -80.0, 80.0))
        )
        weighted_max_so_far = np.maximum.accumulate(weighted_turn_scores)
        raw_l1_max_so_far = np.maximum.accumulate(score_array)

        matched_terms_so_far: list[list[str]] = []
        accumulated_terms: set[str] = set()
        for text in texts:
            accumulated_terms.update(candidate_terms(text) & self.keyword_terms)
            matched_terms_so_far.append(sorted(accumulated_terms))

        latest_index = turn_count - 1
        latest_lstm = float(lstm_scores[latest_index])
        latest_weighted = float(weighted_max_so_far[latest_index])
        latest_raw_l1 = float(raw_l1_max_so_far[latest_index])
        latest_keyword_terms = matched_terms_so_far[latest_index]

        turn_history = []
        for index in range(turn_count):
            row = features[index]
            turn_history.append(
                {
                    "turn": index + 1,
                    "author": authors[index],
                    "text": texts[index],
                    "context": contexts[index],
                    "layer1_score": round(float(score_array[index]), 4),
                    "lstm_score": round(float(lstm_scores[index]), 4),
                    "weighted_score": round(
                        float(weighted_turn_scores[index]), 4
                    ),
                    "proxy_spike": bool(
                        score_array[index] > self.spike_threshold
                    ),
                    "features": {
                        name: (
                            bool(row[position])
                            if name == "spike_then_drop"
                            else int(row[position])
                            if name == "spike_count"
                            else round(float(row[position]), 4)
                        )
                        for position, name in enumerate(FEATURE_NAMES)
                    },
                    "lstm_flagged": bool(
                        lstm_scores[index] >= self.lstm_threshold
                    ),
                }
            )

        return {
            "turns_count": turn_count,
            "latest_turn": turn_history[-1],
            "history": turn_history,
            "endpoint": self.endpoint,
            "decision": {
                "lstm": {
                    "score": round(latest_lstm, 4),
                    "threshold": self.lstm_threshold,
                    "flagged": latest_lstm >= self.lstm_threshold,
                },
                "weighted": {
                    "score": round(latest_weighted, 4),
                    "threshold": self.weighted_threshold,
                    "flagged": latest_weighted >= self.weighted_threshold,
                },
                "raw_layer1": {
                    "score": round(latest_raw_l1, 4),
                    "threshold": self.raw_l1_threshold,
                    "flagged": latest_raw_l1 >= self.raw_l1_threshold,
                },
                "keyword": {
                    "flagged": bool(latest_keyword_terms),
                    "matched_terms": latest_keyword_terms,
                },
            },
            "trajectory_curve": {
                "turns": list(range(1, turn_count + 1)),
                "lstm_scores": [round(float(score), 4) for score in lstm_scores],
                "lstm_flags": [
                    bool(score >= self.lstm_threshold) for score in lstm_scores
                ],
                "layer1_scores": [round(float(score), 4) for score in score_array],
                "topic_distances": [
                    round(float(score), 4) for score in features[:, 5]
                ],
                "lstm_threshold": self.lstm_threshold,
                "spike_threshold": self.spike_threshold,
            },
        }

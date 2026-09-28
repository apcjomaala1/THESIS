"""Frozen-model inference engine with recorded validation-selected F2 cutoffs.

Both selected LSTM checkpoints, Layer 1, features, comparator weights, and
keyword resources remain unchanged. Only final conversation decision cutoffs
come from the separate F2 reanalysis receipt.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any, Callable

# Ensure PyTorch avoids heavy CUDA DLL allocations when running CPU inference
os.environ["CUDA_MODULE_LOADING"] = "LAZY"

import numpy as np
import torch
from transformers import AutoModel, AutoModelForSequenceClassification, AutoTokenizer

from revised_pipeline.features import FEATURE_NAMES, compute_sequence_features
from revised_pipeline.keyword import candidate_terms
from revised_pipeline.lstm import load_lstm_checkpoint


PIPELINE_ROOT = Path(__file__).resolve().parent.parent
REVISED_RUNS = PIPELINE_ROOT / "revised_runs"
FROZEN_PROTOCOL_PATH = REVISED_RUNS / "frozen_protocol.json"
FINAL_EVALUATION_PATH = REVISED_RUNS / "final_results" / "final_evaluation.json"
F2_RESULTS_PATH = PIPELINE_ROOT.parents[1] / "thesis_docs" / ".threshold_analysis" / "f2_test_reanalysis.json"
F2_VALIDATION_PATH = PIPELINE_ROOT.parents[1] / "thesis_docs" / ".threshold_analysis" / "validation_f1_comparison.json"


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
        enhanced_run = _resolve_recorded_path(roles["lstm_enhanced775"]["path"])

        cache_config = _read_json(development_cache / "train" / "manifest.json")
        feature_config = _read_json(comparator_dir / "feature_config.json")
        weighted_config = _read_json(comparator_dir / "weighted_scorer_config.json")
        raw_config = _read_json(comparator_dir / "raw_layer1_config.json")
        keyword_config = _read_json(keyword_dir / "keyword_config.json")
        self.f2_report = _read_json(F2_RESULTS_PATH)
        if self.f2_report.get("status") != "REVISED_F2_POLICY_ON_PREVIOUSLY_EVALUATED_TEST_SCORES":
            raise ValueError("F2 result receipt has an unexpected status")
        if not self.f2_report.get("validation_selection_verified_before_test_read") or self.f2_report.get("test_threshold_search"):
            raise ValueError("F2 receipt does not document validation-only cutoff selection")
        validation_selection = _read_json(F2_VALIDATION_PATH)
        selected_cutoffs = {
            row["method"]: float(row["f2_selected_threshold"])
            for row in validation_selection["results"]
        }
        for key, label in (
            ("lstm_trajectory7", "Primary LSTM"),
            ("lstm_enhanced775", "Enhanced LSTM"),
            ("raw_layer1", "Maximum Layer 1"),
            ("weighted", "Weighted scorer"),
            ("keyword", "Keyword rule"),
        ):
            recorded_cutoff = float(self.f2_report["results"][key]["validation"]["threshold"])
            if not math.isclose(recorded_cutoff, selected_cutoffs[label], rel_tol=0, abs_tol=1e-12):
                raise ValueError(f"F2 cutoff differs from saved validation selection: {label}")

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
        f2_results = self.f2_report["results"]
        self.weighted_threshold = float(f2_results["weighted"]["validation"]["threshold"])
        self.raw_l1_threshold = float(f2_results["raw_layer1"]["validation"]["threshold"])

        expected_keyword_rule = (
            "positive when any turn contains at least one frozen term"
        )
        if keyword_config.get("decision_rule") != expected_keyword_rule:
            raise ValueError("Unsupported frozen keyword decision rule")
        self.keyword_terms = frozenset(
            str(row["term"]) for row in keyword_config["lexicon"]
        )

        self.lstm, _, _ = load_lstm_checkpoint(lstm_run, "trajectory7", "cpu")
        self.enhanced_lstm, _, _ = load_lstm_checkpoint(enhanced_run, "enhanced775", "cpu")
        self.lstm_threshold = float(f2_results["lstm_trajectory7"]["validation"]["threshold"])
        self.enhanced_lstm_threshold = float(f2_results["lstm_enhanced775"]["validation"]["threshold"])

        self.eval_report = (
            _read_json(FINAL_EVALUATION_PATH) if FINAL_EVALUATION_PATH.exists() else {}
        )
        if self.eval_report and self.eval_report.get("endpoint") != self.endpoint:
            raise ValueError("Frozen protocol and final evaluation endpoints disagree")

        print("  [OK] Frozen neural models and comparison artifacts loaded on CPU.")
        print("=" * 60)

    def score_turn(
        self, conversation_history: list[dict[str, Any]],
        progress: Callable[[str], None] | None = None,
        models: tuple[str, ...] = ("lstm", "enhanced_lstm"),
    ) -> dict[str, Any]:
        """Score the current conversation prefix with the frozen pipeline."""
        turn_count = len(conversation_history)
        report = progress if progress is not None else lambda message: None
        if turn_count == 0:
            return {"error": "Empty conversation"}
        if not models or set(models) - {"lstm", "enhanced_lstm"}:
            raise ValueError("models must select the Trajectory-Feature and/or Embedding-and-Feature LSTM")

        texts = [turn["text"].strip() for turn in conversation_history]
        authors = [turn["author"] for turn in conversation_history]
        speaker_indices = np.asarray(
            [0 if author == "user_A" else 1 for author in authors], dtype=np.int64
        )

        proxy_scores: list[float] = []
        embeddings: list[np.ndarray] = []
        contexts: list[str] = []

        report(f"[1/3] Running DistilBERT and base embeddings for all {turn_count} messages...")
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
                report(
                    f"  Message {index + 1:>2}/{turn_count}: Layer 1 = {proxy_scores[-1]:.4f}; "
                    f"context {first + 1}-{index + 1}; embedding ready"
                )

        score_array = np.asarray(proxy_scores, dtype=np.float32)
        embedding_array = np.asarray(embeddings, dtype=np.float32)

        report("[2/3] Computing the seven trajectory features...")
        features = compute_sequence_features(
            score_array,
            embedding_array,
            speaker_indices,
            self.benign_centroid,
            self.spike_threshold,
            self.drop_threshold,
        )

        report("  Latest features: " + ", ".join(
            f"{name}={float(value):.4f}" for name, value in zip(FEATURE_NAMES, features[-1])
        ))
        report(f"[3/3] Running selected LSTM(s) over the {turn_count}-turn sequence...")
        lengths = torch.tensor([turn_count], dtype=torch.long, device=self.device)
        lstm_scores = None
        enhanced_scores = None
        with torch.inference_mode():
            if "lstm" in models:
                values = torch.from_numpy(features).unsqueeze(0).to(self.device)
                turn_logits, _ = self.lstm(values, lengths)
                lstm_scores = torch.sigmoid(turn_logits.float()).squeeze(0).cpu().numpy()
            if "enhanced_lstm" in models:
                enhanced_values = np.concatenate([embedding_array, features], axis=1)
                values = torch.from_numpy(enhanced_values).unsqueeze(0).to(self.device)
                turn_logits, _ = self.enhanced_lstm(values, lengths)
                enhanced_scores = torch.sigmoid(turn_logits.float()).squeeze(0).cpu().numpy()

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
                    "lstm_score": round(float(lstm_scores[index]), 4) if lstm_scores is not None else None,
                    "enhanced_lstm_score": round(float(enhanced_scores[index]), 4) if enhanced_scores is not None else None,
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
                    "lstm_flagged": bool(lstm_scores[index] >= self.lstm_threshold) if lstm_scores is not None else None,
                    "enhanced_lstm_flagged": bool(enhanced_scores[index] >= self.enhanced_lstm_threshold) if enhanced_scores is not None else None,
                }
            )

        result = {
            "turns_count": turn_count,
            "latest_turn": turn_history[-1],
            "history": turn_history,
            "endpoint": self.endpoint,
            "decision": {
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
                "lstm_scores": [round(float(score), 4) for score in lstm_scores] if lstm_scores is not None else [],
                "lstm_flags": [bool(score >= self.lstm_threshold) for score in lstm_scores] if lstm_scores is not None else [],
                "enhanced_lstm_scores": [round(float(score), 4) for score in enhanced_scores] if enhanced_scores is not None else [],
                "enhanced_lstm_flags": [bool(score >= self.enhanced_lstm_threshold) for score in enhanced_scores] if enhanced_scores is not None else [],
                "layer1_scores": [round(float(score), 4) for score in score_array],
                "topic_distances": [
                    round(float(score), 4) for score in features[:, 5]
                ],
                "lstm_threshold": self.lstm_threshold,
                "enhanced_lstm_threshold": self.enhanced_lstm_threshold,
                "spike_threshold": self.spike_threshold,
            },
        }
        if lstm_scores is not None:
            score = float(lstm_scores[latest_index])
            result["decision"]["lstm"] = {
                "score": round(score, 4),
                "threshold": self.lstm_threshold,
                "flagged": score >= self.lstm_threshold,
            }
        if enhanced_scores is not None:
            score = float(enhanced_scores[latest_index])
            result["decision"]["enhanced_lstm"] = {
                "score": round(score, 4),
                "threshold": self.enhanced_lstm_threshold,
                "flagged": score >= self.enhanced_lstm_threshold,
            }
        return result

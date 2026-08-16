import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from revised_pipeline.cache import INDEX_COLUMNS, load_partition_cache
from revised_pipeline.centroid import build_training_centroid
from revised_pipeline.comparators import weighted_conversation_scores
from revised_pipeline.contracts import canonical_sha256, sha256_file
from revised_pipeline.data import build_context_records, load_eligible_rows
from revised_pipeline.features import compute_sequence_features
from revised_pipeline.dataset import ConversationSequence
from revised_pipeline.evaluate_final import _verify_final_cache
from revised_pipeline.lstm import (
    ConversationOnlyLSTM,
    LSTMConfig,
    load_lstm_checkpoint,
    predict_lstm_sequences,
    train_lstm,
    validate_lstm_run,
)
from revised_pipeline.lstm_search import run_search, validate_search
from revised_pipeline.metrics import (
    component_bootstrap_differences,
    component_bootstrap_intervals,
    conversation_metrics,
    select_f05_threshold,
)


def _write_cache_partition(root: Path, split: str = "train") -> Path:
    root.mkdir()
    index = pd.DataFrame(
        [
            ["pan12:n1:1", "pan12:n1", 1, "component_1", 0, 0, 0, "c1", "t1"],
            ["pan12:n1:2", "pan12:n1", 2, "component_1", 1, 0, 0, "c2", "t2"],
            ["pan12:n1:3", "pan12:n1", 3, "component_1", 0, 0, 0, "c3", "t3"],
            ["pan12:n2:1", "pan12:n2", 1, "component_2", 0, 0, 0, "c4", "t4"],
            ["pan12:p1:1", "pan12:p1", 1, "component_3", 0, 1, 1, "c5", "t5"],
            ["pan12:p1:2", "pan12:p1", 2, "component_3", 1, 0, 1, "c6", "t6"],
        ],
        columns=INDEX_COLUMNS,
    )
    scores = np.linspace(0.1, 0.6, len(index), dtype=np.float32)
    embeddings = np.zeros((len(index), 768), dtype=np.float32)
    embeddings[:3, 0] = 1.0
    embeddings[3, 1] = 1.0
    embeddings[4:, 2] = 1.0
    index.to_csv(root / "index.csv", index=False)
    np.save(root / "layer1_scores.npy", scores, allow_pickle=False)
    np.save(root / "base_embeddings.npy", embeddings, allow_pickle=False)
    record = {
        "schema_version": 1,
        "status": "complete",
        "split": split,
        "rows": len(index),
        "conversations": 3,
        "positive_conversations": 1,
        "positive_author_rows": 1,
        "row_id_sequence_sha256": canonical_sha256(index["row_id"].tolist()),
        "provenance": {
            "base_encoder_state_sha256": "base-model-digest",
            "base_encoder_config_sha256": "base-config-digest",
            "base_tokenizer": {"backend_sha256": "backend"},
            "torch_version": "test-torch",
            "transformers_version": "test-transformers",
        },
        "files": {
            "index.csv": sha256_file(root / "index.csv"),
            "layer1_scores.npy": sha256_file(root / "layer1_scores.npy"),
            "base_embeddings.npy": sha256_file(root / "base_embeddings.npy"),
        },
    }
    record["canonical_payload_sha256"] = canonical_sha256(record)
    (root / "manifest.json").write_text(json.dumps(record), encoding="utf-8")
    return root


def test_revised_loader_ignores_is_suspicious_and_preserves_duplicate_text(tmp_path):
    source = tmp_path / "pan.csv"
    pd.DataFrame(
        [
            {"conv_id": "c1", "line": 1, "author": "a", "text": "same", "is_predator": 0, "is_suspicious": "garbage"},
            {"conv_id": "c1", "line": 2, "author": "b", "text": "same", "is_predator": 1, "is_suspicious": None},
            {"conv_id": "c1", "line": 3, "author": "a", "text": "end", "is_predator": 0, "is_suspicious": 99},
        ]
    ).to_csv(source, index=False)
    frame = load_eligible_rows(source)
    frame["split"] = "train"
    contexts = build_context_records(frame)
    assert "is_suspicious" not in frame.columns
    assert contexts["row_id"].is_unique
    assert contexts["context_text"].tolist() == [
        "same",
        "same [SEP] same",
        "same [SEP] same [SEP] end",
    ]


def test_exact_revised_features_use_any_prior_spike_and_turn_counts():
    scores = np.array([0.8, 0.75, 0.4, 0.6], dtype=np.float32)
    embeddings = np.zeros((4, 768), dtype=np.float32)
    embeddings[:, 0] = 1.0
    centroid = np.zeros(768, dtype=np.float32)
    centroid[0] = 1.0
    features = compute_sequence_features(
        scores,
        embeddings,
        np.array([0, 0, 1, 0]),
        centroid,
        spike_threshold=0.7,
        drop_threshold=0.3,
    )
    assert features.shape == (4, 7)
    assert features[:, 0].tolist() == pytest.approx([0.8, 0.8, 0.8, 0.8])
    assert features[:, 2].tolist() == [1, 2, 2, 2]
    assert features[:, 3].tolist() == [0, 0, 1, 1]
    assert features[:, 5].tolist() == pytest.approx([0, 0, 0, 0])
    assert features[:, 6].tolist() == pytest.approx([1.0, 1.0, 1 / 3, 0.5])


def test_spike_threshold_is_strict_by_approved_feature_definition():
    scores = np.array([0.5, 0.2], dtype=np.float32)
    embeddings = np.zeros((2, 768), dtype=np.float32)
    centroid = np.zeros(768, dtype=np.float32)
    features = compute_sequence_features(
        scores,
        embeddings,
        np.array([0, 1]),
        centroid,
        spike_threshold=0.5,
        drop_threshold=0.2,
    )
    assert features[:, 2].tolist() == [0.0, 0.0]
    assert features[:, 3].tolist() == [0.0, 0.0]


def test_threshold_selection_and_metrics_use_greater_than_or_equal():
    labels = np.array([0, 1, 1, 0], dtype=np.int8)
    scores = np.array([0.1, 0.8, 0.8, 0.7])
    threshold, metrics = select_f05_threshold(labels, scores)
    assert threshold == pytest.approx(0.8)
    assert metrics["tp"] == 2
    assert metrics["fp"] == 0
    assert metrics["f0_5"] == pytest.approx(1.0)


def test_weighted_scorer_accepts_seven_features_and_has_no_layer1_resigmoid():
    features = [
        np.array([[0.1] * 7, [0.8] * 7], dtype=np.float32),
        np.array([[0.2] * 7], dtype=np.float32),
    ]
    scores = weighted_conversation_scores(features, np.ones(7))
    assert scores.shape == (2,)
    assert scores[0] == pytest.approx(1 / (1 + np.exp(-0.8)))
    assert scores[1] == pytest.approx(1 / (1 + np.exp(-0.2)))


def test_centroid_is_training_only_conversation_balanced_and_excludes_positive(tmp_path):
    cache_dir = _write_cache_partition(tmp_path / "train")
    output = tmp_path / "centroid"
    record = build_training_centroid(cache_dir, output)
    centroid = np.load(output / "benign_centroid.npy")
    expected = np.zeros(768, dtype=np.float32)
    expected[0] = 1.0
    expected[1] = 1.0
    expected /= np.linalg.norm(expected)
    assert centroid == pytest.approx(expected)
    assert record["negative_conversations"] == 2
    assert record["negative_rows"] == 4
    assert "pan12:p1" not in (output / "source_negative_conversation_ids.txt").read_text()


def test_cache_loader_detects_alignment_tamper(tmp_path):
    cache_dir = _write_cache_partition(tmp_path / "train")
    load_partition_cache(cache_dir, expected_split="train")
    scores = np.load(cache_dir / "layer1_scores.npy")
    np.save(cache_dir / "layer1_scores.npy", scores[::-1], allow_pickle=False)
    with pytest.raises(ValueError, match="hash mismatch"):
        load_partition_cache(cache_dir, expected_split="train")


def test_final_cache_root_must_bind_the_loaded_child_partition(tmp_path):
    final_cache = tmp_path / "final_cache"
    final_cache.mkdir()
    child_dir = _write_cache_partition(final_cache / "final_test", "final_test")
    child = json.loads((child_dir / "manifest.json").read_text())
    root = {
        "schema_version": 1,
        "status": "complete",
        "splits": ["final_test"],
        "development_only": False,
        "final_test_scored": True,
        "historical_test_scored": False,
        "partition_manifest_payload_sha256": {"final_test": "wrong-child-hash"},
        "provenance": child["provenance"],
    }
    root["canonical_payload_sha256"] = canonical_sha256(root)
    (final_cache / "cache_manifest.json").write_text(json.dumps(root))
    with pytest.raises(ValueError, match="root and child"):
        _verify_final_cache(final_cache, {})


def test_lstm_primary_and_enhanced_dimensions_and_padding_invariance():
    torch = pytest.importorskip("torch")
    torch.manual_seed(4)
    primary = ConversationOnlyLSTM.build(
        LSTMConfig(input_mode="trajectory7", hidden_dim=8, num_layers=1, dropout=0.0)
    ).eval()
    enhanced = ConversationOnlyLSTM.build(
        LSTMConfig(input_mode="enhanced775", hidden_dim=8, num_layers=1, dropout=0.0)
    )
    assert primary.input_dim == 7
    assert enhanced.input_dim == 775
    short = torch.randn(1, 3, 7)
    padded = torch.cat([short, torch.randn(1, 4, 7)], dim=1)
    with torch.inference_mode():
        _turn_a, final_a = primary(short, torch.tensor([3]))
        _turn_b, final_b = primary(padded, torch.tensor([3]))
    assert torch.allclose(final_a, final_b, atol=1e-7)


def test_component_bootstrap_and_paired_comparison_are_group_aware():
    labels = np.array([0, 0, 1, 1], dtype=np.int8)
    scores = np.array([0.1, 0.2, 0.8, 0.9])
    components = np.array(["a", "a", "b", "c"])
    intervals = component_bootstrap_intervals(
        labels, scores, 0.5, components, replicates=30, seed=7
    )
    assert intervals["components"] == 3
    assert intervals["requested_replicates"] == 30
    paired = component_bootstrap_differences(
        labels,
        np.array([0.1, 0.2, 0.8, 0.9]),
        0.5,
        np.array([0.1, 0.8, 0.4, 0.9]),
        0.5,
        components,
        replicates=30,
        seed=7,
    )
    assert paired["components"] == 3
    assert paired["requested_replicates"] == 30


def test_conversation_only_lstm_cpu_training_and_reload_smoke(tmp_path):
    torch = pytest.importorskip("torch")
    sequences = []
    for index, label in enumerate([0, 1, 0, 1]):
        trajectory = np.zeros((2 + index, 7), dtype=np.float32)
        trajectory[:, 0] = 0.8 if label else 0.1
        sequences.append(
            ConversationSequence(
                conversation_id=f"c{index}",
                row_ids=[f"c{index}:{turn}" for turn in range(len(trajectory))],
                trajectory_features=trajectory,
                embeddings=np.zeros((len(trajectory), 768), dtype=np.float32),
                label=label,
            )
        )
    config = LSTMConfig(
        input_mode="trajectory7",
        hidden_dim=4,
        num_layers=1,
        dropout=0.0,
        epochs=1,
        batch_size=2,
        early_stopping_patience=1,
    )
    run_dir = tmp_path / "lstm"
    summary = train_lstm(
        sequences,
        sequences,
        run_dir,
        config,
        provenance={"test": True},
        device_name="cpu",
    )
    assert summary["status"] == "completed"
    checkpoint = torch.load(run_dir / "best_model.pt", weights_only=True)
    assert checkpoint["model_config"]["hidden_dim"] == 4
    model, loaded_config, device = load_lstm_checkpoint(
        run_dir, "trajectory7", "cpu"
    )
    ids, labels, scores = predict_lstm_sequences(
        sequences, model, loaded_config, device
    )
    assert ids == ["c0", "c1", "c2", "c3"]
    assert labels.tolist() == [0, 1, 0, 1]
    assert np.isfinite(scores).all()
    summary_path = run_dir / "run_summary.json"
    tampered_summary = json.loads(summary_path.read_text())
    tampered_summary["best_validation_pr_auc"] = 0.0
    summary_path.write_text(json.dumps(tampered_summary))
    with pytest.raises(ValueError, match="PR-AUC differs"):
        validate_lstm_run(run_dir, sequences, "trajectory7", "cpu")


def test_locked_lstm_search_runs_every_candidate_and_reproduces_selection(tmp_path):
    pytest.importorskip("torch")
    sequences = []
    for index, label in enumerate([0, 1, 0, 1]):
        trajectory = np.zeros((2, 7), dtype=np.float32)
        trajectory[:, 0] = 0.9 if label else 0.1
        sequences.append(
            ConversationSequence(
                conversation_id=f"s{index}",
                row_ids=[f"s{index}:0", f"s{index}:1"],
                trajectory_features=trajectory,
                embeddings=np.zeros((2, 768), dtype=np.float32),
                label=label,
            )
        )
    plan = {
        "schema_version": 1,
        "status": "LOCKED_BEFORE_REVISED_LAYER1_RETURN",
        "selection_partition": "validation",
        "checkpoint_objective": "maximum validation average precision",
        "common_config": {
            "epochs": 1,
            "batch_size": 2,
            "weight_decay": 0.0001,
            "gradient_clip": 1.0,
            "early_stopping_patience": 1,
            "seed": 42,
        },
        "modes": {
            "trajectory7": [
                {
                    "candidate_id": "tiny_t7",
                    "hidden_dim": 4,
                    "num_layers": 1,
                    "dropout": 0.0,
                    "learning_rate": 0.001,
                }
            ],
            "enhanced775": [
                {
                    "candidate_id": "tiny_e775",
                    "hidden_dim": 4,
                    "num_layers": 1,
                    "dropout": 0.0,
                    "learning_rate": 0.001,
                }
            ],
        },
        "final_test_used_for_selection": False,
        "excluded_historical_test_used_for_selection": False,
    }
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    search_dir = tmp_path / "search"
    selection = run_search(
        sequences,
        sequences,
        search_dir,
        "trajectory7",
        {"test": True},
        plan_path,
        "cpu",
    )
    assert selection["selected_candidate_id"] == "tiny_t7"
    validated = validate_search(
        search_dir, sequences, "trajectory7", plan_path, "cpu"
    )
    assert validated["selected_candidate_id"] == "tiny_t7"
    config_path = (
        search_dir / "candidates" / "tiny_t7" / "run_configuration.json"
    )
    tampered_config = json.loads(config_path.read_text())
    tampered_config["runtime"]["source_sha256"].pop("metrics.py")
    config_path.write_text(json.dumps(tampered_config))
    with pytest.raises(ValueError, match="source-hash inventory"):
        validate_search(search_dir, sequences, "trajectory7", plan_path, "cpu")

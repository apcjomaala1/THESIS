import numpy as np
import pytest
import torch

from demo.scoring_core import LiveConversation


class DummyClassifier:
    def score(self, text):
        return 0.6 if "risk" in text else 0.1


class DummyEncoder:
    def encode_single(self, text):
        value = 1.0 if "risk" in text else 0.0
        return np.full(768, value, dtype=np.float32)


class DummyWeightedScorer:
    spike_drop = 0.2
    flagging_threshold = 0.7

    def score_turn(self, trajectory):
        return float(trajectory[1])


class DummyLSTM(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.marker = torch.nn.Parameter(torch.zeros(1))

    def forward(self, x):
        scores = torch.full(x.shape[:2], 0.2, device=x.device)
        scores[:, -1] = 0.4 if x.shape[1] == 1 else 0.9
        return scores


def test_live_demo_flags_with_lstm_and_keeps_weighted_comparator():
    conv = LiveConversation(
        DummyClassifier(),
        DummyEncoder(),
        np.zeros(768, dtype=np.float32),
        DummyWeightedScorer(),
        DummyLSTM(),
        lstm_threshold=0.8,
    )

    first = conv.add_message("hello", "user_A")
    second = conv.add_message("risk text", "user_B")

    assert first["flagged_now"] is False
    assert first["first_flagged_turn"] is None
    assert first["lstm_score"] == pytest.approx(0.4)
    assert first["weighted_score"] == pytest.approx(0.1)

    assert second["flagged_now"] is True
    assert second["first_flagged_turn"] == 1
    assert second["lstm_score"] == pytest.approx(0.9)
    assert second["weighted_score"] == pytest.approx(0.6)
    assert second["lstm_threshold"] == pytest.approx(0.8)

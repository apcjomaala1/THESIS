"""
Feature extraction for the trajectory pipeline.

Two categories of features per conversation snapshot:
  1. The 768-dim DistilBERT embedding of the current message.
  2. A 7-dim trajectory feature vector computed over conversation history.

The trajectory features are operationalizations of behaviors described in the
Online Grooming Discourse Model (Lorenzo-Dus et al., 2016) — see the inline
notes on each feature for the specific OGDM construct each one targets.
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


# Default thresholds used by the preserved development pipeline. The historical
# Layer 1 target is now known to be invalid for message-level grooming, so 0.5
# is a development feature threshold rather than a validated safety rule.
# SPIKE_DROP is a hyperparameter and SHOULD be tuned on validation data only.
SPIKE_THRESHOLD = 0.5
DEFAULT_SPIKE_DROP = 0.2

TRAJECTORY_FEATURE_DIM = 7


# -- DistilBERT message encoder --

class MessageEncoder:
    """Wraps base DistilBERT to produce [CLS] embeddings for topic_drift / centroid use."""

    def __init__(self, device=None):
        # Lazy-imported so this file remains usable in environments where the
        # transformers / torch stack isn't installed (e.g., during tests of
        # the pure trajectory math).
        import torch
        from transformers import AutoTokenizer, DistilBertModel

        self._torch = torch
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Loading DistilBERT encoder on {self.device}")
        # The model is already cached as part of the project environment. Keep
        # demonstrations deterministic and prevent startup delays when the
        # consultation venue has no network access.
        self.tokenizer = AutoTokenizer.from_pretrained(
            "distilbert-base-uncased", local_files_only=True
        )
        self.model = DistilBertModel.from_pretrained(
            "distilbert-base-uncased", local_files_only=True
        )
        self.model.eval().to(self.device)

    def encode(self, texts, batch_size=32):
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            encoded = self.tokenizer(
                batch, padding=True, truncation=True, max_length=128, return_tensors="pt",
            )
            encoded = {k: v.to(self.device) for k, v in encoded.items()}
            encoded.pop("token_type_ids", None)
            with self._torch.no_grad():
                output = self.model(**encoded)
            cls = output.last_hidden_state[:, 0, :].cpu().numpy()
            all_embeddings.append(cls)
        return np.vstack(all_embeddings)

    def encode_single(self, text):
        return self.encode([text])[0]


# -- trajectory feature extraction --

def compute_trajectory_features(
    risk_scores_so_far,
    embeddings_so_far,
    texts_so_far,
    authors_so_far,
    benign_centroid,
    spike_drop=DEFAULT_SPIKE_DROP,
):
    """
    Build the 7-dim trajectory feature vector at the current turn.

    Args:
        risk_scores_so_far: list[float], one Layer 1 score per turn up to now.
        embeddings_so_far:  list[np.ndarray(768,)], one [CLS] embedding per turn.
        texts_so_far:       list[str], retained for call-site compatibility; the
            current seven-feature implementation does not read message text.
        authors_so_far:     list[str], author IDs. For multi-party conversations
            the dominant dyad (top-2 by turn count so far) is used for the
            turn-taking-imbalance feature, consistent with OGDM's dyadic framing.
        benign_centroid:    np.ndarray(768,), precomputed benign-chat centroid.
        spike_drop:         float, minimum drop magnitude that counts as a retreat.

    Returns:
        np.ndarray(7,) — features in the order:
            [peak_score, current_score, spike_count, spike_then_drop,
             rate_of_change, topic_drift, turn_taking_imbalance]
    """
    scores = np.asarray(risk_scores_so_far, dtype=np.float32)
    n = len(scores)

    # 1. Peak score so far. Operationalizes OGDM "score-suppression resistance":
    #    once a predatory turn has occurred, the trajectory should remember it
    #    even if subsequent turns are deliberately benign.
    peak_score = float(scores.max())

    # 2. Current turn risk score (Layer 1 output passed through unchanged).
    current_score = float(scores[-1])

    # 3. Spike count — how many turns crossed the binary decision boundary so far.
    spike_count = float((scores > SPIKE_THRESHOLD).sum())

    # 4. Spike-then-drop — binary flag for OGDM "compliance testing" pattern
    #    (Lorenzo-Dus et al., 2016, entrapment phase): a spike followed by a
    #    deliberate retreat of at least `spike_drop`.
    spike_then_drop = 0.0
    if n >= 2:
        for j in range(1, n):
            if scores[j - 1] > SPIKE_THRESHOLD and scores[j] < scores[j - 1] - spike_drop:
                spike_then_drop = 1.0
                break

    # 5. Rate of change — single-step delta. Captures sudden escalation /
    #    de-escalation between adjacent turns.
    rate_of_change = float(scores[-1] - scores[-2]) if n >= 2 else 0.0

    # 6. Topic drift — cosine distance from a fixed benign-chat centroid.
    #    Operationalizes OGDM "approach phase" (Lorenzo-Dus et al., 2016): the
    #    groomer steers conversation away from neutral small-talk toward
    #    personal / sexual content. Using a fixed centroid instead of the
    #    conversation's first message means the feature still fires when
    #    predators open with risky content.
    curr_emb = embeddings_so_far[-1].reshape(1, -1)
    centroid = benign_centroid.reshape(1, -1)
    topic_drift = float(1.0 - cosine_similarity(curr_emb, centroid)[0, 0])

    # 7. Turn-taking imbalance — absolute turn-count gap between the two
    #    most active participants ("dominant dyad"), normalized by their total
    #    words. Operationalizes OGDM "dominance and control" in the entrapment
    #    phase and is consistent with Villatoro-Tello et al. (2021)'s
    #    intervention-rate feature.
    #
    #    OGDM is dyadic; PAN12 contains many group chats (3-23 authors), so for
    #    multi-party conversations we operationalize the dyad as the top-2
    #    speakers by total turns contributed so far. This reduces exactly to
    #    the two-author formula when the conversation only has two speakers,
    #    and concentrates the feature on the predator + primary target — the
    #    two speakers grooming attention is empirically focused on.
    imbalance = 0.0
    if len(authors_so_far) >= 2:
        turns_by_author = {}
        for author in authors_so_far:
            turns_by_author[author] = turns_by_author.get(author, 0) + 1
        if len(turns_by_author) >= 2:
            top_two = sorted(turns_by_author.values(), reverse=True)[:2]
            a, b = top_two[0], top_two[1]
            total = a + b
            if total > 0:
                imbalance = float(abs(a - b) / total)

    return np.array(
        [peak_score, current_score, spike_count, spike_then_drop,
         rate_of_change, topic_drift, imbalance],
        dtype=np.float32,
    )


FEATURE_NAMES = [
    "peak_score", "current_score", "spike_count", "spike_then_drop",
    "rate_of_change", "topic_drift", "turn_taking_imbalance",
]

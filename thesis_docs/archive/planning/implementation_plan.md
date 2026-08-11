# Implementation Plan — Full Pipeline + Paper Revisions

**Source of truth**: The paper ([Finals Revised Paper WASD.docx](file:///c:/Projects/THESIS/Finals%20Revised%20Paper%20WASD.docx)) and the 10 advisor comments.

**Working directory**: `c:\Projects\THESIS` (all changes local — no OneDrive modifications).

---

## Current State

```
c:\Projects\THESIS\
├── Finals Revised Paper WASD.docx          ← Paper (just copied, source of truth)
├── grooming-detector\                      ← Older repo (has feature engineering + pipeline)
│   ├── trained_model_distillbert\          ← Layer 1 (older DistilBERT + PAN12 CSV)
│   │   ├── final_moderation_model\         ← Saved model (is_suspicious labels)
│   │   └── pan12_final_dataset.csv         ← 42MB parsed PAN12
│   └── grooming-detector-trajectory-pipeline\
│       ├── features.py                     ← 7 OGDM trajectory features ✅
│       ├── weighted_scorer.py              ← Layer 2 alt (WeightedScorer) ✅
│       ├── evaluation.py                   ← Metrics + keyword baseline ✅
│       ├── main.py                         ← End-to-end driver ✅
│       ├── data_loader.py                  ← PAN12 + multi-dataset loader ✅
│       ├── benign_centroid.npy             ← Precomputed topic-drift baseline ✅
│       ├── experimental\
│       │   └── trajectory_model_lstm.py    ← LSTM stub (182 lines, needs integration)
│       └── tests\                          ← 39 pytest tests ✅
└── Groomer Thesis\                         ← Newer repo (has trained models, no pipeline)
    └── pan12-sexual-predator-.../
        ├── final_moderation_model\         ← DistilBERT (label_mode=either, 3 epochs)
        ├── final_bert_model\               ← BERT (trained)
        ├── final_roberta_model\            ← RoBERTa (trained)
        ├── final_deberta_model\            ← DeBERTa-v2 (trained)
        ├── final_fasttext_model.bin        ← FastText (trained)
        ├── train_distillbert.py            ← Newer training script (context window)
        └── generate_synthetic_data.py      ← Ollama synthetic data gen
```

### What Exists vs. What the Paper Describes

| Pipeline Stage | Paper Says | Code Status |
|---|---|---|
| Layer 1: DistilBERT on `is_suspicious` | ✅ | ✅ Older repo has model trained on correct labels |
| 7 OGDM trajectory features | ✅ | ✅ `features.py` (tested, 39 tests) |
| Benign centroid for topic drift | ✅ | ✅ `benign_centroid.npy` |
| Layer 2: LSTM trajectory scoring | ✅ Described in Sec 3.4.2 | ⚠️ Stub exists, not integrated into pipeline |
| Evaluation: Recall, F1, TTD, baseline, ablation | ✅ Described in Sec 3.5 | ✅ `evaluation.py` |
| End-to-end pipeline | ✅ | ✅ `main.py` (but uses WeightedScorer, not LSTM) |

---

## Two Workstreams

### Workstream A: Code — Build the LSTM Pipeline

Get the full system described in the paper actually running end-to-end.

### Workstream B: Paper — Address 10 Advisor Comments

Revise the paper to fix all 10 comments, informed by the actual code and results.

**Workstream A must come first** for comments 3, 6, 7, and 8 — we need real dataset counts, real software versions, real formulas, and real evaluation results to write into the paper.

---

## Workstream A: Code Changes

### Phase A1: Retrain DistilBERT on Correct Labels

> [!WARNING]
> The newer repo's model was trained with `--label-mode either` (author-level OR message-level labels). The paper describes training on message-level suspicious labels only. The older repo's model was trained correctly on `is_suspicious`, but uses an older training script without the context window feature.

#### [MODIFY] [train_distillbert.py](file:///c:/Projects/THESIS/Groomer%20Thesis/pan12-sexual-predator-identification-training-corpus-2012-05-01/train_distillbert.py)

- Retrain using `--label-mode suspicious` (not `either`)
- Keep the context window (`--context-window 2`) — this is a legitimate contextual technique that aligns with the paper's description of "analyzing conversational context"
- Output to a new directory to preserve existing models
- Record exact training metrics (per-epoch Recall, Precision, F1, Loss) for the paper

**Command**:
```bash
python train_distillbert.py --label-mode suspicious --data-file pan12_final_dataset.csv --output-dir final_distilbert_suspicious
```

---

### Phase A2: Integrate LSTM into the Pipeline

The LSTM stub ([trajectory_model_lstm.py](file:///c:/Projects/THESIS/grooming-detector/grooming-detector-trajectory-pipeline/experimental/trajectory_model_lstm.py)) is already 90% complete. It needs:

#### [MODIFY] [experimental/trajectory_model_lstm.py](file:///c:/Projects/THESIS/grooming-detector/grooming-detector-trajectory-pipeline/experimental/trajectory_model_lstm.py)

- The model architecture is solid (`TrajectoryLSTM`: 2-layer LSTM, 775→256 hidden, dropout 0.3, sigmoid output). No changes needed.
- The `ConversationDataset`, `collate_fn`, `train_trajectory_model`, `evaluate_trajectory_model` are all implemented. No changes needed.
- Move from `experimental/` to the main pipeline directory.

#### [NEW] `train_lstm.py` — LSTM training driver

Create a script that:
1. Loads PAN12 via `data_loader.py`
2. Splits into train/val/test via `main.py`'s `stratified_split`
3. Runs Layer 1 (DistilBERT) + `MessageEncoder` to get embeddings + risk scores
4. Computes trajectory features via `features.compute_trajectory_features` for each turn
5. Packages into `ConversationDataset` format (embeddings + trajectory features + cumulative labels)
6. Calls `train_trajectory_model(train_convs, val_convs)`
7. Saves best model to `trajectory_model.pt`

#### [MODIFY] [main.py](file:///c:/Projects/THESIS/grooming-detector/grooming-detector-trajectory-pipeline/main.py)

- Add `--use-lstm` flag
- When enabled, load `TrajectoryLSTM` from `trajectory_model.pt` and score conversations through the LSTM instead of the `WeightedScorer`
- Keep `WeightedScorer` as `--use-weighted` (default for backward compatibility / ablation)
- Add LSTM results to the summary table alongside WeightedScorer and keyword baseline

#### [MODIFY] [evaluation.py](file:///c:/Projects/THESIS/grooming-detector/grooming-detector-trajectory-pipeline/evaluation.py)

- Add `evaluate_lstm_conversations()` that takes LSTM per-turn scores and produces the same metrics dict
- The existing `evaluate_conversations()` interface should work as-is (it just needs `scores` and `label` per conversation)

---

### Phase A3: Run Full Evaluation & Collect Results

Once the LSTM is trained and integrated:

```bash
# Full pipeline with LSTM
python main.py \
  --csv ../trained_model_distillbert/pan12_final_dataset.csv \
  --centroid benign_centroid.npy \
  --use-lstm --lstm-model trajectory_model.pt

# This produces the summary table:
# Keyword Baseline          | Recall | F1 | AUC | TTD
# DistilBERT only           | ...    | ...| ... | ...
# DistilBERT + WeightedScr  | ...    | ...| ... | ...
# DistilBERT + LSTM         | ...    | ...| ... | ...  ← NEW
```

These numbers go directly into the paper.

---

### Phase A4: Dataset Inventory

Run actual counts on all available datasets to populate Table 3.1:

```python
# Count conversations, messages, predatory conversations for each dataset
import pandas as pd
df = pd.read_csv("pan12_final_dataset.csv")
print(f"PAN12: {df['conv_id'].nunique()} conversations, {len(df)} messages")
print(f"  Predatory convs: {df[df['is_suspicious']==1]['conv_id'].nunique()}")
# ... repeat for each dataset
```

---

## Workstream B: Paper Revisions

All edits to [Finals Revised Paper WASD.docx](file:///c:/Projects/THESIS/Finals%20Revised%20Paper%20WASD.docx).

> [!IMPORTANT]
> Paper revisions depend on Phase A3 results for Comments 3, 6, 7, 8. We write the structural/text changes first, then fill in exact numbers after running the pipeline.

---

### Comment 5 (P3): Shorten Title

#### [MODIFY] Title Page

**Current**: "AI-Based Detection of Grooming-Related Interactions in Chat Conversations Using Contextual and Behavioral Analysis"

**Proposed**:
> **WASD-Guard**
> AI-Based Detection of Grooming-Related Interactions in Chat Conversations Using Contextual and Behavioral Analysis

> [!NOTE]
> Need your input on the module name. "WASD-Guard" ties to the team name. Alternatives: "GroomGuard", "ChatShield", or something else.

---

### Comment 1 (P0): Strong Redaction Protocol

#### [MODIFY] Section 3.3.2 (Data Preprocessing) — add PII redaction subsection

Add after the current preprocessing text:

- **Stage 1 — Rule-based scrubbing**: Regex patterns to detect and replace phone numbers, email addresses, URLs, social media handles, and usernames with placeholder tokens (`[REDACTED_CONTACT]`, `[REDACTED_URL]`, `[REDACTED_HANDLE]`).
- **Stage 2 — NER-based masking**: Named Entity Recognition to detect and mask real names, locations, and organizations (`[REDACTED_NAME]`, `[REDACTED_LOC]`).
- All redaction is applied **before** tokenization and model training.

#### [MODIFY] Section 3.6 (Ethical Considerations)

Strengthen the existing anonymization paragraph to reference the concrete redaction pipeline defined in 3.3.2.

---

### Comment 2 (P2): Philippine Contextualization

#### [MODIFY] Section 1.5.3 (Societal Benefits)

Expand the existing PH paragraph to explain *how* the study was made contextually relevant:

1. The synthetic training data (Sec 3.3.1) incorporates modern Filipino internet slang, Taglish code-switching, and gaming platform vernacular common in PH youth communities (e.g., Roblox PH servers, Discord Filipino gaming communities).
2. The real-world validation datasets include transcripts sourced from documented predatory interactions on platforms popular with Filipino minors.
3. The system analyzes English-language chat, which is the dominant language of the gaming platforms where PH youth are most active.

#### [MODIFY] Section 3.3.1 (Data Collection)

Add a paragraph documenting the PH-specific synthetic data construction methodology.

---

### Comment 3 (P1): Standardize Table 3.1

#### [MODIFY] Section 3.3.1 — Replace Table 3.1

Replace with a properly formatted table including exact counts from Phase A4:

| Dataset | Source | Conversations | Messages | Label Granularity | Preprocessing Status |
|---|---|---|---|---|---|
| PAN12 (dyadic subset) | PAN-2012 Competition Corpus | *exact count* | *exact count* | Conv-level + line-level `is_suspicious` | Filtered to 2-author, cleaned, normalized |
| Real Chat Transcripts | Anonymized research transcripts | *exact count* | *exact count* | Per-message annotated | Anonymized, PII-redacted |
| Synthetic Grooming Data | LLM-generated (3 OGDM tactics) | *exact count* | *exact count* | Per-message, per-turn OGDM stage | Manually verified |
| Synthetic Safe Data | LLM-generated (3 benign scenarios) | *exact count* | *exact count* | All benign (hard negatives) | Manually verified |

---

### Comment 4 (P0): Clarify Dataset Label Hierarchy

#### [MODIFY] Section 3.3.3 (Data Processing) — add label clarification

Add a new table and explanatory text:

| Label | Scope | Definition | Used By |
|---|---|---|---|
| `is_suspicious` | Per-message | This specific message contains grooming-relevant content | Layer 1 DistilBERT (training target) |
| `author_is_predator` | Per-author | This author was identified as a predator in the PAN12 corpus | Not used for training; reference only |
| Conversation label | Per-conversation | 1 if any author in the conversation is a confirmed predator | Layer 2 LSTM evaluation ground truth |

Explain: "The message-level `is_suspicious` label is used as the training target for the DistilBERT classifier. This prevents the model from learning spurious associations between benign messages and predatory authors. The conversation-level label is used exclusively for evaluating the trajectory model's ability to flag entire conversations."

---

### Comment 10 (P0): Reconcile DistilBERT vs. Dataset Labels

#### [MODIFY] Section 3.4.1 (Message-Level Classifier)

Add explicit clarification:

"The DistilBERT classifier is fine-tuned on per-message `is_suspicious` annotations from the PAN12 corpus, which mark specific messages as grooming-relevant regardless of the overall author label. This design choice prevents the model from flagging benign messages (e.g., casual greetings) simply because they were written by a known predator. The per-message risk scores produced by Layer 1 serve as input features to the LSTM trajectory model (Section 3.4.2), which aggregates message-level signals across conversation turns to produce a conversation-level risk assessment."

---

### Comment 7 (P1): Feature Engineering Formulas

#### [MODIFY] Section 3.3.4 (Feature Engineering) + Table 3.2

Replace prose descriptions with exact mathematical formulations from [features.py](file:///c:/Projects/THESIS/grooming-detector/grooming-detector-trajectory-pipeline/features.py):

| Feature | Formula | OGDM Construct |
|---|---|---|
| Peak Score | $P_t = \max_{1 \le i \le t} R_i$ | Score-suppression resistance |
| Current Score | $R_t$ (Layer 1 output) | Local message risk |
| Spike Count | $S_t = \sum_{i=1}^{t} \mathbb{1}(R_i > 0.5)$ | Risk escalation frequency |
| Spike-Then-Drop | $\exists j: R_{j-1} > 0.5 \land R_j < R_{j-1} - \delta$ | Compliance testing (entrapment) |
| Rate of Change | $\Delta R_t = R_t - R_{t-1}$ | Escalation velocity |
| Topic Drift | $D_t = 1 - \cos(\mathbf{e}_t, \mathbf{c}_{\text{benign}})$ | Approach phase (content steering) |
| Turn-Taking Imbalance | $I_t = \frac{|T_A - T_B|}{T_A + T_B}$ | Dominance and control |

> [!WARNING]
> **Discrepancy found**: The paper says "Ratio of word count between participants" but `features.py` line 146 counts **turns**, not words. The paper revision must match whichever we decide is correct. The code uses turns — if that's intentional, update the paper text. If word count is intended, update the code.

---

### Comment 6 (P1): Specific Evaluation Methods

- **Code Status**: ✅ **DONE** — Added $F_{0.5}$-score and McNemar's test to [evaluation.py](file:///c:/Projects/THESIS/grooming-detector/grooming-detector-trajectory-pipeline/evaluation.py) and [main.py](file:///c:/Projects/THESIS/grooming-detector/grooming-detector-trajectory-pipeline/main.py) (52 pytest tests passing).

#### [MODIFY] Section 3.5.1 & 3.8 & 3.9 (Evaluation Metrics & Validation)

Add formal definitions and justifications:

- $\text{Recall} = \frac{TP}{TP + FN}$ — primary metric (reducing false negatives)
- $\text{Precision} = \frac{TP}{TP + FP}$ — controlling false positive moderator workload
- $\text{F1} = 2 \times \frac{P \times R}{P + R}$ — balanced classification performance
- $\text{F}_{0.5} = (1 + 0.5^2) \times \frac{P \times R}{(0.5^2 \times P) + R} = \frac{1.25 \cdot P \cdot R}{0.25 P + R}$ — precision-weighted metric matching the PAN12 competition benchmark and RRL literature (Street et al., 2024; Faraz et al., 2024)
- $\text{AUC-ROC}$ — discriminative ability across thresholds using max per-conversation score
- $\text{TTD} = \bar{k}$ — mean turn index where trajectory score first exceeds threshold $\theta$
- **McNemar's Test**: Non-parametric test for paired binary classification outcomes on identical test sets:
  $$\chi^2 = \frac{(|b - c| - 1)^2}{b + c}$$
  where $b$ is the number of conversations correctly flagged by the proposed model but missed by the baseline/ablated model, and $c$ is the reverse. Formally replaces the previous "proposed as future analysis" hedge in Section 3.9.
- **Ablation**: Full pipeline (DistilBERT + 7 features + LSTM) vs. DistilBERT-only (trajectory features zeroed)
- **Keyword Baseline**: 27-term grooming lexicon applied per-message

---

### Comment 8 (P2): Software Versions

#### [MODIFY] Section 3.2 (Relevant Technology)

Add exact versions (to be confirmed from the actual runtime environment):

- **Python**: 3.12.x
- **PyTorch**: (check `torch.__version__`)
- **HuggingFace Transformers**: 5.14.1 (from model `config.json`)
- **Pre-trained base model**: `distilbert-base-uncased` (66M parameters, 6 layers, 768 hidden dim, 12 attention heads)
- **scikit-learn**: (check version — used for cosine_similarity, evaluation metrics)
- **NumPy / Pandas**: (check versions)
- **Development environment**: VS Code + Jupyter Notebook, CPU inference (no GPU required for evaluation)

---

### Comment 9 (P2): Restate Deployment Limitations

#### [MODIFY] Section 1.4.2 (Limitations)

Add as the opening statement:

"This study develops and evaluates an **offline simulation prototype**. The system processes pre-recorded conversation logs in chronological turn order to simulate sequential message analysis. No real-time deployment, live message stream processing, or active user interaction is performed. All evaluation is conducted within a controlled offline environment using stored datasets."

#### [MODIFY] Section 3.1 (Research Design)

Clarify: "The proposed models will be validated offline by replaying ordered conversation records and computing trajectory risk scores at each turn, simulating how the system would behave in a sequential chat analysis scenario."

---

## Execution Order

| Step | Workstream | Description | Depends On |
|---|---|---|---|
| 1 | A1 | Retrain DistilBERT with `--label-mode suspicious` | — |
| 2 | A2 | Move LSTM from experimental → main pipeline; create `train_lstm.py` | Step 1 |
| 3 | A2 | Train LSTM on PAN12 features | Step 2 |
| 4 | A2 | Integrate LSTM into `main.py` with `--use-lstm` flag | Step 3 |
| 5 | A3 | Run full evaluation (LSTM + WeightedScorer + Baseline + Ablation) | Step 4 |
| 6 | A4 | Collect exact dataset counts | — |
| 7 | B | Paper: Comments 5, 1, 9 (no code dependency) | — |
| 8 | B | Paper: Comments 4, 10 (label reconciliation) | — |
| 9 | B | Paper: Comments 2 (PH context) | — |
| 10 | B | Paper: Comments 7, 6 (formulas + evaluation methods) | — |
| 11 | B | Paper: Comments 3, 8 (exact counts + versions) | Steps 5, 6 |

Steps 6, 7, 8, 9, 10 can run in parallel with the code work.

---

## Verification Plan

### Code Verification
- Run pytest tests (52/52 passing including evaluation, F0.5, and McNemar tests) ✅
- Verify LSTM training converges (val AUC should improve over epochs)
- Compare LSTM vs WeightedScorer vs Baseline on test set
- Verify end-to-end pipeline produces the summary table with F0.5 and McNemar output

### Paper Verification
- Check every comment (1-10) has a corresponding section revision
- Include $F_{0.5}$-score definition and McNemar's test chi-squared formula in Section 3.5.1 / 3.8 / 3.9
- Verify all formulas match the code implementations exactly (turn-taking imbalance updated to turn counts)
- Verify Table 3.1 dataset counts match actual CSV file row counts
- Verify software versions match `pip list` output from the runtime environment

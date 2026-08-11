# Advisor Comments → Code vs. Paper Audit

After reading through all the codebase files, here's the honest breakdown of what needs code changes vs. just paper edits.

---

## Comments That Need Code Changes

### Comment 1: Strong Redaction Protocol 🔴 CODE NEEDED

**The problem**: The advisor wants a concrete PII redaction pipeline. The implementation plan describes regex scrubbing + NER-based masking. But **zero redaction code exists anywhere**. The word "redact" only appears in the data itself (PAN12 XML already has some `[REDACTED]` tokens baked in by the corpus authors), not in any preprocessing script.

**What needs to happen**:
- [NEW] `redaction.py` — a preprocessing module with:
  - Stage 1: Regex patterns for phone numbers, emails, URLs, social handles → `[REDACTED_CONTACT]`, `[REDACTED_URL]`, `[REDACTED_HANDLE]`
  - Stage 2: spaCy NER for PERSON, GPE, ORG → `[REDACTED_NAME]`, `[REDACTED_LOC]`
- [MODIFY] [data_loader.py](file:///c:/Projects/THESIS/grooming-detector/grooming-detector-trajectory-pipeline/data_loader.py) — apply redaction in `build_conversation_snapshots()` or `load_canonical_csv()` before passing text downstream
- **Retrain?** If we redact the training data, the model should ideally be retrained on redacted text. But this is a tradeoff — if PAN12 already has partial redaction and the model learned fine, we can argue redaction is applied "before deployment" (inference-time only). This is a design decision.

> [!WARNING]
> Without this code, any claim in the paper about "strong redaction" is unsupported. The advisor specifically flagged this as **P0**.

---

### Comment 6: Specific Evaluation Methods ✅ CODE DONE

**What exists**: [evaluation.py](file:///c:/Projects/THESIS/grooming-detector/grooming-detector-trajectory-pipeline/evaluation.py) has:
- ✅ Recall, Precision, F1, AUC-ROC
- ✅ $F_{0.5}$-score (PAN12 competition standard, precision-weighted)
- ✅ Time-to-detection
- ✅ McNemar's test (`mcnemar_test()`) — non-parametric paired classifier significance test
- ✅ Keyword baseline
- ✅ Ablation utility

**What's remaining for Comment 6**:
- ❌ **LSTM evaluation path** — `evaluation.py` can score any model that produces `scores` per conversation, so the interface works. But `main.py` has no `--use-lstm` flag yet (Phase A2).
- 📝 **Paper update**: Document $F_{0.5}$-score definition and McNemar's test $\chi^2$ formula in Sections 3.5.1, 3.8, and 3.9.

---

### Comment 3 / Phase A4: Dataset Counts 🟡 SCRIPT NEEDED

**The problem**: Table 3.1 needs exact conversation/message/label counts for each dataset.

**What needs to happen**: A small script to load each CSV and print counts. Not complex, but it *is* code that needs to run to produce the numbers.

---

### Comment 8: Software Versions 🟡 SCRIPT NEEDED

**The problem**: Need exact versions of Python, PyTorch, Transformers, scikit-learn, NumPy, Pandas.

**What needs to happen**: Run `pip list` or a small version-checking script in the actual training environment. If Justin ran this on his machine, we need his `pip freeze` output.

---

## Comments That Are Paper-Only

### Comment 2: Philippine Contextualization ✅ PAPER ONLY

The synthetic data generators ([generate_synthetic_data.py](file:///c:/Projects/THESIS/Groomer%20Thesis/pan12-sexual-predator-identification-training-corpus-2012-05-01/generate_synthetic_data.py), [generate_safe_data.py](file:///c:/Projects/THESIS/Groomer%20Thesis/pan12-sexual-predator-identification-training-corpus-2012-05-01/generate_safe_data.py)) already exist and presumably generate PH-contextualized content. The paper just needs to *describe* this methodology better.

### Comment 4: Dataset Label Hierarchy ✅ PAPER ONLY

The code already correctly uses `is_suspicious` for Layer 1 training and `conversation_label` (derived from `author_is_predator`) for evaluation. See:
- [data_loader.py L150](file:///c:/Projects/THESIS/grooming-detector/grooming-detector-trajectory-pipeline/data_loader.py#L150): `"label": int(row["is_suspicious"])`
- [data_loader.py L151](file:///c:/Projects/THESIS/grooming-detector/grooming-detector-trajectory-pipeline/data_loader.py#L151): `"conversation_label": conv_is_predatory`

The paper just needs to explain this clearly.

### Comment 5: Shorten Title ✅ PAPER ONLY

### Comment 7: Feature Engineering Formulas ✅ PAPER ONLY

All 7 features are implemented correctly in [features.py](file:///c:/Projects/THESIS/grooming-detector/grooming-detector-trajectory-pipeline/features.py). The paper just needs to document the formulas that match the code. **Your decision**: paper says "word count ratio" but code counts turns (line 146). You said: **change the paper** ✅.

### Comment 9: Restate Deployment Limitations ✅ PAPER ONLY

### Comment 10: Reconcile DistilBERT vs Dataset Labels ✅ PAPER ONLY

Phase A1 is done — Justin retrained with `--label-mode suspicious`. The paper just needs to clearly explain that the model is trained on per-message `is_suspicious` labels, not author-level labels.

---

## The Big Code Task: Phase A2 (LSTM Integration)

This isn't tied to a single comment but is the **backbone** that several comments depend on:

| File | Change |
|---|---|
| [trajectory_model_lstm.py](file:///c:/Projects/THESIS/grooming-detector/grooming-detector-trajectory-pipeline/experimental/trajectory_model_lstm.py) | Move from `experimental/` → main directory |
| **[NEW]** `train_lstm.py` | LSTM training driver (load data → Layer 1 scores → features → train LSTM → save `trajectory_model.pt`) |
| [main.py](file:///c:/Projects/THESIS/grooming-detector/grooming-detector-trajectory-pipeline/main.py) | Add `--use-lstm` flag, load `TrajectoryLSTM`, score through LSTM |
| [evaluation.py](file:///c:/Projects/THESIS/grooming-detector/grooming-detector-trajectory-pipeline/evaluation.py) | Add McNemar's test |
| [message_classifier.py](file:///c:/Projects/THESIS/grooming-detector/grooming-detector-trajectory-pipeline/message_classifier.py) | Point `--classifier` default at Justin's new model |

---

## Summary: Prioritized Action Plan

| Priority | Task | Type | Effort |
|---|---|---|---|
| 🔴 **1** | PII redaction module (`redaction.py` + wire into pipeline) | Code | Medium |
| 🔴 **2** | Wire Justin's model into working pipeline | Code | Small |
| 🔴 **3** | Move LSTM from experimental, create `train_lstm.py` | Code | Large |
| 🔴 **4** | Add `--use-lstm` to `main.py` + McNemar's test | Code | Medium |
| 🟡 **5** | Dataset count script (Table 3.1 numbers) | Code | Small |
| 🟡 **6** | Version extraction (Comment 8) | Code | Trivial |
| 🟢 **7** | Paper revisions (Comments 2, 4, 5, 7, 9, 10) | Paper | Medium |
| 🟢 **8** | Paper revisions requiring results (Comments 3, 6, 8) | Paper | Blocked until code done |

> [!IMPORTANT]
> **The critical question**: Do we need to actually build and run the redaction pipeline (Comment 1), or can we describe it in the paper as a "deployment-stage" preprocessing step and argue that PAN12's existing partial redaction + our offline simulation framing (Comment 9) makes it acceptable? This determines how much work Comment 1 really is.

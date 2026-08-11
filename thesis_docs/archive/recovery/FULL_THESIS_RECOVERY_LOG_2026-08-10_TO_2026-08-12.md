# Thesis Recovery: Current State and Next Steps

> **Current interpretation:** Read `CURRENT_STATE_ZERO_AMBIGUITY.md` first.
> This file is a chronological log and intentionally preserves earlier findings;
> later correction rows supersede conflicting earlier rows.

**Created:** 2026-08-10  
**Purpose:** Persistent, evidence-based handoff after reviewing `transcript_full.jsonl`. This file is the on-disk record for future thesis-work updates.

## One-Sentence Current State

The working system is a retrained DistilBERT message scorer plus a weighted seven-feature trajectory scorer; an LSTM trajectory model was implemented and evaluated, but its current checkpoint failed to detect any positive conversations at the evaluated thresholds.

## Canonical Sources

| Purpose | Canonical location | Do not use as authority |
|---|---|---|
| Current paper | `Finals Revised Paper WASD.docx` and `Finals_Revised_Paper_WASD.md` | `Main_paper_Chapters_1-3.md`, `Chapter_3_TEMPORARY.md` |
| Active pipeline | `grooming-detector/grooming-detector-trajectory-pipeline/` | `grooming-detector-main-2/.../grooming-detector-trajectory-pipeline/` |
| Retrained Layer 1 model | `grooming-detector/trained_model_distillbert/final_moderation_model/` | Older model copies |
| Raw recovery evidence | `transcript_full.jsonl` | Chat summaries alone |

## Verified Evaluation Snapshot

Raw command evidence in `transcript_full.jsonl` records this PAN12 dyadic test split: 1,857 conversations, including 45 positive conversations.

| Model | Recall | F1 | F0.5 | AUC-ROC | Average time to detection |
|---|---:|---:|---:|---:|---:|
| Keyword baseline | 0.0889 | 0.0816 | 0.0778 | 0.5309 | 84.0 turns |
| DistilBERT only | 0.0000 | 0.0000 | 0.0000 | 0.8299 | N/A |
| DistilBERT + weighted trajectory scorer | 0.2222 | 0.1639 | 0.1416 | 0.8522 | 78.2 turns |
| DistilBERT + LSTM trajectory model | 0.0000 | 0.0000 | 0.0000 | 0.5430 | N/A |

The LSTM checkpoint, sample checkpoint, and embedding cache exist in the active pipeline directory. The LSTM is real code and was evaluated; it is not a successful final model yet.

## Recommended Immediate Decision

**Do not retrain the LSTM again yet.** First make the methodology and claims accurate.

Recommended thesis position unless the LSTM is deliberately rebuilt and re-evaluated:

1. Present the **weighted trajectory scorer** as the implemented and best-performing Layer 2 method.
2. Present the **LSTM** as an implemented comparative sequence-model experiment that underperformed in the current evaluation.
3. Keep the LSTM results as a limitation and a future-improvement path, rather than claiming it is the final operational detector.

This is the shortest defensible route because it matches the measured results and preserves the useful LSTM work without inventing performance.

## Work Order

### Step 1 — Paper/code alignment (next task)

Revise the current paper so it states the exact implemented architecture and result:

- The weighted scorer consumes the seven trajectory features and uses a tuned threshold.
- The LSTM experiment consumes a 768-dimensional base-DistilBERT embedding plus the seven trajectory features.
- The message-risk score is present through the `current_score` trajectory feature.
- The LSTM checkpoint underperformed; do not claim real-time/operational success for it.
- Replace the inaccurate claim that Layer 1 uses class-weighted loss if keeping the present code. It currently uses negative downsampling.
- Explain the label hierarchy: message training uses `is_suspicious`; conversation evaluation uses `author_is_predator`.

### Step 2 — Fix the evaluation narrative before using results

- Do not claim the McNemar outputs prove the weighted scorer is better. McNemar here measures per-conversation correctness/accuracy, which is dominated by benign conversations.
- Report recall, precision, F1/F0.5, AUC-ROC, false positives, and time-to-detection as the substantive results.
- State that the test set has 45 positive conversations; treat estimates as limited by that count.

### Step 3 — Finish the advisor-requested non-result work

After Step 1, address the remaining paper/code tasks in this order:

1. Add and document a real PII-redaction stage, or narrow the paper to an offline, pre-redacted-data claim.
2. Generate and preserve exact dataset inventory counts for Table 3.1.
3. Record actual environment/package versions used for training and evaluation.
4. Add the Philippine synthetic-data generation methodology and label hierarchy explanation.
5. Finalize title, feature operational definitions, and offline-simulation limitations.

### Step 4 — Only if the LSTM must remain the primary model

Treat this as a separate experiment, not a quick patch:

- decide the intended target (message/cumulative suspicion or author-level conversation detection);
- use a class-imbalance-aware loss or sampling method;
- tune its threshold on validation data, not a hard-coded 0.5;
- select checkpoints with a metric aligned to early conversation-level recall/F0.5;
- evaluate on the untouched test split and save a machine-readable results file;
- compare against the weighted scorer using a hypothesis that matches the safety goal.

## Known Technical Facts to Preserve

- `train_lstm.py` and `main.py --use-lstm` are in the active pipeline.
- Current LSTM training uses unweighted `BCELoss`.
- Current LSTM validation selection uses turn-level AUC, while the paper's operational goal is conversation-level early detection.
- The weighted scorer is the best measured method in the recovered run.
- The existing `pan12_distilbert_cache.pkl` should be treated as tied to the exact data/model preprocessing that produced it; it has no automatic provenance validation.

## Update Log

| Timestamp | Update | Evidence / affected files |
|---|---|---|
| 2026-08-10 | Created recovery roadmap after raw transcript audit. No model, paper, or pipeline files changed. | `transcript_full.jsonl`; this file |
| 2026-08-10 | User directed that the LSTM must be improved rather than reframed as an underperforming comparison. Began validation-only model-improvement work; no model-selection claim will be made until a fresh held-out-test evaluation is saved. | `transcript_full.jsonl`; active pipeline |
| 2026-08-10 | Updated LSTM trial controls: imbalance-aware positive loss weighting, validation F0.5 threshold selection, and checkpoint metadata. The original checkpoint remains unchanged; new trials use separate output names. | `trajectory_model_lstm.py`; `train_lstm.py` |
| 2026-08-10 | Completed a 20-epoch weighted-loss LSTM trial and saved `trajectory_model_weighted.pt`; its persistent training log is `lstm_weighted_train.log`. Added a reproducible validator/test evaluator that writes JSON reports. | `trajectory_model_weighted.pt`; `lstm_weighted_train.log`; `evaluate_lstm_checkpoint.py` |
| 2026-08-10 | First new-checkpoint evaluation was blocked before test scoring by two reproducibility defects: unnecessary base-encoder network initialization despite the local cache, and PyTorch 2.6 metadata loading. Corrected both; no test result from that failed attempt was used. | `lstm_weighted_evaluation.log`; `evaluate_lstm_checkpoint.py`; `trajectory_model_lstm.py` |
| 2026-08-10 | Second evaluation attempt reached validation scoring and selected a validation-only threshold, but stopped before the test pass on a JSON field-name mismatch. Corrected the report formatter; no test result from that attempt was used. | `lstm_weighted_evaluation_retry.log`; `evaluate_lstm_checkpoint.py` |
| 2026-08-10 | Completed the weighted-loss trial and saved `lstm_weighted_evaluation.json`. It raised held-out recall to 0.7778 but had 835 false positives and did not beat the weighted scorer on precision, F0.5, or AUC. Began a second trial design with conversation-level supervision and validation conversation-F0.5 checkpoint selection. | `lstm_weighted_evaluation.json`; `trajectory_model_lstm.py`; `train_lstm.py` |
| 2026-08-10 | Stopped the conversation-supervised trial before a checkpoint was saved after finding validation was needlessly scoring conversations one at a time. Replaced it with equivalent batched validation; no partial result was used. | `lstm_conversation_train.log`; `trajectory_model_lstm.py` |
| 2026-08-10 | Short detached conversation-supervised trial exposed a third reproducibility defect: `train_lstm.py` initialized the base encoder before checking the complete local embedding cache, causing a blocked network request. Moved encoder creation behind the cache miss path; no checkpoint from that attempt was used. | `lstm_conversation_train.err.log`; `train_lstm.py` |
| 2026-08-10 | Completed the cache-aware five-epoch conversation-supervised LSTM trial. Validation chose its threshold without test labels; held-out test result: recall 0.5333, precision 0.9600, F1 0.6857, F0.5 0.8276, AUC 0.9932, 1 false positive, mean detection 18.2 turns. It exceeds both the weighted scorer and the DistilBERT-only ablation in the recovered benchmark. Main pipeline now defaults to checkpoint metadata threshold unless explicitly overridden. | `trajectory_model_conversation.pt`; `lstm_conversation_evaluation.json`; `lstm_conversation_evaluation.log`; `main.py` |
| 2026-08-10 | Extended the reproducible evaluator so its final JSON contains the same held-out comparison against the DistilBERT current-score-only ablation, in addition to the weighted scorer. | `evaluate_lstm_checkpoint.py`; `lstm_conversation_evaluation.json` |
| 2026-08-10 | The first three-way report rerun reached test scoring but stopped only when serializing the classifier baseline's undefined time-to-detection. Converted non-finite JSON values to `null`; no model, split, or threshold changed. | `lstm_conversation_evaluation.log`; `evaluate_lstm_checkpoint.py` |
| 2026-08-12 | Leakage audit: the deterministic split has zero shared conversation IDs, but it is not author-disjoint. Train/test share 147 authors and, critically, 27 of the 32 test-set predator authors also occur in training; 17.7% of unique test message texts also occur in training. The reported LSTM result is valid only as an unseen-conversation benchmark and may be materially optimistic for detecting unseen predators. Do not present it as unseen-predator generalization without a stricter author-grouped evaluation. | Read-only audit of `data_loader.py`, `main.stratified_split`, and `pan12_final_dataset.csv` |
| 2026-08-12 | Created a standalone next-agent handoff with the active architecture, trial artifacts, verified metrics, leakage finding, required author-disjoint experiment, paper implications, exact commands, and next-window prompt. No model, paper, or data files changed. | `NEXT_AGENT_HANDOFF.md` |
| 2026-08-12 | Resumed work after context compaction. Re-read the persistent handoff and recovery log, confirmed the active pipeline and preserved all pre-existing worktree changes. Began the required author-disjoint split investigation; no model or dataset file changed in this update. | `NEXT_AGENT_HANDOFF.md`; `THESIS_RECOVERY_NEXT_STEPS.md`; active pipeline worktree |
| 2026-08-12 | Measured the dyadic PAN12 author graph before implementation: 18,572 conversations, 34,696 authors, 17,044 connected components, 454 positive conversations across 102 positive components. Added predator-author identity metadata to in-memory snapshots so the new split audit can explicitly verify both all-author and predator-author separation; the source CSV remains unchanged. | `data_loader.py`; `tests/test_data_loader.py`; read-only PAN12 component analysis |
| 2026-08-12 | Implemented a deterministic author-disjoint splitter. Conversations sharing any dataset-namespaced author are collapsed into connected components; 10 component-disjoint folds are formed, and validation/test folds are chosen only by size and source/class balance. The generated JSON manifest records every conversation assignment and raises an error if any conversation or author crosses partitions. Added a focused leakage-invariant test. | `splitting.py`; `tests/test_author_disjoint_split.py` |
| 2026-08-12 | Integrated the new split into LSTM training and checkpoint evaluation behind explicit `--split-protocol author-disjoint` controls. Training now writes the split manifest before feature construction; evaluation regenerates the deterministic manifest and records its absolute path and SHA-256 digest in the metrics report. Historical conversation-split behavior remains available for baseline reproducibility. | `train_lstm.py`; `evaluate_lstm_checkpoint.py` |
| 2026-08-12 | Initial focused verification compiled the modified Python files successfully. Pytest reported four passes, while three `tmp_path`-dependent tests could not start because the sandbox denied access to Python's user temp directory; rerunning with a project-local pytest base temp was selected as the corrective verification step. | `data_loader.py`; `splitting.py`; `train_lstm.py`; `evaluate_lstm_checkpoint.py`; focused pytest output |
| 2026-08-12 | Reran verification with a project-local pytest temporary directory: all seven focused loader/split tests passed, and all modified Python files compiled. Added a standalone reproducible command-line audit generator so split feasibility and zero-overlap evidence can be produced without starting model training. | `audit_author_disjoint_split.py`; focused pytest result: 7 passed |
| 2026-08-12 | Generated the complete PAN12 split manifest. The author-disjoint partitions contain 14,893/1,828/1,847 train/validation/test conversations and 363/49/42 positives. All pairwise conversation, author, and predator-author overlaps are exactly zero. Persistent console output and full per-conversation assignments were saved. | `author_disjoint_split_audit.json`; `author_disjoint_split_audit.log` |
| 2026-08-12 | Closed a training reproducibility gap before the final run: the CLI random state now seeds NumPy, PyTorch, CUDA, and DataLoader shuffling, with deterministic cuDNN settings recorded in behavior. Removed the old turn-label classification report because it applied a conversation-selected threshold to a different target and could mislead later Results writing. | `trajectory_model_lstm.py`; `train_lstm.py` |
| 2026-08-12 | Reverified the final pre-training code: all five modified scripts compile, all seven focused tests pass, and CUDA is available through PyTorch 2.11.0 on an NVIDIA GeForce RTX 3050 Laptop GPU. Frozen the experiment protocol and exact training/evaluation commands in a standalone record; it explicitly flags Layer 1 provenance as a remaining end-to-end leakage question. | `AUTHOR_DISJOINT_EXPERIMENT.md`; focused compile/pytest/device checks |
| 2026-08-12 | Completed the frozen five-epoch author-disjoint LSTM training run and verified the saved checkpoint reloads. Best validation checkpoint: conversation F0.5 0.7868, conversation AUC 0.9868, validation threshold 0.889397, random state 42. PowerShell returned a wrapper-level `NativeCommandError` solely because `tqdm` emitted progress to stderr; the model and test-snapshot save messages completed and all expected artifacts exist. No held-out test result had been inspected at this update. | `trajectory_model_author_disjoint.pt`; `test_snapshots_author_disjoint.pkl`; `lstm_author_disjoint_train.log`; `AUTHOR_DISJOINT_EXPERIMENT.md` |
| 2026-08-12 | Completed the single frozen author-disjoint held-out evaluation. Validation-only threshold 0.889347. Test LSTM: recall 0.8333, precision 0.8750, F1 0.8537, F0.5 0.8663, AUC 0.9904, 35 TP, 7 FN, 5 FP, mean detection turn 10.77. Weighted scorer: recall 0.3333, F0.5 0.2023, AUC 0.8841, 62 FP. DistilBERT current-score-only: zero recall/F0.5, AUC 0.8559. The LSTM therefore beats both required comparators at the Layer 2 evaluation boundary. Layer 1 training provenance remains to be audited before an end-to-end unseen-author claim. | `lstm_author_disjoint_evaluation.json`; `lstm_author_disjoint_evaluation.log`; `AUTHOR_DISJOINT_EXPERIMENT.md` |
| 2026-08-12 | Layer 1/label provenance audit confirmed two critical limitations. The active trainer uses author-level `is_predator` with a random message-row split, so Layer 1 is not proven disjoint from Layer 2 held-out authors/messages. More fundamentally, PAN's own readme defines the diff file as locations of modified text, while `Python.py` incorrectly names those rows `is_suspicious`; they are not genuine grooming-message/onset labels. Preserved the completed LSTM run as a conditional fixed-Layer-1 baseline and documented the required end-to-end remediation. | `LABEL_PROVENANCE_AUDIT.md`; active `train_distillbert.py`; `Python.py`; PAN12 `readme.txt`; diff file; checkpoint hash comparison |
| 2026-08-12 | Consolidated the complete state into a plain-language progress report: recovery/audit work, all LSTM repairs and trials, strict author-disjoint protocol, final comparator metrics, the Layer 1/label-provenance limitation, and the exact end-to-end remediation sequence. No model, dataset, or evaluation result changed. | `PROGRESS_REPORT_2026-08-12.md`; existing saved experiment artifacts |
| 2026-08-12 | Clarified the label architecture in response to reviewer feedback. Layer 1 is intended to be message-level but the active trainer repeats author-level `is_predator` labels on message rows. Layer 2 uses separate turn and conversation losses rather than one merged label; multi-objective supervision is conceptually valid, but the PAN diff-derived turn label is not valid grooming ground truth. Recorded the clean separation required for remediation. | `LABEL_PROVENANCE_AUDIT.md`; no model or result changed |
| 2026-08-12 | Verified model/directory authority from checkpoint timestamps and SHA-256 hashes. `grooming-detector` is the canonical active project; its `trajectory_model_author_disjoint.pt` saved 2026-08-12 02:46:59 is the newest trained model overall. Its active Layer 1 DistilBERT is byte-identical to the best `checkpoint-750`/final copy in `grooming-detector-main-2`, so they are duplicate copies rather than different models. `Groomer Thesis` has scripts/data but no saved final model; `grooming-detector-main` is older. | `MODEL_AUTHORITY_MAP.md`; filesystem timestamp and SHA-256 audit |
| 2026-08-12 | Corrected the Layer 1 trainer identification using the user-supplied source, recovered transcript, checkpoint `trainer_state.json`, and `training_args.bin`. The attached trainer exactly matches the newer `Groomer Thesis` trainer after restoring paste-mangled double underscores; its F1 selection, FP16, learning rate, three-epoch schedule, and checkpoint-750 state match the active model, unlike the stale trainer beside the copied active weights. Best-supported label mode is `suspicious`, but the custom flag was not serialized. The remaining problems are author-disjointness across Layer 1 and the invalid PAN diff-derived meaning of `is_suspicious`. | attached trainer; `LABEL_PROVENANCE_AUDIT.md`; `MODEL_AUTHORITY_MAP.md`; checkpoint metadata; `transcript_full.jsonl` |
| 2026-08-12 | Created a single authoritative zero-ambiguity progress report separating confirmed facts, strong inferences, and unknown provenance. It reconciles directory authority, the verified newer Layer 1 trainer lineage, the strongly supported-but-unserialized `suspicious` mode, unknown exact Layer 1 row manifest, confirmed PAN diff-label error, exact Layer 2 architecture/split/results, first-flag-turn semantics, defensible claims, and the clean end-to-end experiment required next. Marked prior progress report and handoff as superseded. No checkpoint, dataset, split, or metric changed. | `CURRENT_STATE_ZERO_AMBIGUITY.md`; supersession notices in `PROGRESS_REPORT_2026-08-12.md` and `NEXT_AGENT_HANDOFF.md` |
| 2026-08-12 | Consolidated all 15 workspace-root thesis/report Markdown files into `thesis_docs/` and added a documentation index. Package-specific README files remain beside their code. No paper content, model, dataset, split, or metric was deleted or changed. | `thesis_docs/README.md`; `thesis_docs/*.md` |
| 2026-08-12 | Inventoried the four project trees before destructive cleanup. Preserved the two unique synthetic CSVs in the canonical active project and copied checkpoint-750 plus full-run Layer 1 trainer states into `thesis_docs/evidence/`, recording SHA-256 hashes. Recorded every nested repository's HEAD, branch, and remote before Git metadata removal. Added a root `.gitignore` for large model/cache/corpus artifacts and a cleanup manifest. | `.gitignore`; `thesis_docs/WORKSPACE_CLEANUP_MANIFEST.md`; `grooming-detector/data_sources/synthetic/`; `thesis_docs/evidence/` |
| 2026-08-12 | Removed exactly three validated nested `.git` directories at the user's request and initialized one new Git repository at `C:\Projects\THESIS\.git` on branch `main`; the old local Git histories are no longer recoverable except through the recorded remotes/HEADs. Before deleting duplicate project trees, discovered their Layer 1 PAN CSV differs from the newer active PAN CSV, so preserved that exact archived CSV and trainer with SHA-256 hashes. | root `.git`; `grooming-detector/data_sources/layer1_training_archive/`; `thesis_docs/WORKSPACE_CLEANUP_MANIFEST.md` |
| 2026-08-12 | Deleted the validated obsolete `grooming-detector-main` and `grooming-detector-main-2` trees after preserving unique data and provenance evidence. Workspace size fell to approximately 0.795 GiB from roughly 17.6 GiB across the former project trees. Removed regenerable Python/pytest temporary caches except one permission-locked, Git-ignored `.pytest_cache`. Moved the final non-README experiment Markdown into `thesis_docs/`. Verified only the root `.git` remains and all canonical models, results, paper, and evidence files still exist. These deleted trees and nested Git histories are not recoverable locally. | `thesis_docs/WORKSPACE_CLEANUP_MANIFEST.md`; root `.git`; retained canonical project and artifacts |
| 2026-08-12 | Completed final cleanup verification. Removed the last permission-locked `.pytest_cache` with path-specific elevated approval. Confirmed no Python/pytest caches remain, only the root `.git` exists on branch `main`, all non-README Markdown records are in `thesis_docs/`, and the workspace contains 152 files totaling approximately 0.795 GiB. Recorded SHA-256 hashes for the latest LSTM, final evaluation JSON, active Layer 1 weights, and authoritative paper DOCX. No initial Git commit was created. | `thesis_docs/WORKSPACE_CLEANUP_MANIFEST.md`; root Git status; retained-artifact hash audit |
| 2026-08-12 | Recorded the user's explicit provenance correction that `grooming-detector-main-2` was the bundle containing the latest trained Layer 1 model and the trainer script supplied earlier. Reconciled this with the pre-deletion hash audit: the surviving canonical Layer 1 weights are byte-identical, and the exact trainer, likely training-source CSVs, and trainer states were preserved. Updated authority documents to describe both duplicate trees as deleted. The custom `--label-mode` and exact executed command remain unserialized. | `CURRENT_STATE_ZERO_AMBIGUITY.md`; `MODEL_AUTHORITY_MAP.md`; `WORKSPACE_CLEANUP_MANIFEST.md`; preserved Layer 1 archive and evidence files |
| 2026-08-12 | Consolidated redundant documentation. Removed four fully superseded model-state/progress/handoff documents after merging their surviving authority into `CURRENT_STATE_ZERO_AMBIGUITY.md`, the experiment record, cleanup manifest, and this log. Moved eight older paper drafts, planning documents, and the recovered conversation record into labeled archive subfolders. The `thesis_docs` root now contains six authoritative Markdown files. No code, model, dataset, evaluation result, or current paper was changed. | `thesis_docs/README.md`; `thesis_docs/archive/`; authoritative documentation set |

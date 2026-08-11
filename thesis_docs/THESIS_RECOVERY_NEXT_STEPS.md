# Thesis Decision and Change Log

**Current-state authority:** `CURRENT_STATE_ZERO_AMBIGUITY.md`  
**Detailed historical log:**
`archive/recovery/FULL_THESIS_RECOVERY_LOG_2026-08-10_TO_2026-08-12.md`

This is the compact, current log. Every material code, model, data, evaluation,
paper, provenance, or workspace change must receive a dated row here. The
archived full log preserves every granular update from the recovery and LSTM
repair sessions, including superseded findings.

## Immediate Next Steps

1. Preserve the existing author-disjoint LSTM checkpoint and evaluation as the
   fixed-Layer-1 conditional baseline.
2. Replace invalid PAN diff-derived message labels with a genuinely annotated
   message-level source, or explicitly use weak author-level supervision.
3. Apply one frozen connected-author partition across every PAN-dependent
   stage, including Layer 1 and Layer 2.
4. Save the exact Layer 1 command, dataset hashes/row manifest, package
   versions, seed, checkpoint-selection rule, and validation metrics.
5. Retrain and evaluate once against the weighted scorer and current-score-only
   classifier, then write Results and Recommendations from that final report.

## Milestone Log

| Date | Milestone | Persistent evidence |
|---|---|---|
| 2026-08-10 | Recovered the project history, repaired the LSTM training/evaluation workflow, added validation-only threshold and checkpoint selection, and ran weighted-loss and conversation-supervised trials. | Archived full recovery log; trial checkpoints, logs, and evaluation JSON files in the active pipeline |
| 2026-08-12 | Audited the original conversation split and found substantial author/predator-author overlap. Implemented deterministic connected-author partitions with zero conversation, author, and predator-author overlap. | `author_disjoint_split_audit.json`; `splitting.py`; focused tests |
| 2026-08-12 | Completed the frozen author-disjoint LSTM run. Test LSTM: recall 0.8333, precision 0.8750, F1 0.8537, F0.5 0.8663, AUC 0.9904, 5 false positives. It beats both required Layer 2 comparators under the fixed Layer 1 boundary. | `AUTHOR_DISJOINT_EXPERIMENT.md`; `lstm_author_disjoint_evaluation.json`; saved checkpoint and logs |
| 2026-08-12 | Confirmed that PAN12 diff locations are correction metadata, not grooming-message labels. The current LSTM result therefore remains conditional and is not a clean end-to-end unseen-author claim. | `CURRENT_STATE_ZERO_AMBIGUITY.md`; PAN readme/diff audit |
| 2026-08-12 | Matched the user-supplied context-window/F1 trainer to the active Layer 1 checkpoint family. Best-supported label mode is `suspicious`, but the exact command, custom flag, and row manifest were not serialized. | Preserved trainer; checkpoint `training_args.bin`; trainer-state evidence |
| 2026-08-12 | Confirmed that deleted `grooming-detector-main-2` was the latest trained Layer 1 bundle. The surviving canonical Layer 1 weights are byte-identical, and its trainer/data candidates/trainer states were preserved before deletion. | `WORKSPACE_CLEANUP_MANIFEST.md`; retained SHA-256 hashes and Layer 1 archive |
| 2026-08-12 | Consolidated nested repositories into one root Git repository, removed validated duplicate project trees and caches, and retained the canonical models, data evidence, results, and paper. | `WORKSPACE_CLEANUP_MANIFEST.md` |
| 2026-08-12 | Consolidated documentation: deleted four fully superseded model-state/handoff reports, archived nine older drafts/plans/recovery records, and reduced the active documentation root to six authoritative Markdown files. No code, model, dataset, evaluation result, or current paper changed. | `README.md`; `archive/`; `WORKSPACE_CLEANUP_MANIFEST.md` |
| 2026-08-12 | Prepared the first consolidated root Git baseline. Extended ignore rules so raw PAN diff/predator/ground-truth files and the recovered raw conversation Markdown remain local alongside the already excluded checkpoints, caches, logs, PAN CSV/XML files, and JSONL transcripts. Reproducibility code, compact history, trainer-state evidence, synthetic datasets, evaluation JSON, split audit, and current paper remain eligible for version control. | `.gitignore`; root Git staging audit |

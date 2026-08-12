# Thesis Decision and Change Log

**Current-state authority:** `CURRENT_STATE_ZERO_AMBIGUITY.md`  
**Detailed historical log:**
`archive/recovery/FULL_THESIS_RECOVERY_LOG_2026-08-10_TO_2026-08-12.md`

This is the compact, current log. Every material code, model, data, evaluation,
paper, provenance, or workspace change must receive a dated row here. The
archived full log preserves every granular update from the recovery and LSTM
repair sessions, including superseded findings.

## Consultation Demonstration for 2026-08-13

### What is ready to show

The defensible update is a **working provisional two-layer pipeline** and a
frozen Layer-2 comparison, not a final end-to-end thesis result. The latest
author-disjoint LSTM achieved recall 0.8333, precision 0.8750, F0.5 0.8663,
and AUC 0.9904 on its held-out test partition. Under the same fixed Layer 1,
the weighted scorer achieved F0.5 0.2023 and the Layer-1-only comparator
achieved F0.5 0.0000. The browser demo now runs the saved author-disjoint LSTM
turn by turn, displays the validation-selected threshold, retains the weighted
score as a comparator, and shows the frozen comparison table on the same page.

### Exact launch procedure

Open PowerShell and run:

```powershell
Set-Location 'C:\Projects\THESIS\grooming-detector\grooming-detector-trajectory-pipeline'
.\run_consultation_demo.ps1
```

If PowerShell execution policy blocks that launcher, run `python -m demo.app`
from the same folder instead.

Wait for `Ready.`, then open `http://127.0.0.1:5000`. Initial model loading was
smoke-tested offline on the project machine and took approximately 11 seconds.
The page and message API returned HTTP 200 in the final check.

### Sixty-second explanation

> The major implementation update is that the LSTM is now functioning as the
> sequence-level second layer. I also replaced the leaky conversation split
> with a connected-author-disjoint split, selected the alert threshold using
> validation data only, and compared all methods on the same held-out Layer-2
> partition. Under that fixed boundary, the LSTM substantially outperformed
> both the weighted scoring method and the message-classifier-only ablation.
> During the audit, however, I discovered that the existing PAN training
> `is_suspicious` field came from corpus correction metadata, not real
> message-level grooming annotation. Therefore these are explicitly provisional
> fixed-Layer-1 results. The next experiment will independently annotate the
> message data, retrain Layer 1 under the same author-disjoint boundary, and then
> repeat the frozen comparison end to end.

### Ask the adviser to decide

1. Is two independent reviewers for all 1,335 candidate messages acceptable,
   or is a documented overlapping subset plus adjudication sufficient?
2. May the thesis retain the current fixed-Layer-1 LSTM result as a preliminary
   or ablation result while reserving the clean retrained run as the final result?
3. Does the adviser approve requesting the Cook et al. and Cano Basave et al.
   labelled datasets as supplementary Layer-1 sources?

### Do not claim

- Do not call the current run the final end-to-end model.
- Do not describe PAN training `is_suspicious` as genuine message annotation.
- Do not call a live typed message a validated safety decision; the page is a
  mechanism demonstration.
- Do not interpret the current live Layer-1/LSTM values as a faithful run of
  the recovered context-window trainer: the UI currently passes one isolated
  message to Layer 1 instead of current plus two preceding messages.
- Do not retrain or tune anything immediately before the consultation. Use the
  frozen JSON and checkpoint already verified.

## Immediate Next Steps

1. Preserve the existing author-disjoint LSTM checkpoint and evaluation as the
   fixed-Layer-1 conditional baseline.
2. Complete two independent message-level reviews of the 1,335 synthetic
   candidates, adjudicate disagreements, and freeze approved rows. The audit
   confirms that the generated labels themselves are not final ground truth.
3. Apply the existing frozen connected-author partition across every PAN-dependent
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
| 2026-08-12 | Audited all preserved Layer 1 candidate sources and implemented a deterministic manifest generator. Confirmed that the 739-message grooming file copies speaker role directly into `is_suspicious`, while the 596-message safe file assigns scenario-derived zeros; neither has independent human message annotation. The generators also lack a model digest, seed, raw-response archive, and adjudication. PAN remains excluded from message-level supervision because its `is_suspicious` field is diff metadata; its frozen author-disjoint assignments are now recorded as a hard boundary for any optional weak supervision. Generated a 1,335-row two-reviewer worksheet and explicitly blocked retraining with zero approved rows until annotation/adjudication is complete. | `grooming-detector/data_sources/layer1_dataset_manifest.json`; `layer1_annotation_candidates.csv`; `data_sources/README.md`; `audit_layer1_dataset.py`; focused tests |
| 2026-08-12 | Rechecked PAN12 line semantics against all three PAN-relevant sources cited in the thesis and the retained official ground truth. PAN12 genuinely defined a line-identification test task, but the organizers explicitly released no line-level training data; they later pooled and manually judged submitted test lines, mostly through one expert. The retained Problem-2 file contains 6,478 judged lines across 834 test conversations and has zero conversation overlap with the 16,948-entry training diff or current training CSV. Its matching test XML is absent locally. Villatoro-Tello uses derived conversation labels and no line training labels; Street et al. classify Adult-versus-Child speaker role rather than grooming behavior. Corrected the authority report: every current PAN `is_suspicious` value remains invalid as grooming-message truth, while the separate official test judgments may be a qualified future evaluation resource if their exact corpus is recovered. | Official PAN overview cited as [13]; Villatoro-Tello et al. [14]; Street et al. [2]; retained PAN ground-truth readme/problem2 file; local ID-overlap audit |
| 2026-08-12 | Fixed the permitted use of PAN12 Problem 2: frozen external message-level evaluation only, never training, validation, tuning, early stopping, or annotation guidance. Any future result must disclose pooled/single-expert, non-exhaustive judgments and use the exact matching test XML plus original conversation/line IDs; the local ID file alone cannot be evaluated. Use the official precision, recall, and recall-weighted F3 measure for comparability. | `CURRENT_STATE_ZERO_AMBIGUITY.md`; official PAN12 overview, Sections 2.2, 3.2, and 4.2 |
| 2026-08-12 | Audited established alternatives to PAN12. The best Layer-1 acquisition targets are Cook et al. (2023: 6,771 offender messages from 24 PJ chats, 11 strategies plus null, two forensic-psychology coders) and Cano Basave et al. (2014: predator lines from 50 PJ transcripts, three grooming stages plus Other, two trained analysts with agreement-only labels). No public data package was located for either, so access must be requested. Gupta's 75 annotated positive chats are a weaker fallback. ChatCoder2/PANC are useful for supplementary early-detection work but reuse PJ/PAN sources and do not provide fresh message-onset truth; LiveMe is modern and large but its grooming signal is analysis-derived rather than expert message annotation. Any acquired PJ-derived data must undergo transcript/author overlap and licensing/ethics audits before use. | `CURRENT_STATE_ZERO_AMBIGUITY.md`; Cook et al. AIES 2023; Cano Basave et al. SocInfo 2014; Gupta et al. 2012; Vogt et al. ACL 2021; Lykousas and Patsakis 2020 |
| 2026-08-12 | Prepared the 2026-08-13 consultation demonstration. Updated the browser demo to run the saved author-disjoint LSTM instead of presenting the weighted scorer as the active model; added the validation-selected LSTM threshold, weighted comparator, frozen three-method results table, and an explicit provisional fixed-Layer-1 warning. Made the base DistilBERT encoder load from the local cache to avoid network retries. Added a focused LSTM-demo test; all 56 tests passed with a workspace-local pytest base directory. Real model loading and one-message scoring passed offline, and Flask page/API checks returned HTTP 200. Added a simple PowerShell launcher and updated the package README to identify the LSTM as active and quarantine its superseded weighted-only methodology notes. Browser visual inspection could not be performed because no controllable browser was connected. | `run_consultation_demo.ps1`; `demo/scoring_core.py`; `demo/app.py`; `demo/templates/chat.html`; `demo/static/app.js`; `demo/static/style.css`; `demo/replay.py`; `tests/test_demo_scoring_core.py`; `features.py`; pipeline `README.md`; consultation section above |
| 2026-08-12 | Diagnosed the first live consultation example. The screen correctly reported no alert for that run, but code inspection exposed an additional input-protocol limitation: the recovered Layer-1 checkpoint was trained on current plus two preceding messages, while `MessageClassifier.score(text)` and the live demo pass only the isolated current message. The LSTM receives the full sequence but its trajectory features inherit those isolated-message probabilities. Recorded that the live UI is presently a mechanism demonstration only; context-matched Layer-1 scoring, cache regeneration, Layer-2 retraining, and reevaluation are required before using its values as model evidence. | `CURRENT_STATE_ZERO_AMBIGUITY.md`; `message_classifier.py`; recovered `train_distillbert.py`; live screenshot |

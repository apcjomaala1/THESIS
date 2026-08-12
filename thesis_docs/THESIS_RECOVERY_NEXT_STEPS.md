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
historical Layer-2 development run, not a final comparison or end-to-end thesis result. The latest
author-disjoint LSTM achieved recall 0.8333, precision 0.8750, F0.5 0.8663,
and AUC 0.9904 on its held-out test partition. The displayed weighted and
current-score-only rows are retained only as historical outputs: an audit found
unmatched validation tuning and a threshold that made the current-score-only
row incapable of flagging. The browser demo now runs the saved author-disjoint LSTM
turn by turn, displays the validation-selected threshold, retains the weighted
score as a legacy output, and shows the historical table with an explicit
invalid-comparison warning on the same page.

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
> partition. That provisional LSTM produced strong development numbers, but a
> subsequent audit found that the displayed baselines were not fairly tuned and
> the classifier ablation could not cross its inherited threshold. I am not
> claiming a confirmed baseline victory from that run.
> During the audit, however, I discovered that the existing PAN training
> `is_suspicious` field came from corpus correction metadata, not real
> message-level grooming annotation. Therefore these are explicitly provisional
> fixed-Layer-1 results. The next experiment will independently annotate the
> message data, retrain Layer 1 under the same author-disjoint boundary, and then
> repeat the frozen comparison end to end.

### Ask the adviser to decide

1. Does the adviser approve narrowing the final time-constrained endpoint to
   author-disjoint identification of PAN12 conversations containing a listed
   predator, with genuine message-level grooming/onset detection deferred until
   independently verified message annotations are available, and revising the
   title, questions, scope, and methodology accordingly?

If the adviser rejects this change, there is no defensible quick substitute:
message-level work requires independent human annotation or acquisition of a
suitable annotated corpus.

### Do not claim

- Do not call the current run the final end-to-end model.
- Do not claim that the current LSTM fairly beat the weighted scorer or Layer 1;
  the comparator thresholds were unmatched and the displayed classifier row
  could not cross its inherited threshold.
- Do not describe PAN training `is_suspicious` as genuine message annotation.
- Do not call a live typed message a validated safety decision; the page is a
  mechanism demonstration.
- Do not interpret the current live Layer-1/LSTM values as a faithful run of
  the recovered context-window trainer: the UI currently passes one isolated
  message to Layer 1 instead of current plus two preceding messages.
- Do not retrain or tune anything immediately before the consultation. Use the
  frozen JSON and checkpoint already verified.

## Immediate Next Steps

### Recommended time-constrained rescue path

The primary final experiment should be narrowed to **conversation-level
identification of PAN12 conversations containing a listed predator**. This is
the only large, locally available PAN12 target whose provenance is currently
defensible. The LSTM remains the proposed sequence model. The existing result
remains a provisional fixed-pipeline development result, not the final result.

Execute the rescue in this order:

1. Preserve the existing checkpoint, split audit, and evaluation without
   overwriting them.
2. Freeze a new connected-author final holdout before rebuilding because the
   previous test result has already been inspected. If the deadline requires
   reuse, call it a retrospective corrected rerun, not a pristine final test.
3. Rebuild Layer 1 using no PAN `is_suspicious` values. Under the fast rescue,
   train it only as an explicitly **weakly supervised predator-author message
   classifier**, using PAN's valid predator-author list, current plus two
   preceding messages, and training-partition conversations only. Its output
   must not be called a message-level grooming probability.
4. Select the Layer-1 checkpoint and any operating choices using validation
   data only, then generate a fresh context-matched score cache keyed by stable
   conversation/line IDs. Save row IDs, hashes, command, seed, versions, and
   model digest.
5. Retrain the LSTM using the valid conversation target only. Disable the
   current turn-level loss derived from `is_suspicious`; do not substitute
   repeated predator-author labels as grooming-onset truth.
6. Recompute the benign centroid from training-partition data only and save its
   source-ID manifest and digest.
7. Compare the raw Layer-1 classifier, weighted scorer, keyword baseline, and
   LSTM on identical frozen partitions and the same conversation endpoint.
   Independently select each learned method's threshold/configuration on the
   same validation partition. For the primary architecture comparison, use a
   seven-feature LSTM against the seven-feature weighted scorer; report the
   775-input LSTM separately or with matched ablations.
8. Iterate only from training/validation evidence. Run the untouched held-out
   test exactly once after the protocol is frozen; report the result even if
   the LSTM does not win.
9. Report conversation-level recall, precision, F1, F0.5, AUC, confusion
   counts, split sizes, and uncertainty where feasible. Describe the Layer-1
   supervision honestly as weak supervision.
10. Rename demo labels and thesis claims accordingly: the live value is a
   provisional conversation-risk trajectory, not a validated per-message
   grooming determination or grooming-onset detector.

This route preserves the required LSTM-versus-weighted-versus-classifier
comparison while removing the known false PAN message target and end-to-end
author leakage. It does **not** guarantee in advance that the LSTM will win;
model development may optimize validation performance, but an unfavorable
held-out result must not be hidden or tuned away.

### Paper revision gate after adviser approval

Do not rewrite the study endpoint before the adviser answers the scope question
above. If approved, revise the title, research questions, objectives, scope,
and methodology together so they consistently say **conversation-level PAN12
predator-conversation identification**, not validated message-level grooming or
onset detection. The revision must also:

- remove the claims that PAN supplied suspicious-line training annotations,
  that the synthetic files were manually annotated, and that a separate real
  message-annotated study dataset was used;
- identify Layer 1 as author-derived weak supervision and its output as a proxy
  score rather than a grooming probability;
- state that the 768 LSTM embedding inputs come from base
  `distilbert-base-uncased`, while the fine-tuned classifier supplies the
  trajectory risk proxy;
- describe connected-author partitioning, the newly locked final holdout,
  training-only centroid construction, conversation-only LSTM loss, and
  validation-only selection exactly as implemented;
- report raw Layer 1, independently tuned weighted scoring, matched-input LSTM,
  the full-input LSTM as a separate model, and the paper-promised keyword
  baseline on the same endpoint; and
- remove or mark as future work any redaction, adversarial robustness, live
  deployment, or early-onset validation that was not actually implemented.

### If message-level grooming remains mandatory

There is no responsible instant substitute. Complete independent human review
and adjudication of the 1,335-row worksheet (LLM output may only assist), or
recover and qualify an appropriate genuinely annotated corpus. Validation and
test must remain human-reviewed. This is a separate, slower extension and
must not delay the conversation-level rescue unless the adviser explicitly
rejects the narrowed endpoint.

## Milestone Log

| Date | Milestone | Persistent evidence |
|---|---|---|
| 2026-08-10 | Recovered the project history, repaired the LSTM training/evaluation workflow, added validation-only threshold and checkpoint selection, and ran weighted-loss and conversation-supervised trials. | Archived full recovery log; trial checkpoints, logs, and evaluation JSON files in the active pipeline |
| 2026-08-12 | Audited the original conversation split and found substantial author/predator-author overlap. Implemented deterministic connected-author partitions with zero conversation, author, and predator-author overlap. | `author_disjoint_split_audit.json`; `splitting.py`; focused tests |
| 2026-08-12 | Completed the frozen author-disjoint LSTM development run. Test LSTM: recall 0.8333, precision 0.8750, F1 0.8537, F0.5 0.8663, AUC 0.9904, 5 false positives. The initial apparent comparator advantage was later withdrawn by the final audit row below. | `AUTHOR_DISJOINT_EXPERIMENT.md`; `lstm_author_disjoint_evaluation.json`; saved checkpoint and logs |
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
| 2026-08-12 | Evaluated the proposal to have an LLM annotate messages using OGDM. Approved it only as pre-annotation or explicitly disclosed weak supervision, not as sole ground truth. Fixed the defensible protocol: OGDM-derived observable behavior tags on the current message under inference-matched preceding context; no predator/diff/source leakage; a human-adjudicated pilot used to validate the LLM; versioned prompts and raw outputs; human-reviewed validation and test labels; privacy/licence/ethics approval before hosted processing; and deterministic computation of the seven trajectory features rather than LLM assignment. Recommended piloting a stratified subset or the existing 1,335-row worksheet before scaling, followed by context-matched Layer-1 retraining, cache regeneration, and full Layer-2 reevaluation. | `CURRENT_STATE_ZERO_AMBIGUITY.md`; Lorenzo-Dus et al. (2016); Gilardi et al. (2023); Horych et al. (2025); Kasner et al. (2026) |
| 2026-08-12 | Set the initial time-constrained rescue direction, later refined by the final audit row below: narrow the primary endpoint to PAN12 conversation-level predator-conversation identification; rebuild context-matched Layer 1 as disclosed author-derived weak supervision; remove PAN `is_suspicious`; and train the LSTM with conversation loss only. Message-level grooming remains a separate annotation-dependent extension. | Time-constrained rescue section above; `CURRENT_STATE_ZERO_AMBIGUITY.md`; PAN training readme and preprocessing audit |
| 2026-08-12 | Corrected the provisional comparison claim after a deeper evaluator audit. Only the LSTM threshold was selected on the author-disjoint validation split; the weighted scorer reused an older configuration, while the displayed current-score-only row passed `0.1 * probability` through another sigmoid and then used threshold 0.7 even though its possible range was only about 0.500–0.525. Its zero recall is an artifact, not classifier evidence. The LSTM also received 775 inputs versus the weighted scorer's seven, and the saved benign centroid has no proof of training-only construction. Withdrew the claim that the LSTM has fairly beaten both baselines; preserved its numbers only as a historical development result. Added requirements for a new locked holdout, training-only centroid, independently validation-tuned raw Layer 1/weighted/keyword comparisons, and a matched seven-feature LSTM comparison. Relabeled the consultation UI so it cannot visually present the historical table or live outputs as final risk evidence. All 56 tests passed after the UI/documentation corrections. | `evaluate_lstm_checkpoint.py`; `main.py`; `weighted_scorer.json`; `trajectory_model_lstm.py`; `run_pipeline.py`; demo template/JavaScript/style; corrected authoritative reports; pytest output |
| 2026-08-12 | Rebuilt the consultation interface into a presentation-ready conversation trajectory lab. Added a prominent development-only guardrail, active-LSTM pipeline strip, two-speaker chat with automatic alternation, selected-turn score/threshold/distance/sequence summary, a turn-by-turn trajectory chart, plain-language feature inspection, explicit below-threshold-is-not-safe wording, loading and error feedback, keyboard-accessible turn selection, responsive layouts, and a clear/reset confirmation. Moved the flawed comparison and the three known protocol defects into collapsed audit panels. Removed mojibake and misleading green/winner styling. Added route/content/DOM-binding guardrail tests; JavaScript syntax passed and the full suite passed 59/59. The live page returned HTTP 200 and a two-turn real-model API smoke test returned all seven features. Visual browser QA could not be completed because no controllable browser was connected; the local server was left running for immediate manual inspection. | `demo/templates/chat.html`; `demo/static/style.css`; `demo/static/app.js`; `demo/app.py`; `tests/test_demo_app.py`; pipeline `README.md`; local HTTP/API checks; pytest output |
| 2026-08-13 | Applied Comment Matrix 2 across the main paper, code, and consultation deck. The paper now uses `Conversation Trajectory Lab` as the short title; standardizes dataset inventory and label provenance; defines the seven trajectory features and corrected split/evaluation protocol; records the current software environment; limits Philippine relevance to motivation rather than validation; distinguishes the base DistilBERT encoder from the historical Layer 1 proxy; and consistently describes offline replay, invalid PAN diff supervision, unmatched historical comparisons, and the absence of a final superiority result. The code batch deliberately avoided changing training targets or producing new model results: it added direct-identifier masking before demo scoring/in-memory retention, opaque server-generated conversation IDs, rejection of unknown user-supplied IDs, no-store response headers, offline terminology, an environment snapshot/checker, SciPy as an explicit dependency, and guardrail tests. The 34-slide PowerPoint was edited in its inherited template; slides 19-23 now account for all ten comments, while the study/method slides and speaker notes were corrected so pending methodology work is not presented as complete. Final verification: 68/68 pipeline tests passed; the recorded environment matched; JavaScript syntax passed; every final slide was visually inspected; PowerPoint overflow and template-fidelity checks passed with zero issues. | `Finals_Revised_Paper_WASD.md`; `WASD - Thesis 2.pptx`; `privacy.py`; `demo/app.py`; `demo/scoring_core.py`; `capture_environment.py`; `environment_snapshot.json`; `tests/test_privacy.py`; `tests/test_environment_snapshot.py`; demo tests; pipeline README |
| 2026-08-13 | Corrected the Comment Matrix scope after the preceding batch overreached. Restored the paper and presentation's adviser-dependent methodology content instead of pre-emptively changing labels, dataset interpretation, research questions, objectives, training, baselines, or final evaluation. Retained only items that can be completed independently now: privacy safeguards, Philippine-context limitations, the short module title, implemented feature formulas, current software versions, and offline-deployment wording. Rebuilt the four Comment Matrix slides in explanatory language and explicitly marked items 3, 4, 6, and 10 as awaiting adviser approval. Kept the unrelated privacy, offline-demo, and reproducibility code changes. The original PowerPoint was open and Windows refused in-place replacement, so the verified correction was saved as `WASD - Thesis 2 - corrected.pptx`; it is the authoritative presentation copy until the open original can be replaced. Verification passed: 68/68 tests, environment snapshot, JavaScript syntax, template fidelity, visual review of edited slides, and element-bounds inspection. This row supersedes the preceding row's claim that all evidence-supported methodology revisions were applied to the paper and deck. | `Finals_Revised_Paper_WASD.md`; `WASD - Thesis 2 - corrected.pptx`; this recovery log; `CURRENT_STATE_ZERO_AMBIGUITY.md` |
| 2026-08-13 | Reconverted the current Markdown thesis into an editable Word document. The Markdown remains the unchanged content authority; the retained July Word copy was used only as the visual/style reference. Preserved the cover, chapter hierarchy, numbered questions/objectives/features, equations, hyperlinks, references, and three editable tables. This was a format conversion only and made no new methodology or claim revisions. The final 22-page render was inspected page by page with no clipping, overlap, or missing conversion content found. | `Finals_Revised_Paper_WASD.docx`; `thesis_docs/Finals_Revised_Paper_WASD.md`; final DOCX render audit |

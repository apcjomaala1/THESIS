# Thesis Documentation Index

The main folder intentionally contains only the current authoritative records.
Older paper drafts, recovery transcripts, and superseded plans are under
`archive/` and must not be treated as current specifications.

## Authoritative Set

1. `CURRENT_STATE_ZERO_AMBIGUITY.md` - historical August 12 recovery report;
   its model and label descriptions are superseded by the current manuscript.
2. `AUTHOR_DISJOINT_EXPERIMENT.md` - historical 2026-08-12 development run;
   retained as evidence but superseded by the revised final evaluation.
3. `THESIS_RECOVERY_NEXT_STEPS.md` - chronological decision/change log. Read
   later rows when an older row conflicts with a newer correction.
4. `WORKSPACE_CLEANUP_MANIFEST.md` - repository and documentation cleanup
   record, retained hashes, and recovery limitations.
5. `Finals_Revised_Paper_WASD.md` - authoritative Chapters I-III Markdown.
6. `CHAPTER_IV_RESULTS_AND_DISCUSSION.md` - authoritative final results and
   discussion from the revised F2 analysis of preserved test-score artifacts.
7. `CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md` - authoritative
   summary, conclusions, and recommendations aligned with the frozen endpoint.
8. `EXPLAINER_FOR_STUDENTS_AND_ADVISERS.md` - plain-language defense guide
   awaiting synchronization with the September 20 F2 manuscript revision.
9. `PANEL_COMMENTS_MATRIX.md` - one-row-per-comment response matrix for the
   final-panel feedback, including completed manuscript actions, remaining
   empirical work, exact evidence locations, and ready defense responses. Its
   September 15 three-page export, not yet synchronized with the F2 matrix update, is `output/pdf/WASD_Final_Panel_Comments_Matrix.pdf`.
10. `PRESENTATION_SPEAKER_SCRIPT.md` - current defense rehearsal script, numbered to match `WASD - Thesis 2 - F2 and latency revised.pptx` and coordinated with its speaker notes.
11. `README.md` - this index.

The established Word counterpart for Chapters I-III remains at the workspace root (F2 synchronization pending):
`C:\Projects\THESIS\Finals Revised Paper WASD.docx`.

**Current manuscript status (updated September 28):** the authoritative Chapters I-V Markdown and abstract use the GroomShield title naming DistilBERT and LSTM-based behavioral sequence modeling, and an F2/recall-focused final conversation policy. Chapter IV reports validation-selected F2 cutoffs applied to previously evaluated test scores; Section 3.5.1 gives the explicit F2 threshold-selection procedure and cutoff table, and Section 3.5.2 records the evaluation chronology. The Trajectory-Feature LSTM detects 41/44 positives (recall 0.9318, precision 0.6613, F2 0.8613; 21 false positives), and the Embedding-and-Feature LSTM detects 44/44 (precision 0.5176, F2 0.8429; 41 false positives). Neither variant is designated the primary model. Both use DistilBERT upstream; their names distinguish the seven-feature versus 775-dimensional direct recurrent inputs. Research questions, adviser-locked objectives, Chapter II, and references remain unchanged.

**Current synchronization boundary (September 30):** The authoritative Chapters I-V Markdown, complete Word/PDF paper, current presentation and speaker script, and panel matrix include the F2 results and F0.5/F1/F2 comparison. The live demo continues to use the F2 cutoffs. Chapter III Section 3.5.4 and Chapter IV Table 4.4 report the local CPU latency benchmark for both LSTMs; its reproducible code is `demo_live/benchmark_latency.py` in the trajectory pipeline and the receipt is `.benchmark_evidence/latency_2026-09-27.json`. The separate Chapters I-III Word file, alignment table, defense guide, and matrix PDF remain older versions. Original models, checkpoint records, final-test gate, and original evaluation outputs remain unchanged. ABSTRACT_F2.md contains the abstract also inserted into the main Markdown. Reproduce F2 results with `python thesis_docs/.threshold_analysis/analyze_f2_test.py`; the aggregate receipt is `.threshold_analysis/f2_test_reanalysis.json`.

**Current presentation flow (September 30):** `WASD - Thesis 2 - F2 and latency revised.pptx` has 24 visible slides, two hidden evidence backups, and five hidden original template resources. The talk now runs from motivation and approved objectives through alignment, design, controlled evaluation, results/trade-offs, and conclusions by objective. The two separate LSTM cutoff slides are one editable six-row comparison on slide 19; all five methods' F2 results remain on slide 16. The early alignment tables, architecture, three retained native result charts, latency, and F1-versus-F2 recommendation remain available. `PRESENTATION_SPEAKER_SCRIPT.md` and embedded notes follow the new slide order. One visual QA render of this condensed candidate was performed; a single wording correction was then checked structurally without rerendering. Earlier dated deck entries below describe superseded versions, not the current slide count. No paper, model, threshold, test score, Word/PDF, or earlier panel deck changed in this flow revision.

**September 21 matrix update:** PANEL_COMMENTS_MATRIX.md now records F2 threshold selection, current results, updated section references, and the defense responses for Comments 13 and 15. The PDF remains pending synchronization.

**September 27 demo/deck and latency update, renamed September 28:** `WASD - Thesis 2 - F2 and latency revised.pptx` is the current deck. It updates the F2 result table, four native charts, explanatory slides, speaker notes, and adds a local-latency slide. The source `WASD - Thesis 2 - panel revised.pptx` is retained as an earlier version. The demo loads both selected checkpoints, uses the recorded validation-selected F2 cutoffs, and displays both live outputs with equal emphasis under descriptive input-based names. Its example captions were rechecked under F2. The latency result is a warmed, synthetic, single-client localhost HTTP measurement, not production real-time validation. A lower pooled median for the embedding-and-feature variant does not establish faster overall performance: its p95/p99 are higher and throughput is slightly lower. No visual rendering was performed, per user request. Historical experiment keys and receipts retain their original names; Word manuscripts and the standalone architecture exports remain pending synchronization.

**September 29 policy-comparison update:** Chapter III Section 3.5.2 now explains the original F0.5 evaluation and subsequent validation-selected F1/F2 comparison. Chapter IV Section 4.2.1 and Table 4.1a report all five methods' three cutoffs, complete test confusion counts, precision, and recall. Chapter V adds the comparative finding and recommends independent workflow evaluation of the Embedding-and-Feature LSTM's F1 option (43/44 detected, 14 false alerts) against F2 (44/44 detected, 41 false alerts). F2 remains the main reported policy; model weights, active demo cutoffs, original receipts, objectives, and F2 bootstrap results are unchanged. Reproduce the comparison with `python thesis_docs/.threshold_analysis/compare_test_threshold_policies.py`; its aggregate receipt is `.threshold_analysis/test_threshold_policy_comparison.json`. The complete Word manuscript, current deck, and speaking script were subsequently synchronized as recorded below; the matrix PDF remains older. No rendering was performed for this initial Markdown revision.

**September 29 complete Word build:** `Finalized Complete Paper WASD - reconciled.docx` at the workspace root is now synchronized with the current authoritative Chapters I-V Markdown, including the GroomShield title, abstract, descriptive model names, F2 main results, local latency findings, and F0.5/F1/F2 comparison and recommendations. The reference cover's non-title content and author table, References and hyperlinks, section geometry, and unrelated package parts are preserved. Wide tables use clearly labeled parts under the manuscript's original table numbers; Table 4.1a has a confusion-count/cutoff part and a precision/recall part. All 15 policy rows, all generated prose/table text, and 48 native Word equations were checked structurally. No visual rendering was performed. Build code and receipt are `.docx_reconciliation_qa/build_current_complete_docx.py` and `.docx_reconciliation_qa/current_complete_docx_build_receipt.json`. The separate `Finals Revised Paper WASD.docx` Chapters I-III counterpart and older source copies remain unsynchronized. This build was not automatically committed or pushed.

**September 29 clean PDF export:** The current complete paper is also available at `output/pdf/Finalized Complete Paper WASD - reconciled.pdf` (43 pages). Exported directly through Word with document content selected, review markup excluded, and comments/revision display disabled. Structural checks found no comment annotations, confirmed the F0.5/F1/F2 comparison is included, and verified that the source DOCX remained byte-for-byte unchanged. No page-image rendering or visual QA was performed.

**September 29 presentation update:** `WASD - Thesis 2 - F2 and latency revised.pptx` now has 37 main slides, a hidden baseline-policy backup on slide 38, and five retained hidden template slides (39-43). Slides 30-31 compare F0.5/F1/F2 for each LSTM using editable native tables; slide 38 supplies the other nine policy rows. Slide 23 explains the selection objectives, slide 36 presents the independent F1-versus-F2 workflow recommendation, and all speaker notes match `PRESENTATION_SPEAKER_SCRIPT.md`. The existing four native charts and F2 results remain intact. Exactly one batch rendered all 43 slides for visual inspection. That pass identified an inherited error-chart axis capped at 25, low-contrast new table headers, a sparse cover, and fixed divider numbers. Corrected those issues, then checked the final package and geometry without a second render. Evidence and scripts are in `.pptx_revision_qa/`; see `artifact.md`. Word/PDF files and the earlier `panel revised` deck were not changed by this presentation update. No automatic commit or push.

**September 30 speaker-notes revision:** Rewrote the 37-slide main talk and the hidden baseline backup into a connected, read-aloud explanation, then synchronized the PPTX's embedded notes with `PRESENTATION_SPEAKER_SCRIPT.md`. Source citations remain in each note. The unchanged approved objectives are retained as a separate presenter reference in the script instead of interrupting slide 7's speech. Only 43 notes XML parts changed in the deck; every visible slide, chart, workbook, image, layout, and master part is byte-identical to the September 29 deck. PowerPoint opened the updated package; no new visual render was done for this notes-only change. Evidence is `.pptx_revision_qa/narrative_notes_receipt.json`. No automatic commit or push.

**Earlier artifact history (not current F2 synchronization):**

The Chapters I-III Word manuscript was synchronized on September 15 from the current authoritative Markdown after structural checks and one bounded visual-QA pass of all 22 pages. `Finals Revised Paper WASD.docx` has SHA-256 `D5FDF004C562AA0B134124149C764D6015021C5B3E3C6A3E79A221A142D2C60C`. The complete Chapters I-V manuscript, `Finalized Complete Paper WASD - reconciled.docx`, remains at the approved September 2 revision with SHA-256 `C204E31B375F9F833BA6252BF334C9121CB50BFD69E69CCD104F13E27CA89661`; its Chapter IV-V panel-response revisions remain Markdown-first until that complete manuscript is synchronized separately.

The September 16 defense-deck snapshot was `WASD - Thesis 2 - panel revised.pptx`, SHA-256 `8AA570A20855E238BC72D983E6C003C623AE85D993AED59ABB87F09E22A161FF`. It incorporates the September panel revisions while preserving the original theme and the research-first narrative. Slides 8-9 contain the concise editable alignment table, slide 16 maps OGDM to the features, and slide 18 contains the editable model architecture. The actual results table remains on slide 26. Four editable charts on slides 27, 28, 29, and 31 show PR-AUC/F0.5, recall, error counts, and the lengths of the four missed conversations. F0.5, connected-author partitioning, the current conversation target, and future latency/contemporary-data/onset evaluation are explained in plain language. The main presentation has 34 slides, including the team introduction; five original resource slides remain hidden. `PRESENTATION_SPEAKER_SCRIPT.md` matches the final slide order, and the same script is embedded in the speaker notes with sources. All slides were visually inspected in one PowerPoint render pass. Subsequent ordering and numeric alignment corrections were checked structurally, and the final deck reopened in PowerPoint with four native charts and their embedded workbooks. The earlier `final revised` deck is retained as the source revision.

## Standalone Visual Assets

The separate F1_THRESHOLD_VALIDATION_ANALYSIS.md records the September 17 final-cutoff comparison, extended September 19 to compare F0.5, F1, and F2 across all five methods on saved validation scores. That validation-only analysis leaves models and active thresholds unchanged. The September 20 manuscript uses the separate F2 test-score reanalysis described above. Scripts and aggregate receipts are in .threshold_analysis/.

`assets/AI_Model_Architecture_Diagram.svg` is the editable, programmatically generated architecture figure. Its 16:9 left-to-right flow separates contextual turn analysis, the author-derived proxy signal, seven chronological trajectory features, primary LSTM aggregation, and threshold-based human-review prioritization. `assets/AI_Model_Architecture_Diagram.png` is the high-resolution preview/export. The figure intentionally presents the research architecture independently of the dataset selected for evaluation. Its generator and verification receipt are in `.pptx_revision_qa/`.
`archive/paper_drafts/Finals_Complete_Paper_WASD_superseded.md` preserves the
superseded generated complete-paper draft for history only; it must not be used
for submission or methodology reference.

## Consolidation Rule

There are no separate current model-authority, label-provenance, progress, or
agent-handoff specifications. Their nonredundant facts were consolidated into
`CURRENT_STATE_ZERO_AMBIGUITY.md`, the experiment record, and the chronological
log before those superseded documents were removed.

## Archive

- `archive/paper_drafts/` - superseded paper drafts and an audit tied to a
  temporary Chapter 3.
- `archive/planning/` - older adviser-comment matrices and implementation/audit
  plans that predate the authoritative current model state.
- `archive/recovery/` - raw recovered conversation material.
- `archive/reconciliation/` - source-to-authority reconciliation decisions
  for externally edited manuscript copies.

Archived files are evidence only, not instructions for current work.

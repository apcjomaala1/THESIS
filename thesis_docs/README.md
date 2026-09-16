# Thesis Documentation Index

The main folder intentionally contains only the current authoritative records.
Older paper drafts, recovery transcripts, and superseded plans are under
`archive/` and must not be treated as current specifications.

## Authoritative Set

1. `CURRENT_STATE_ZERO_AMBIGUITY.md` - single source of truth for the current
   endpoint, model, completed evaluation, limitations, and next work.
2. `AUTHOR_DISJOINT_EXPERIMENT.md` - historical 2026-08-12 development run;
   retained as evidence but superseded by the revised final evaluation.
3. `THESIS_RECOVERY_NEXT_STEPS.md` - chronological decision/change log. Read
   later rows when an older row conflicts with a newer correction.
4. `WORKSPACE_CLEANUP_MANIFEST.md` - repository and documentation cleanup
   record, retained hashes, and recovery limitations.
5. `Finals_Revised_Paper_WASD.md` - authoritative Chapters I-III Markdown.
6. `CHAPTER_IV_RESULTS_AND_DISCUSSION.md` - authoritative final results and
   discussion derived from the frozen evaluation artifacts.
7. `CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md` - authoritative
   summary, conclusions, and recommendations aligned with the frozen endpoint.
8. `EXPLAINER_FOR_STUDENTS_AND_ADVISERS.md` - plain-language defense guide
   aligned with the authoritative paper and final results.
9. `PANEL_COMMENTS_MATRIX.md` - one-row-per-comment response matrix for the
   final-panel feedback, including completed manuscript actions, remaining
   empirical work, exact evidence locations, and ready defense responses. Its
   verified three-page export is `output/pdf/WASD_Final_Panel_Comments_Matrix.pdf`.
10. `PRESENTATION_SPEAKER_SCRIPT.md` - current defense rehearsal script, numbered to match the panel-revised deck and also embedded in its speaker notes.
11. `README.md` - this index.

The authoritative editable Chapters I-III paper remains at the workspace root:
`C:\Projects\THESIS\Finals Revised Paper WASD.docx`.

**Current 2026-09-15 manuscript status:** the latest authoritative Markdown has completed the full Chapters I-V framing review and the immediately actionable final-panel revisions. The research problem, two-layer contextual and behavioral architecture, and evaluation requirements are presented first; PAN-2012 is presented as the dataset selected to evaluate that work. The final-panel pass clarifies the conversation-level target, early-trajectory error pattern, production-latency boundary, contemporary-data requirement, OGDM feature motivation, connected-author partition evidence, and precision-oriented F0.5 threshold rationale. Dataset-specific label boundaries remain only where necessary for scope, methodology, and correct error interpretation. The exact original title, research questions, and adviser-locked objectives are unchanged.

The Chapters I-III Word manuscript was synchronized on September 15 from the current authoritative Markdown after structural checks and one bounded visual-QA pass of all 22 pages. `Finals Revised Paper WASD.docx` has SHA-256 `D5FDF004C562AA0B134124149C764D6015021C5B3E3C6A3E79A221A142D2C60C`. The complete Chapters I-V manuscript, `Finalized Complete Paper WASD - reconciled.docx`, remains at the approved September 2 revision with SHA-256 `C204E31B375F9F833BA6252BF334C9121CB50BFD69E69CCD104F13E27CA89661`; its Chapter IV-V panel-response revisions remain Markdown-first until that complete manuscript is synchronized separately.

The current defense deck is `WASD - Thesis 2 - panel revised.pptx`, SHA-256 `8AA570A20855E238BC72D983E6C003C623AE85D993AED59ABB87F09E22A161FF`. It incorporates the September panel revisions while preserving the original theme and the research-first narrative. Slides 8-9 contain the concise editable alignment table, slide 16 maps OGDM to the features, and slide 18 contains the editable model architecture. The actual results table remains on slide 26. Four editable charts on slides 27, 28, 29, and 31 show PR-AUC/F0.5, recall, error counts, and the lengths of the four missed conversations. F0.5, connected-author partitioning, the current conversation target, and future latency/contemporary-data/onset evaluation are explained in plain language. The main presentation has 34 slides, including the team introduction; five original resource slides remain hidden. `PRESENTATION_SPEAKER_SCRIPT.md` matches the final slide order, and the same script is embedded in the speaker notes with sources. All slides were visually inspected in one PowerPoint render pass. Subsequent ordering and numeric alignment corrections were checked structurally, and the final deck reopened in PowerPoint with four native charts and their embedded workbooks. The earlier `final revised` deck is retained as the source revision.

## Standalone Visual Assets

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

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
9. `README.md` - this index.

The authoritative editable Chapters I-III paper remains at the workspace root:
`C:\Projects\THESIS\Finals Revised Paper WASD.docx`.

**Current 2026-09-02 manuscript status:** the latest authoritative Markdown has completed a full Chapters I-V framing review. The research problem, two-layer contextual and behavioral architecture, and evaluation requirements are presented first; PAN-2012 is presented as the dataset selected to evaluate that work. Dataset-specific label boundaries remain only where they are necessary for scope, methodology, and correct error interpretation. The exact original title, research questions, and adviser-locked objectives are unchanged.

Following user approval, the authoritative Markdown was synchronized into both Word manuscripts. `Finals Revised Paper WASD.docx` now has SHA-256 `481A95449DD144EC07ADA0DD6E6B90100972BBE287645AE7501DC5606FB582D2`. `Finalized Complete Paper WASD - reconciled.docx` now has SHA-256 `C204E31B375F9F833BA6252BF334C9121CB50BFD69E69CCD104F13E27CA89661` and includes the approved Chapters IV-V wording and objective-aligned conclusions. Structural and exact-text verification passed. At the user's standing direction, no rendering was performed.

The current defense deck is `WASD - Thesis 2 - final revised.pptx`, SHA-256 `EB0F97D9E4C0060774DB4D07149F2B01F50CBF7475A4656CE29BAD9148BC6CA8`. It presents the research problem and two-layer architecture before explaining why PAN-2012 was selected for evaluation. The obsolete comment-matrix section was replaced with the frozen experimental setup, an editable held-out results table, the matched recurrent-versus-static comparison, and objective-aligned conclusions. Plain-language speaker scripts with source blocks are included on slides 1 and 3-29. Slides 2 and 30-34 remain unchanged. Body text was enlarged slightly, structural and text-fit checks passed with zero overflow warnings, and exactly one requested visual-QA render was performed without an iterative rendering loop.

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

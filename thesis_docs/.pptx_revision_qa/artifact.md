# September 29 presentation revision

Final artifact: `C:/Projects/THESIS/WASD - Thesis 2 - F2 and latency revised.pptx`.

## Content and verification

- 43 slides: 37 main, one hidden evidence backup, five retained hidden template resources.
- Added native editable F0.5/F1/F2 tables for both LSTMs and all three baselines, using the existing policy receipt; all 15 rows verified.
- F2 remains the main policy. The original F0.5 evaluation and subsequent F1/F2 saved-score comparison remain explicit in the speaking script and notes.
- Embedding F1 versus F2: 43 versus 44 detected; 14 versus 41 false alerts. The recommendation is independent workflow evaluation, not an already established deployment optimum.
- Trajectory F1 adds two false alerts over F0.5 without extra detections; F2 reduces misses from four to three.
- Revised selection explanation, architecture inputs, conclusions, recommendations, and all 43 notes; retained early alignment tables and local latency results.
- Retained all four native chart series/category data and the original F2 result table unchanged. Corrected the inherited error-chart value axis from 25 to 90 so values 78 and 41 are no longer clipped.
- Font policy: Calibri and Calibri Light, both verified reference fonts from the supplied deck.
- The managed presentation dependency loader was unavailable. Native PowerPoint automation preserved the supplied masters, layouts, charts, workbooks, and editable content. No Python-PPTX or Computer Use.

## Exactly one visual QA pass

Rendered all 43 slides once, using `render_policy_deck_once.ps1`, and inspected every image individually at 1280 x 720. That script refuses to render again if the QA output directory exists.

Corrections from that pass: error-chart scale, white-on-blue policy-table headers, cover title hierarchy, actual divider slide numbers, and shorter line-separated preparation/evaluation text. The architecture base-encoder label also explicitly identifies the current-turn embedding. Retained the original hidden resource slides, including their decorative content.

No second rendering or visual confirmation of these post-pass corrections was performed. Their saved OOXML, native geometry/text-fit, table values, notes, chart data, and axis limits were checked structurally.

Build sequence: `prepare_policy_deck.py`, `update_policy_comparison.ps1`, `verify_policy_deck.py`, `render_policy_deck_once.ps1` (once), `apply_single_pass_fixes.ps1`, `verify_policy_deck.py`. The content preparer expects the original 40-slide script and intentionally refuses a blind rerun against the revised 43-slide script.

No model, checkpoint, cutoff, evaluation source, approved objective, complete Word/PDF paper, or earlier dirty panel deck was changed. No commit or push.

## September 30 speaker-notes revision

The first delivery's notes recited slide content and did not sustain a clear argument. Rewrote the read-aloud script across slides 1-38 as a continuous explanation: motivation, objectives, design, dataset/controls, matched comparison, F2 result, operating-policy trade-off, conclusion, and independent next evaluation. Slide 7's exact approved objectives were moved from spoken notes to a clearly labeled presenter reference at the end of `PRESENTATION_SPEAKER_SCRIPT.md`; their wording was preserved. Slide 4's script heading now matches its existing visible title.

The rewritten text and original citations were embedded in the PPTX. Native PowerPoint saving also touched layout/master metadata, so the delivered package uses only the edited 43 notes XML parts and preserves every other original package part byte-for-byte. `verify_narrative_notes.py` confirms all 43 embedded notes match the script, all 192 non-note parts are identical, and PowerPoint opens the packaged deck. No slide render or visual QA pass was performed because visible content did not change. See `narrative_notes_receipt.json`.

## September 30 flow consolidation (current deck)

The user identified slide accumulation as the larger issue. The same deliverable now has **24 visible main slides**, **two hidden evidence backups**, and **five hidden template resources**, down from 37 visible slides. The talk's sequence is problem → questions/objectives and early alignment → theory/features/architecture → dataset and author-disjoint evaluation → F2 findings and cutoff trade-off → conclusions/next evaluation. Removed repeated introductions, section dividers, duplicate theoretical/setup exposition, the standalone recall chart, and the two separate LSTM policy slides. Added one native editable six-row comparison for both LSTMs' F0.5/F1/F2 outcomes. Moved the short-conversation chart and baseline policy table to hidden backups. Preserved the early alignment tables, architecture, the F2 result table, three native result charts with their values unchanged, and the local latency slide.

The read-aloud script was renumbered and all 31 slide notes synchronized. `condensed_flow_manifest.json` records the source-to-destination mapping; `condensed_flow_receipt.json` records the final structural check (passed) and output hash. `prepare_condensed_flow.py`, `build_condensed_flow.ps1`, and `verify_condensed_flow.py` reproduce the change from the preceding 43-slide version. The current source deck has already been replaced, so a blind rerun of the build script against that path is not appropriate; the staged source copy is retained locally.

Exactly one batch rendered the 31-slide condensed candidate at 1280 × 720 into `condensed_visual_pass_2026-09-30/`; the render script refuses another pass in that directory. Inspected the flow and critical slides, including alignment, architecture, all core results, cutoff comparison, and close. The new cutoff takeaway was changed from “alerts” to “false alerts” afterward, checked for text fit, and structurally reverified; it was **not** rerendered. No model, score, cutoff, objective, paper, Word/PDF, or earlier panel deck changed. No commit or push.

# September 16 presentation build

The final deliverables are `WASD - Thesis 2 - panel revised.pptx` and `thesis_docs/PRESENTATION_SPEAKER_SCRIPT.md`.

The accepted source deck remains `WASD - Thesis 2 - final revised.pptx`. The source slide order contained 29 slides; earlier prose that called it a 34-slide file was stale. The current output has 39 slides, of which 34 are visible.

To reproduce the content from the repository root, run these in order:

```powershell
& 'thesis_docs/.pptx_revision_qa/panel_update_2026_09_16.ps1' -SkipRender
python 'thesis_docs/.pptx_revision_qa/attach_native_result_charts.py'
python 'thesis_docs/.pptx_revision_qa/finalize_panel_deck.py'
```

The first command alone is an intermediate deck with chart placeholders. The second replaces those placeholders with native charts and verified embedded Excel data. The third finalizes the order, team-slide visibility, numeric table alignment, rehearsal script, and receipt. A reproduction requires fresh verification before delivery. Recorded visual inspection in the receipt describes the accepted September 16 run, not an automatic proof that a later rebuild has been inspected.

The accepted run used PowerPoint automation because the presentation dependency loader and artifact-tool package were unavailable. PowerPoint chart creation also failed, so chart XML and embedded workbook data were generated directly. The final deck was opened successfully in PowerPoint, and the charts rendered with the expected values.

Visual review used one set of 39 rendered slides under `tmp/presentation_panel_2026-09-16/final_render`. The final receipt maps final slide positions to those inspected render indices. Ordering and simple numeric alignment corrections followed that pass without a rendering loop. Those temporary previews are reproducible and are not authoritative manuscript or model evidence.

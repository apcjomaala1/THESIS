# Teammate DOCX Reconciliation - 2026-08-24

## Inputs and authority

- Current verified Chapters I-III DOCX: `Finals Revised Paper WASD.docx`
  - SHA-256: `F631C00B4CA0E777B3E200EC0631472304327C4A4E52E7AC0B4FAA38752A6F96`
- Teammate/Gemini-derived complete paper: `Finalized_Complete_Paper_WASD_updated.docx`
  - SHA-256: `D1973E367C391AD0A2752804FFD1743CE0B42B4009B0D7C0B57AFECE429F686A`
- Authoritative Chapter IV: `thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md`
- Reconciled Chapter V: `thesis_docs/CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md`

The verified current paper and frozen experiment artifacts controlled every
methodology and result decision. The teammate document was treated as a source
of complete-paper organization and possible later-chapter material, not as a
replacement for the adviser-approved endpoint or final protocol.

## Retained from the teammate contribution

- The useful complete-paper structure extending the manuscript through
  Chapters IV and V.
- The Chapter V organization into summary, conclusions, and recommendations.
- Defensible recommendation topics: external validation, platform adaptation,
  multi-party extension, and human-review integration.
- The idea of presenting final metrics, paired differences, and
  validation-versus-test behavior in reader-facing tables.

## Rejected or corrected

- Chapters I-III from the teammate copy were not imported because they reverted
  to general grooming-detection, message-level, early-detection, and deployment
  claims that exceed the author-derived PAN12 conversation endpoint.
- The final-test turn count was corrected from 22,798 to 22,929, and the
  excluded historical-test group was restored for complete partition
  accounting.
- Obsolete feature names such as `score_ewma`, `delta`, `risk_spike`, and
  `risk_drop` were replaced by the seven features actually used in the frozen
  primary model.
- Statements that all false negatives had fewer than six turns and that false
  positives had specific benign/adversarial meanings were rejected. The
  reconciled error analysis uses the observed turn counts and keeps the
  author-derived label limitation explicit.
- Claims of computed p-values, statistical equivalence, more than 99% parameter
  reduction, 100-times-faster execution, sub-millisecond latency, and more than
  95% alert elimination were removed because the frozen artifacts do not
  support them.
- Claims of proven live-platform suitability, moderator effectiveness,
  autonomous safety, or real-world harm prevention were removed. These remain
  future evaluation requirements.

## Output

The initial clean reconciliation candidate was
`Finalized Complete Paper WASD - reconciled.docx`, SHA-256
`02ED4BD332F452B2371E8516BB7648947F907183940983436A7D8309AB337BD3`.

Structural validation confirmed:

- the cover, author table, Chapters I-III, and References match their protected
  fingerprints from the verified current DOCX;
- 6 Heading 1, 26 Heading 2, and 20 Heading 3 paragraphs;
- five direct chapter page breaks and 13 preserved hyperlinks;
- no comments, tracked insertions/deletions, fields, or automatic numbering;
- explicit geometry checks passed for all seven new results tables; and
- no frozen stale-claim pattern remained.

At the user's direction, render-based visual QA was stopped. The user will
inspect and, if needed, adjust minor Word formatting directly. This output is
therefore structurally and substantively reconciled but not claimed to have
passed a final rendered-page visual review.

No model was retrained or retuned, and no final-test data was rescored.

## Post-reconciliation framing correction

After reviewing the initial reconciliation, the user confirmed that the
adviser-locked objectives must remain unchanged and directed that the study not
be minimized around the narrowest implementation-specific endpoint. The exact
objective block from commit `c597cb8` was restored. The title, research
questions, background, scope, significance, definitions, related studies, and
theoretical background were then revised to restore the study's full
AI-moderation, contextual-analysis, behavioral-trajectory, and OGDM-informed
contribution.

This was not a wholesale import of the teammate/Gemini Chapters I-III.
Corrections required by the completed experiment remain in force: PAN12
author-list supervision is not message-level grooming ground truth; synthetic
and other unreviewed candidate datasets are excluded from the primary
experiment; grooming stage and onset were not validated; no language filter,
live deployment, moderator outcome, or real-world harm-prevention result is
claimed; and the trajectory features are theoretically informed indicators,
not independently validated OGDM-stage measurements.

The current files are:

- `Finals Revised Paper WASD.docx`
  - SHA-256: `D920524D78C871F7E503675C423C6F82573C3BE5E53D7587E7D4005BF11D9FE3`
- `Finalized Complete Paper WASD - reconciled.docx`
  - SHA-256: `8768C86EE698D945531784783D95E41FA29BC31CB7A13C2800441569318148A9`
- Structural receipt:
  `thesis_docs/.docx_reconciliation_qa/balanced_framing_receipt.json`

The synchronized Word pass confirmed unchanged non-title cover text, unchanged
Chapter III onward, unchanged tables, preserved heading counts, three/five
chapter breaks, and 13 hyperlinks. No rendering was performed at the user's
explicit request. No model was retrained or retuned, and no final-test data was
rescored.

## Confident-claims pass (2026-09-02)

The authoritative manuscript received a focused voice revision so the completed
two-layer module, working review interface, trajectory-LSTM performance,
false-negative reductions, and matched recurrent-aggregation result are stated
directly and confidently. The revision removed apologetic repetition from the
significance, results interpretation, practical implications, conclusions, and
recommendations while preserving the substantive PAN12 label boundary in the
scope, methodology, ethical considerations, and error-analysis sections.

The pass did not alter the title, adviser-locked objectives, research questions,
methods, model artifacts, thresholds, tables, metrics, confidence intervals, or
experimental records. The updated Chapters I-III DOCX has SHA-256
`F41F2ACA02CE053DD649AE1C9940B66665667B63F2A8B21A1F2F55F3378EC55C`; the
updated complete DOCX has SHA-256
`72D23405C1FCB2882DFEAA4915C045F0298C4209D8914D7F0B1E4FAE0F1B6FD3`.
Structural and textual QA passed. Rendering was intentionally skipped at the
user's request.

## Objective-aligned conclusions (2026-09-02)

Section 5.2 was reorganized to answer the unchanged research objectives
directly. Conclusions 1-3 now correspond to Specific Objectives 1-3, and the
fourth conclusion explicitly states that the General Objective was achieved.
The quantitative conclusion records recall and false-negative reductions
against the tested keyword, maximum Layer 1, and weighted approaches, while
describing report-driven moderation as a complementary workflow rather than an
unperformed quantitative baseline.

The conclusion does not repeat the detailed PAN12 label-boundary discussion
already contained in the scope, methodology, ethics, and error-analysis
sections. No research question, objective, method, model artifact, threshold,
table, metric, confidence interval, or experimental record changed. The updated
complete DOCX has SHA-256
`B4C4BB0069C408185A1C18D234C03CDC0D4039B762BACAC568BE3F37CD135E1D`.
Structural and textual QA passed. Rendering was intentionally skipped at the
user's request.

## Markdown-first full framing review (2026-09-02)

A complete semantic review of the authoritative Chapters I-V Markdown established a consistent research-first, dataset-second narrative. The manuscript first presents the moderation problem, the two-layer contextual and behavioral trajectory architecture, and the comparison requirements. PAN-2012 is then identified as the dataset selected because its scale, chronology, persistent speaker identifiers, and official author list support the required sequence construction and author-disjoint evaluation.

Repeated dataset-specific caveats were removed from the background, significance, general results interpretation, chapter summary, and conclusion. The factual label boundary remains in the dedicated Scope and Limitations, Corpus and Label Provenance, evaluation interpretation, and error-analysis passages where omitting it would misstate what the experiment measures. The title, four research questions, General Objective, three Specific Objectives, methods, Chapter IV tables, model artifacts, thresholds, metrics, confidence intervals, and frozen results were not changed.

This review is Markdown-only pending user approval. It was not synchronized into either Word document, no document rendering was performed, and no model training, tuning, or final-test rescoring occurred. The complete DOCX was restored to its pre-objective-alignment content at SHA-256 `8D50D502A87542651EB59D12312B0852AD2414CC25ADE03D2A15E899BFCB686A`.
## Approved Markdown-to-DOCX synchronization (2026-09-02)

After the user approved the full Markdown framing review, the authoritative Chapters I-III Markdown was synchronized into `Finals Revised Paper WASD.docx` and the authoritative Chapters IV-V Markdown was inserted into `Finalized Complete Paper WASD - reconciled.docx`. The resulting hashes are `481A95449DD144EC07ADA0DD6E6B90100972BBE287645AE7501DC5606FB582D2` and `C204E31B375F9F833BA6252BF334C9121CB50BFD69E69CCD104F13E27CA89661`, respectively.

Verification confirmed the research-first, dataset-second framing; the exact original title, research questions, and adviser-locked objectives; the objective-aligned Chapter V conclusions; unchanged Chapter IV table geometry and reported metrics; preserved cover, author table, references, hyperlinks, and chapter breaks; and the absence of comments, tracked changes, or fields. No model training, tuning, or final-test rescoring occurred. At the user's standing direction, no render-based QA was performed.
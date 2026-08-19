# Thesis DOCX conversion contract

- Reference: `C:\Projects\THESIS\Finals_Revised_Paper_WASD.docx`
- Reference SHA-256: `3AE8786F8918E2B60AF51EDEFAA5A4007EADF07AD08E1B8B672CD991D22FFFC5`
- Source: `C:\Projects\THESIS\thesis_docs\Finals_Revised_Paper_WASD.md`
- Output: `C:\Projects\THESIS\Finals_Revised_Paper_WASD_from_markdown.docx`

## Preserved page system

- One portrait Letter section with 1-inch margins.
- Existing headers, footers, styles, numbering definitions, and document theme
  are retained by copying the reference package before body replacement.

## Content mapping

- Cover: recreate the title, institution, course, and author block using the
  retained cover paragraph patterns; source Markdown controls text.
- Chapters and subsections: use retained Heading 1, Heading 2, and Heading 3
  paragraph patterns.
- Body: use retained Normal pattern with 0.5-inch first-line indentation and
  1.15 line spacing.
- Captions: centered italic retained Normal pattern.
- Tables: reproduce the reference's bordered, centered header treatment and
  explicit column widths, with widths selected to fit the source table fields.
- References: retain body-style text while preserving Markdown link targets as
  ordinary visible text where a native hyperlink cannot be safely reconstructed.

## Fidelity checks

- The reference DOCX remains unchanged.
- Source heading order and the three Markdown tables must appear in the output.
- Output must retain Letter portrait geometry, one-inch margins, title page,
  heading hierarchy, tables, and reference section.
- Render through Word to PDF and inspect page images because LibreOffice is not
  installed in this environment.

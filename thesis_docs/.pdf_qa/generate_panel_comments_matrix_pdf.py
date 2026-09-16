from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "thesis_docs" / "PANEL_COMMENTS_MATRIX.md"
OUTPUT = ROOT / "output" / "pdf" / "WASD_Final_Panel_Comments_Matrix.pdf"

NAVY = colors.HexColor("#18324A")
BLUE = colors.HexColor("#2F6F9F")
PALE_BLUE = colors.HexColor("#EAF3F8")
PALE_GREEN = colors.HexColor("#EAF5EE")
PALE_AMBER = colors.HexColor("#FFF4D6")
GRID = colors.HexColor("#B8C4CE")
TEXT = colors.HexColor("#17212B")
MUTED = colors.HexColor("#53616E")


def register_fonts() -> tuple[str, str]:
    regular_candidates = [
        Path(r"C:\Windows\Fonts\aptos.ttf"),
        Path(r"C:\Windows\Fonts\calibri.ttf"),
        Path(r"C:\Windows\Fonts\arial.ttf"),
    ]
    bold_candidates = [
        Path(r"C:\Windows\Fonts\aptosbd.ttf"),
        Path(r"C:\Windows\Fonts\calibrib.ttf"),
        Path(r"C:\Windows\Fonts\arialbd.ttf"),
    ]
    regular = next((p for p in regular_candidates if p.exists()), None)
    bold = next((p for p in bold_candidates if p.exists()), None)
    if regular and bold:
        pdfmetrics.registerFont(TTFont("MatrixRegular", str(regular)))
        pdfmetrics.registerFont(TTFont("MatrixBold", str(bold)))
        return "MatrixRegular", "MatrixBold"
    return "Helvetica", "Helvetica-Bold"


REGULAR_FONT, BOLD_FONT = register_fonts()


def ascii_normalize(text: str) -> str:
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2011": "-",
        "\u00a0": " ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def inline_markup(text: str) -> str:
    text = ascii_normalize(text.strip())
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r"<font name='Courier'>\1</font>", text)
    return text


def parse_source() -> tuple[list[list[str]], list[str], str]:
    raw = SOURCE.read_text(encoding="utf-8")
    rows: list[list[str]] = []
    for line in raw.splitlines():
        if re.match(r"^\|\s*\d+\s*\|", line):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) != 6:
                raise ValueError(f"Expected 6 cells, got {len(cells)}: {line}")
            rows.append(cells)
    if [int(row[0]) for row in rows] != list(range(1, 16)):
        raise ValueError("Expected exactly 15 sequential comment rows")

    status_match = re.search(
        r"## Consolidated Status\s+(.*?)(?=\n## Core Defense Statement)",
        raw,
        flags=re.S,
    )
    if not status_match:
        raise ValueError("Consolidated Status section not found")
    status_items = [
        re.sub(r"^-\s*", "", line).strip()
        for line in status_match.group(1).splitlines()
        if line.strip().startswith("-")
    ]

    defense_match = re.search(r"## Core Defense Statement\s+(.*)\s*$", raw, flags=re.S)
    if not defense_match:
        raise ValueError("Core Defense Statement section not found")
    defense = " ".join(line.strip() for line in defense_match.group(1).splitlines() if line.strip())
    return rows, status_items, defense


class NumberedDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str, **kwargs):
        super().__init__(filename, **kwargs)
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id="content",
            leftPadding=0,
            rightPadding=0,
            topPadding=8 * mm,
            bottomPadding=7 * mm,
        )
        self.addPageTemplates(PageTemplate(id="matrix", frames=frame, onPage=self.draw_page))

    def draw_page(self, canvas, doc):
        width, height = landscape(A4)
        canvas.saveState()
        canvas.setFillColor(NAVY)
        canvas.rect(0, height - 13 * mm, width, 13 * mm, fill=1, stroke=0)
        canvas.setFont(BOLD_FONT, 8.5)
        canvas.setFillColor(colors.white)
        canvas.drawString(14 * mm, height - 8.5 * mm, "WASD Thesis - Final-Panel Comments Matrix")
        canvas.setStrokeColor(GRID)
        canvas.line(14 * mm, 11 * mm, width - 14 * mm, 11 * mm)
        canvas.setFillColor(MUTED)
        canvas.setFont(REGULAR_FONT, 7.5)
        canvas.drawString(14 * mm, 6.5 * mm, "Prepared September 15, 2026 | Authoritative Markdown response record")
        canvas.drawRightString(width - 14 * mm, 6.5 * mm, f"Page {doc.page}")
        canvas.restoreState()


def build_pdf() -> None:
    rows, status_items, defense = parse_source()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontName=BOLD_FONT,
        fontSize=20,
        leading=23,
        textColor=NAVY,
        alignment=TA_LEFT,
        spaceAfter=4 * mm,
    )
    intro_style = ParagraphStyle(
        "Intro",
        parent=styles["BodyText"],
        fontName=REGULAR_FONT,
        fontSize=9,
        leading=12,
        textColor=TEXT,
        spaceAfter=2.5 * mm,
    )
    cell_style = ParagraphStyle(
        "Cell",
        parent=styles["BodyText"],
        fontName=REGULAR_FONT,
        fontSize=7.2,
        leading=8.6,
        textColor=TEXT,
        alignment=TA_LEFT,
        allowWidows=0,
        allowOrphans=0,
    )
    number_style = ParagraphStyle(
        "Number",
        parent=cell_style,
        fontName=BOLD_FONT,
        fontSize=8,
        alignment=TA_CENTER,
    )
    header_style = ParagraphStyle(
        "Header",
        parent=cell_style,
        fontName=BOLD_FONT,
        fontSize=7.3,
        leading=8.5,
        textColor=colors.white,
        alignment=TA_CENTER,
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontName=BOLD_FONT,
        fontSize=13,
        leading=15,
        textColor=NAVY,
        spaceBefore=4 * mm,
        spaceAfter=2.5 * mm,
    )
    bullet_style = ParagraphStyle(
        "Bullet",
        parent=intro_style,
        leftIndent=5 * mm,
        firstLineIndent=-3 * mm,
        bulletIndent=0,
        spaceAfter=1.5 * mm,
    )
    defense_style = ParagraphStyle(
        "Defense",
        parent=intro_style,
        fontSize=10,
        leading=14,
        borderColor=BLUE,
        borderWidth=1,
        borderPadding=9,
        backColor=PALE_BLUE,
        spaceBefore=1.5 * mm,
    )

    doc = NumberedDocTemplate(
        str(OUTPUT),
        pagesize=landscape(A4),
        leftMargin=9 * mm,
        rightMargin=9 * mm,
        topMargin=14 * mm,
        bottomMargin=12 * mm,
        title="WASD Final-Panel Comments Matrix",
        author="WASD Thesis Group",
        subject="Panel comments, actions, evidence locations, and remaining work",
    )

    story = [
        Paragraph("Final-Panel Comments Matrix", title_style),
        Paragraph(
            "One row is retained for each of the 15 reported panel comments and emphasis notes. "
            "The matrix separates manuscript corrections already completed from empirical work "
            "that still requires new data, annotation, or operational testing.",
            intro_style,
        ),
        Paragraph(
            "<b>Status:</b> Addressed = present in the authoritative Markdown. "
            "Addressed; validation pending = wording is corrected, but the requested empirical "
            "extension remains future work. Priority defense point = written correction is complete "
            "and should be emphasized during questioning.",
            intro_style,
        ),
        Spacer(1, 2 * mm),
    ]

    headers = [
        "No.",
        "Panel comment",
        "Required interpretation",
        "Action taken / evidence",
        "Manuscript location",
        "Status and remaining work",
    ]
    table_data = [[Paragraph(h, header_style) for h in headers]]
    for row in rows:
        table_data.append(
            [
                Paragraph(inline_markup(row[0]), number_style),
                Paragraph(inline_markup(row[1]), cell_style),
                Paragraph(inline_markup(row[2]), cell_style),
                Paragraph(inline_markup(row[3]), cell_style),
                Paragraph(inline_markup(row[4]), cell_style),
                Paragraph(inline_markup(row[5]), cell_style),
            ]
        )

    table = Table(
        table_data,
        colWidths=[9 * mm, 48 * mm, 45 * mm, 74 * mm, 39 * mm, 64 * mm],
        repeatRows=1,
        splitByRow=1,
        hAlign="LEFT",
    )
    style_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.35, GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
    ]
    for index, row in enumerate(rows, start=1):
        if index % 2 == 0:
            style_commands.append(("BACKGROUND", (0, index), (-2, index), colors.HexColor("#F5F8FA")))
        status_text = row[5]
        if "validation pending" in status_text.lower():
            status_color = PALE_AMBER
        elif "priority defense point" in status_text.lower():
            status_color = PALE_BLUE
        else:
            status_color = PALE_GREEN
        style_commands.append(("BACKGROUND", (-1, index), (-1, index), status_color))
    table.setStyle(TableStyle(style_commands))
    story.append(table)

    story.extend([PageBreak(), Paragraph("Consolidated Status", section_style)])
    for item in status_items:
        story.append(Paragraph(inline_markup(item), bullet_style, bulletText="-"))
    story.extend(
        [
            Spacer(1, 3 * mm),
            Paragraph("Core Defense Statement", section_style),
            Paragraph(inline_markup(defense), defense_style),
        ]
    )

    doc.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    build_pdf()

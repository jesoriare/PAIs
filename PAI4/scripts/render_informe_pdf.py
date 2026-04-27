from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "Informe-PAI4.md"
OUTPUT = ROOT / "Informe-PAI4.pdf"


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TitleCenter",
            parent=styles["Title"],
            alignment=TA_CENTER,
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyTight",
            parent=styles["BodyText"],
            leading=14,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BulletTight",
            parent=styles["BodyText"],
            leading=14,
            leftIndent=14,
            firstLineIndent=-8,
            spaceAfter=4,
        )
    )
    return styles


def flush_paragraph(buffer, story, styles):
    if not buffer:
        return
    text = " ".join(part.strip() for part in buffer if part.strip()).strip()
    if text:
        story.append(Paragraph(text, styles["BodyTight"]))
    buffer.clear()


def flush_table(table_lines, story):
    if not table_lines:
        return

    rows = []
    for line in table_lines:
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if all(set(cell) <= {"-", " "} for cell in cells):
            continue
        rows.append(cells)

    if not rows:
        table_lines.clear()
        return

    table = Table(rows, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d9e2f3")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("PADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 0.2 * cm))
    table_lines.clear()


def markdown_to_story(source_text: str):
    styles = build_styles()
    story = []
    paragraph_buffer = []
    table_lines = []
    in_code = False
    code_lines = []

    for raw_line in source_text.splitlines():
        line = raw_line.rstrip()

        if line.startswith("```"):
            flush_paragraph(paragraph_buffer, story, styles)
            flush_table(table_lines, story)
            if in_code:
                story.append(Preformatted("\n".join(code_lines), styles["Code"]))
                story.append(Spacer(1, 0.15 * cm))
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        if line.startswith("|"):
            flush_paragraph(paragraph_buffer, story, styles)
            table_lines.append(line)
            continue
        else:
            flush_table(table_lines, story)

        if not line.strip():
            flush_paragraph(paragraph_buffer, story, styles)
            story.append(Spacer(1, 0.12 * cm))
            continue

        if line.startswith("# "):
            flush_paragraph(paragraph_buffer, story, styles)
            story.append(Paragraph(line[2:].strip(), styles["TitleCenter"]))
            continue

        if line.startswith("## "):
            flush_paragraph(paragraph_buffer, story, styles)
            story.append(Paragraph(line[3:].strip(), styles["Heading1"]))
            continue

        if line.startswith("### "):
            flush_paragraph(paragraph_buffer, story, styles)
            story.append(Paragraph(line[4:].strip(), styles["Heading2"]))
            continue

        if line.startswith("#### "):
            flush_paragraph(paragraph_buffer, story, styles)
            story.append(Paragraph(line[5:].strip(), styles["Heading3"]))
            continue

        if line.startswith("- "):
            flush_paragraph(paragraph_buffer, story, styles)
            story.append(Paragraph(f"- {line[2:].strip()}", styles["BulletTight"]))
            continue

        paragraph_buffer.append(line)

    flush_paragraph(paragraph_buffer, story, styles)
    flush_table(table_lines, story)
    if code_lines:
        story.append(Preformatted("\n".join(code_lines), styles["Code"]))

    return story


def main() -> None:
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        topMargin=1.8 * cm,
        bottomMargin=1.6 * cm,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        title="Informe PAI-4",
        author="Codex",
    )
    source_text = SOURCE.read_text(encoding="utf-8")
    story = markdown_to_story(source_text)
    doc.build(story)
    print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    main()

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
from typing import List, Tuple


def build_antenna_report(
    output_pdf: str,
    antname: str = "Default",
    minima_rows: List[List[str]] = None,
    title: str = "Antenna Test Report",
    subtitle: str = "Automatically generated",
    author: str = "",
    notes: str = "",
    design_freq_ghz = None,
    assets: List[Tuple[str, Path]] = None,
    verbose: bool = False,
):
    """Build PDF report for antenna measurement"""
    output_pdf = Path(output_pdf)
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    output_pdf = str(output_pdf)

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title=title,
        author=author,
    )

    story = []
    max_width = doc.width
    max_height = 8.5 * inch

    # Title
    logo_path = Path("./Title_Page/MRILogo.png")
    if logo_path.exists():
        im = Image(str(logo_path))
        im._restrictSize(max_width * 0.25, max_height * 0.25)
        story.append(im)

    cleanantname = antname.replace("_", " ")
    story.append(Paragraph(f"<b>{cleanantname} {title}</b>", styles["Title"]))
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph(subtitle, styles["Heading2"]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))

    if design_freq_ghz is not None:
        story.append(Paragraph(f"Designed Frequency: <b>{design_freq_ghz} GHz</b>", styles["Normal"]))

    if author:
        story.append(Paragraph(f"Author: {author}", styles["Normal"]))

    if notes:
        story.append(Spacer(1, 0.15 * inch))
        story.append(Paragraph(f"<b>Notes:</b> {notes}", styles["Normal"]))

    story.append(PageBreak())

    # Minima table
    story.append(Paragraph("<b>First 4 S11 Minima</b>", styles["Heading1"]))
    story.append(Spacer(1, 0.15 * inch))
    if minima_rows and len(minima_rows) > 1:
        t = Table(minima_rows, colWidths=[1.2 * inch, 2.1 * inch, 2.1 * inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#222222")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(t)
    else:
        story.append(Paragraph("No minima found / provided.", styles["Normal"]))

    story.append(PageBreak())

    # Figures
    story.append(Paragraph("<b>Figures</b>", styles["Heading1"]))
    story.append(Spacer(1, 0.15 * inch))
    if not assets:
        story.append(Paragraph("No figures found for this antenna name.", styles["Normal"]))
    else:
        for i, (caption, img_path) in enumerate(assets):
            story.append(Paragraph(f"<b>{caption}</b>", styles["Heading3"]))
            story.append(Spacer(1, 0.15 * inch))
            im = Image(str(img_path))
            im._restrictSize(max_width, max_height)
            story.append(im)
            if i < len(assets) - 1:
                story.append(PageBreak())

    doc.build(story)

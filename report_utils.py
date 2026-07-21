"""
report_utils.py
---------------
PDF report generation for the Smart Attendance System.
Uses only the built-in `reportlab` library (pip install reportlab).
"""

import io
from datetime import date

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph,
        Spacer, HRFlowable
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def generate_pdf(df, title="Attendance Report", subtitle=""):
    """
    Generate a styled PDF from a pandas DataFrame.

    Parameters
    ----------
    df       : pandas.DataFrame — the attendance data to render
    title    : str — main heading of the report
    subtitle : str — secondary heading (e.g. subject / date range)

    Returns
    -------
    bytes — raw PDF bytes ready for st.download_button
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError(
            "reportlab is not installed. Run: pip install reportlab"
        )

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    # ── Colour palette (matches the dark UI feel in a light PDF) ──
    HEADER_BG   = colors.HexColor("#1f6feb")
    HEADER_FG   = colors.white
    ROW_ALT     = colors.HexColor("#f0f4ff")
    ROW_NORMAL  = colors.white
    ACCENT      = colors.HexColor("#1f6feb")
    TEXT_DARK   = colors.HexColor("#0d1117")
    LATE_COLOR  = colors.HexColor("#b45309")
    GRID_COLOR  = colors.HexColor("#d0d7de")

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=20,
        textColor=ACCENT,
        spaceAfter=4,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#57606a"),
        spaceAfter=2,
        alignment=TA_CENTER,
        fontName="Helvetica",
    )
    meta_style = ParagraphStyle(
        "Meta",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.HexColor("#8b949e"),
        spaceAfter=0,
        alignment=TA_CENTER,
        fontName="Helvetica",
    )

    story = []

    # ── Header section ─────────────────────────────────────────────
    story.append(Paragraph("🎓 Smart Attendance System", title_style))
    story.append(Paragraph(title, subtitle_style))
    if subtitle:
        story.append(Paragraph(subtitle, meta_style))
    story.append(Paragraph(
        f"Generated on {date.today().strftime('%A, %d %B %Y')}  ·  Total records: {len(df)}",
        meta_style
    ))
    story.append(Spacer(1, 0.3 * cm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT))
    story.append(Spacer(1, 0.4 * cm))

    # ── Summary stats row ──────────────────────────────────────────
    on_time = len(df[df["Is Late"] == "No"]) if "Is Late" in df.columns else "—"
    late    = len(df[df["Is Late"] == "Yes"]) if "Is Late" in df.columns else "—"

    summary_data = [
        ["Total Records", "On Time", "Late Arrivals", "Report Period"],
        [
            str(len(df)),
            str(on_time),
            str(late),
            subtitle.replace("Subject: ", "") if subtitle else "All",
        ],
    ]
    summary_table = Table(summary_data, colWidths=[6 * cm] * 4)
    summary_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), colors.HexColor("#f6f8fa")),
        ("TEXTCOLOR",    (0, 0), (-1, 0), colors.HexColor("#57606a")),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica"),
        ("FONTSIZE",     (0, 0), (-1, 0), 8),
        ("FONTNAME",     (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 1), (-1, 1), 14),
        ("TEXTCOLOR",    (0, 1), (-1, 1), ACCENT),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#f6f8fa"), colors.white]),
        ("BOX",          (0, 0), (-1, -1), 0.5, GRID_COLOR),
        ("INNERGRID",    (0, 0), (-1, -1), 0.5, GRID_COLOR),
        ("TOPPADDING",   (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── Main data table ────────────────────────────────────────────
    col_order = [c for c in [
        "Student ID", "Name", "Date", "Time",
        "Subject", "Status", "Is Late", "Confidence"
    ] if c in df.columns]

    # Header row
    table_data = [col_order]

    # Data rows
    for _, row in df.iterrows():
        table_data.append([str(row.get(c, "—")) for c in col_order])

    # Dynamic column widths
    n_cols = len(col_order)
    total_width = 26 * cm
    col_widths_map = {
        "Student ID":  3.0 * cm,
        "Name":        5.0 * cm,
        "Date":        3.2 * cm,
        "Time":        2.8 * cm,
        "Subject":     4.5 * cm,
        "Status":      3.0 * cm,
        "Is Late":     2.5 * cm,
        "Confidence":  3.0 * cm,
    }
    col_widths = [col_widths_map.get(c, total_width / n_cols) for c in col_order]

    data_table = Table(table_data, colWidths=col_widths, repeatRows=1)

    # Build row-level styling (colour late rows)
    ts = [
        # Header
        ("BACKGROUND",    (0, 0), (-1, 0), HEADER_BG),
        ("TEXTCOLOR",     (0, 0), (-1, 0), HEADER_FG),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 9),
        ("ALIGN",         (0, 0), (-1, 0), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        # Grid
        ("BOX",           (0, 0), (-1, -1), 0.5, GRID_COLOR),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, GRID_COLOR),
        # Data rows
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 8),
        ("TEXTCOLOR",     (0, 1), (-1, -1), TEXT_DARK),
    ]

    # Alternating row colours + highlight late rows
    is_late_col = col_order.index("Is Late") if "Is Late" in col_order else None
    for i, row in enumerate(table_data[1:], start=1):
        bg = ROW_ALT if i % 2 == 0 else ROW_NORMAL
        ts.append(("BACKGROUND", (0, i), (-1, i), bg))
        if is_late_col is not None and row[is_late_col] == "Yes":
            ts.append(("TEXTCOLOR", (is_late_col, i), (is_late_col, i), LATE_COLOR))
            ts.append(("FONTNAME",  (is_late_col, i), (is_late_col, i), "Helvetica-Bold"))

    data_table.setStyle(TableStyle(ts))
    story.append(data_table)

    # ── Footer note ────────────────────────────────────────────────
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRID_COLOR))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "This report was auto-generated by Smart Attendance System · Confidential",
        meta_style
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

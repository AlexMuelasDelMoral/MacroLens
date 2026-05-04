"""Generate professional PDF reports for MacroLens.

ReportLab is imported lazily inside each public function so it does not
contribute to cold-start time on pages that never generate a PDF.
"""
from __future__ import annotations

from datetime import datetime
from io import BytesIO

_BRAND_PRIMARY   = "#00D4FF"
_BRAND_SECONDARY = "#7C3AED"
_BRAND_DARK      = "#0A0E27"
_BRAND_TEXT      = "#1a1a2e"
_BRAND_MUTED     = "#6b7280"
_POSITIVE        = "#10b981"
_NEGATIVE        = "#ef4444"
_GRAY_LIGHT      = "#f9fafb"
_GRAY_BORDER     = "#e5e7eb"
_WHITE           = "#ffffff"


def _get_styles():
    """Build and return custom paragraph styles. Called once per report."""
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import HexColor
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="BrandTitle",
        fontSize=28,
        textColor=HexColor(_BRAND_PRIMARY),
        fontName="Helvetica-Bold",
        spaceAfter=6,
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name="BrandSubtitle",
        fontSize=12,
        textColor=HexColor(_BRAND_MUTED),
        fontName="Helvetica",
        spaceAfter=20,
    ))
    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontSize=16,
        textColor=HexColor(_BRAND_DARK),
        fontName="Helvetica-Bold",
        spaceAfter=12,
        spaceBefore=20,
    ))
    styles.add(ParagraphStyle(
        name="Body",
        fontSize=10,
        textColor=HexColor(_BRAND_TEXT),
        fontName="Helvetica",
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        leading=14,
    ))
    styles.add(ParagraphStyle(
        name="Caption",
        fontSize=8,
        textColor=HexColor(_BRAND_MUTED),
        fontName="Helvetica-Oblique",
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="Footer",
        fontSize=8,
        textColor=HexColor(_BRAND_PRIMARY),
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
    ))
    return styles


def generate_scenario_report(
    user_conditions: dict,
    similar_events: list,
    predictions_by_asset: dict,
    event_category: str = "Custom Scenario",
) -> BytesIO:
    """Generate a professional scenario analysis PDF report."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor, white
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    )

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        rightMargin=0.75 * inch, leftMargin=0.75 * inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
    )
    styles = _get_styles()
    story = []

    story.append(Paragraph("MacroLens", styles["BrandTitle"]))
    story.append(Paragraph("Economic Scenario Analysis Report", styles["BrandSubtitle"]))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M UTC')}",
        styles["Caption"],
    ))
    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph("Executive Summary", styles["SectionHeader"]))
    story.append(Paragraph(
        f"This report analyzes a <b>{event_category}</b> scenario based on the specified "
        f"macro conditions. Using pattern matching against {len(similar_events)} historical "
        "events, we identify precedents and generate probabilistic forecasts across multiple "
        "asset classes and time horizons.",
        styles["Body"],
    ))
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("Input Macro Conditions", styles["SectionHeader"]))
    macro_data = [
        ["Indicator", "Value"],
        ["Inflation Rate",    f"{user_conditions.get('inflation', 'N/A')}%"],
        ["Fed Funds Rate",    f"{user_conditions.get('fed_funds_rate', 'N/A')}%"],
        ["Unemployment Rate", f"{user_conditions.get('unemployment', 'N/A')}%"],
        ["GDP Growth",        f"{user_conditions.get('gdp_growth', 'N/A')}%"],
    ]
    macro_table = Table(macro_data, colWidths=[3 * inch, 2 * inch])
    macro_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), HexColor(_BRAND_PRIMARY)),
        ("TEXTCOLOR",     (0, 0), (-1, 0), white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 11),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("TOPPADDING",    (0, 0), (-1, 0), 10),
        ("BACKGROUND",    (0, 1), (-1, -1), HexColor(_GRAY_LIGHT)),
        ("TEXTCOLOR",     (0, 1), (-1, -1), HexColor(_BRAND_TEXT)),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 10),
        ("ALIGN",         (1, 0), (1, -1), "RIGHT"),
        ("ALIGN",         (0, 0), (0, -1), "LEFT"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [HexColor(_WHITE), HexColor(_GRAY_LIGHT)]),
        ("LINEBELOW",     (0, 0), (-1, 0), 2, HexColor(_BRAND_PRIMARY)),
        ("GRID",          (0, 1), (-1, -1), 0.5, HexColor(_GRAY_BORDER)),
        ("TOPPADDING",    (0, 1), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
    ]))
    story.append(macro_table)
    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph("Historical Precedents", styles["SectionHeader"]))
    story.append(Paragraph(
        "The following historical events show the highest similarity to your scenario:",
        styles["Body"],
    ))
    events_data = [["#", "Historical Event", "Year", "Category", "Similarity"]]
    for i, item in enumerate(similar_events[:5], 1):
        events_data.append([
            str(i),
            item["event"]["name"],
            str(item["event"]["year"]),
            item["event"]["category"],
            f"{item['similarity']}%",
        ])
    events_table = Table(
        events_data,
        colWidths=[0.4 * inch, 2.5 * inch, 0.7 * inch, 1.5 * inch, 0.9 * inch],
    )
    events_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), HexColor(_BRAND_PRIMARY)),
        ("TEXTCOLOR",     (0, 0), (-1, 0), white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING",    (0, 0), (-1, 0), 8),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 9),
        ("ALIGN",         (0, 0), (0, -1), "CENTER"),
        ("ALIGN",         (2, 0), (2, -1), "CENTER"),
        ("ALIGN",         (4, 0), (4, -1), "RIGHT"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [HexColor(_WHITE), HexColor(_GRAY_LIGHT)]),
        ("GRID",          (0, 0), (-1, -1), 0.5, HexColor(_GRAY_BORDER)),
        ("TOPPADDING",    (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
    ]))
    story.append(events_table)
    story.append(Spacer(1, 0.3 * inch))

    story.append(PageBreak())
    story.append(Paragraph("Predicted Asset Class Impacts", styles["SectionHeader"]))

    pred_data = [["Asset Class", "1M", "3M", "6M", "1Y", "2Y"]]
    for asset, predictions in predictions_by_asset.items():
        row = [asset]
        for horizon in ("1m", "3m", "6m", "1y", "2y"):
            val = (
                predictions[horizon]["expected"]
                if predictions.get(horizon) else None
            )
            row.append(f"{val:+.1f}%" if val is not None else "-")
        pred_data.append(row)

    pred_style = [
        ("BACKGROUND",    (0, 0), (-1, 0), HexColor(_BRAND_DARK)),
        ("TEXTCOLOR",     (0, 0), (-1, 0), white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 10),
        ("ALIGN",         (1, 0), (-1, -1), "CENTER"),
        ("ALIGN",         (0, 0), (0, -1), "LEFT"),
        ("FONTNAME",      (0, 1), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 1), (-1, -1), 9),
        ("GRID",          (0, 0), (-1, -1), 0.5, HexColor(_GRAY_BORDER)),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [HexColor(_WHITE), HexColor(_GRAY_LIGHT)]),
    ]
    for row_idx, row in enumerate(pred_data[1:], 1):
        for col_idx, cell in enumerate(row[1:], 1):
            if cell != "-":
                try:
                    val = float(cell.replace("%", "").replace("+", ""))
                    color = _POSITIVE if val > 0 else _NEGATIVE
                    pred_style.append(
                        ("TEXTCOLOR", (col_idx, row_idx), (col_idx, row_idx), HexColor(color))
                    )
                except ValueError:
                    pass

    pred_table = Table(
        pred_data,
        colWidths=[2.2 * inch, 0.85 * inch, 0.85 * inch, 0.85 * inch, 0.85 * inch, 0.85 * inch],
    )
    pred_table.setStyle(TableStyle(pred_style))
    story.append(pred_table)
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        "<i>Values represent expected returns based on similarity-weighted averages of "
        "historical precedents. Actual outcomes may vary significantly.</i>",
        styles["Caption"],
    ))
    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph("Important Disclaimer", styles["SectionHeader"]))
    story.append(Paragraph(
        "<b>This report is for educational and research purposes only.</b> It does not "
        "constitute financial advice, investment recommendation, or solicitation to buy or "
        "sell any securities. Historical patterns may not repeat. Always consult qualified "
        "financial advisors before making investment decisions.",
        styles["Body"],
    ))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph(
        "Generated by MacroLens — Economic Intelligence Platform",
        styles["Footer"],
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_portfolio_report(
    portfolio: dict,
    scenario_name: str,
    results_df,
    total_impact: float,
) -> BytesIO:
    """Generate a portfolio stress test PDF report."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor, white
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    )

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        rightMargin=0.75 * inch, leftMargin=0.75 * inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
    )
    styles = _get_styles()
    story = []

    story.append(Paragraph("MacroLens", styles["BrandTitle"]))
    story.append(Paragraph("Portfolio Stress Test Report", styles["BrandSubtitle"]))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y')}  |  "
        f"Scenario: <b>{scenario_name}</b>",
        styles["Caption"],
    ))
    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph("Portfolio Composition", styles["SectionHeader"]))
    port_data = [["Asset Class", "Allocation"]]
    for asset, weight in portfolio.items():
        if weight > 0:
            port_data.append([asset, f"{weight}%"])

    port_table = Table(port_data, colWidths=[3 * inch, 2 * inch])
    port_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), HexColor(_BRAND_PRIMARY)),
        ("TEXTCOLOR",     (0, 0), (-1, 0), white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN",         (1, 0), (1, -1), "RIGHT"),
        ("GRID",          (0, 0), (-1, -1), 0.5, HexColor(_GRAY_BORDER)),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [HexColor(_WHITE), HexColor(_GRAY_LIGHT)]),
    ]))
    story.append(port_table)
    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph("Projected Portfolio Impact", styles["SectionHeader"]))
    impact_color = _NEGATIVE if total_impact < 0 else _POSITIVE
    story.append(Paragraph(
        f"Under the <b>{scenario_name}</b> scenario, your portfolio is projected to "
        f'<font color="{impact_color}"><b>{total_impact:+.2f}%</b></font> '
        "over the analysis period, based on historical precedent data.",
        styles["Body"],
    ))

    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Disclaimer", styles["SectionHeader"]))
    story.append(Paragraph(
        "<b>Not financial advice.</b> For educational purposes only. "
        "Always consult qualified professionals.",
        styles["Body"],
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer
"""Generate professional PDF reports."""
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


# Brand Colors
BRAND_PRIMARY = HexColor("#00D4FF")
BRAND_SECONDARY = HexColor("#7C3AED")
BRAND_DARK = HexColor("#0A0E27")
BRAND_TEXT = HexColor("#1a1a2e")
BRAND_MUTED = HexColor("#6b7280")
POSITIVE = HexColor("#10b981")
NEGATIVE = HexColor("#ef4444")


def get_custom_styles():
    """Custom paragraph styles."""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='BrandTitle',
        fontSize=28,
        textColor=BRAND_PRIMARY,
        fontName='Helvetica-Bold',
        spaceAfter=6,
        alignment=TA_LEFT
    ))
    
    styles.add(ParagraphStyle(
        name='BrandSubtitle',
        fontSize=12,
        textColor=BRAND_MUTED,
        fontName='Helvetica',
        spaceAfter=20
    ))
    
    styles.add(ParagraphStyle(
        name='SectionHeader',
        fontSize=16,
        textColor=BRAND_DARK,
        fontName='Helvetica-Bold',
        spaceAfter=12,
        spaceBefore=20,
        borderPadding=5,
        leftIndent=0
    ))
    
    styles.add(ParagraphStyle(
        name='Body',
        fontSize=10,
        textColor=BRAND_TEXT,
        fontName='Helvetica',
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        leading=14
    ))
    
    styles.add(ParagraphStyle(
        name='Caption',
        fontSize=8,
        textColor=BRAND_MUTED,
        fontName='Helvetica-Oblique',
        spaceAfter=4
    ))
    
    return styles


def generate_scenario_report(user_conditions, similar_events, predictions_by_asset, 
                               event_category="Custom Scenario"):
    """Generate professional scenario analysis PDF."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    styles = get_custom_styles()
    story = []
    
    # --- HEADER ---
    story.append(Paragraph("⚡ MacroLens", styles['BrandTitle']))
    story.append(Paragraph("Economic Scenario Analysis Report", styles['BrandSubtitle']))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M UTC')}",
        styles['Caption']
    ))
    story.append(Spacer(1, 0.3*inch))
    
    # --- EXECUTIVE SUMMARY ---
    story.append(Paragraph("Executive Summary", styles['SectionHeader']))
    
    summary_text = f"""
    This report analyzes a <b>{event_category}</b> scenario based on the specified macro conditions.
    Using pattern matching against {len(similar_events)} historical events, we identify precedents
    and generate probabilistic forecasts across multiple asset classes and time horizons.
    """
    story.append(Paragraph(summary_text, styles['Body']))
    story.append(Spacer(1, 0.15*inch))
    
    # --- MACRO CONDITIONS TABLE ---
    story.append(Paragraph("Input Macro Conditions", styles['SectionHeader']))
    
    macro_data = [
        ["Indicator", "Value"],
        ["Inflation Rate", f"{user_conditions.get('inflation', 'N/A')}%"],
        ["Fed Funds Rate", f"{user_conditions.get('fed_funds_rate', 'N/A')}%"],
        ["Unemployment Rate", f"{user_conditions.get('unemployment', 'N/A')}%"],
        ["GDP Growth", f"{user_conditions.get('gdp_growth', 'N/A')}%"],
    ]
    
    macro_table = Table(macro_data, colWidths=[3*inch, 2*inch])
    macro_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor("#f9fafb")),
        ('TEXTCOLOR', (0, 1), (-1, -1), BRAND_TEXT),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor("#ffffff"), HexColor("#f9fafb")]),
        ('LINEBELOW', (0, 0), (-1, 0), 2, BRAND_PRIMARY),
        ('GRID', (0, 1), (-1, -1), 0.5, HexColor("#e5e7eb")),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    story.append(macro_table)
    story.append(Spacer(1, 0.3*inch))
    
    # --- SIMILAR EVENTS ---
    story.append(Paragraph("Historical Precedents", styles['SectionHeader']))
    story.append(Paragraph(
        "The following historical events show the highest similarity to your scenario:",
        styles['Body']
    ))
    
    events_data = [["#", "Historical Event", "Year", "Category", "Similarity"]]
    for i, item in enumerate(similar_events[:5], 1):
        events_data.append([
            str(i),
            item["event"]["name"],
            str(item["event"]["year"]),
            item["event"]["category"],
            f"{item['similarity']}%"
        ])
    
    events_table = Table(events_data, colWidths=[0.4*inch, 2.5*inch, 0.7*inch, 1.5*inch, 0.9*inch])
    events_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor("#ffffff"), HexColor("#f9fafb")]),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#e5e7eb")),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    story.append(events_table)
    story.append(Spacer(1, 0.3*inch))
    
    # --- PREDICTIONS TABLE ---
    story.append(PageBreak())
    story.append(Paragraph("Predicted Asset Class Impacts", styles['SectionHeader']))
    
    pred_header = ["Asset Class", "1M", "3M", "6M", "1Y", "2Y"]
    pred_data = [pred_header]
    
    for asset, predictions in predictions_by_asset.items():
        row = [asset]
        for horizon in ["1m", "3m", "6m", "1y", "2y"]:
            val = predictions.get(horizon, {}).get("expected") if predictions.get(horizon) else None
            if val is not None:
                row.append(f"{val:+.1f}%")
            else:
                row.append("—")
        pred_data.append(row)
    
    pred_table = Table(pred_data, colWidths=[2.2*inch, 0.85*inch, 0.85*inch, 0.85*inch, 0.85*inch, 0.85*inch])
    
    # Build dynamic styling for cell colors
    pred_style = [
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#e5e7eb")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor("#ffffff"), HexColor("#f9fafb")]),
    ]
    
    # Color code cells based on value
    for row_idx, row in enumerate(pred_data[1:], 1):
        for col_idx, cell in enumerate(row[1:], 1):
            if cell != "—":
                try:
                    val = float(cell.replace('%', '').replace('+', ''))
                    if val > 0:
                        pred_style.append(('TEXTCOLOR', (col_idx, row_idx), (col_idx, row_idx), POSITIVE))
                    elif val < 0:
                        pred_style.append(('TEXTCOLOR', (col_idx, row_idx), (col_idx, row_idx), NEGATIVE))
                except:
                    pass
    
    pred_table.setStyle(TableStyle(pred_style))
    story.append(pred_table)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph(
        "<i>Values represent expected returns based on similarity-weighted averages of historical precedents. "
        "Actual outcomes may vary significantly.</i>",
        styles['Caption']
    ))
    
    story.append(Spacer(1, 0.3*inch))
    
    # --- DISCLAIMER ---
    story.append(Paragraph("Important Disclaimer", styles['SectionHeader']))
    disclaimer = """
    <b>This report is for educational and research purposes only.</b> It does not constitute 
    financial advice, investment recommendation, or solicitation to buy or sell any securities. 
    Historical patterns may not repeat, and past performance does not guarantee future results. 
    Markets are subject to black swan events and regime changes that cannot be captured by 
    historical analysis. Always consult with qualified financial advisors before making 
    investment decisions. The authors and MacroLens assume no responsibility for any financial 
    decisions made based on this analysis.
    """
    story.append(Paragraph(disclaimer, styles['Body']))
    
    # Footer
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(
        "Generated by MacroLens • Economic Intelligence Platform",
        ParagraphStyle(
            name='Footer',
            fontSize=8,
            textColor=BRAND_PRIMARY,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )
    ))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_portfolio_report(portfolio, scenario_name, results_df, total_impact):
    """Generate portfolio stress test PDF report."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        rightMargin=0.75*inch, leftMargin=0.75*inch,
        topMargin=0.75*inch, bottomMargin=0.75*inch
    )
    
    styles = get_custom_styles()
    story = []
    
    # Header
    story.append(Paragraph("⚡ MacroLens", styles['BrandTitle']))
    story.append(Paragraph("Portfolio Stress Test Report", styles['BrandSubtitle']))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y')}  |  Scenario: <b>{scenario_name}</b>",
        styles['Caption']
    ))
    story.append(Spacer(1, 0.3*inch))
    
    # Portfolio Composition
    story.append(Paragraph("Portfolio Composition", styles['SectionHeader']))
    
    port_data = [["Asset Class", "Allocation"]]
    for asset, weight in portfolio.items():
        if weight > 0:
            port_data.append([asset, f"{weight}%"])
    
    port_table = Table(port_data, colWidths=[3*inch, 2*inch])
    port_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#e5e7eb")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor("#ffffff"), HexColor("#f9fafb")]),
    ]))
    story.append(port_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Expected Impact
    story.append(Paragraph("Projected Portfolio Impact", styles['SectionHeader']))
    
    impact_color = NEGATIVE if total_impact < 0 else POSITIVE
    impact_text = f"""
    Under the <b>{scenario_name}</b> scenario, your portfolio is projected to 
    <font color="{impact_color.hexval()}"><b>{total_impact:+.2f}%</b></font> 
    over the analysis period, based on historical precedent data.
    """
    story.append(Paragraph(impact_text, styles['Body']))
    
    # Disclaimer
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Disclaimer", styles['SectionHeader']))
    story.append(Paragraph(
        "<b>Not financial advice.</b> For educational purposes only. Always consult qualified professionals.",
        styles['Body']
    ))
    
    doc.build(story)
    buffer.seek(0)
    return buffer
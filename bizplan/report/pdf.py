"""Stage 6 of the equity-report pipeline: PDF assembly. Pure Python, no LLM — takes
Stage 5's `report_reviewed.md` plus the Stage 1/2/3 JSON ground truth and renders the
final PDF via ReportLab (pure-Python, no system dependencies like Pango/cairo, so
`launch.bat` keeps working unattended on Windows) and matplotlib charts.

A lightweight, deliberately narrow markdown-to-flowables converter handles exactly the
markdown shapes the equity-report SOPs actually produce (## headings, **bold**, `- `
bullets, `> ` blockquotes, plain paragraphs) — not a general markdown parser, since the
input is fully controlled by this repo's own SOP files.
"""
import json
import os
import re
import tempfile
import xml.sax.saxutils as saxutils

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                 Image, PageBreak)

NAVY = colors.HexColor("#1c3d5a")
BLUE = colors.HexColor("#2a78d6")
GOLD = colors.HexColor("#c98500")
GRAY = colors.HexColor("#52514e")
HAIRLINE = colors.HexColor("#e1e0d9")
ALT_ROW = colors.HexColor("#f4f4f2")
WARN_RED = colors.HexColor("#b3261e")
WARN_BG = colors.HexColor("#fbeceb")

_CHART_BLUE = "#2a78d6"
_CHART_GOLD = "#eda100"
_CHART_RED = "#e34948"
_CHART_GREEN = "#1baf7a"


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("H2Report", parent=styles["Heading2"], textColor=NAVY,
                               spaceBefore=14, spaceAfter=6))
    styles.add(ParagraphStyle("BodyReport", parent=styles["BodyText"], spaceAfter=8, leading=14))
    styles.add(ParagraphStyle("BulletReport", parent=styles["BodyText"], leftIndent=14,
                               spaceAfter=4, leading=13))
    styles.add(ParagraphStyle("QuoteReport", parent=styles["BodyText"], leftIndent=14,
                               textColor=GRAY, fontName="Helvetica-Oblique", leading=13))
    styles.add(ParagraphStyle("H2Warning", parent=styles["Heading2"], textColor=WARN_RED,
                               spaceBefore=14, spaceAfter=6))
    styles.add(ParagraphStyle("WarningBody", parent=styles["BodyText"], spaceAfter=8,
                               leading=14, textColor=WARN_RED))
    return styles


def _inline_markup(text):
    """Escapes raw text for ReportLab's mini-XML, then converts **bold** markdown."""
    text = saxutils.escape(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)


def _markdown_to_flowables(md_text, styles):
    flowables = []
    for raw_line in md_text.split("\n"):
        line = raw_line.rstrip()
        if not line:
            continue
        if line.startswith("## "):
            flowables.append(Paragraph(_inline_markup(line[3:]), styles["H2Report"]))
        elif line.startswith("# "):
            flowables.append(Paragraph(_inline_markup(line[2:]), styles["Title"]))
        elif line.startswith("- ") or line.startswith("* "):
            flowables.append(Paragraph("&bull; " + _inline_markup(line[2:]), styles["BulletReport"]))
        elif line.startswith("> "):
            flowables.append(Paragraph(_inline_markup(line[2:]), styles["QuoteReport"]))
        else:
            flowables.append(Paragraph(_inline_markup(line), styles["BodyReport"]))
    return flowables


def _chart_valuation_methods(report_json, price, path):
    vps = report_json["valuation_per_share"]
    labels = ["DDM", "Residual\nIncome", "P/B-ROE", "Blended"]
    values = [vps["ddm"], vps["residual_income"], vps["pb_regression"], vps["blended"]]
    fig, ax = plt.subplots(figsize=(6, 3.2))
    bars = ax.bar(labels, values, color=[_CHART_BLUE, _CHART_BLUE, _CHART_BLUE, _CHART_GOLD])
    ax.axhline(price, color=_CHART_RED, linestyle="--", linewidth=1.5,
               label=f"Current price ({price:.2f})")
    ax.set_ylabel(f"{report_json['currency']} per share")
    ax.set_title("Valuation by method vs. current price")
    ax.legend(loc="upper left", fontsize=8)
    for bar, v in zip(bars, values):
        ax.annotate(f"{v:.2f}", (bar.get_x() + bar.get_width() / 2, v),
                    ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _chart_sensitivity(report_json, path):
    factors = report_json["sensitivity_factors"]
    names = [f["name"] for f in factors]
    downs = [f["downside"] * 100 for f in factors]
    ups = [f["upside"] * 100 for f in factors]
    fig, ax = plt.subplots(figsize=(6, 3.2))
    y = list(range(len(names)))
    ax.barh(y, ups, color=_CHART_GREEN, label="Upside")
    ax.barh(y, downs, color=_CHART_RED, label="Downside")
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=8)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("% impact on average PAT")
    ax.set_title("Net Income sensitivity")
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _chart_scenarios(report_json, path):
    vbs = report_json["valuation_by_scenario"]
    labels = ["Worst", "Base", "Best"]
    values = [vbs["worst"]["blended_per_share"], vbs["base"]["blended_per_share"],
              vbs["best"]["blended_per_share"]]
    fig, ax = plt.subplots(figsize=(6, 3.2))
    bars = ax.bar(labels, values, color=[_CHART_RED, _CHART_BLUE, _CHART_GREEN])
    ax.set_ylabel(f"{report_json['currency']} per share")
    ax.set_title("Blended fair value by scenario")
    for bar, v in zip(bars, values):
        ax.annotate(f"{v:.2f}", (bar.get_x() + bar.get_width() / 2, v),
                    ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _cover_flowables(report_json, price_json, decision_json, styles):
    flowables = [
        Paragraph(_inline_markup(report_json["business_name"]), styles["Title"]),
        Spacer(1, 6),
        Paragraph("Equity Research Report", styles["Heading3"]),
        Spacer(1, 12),
    ]
    price = price_json["share_price"]["value"]
    fair_value = report_json["valuation_per_share"]["blended"]
    currency = report_json["currency"]

    data = [
        ["Current Price", f"{currency} {price:,.2f}"],
        ["Blended Fair Value", f"{currency} {fair_value:,.2f}"],
        ["Mechanical Signal", decision_json["mechanical_signal"]],
        ["Uncertainty Tier", decision_json["uncertainty_tier"]],
        ["Reference Date", price_json["reference_date"]],
    ]
    table = Table(data, colWidths=[180, 220])
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (-1, -1), GRAY),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, HAIRLINE),
    ]))
    flowables.append(table)
    flowables.append(PageBreak())
    return flowables


def _peer_table_flowables(report_json, styles):
    flowables = [Paragraph("Peer Comparables", styles["H2Report"])]
    peers = report_json["peer_banks"]
    header = ["Bank", "EPS FY25", "ROAE FY25", "Payout FY25", "P/B"]
    data = [header] + [
        [p["name"], f"{p['eps_fy25']:.1f}", f"{p['roae_fy25'] * 100:.1f}%",
         f"{p['payout_fy25'] * 100:.1f}%", f"{p['pb_placeholder']:.2f}"]
        for p in peers
    ]
    table = Table(data, colWidths=[140, 70, 70, 80, 60])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ALT_ROW]),
        ("GRID", (0, 0), (-1, -1), 0.4, HAIRLINE),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ]))
    flowables.append(table)
    flowables.append(Spacer(1, 12))
    return flowables


def _qa_flags_flowables(findings, styles):
    """Renders unresolved coherence-gate findings as a distinct, clearly-labeled
    appendix -- never mixed into the narrative sections. Only called when the coherence
    gate (coherence.py) did not converge within its iteration budget; an empty/absent
    findings list means this section is omitted entirely."""
    flowables = [
        PageBreak(),
        Paragraph("Unresolved QA Flags", styles["H2Warning"]),
        Paragraph(
            "The automated coherence check below found issues in this report that could "
            "not be automatically resolved within the retry budget. These are listed here "
            "for transparency rather than silently omitted -- verify the flagged items "
            "against the underlying financial model before relying on this report.",
            styles["WarningBody"],
        ),
        Spacer(1, 6),
    ]
    header = ["Severity", "Section", "Description", "Model value", "Report states"]
    data = [header] + [
        [
            str(f.get("severity", "")),
            str(f.get("section", "")),
            str(f.get("description", "")),
            str(f.get("expected_value", "") or ""),
            str(f.get("actual_value", "") or ""),
        ]
        for f in findings
    ]
    table = Table(data, colWidths=[50, 70, 210, 90, 90], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), WARN_RED),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, WARN_BG]),
        ("GRID", (0, 0), (-1, -1), 0.4, HAIRLINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    flowables.append(table)
    return flowables


def build_pdf(output_dir, pdf_path, unresolved_findings=None):
    """Reads Stage 1/2/3's JSON and Stage 5's report_reviewed.md from `output_dir`,
    writes the final PDF to `pdf_path`. Returns `pdf_path`.

    `unresolved_findings`: leftover findings from the coherence gate (coherence.py) that
    didn't converge within its iteration budget. If `None`, falls back to reading
    `review_findings.json` from `output_dir` if present (so Stage 6 still surfaces flags
    when run standalone, not only via the full pipeline). An empty list/file means no
    appendix is rendered.
    """
    output_dir = str(output_dir)
    with open(os.path.join(output_dir, "valuation_inputs.json")) as f:
        report_json = json.load(f)
    with open(os.path.join(output_dir, "price_consensus_research.json")) as f:
        price_json = json.load(f)
    with open(os.path.join(output_dir, "recommendation_decision.json")) as f:
        decision_json = json.load(f)
    with open(os.path.join(output_dir, "report_reviewed.md")) as f:
        report_md = f.read()

    if unresolved_findings is None:
        findings_path = os.path.join(output_dir, "review_findings.json")
        if os.path.exists(findings_path):
            with open(findings_path) as f:
                unresolved_findings = json.load(f)
        else:
            unresolved_findings = []

    styles = _styles()
    price = price_json["share_price"]["value"]

    with tempfile.TemporaryDirectory() as tmp:
        chart_valuation = os.path.join(tmp, "valuation.png")
        chart_sensitivity = os.path.join(tmp, "sensitivity.png")
        chart_scenarios = os.path.join(tmp, "scenarios.png")
        _chart_valuation_methods(report_json, price, chart_valuation)
        _chart_sensitivity(report_json, chart_sensitivity)
        _chart_scenarios(report_json, chart_scenarios)

        doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                                 topMargin=0.75 * inch, bottomMargin=0.75 * inch,
                                 leftMargin=0.75 * inch, rightMargin=0.75 * inch)
        flowables = []
        flowables += _cover_flowables(report_json, price_json, decision_json, styles)
        flowables += _markdown_to_flowables(report_md, styles)
        flowables.append(Spacer(1, 12))
        flowables.append(Paragraph("Charts", styles["H2Report"]))
        for chart_path in (chart_valuation, chart_sensitivity, chart_scenarios):
            flowables.append(Image(chart_path, width=6 * inch, height=3.2 * inch))
            flowables.append(Spacer(1, 10))
        flowables += _peer_table_flowables(report_json, styles)
        if unresolved_findings:
            flowables += _qa_flags_flowables(unresolved_findings, styles)

        doc.build(flowables)
    return pdf_path

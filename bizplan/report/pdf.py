# Copyright (c) 2026 Edwin Njeru. Licensed under the MIT License (see LICENSE).

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


def _chart_scenario_comparison(report_json, path):
    comparison = report_json["scenario_comparison"]
    labels = ["World A\n(current rate)", "World B\n(US GAAP temporal)", "World C\n(IFRS actual)"]
    values = [comparison["operating_profit"]["A"], comparison["operating_profit"]["B"],
              comparison["operating_profit"]["C"]]
    fig, ax = plt.subplots(figsize=(6, 3.2))
    bars = ax.bar(labels, values, color=[_CHART_BLUE, _CHART_GOLD, _CHART_GREEN])
    ax.set_ylabel(f"{report_json['currency_unit']}")
    ax.set_title("Group operating profit by accounting treatment")
    for bar, v in zip(bars, values):
        ax.annotate(f"{v:,.0f}", (bar.get_x() + bar.get_width() / 2, v),
                    ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _chart_ias29_impact(report_json, path):
    impact = report_json["ias29_impact_primary_year"]["by_subsidiary"]
    metrics = ["total_assets", "turnover", "operating_profit", "net_monetary_gain_loss"]
    metric_labels = ["Total assets", "Turnover", "Op. profit", "Net monetary g/(l)"]
    subs = list(impact.keys())
    fig, ax = plt.subplots(figsize=(6, 3.2))
    x = range(len(metrics))
    width = 0.35
    colors_by_sub = [_CHART_BLUE, _CHART_GOLD]
    for i, sub in enumerate(subs):
        vals = [impact[sub][m] for m in metrics]
        offsets = [xi + (i - 0.5) * width for xi in x]
        ax.bar(offsets, vals, width=width, label=sub.capitalize(), color=colors_by_sub[i % 2])
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(list(x))
    ax.set_xticklabels(metric_labels, fontsize=8)
    ax.set_ylabel(f"{report_json['currency_unit']}")
    ax.set_title(f"IAS 29 impact by subsidiary, {report_json['ias29_impact_primary_year']['year']}")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _chart_validation_gap(report_json, path):
    gap = report_json["validation_gap"]["by_subsidiary"]
    metrics = ["total_assets", "turnover", "operating_profit", "net_monetary_gain_loss"]
    metric_labels = ["Total assets", "Turnover", "Op. profit", "Net monetary g/(l)"]
    subs = list(gap.keys())
    fig, axes = plt.subplots(1, len(subs), figsize=(6, 3.2), sharey=True)
    for ax, sub in zip(axes, subs):
        model_vals = [gap[sub][m]["model"] for m in metrics]
        disclosed_vals = [gap[sub][m]["disclosed"] for m in metrics]
        x = range(len(metrics))
        width = 0.35
        ax.bar([xi - width / 2 for xi in x], model_vals, width=width, label="Model", color=_CHART_BLUE)
        ax.bar([xi + width / 2 for xi in x], disclosed_vals, width=width, label="Disclosed", color=_CHART_GOLD)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_xticks(list(x))
        ax.set_xticklabels(metric_labels, fontsize=7, rotation=30, ha="right")
        ax.set_title(sub.capitalize(), fontsize=9)
    axes[0].set_ylabel(f"{report_json['currency_unit']}")
    axes[0].legend(fontsize=7)
    fig.suptitle(f"Model vs. disclosed, {report_json['validation_gap']['year']} (roll-forward validation)",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _cover_flowables(report_json, decision_json, styles):
    flowables = [
        Paragraph(_inline_markup(report_json["business_name"]), styles["Title"]),
        Spacer(1, 6),
        Paragraph("Hyperinflation Accounting Analysis — CFA LII Multinational Operations", styles["Heading3"]),
        Spacer(1, 12),
    ]
    facts = report_json["company_facts"]
    currency = report_json["currency"]

    data = [
        ["Group Operating Profit (IFRS actual)", f"{currency} {facts['operating_profit_eur']:,.1f}m"],
        ["Net Monetary Gain/(Loss)", f"{currency} {facts['net_monetary_gain_loss_eur']:,.1f}m"],
        ["Earnings-Quality Signal", decision_json["mechanical_signal"]],
        ["Materiality Ratio", f"{decision_json['ratio'] * 100:.1f}%"],
        ["As-of Year", str(facts["as_of_year"])],
    ]
    table = Table(data, colWidths=[220, 180])
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


def _monetary_exposure_table_flowables(report_json, styles):
    flowables = [Paragraph("Monetary-Exposure Grades", styles["H2Report"])]
    exposure = report_json["monetary_exposure"]
    header = ["Subsidiary", "Grade", "Net Monetary G/(L)", "Total Assets", "Exposure Ratio"]
    data = [header] + [
        [name.capitalize(), g["grade"], f"{g['monetary_gain_loss']:,.1f}", f"{g['total_assets']:,.1f}",
         f"{g['exposure_ratio'] * 100:+.1f}%"]
        for name, g in exposure.items() if name != "overall_grade"
    ]
    table = Table(data, colWidths=[110, 60, 110, 100, 90])
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

    with tempfile.TemporaryDirectory() as tmp:
        chart_scenario = os.path.join(tmp, "scenario_comparison.png")
        chart_impact = os.path.join(tmp, "ias29_impact.png")
        chart_validation = os.path.join(tmp, "validation_gap.png")
        _chart_scenario_comparison(report_json, chart_scenario)
        _chart_ias29_impact(report_json, chart_impact)
        _chart_validation_gap(report_json, chart_validation)

        doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                                 topMargin=0.75 * inch, bottomMargin=0.75 * inch,
                                 leftMargin=0.75 * inch, rightMargin=0.75 * inch)
        flowables = []
        flowables += _cover_flowables(report_json, decision_json, styles)
        flowables += _markdown_to_flowables(report_md, styles)
        flowables.append(Spacer(1, 12))
        flowables.append(Paragraph("Charts", styles["H2Report"]))
        for chart_path in (chart_scenario, chart_impact, chart_validation):
            flowables.append(Image(chart_path, width=6 * inch, height=3.2 * inch))
            flowables.append(Spacer(1, 10))
        flowables += _monetary_exposure_table_flowables(report_json, styles)
        if unresolved_findings:
            flowables += _qa_flags_flowables(unresolved_findings, styles)

        doc.build(flowables)
    return pdf_path

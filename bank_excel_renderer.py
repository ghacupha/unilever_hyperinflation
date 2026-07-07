"""Bank financial model Excel renderer.

Produces a fully formula-linked workbook: Cover, Summary, Assumptions, Scenarios, Model,
Valuation. Every calculated cell on the Model sheet (Base Case) is a live Excel formula
string referencing other cells — Assumptions-sheet input cells for rates/opening balances,
and prior-column-same-row for recurrences — not a Python-computed static value. Best/Worst
on the Scenarios sheet remain Python-computed static values (existing convention).

`bank_calculations.py`'s output (`results`, from `build_all()`) is used only to (a) source
input/assumption values and (b) as a ground-truth cross-check while writing formulas — it
is not written into Model-sheet calculated cells directly.

Bookkeeping: `A` (assumption refs) maps a descriptive key -> Assumptions-sheet row number
(column is always ASSUM_COL). `M` (model row_refs) maps a descriptive key -> Model-sheet
row number. Both dicts are threaded through the builder functions as they write rows, so
later formulas can reference earlier rows by key instead of a hardcoded row number.
"""

import os

from openpyxl.utils import get_column_letter

from bizplan.financial.xl_helpers import (
    NAVY, MED_BLUE, LIGHT_BLUE, WHITE, DARK, MID_GRAY, ALT_ROW, GOLD, TOTAL_FILL,
    GREEN_DRK, RED_DARK, ORANGE, TEAL, BLUE_INPUT,
    fill, write, num, pct, header_row, section_header, year_header_row, blank_row,
    data_row, total_row, set_col_widths, top_bottom_border,
    _cell, _sum_f, _add_rows_f, _sub_f, _ratio_f, _ref_f, _model_ref,
)

ACTUAL_COLS = [8, 9, 10]          # H, I, J: 2023-2025 actuals (hardcoded facts + subtotal formulas)
DATA_COLS = [11, 12, 13, 14, 15]  # K-O: 2026-2030 projection (fully live formulas)
ASSUM_COL = 8  # single "value" column for scalar assumptions (Assumptions sheet only —
               # unaffected by the Model sheet's actual/projected column split)
LABEL_COL = 3
UNITS_COL = 6
MASTER_HEADER_ROW = 11  # Model sheet's own top year-header row (written once in build_model);
# every other Model-sheet schedule repeats a formula-linked copy of it via
# _linked_year_header_row(), so scrolling never loses the column-to-period mapping.

# Scenario switch: a single cell (1=Base, 2=Best, 3=Worst) on the Scenarios sheet. Every
# scenario-dependent assumption on the Assumptions sheet resolves to an "ACTIVE" row via
# CHOOSE() keyed to this cell, so flipping it re-drives the entire live Model sheet —
# matches the Blu Containers FMI reference's `Scenarios!$D$6` pattern exactly.
SWITCH_CELL_REF = "'Scenarios'!$D$5"

PROVENANCE_LEGEND = [
    ("Disclosed fact (company filing)", BLUE_INPUT),
    ("Internal formula", DARK),
    ("Cross-sheet reference", TEAL),
    ("Modeled proxy / benchmark / macro forecast — not directly disclosed", ORANGE),
]


def _col_widths(ws):
    set_col_widths(ws, {
        'A': 2, 'B': 2, 'C': 32, 'D': 16, 'E': 4, 'F': 12,
        'G': 2, 'H': 14, 'I': 14, 'J': 14, 'K': 14, 'L': 14, 'M': 14, 'N': 14, 'O': 14,
        'P': 4,
    })


# ─────────────────────────────────────────────
# ASSUMPTIONS SHEET
# ─────────────────────────────────────────────

def _assum_row(ws, row, label, value, color, refs=None, key=None, fmt='#,##0.00', note=""):
    write(ws, row, LABEL_COL, label, bg=WHITE)
    if isinstance(value, str) and value.startswith("="):
        num(ws, row, ASSUM_COL, value, fmt=fmt, txt_color=color)
    else:
        num(ws, row, ASSUM_COL, value, fmt=fmt, txt_color=color)
    if note:
        write(ws, row, 10, note, txt_color=MID_GRAY, italic=True, size=9)
    if refs is not None and key is not None:
        refs[key] = row
    return row + 1


def _scenario_row(ws, row, label, base_value, mult_best_ref, mult_worst_ref, refs, key, fmt='0.0%'):
    """Writes Base (hardcoded)/Best/Worst (formula = Base x multiplier)/ACTIVE (CHOOSE on
    the scenario switch) as 4 rows. `refs[key]` is set to the ACTIVE row, so every
    downstream Model-sheet formula that references this assumption automatically follows
    whichever scenario the switch is set to."""
    base_row = row
    write(ws, row, LABEL_COL, f"    {label} — Base")
    num(ws, row, ASSUM_COL, base_value, fmt=fmt, txt_color=ORANGE)
    row += 1

    best_row = row
    write(ws, row, LABEL_COL, f"    {label} — Best", txt_color=MID_GRAY, italic=True)
    num(ws, row, ASSUM_COL, f"={_cell(base_row, ASSUM_COL)}*{mult_best_ref}", fmt=fmt, txt_color=DARK)
    row += 1

    worst_row = row
    write(ws, row, LABEL_COL, f"    {label} — Worst", txt_color=MID_GRAY, italic=True)
    num(ws, row, ASSUM_COL, f"={_cell(base_row, ASSUM_COL)}*{mult_worst_ref}", fmt=fmt, txt_color=DARK)
    row += 1

    active_row = row
    write(ws, row, LABEL_COL, f"{label} (ACTIVE)", bold=True)
    active_formula = (f"=CHOOSE({SWITCH_CELL_REF},{_cell(base_row, ASSUM_COL)},"
                       f"{_cell(best_row, ASSUM_COL)},{_cell(worst_row, ASSUM_COL)})")
    num(ws, row, ASSUM_COL, active_formula, fmt=fmt, txt_color=TEAL, bold=True)
    row += 1

    refs[key] = active_row
    return row


def build_assumptions(wb, config):
    ws = wb.create_sheet("Assumptions", index=2)
    ws.sheet_view.showGridLines = False
    _col_widths(ws)
    A = {}

    R = 1
    write(ws, R, LABEL_COL, config.BUSINESS_NAME, bold=True, size=14, txt_color=NAVY); R += 2
    write(ws, R, LABEL_COL, "Inputs and Assumptions", txt_color=MID_GRAY); R += 2

    section_header(ws, R, "Data Provenance Legend"); R += 1
    for label, color in PROVENANCE_LEGEND:
        write(ws, R, LABEL_COL, "■", txt_color=color, bold=True)
        write(ws, R, 4, label, txt_color=MID_GRAY, size=9, italic=True)
        R += 1
    R += 1

    section_header(ws, R, "GENERAL"); R += 1
    R = _assum_row(ws, R, "First forecast year", config.YEARS[0], BLUE_INPUT, A, "first_year", fmt='0')
    R = _assum_row(ws, R, "Tax rate", config.TAX_RATE, BLUE_INPUT, A, "tax_rate", fmt='0.0%')
    R = _assum_row(ws, R, "Dividend payout ratio", config.DIVIDEND_PAYOUT_RATIO, ORANGE, A, "dividend_payout", fmt='0.0%')
    R += 1

    section_header(ws, R, "SCENARIO CONTROL"); R += 1
    write(ws, R, 10, "Switch lives on the Scenarios sheet ($D$5) — every row below tagged "
                     "'(ACTIVE)' follows it live.", txt_color=MID_GRAY, italic=True, size=9)
    sm = config.SCENARIO_MULTIPLIERS
    R = _assum_row(ws, R, "Growth multiplier — Best", sm["best"]["growth_mult"], ORANGE, A, "growth_mult_best", fmt='0.00')
    R = _assum_row(ws, R, "Growth multiplier — Worst", sm["worst"]["growth_mult"], ORANGE, A, "growth_mult_worst", fmt='0.00')
    R = _assum_row(ws, R, "Loss-rate multiplier — Best", sm["best"]["loss_rate_mult"], ORANGE, A, "loss_rate_mult_best", fmt='0.00')
    R = _assum_row(ws, R, "Loss-rate multiplier — Worst", sm["worst"]["loss_rate_mult"], ORANGE, A, "loss_rate_mult_worst", fmt='0.00')
    R = _assum_row(ws, R, "Opex-escalation multiplier — Best", sm["best"]["opex_mult"], ORANGE, A, "opex_mult_best", fmt='0.00')
    R = _assum_row(ws, R, "Opex-escalation multiplier — Worst", sm["worst"]["opex_mult"], ORANGE, A, "opex_mult_worst", fmt='0.00')
    R += 1

    growth_mult_best_ref = _assum_ref(A, "growth_mult_best")
    growth_mult_worst_ref = _assum_ref(A, "growth_mult_worst")
    loss_rate_mult_best_ref = _assum_ref(A, "loss_rate_mult_best")
    loss_rate_mult_worst_ref = _assum_ref(A, "loss_rate_mult_worst")

    section_header(ws, R, "LOAN BOOK — BY PRODUCT (FY2025 opening; growth/rates scenario-switched)"); R += 1
    for seg in config.LOAN_SEGMENTS:
        k = seg["key"]
        write(ws, R, LABEL_COL, seg["name"], bold=True, txt_color=NAVY); R += 1
        R = _assum_row(ws, R, "Opening gross — Stage 1", seg["opening_s1"], BLUE_INPUT, A, f"{k}_opening_s1")
        R = _assum_row(ws, R, "Opening gross — Stage 2", seg["opening_s2"], BLUE_INPUT, A, f"{k}_opening_s2")
        R = _assum_row(ws, R, "Opening gross — Stage 3", seg["opening_s3"], BLUE_INPUT, A, f"{k}_opening_s3")
        R = _scenario_row(ws, R, "Loss rate — Stage 1 (12m)", seg["loss_rate_s1"],
                           loss_rate_mult_best_ref, loss_rate_mult_worst_ref, A, f"{k}_loss_rate_s1", fmt='0.000%')
        R = _scenario_row(ws, R, "Loss rate — Stage 2 (lifetime)", seg["loss_rate_s2"],
                           loss_rate_mult_best_ref, loss_rate_mult_worst_ref, A, f"{k}_loss_rate_s2", fmt='0.000%')
        R = _scenario_row(ws, R, "Loss rate — Stage 3 (lifetime)", seg["loss_rate_s3"],
                           loss_rate_mult_best_ref, loss_rate_mult_worst_ref, A, f"{k}_loss_rate_s3", fmt='0.000%')
        R = _scenario_row(ws, R, "Gross loan growth p.a.", seg["growth"],
                           growth_mult_best_ref, growth_mult_worst_ref, A, f"{k}_growth", fmt='0.0%')
        R = _assum_row(ws, R, "Yield on loans", seg["yield_rate"], ORANGE, A, f"{k}_yield_rate", fmt='0.00%')
        R = _assum_row(ws, R, "SICR rate (Stage 1→2)", seg["sicr_rate"], ORANGE, A, f"{k}_sicr_rate", fmt='0.0%')
        R = _assum_row(ws, R, "Cure rate (Stage 2→1)", seg["cure_21"], ORANGE, A, f"{k}_cure_21", fmt='0.0%')
        R = _assum_row(ws, R, "Default rate (Stage 2→3)", seg["default_rate"], ORANGE, A, f"{k}_default_rate", fmt='0.0%')
        R = _assum_row(ws, R, "Cure rate (Stage 3→2)", seg["cure_32"], ORANGE, A, f"{k}_cure_32", fmt='0.0%')
        R = _assum_row(ws, R, "Write-off rate (of Stage 3)", seg["writeoff_rate"], ORANGE, A, f"{k}_writeoff_rate", fmt='0.0%')
        R = _assum_row(ws, R, "Risk weight (RWA)", seg["risk_weight"], ORANGE, A, f"{k}_risk_weight", fmt='0%')
        R += 1

    write(ws, R, LABEL_COL, "Off-Balance-Sheet Exposure", bold=True, txt_color=NAVY); R += 1
    ob = config.OFF_BALANCE_SHEET
    R = _assum_row(ws, R, "Opening balance", ob["opening"], BLUE_INPUT, A, "ob_opening")
    R = _assum_row(ws, R, "Growth p.a.", ob["growth"], ORANGE, A, "ob_growth", fmt='0.0%')
    R = _assum_row(ws, R, "Credit conversion factor", ob["ccf"], ORANGE, A, "ob_ccf", fmt='0%')
    R = _assum_row(ws, R, "Risk weight", ob["risk_weight"], ORANGE, A, "ob_risk_weight", fmt='0%')
    R += 1

    section_header(ws, R, "FORWARD-LOOKING MACRO OVERLAY (IFRS 9)"); R += 1
    m = config.MACRO_SCENARIOS
    R = _assum_row(ws, R, "Weight — Base", m["weights"]["base"], ORANGE, A, "macro_w_base", fmt='0%')
    R = _assum_row(ws, R, "Weight — Upside", m["weights"]["upside"], ORANGE, A, "macro_w_upside", fmt='0%')
    R = _assum_row(ws, R, "Weight — Downside", m["weights"]["downside"], ORANGE, A, "macro_w_downside", fmt='0%')
    R = _assum_row(ws, R, "Multiplier — Base", m["multipliers"]["base"], ORANGE, A, "macro_m_base", fmt='0.00')
    R = _assum_row(ws, R, "Multiplier — Upside", m["multipliers"]["upside"], ORANGE, A, "macro_m_upside", fmt='0.00')
    R = _assum_row(ws, R, "Multiplier — Downside", m["multipliers"]["downside"], ORANGE, A, "macro_m_downside", fmt='0.00')
    blend_formula = (
        f"={_cell(A['macro_w_base'], ASSUM_COL)}*{_cell(A['macro_m_base'], ASSUM_COL)}"
        f"+{_cell(A['macro_w_upside'], ASSUM_COL)}*{_cell(A['macro_m_upside'], ASSUM_COL)}"
        f"+{_cell(A['macro_w_downside'], ASSUM_COL)}*{_cell(A['macro_m_downside'], ASSUM_COL)}"
    )
    write(ws, R, LABEL_COL, "Blended macro multiplier (probability-weighted)", bold=True)
    num(ws, R, ASSUM_COL, blend_formula, fmt='0.0000', txt_color=DARK, bold=True)
    A["macro_mult"] = R
    R += 2

    section_header(ws, R, "DEPOSITS / FUNDING (allocation modeled — only the aggregate is disclosed)"); R += 1
    for dep in config.DEPOSIT_TYPES:
        k = dep["key"]
        write(ws, R, LABEL_COL, dep["name"], bold=True); R += 1
        R = _assum_row(ws, R, "Opening balance", dep["opening"], ORANGE, A, f"{k}_opening")
        R = _scenario_row(ws, R, "Growth p.a.", dep["growth"],
                           growth_mult_best_ref, growth_mult_worst_ref, A, f"{k}_growth", fmt='0.0%')
        R = _assum_row(ws, R, "Cost of funds", dep["cost_rate"], ORANGE, A, f"{k}_cost_rate", fmt='0.00%')
    R += 1

    section_header(ws, R, "INVESTMENT SECURITIES"); R += 1
    sec = config.INVESTMENT_SECURITIES
    R = _assum_row(ws, R, "Opening balance", sec["opening"], BLUE_INPUT, A, "sec_opening")
    R = _assum_row(ws, R, "Growth p.a.", sec["growth"], ORANGE, A, "sec_growth", fmt='0.0%')
    R = _assum_row(ws, R, "Yield", sec["yield_rate"], ORANGE, A, "sec_yield_rate", fmt='0.00%')
    R += 1

    section_header(ws, R, "NON-INTEREST INCOME"); R += 1
    R = _assum_row(ws, R, "Fee/commission income (% of deposits)",
                   getattr(config, "NON_INTEREST_INCOME_RATE", 0.012), ORANGE, A, "nii_rate", fmt='0.00%')
    R += 1

    opex_mult_best_ref = _assum_ref(A, "opex_mult_best")
    opex_mult_worst_ref = _assum_ref(A, "opex_mult_worst")
    section_header(ws, R, "OPERATING EXPENSES"); R += 1
    for item in config.OPEX_ITEMS:
        k = item["key"]
        R = _assum_row(ws, R, f"{item['name']} — Year 1", item["y1"], ORANGE, A, f"opex_{k}_y1")
        R = _scenario_row(ws, R, f"{item['name']} — escalation p.a.", item["escalation"],
                           opex_mult_best_ref, opex_mult_worst_ref, A, f"opex_{k}_esc", fmt='0.0%')
    R += 1

    section_header(ws, R, "CAPITAL"); R += 1
    cap = config.CAPITAL
    R = _assum_row(ws, R, "Opening Tier 1 capital (accounting equity, Balance Sheet anchor)",
                    cap["opening_tier1"], ORANGE, A, "opening_tier1")
    R = _assum_row(ws, R, "Opening Tier 2 capital (Balance Sheet liability-side anchor)",
                    cap["opening_tier2"], ORANGE, A, "opening_tier2")
    R = _assum_row(ws, R, "Core capital / RWA minimum (CBK)", cap["core_capital_rwa_min"], BLUE_INPUT, A, "core_min", fmt='0.0%')
    R = _assum_row(ws, R, "Total capital / RWA minimum (CBK)", cap["total_capital_rwa_min"], BLUE_INPUT, A, "total_min", fmt='0.0%')
    R = _assum_row(ws, R, "Core capital / deposits minimum (CBK)", cap["core_capital_deposits_min"], BLUE_INPUT, A, "deposits_min", fmt='0.0%')
    R = _assum_row(ws, R, "Minimum core capital, absolute (CBK)", cap["min_core_capital_absolute"], BLUE_INPUT, A, "min_core_capital_absolute")
    R = _assum_row(ws, R, "Other RWA (% of gross loans, projected years)",
                    cap["other_rwa_pct_of_gross_loans"], ORANGE, A, "other_rwa_pct_of_gross_loans", fmt='0.0%')
    R = _assum_row(ws, R, "Regulatory Tier 1 (% of Total Equity, projected years)",
                    cap["tier1_pct_of_equity"], ORANGE, A, "tier1_pct_of_equity", fmt='0.0%')
    R = _assum_row(ws, R, "Regulatory Tier 2 (opening, held flat, projected years)",
                    cap["reg_tier2_opening"], ORANGE, A, "reg_tier2_opening")
    last_actual = config.ACTUALS[max(config.ACTUAL_YEARS)]
    R = _assum_row(ws, R, "Share capital (opening, held flat)", last_actual["share_capital"], ORANGE, A, "share_capital_opening")
    R = _assum_row(ws, R, "Share premium (opening, held flat)", last_actual["share_premium"], ORANGE, A, "share_premium_opening")
    R += 1

    section_header(ws, R, "PP&E, LIQUIDITY & BALANCE-SHEET PLUGS"); R += 1
    ppe = config.PPE
    R = _assum_row(ws, R, "Opening PP&E", ppe["opening"], ORANGE, A, "ppe_opening")
    R = _assum_row(ws, R, "D&A rate (of opening PP&E)", ppe["da_rate"], ORANGE, A, "da_rate", fmt='0.0%')
    R = _assum_row(ws, R, "Capex rate (of opening PP&E)", ppe["capex_rate"], ORANGE, A, "capex_rate", fmt='0.0%')
    R = _assum_row(ws, R, "Opening cash", config.OPENING_CASH, BLUE_INPUT, A, "opening_cash", note="Derived to tie opening liquidity ratio to disclosed 38.7%")
    R = _assum_row(ws, R, "Other B/S items growth rate (projected years)",
                    config.OTHER_BS_ITEMS_GROWTH_RATE, ORANGE, A, "other_bs_items_growth", fmt='0.0%',
                    note="Applies to granular Balance Sheet lines with no disclosed forward driver")
    R = _assum_row(ws, R, "Statutory liquidity ratio minimum (CBK)", config.LIQUIDITY_STATUTORY_MIN, BLUE_INPUT, A, "liquidity_min", fmt='0.0%')
    R += 1

    section_header(ws, R, "VALUATION"); R += 1
    v = config.VALUATION
    R = _assum_row(ws, R, "Risk-free rate (Kenya 10Y bond yield)", v["risk_free_rate"], BLUE_INPUT, A, "risk_free_rate", fmt='0.00%')
    R = _assum_row(ws, R, "Equity risk premium (Kenya, Damodaran)", v["equity_risk_premium"], ORANGE, A, "erp", fmt='0.00%',
                   note="[PLACEHOLDER] pending exact Damodaran Kenya figure")
    R = _assum_row(ws, R, "Beta", v["beta"], ORANGE, A, "beta", fmt='0.00', note="[PLACEHOLDER] pending peer/company beta research")
    R = _assum_row(ws, R, "Terminal growth rate", v["terminal_growth"], ORANGE, A, "terminal_growth", fmt='0.0%')
    coe_formula = f"={_cell(A['risk_free_rate'], ASSUM_COL)}+{_cell(A['beta'], ASSUM_COL)}*{_cell(A['erp'], ASSUM_COL)}"
    write(ws, R, LABEL_COL, "Cost of equity (CAPM)", bold=True)
    num(ws, R, ASSUM_COL, coe_formula, fmt='0.00%', txt_color=DARK, bold=True)
    A["cost_of_equity"] = R
    R += 1
    R = _assum_row(ws, R, "Shares outstanding (FY2025 year-end, KES 1.00 par value)",
                    config.SHARES_OUTSTANDING_2025, BLUE_INPUT, A, "shares_outstanding",
                    fmt='#,##0.000', note="Integrated Report 2025 p.265 — period-end count, not the "
                    "weighted-average count used for historical EPS")
    R += 1

    section_header(ws, R, "PEER BANKS — for P/B-ROE regression and P/E cross-check "
                          "([PLACEHOLDER] P/B pending real peer market data)"); R += 1
    hdr_row = R
    for col, label in [(3, "Bank"), (7, "EPS FY24"), (8, "EPS FY25"), (9, "ROAE FY24"),
                       (10, "ROAE FY25"), (11, "Payout FY25"), (12, "P/B (placeholder)")]:
        write(ws, R, col, label, bold=True, bg=LIGHT_BLUE, halign="center" if col > 3 else "left")
    R += 1
    peer_first_row = R
    for peer in config.PEER_BANKS:
        write(ws, R, 3, peer["name"])
        num(ws, R, 7, peer["eps_fy24"], fmt='#,##0.0', txt_color=BLUE_INPUT)
        num(ws, R, 8, peer["eps_fy25"], fmt='#,##0.0', txt_color=BLUE_INPUT)
        num(ws, R, 9, peer["roae_fy24"], fmt='0.0%', txt_color=BLUE_INPUT)
        num(ws, R, 10, peer["roae_fy25"], fmt='0.0%', txt_color=BLUE_INPUT)
        num(ws, R, 11, peer["payout_fy25"], fmt='0.0%', txt_color=BLUE_INPUT)
        num(ws, R, 12, peer["pb_placeholder"], fmt='0.00', txt_color=ORANGE)
        R += 1
    peer_last_row = R - 1
    A["peer_first_row"] = peer_first_row
    A["peer_last_row"] = peer_last_row
    R += 1
    slope_formula = f"=SLOPE({_cell(peer_first_row, 12)}:{_cell(peer_last_row, 12)},{_cell(peer_first_row, 10)}:{_cell(peer_last_row, 10)})"
    intercept_formula = f"=INTERCEPT({_cell(peer_first_row, 12)}:{_cell(peer_last_row, 12)},{_cell(peer_first_row, 10)}:{_cell(peer_last_row, 10)})"
    write(ws, R, LABEL_COL, "P/B-ROE regression slope", bold=True)
    num(ws, R, ASSUM_COL, slope_formula, fmt='0.0000', txt_color=DARK, bold=True)
    A["pb_roe_slope"] = R; R += 1
    write(ws, R, LABEL_COL, "P/B-ROE regression intercept", bold=True)
    num(ws, R, ASSUM_COL, intercept_formula, fmt='0.0000', txt_color=DARK, bold=True)
    A["pb_roe_intercept"] = R; R += 1

    return A


# ─────────────────────────────────────────────
# MODEL SHEET — helpers
# ─────────────────────────────────────────────

def _assum_ref(A, key):
    return f"Assumptions!${get_column_letter(ASSUM_COL)}${A[key]}"


def _prev(i, model_row):
    """Cell reference to the prior period's value on the Model sheet: the last actual
    column for the first projected period (2026 rolls forward from the 2025 actual,
    same row, same sheet — no Assumptions-cell fallback needed since the actual column
    now exists directly on the Model sheet), same-row-prior-column otherwise."""
    if i == 0:
        return _cell(model_row, ACTUAL_COLS[-1])
    return _cell(model_row, DATA_COLS[i - 1])


def _write_formula_row(ws, row, label, formulas, bold=False, fmt='#,##0.0', units=None,
                        alt_idx=None, indent=0, cols=None):
    cols = cols or DATA_COLS
    row_bg = ALT_ROW if (alt_idx is not None and alt_idx % 2 == 0) else WHITE
    for c in range(1, 17):
        ws.cell(row=row, column=c).fill = fill(row_bg)
    lbl = ("    " * indent) + label if indent else label
    write(ws, row, LABEL_COL, lbl, bold=bold, bg=row_bg)
    if units:
        write(ws, row, UNITS_COL, units, txt_color=MID_GRAY, italic=True, size=9, bg=row_bg, halign="center")
    for i, col in enumerate(cols):
        val = formulas[i]
        is_formula = isinstance(val, str) and val.startswith("=")
        color = (TEAL if (is_formula and "Assumptions!" in val)
                 else DARK if is_formula else BLUE_INPUT)
        num(ws, row, col, val, fmt=fmt, bold=bold, bg=row_bg, txt_color=color)


def _write_actual_row(ws, row, label, values, bold=False, fmt='#,##0.0', units=None,
                       alt_idx=None, indent=0):
    """Actual-year columns: raw disclosed figures are hardcoded facts (blue); subtotal/
    ratio rows are same-column formula strings (start with '=', colored dark)."""
    _write_formula_row(ws, row, label, values, bold=bold, fmt=fmt, units=units,
                        alt_idx=alt_idx, indent=indent, cols=ACTUAL_COLS)


def _model_period_header(ws, R):
    """'Actual' band over ACTUAL_COLS, 'Projected' band over DATA_COLS."""
    ws.row_dimensions[R].height = 13
    for c in range(1, 17):
        ws.cell(row=R, column=c).fill = fill(MED_BLUE)
    write(ws, R, ACTUAL_COLS[len(ACTUAL_COLS) // 2], "Actual", bold=True, bg=MED_BLUE,
          txt_color=WHITE, halign="center")
    write(ws, R, DATA_COLS[len(DATA_COLS) // 2], "Projected", bold=True, bg=MED_BLUE,
          txt_color=WHITE, halign="center")
    return R + 1


def _all_cols():
    return ACTUAL_COLS + DATA_COLS


def _period_label(year, is_actual):
    return f"{year}{'A' if is_actual else 'P'}"


def _period_labels(config):
    return [_period_label(y, True) for y in config.ACTUAL_YEARS] + \
           [_period_label(y, False) for y in config.YEARS]


def _period_labels_actual(config):
    return [_period_label(y, True) for y in config.ACTUAL_YEARS]


def _period_labels_proj(config):
    return [_period_label(y, False) for y in config.YEARS]


def _linked_year_header_row(ws, row, cols, label_col=None):
    """Repeats the Model sheet's master year-header row (MASTER_HEADER_ROW) at the top of
    every schedule, so scrolling down the sheet never loses the column-to-period mapping.
    Every cell is a formula referencing the master row — a single source of truth, not a
    duplicated literal — so relabeling the master row propagates everywhere automatically."""
    ws.row_dimensions[row].height = 14
    for c in range(1, 17):
        ws.cell(row=row, column=c).fill = fill(MED_BLUE)
    if label_col:
        write(ws, row, label_col, "", bg=MED_BLUE)
    for col in cols:
        write(ws, row, col, f"={_cell(MASTER_HEADER_ROW, col)}", bold=True, size=10,
              txt_color=WHITE, bg=MED_BLUE, halign="center")


# ─────────────────────────────────────────────
# MODEL SHEET — Schedule 1/1b: Loan Book & IFRS 9 Provisioning
# ─────────────────────────────────────────────

def _actual(config, year, *path):
    """Dig into config.ACTUALS[year] along `path` (dict keys)."""
    node = config.ACTUALS[year]
    for p in path:
        node = node[p]
    return node


def _build_loan_book_section(ws, config, A, M, R):
    section_header(ws, R, "LOAN BOOK & IFRS 9 PROVISIONING", bg=NAVY, txt_color=WHITE); R += 1
    _linked_year_header_row(ws, R, _all_cols(), label_col=LABEL_COL); R += 1
    blank_row(ws, R); R += 1

    agg_gross_rows, agg_ecl_rows, agg_s3_gross_rows, agg_charge_rows = [], [], [], []
    ay = config.ACTUAL_YEARS

    for seg in config.LOAN_SEGMENTS:
        k = seg["key"]
        write(ws, R, LABEL_COL, seg["name"], bold=True, txt_color=NAVY); R += 1

        s1_row, s2_row, s3_row = R, R + 1, R + 2

        # Actual columns: raw disclosed stage balances, hardcoded.
        s1_actual = [_actual(config, y, "loan_segments", k, "gross_s1") for y in ay]
        s2_actual = [_actual(config, y, "loan_segments", k, "gross_s2") for y in ay]
        s3_actual = [_actual(config, y, "loan_segments", k, "gross_s3") for y in ay]

        # Projected columns: live recurrence, referencing the prior period same row
        # (last actual column for 2026, per _prev()).
        s1_proj, s2_proj, s3_proj = [], [], []
        for i, col in enumerate(DATA_COLS):
            prev1, prev2, prev3 = _prev(i, s1_row), _prev(i, s2_row), _prev(i, s3_row)
            sicr = _assum_ref(A, f"{k}_sicr_rate")
            cure21 = _assum_ref(A, f"{k}_cure_21")
            growth = _assum_ref(A, f"{k}_growth")
            wo = _assum_ref(A, f"{k}_writeoff_rate")
            s1_proj.append(f"={prev1}-{sicr}*{prev1}+{cure21}*{prev2}"
                           f"+{growth}*({prev1}+{prev2}+{prev3})+{wo}*{prev3}")
            default_r = _assum_ref(A, f"{k}_default_rate")
            cure32 = _assum_ref(A, f"{k}_cure_32")
            s2_proj.append(f"={prev2}+{sicr}*{prev1}-{cure21}*{prev2}-{default_r}*{prev2}+{cure32}*{prev3}")
            s3_proj.append(f"={prev3}+{default_r}*{prev2}-{cure32}*{prev3}-{wo}*{prev3}")
        R += 3

        _write_actual_row(ws, s1_row, "Gross — Stage 1", s1_actual, units="(KES MM)", alt_idx=0)
        _write_formula_row(ws, s1_row, "Gross — Stage 1", s1_proj, units="(KES MM)", alt_idx=0)
        _write_actual_row(ws, s2_row, "Gross — Stage 2", s2_actual, units="(KES MM)", alt_idx=1)
        _write_formula_row(ws, s2_row, "Gross — Stage 2", s2_proj, units="(KES MM)", alt_idx=1)
        _write_actual_row(ws, s3_row, "Gross — Stage 3", s3_actual, units="(KES MM)", alt_idx=0)
        _write_formula_row(ws, s3_row, "Gross — Stage 3", s3_proj, units="(KES MM)", alt_idx=0)

        gross_total_row = R
        total_row(ws, R, f"Total Gross — {seg['name']}", [_sum_f(s1_row, s3_row, c) for c in ACTUAL_COLS],
                  ACTUAL_COLS, label_col=LABEL_COL)
        total_row(ws, R, f"Total Gross — {seg['name']}", [_sum_f(s1_row, s3_row, c) for c in DATA_COLS],
                  DATA_COLS, label_col=LABEL_COL)
        R += 1

        e1_row, e2_row, e3_row = R, R + 1, R + 2
        e1_actual = [_actual(config, y, "loan_segments", k, "ecl_s1") for y in ay]
        e2_actual = [_actual(config, y, "loan_segments", k, "ecl_s2") for y in ay]
        e3_actual = [_actual(config, y, "loan_segments", k, "ecl_s3") for y in ay]
        e1_proj = [f"={_assum_ref(A, f'{k}_loss_rate_s1')}*{_assum_ref(A, 'macro_mult')}*{_cell(s1_row, c)}"
                   for c in DATA_COLS]
        e2_proj = [f"={_assum_ref(A, f'{k}_loss_rate_s2')}*{_assum_ref(A, 'macro_mult')}*{_cell(s2_row, c)}"
                   for c in DATA_COLS]
        e3_proj = [f"={_assum_ref(A, f'{k}_loss_rate_s3')}*{_assum_ref(A, 'macro_mult')}*{_cell(s3_row, c)}"
                   for c in DATA_COLS]
        _write_actual_row(ws, e1_row, "ECL — Stage 1", e1_actual, units="(KES MM)", alt_idx=1)
        _write_formula_row(ws, e1_row, "ECL — Stage 1", e1_proj, units="(KES MM)", alt_idx=1)
        _write_actual_row(ws, e2_row, "ECL — Stage 2", e2_actual, units="(KES MM)", alt_idx=0)
        _write_formula_row(ws, e2_row, "ECL — Stage 2", e2_proj, units="(KES MM)", alt_idx=0)
        _write_actual_row(ws, e3_row, "ECL — Stage 3", e3_actual, units="(KES MM)", alt_idx=1)
        _write_formula_row(ws, e3_row, "ECL — Stage 3", e3_proj, units="(KES MM)", alt_idx=1)
        R += 3

        ecl_total_row = R
        total_row(ws, R, f"Total ECL — {seg['name']}", [_sum_f(e1_row, e3_row, c) for c in ACTUAL_COLS],
                  ACTUAL_COLS, label_col=LABEL_COL)
        total_row(ws, R, f"Total ECL — {seg['name']}", [_sum_f(e1_row, e3_row, c) for c in DATA_COLS],
                  DATA_COLS, label_col=LABEL_COL)
        R += 1

        net_row = R
        _write_actual_row(ws, R, f"Net Loans — {seg['name']}",
                           [_sub_f(gross_total_row, ecl_total_row, c) for c in ACTUAL_COLS],
                           bold=True, units="(KES MM)")
        _write_formula_row(ws, R, f"Net Loans — {seg['name']}",
                            [_sub_f(gross_total_row, ecl_total_row, c) for c in DATA_COLS],
                            bold=True, units="(KES MM)")
        R += 1

        charge_row = R
        # Actual: 2023 (first actual year) has no prior-year ECL total in this model to
        # diff against, so it's left blank; 2024/2025 diff against the actual column
        # immediately before them, same row.
        charge_actual = [None]
        for i in range(1, len(ACTUAL_COLS)):
            charge_actual.append(f"={_cell(ecl_total_row, ACTUAL_COLS[i])}-{_cell(ecl_total_row, ACTUAL_COLS[i-1])}")
        charge_proj = [f"={_cell(ecl_total_row, col)}-{_prev(i, ecl_total_row)}" for i, col in enumerate(DATA_COLS)]
        _write_actual_row(ws, R, f"Provision Charge — {seg['name']}", charge_actual, units="(KES MM)")
        _write_formula_row(ws, R, f"Provision Charge — {seg['name']}", charge_proj, units="(KES MM)")
        R += 1
        blank_row(ws, R); R += 1

        M[f"{k}_gross_s1"] = s1_row
        M[f"{k}_gross_s2"] = s2_row
        M[f"{k}_gross_s3"] = s3_row
        M[f"{k}_gross_total"] = gross_total_row
        M[f"{k}_ecl_total"] = ecl_total_row
        M[f"{k}_net_total"] = net_row
        M[f"{k}_charge"] = charge_row
        agg_gross_rows.append(gross_total_row)
        agg_ecl_rows.append(ecl_total_row)
        agg_s3_gross_rows.append(s3_row)
        agg_charge_rows.append(charge_row)

    # Off-balance sheet
    write(ws, R, LABEL_COL, "Off-Balance-Sheet Exposure", bold=True, txt_color=NAVY); R += 1
    ob_row = R
    ob_actual = [_actual(config, y, "off_balance", "gross") for y in ay]
    ob_proj = [f"={_prev(i, ob_row)}*(1+{_assum_ref(A, 'ob_growth')})" for i, c in enumerate(DATA_COLS)]
    _write_actual_row(ws, R, "Off-Balance-Sheet Balance", ob_actual, units="(KES MM)")
    _write_formula_row(ws, R, "Off-Balance-Sheet Balance", ob_proj, units="(KES MM)")
    R += 1
    ob_rwa_row = R
    ob_rwa_actual = [f"={_cell(ob_row, c)}*{_assum_ref(A, 'ob_ccf')}*{_assum_ref(A, 'ob_risk_weight')}" for c in ACTUAL_COLS]
    ob_rwa_proj = [f"={_cell(ob_row, c)}*{_assum_ref(A, 'ob_ccf')}*{_assum_ref(A, 'ob_risk_weight')}" for c in DATA_COLS]
    _write_actual_row(ws, R, "Off-Balance-Sheet RWA", ob_rwa_actual, units="(KES MM)")
    _write_formula_row(ws, R, "Off-Balance-Sheet RWA", ob_rwa_proj, units="(KES MM)")
    R += 1
    blank_row(ws, R); R += 1
    M["ob_balance"] = ob_row
    M["ob_rwa"] = ob_rwa_row

    # Aggregate
    section_header(ws, R, "Loan Book — Aggregate"); R += 1
    agg_gross_row = R
    total_row(ws, R, "Total Gross Loans", [_add_rows_f(agg_gross_rows, c) for c in ACTUAL_COLS], ACTUAL_COLS, label_col=LABEL_COL)
    total_row(ws, R, "Total Gross Loans", [_add_rows_f(agg_gross_rows, c) for c in DATA_COLS], DATA_COLS, label_col=LABEL_COL)
    R += 1
    agg_ecl_row = R
    total_row(ws, R, "Total ECL Allowance", [_add_rows_f(agg_ecl_rows, c) for c in ACTUAL_COLS], ACTUAL_COLS, label_col=LABEL_COL)
    total_row(ws, R, "Total ECL Allowance", [_add_rows_f(agg_ecl_rows, c) for c in DATA_COLS], DATA_COLS, label_col=LABEL_COL)
    R += 1
    agg_net_row = R
    _write_actual_row(ws, R, "Total Net Loans", [_sub_f(agg_gross_row, agg_ecl_row, c) for c in ACTUAL_COLS], bold=True)
    _write_formula_row(ws, R, "Total Net Loans", [_sub_f(agg_gross_row, agg_ecl_row, c) for c in DATA_COLS], bold=True)
    R += 1
    agg_s3_row = R
    _write_actual_row(ws, R, "Total Stage 3 (NPL) Gross", [_add_rows_f(agg_s3_gross_rows, c) for c in ACTUAL_COLS], units="(KES MM)")
    _write_formula_row(ws, R, "Total Stage 3 (NPL) Gross", [_add_rows_f(agg_s3_gross_rows, c) for c in DATA_COLS], units="(KES MM)")
    R += 1
    npl_ratio_row = R
    _write_actual_row(ws, R, "NPL Ratio", [_ratio_f(agg_s3_row, agg_gross_row, c) for c in ACTUAL_COLS], fmt='0.0%')
    _write_formula_row(ws, R, "NPL Ratio", [_ratio_f(agg_s3_row, agg_gross_row, c) for c in DATA_COLS], fmt='0.0%')
    R += 1
    agg_charge_row = R
    # First actual year (2023) has no prior-year ECL total to diff against (see per-segment
    # charge rows above), so its aggregate is blank too — total_row skips None values.
    charge_agg_actual = [None] + [_add_rows_f(agg_charge_rows, c) for c in ACTUAL_COLS[1:]]
    total_row(ws, R, "Total Provision Charge", charge_agg_actual, ACTUAL_COLS, label_col=LABEL_COL)
    total_row(ws, R, "Total Provision Charge", [_add_rows_f(agg_charge_rows, c) for c in DATA_COLS], DATA_COLS, label_col=LABEL_COL)
    R += 1
    blank_row(ws, R, 8); R += 1

    M["agg_gross_total"] = agg_gross_row
    M["agg_ecl_total"] = agg_ecl_row
    M["agg_net_total"] = agg_net_row
    M["agg_s3_gross"] = agg_s3_row
    M["npl_ratio"] = npl_ratio_row
    M["agg_charge_total"] = agg_charge_row

    R = _build_sector_concentration_section(ws, config, R)

    return R


def _build_sector_concentration_section(ws, config, R):
    """Loan Book Concentration — Sector Detail (Actuals only, disclosed). No CBK sector
    -concentration ceiling is disclosed anywhere in Family Bank's own filings (confirmed via
    targeted search) — this shows the real disclosed sector breakdown for context, not a
    compliance check against a limit that doesn't exist in the disclosure."""
    section_header(ws, R, "Loan Book Concentration — Sector Detail (Actuals, disclosed)"); R += 1
    write(ws, R, LABEL_COL,
          "Family Bank changed its sector classification scheme between FY2023 (7 categories) "
          "and FY2024/FY2025 (10 categories, FY2024 restated into the new scheme in the "
          "FY2025 report) — shown as two separate tables rather than forced into one. No CBK "
          "sector-concentration limit is disclosed anywhere to check this against.",
          italic=True, txt_color=MID_GRAY, size=9)
    R += 2

    sectors_10cat = [
        ("agriculture", "Agriculture"), ("building_and_construction", "Building & Construction"),
        ("energy_and_water", "Energy & Water"), ("finance_and_insurance", "Finance & Insurance Services"),
        ("manufacturing", "Manufacturing"), ("personal_household", "Personal/Household"),
        ("real_estate", "Real Estate"), ("tourism_restaurant_hotels", "Tourism, Restaurant & Hotels"),
        ("trade", "Trade"), ("transport_and_communication", "Transport & Communication"),
    ]
    sc10 = config.SECTOR_CONCENTRATION_10CAT
    write(ws, R, LABEL_COL, "10-Category Scheme (2023 not available in this scheme)", bold=True, txt_color=NAVY)
    R += 1
    _linked_year_header_row(ws, R, ACTUAL_COLS, label_col=LABEL_COL); R += 1
    sector10_rows = []
    for key, label in sectors_10cat:
        vals = [None, sc10[2024][key], sc10[2025][key]]
        _write_actual_row(ws, R, label, vals, units="(KES MM)")
        sector10_rows.append(R)
        R += 1
    total10_row = R
    total_actual = [None] + [_add_rows_f(sector10_rows, c) for c in ACTUAL_COLS[1:]]
    total_row(ws, R, "Total", total_actual, ACTUAL_COLS, label_col=LABEL_COL)
    R += 1
    for row, (key, label) in zip(sector10_rows, sectors_10cat):
        pct_formulas = [None, _ratio_f(row, total10_row, ACTUAL_COLS[1]), _ratio_f(row, total10_row, ACTUAL_COLS[2])]
        _write_actual_row(ws, R, f"  % of Total — {label}", pct_formulas, fmt='0.0%')
        R += 1
    R += 1
    blank_row(ws, R, 8); R += 1

    sectors_7cat = [
        ("manufacturing", "Manufacturing"), ("wholesale_and_retail", "Wholesale and Retail"),
        ("transport_and_communication", "Transport and Communication"), ("agriculture", "Agriculture"),
        ("business_services", "Business Services"), ("building_and_construction", "Building and Construction"),
        ("other", "Other"),
    ]
    sc7 = config.SECTOR_CONCENTRATION_7CAT_2023
    write(ws, R, LABEL_COL, "FY2023 — Prior 7-Category Scheme (not directly comparable to above)",
          bold=True, txt_color=NAVY)
    R += 1
    sector7_rows = []
    for key, label in sectors_7cat:
        vals = [sc7[key], None, None]
        _write_actual_row(ws, R, label, vals, units="(KES MM)")
        sector7_rows.append(R)
        R += 1
    total7_row = R
    total_actual_7 = [_add_rows_f(sector7_rows, ACTUAL_COLS[0]), None, None]
    total_row(ws, R, "Total", total_actual_7, ACTUAL_COLS, label_col=LABEL_COL)
    R += 1
    blank_row(ws, R, 8); R += 1

    return R


# ─────────────────────────────────────────────
# MODEL SHEET — Schedule 2/3/4-6: Securities, Deposits, Interest Income/Expense, NII
# ─────────────────────────────────────────────

def _build_funding_section(ws, config, A, M, R):
    section_header(ws, R, "SECURITIES, DEPOSITS & NET INTEREST INCOME",
                    bg=NAVY, txt_color=WHITE); R += 1
    _linked_year_header_row(ws, R, _all_cols(), label_col=LABEL_COL); R += 1
    blank_row(ws, R); R += 1
    ay = config.ACTUAL_YEARS

    write(ws, R, LABEL_COL, "Investment Securities", bold=True, txt_color=NAVY); R += 1
    sec_row = R
    sec_actual = [_actual(config, y, "securities_amortised") + _actual(config, y, "securities_fvoci")
                  for y in ay]  # [DISCLOSED] real totals (amortised cost + FVOCI)
    sec_proj = [f"={_prev(i, sec_row)}*(1+{_assum_ref(A, 'sec_growth')})" for i, c in enumerate(DATA_COLS)]
    _write_actual_row(ws, R, "Government Securities Balance", sec_actual, units="(KES MM)")
    _write_formula_row(ws, R, "Government Securities Balance", sec_proj, units="(KES MM)")
    R += 1
    sec_income_row = R
    # Actual years: left blank. The bank discloses total interest income, not a
    # loan-vs-securities split — applying the forward yield assumption to actual balances
    # would produce a number that doesn't match the real disclosed total, so it's not
    # fabricated here. Projected years: live formula, balance x assumed yield.
    _write_actual_row(ws, R, "Securities Interest Income", [None] * len(ACTUAL_COLS), units="(KES MM)")
    _write_formula_row(ws, R, "Securities Interest Income",
                        [f"={_cell(sec_row, c)}*{_assum_ref(A, 'sec_yield_rate')}" for c in DATA_COLS],
                        units="(KES MM)")
    R += 1
    blank_row(ws, R); R += 1
    M["sec_balance"] = sec_row
    M["sec_income"] = sec_income_row

    write(ws, R, LABEL_COL, "Deposits / Funding", bold=True, txt_color=NAVY); R += 1
    dep_opening_total = sum(d["opening"] for d in config.DEPOSIT_TYPES)
    dep_balance_rows, dep_expense_rows = [], []
    for dep in config.DEPOSIT_TYPES:
        k = dep["key"]
        proportion = dep["opening"] / dep_opening_total  # [MODELED] allocation, held
        # constant across actual years too — only the aggregate deposit total is disclosed
        bal_row = R
        bal_actual = [f"={proportion:.6f}*{_actual(config, y, 'deposits_total')}" for y in ay]
        bal_proj = [f"={_prev(i, bal_row)}*(1+{_assum_ref(A, f'{k}_growth')})" for i, c in enumerate(DATA_COLS)]
        _write_actual_row(ws, R, f"{dep['name']} — Balance", bal_actual, units="(KES MM)",
                           alt_idx=len(dep_balance_rows))
        _write_formula_row(ws, R, f"{dep['name']} — Balance", bal_proj, units="(KES MM)",
                            alt_idx=len(dep_balance_rows))
        R += 1
        exp_row = R
        # Actual years: left blank, same reasoning as Securities Interest Income above —
        # only the aggregate interest expense is disclosed, not a per-deposit-type split.
        exp_actual = [None] * len(ACTUAL_COLS)
        exp_proj = [f"={_cell(bal_row, c)}*{_assum_ref(A, f'{k}_cost_rate')}" for c in DATA_COLS]
        _write_actual_row(ws, R, f"{dep['name']} — Interest Expense", exp_actual, units="(KES MM)",
                           alt_idx=len(dep_balance_rows) + 1)
        _write_formula_row(ws, R, f"{dep['name']} — Interest Expense", exp_proj, units="(KES MM)",
                            alt_idx=len(dep_balance_rows) + 1)
        R += 1
        M[f"{k}_balance"] = bal_row
        M[f"{k}_expense"] = exp_row
        dep_balance_rows.append(bal_row)
        dep_expense_rows.append(exp_row)

    dep_total_row = R
    total_row(ws, R, "Total Deposits", [_add_rows_f(dep_balance_rows, c) for c in ACTUAL_COLS], ACTUAL_COLS, label_col=LABEL_COL)
    total_row(ws, R, "Total Deposits", [_add_rows_f(dep_balance_rows, c) for c in DATA_COLS], DATA_COLS, label_col=LABEL_COL)
    R += 1
    dep_exp_total_row = R
    # Actual years: hardcoded real disclosed interest expense (not a sum of the per-type
    # rows above, which are blank for actual years — see note above).
    dep_exp_actual = [_actual(config, y, "interest_expense") for y in ay]
    total_row(ws, R, "Total Interest Expense", dep_exp_actual, ACTUAL_COLS, label_col=LABEL_COL)
    total_row(ws, R, "Total Interest Expense", [_add_rows_f(dep_expense_rows, c) for c in DATA_COLS], DATA_COLS, label_col=LABEL_COL)
    R += 1
    blank_row(ws, R); R += 1
    M["dep_total"] = dep_total_row
    M["dep_expense_total"] = dep_exp_total_row

    write(ws, R, LABEL_COL, "Interest Income & Net Interest Income", bold=True, txt_color=NAVY); R += 1
    loan_income_row = R

    def _loan_income_formula(col):
        terms = []
        for seg in config.LOAN_SEGMENTS:
            k = seg["key"]
            terms.append(f"{_cell(M[f'{k}_gross_total'], col)}*{_assum_ref(A, f'{k}_yield_rate')}")
        return "=" + "+".join(terms)

    # Actual years: left blank, same reasoning as Securities Interest Income — the
    # loan-vs-securities split of interest income isn't disclosed.
    _write_actual_row(ws, R, "Loan Interest Income", [None] * len(ACTUAL_COLS), units="(KES MM)")
    _write_formula_row(ws, R, "Loan Interest Income", [_loan_income_formula(c) for c in DATA_COLS], units="(KES MM)")
    R += 1

    total_interest_income_row = R
    # Actual years: hardcoded real disclosed total interest income.
    total_interest_actual = [_actual(config, y, "interest_income") for y in ay]
    _write_actual_row(ws, R, "Total Interest Income", total_interest_actual, bold=True, units="(KES MM)")
    _write_formula_row(ws, R, "Total Interest Income",
                        [f"={_cell(loan_income_row, c)}+{_cell(sec_income_row, c)}" for c in DATA_COLS],
                        bold=True, units="(KES MM)")
    R += 1

    nii_row = R
    total_row(ws, R, "Net Interest Income (NII)",
              [_sub_f(total_interest_income_row, dep_exp_total_row, c) for c in ACTUAL_COLS], ACTUAL_COLS, label_col=LABEL_COL)
    total_row(ws, R, "Net Interest Income (NII)",
              [_sub_f(total_interest_income_row, dep_exp_total_row, c) for c in DATA_COLS], DATA_COLS, label_col=LABEL_COL)
    R += 1
    blank_row(ws, R, 8); R += 1

    M["loan_income"] = loan_income_row
    M["total_interest_income"] = total_interest_income_row
    M["nii"] = nii_row

    return R


# ─────────────────────────────────────────────
# MODEL SHEET — Schedule 7/8/10: Non-Interest Income, Opex, Income Statement
# ─────────────────────────────────────────────

def _build_income_statement_section(ws, config, A, M, R):
    section_header(ws, R, "INCOME STATEMENT", bg=NAVY, txt_color=WHITE); R += 1
    _linked_year_header_row(ws, R, _all_cols(), label_col=LABEL_COL); R += 1
    blank_row(ws, R); R += 1
    ay = config.ACTUAL_YEARS

    non_int_row = R
    # Actual years: hardcoded real disclosed non-interest income (fees+investment+
    # trading+other income, already summed in ACTUALS). Projected: modeled ratio of deposits.
    non_int_actual = [_actual(config, y, "non_interest_income") for y in ay]
    _write_actual_row(ws, R, "Non-Interest Income", non_int_actual, units="(KES MM)")
    _write_formula_row(ws, R, "Non-Interest Income",
                        [f"={_cell(M['dep_total'], c)}*{_assum_ref(A, 'nii_rate')}" for c in DATA_COLS],
                        units="(KES MM)")
    R += 1
    blank_row(ws, R); R += 1
    M["non_interest_income"] = non_int_row

    write(ws, R, LABEL_COL, "Operating Expenses", bold=True, txt_color=NAVY); R += 1
    opex_rows = []
    for i, item in enumerate(config.OPEX_ITEMS):
        k = item["key"]
        row = R
        # Actual years: category-level opex isn't disclosed (see Total Operating Expenses
        # below for the real hardcoded aggregate) — left blank.
        proj_formulas = [f"={_assum_ref(A, f'opex_{k}_y1')}*(1+{_assum_ref(A, f'opex_{k}_esc')})^{yi}"
                         for yi, c in enumerate(DATA_COLS)]
        _write_actual_row(ws, R, item["name"], [None] * len(ACTUAL_COLS), units="(KES MM)", alt_idx=i)
        _write_formula_row(ws, R, item["name"], proj_formulas, units="(KES MM)", alt_idx=i)
        opex_rows.append(row)
        R += 1
    opex_total_row = R
    opex_actual = [_actual(config, y, "opex") for y in ay]
    total_row(ws, R, "Total Operating Expenses", opex_actual, ACTUAL_COLS, label_col=LABEL_COL)
    total_row(ws, R, "Total Operating Expenses", [_add_rows_f(opex_rows, c) for c in DATA_COLS],
              DATA_COLS, label_col=LABEL_COL)
    R += 1
    blank_row(ws, R); R += 1
    M["opex_total"] = opex_total_row

    pbt_row = R
    # Actual years: hardcoded real disclosed PBT (deriving it from NII+non-interest-opex
    # -provisions would miss the fact that 2023's provision charge is blank — see the loan
    # book section — so the real figure is used directly rather than an incomplete formula).
    pbt_actual = [_actual(config, y, "pbt") for y in ay]
    total_row(ws, R, "Profit Before Tax (PBT)", pbt_actual, ACTUAL_COLS, label_col=LABEL_COL, bg=TOTAL_FILL)
    total_row(ws, R, "Profit Before Tax (PBT)",
              [f"={_cell(M['nii'], c)}+{_cell(non_int_row, c)}-{_cell(opex_total_row, c)}"
               f"-{_cell(M['agg_charge_total'], c)}" for c in DATA_COLS],
              DATA_COLS, label_col=LABEL_COL, bg=TOTAL_FILL)
    R += 1
    tax_row = R
    tax_actual = [_actual(config, y, "tax") for y in ay]
    _write_actual_row(ws, R, "Income Tax", tax_actual, units="(KES MM)")
    _write_formula_row(ws, R, "Income Tax",
                        [f"=MAX(0,{_cell(pbt_row, c)}*{_assum_ref(A, 'tax_rate')})" for c in DATA_COLS],
                        units="(KES MM)")
    R += 1
    pat_row = R
    # PAT = PBT - Tax as a formula in both regions — for actual years both operands are
    # themselves hardcoded real facts, so the formula ties to the real disclosed PAT exactly.
    total_row(ws, R, "NET PROFIT AFTER TAX (PAT)", [_sub_f(pbt_row, tax_row, c) for c in ACTUAL_COLS],
              ACTUAL_COLS, label_col=LABEL_COL, bg=NAVY, txt_color=WHITE)
    total_row(ws, R, "NET PROFIT AFTER TAX (PAT)", [_sub_f(pbt_row, tax_row, c) for c in DATA_COLS],
              DATA_COLS, label_col=LABEL_COL, bg=NAVY, txt_color=WHITE)
    R += 1
    div_row = R
    # Dividends Paid: illustrative at the modeled payout ratio in both regions (real
    # disclosed dividend timing/amount doesn't cleanly map to a single "paid this year"
    # figure across proposed-vs-paid distinctions — see research_output.md) — shown as a
    # formula (payout ratio x PAT) throughout, not presented as a disclosed fact for actuals.
    div_formula = lambda c: f"={_cell(pat_row, c)}*{_assum_ref(A, 'dividend_payout')}"
    _write_actual_row(ws, R, "Dividends Paid (illustrative, modeled payout ratio)",
                       [div_formula(c) for c in ACTUAL_COLS], units="(KES MM)")
    _write_formula_row(ws, R, "Dividends Paid (illustrative, modeled payout ratio)",
                        [div_formula(c) for c in DATA_COLS], units="(KES MM)")
    R += 1
    blank_row(ws, R, 8); R += 1

    M["pbt"] = pbt_row
    M["tax"] = tax_row
    M["pat"] = pat_row
    M["dividends"] = div_row

    return R


# ─────────────────────────────────────────────
# MODEL SHEET — Schedule 11/12: Cash Flow & Balance Sheet
# ─────────────────────────────────────────────

def _build_cash_flow_balance_sheet_section(ws, config, A, M, R):
    section_header(ws, R, "CASH FLOW STATEMENT", bg=NAVY, txt_color=WHITE); R += 1
    _linked_year_header_row(ws, R, _all_cols(), label_col=LABEL_COL); R += 1
    blank_row(ws, R); R += 1
    ay = config.ACTUAL_YEARS

    # PP&E roll-forward (projected years only need D&A/Capex; actual years hardcode the
    # real disclosed PP&E balance directly and don't need the roll-forward mechanics).
    ppe_row = R
    da_row = R + 1
    capex_row = R + 2
    ppe_actual = [_actual(config, y, "ppe") for y in ay]
    ppe_proj, da_proj, capex_proj = [], [], []
    for i, col in enumerate(DATA_COLS):
        prev_ppe = _prev(i, ppe_row)
        da_proj.append(f"={prev_ppe}*{_assum_ref(A, 'da_rate')}")
        capex_proj.append(f"={prev_ppe}*{_assum_ref(A, 'capex_rate')}")
        ppe_proj.append(f"={prev_ppe}+{_cell(capex_row, col)}-{_cell(da_row, col)}")
    _write_actual_row(ws, ppe_row, "Net PP&E", ppe_actual, units="(KES MM)")
    _write_formula_row(ws, ppe_row, "Net PP&E", ppe_proj, units="(KES MM)")
    _write_actual_row(ws, da_row, "Depreciation & Amortisation", [None] * len(ay), units="(KES MM)")
    _write_formula_row(ws, da_row, "Depreciation & Amortisation", da_proj, units="(KES MM)")
    _write_actual_row(ws, capex_row, "Capital Expenditure", [None] * len(ay), units="(KES MM)")
    _write_formula_row(ws, capex_row, "Capital Expenditure", capex_proj, units="(KES MM)")
    R += 3
    blank_row(ws, R); R += 1
    M["ppe"] = ppe_row; M["da"] = da_row; M["capex"] = capex_row

    # Other Assets / Other Liabilities — granular real disclosed line items (KES MM).
    # None of these have a disclosed forward-looking driver, so projected years grow each
    # independently at the generic OTHER_BS_ITEMS_GROWTH_RATE (see config.py). Built here
    # (ahead of the Cash Flow Statement) so the OCF working-capital delta below can
    # reference the resulting aggregate rows, same position/role the old single blended
    # "Other Assets"/"Other Liabilities" rows occupied — each individual line is shown
    # again, cross-referenced, under its natural home in the BALANCE SHEET section further
    # down.
    write(ws, R, LABEL_COL, "Other Assets & Other Liabilities — Detail", bold=True, txt_color=NAVY); R += 1

    def _other_item_row(label, key, alt_idx):
        nonlocal R
        row = R
        actual_vals = [_actual(config, y, key) for y in ay]
        proj_vals = [f"={_prev(i, row)}*(1+{_assum_ref(A, 'other_bs_items_growth')})" for i in range(len(DATA_COLS))]
        _write_actual_row(ws, row, label, actual_vals, units="(KES MM)", alt_idx=alt_idx)
        _write_formula_row(ws, row, label, proj_vals, units="(KES MM)", alt_idx=alt_idx)
        R += 1
        return row

    other_asset_item_rows = [
        _other_item_row("Investment in Subsidiaries", "investment_in_subsidiary", 0),
        _other_item_row("Investment Properties", "investment_properties", 1),
        _other_item_row("Intangible Assets", "intangibles", 0),
        _other_item_row("Right-of-Use Assets", "rou_assets", 1),
        _other_item_row("Prepaid Operating Leases", "prepaid_leases", 0),
        _other_item_row("Current Income Tax Asset", "current_tax_asset", 1),
        _other_item_row("Deferred Income Tax Asset", "deferred_tax_asset", 0),
        _other_item_row("Other Assets (residual)", "other_assets_residual", 1),
    ]
    other_assets_row = R
    total_row(ws, R, "Total Other Assets", [_add_rows_f(other_asset_item_rows, c) for c in ACTUAL_COLS], ACTUAL_COLS, label_col=LABEL_COL)
    total_row(ws, R, "Total Other Assets", [_add_rows_f(other_asset_item_rows, c) for c in DATA_COLS], DATA_COLS, label_col=LABEL_COL)
    R += 1
    blank_row(ws, R); R += 1
    M["other_assets"] = other_assets_row

    due_to_banks_row = _other_item_row("Balances Due to Banking Institutions", "due_to_banks", 0)
    st_cbk_row = R
    # Real FY2023-only line (repaid by FY2024) — held at 0 for projected years since it's
    # genuinely gone, not just undisclosed at this granularity (unlike the other items,
    # which don't grow generically here because there's nothing to grow).
    _write_actual_row(ws, R, "Short-Term CBK Borrowings", [_actual(config, y, "st_cbk_borrowings") for y in ay], units="(KES MM)", alt_idx=1)
    _write_formula_row(ws, R, "Short-Term CBK Borrowings", [0.0] * len(DATA_COLS), units="(KES MM)", alt_idx=1)
    R += 1
    other_liab_item_rows = [
        due_to_banks_row, st_cbk_row,
        _other_item_row("Accruals & Other Provisions", "accruals_provisions", 0),
        _other_item_row("Other Liabilities (residual)", "other_liabilities_residual", 1),
        _other_item_row("Borrowings", "borrowings", 0),
        _other_item_row("Lease Liabilities", "lease_liabilities", 1),
        _other_item_row("Current Income Tax Liability", "current_tax_liability", 0),
    ]
    other_liab_row = R
    total_row(ws, R, "Total Other Liabilities", [_add_rows_f(other_liab_item_rows, c) for c in ACTUAL_COLS], ACTUAL_COLS, label_col=LABEL_COL)
    total_row(ws, R, "Total Other Liabilities", [_add_rows_f(other_liab_item_rows, c) for c in DATA_COLS], DATA_COLS, label_col=LABEL_COL)
    R += 1
    blank_row(ws, R); R += 1
    M["other_liab"] = other_liab_row

    # Cash flow: actual years hardcode the real disclosed statement (OCF/ICF/FCF/ending
    # cash are all genuine facts, not derived — see research_output.md for sourcing,
    # including the FY2024 restatement). Projected years keep the indirect-method
    # derivation, now referencing the actual columns directly for the first period's delta
    # (via _prev()) instead of reconstructing an "opening" expression from Assumptions cells.
    write(ws, R, LABEL_COL, "Operating / Investing / Financing Activities", bold=True, txt_color=NAVY); R += 1
    ocf_row = R
    ocf_actual = [_actual(config, y, "ocf") for y in ay]
    ocf_proj = []
    for i, col in enumerate(DATA_COLS):
        d_gross = f"({_cell(M['agg_gross_total'], col)}-{_prev(i, M['agg_gross_total'])})"
        d_sec = f"({_cell(M['sec_balance'], col)}-{_prev(i, M['sec_balance'])})"
        d_other_assets = f"({_cell(other_assets_row, col)}-{_prev(i, other_assets_row)})"
        d_dep = f"({_cell(M['dep_total'], col)}-{_prev(i, M['dep_total'])})"
        d_other_liab = f"({_cell(other_liab_row, col)}-{_prev(i, other_liab_row)})"
        ocf_proj.append(
            f"={_cell(M['pat'], col)}+{_cell(da_row, col)}+{_cell(M['agg_charge_total'], col)}"
            f"-{d_gross}-{d_sec}-{d_other_assets}+{d_dep}+{d_other_liab}")
    _write_actual_row(ws, R, "Operating Cash Flow", ocf_actual, bold=True, units="(KES MM)")
    _write_formula_row(ws, R, "Operating Cash Flow", ocf_proj, bold=True, units="(KES MM)")
    R += 1

    icf_row = R
    icf_actual = [_actual(config, y, "icf") for y in ay]
    _write_actual_row(ws, R, "Investing Cash Flow (Capex)", icf_actual, units="(KES MM)")
    _write_formula_row(ws, R, "Investing Cash Flow (Capex)",
                        [f"=-{_cell(capex_row, c)}" for c in DATA_COLS], units="(KES MM)")
    R += 1

    fcf_row = R
    fcf_actual = [_actual(config, y, "fcf") for y in ay]
    _write_actual_row(ws, R, "Financing Cash Flow (Dividends)", fcf_actual, units="(KES MM)")
    _write_formula_row(ws, R, "Financing Cash Flow (Dividends)",
                        [f"=-{_cell(M['dividends'], c)}" for c in DATA_COLS], units="(KES MM)")
    R += 1

    net_change_row = R
    net_change_actual = [f"={_cell(ocf_row, c)}+{_cell(icf_row, c)}+{_cell(fcf_row, c)}" for c in ACTUAL_COLS]
    total_row(ws, R, "Net Change in Cash", net_change_actual, ACTUAL_COLS, label_col=LABEL_COL)
    total_row(ws, R, "Net Change in Cash",
              [f"={_cell(ocf_row, c)}+{_cell(icf_row, c)}+{_cell(fcf_row, c)}" for c in DATA_COLS],
              DATA_COLS, label_col=LABEL_COL)
    R += 1

    cash_row = R
    # Actual years: hardcoded real disclosed ending cash-and-equivalents (a narrower
    # definition than OPENING_CASH's cash+due-from-banks bucket used elsewhere — see
    # research_output.md — so this row is real fact, not derived from the BS cash lines).
    cash_actual = [_actual(config, y, "cash_end") for y in ay]
    cash_proj = [f"={_prev(i, cash_row)}+{_cell(net_change_row, c)}" for i, c in enumerate(DATA_COLS)]
    total_row(ws, R, "Ending Cash Balance", cash_actual, ACTUAL_COLS, label_col=LABEL_COL, bg=NAVY, txt_color=WHITE)
    total_row(ws, R, "Ending Cash Balance", cash_proj, DATA_COLS, label_col=LABEL_COL, bg=NAVY, txt_color=WHITE)
    R += 1
    blank_row(ws, R, 8); R += 1

    M["ocf"] = ocf_row; M["icf"] = icf_row; M["fcf"] = fcf_row
    M["net_change"] = net_change_row; M["cash"] = cash_row

    # ── Balance Sheet ──
    # Every row below is a real disclosed line item (Family Bank's own Bank-column
    # Balance Sheet), not a blended bucket — actual years hardcode the real fact;
    # projected years use whichever mechanic already exists for that item (Cash Flow
    # roll-forward for cash, INVESTMENT_SECURITIES growth for securities, the Loan Book
    # schedule for net loans, the PP&E roll-forward, or a cross-reference to the granular
    # detail block above), split into presentational sub-lines via the FY2025 actual mix
    # where a single existing aggregate covers more than one disclosed line.
    section_header(ws, R, "BALANCE SHEET", bg=NAVY, txt_color=WHITE); R += 1
    _linked_year_header_row(ws, R, _all_cols(), label_col=LABEL_COL); R += 1
    blank_row(ws, R); R += 1

    section_header(ws, R, "ASSETS", bg=LIGHT_BLUE, txt_color=DARK); R += 1

    # Cash split: Cash Flow's own `cash_row` stays the single driver for projected years
    # (preserves the Cash-Flow-to-Balance-Sheet linkage); split into its 2 disclosed lines
    # via the FY2025 actual mix rather than growing each independently, which would
    # disconnect the split from the CF mechanic and risk the Balance Sheet Check.
    cbk_pct, due_from_pct = 0.554516, 0.445484
    cash_cbk_row = R
    _write_actual_row(ws, R, "Cash and Balances with CBK", [_actual(config, y, "cash_cbk") for y in ay], units="(KES MM)")
    _write_formula_row(ws, R, "Cash and Balances with CBK", [f"={_cell(cash_row, c)}*{cbk_pct}" for c in DATA_COLS], units="(KES MM)")
    R += 1
    due_from_banks_row = R
    _write_actual_row(ws, R, "Balances Due from Banking Institutions", [_actual(config, y, "due_from_banks") for y in ay], units="(KES MM)")
    _write_formula_row(ws, R, "Balances Due from Banking Institutions", [f"={_cell(cash_row, c)}*{due_from_pct}" for c in DATA_COLS], units="(KES MM)")
    R += 1

    # Securities split: same reasoning, split off M['sec_balance'] (INVESTMENT_SECURITIES
    # growth mechanic, unchanged) via the FY2025 actual mix.
    amort_pct, fvoci_pct = 0.536160, 0.463840
    sec_amort_row = R
    _write_actual_row(ws, R, "Government Securities — Amortised Cost", [_actual(config, y, "securities_amortised") for y in ay], units="(KES MM)")
    _write_formula_row(ws, R, "Government Securities — Amortised Cost", [f"={_cell(M['sec_balance'], c)}*{amort_pct}" for c in DATA_COLS], units="(KES MM)")
    R += 1
    sec_fvoci_row = R
    _write_actual_row(ws, R, "Government Securities — FVOCI", [_actual(config, y, "securities_fvoci") for y in ay], units="(KES MM)")
    _write_formula_row(ws, R, "Government Securities — FVOCI", [f"={_cell(M['sec_balance'], c)}*{fvoci_pct}" for c in DATA_COLS], units="(KES MM)")
    R += 1

    net_loans_row = R
    _write_actual_row(ws, R, "Loans and Advances to Customers (net)", [_ref_f(M['agg_net_total'], c) for c in ACTUAL_COLS], units="(KES MM)")
    _write_formula_row(ws, R, "Loans and Advances to Customers (net)", [_ref_f(M['agg_net_total'], c) for c in DATA_COLS], units="(KES MM)")
    R += 1

    ppe_ref_row = R
    _write_actual_row(ws, R, "Property and Equipment", [_ref_f(ppe_row, c) for c in ACTUAL_COLS], units="(KES MM)")
    _write_formula_row(ws, R, "Property and Equipment", [_ref_f(ppe_row, c) for c in DATA_COLS], units="(KES MM)")
    R += 1

    other_assets_ref_row = R
    _write_actual_row(ws, R, "Other Assets (Investment in Subsidiaries, Investment Properties, "
                             "Intangibles, ROU Assets, Prepaid Leases, Tax Assets — see detail above)",
                       [_ref_f(other_assets_row, c) for c in ACTUAL_COLS], units="(KES MM)")
    _write_formula_row(ws, R, "Other Assets (Investment in Subsidiaries, Investment Properties, "
                              "Intangibles, ROU Assets, Prepaid Leases, Tax Assets — see detail above)",
                        [_ref_f(other_assets_row, c) for c in DATA_COLS], units="(KES MM)")
    R += 1
    blank_row(ws, R); R += 1

    total_assets_row = R
    asset_rows = [cash_cbk_row, due_from_banks_row, sec_amort_row, sec_fvoci_row,
                  net_loans_row, ppe_ref_row, other_assets_ref_row]
    total_row(ws, R, "TOTAL ASSETS", [_add_rows_f(asset_rows, c) for c in ACTUAL_COLS], ACTUAL_COLS, label_col=LABEL_COL, bg=NAVY, txt_color=WHITE)
    total_row(ws, R, "TOTAL ASSETS", [_add_rows_f(asset_rows, c) for c in DATA_COLS], DATA_COLS, label_col=LABEL_COL, bg=NAVY, txt_color=WHITE)
    R += 1
    blank_row(ws, R); R += 1

    section_header(ws, R, "LIABILITIES", bg=LIGHT_BLUE, txt_color=DARK); R += 1
    deposits_ref_row = R
    _write_actual_row(ws, R, "Customer Deposits", [_ref_f(M['dep_total'], c) for c in ACTUAL_COLS], units="(KES MM)")
    _write_formula_row(ws, R, "Customer Deposits", [_ref_f(M['dep_total'], c) for c in DATA_COLS], units="(KES MM)")
    R += 1
    other_liab_ref_row = R
    _write_actual_row(ws, R, "Other Liabilities (Due to Banks, Borrowings, Lease Liabilities, "
                             "Accruals & Provisions, Tax Liability — see detail above)",
                       [_ref_f(other_liab_row, c) for c in ACTUAL_COLS], units="(KES MM)")
    _write_formula_row(ws, R, "Other Liabilities (Due to Banks, Borrowings, Lease Liabilities, "
                              "Accruals & Provisions, Tax Liability — see detail above)",
                        [_ref_f(other_liab_row, c) for c in DATA_COLS], units="(KES MM)")
    R += 1
    blank_row(ws, R); R += 1

    total_liab_row = R
    liab_rows = [deposits_ref_row, other_liab_ref_row]
    total_row(ws, R, "TOTAL LIABILITIES", [_add_rows_f(liab_rows, c) for c in ACTUAL_COLS], ACTUAL_COLS, label_col=LABEL_COL)
    total_row(ws, R, "TOTAL LIABILITIES", [_add_rows_f(liab_rows, c) for c in DATA_COLS], DATA_COLS, label_col=LABEL_COL)
    R += 1
    blank_row(ws, R); R += 1

    section_header(ws, R, "SHAREHOLDERS' EQUITY", bg=LIGHT_BLUE, txt_color=DARK); R += 1
    # Layout is pre-planned so Retained Earnings' projected-year plug formula (below) can
    # reference Total Equity's own row before it's written — same row every period, so a
    # forward reference within the same column structure is fine.
    share_capital_row = R
    share_premium_row = R + 1
    revaluation_row = R + 2
    fv_reserve_row = R + 3
    statutory_reserve_row = R + 4
    proposed_div_row = R + 5
    retained_earnings_row = R + 6
    equity_row = R + 8  # + 1 blank row before the total

    _write_actual_row(ws, share_capital_row, "Share Capital", [_actual(config, y, "share_capital") for y in ay], units="(KES MM)")
    _write_formula_row(ws, share_capital_row, "Share Capital", [f"={_assum_ref(A, 'share_capital_opening')}" for _ in DATA_COLS], units="(KES MM)")
    _write_actual_row(ws, share_premium_row, "Share Premium", [_actual(config, y, "share_premium") for y in ay], units="(KES MM)")
    _write_formula_row(ws, share_premium_row, "Share Premium", [f"={_assum_ref(A, 'share_premium_opening')}" for _ in DATA_COLS], units="(KES MM)")

    def _grown_reserve_row(row, label, key, alt_idx):
        actual_vals = [_actual(config, y, key) for y in ay]
        proj_vals = [f"={_prev(i, row)}*(1+{_assum_ref(A, 'other_bs_items_growth')})" for i in range(len(DATA_COLS))]
        _write_actual_row(ws, row, label, actual_vals, units="(KES MM)", alt_idx=alt_idx)
        _write_formula_row(ws, row, label, proj_vals, units="(KES MM)", alt_idx=alt_idx)

    _grown_reserve_row(revaluation_row, "Revaluation Surplus", "revaluation_surplus", 0)
    _grown_reserve_row(fv_reserve_row, "Fair Value Reserve", "fair_value_reserve", 1)
    _grown_reserve_row(statutory_reserve_row, "Statutory Reserve", "statutory_reserve", 0)

    div_formula = lambda c: f"={_cell(M['pat'], c)}*{_assum_ref(A, 'dividend_payout')}"
    _write_actual_row(ws, proposed_div_row, "Proposed Dividends", [_actual(config, y, "proposed_dividends") for y in ay], units="(KES MM)", alt_idx=1)
    _write_formula_row(ws, proposed_div_row, "Proposed Dividends", [div_formula(c) for c in DATA_COLS], units="(KES MM)", alt_idx=1)

    # Retained Earnings: real disclosed fact for actual years. For projected years, it's
    # the residual/plug that preserves the exact pre-existing Total Equity roll-forward
    # (prior Total Equity + PAT − modeled dividends) while presenting the granular split
    # above — Total Equity's own mechanic doesn't change, only how it's broken out.
    re_actual = [_actual(config, y, "retained_earnings") for y in ay]
    re_proj = []
    for i, col in enumerate(DATA_COLS):
        old_mechanic_equity = f"({_prev(i, equity_row)}+{_cell(M['pat'], col)}-{_cell(M['dividends'], col)})"
        re_proj.append(
            f"={old_mechanic_equity}-{_cell(share_capital_row, col)}-{_cell(share_premium_row, col)}"
            f"-{_cell(revaluation_row, col)}-{_cell(fv_reserve_row, col)}-{_cell(statutory_reserve_row, col)}"
            f"-{_cell(proposed_div_row, col)}")
    _write_actual_row(ws, retained_earnings_row, "Retained Earnings", re_actual, units="(KES MM)")
    _write_formula_row(ws, retained_earnings_row, "Retained Earnings", re_proj, units="(KES MM)")
    M["retained_earnings"] = retained_earnings_row

    R = retained_earnings_row + 1
    blank_row(ws, R); R += 1
    assert R == equity_row, f"equity_row layout drifted: expected {equity_row}, got {R}"

    equity_component_rows = [share_capital_row, share_premium_row, revaluation_row, fv_reserve_row,
                              statutory_reserve_row, proposed_div_row, retained_earnings_row]
    total_row(ws, R, "TOTAL SHAREHOLDERS' EQUITY", [_add_rows_f(equity_component_rows, c) for c in ACTUAL_COLS], ACTUAL_COLS, label_col=LABEL_COL)
    total_row(ws, R, "TOTAL SHAREHOLDERS' EQUITY", [_add_rows_f(equity_component_rows, c) for c in DATA_COLS], DATA_COLS, label_col=LABEL_COL)
    R += 1
    blank_row(ws, R); R += 1

    check_row = R
    check_actual = [f"={_cell(total_assets_row, c)}-{_cell(total_liab_row, c)}-{_cell(equity_row, c)}" for c in ACTUAL_COLS]
    check_proj = [f"={_cell(total_assets_row, c)}-{_cell(total_liab_row, c)}-{_cell(equity_row, c)}" for c in DATA_COLS]
    _write_actual_row(ws, R, "Balance Sheet Check (Assets − Liab − Equity)", check_actual, bold=True, fmt='#,##0.000000')
    _write_formula_row(ws, R, "Balance Sheet Check (Assets − Liab − Equity)", check_proj, bold=True, fmt='#,##0.000000')
    R += 1
    blank_row(ws, R, 8); R += 1

    M["total_assets"] = total_assets_row
    M["total_liab"] = total_liab_row
    M["total_equity"] = equity_row
    M["bs_check"] = check_row

    return R


# ─────────────────────────────────────────────
# MODEL SHEET — Schedule 13/14: Capital Adequacy & Liquidity
# ─────────────────────────────────────────────

def _build_capital_liquidity_section(ws, config, A, M, R):
    section_header(ws, R, "CAPITAL ADEQUACY & LIQUIDITY", bg=NAVY, txt_color=WHITE); R += 1
    _linked_year_header_row(ws, R, _all_cols(), label_col=LABEL_COL); R += 1
    blank_row(ws, R); R += 1
    ay = config.ACTUAL_YEARS
    rc = config.REGULATORY_CAPITAL

    def _loan_rwa_formula(col):
        terms = []
        for seg in config.LOAN_SEGMENTS:
            k = seg["key"]
            terms.append(f"{_cell(M[f'{k}_gross_total'], col)}*{_assum_ref(A, f'{k}_risk_weight')}")
        return "=" + "+".join(terms)

    write(ws, R, LABEL_COL, "Risk-Weighted Assets", bold=True, txt_color=NAVY); R += 1
    loan_rwa_row = R
    _write_actual_row(ws, R, "Loan Book RWA (modeled, own risk-weight assumptions)",
                       [_loan_rwa_formula(c) for c in ACTUAL_COLS], units="(KES MM)")
    _write_formula_row(ws, R, "Loan Book RWA (modeled, own risk-weight assumptions)",
                        [_loan_rwa_formula(c) for c in DATA_COLS], units="(KES MM)")
    R += 1
    ob_rwa_note_row = R
    _write_actual_row(ws, R, "Off-Balance-Sheet RWA (modeled)", [f"={_cell(M['ob_rwa'], c)}" for c in ACTUAL_COLS], units="(KES MM)")
    _write_formula_row(ws, R, "Off-Balance-Sheet RWA (modeled)", [f"={_cell(M['ob_rwa'], c)}" for c in DATA_COLS], units="(KES MM)")
    R += 1
    rwa_row = R
    # Actual years: RWA is Family Bank's own disclosed aggregate (Capital Management note —
    # no Basel-style credit/market/operational split exists in the filings to check our own
    # loan/off-balance-sheet RWA sub-rows above against, so they're shown for context only,
    # not summed into this total). Projected years: no better forward-looking driver is
    # disclosed, so the modeled loan/off-balance RWA plus a gross-loans-scaled residual
    # (calibrated to the real FY2025 anchor — see config.py) continues to be used.
    rwa_actual = [rc[y]["rwa"] for y in ay]
    rwa_proj = [f"={_cell(loan_rwa_row, c)}+{_cell(M['ob_rwa'], c)}"
                f"+{_cell(M['agg_gross_total'], c)}*{_assum_ref(A, 'other_rwa_pct_of_gross_loans')}"
                for c in DATA_COLS]
    _write_actual_row(ws, R, "Total RWA (disclosed for actuals; modeled for projected)",
                       rwa_actual, bold=True, units="(KES MM)")
    _write_formula_row(ws, R, "Total RWA (disclosed for actuals; modeled for projected)",
                        rwa_proj, bold=True, units="(KES MM)")
    R += 1
    blank_row(ws, R); R += 1
    M["loan_rwa"] = loan_rwa_row
    M["rwa"] = rwa_row

    write(ws, R, LABEL_COL, "Regulatory Capital — Tier 1 Build-up (Actuals, disclosed)",
          bold=True, txt_color=NAVY); R += 1
    rc_share_cap_row = R
    _write_actual_row(ws, R, "Share Capital (regulatory)", [rc[y]["share_capital"] for y in ay], units="(KES MM)")
    _write_formula_row(ws, R, "Share Capital (regulatory)", [None] * len(DATA_COLS), units="(KES MM)")
    R += 1
    rc_share_prem_row = R
    _write_actual_row(ws, R, "Share Premium", [rc[y]["share_premium"] for y in ay], units="(KES MM)")
    _write_formula_row(ws, R, "Share Premium", [None] * len(DATA_COLS), units="(KES MM)")
    R += 1
    rc_re_row = R
    _write_actual_row(ws, R, "Retained Earnings (regulatory)", [rc[y]["retained_earnings"] for y in ay], units="(KES MM)")
    _write_formula_row(ws, R, "Retained Earnings (regulatory)", [None] * len(DATA_COLS), units="(KES MM)")
    R += 1
    rc_dta_row = R
    _write_actual_row(ws, R, "Less: Deferred Tax", [rc[y]["deferred_tax"] for y in ay], units="(KES MM)")
    _write_formula_row(ws, R, "Less: Deferred Tax", [None] * len(DATA_COLS), units="(KES MM)")
    R += 1
    tier1_row = R
    tier1_actual = [f"={_cell(rc_share_cap_row, c)}+{_cell(rc_share_prem_row, c)}"
                    f"+{_cell(rc_re_row, c)}+{_cell(rc_dta_row, c)}" for c in ACTUAL_COLS]
    # Projected years: no forward-looking regulatory-bridge methodology is disclosed, so
    # Tier 1 is modeled as a fixed % of Total Equity, calibrated to the real FY2025 anchor.
    tier1_proj = [f"={_cell(M['total_equity'], c)}*{_assum_ref(A, 'tier1_pct_of_equity')}" for c in DATA_COLS]
    _write_actual_row(ws, R, "Total Tier 1 Capital (regulatory)", tier1_actual, bold=True, units="(KES MM)")
    _write_formula_row(ws, R, "Total Tier 1 Capital (regulatory)", tier1_proj, bold=True, units="(KES MM)")
    R += 1
    blank_row(ws, R); R += 1

    write(ws, R, LABEL_COL, "Regulatory Capital — Tier 2 Build-up (Actuals, disclosed)",
          bold=True, txt_color=NAVY); R += 1
    rc_reval_row = R
    _write_actual_row(ws, R, "Revaluation Reserve (25% eligible)", [rc[y]["revaluation_reserve"] for y in ay], units="(KES MM)")
    _write_formula_row(ws, R, "Revaluation Reserve (25% eligible)", [None] * len(DATA_COLS), units="(KES MM)")
    R += 1
    rc_subdebt_row = R
    _write_actual_row(ws, R, "Subordinated Term Debt", [rc[y]["subordinated_debt"] for y in ay], units="(KES MM)")
    _write_formula_row(ws, R, "Subordinated Term Debt", [None] * len(DATA_COLS), units="(KES MM)")
    R += 1
    rc_statres_row = R
    _write_actual_row(ws, R, "Statutory Reserve", [rc[y]["statutory_reserve"] for y in ay], units="(KES MM)")
    _write_formula_row(ws, R, "Statutory Reserve", [None] * len(DATA_COLS), units="(KES MM)")
    R += 1
    tier2_row = R
    tier2_actual = [f"={_cell(rc_reval_row, c)}+{_cell(rc_subdebt_row, c)}+{_cell(rc_statres_row, c)}" for c in ACTUAL_COLS]
    tier2_proj = [f"={_assum_ref(A, 'reg_tier2_opening')}" for _ in DATA_COLS]
    _write_actual_row(ws, R, "Total Tier 2 Capital (regulatory)", tier2_actual, bold=True, units="(KES MM)")
    _write_formula_row(ws, R, "Total Tier 2 Capital (regulatory)", tier2_proj, bold=True, units="(KES MM)")
    R += 1
    total_cap_row = R
    total_row(ws, R, "Total Regulatory Capital", [f"={_cell(tier1_row, c)}+{_cell(tier2_row, c)}" for c in ACTUAL_COLS], ACTUAL_COLS, label_col=LABEL_COL)
    total_row(ws, R, "Total Regulatory Capital", [f"={_cell(tier1_row, c)}+{_cell(tier2_row, c)}" for c in DATA_COLS], DATA_COLS, label_col=LABEL_COL)
    R += 1
    blank_row(ws, R); R += 1
    M["tier1"] = tier1_row; M["tier2"] = tier2_row; M["total_capital"] = total_cap_row

    write(ws, R, LABEL_COL, "Capital Ratios", bold=True, txt_color=NAVY); R += 1
    core_ratio_row = R
    _write_actual_row(ws, R, "Core Capital / RWA", [_ratio_f(tier1_row, rwa_row, c) for c in ACTUAL_COLS], fmt='0.0%')
    _write_formula_row(ws, R, "Core Capital / RWA", [_ratio_f(tier1_row, rwa_row, c) for c in DATA_COLS], fmt='0.0%')
    R += 1
    total_ratio_row = R
    _write_actual_row(ws, R, "Total Capital / RWA", [_ratio_f(total_cap_row, rwa_row, c) for c in ACTUAL_COLS], fmt='0.0%')
    _write_formula_row(ws, R, "Total Capital / RWA", [_ratio_f(total_cap_row, rwa_row, c) for c in DATA_COLS], fmt='0.0%')
    R += 1
    core_deposits_row = R
    _write_actual_row(ws, R, "Core Capital / Deposits", [_ratio_f(tier1_row, M["dep_total"], c) for c in ACTUAL_COLS], fmt='0.0%')
    _write_formula_row(ws, R, "Core Capital / Deposits", [_ratio_f(tier1_row, M["dep_total"], c) for c in DATA_COLS], fmt='0.0%')
    R += 1
    blank_row(ws, R); R += 1
    M["core_capital_ratio"] = core_ratio_row
    M["total_capital_ratio"] = total_ratio_row
    M["core_capital_to_deposits"] = core_deposits_row

    write(ws, R, LABEL_COL, "Liquidity", bold=True, txt_color=NAVY); R += 1
    liquid_assets_row = R
    la_f = lambda c: f"={_cell(M['cash'], c)}+{_cell(M['sec_balance'], c)}"
    _write_actual_row(ws, R, "Liquid Assets (Cash + Securities)", [la_f(c) for c in ACTUAL_COLS], units="(KES MM)")
    _write_formula_row(ws, R, "Liquid Assets (Cash + Securities)", [la_f(c) for c in DATA_COLS], units="(KES MM)")
    R += 1
    liquidity_ratio_row = R
    _write_actual_row(ws, R, "Liquidity Ratio", [_ratio_f(liquid_assets_row, M["dep_total"], c) for c in ACTUAL_COLS], fmt='0.0%')
    _write_formula_row(ws, R, "Liquidity Ratio", [_ratio_f(liquid_assets_row, M["dep_total"], c) for c in DATA_COLS], fmt='0.0%')
    R += 1
    blank_row(ws, R, 8); R += 1
    M["liquid_assets"] = liquid_assets_row
    M["liquidity_ratio"] = liquidity_ratio_row

    return R


# ─────────────────────────────────────────────
# MODEL SHEET — Master Check (filled in last, once all rows exist)
# ─────────────────────────────────────────────

def _build_master_check(ws, A, M, title_row):
    """Reserves/fills rows just below the title with OK/ERROR status formulas. Called
    after the rest of the Model sheet is built so the referenced rows exist."""
    from openpyxl.formatting.rule import FormulaRule

    R = title_row
    section_header(ws, R, "MASTER CHECK", bg=GOLD, txt_color=DARK); R += 1
    status_rows = []

    def _status_row(label, formulas):
        nonlocal R
        _write_formula_row(ws, R, label, formulas, bold=True, cols=_all_cols())
        status_rows.append(R)
        R += 1

    all_cols = _all_cols()
    _status_row("Balance Sheet Check (Assets = Liab + Equity)",
                 [f'=IF(ABS({_cell(M["bs_check"], col)})<0.01,"OK","ERROR")' for col in all_cols])
    _status_row("Capital Adequacy Check (Total Capital ≥ CBK minimum)",
                 [f'=IF({_cell(M["total_capital_ratio"], col)}>={_assum_ref(A, "total_min")},"OK","ERROR")'
                  for col in all_cols])
    _status_row("Liquidity Check (≥ CBK statutory minimum)",
                 [f'=IF({_cell(M["liquidity_ratio"], col)}>={_assum_ref(A, "liquidity_min")},"OK","ERROR")'
                  for col in all_cols])

    for row in status_rows:
        cell_range = f"{_cell(row, all_cols[0])}:{_cell(row, all_cols[-1])}"
        ws.conditional_formatting.add(
            cell_range,
            FormulaRule(formula=[f'{_cell(row, DATA_COLS[0])}="ERROR"'],
                        fill=fill(RED_DARK), font=None)
        )
        ws.conditional_formatting.add(
            cell_range,
            FormulaRule(formula=[f'{_cell(row, DATA_COLS[0])}="OK"'],
                        fill=fill(GREEN_DRK), font=None)
        )

    return R


# ─────────────────────────────────────────────
# MODEL SHEET — orchestrator
# ─────────────────────────────────────────────

def build_model(wb, config, A):
    ws = wb.create_sheet("Model", index=4)
    ws.sheet_view.showGridLines = False
    _col_widths(ws)
    M = {}

    write(ws, 1, LABEL_COL, config.BUSINESS_NAME, bold=True, size=14, txt_color=NAVY)
    write(ws, 1, 8,
          f'="CURRENTLY RUNNING: "&UPPER(CHOOSE({SWITCH_CELL_REF},"Base","Best","Worst"))&" SCENARIO"',
          bold=True, txt_color=GOLD)
    write(ws, 2, LABEL_COL, "Model — Scenario-Switched (fully formula-linked)", txt_color=MID_GRAY)
    master_check_title_row = 4
    # Reserve rows 4-8 for the Master Check (filled in after the rest of the sheet exists)
    R = 10
    R = _model_period_header(ws, R)
    assert R == MASTER_HEADER_ROW, f"MASTER_HEADER_ROW drifted: expected {MASTER_HEADER_ROW}, got {R}"
    year_header_row(ws, R, _period_labels(config), _all_cols(),
                     label_col=LABEL_COL, units_col=UNITS_COL)
    R += 1
    blank_row(ws, R, 8); R += 1

    R = _build_loan_book_section(ws, config, A, M, R)
    R = _build_funding_section(ws, config, A, M, R)
    R = _build_income_statement_section(ws, config, A, M, R)
    R = _build_cash_flow_balance_sheet_section(ws, config, A, M, R)
    R = _build_capital_liquidity_section(ws, config, A, M, R)

    _build_master_check(ws, A, M, master_check_title_row)

    return M


# ─────────────────────────────────────────────
# SUMMARY SHEET
# ─────────────────────────────────────────────

def build_summary(wb, config, A, M, scenarios):
    ws = wb.create_sheet("Summary", index=1)
    ws.sheet_view.showGridLines = False
    _col_widths(ws)

    R = 1
    write(ws, R, LABEL_COL, config.BUSINESS_NAME, bold=True, size=14, txt_color=NAVY); R += 2
    write(ws, R, LABEL_COL, "Summary Financial Outputs — Three Scenarios", txt_color=MID_GRAY); R += 2

    def _kpi_block(label, data, bg_hdr):
        nonlocal R
        header_row(ws, R, label, bg=bg_hdr, txt_color=WHITE, height=18, merge_to_col=12); R += 1
        year_header_row(ws, R, _period_labels_proj(config), DATA_COLS, label_col=LABEL_COL); R += 1
        blank_row(ws, R); R += 1
        pat = data["income_stmt"]["pat"]
        nii = data["nii"]["nii"]
        total_income = [nii[i] + data["income_stmt"]["non_interest_income"][i] for i in range(len(nii))]
        data_row(ws, R, "Total Income (NII + Non-Interest)", total_income, DATA_COLS, label_col=LABEL_COL,
                 units="(KES MM)", units_col=UNITS_COL, bold=True, alt_idx=0); R += 1
        data_row(ws, R, "Net Interest Income", nii, DATA_COLS, label_col=LABEL_COL,
                 units="(KES MM)", units_col=UNITS_COL, alt_idx=1); R += 1
        data_row(ws, R, "Net Profit After Tax", pat, DATA_COLS, label_col=LABEL_COL,
                 units="(KES MM)", units_col=UNITS_COL, bold=True, alt_idx=0); R += 1
        data_row(ws, R, "Total Capital Ratio", data["capital"]["total_capital_ratio"], DATA_COLS,
                 label_col=LABEL_COL, fmt='0.0%', alt_idx=1); R += 1
        data_row(ws, R, "NPL Ratio", data["loan_book"]["npl_ratio"], DATA_COLS, label_col=LABEL_COL,
                 fmt='0.0%', alt_idx=0); R += 1
        R += 1

    _kpi_block("BASE CASE — Financial Summary", scenarios["base"], NAVY)
    _kpi_block("BEST CASE — Financial Summary", scenarios["best"], GREEN_DRK)
    _kpi_block("WORST CASE — Financial Summary", scenarios["worst"], RED_DARK)

    all_cols = _all_cols()
    all_years = _period_labels(config)

    section_header(ws, R, "RATIO DISCLOSURES — BASE CASE (live-linked to Model sheet)",
                   bg=MED_BLUE, txt_color=WHITE); R += 1
    year_header_row(ws, R, all_years, all_cols, label_col=LABEL_COL); R += 1
    blank_row(ws, R); R += 1

    section_header(ws, R, "Profitability (CAMELS: Earnings)"); R += 1
    # ROE/NIM/cost-to-income aren't yet Model-sheet rows (Model sheet computes ratios via
    # capital/liquidity sections only) — compute them directly here as cross-sheet formulas.
    # First actual year (2023) has no prior-year equity on record, so average equity can't
    # be computed there — left blank rather than fabricated. Every later column (actual or
    # projected) references the prior column directly, same sheet, same simplification as
    # the Model sheet's own _prev() — no Assumptions-cell fallback needed anywhere now.
    roe_formulas = []
    for i, col in enumerate(all_cols):
        if i == 0:
            roe_formulas.append(None)
            continue
        prev_equity_ref = f"'Model'!{_cell(M['total_equity'], all_cols[i-1])}"
        roe_formulas.append(
            f"=IFERROR('Model'!{_cell(M['pat'], col)}/(({prev_equity_ref}+'Model'!{_cell(M['total_equity'], col)})/2),0)")
    data_row(ws, R, "Return on Equity (ROE)", roe_formulas, all_cols, label_col=LABEL_COL, fmt='0.0%', alt_idx=0)
    R += 1
    data_row(ws, R, "Net Interest Margin (proxy: NII / Total Deposits)",
             [f"=IFERROR('Model'!{_cell(M['nii'], col)}/'Model'!{_cell(M['dep_total'], col)},0)" for col in all_cols],
             all_cols, label_col=LABEL_COL, fmt='0.0%', alt_idx=1)
    R += 1
    data_row(ws, R, "Cost-to-Income Ratio",
             [f"=IFERROR('Model'!{_cell(M['opex_total'], col)}/('Model'!{_cell(M['nii'], col)}"
              f"+'Model'!{_cell(M['non_interest_income'], col)}),0)" for col in all_cols],
             all_cols, label_col=LABEL_COL, fmt='0.0%', alt_idx=0)
    R += 1
    R += 1

    section_header(ws, R, "Capital Adequacy (CAMELS: Capital)"); R += 1
    data_row(ws, R, "Core Capital / RWA", [f"='Model'!{_cell(M['core_capital_ratio'], col)}" for col in all_cols],
             all_cols, label_col=LABEL_COL, fmt='0.0%', alt_idx=0)
    R += 1
    data_row(ws, R, "Total Capital / RWA", [f"='Model'!{_cell(M['total_capital_ratio'], col)}" for col in all_cols],
             all_cols, label_col=LABEL_COL, fmt='0.0%', alt_idx=1)
    R += 1
    R += 1

    section_header(ws, R, "Liquidity (CAMELS: Liquidity)"); R += 1
    data_row(ws, R, "Liquidity Ratio", [f"='Model'!{_cell(M['liquidity_ratio'], col)}" for col in all_cols],
             all_cols, label_col=LABEL_COL, fmt='0.0%', alt_idx=0)
    R += 1
    R += 1

    section_header(ws, R, "Cash Flow Ratios"); R += 1
    data_row(ws, R, "Operating Cash Flow / PAT",
             [f"=IFERROR('Model'!{_cell(M['ocf'], col)}/'Model'!{_cell(M['pat'], col)},0)" for col in all_cols],
             all_cols, label_col=LABEL_COL, fmt='0.0%', alt_idx=0)
    R += 1
    data_row(ws, R, "Operating Cash Flow / Total Deposits",
             [f"=IFERROR('Model'!{_cell(M['ocf'], col)}/'Model'!{_cell(M['dep_total'], col)},0)" for col in all_cols],
             all_cols, label_col=LABEL_COL, fmt='0.0%', alt_idx=1)
    R += 1

    return R


# ─────────────────────────────────────────────
# SCENARIOS SHEET (Base/Best/Worst — static Python-computed values, existing convention)
# ─────────────────────────────────────────────

def build_scenarios_sheet(wb, config, scenarios):
    ws = wb.create_sheet("Scenarios", index=3)
    ws.sheet_view.showGridLines = False
    _col_widths(ws)

    R = 1
    write(ws, R, LABEL_COL, config.BUSINESS_NAME, bold=True, size=14, txt_color=NAVY); R += 2
    write(ws, R, LABEL_COL, "Scenario Comparison — Key Drivers", txt_color=MID_GRAY); R += 1

    # Scenario switch — fixed at row 5, col D (SWITCH_CELL_REF = 'Scenarios'!$D$5), referenced
    # by every CHOOSE()-driven "(ACTIVE)" row on the Assumptions sheet. This single cell
    # re-drives the entire live Model sheet: 1=Base, 2=Best, 3=Worst.
    write(ws, 5, LABEL_COL, "SCENARIO SWITCH (1=Base, 2=Best, 3=Worst):", bold=True, txt_color=NAVY)
    num(ws, 5, 4, 1, fmt='0', bold=True, txt_color=BLUE_INPUT)
    write(ws, 5, 7, '=UPPER(CHOOSE($D$5,"Base","Best","Worst"))&" CASE IS CURRENTLY LIVE ON THE MODEL SHEET"',
          italic=True, txt_color=MID_GRAY)
    R = 7

    scenario_defs = [
        ("BASE CASE", NAVY, "Modeled loan growth / IFRS 9 loss rates / opex escalation as calibrated", scenarios["base"]),
        ("BEST CASE", GREEN_DRK, "Loan growth x1.2, loss rates x0.8, opex escalation x0.9", scenarios["best"]),
        ("WORST CASE", RED_DARK, "Loan growth x0.7, loss rates x1.4, opex escalation x1.15", scenarios["worst"]),
    ]
    for name, color, note, data in scenario_defs:
        header_row(ws, R, name, bg=color, txt_color=WHITE, height=18, merge_to_col=12); R += 1
        write(ws, R, LABEL_COL, note, italic=True, txt_color=MID_GRAY, size=9); R += 1
        blank_row(ws, R); R += 1
        year_header_row(ws, R, _period_labels_proj(config), DATA_COLS, label_col=LABEL_COL); R += 1

        pat = data["income_stmt"]["pat"]
        nii = data["nii"]["nii"]
        non_int = data["income_stmt"]["non_interest_income"]
        total_income = [nii[i] + non_int[i] for i in range(len(nii))]
        metrics = [
            ("Total Income (KES MM)", total_income, '#,##0.0'),
            ("Net Interest Income (KES MM)", nii, '#,##0.0'),
            ("Net Profit After Tax (KES MM)", pat, '#,##0.0'),
            ("NPL Ratio", data["loan_book"]["npl_ratio"], '0.0%'),
            ("Total Capital Ratio", data["capital"]["total_capital_ratio"], '0.0%'),
            ("Liquidity Ratio", data["liquidity"]["ratio"], '0.0%'),
            ("Return on Assets (avg)", data["ratios"]["roa"], '0.0%'),
            ("Return on Equity (avg)", data["ratios"]["roe"], '0.0%'),
        ]
        for i, (label, vals, fmt) in enumerate(metrics):
            data_row(ws, R, label, vals, DATA_COLS, label_col=LABEL_COL, fmt=fmt, alt_idx=i)
            R += 1
        R += 1
        blank_row(ws, R, 8); R += 1


# ─────────────────────────────────────────────
# VALUATION SHEET
# ─────────────────────────────────────────────

def build_valuation_sheet(wb, config, A, M):
    ws = wb.create_sheet("Valuation", index=5)
    ws.sheet_view.showGridLines = False
    _col_widths(ws)
    n = len(config.YEARS)

    R = 1
    write(ws, R, LABEL_COL, config.BUSINESS_NAME, bold=True, size=14, txt_color=NAVY); R += 2
    write(ws, R, LABEL_COL, "Equity Valuation — Base Case", txt_color=MID_GRAY); R += 2

    section_header(ws, R, "COST OF EQUITY (CAPM)"); R += 1
    write(ws, R, LABEL_COL, "Risk-free rate"); num(ws, R, ASSUM_COL, f"={_assum_ref(A, 'risk_free_rate')}", fmt='0.00%'); R += 1
    write(ws, R, LABEL_COL, "Beta"); num(ws, R, ASSUM_COL, f"={_assum_ref(A, 'beta')}", fmt='0.00'); R += 1
    write(ws, R, LABEL_COL, "Equity risk premium"); num(ws, R, ASSUM_COL, f"={_assum_ref(A, 'erp')}", fmt='0.00%'); R += 1
    write(ws, R, LABEL_COL, "Cost of equity", bold=True)
    num(ws, R, ASSUM_COL, f"={_assum_ref(A, 'cost_of_equity')}", fmt='0.00%', bold=True)
    coe_cell = _cell(R, ASSUM_COL)
    R += 2

    section_header(ws, R, "DIVIDEND DISCOUNT MODEL (multi-stage)"); R += 1
    year_header_row(ws, R, _period_labels_proj(config), DATA_COLS, label_col=LABEL_COL); R += 1
    div_row = R
    _write_formula_row(ws, R, "Dividends", [f"='Model'!{_cell(M['dividends'], col)}" for col in DATA_COLS],
                        units="(KES MM)")
    R += 1
    pv_div_row = R
    pv_formulas = [f"={_cell(div_row, col)}/(1+{coe_cell})^{i+1}" for i, col in enumerate(DATA_COLS)]
    _write_formula_row(ws, R, "PV of Dividends", pv_formulas, units="(KES MM)")
    R += 1
    write(ws, R, LABEL_COL, "Terminal value (Gordon growth)")
    terminal_formula = (f"={_cell(div_row, DATA_COLS[-1])}*(1+{_assum_ref(A, 'terminal_growth')})"
                        f"/({coe_cell}-{_assum_ref(A, 'terminal_growth')})")
    num(ws, R, ASSUM_COL, terminal_formula, fmt='#,##0.0'); terminal_row = R; R += 1
    write(ws, R, LABEL_COL, "PV of terminal value")
    pv_terminal_formula = f"={_cell(terminal_row, ASSUM_COL)}/(1+{coe_cell})^{n}"
    num(ws, R, ASSUM_COL, pv_terminal_formula, fmt='#,##0.0'); pv_terminal_row = R; R += 1
    write(ws, R, LABEL_COL, "DDM Implied Equity Value", bold=True, txt_color=NAVY)
    ddm_formula = f"=SUM({_cell(pv_div_row, DATA_COLS[0])}:{_cell(pv_div_row, DATA_COLS[-1])})+{_cell(pv_terminal_row, ASSUM_COL)}"
    num(ws, R, ASSUM_COL, ddm_formula, fmt='#,##0.0', bold=True, txt_color=NAVY)
    ddm_value_row = R
    R += 1
    write(ws, R, LABEL_COL, "DDM Implied Value Per Share (KES)", bold=True, txt_color=NAVY)
    num(ws, R, ASSUM_COL, f"={_cell(ddm_value_row, ASSUM_COL)}/{_assum_ref(A, 'shares_outstanding')}",
        fmt='#,##0.00', bold=True, txt_color=NAVY)
    ddm_per_share_row = R
    R += 2

    section_header(ws, R, "RESIDUAL INCOME / EXCESS RETURN MODEL (cross-check)"); R += 1
    year_header_row(ws, R, _period_labels_proj(config), DATA_COLS, label_col=LABEL_COL); R += 1
    equity_row_ref = R
    _write_formula_row(ws, R, "Book Equity (period-end)", [f"='Model'!{_cell(M['total_equity'], col)}" for col in DATA_COLS],
                        units="(KES MM)")
    R += 1
    roe_row_ref = R
    roe_formulas = []
    for i, col in enumerate(DATA_COLS):
        prev_eq = _assum_ref(A, "opening_tier1") if i == 0 else _cell(equity_row_ref, DATA_COLS[i - 1])
        roe_formulas.append(f"=IFERROR('Model'!{_cell(M['pat'], col)}/{prev_eq},0)")
    _write_formula_row(ws, R, "ROE (on opening equity)", roe_formulas, fmt='0.0%')
    R += 1
    ri_row = R
    ri_formulas = []
    for i, col in enumerate(DATA_COLS):
        prev_eq = _assum_ref(A, "opening_tier1") if i == 0 else _cell(equity_row_ref, DATA_COLS[i - 1])
        ri_formulas.append(f"=({_cell(roe_row_ref, col)}-{coe_cell})*{prev_eq}")
    _write_formula_row(ws, R, "Residual Income", ri_formulas, units="(KES MM)")
    R += 1
    pv_ri_row = R
    _write_formula_row(ws, R, "PV of Residual Income",
                        [f"={_cell(ri_row, col)}/(1+{coe_cell})^{i+1}" for i, col in enumerate(DATA_COLS)],
                        units="(KES MM)")
    R += 1
    write(ws, R, LABEL_COL, "Terminal residual income value")
    ri_terminal_formula = (f"={_cell(ri_row, DATA_COLS[-1])}*(1+{_assum_ref(A, 'terminal_growth')})"
                          f"/({coe_cell}-{_assum_ref(A, 'terminal_growth')})")
    num(ws, R, ASSUM_COL, ri_terminal_formula, fmt='#,##0.0'); ri_terminal_row = R; R += 1
    write(ws, R, LABEL_COL, "PV of terminal residual income")
    pv_ri_terminal_formula = f"={_cell(ri_terminal_row, ASSUM_COL)}/(1+{coe_cell})^{n}"
    num(ws, R, ASSUM_COL, pv_ri_terminal_formula, fmt='#,##0.0'); pv_ri_terminal_row = R; R += 1
    write(ws, R, LABEL_COL, "Residual Income Implied Equity Value", bold=True, txt_color=NAVY)
    ri_value_formula = (f"={_assum_ref(A, 'opening_tier1')}"
                        f"+SUM({_cell(pv_ri_row, DATA_COLS[0])}:{_cell(pv_ri_row, DATA_COLS[-1])})"
                        f"+{_cell(pv_ri_terminal_row, ASSUM_COL)}")
    num(ws, R, ASSUM_COL, ri_value_formula, fmt='#,##0.0', bold=True, txt_color=NAVY)
    ri_value_row = R
    R += 1
    write(ws, R, LABEL_COL, "Residual Income Implied Value Per Share (KES)", bold=True, txt_color=NAVY)
    num(ws, R, ASSUM_COL, f"={_cell(ri_value_row, ASSUM_COL)}/{_assum_ref(A, 'shares_outstanding')}",
        fmt='#,##0.00', bold=True, txt_color=NAVY)
    ri_per_share_row = R
    R += 2

    section_header(ws, R, "RELATIVE VALUATION — P/B-ROE REGRESSION ([PLACEHOLDER] peer P/B)"); R += 1
    write(ws, R, LABEL_COL, "Final-year ROE (on opening equity)")
    num(ws, R, ASSUM_COL, f"={_cell(roe_row_ref, DATA_COLS[-1])}", fmt='0.0%'); final_roe_row = R; R += 1
    write(ws, R, LABEL_COL, "Implied P/B (regression slope x ROE + intercept)")
    implied_pb_formula = (f"={_assum_ref(A, 'pb_roe_slope')}*{_cell(final_roe_row, ASSUM_COL)}"
                          f"+{_assum_ref(A, 'pb_roe_intercept')}")
    num(ws, R, ASSUM_COL, implied_pb_formula, fmt='0.00', txt_color=ORANGE); implied_pb_row = R; R += 1
    write(ws, R, LABEL_COL, "P/B-ROE Regression Implied Equity Value", bold=True, txt_color=NAVY)
    pb_value_formula = f"={_cell(implied_pb_row, ASSUM_COL)}*'Model'!{_cell(M['total_equity'], DATA_COLS[-1])}"
    num(ws, R, ASSUM_COL, pb_value_formula, fmt='#,##0.0', bold=True, txt_color=NAVY)
    pb_value_row = R
    R += 1
    write(ws, R, LABEL_COL, "P/B-ROE Regression Implied Value Per Share (KES)", bold=True, txt_color=NAVY)
    num(ws, R, ASSUM_COL, f"={_cell(pb_value_row, ASSUM_COL)}/{_assum_ref(A, 'shares_outstanding')}",
        fmt='#,##0.00', bold=True, txt_color=NAVY)
    pb_per_share_row = R
    R += 2

    section_header(ws, R, "SUMMARY — IMPLIED EQUITY VALUE BY METHOD"); R += 1
    write(ws, R, LABEL_COL, "Method", bold=True)
    write(ws, R, ASSUM_COL, "Total (KES MM)", bold=True, txt_color=MID_GRAY, halign="center")
    write(ws, R, ASSUM_COL + 1, "Per Share (KES)", bold=True, txt_color=MID_GRAY, halign="center")
    R += 1
    for label, value_row, per_share_row in [
        ("Dividend Discount Model (DDM)", ddm_value_row, ddm_per_share_row),
        ("Residual Income / Excess Return", ri_value_row, ri_per_share_row),
        ("P/B-ROE Regression (relative)", pb_value_row, pb_per_share_row),
    ]:
        write(ws, R, LABEL_COL, label, bold=True)
        num(ws, R, ASSUM_COL, f"={_cell(value_row, ASSUM_COL)}", fmt='#,##0.0', bold=True, txt_color=NAVY)
        num(ws, R, ASSUM_COL + 1, f"={_cell(per_share_row, ASSUM_COL)}", fmt='#,##0.00', bold=True, txt_color=NAVY)
        R += 1
    R += 1

    section_header(ws, R, "BOOK VALUE PER SHARE (Actuals, cross-check)"); R += 1
    write(ws, R, LABEL_COL,
          "Total Equity ÷ that year's own share count (share count changed year to year via "
          "the FY2023 rights issue and FY2025 private placement — not the FY2025 count "
          "applied retroactively). Uses our Bank-basis Total Equity, so runs slightly below "
          "Family Bank's own disclosed Group-basis BVPS (e.g. FY2025: ours ~19.31 vs the "
          "disclosed 19.62) — expected, not an error, per this model's bank-not-group basis.",
          italic=True, txt_color=MID_GRAY, size=9)
    R += 2
    year_header_row(ws, R, _period_labels_actual(config), ACTUAL_COLS, label_col=LABEL_COL); R += 1
    bvps_formulas = [f"=IFERROR('Model'!{_cell(M['total_equity'], c)}/{_actual(config, y, 'share_capital')},0)"
                     for y, c in zip(config.ACTUAL_YEARS, ACTUAL_COLS)]
    _write_actual_row(ws, R, "Book Value Per Share (KES)", bvps_formulas, fmt='#,##0.00', bold=True)
    R += 1
    blank_row(ws, R); R += 1

    ay = config.ACTUAL_YEARS
    section_header(ws, R, "FINANCIAL STATEMENT QUALITY ANALYSIS (Actuals only — 2023-2025)",
                   bg=MED_BLUE, txt_color=WHITE); R += 1
    write(ws, R, LABEL_COL,
          "Evaluates the reported actuals for signs of earnings management/manipulation — "
          "scoped to the 3 actual years only. The projection is our own modeling, not a "
          "filing to scrutinize.", italic=True, txt_color=MID_GRAY, size=9)
    R += 2
    year_header_row(ws, R, _period_labels_actual(config), ACTUAL_COLS, label_col=LABEL_COL); R += 1
    blank_row(ws, R); R += 1

    total_assets_ref = lambda col: f"'Model'!{_cell(M['total_assets'], col)}"
    pat_ref = lambda col: f"'Model'!{_cell(M['pat'], col)}"
    ocf_ref = lambda col: f"'Model'!{_cell(M['ocf'], col)}"

    section_header(ws, R, "Accruals Ratio (Sloan, 1996) — applies to banks unmodified"); R += 1
    write(ws, R, LABEL_COL,
          "(PAT − Operating Cash Flow) / Average Total Assets. A rising ratio means profit "
          "is increasingly outpacing the cash actually generated — the classic earnings-"
          "quality red flag.", italic=True, txt_color=MID_GRAY, size=9)
    R += 1
    avg_ta_formulas = []
    for i, col in enumerate(ACTUAL_COLS):
        if i == 0:
            avg_ta_formulas.append(f"={total_assets_ref(col)}")
        else:
            avg_ta_formulas.append(f"=({total_assets_ref(ACTUAL_COLS[i-1])}+{total_assets_ref(col)})/2")
    avg_ta_row = R
    _write_actual_row(ws, R, "Average Total Assets (2023: period-end — no 2022 figure on record)",
                       avg_ta_formulas, units="(KES MM)")
    R += 1
    accruals_row = R
    accruals_formulas = [f"=({pat_ref(col)}-{ocf_ref(col)})/{_cell(avg_ta_row, col)}" for col in ACTUAL_COLS]
    _write_actual_row(ws, R, "Accruals Ratio", accruals_formulas, fmt='0.00%')
    R += 2

    section_header(ws, R, "Profitability vs. Operating Cash Flow Trend"); R += 1
    _write_actual_row(ws, R, "Net Profit After Tax (PAT)", [f"={pat_ref(col)}" for col in ACTUAL_COLS],
                       units="(KES MM)")
    R += 1
    _write_actual_row(ws, R, "Operating Cash Flow (OCF)", [f"={ocf_ref(col)}" for col in ACTUAL_COLS],
                       units="(KES MM)")
    R += 1
    ocf_pat_row = R
    _write_actual_row(ws, R, "OCF / PAT",
                       [f"=IFERROR({ocf_ref(col)}/{pat_ref(col)},0)" for col in ACTUAL_COLS], fmt='0.0%')
    R += 1
    trend_flag_formulas = [None] + [
        f'=IF({_cell(ocf_pat_row, col)}<{_cell(ocf_pat_row, ACTUAL_COLS[i-1])},"FLAG: declining","OK")'
        for i, col in enumerate(ACTUAL_COLS) if i > 0
    ]
    _write_actual_row(ws, R, "Trend Flag (OCF/PAT vs. prior year)", trend_flag_formulas)
    R += 2

    section_header(ws, R, "Texas Ratio — bank-specific distress indicator (Cassidy, 1980s Texas banking crisis)")
    R += 1
    write(ws, R, LABEL_COL,
          "Stage 3 Gross NPLs / (Total Equity + Total Loan Loss Reserves). Historically, "
          ">100% has been a strong signal of severe bank distress.",
          italic=True, txt_color=MID_GRAY, size=9)
    R += 1
    texas_formulas = [
        f"=IFERROR('Model'!{_cell(M['agg_s3_gross'], col)}/('Model'!{_cell(M['total_equity'], col)}"
        f"+'Model'!{_cell(M['agg_ecl_total'], col)}),0)" for col in ACTUAL_COLS]
    _write_actual_row(ws, R, "Texas Ratio (Total Equity used as Tangible Common Equity proxy — "
                             "no intangibles disclosed separately)", texas_formulas, fmt='0.0%')
    R += 2

    section_header(ws, R, "Beneish M-Score — Adapted Proxy for Financial Institutions"); R += 1
    write(ws, R, LABEL_COL,
          "CAVEAT: the standard Beneish M-Score explicitly excludes financial institutions — "
          "Sales/Receivables/Gross-Margin/COGS concepts don't translate to a bank balance "
          "sheet. Below substitutes bank-equivalent concepts per component and omits the "
          "Depreciation Index (no actual-year D&A breakdown disclosed). Interpret "
          "directionally only — NOT against the original model's -2.22 threshold.",
          italic=True, txt_color=RED_DARK, size=9)
    R += 1
    write(ws, R, LABEL_COL,
          "Every index needs a prior year, so only 2024 and 2025 are computable "
          "(2023 has no 2022 comparative on record).",
          italic=True, txt_color=MID_GRAY, size=9)
    R += 2

    op_income = lambda col: f"('Model'!{_cell(M['nii'], col)}+'Model'!{_cell(M['non_interest_income'], col)})"
    net_loans_ref = lambda col: f"'Model'!{_cell(M['agg_net_total'], col)}"
    other_assets_ref = lambda col: f"'Model'!{_cell(M['other_assets'], col)}"
    total_liab_ref = lambda col: f"'Model'!{_cell(M['total_liab'], col)}"
    nii_ref = lambda col: f"'Model'!{_cell(M['nii'], col)}"
    dep_total_ref = lambda col: f"'Model'!{_cell(M['dep_total'], col)}"
    opex_ref = lambda col: f"'Model'!{_cell(M['opex_total'], col)}"
    cti_ref = lambda col: f"({opex_ref(col)}/{op_income(col)})"

    def _pair(build):
        return [None] + [build(ACTUAL_COLS[i], ACTUAL_COLS[i - 1]) for i in range(1, len(ACTUAL_COLS))]

    dsri_row = R
    _write_actual_row(ws, R, "DSRI proxy (Net Loans / Total Op. Income index)",
                       _pair(lambda c, p: f"=IFERROR(({net_loans_ref(c)}/{op_income(c)})/({net_loans_ref(p)}/{op_income(p)}),0)"),
                       fmt='0.00')
    R += 1
    gmi_row = R
    # NIM proxy = NII / Total Deposits (same convention as the Summary sheet's own NIM row).
    # GMI = prior NIM / current NIM — index > 1 signals margin deterioration.
    _write_actual_row(ws, R, "GMI proxy (prior NIM / current NIM)",
                       _pair(lambda c, p: f"=IFERROR(({nii_ref(p)}/{dep_total_ref(p)})/({nii_ref(c)}/{dep_total_ref(c)}),0)"),
                       fmt='0.00')
    R += 1
    aqi_row = R
    _write_actual_row(ws, R, "AQI proxy (Other Assets / Total Assets index)",
                       _pair(lambda c, p: f"=IFERROR(({other_assets_ref(c)}/{total_assets_ref(c)})/({other_assets_ref(p)}/{total_assets_ref(p)}),0)"),
                       fmt='0.00')
    R += 1
    sgi_row = R
    _write_actual_row(ws, R, "SGI (Total Operating Income growth index)",
                       _pair(lambda c, p: f"=IFERROR({op_income(c)}/{op_income(p)},0)"), fmt='0.00')
    R += 1
    sgai_row = R
    _write_actual_row(ws, R, "SGAI proxy (Cost-to-Income index)",
                       _pair(lambda c, p: f"=IFERROR({cti_ref(c)}/{cti_ref(p)},0)"), fmt='0.00')
    R += 1
    tata_row = R
    _write_actual_row(ws, R, "TATA (Total Accruals / Total Assets, point-in-time)",
                       [f"=({pat_ref(col)}-{ocf_ref(col)})/{total_assets_ref(col)}" for col in ACTUAL_COLS],
                       fmt='0.00%')
    R += 1
    lvgi_row = R
    _write_actual_row(ws, R, "LVGI (Leverage Index)",
                       _pair(lambda c, p: f"=IFERROR(({total_liab_ref(c)}/{total_assets_ref(c)})/({total_liab_ref(p)}/{total_assets_ref(p)}),0)"),
                       fmt='0.00')
    R += 1
    mscore_formulas = [None] + [
        f"=-4.84+0.92*{_cell(dsri_row, col)}+0.528*{_cell(gmi_row, col)}+0.404*{_cell(aqi_row, col)}"
        f"+0.892*{_cell(sgi_row, col)}-0.172*{_cell(sgai_row, col)}+4.679*{_cell(tata_row, col)}"
        f"-0.327*{_cell(lvgi_row, col)}" for col in ACTUAL_COLS[1:]
    ]
    _write_actual_row(ws, R, "Beneish M-Score (adapted proxy, DEPI omitted)", mscore_formulas,
                       bold=True, fmt='0.00')
    R += 1

    return R


# ─────────────────────────────────────────────
# COVER SHEET
# ─────────────────────────────────────────────

def build_cover(wb, config):
    ws = wb.create_sheet("Cover", index=0)
    ws.sheet_view.showGridLines = False
    _col_widths(ws)

    for r in range(1, 30):
        for c in range(1, 17):
            ws.cell(r, c).fill = fill(WHITE)

    write(ws, 5, LABEL_COL, config.BUSINESS_NAME.upper(), bold=True, size=22, txt_color=NAVY)
    write(ws, 7, LABEL_COL, f"Five-Year Bank Financial Model  |  {config.YEARS[0]} – {config.YEARS[-1]}",
          size=13, txt_color=GOLD, italic=True)

    info = [
        (10, "Currency:", f"{config.CURRENCY} – {config.CURRENCY_UNIT}"),
        (11, "Projection Period:", config.COVER_INFO.get("Projection Period", "")),
        (12, "Scenarios:", "Base Case  |  Best Case  |  Worst Case"),
        (13, "Prepared By:", config.COVER_INFO.get("Prepared By", "")),
        (14, "Classification:", config.COVER_INFO.get("Classification", "")),
    ]
    for row, label, value in info:
        write(ws, row, 4, label, bold=True, txt_color=NAVY)
        write(ws, row, 7, value, txt_color=DARK)

    write(ws, 17, LABEL_COL, "Model Contents", bold=True, size=13, txt_color=NAVY)
    for i, tab in enumerate(["Summary", "Assumptions", "Scenarios",
                              "Model (Loan Book, IFRS 9, Statements, Capital, Liquidity)",
                              "Valuation (DDM, Residual Income, P/B-ROE)"]):
        write(ws, 19 + i, 4, f"•  {tab}", txt_color=MID_GRAY)


# ─────────────────────────────────────────────
# PUBLIC ENTRY POINT
# ─────────────────────────────────────────────

def build_excel(config, results, output_path):
    """Build the full bank financial model workbook.

    `results` is accepted for interface symmetry with the generic renderer and as a
    ground-truth reference during development, but the Model sheet's calculated cells are
    independently reconstructed as live formulas — see module docstring.
    """
    import openpyxl
    from bizplan.financial import bank_calculations

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    build_cover(wb, config)
    A = build_assumptions(wb, config)
    M = build_model(wb, config, A)
    scenarios = bank_calculations.build_scenarios(config)
    build_summary(wb, config, A, M, scenarios)
    build_scenarios_sheet(wb, config, scenarios)
    build_valuation_sheet(wb, config, A, M)

    wb.save(output_path)
    return output_path

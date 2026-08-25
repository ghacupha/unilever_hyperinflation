"""REIT financial model Excel renderer.

Produces a fully formula-linked workbook: Cover, Summary, Assumptions, Scenarios, Model,
Output, Sources. Every calculated cell on the Model sheet is a live Excel formula string
referencing other cells -- Assumptions-sheet input cells for rates/opening balances, and
prior-column-same-row for recurrences -- not a Python-computed static value. Actual-year
columns hold hardcoded disclosed (or clearly-flagged modeled) facts for INPUT rows, with
DERIVED/subtotal rows still live formulas over those facts, so a hand-edit to an actual-year
input immediately re-flows through every subtotal -- same convention the bank model used.

`reit_calculations.py`'s output (`results`, from `build_all()`) is used only to (a) source
input/assumption values and (b) as a ground-truth cross-check while writing formulas -- it
is not written into Model-sheet calculated cells directly.

Bookkeeping: `A` (assumption refs) maps a descriptive key -> Assumptions-sheet row number
(column is always ASSUM_COL). `M` (model row_refs) maps a descriptive key -> Model-sheet
row number. Both dicts are threaded through the builder functions as they write rows, so
later formulas can reference earlier rows by key instead of a hardcoded row number.
"""

from openpyxl.utils import get_column_letter

from bizplan.financial.xl_helpers import (
    NAVY, MED_BLUE, WHITE, DARK, MID_GRAY, ALT_ROW, GOLD,
    GREEN_DRK, RED_DARK, ORANGE, TEAL, BLUE_INPUT,
    fill, write, num, header_row, section_header, year_header_row, blank_row,
    total_row, set_col_widths, outline_range,
    _cell,
)

ACTUAL_COLS = [8, 9, 10]          # H, I, J: 2023-2025 actuals (hardcoded facts + subtotal formulas)
DATA_COLS = [11, 12, 13, 14, 15]  # K-O: 2026-2030 projection (fully live formulas)
ASSUM_COL = 8
LABEL_COL = 3
UNITS_COL = 6
MASTER_HEADER_ROW = 11

SWITCH_CELL_REF = "'Scenarios'!$D$5"


def _units(config):
    return f"({config.CURRENCY_UNIT_ABBR})"


def _scenario_banner_formula():
    return (f'=HYPERLINK("#\'Scenarios\'!D5","Currently running: "&'
            f'UPPER(CHOOSE({SWITCH_CELL_REF},"Base","Best","Worst"))&" CASE")')


PROVENANCE_LEGEND = [
    ("Disclosed fact (Acorn's own filings)", BLUE_INPUT),
    ("Internal formula", DARK),
    ("Cross-sheet reference", TEAL),
    ("Modeled proxy / benchmark / macro forecast -- not directly disclosed", ORANGE),
]


def _col_widths(ws):
    set_col_widths(ws, {
        'A': 2, 'B': 2, 'C': 34, 'D': 16, 'E': 4, 'F': 12,
        'G': 2, 'H': 12, 'I': 12, 'J': 12, 'K': 12, 'L': 12, 'M': 12, 'N': 12, 'O': 12,
        'P': 4,
    })


def _all_cols():
    return ACTUAL_COLS + DATA_COLS


def _print_right_col():
    return get_column_letter(max(_all_cols()))


def _apply_print_setup(ws, blocks=None, right=None):
    right = right or _print_right_col()
    ws.page_setup.orientation = "landscape"
    ws.page_setup.scale = 95
    ws.print_options.horizontalCentered = True
    if blocks:
        ws.print_area = [f"$B${s}:${right}${e}" for s, e in blocks]
    else:
        ws.print_area = f"$B$1:${right}${ws.max_row}"
    ws.print_title_rows = "1:1"
    ws.oddFooter.left.text = "Page &[Page] of &[Pages]"
    ws.oddFooter.center.text = "&[Tab]"
    ws.oddFooter.right.text = "&[Date]&[Time]"


def _write_scenario_banner(ws, right_col):
    write(ws, 1, right_col, _scenario_banner_formula(), bold=True, txt_color=GOLD, halign="right")


def _period_label(year, is_actual):
    return f"{year}{'A' if is_actual else 'P'}"


def _period_labels(config):
    return [_period_label(y, True) for y in config.ACTUAL_YEARS] + \
           [_period_label(y, False) for y in config.YEARS if y not in config.ACTUAL_YEARS]


def _period_labels_proj(config):
    return [_period_label(y, False) for y in config.YEARS if y not in config.ACTUAL_YEARS]


def _linked_year_header_row(ws, row, cols, label_col=None):
    ws.row_dimensions[row].height = 14
    for c in range(1, 17):
        ws.cell(row=row, column=c).fill = fill(MED_BLUE)
    if label_col:
        write(ws, row, label_col, "", bg=MED_BLUE)
    for col in cols:
        write(ws, row, col, f"={_cell(MASTER_HEADER_ROW, col)}", bold=True, size=10,
              txt_color=WHITE, bg=MED_BLUE)


def _model_period_header(ws, R):
    ws.row_dimensions[R].height = 13
    for c in range(1, 17):
        ws.cell(row=R, column=c).fill = fill(MED_BLUE)
    write(ws, R, ACTUAL_COLS[len(ACTUAL_COLS) // 2], "Actual", bold=True, bg=MED_BLUE,
          txt_color=WHITE)
    write(ws, R, DATA_COLS[len(DATA_COLS) // 2], "Projected", bold=True, bg=MED_BLUE,
          txt_color=WHITE)
    return R + 1


def _assum_ref(A, key):
    """Cross-sheet reference to the Assumptions sheet's ASSUM_COL cell for `key` --
    absolute row/column so a formula containing it is safe to treat as a template even
    though nothing here currently copies formulas across cells."""
    return f"Assumptions!${get_column_letter(ASSUM_COL)}${A[key]}"


def _prev(i, model_row):
    """Cell reference to the prior period's value on the Model sheet."""
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
        write(ws, row, UNITS_COL, units, txt_color=MID_GRAY, italic=True, size=9, bg=row_bg)
    for i, col in enumerate(cols):
        val = formulas[i]
        is_formula = isinstance(val, str) and val.startswith("=")
        color = (TEAL if (is_formula and "Assumptions!" in val)
                 else DARK if is_formula else BLUE_INPUT)
        num(ws, row, col, val, fmt=fmt, bold=bold, bg=row_bg, txt_color=color)


def _write_actual_row(ws, row, label, values, bold=False, fmt='#,##0.0', units=None,
                       alt_idx=None, indent=0):
    _write_formula_row(ws, row, label, values, bold=bold, fmt=fmt, units=units,
                        alt_idx=alt_idx, indent=indent, cols=ACTUAL_COLS)


def _write_row(ws, row, label, actual_values, proj_formulas, bold=False, fmt='#,##0.0',
               units=None, alt_idx=None, indent=0):
    """Convenience: write one logical schedule row across ALL columns (actual + projected)
    in a single call -- actual_values is a 3-item list (hardcoded facts or same-column
    formula strings), proj_formulas is a 5-item list of live formula strings."""
    _write_actual_row(ws, row, label, actual_values, bold=bold, fmt=fmt, units=units,
                      alt_idx=alt_idx, indent=indent)
    _write_formula_row(ws, row, label, proj_formulas, bold=bold, fmt=fmt, units=units,
                       alt_idx=alt_idx, indent=indent, cols=DATA_COLS)


# ─────────────────────────────────────────────
# ASSUMPTIONS SHEET
# ─────────────────────────────────────────────

def _assum_row(ws, row, label, value, color, refs=None, key=None, fmt='#,##0.00', note=""):
    write(ws, row, LABEL_COL, label, bg=WHITE)
    num(ws, row, ASSUM_COL, value, fmt=fmt, txt_color=color)
    if note:
        write(ws, row, 10, note, txt_color=MID_GRAY, italic=True, size=9)
    if refs is not None and key is not None:
        refs[key] = row
    return row + 1


def _scenario_row(ws, row, label, base_value, mult_best_ref, mult_worst_ref, refs, key,
                  fmt='0.0%', best_is_delta=False, base_color=ORANGE):
    """Compact scenario-metric block: title row, blank spacer, an outlined ACTIVE row
    (CHOOSE on the scenario switch), then plain Base/Best/Worst rows. `refs[key]` is set
    to the ACTIVE row. If `best_is_delta`, the Best/Worst rows ADD the multiplier ref
    (a basis-point delta) instead of multiplying by it -- used for the cap-rate lever.
    `base_color` should reflect the Base value's true provenance (BLUE_INPUT for a
    disclosed/disclosed-derived figure, ORANGE -- the default -- for a genuinely modeled/
    placeholder/macro-forecast one); only the Base row's color is caller-controlled, since
    the Best/Worst rows are always live formulas off it (DARK, internal formula)."""
    write(ws, row, LABEL_COL, label, bold=True, txt_color=NAVY)
    row += 1
    row += 1

    active_row = row
    base_row = row + 1
    best_row = row + 2
    worst_row = row + 3
    active_formula = (f"=CHOOSE({SWITCH_CELL_REF},{_cell(base_row, ASSUM_COL)},"
                       f"{_cell(best_row, ASSUM_COL)},{_cell(worst_row, ASSUM_COL)})")
    num(ws, row, ASSUM_COL, active_formula, fmt=fmt, txt_color=TEAL, bold=True)
    outline_range(ws, row, [ASSUM_COL])
    row += 1

    write(ws, row, LABEL_COL, "    Base", txt_color=MID_GRAY, italic=True)
    num(ws, row, ASSUM_COL, base_value, fmt=fmt, txt_color=base_color)
    row += 1

    op = "+" if best_is_delta else "*"
    write(ws, row, LABEL_COL, "    Best", txt_color=MID_GRAY, italic=True)
    num(ws, row, ASSUM_COL, f"={_cell(base_row, ASSUM_COL)}{op}{mult_best_ref}", fmt=fmt, txt_color=DARK)
    row += 1

    write(ws, row, LABEL_COL, "    Worst", txt_color=MID_GRAY, italic=True)
    num(ws, row, ASSUM_COL, f"={_cell(base_row, ASSUM_COL)}{op}{mult_worst_ref}", fmt=fmt, txt_color=DARK)
    row += 1

    refs[key] = active_row
    return row


def build_assumptions(wb, config):
    ws = wb.create_sheet("Assumptions", index=2)
    ws.sheet_view.showGridLines = False
    _col_widths(ws)
    A = {}

    R = 1
    write(ws, R, LABEL_COL, config.BUSINESS_NAME, bold=True, size=14, txt_color=NAVY)
    _write_scenario_banner(ws, max(_all_cols()))
    R += 2
    write(ws, R, LABEL_COL, "Inputs and Assumptions", txt_color=MID_GRAY); R += 2

    section_header(ws, R, "Data Provenance Legend"); R += 1
    for label, color in PROVENANCE_LEGEND:
        write(ws, R, LABEL_COL, "■  " + label, txt_color=color, size=9)
        R += 1
    R += 1

    m = config.SCENARIO_MULTIPLIERS
    best_occ_ref = _cell(R, ASSUM_COL)
    R = _assum_row(ws, R, "Scenario multiplier -- Best (occupancy) [MODELED]", m["best"]["occupancy_mult"], ORANGE, fmt='0.00')
    worst_occ_ref = _cell(R, ASSUM_COL)
    R = _assum_row(ws, R, "Scenario multiplier -- Worst (occupancy) [MODELED]", m["worst"]["occupancy_mult"], ORANGE, fmt='0.00')
    best_esc_ref = _cell(R, ASSUM_COL)
    R = _assum_row(ws, R, "Scenario multiplier -- Best (escalation) [MODELED]", m["best"]["escalation_mult"], ORANGE, fmt='0.00')
    worst_esc_ref = _cell(R, ASSUM_COL)
    R = _assum_row(ws, R, "Scenario multiplier -- Worst (escalation) [MODELED]", m["worst"]["escalation_mult"], ORANGE, fmt='0.00')
    best_rate_ref = _cell(R, ASSUM_COL)
    R = _assum_row(ws, R, "Scenario multiplier -- Best (cost of debt) [MODELED]", m["best"]["rate_mult"], ORANGE, fmt='0.00')
    worst_rate_ref = _cell(R, ASSUM_COL)
    R = _assum_row(ws, R, "Scenario multiplier -- Worst (cost of debt) [MODELED]", m["worst"]["rate_mult"], ORANGE, fmt='0.00')
    best_cap_delta_ref = _cell(R, ASSUM_COL)
    R = _assum_row(ws, R, "Scenario delta -- Best (cap rate, bps) [MODELED]", m["best"]["cap_rate_delta"], ORANGE, fmt='0.00%')
    worst_cap_delta_ref = _cell(R, ASSUM_COL)
    R = _assum_row(ws, R, "Scenario delta -- Worst (cap rate, bps) [MODELED]", m["worst"]["cap_rate_delta"], ORANGE, fmt='0.00%')
    R += 1

    section_header(ws, R, "PROPERTY & RENTAL DRIVERS", bg=NAVY, txt_color=WHITE); R += 1
    ri = config.RENTAL_INCOME
    R = _scenario_row(ws, R, "Rental escalation (p.a.) [DISCLOSED-DERIVED]", ri["escalation"], best_esc_ref, worst_esc_ref,
                      A, "escalation", fmt='0.0%', base_color=BLUE_INPUT)
    R = _scenario_row(ws, R, "Stabilized occupancy target [DISCLOSED]", ri["occupancy_stabilized"], best_occ_ref, worst_occ_ref,
                      A, "occupancy_stabilized", fmt='0.0%', base_color=BLUE_INPUT)
    A["occupancy_h1_2025"] = R
    R = _assum_row(ws, R, "Portfolio occupancy, H1 2025 actual [DISCLOSED]", ri["occupancy_portfolio_h1_2025"],
                   BLUE_INPUT, fmt='0.0%')
    A["occupancy_recovery_years"] = R
    R = _assum_row(ws, R, "Occupancy recovery period (years) [MODELED]", ri["occupancy_recovery_years"], ORANGE, fmt='0')
    R += 1

    section_header(ws, R, "DEBT & GEARING", bg=NAVY, txt_color=WHITE); R += 1
    cap = config.CAPITAL
    A["opening_borrowings"] = R
    R = _assum_row(ws, R, "Borrowings, Jun-2025 actual [DISCLOSED]", cap["opening_borrowings"],
                   BLUE_INPUT, fmt='#,##0.0')
    R = _scenario_row(ws, R, "Weighted-average borrowing rate (projected) [MACRO]", cap["weighted_avg_rate_projected"],
                      best_rate_ref, worst_rate_ref, A, "weighted_avg_rate_projected", fmt='0.00%')
    A["issuance_rate"] = R
    R = _assum_row(ws, R, "Unit issuance rate (p.a., projected) [MODELED]", config.UNITS["issuance_rate"], ORANGE, fmt='0.0%')
    R += 1

    section_header(ws, R, "REGULATORY LIMITS (CMA I-REIT)", bg=NAVY, txt_color=WHITE); R += 1
    reg = config.REGULATORY
    A["payout_min"] = R
    R = _assum_row(ws, R, "Minimum distribution payout [DISCLOSED -- CMA]", reg["payout_min"],
                   BLUE_INPUT, fmt='0.0%')
    A["ltv_max"] = R
    R = _assum_row(ws, R, "Maximum LTV / gearing [DISCLOSED -- CMA]", reg["ltv_max"], BLUE_INPUT, fmt='0.0%')
    A["income_producing_min"] = R
    R = _assum_row(ws, R, "Minimum income-producing real estate % [DISCLOSED -- CMA]",
                   reg["income_producing_min"], BLUE_INPUT, fmt='0.0%')
    R += 1

    section_header(ws, R, "VALUATION (CAPM / cap rate)", bg=NAVY, txt_color=WHITE); R += 1
    v = config.VALUATION
    A["risk_free_rate"] = R
    R = _assum_row(ws, R, "Risk-free rate (Kenya 10Y bond) [DISCLOSED]", v["risk_free_rate"],
                   BLUE_INPUT, fmt='0.00%')
    A["beta"] = R
    R = _assum_row(ws, R, "Beta [PLACEHOLDER]", v["beta"], ORANGE, fmt='0.00')
    A["erp"] = R
    R = _assum_row(ws, R, "Equity risk premium (Kenya) [DISCLOSED]", v["equity_risk_premium"],
                   BLUE_INPUT, fmt='0.00%')
    A["cost_of_equity"] = R
    coe_formula = f"={_assum_ref(A, 'risk_free_rate')}+{_assum_ref(A, 'beta')}*{_assum_ref(A, 'erp')}"
    R = _assum_row(ws, R, "Cost of equity (CAPM)", coe_formula, DARK, fmt='0.00%')
    R = _scenario_row(ws, R, "Direct-capitalization cap rate [DISCLOSED-DERIVED]", v["cap_rate"], best_cap_delta_ref,
                      worst_cap_delta_ref, A, "cap_rate", fmt='0.00%', best_is_delta=True, base_color=BLUE_INPUT)
    A["nav_blend_weight"] = R
    R = _assum_row(ws, R, "Blend weight -- NAV [MODELED]", v["blend_weights"]["nav"], ORANGE, fmt='0.00')
    A["ddm_blend_weight"] = R
    R = _assum_row(ws, R, "Blend weight -- DDM [MODELED]", v["blend_weights"]["ddm"], ORANGE, fmt='0.00')
    A["cap_rate_blend_weight"] = R
    R = _assum_row(ws, R, "Blend weight -- Cap rate [MODELED]", v["blend_weights"]["cap_rate"], ORANGE, fmt='0.00')
    R += 1

    section_header(ws, R, "PROPERTY PORTFOLIO (as at 30 Jun 2025) [DISCLOSED]", bg=NAVY, txt_color=WHITE); R += 1
    write(ws, R, LABEL_COL, "Property", bold=True, txt_color=NAVY)
    write(ws, R, 5, "Beds", bold=True, txt_color=NAVY)
    write(ws, R, ASSUM_COL, f"Fair value ({config.CURRENCY_UNIT_ABBR})", bold=True, txt_color=NAVY)
    R += 1
    for p in config.PROPERTIES:
        write(ws, R, LABEL_COL, f"{p['name']} ({p['location']})")
        write(ws, R, 5, p["beds"])
        num(ws, R, ASSUM_COL, p["opening_fair_value"], fmt='#,##0.0', txt_color=BLUE_INPUT)
        R += 1
    total_row(ws, R, "Total", [None, None, sum(p["opening_fair_value"] for p in config.PROPERTIES)],
             [None, 5, ASSUM_COL]); R += 1

    ws.print_area = f"$B$1:$J${R}"
    ws.page_setup.orientation = "landscape"
    return A


# ─────────────────────────────────────────────
# MODEL SHEET
# ─────────────────────────────────────────────

def _r(config, key):
    """Look up a REIT ACTUALS field for every actual year, in ACTUAL_YEARS order."""
    return [config.ACTUALS[y][key] for y in config.ACTUAL_YEARS]


def _build_property_section(ws, config, A, M, R):
    section_header(ws, R, "PROPERTY PORTFOLIO", bg=NAVY, txt_color=WHITE); R += 1
    _linked_year_header_row(ws, R, _all_cols(), label_col=LABEL_COL); R += 1
    blank_row(ws, R); R += 1

    n_proj = len(DATA_COLS)
    opening_row = R
    closing_row = opening_row + 3  # opening / additions / fair value gain / closing -- fixed layout
    closing_actual = _r(config, "investment_property")
    fvg_actual = _r(config, "fair_value_gain")
    # 2023 has no prior-year closing on file, so its own opening is back-solved the same
    # way as the projected years' "additions" residual below: closing - fvg (no capex
    # assumed for the un-anchored first year). 2024/2025 opening is the true prior-year
    # disclosed closing (from note 7(a)'s own "At 1 January" column for 2024).
    opening_actual = [closing_actual[0] - fvg_actual[0]] + closing_actual[:-1]
    _write_actual_row(ws, R, "Opening Fair Value", opening_actual, units=_units(config))
    # References the PRIOR period's CLOSING balance (row `closing_row`), not this row's
    # own prior column -- otherwise Opening (and therefore Closing) never advances past
    # the first projected year.
    _write_formula_row(ws, R, "Opening Fair Value",
                       [f"={_prev(i, closing_row)}" for i in range(n_proj)], units=_units(config))
    R += 1

    additions_row = R
    # Additions & Acquisitions is the back-solved residual (closing - opening - fair
    # value gain) for actual years -- this correctly folds in FY2024's KES 1,480.0m
    # property acquisition (Note 7(a)), not just ordinary capex, so the closing-balance
    # formula below ties to the disclosed Investment Property figure exactly.
    additions_actual = [closing_actual[i] - opening_actual[i] - fvg_actual[i] for i in range(3)]
    additions_proj = [f"={_cell(opening_row, col)}*0.005" for col in DATA_COLS]
    _write_row(ws, R, "Additions & Acquisitions", additions_actual, additions_proj, units=_units(config))
    R += 1

    fvg_row = R
    fvg_proj = [f"={_cell(opening_row, DATA_COLS[i])}*{_assum_ref(A, 'escalation')}" for i in range(n_proj)]
    _write_row(ws, R, "Fair Value Gain", fvg_actual, fvg_proj, units=_units(config))
    R += 1

    closing_row = R
    closing_formulas_actual = [f"={_cell(opening_row, c)}+{_cell(additions_row, c)}+{_cell(fvg_row, c)}"
                               for c in ACTUAL_COLS]
    closing_formulas_proj = [f"={_cell(opening_row, c)}+{_cell(additions_row, c)}+{_cell(fvg_row, c)}"
                             for c in DATA_COLS]
    _write_formula_row(ws, R, "Investment Property (closing)", closing_formulas_actual,
                       bold=True, cols=ACTUAL_COLS, units=_units(config))
    _write_formula_row(ws, R, "Investment Property (closing)", closing_formulas_proj,
                       bold=True, cols=DATA_COLS, units=_units(config))
    M["investment_property"] = closing_row
    R += 2
    return R


def _build_rental_noi_section(ws, config, A, M, R):
    section_header(ws, R, "RENTAL INCOME & NET OPERATING INCOME", bg=NAVY, txt_color=WHITE); R += 1
    _linked_year_header_row(ws, R, _all_cols(), label_col=LABEL_COL); R += 1
    blank_row(ws, R); R += 1

    n_proj = len(DATA_COLS)
    occ_row = R
    occ_actual = [0.78, 0.85, config.RENTAL_INCOME["occupancy_portfolio_h1_2025"]]
    occ_proj = []
    for i in range(n_proj):
        prev_ref = _prev(i, occ_row)
        occ_proj.append(
            f"=MIN({_assum_ref(A,'occupancy_stabilized')},{prev_ref}+"
            f"({_assum_ref(A,'occupancy_stabilized')}-{_assum_ref(A,'occupancy_h1_2025')})"
            f"/{_assum_ref(A,'occupancy_recovery_years')})"
        )
    _write_row(ws, R, "Occupancy (portfolio blended)", occ_actual, occ_proj, fmt='0.0%')
    R += 1

    rental_row = R
    rental_actual = _r(config, "rental_income")
    rental_proj = []
    for i in range(n_proj):
        prev_ri = _prev(i, rental_row)
        prev_occ = _prev(i, occ_row)
        rental_proj.append(
            f"={prev_ri}*(1+{_assum_ref(A,'escalation')})*{_cell(occ_row, DATA_COLS[i])}/{prev_occ}"
        )
    _write_row(ws, R, "Rental Income", rental_actual, rental_proj, units=_units(config))
    M["rental_income"] = rental_row
    R += 1

    other_row = R
    _write_row(ws, R, "Other Income (parking, etc.)", [0.3, 0.3, 0.267], [0.3] * n_proj, units=_units(config))
    R += 1

    opinc_row = R
    opinc_formulas = [f"={_cell(rental_row, c)}+{_cell(other_row, c)}" for c in _all_cols()]
    _write_formula_row(ws, R, "Operating Income", opinc_formulas[:3], bold=True, cols=ACTUAL_COLS, units=_units(config))
    _write_formula_row(ws, R, "Operating Income", opinc_formulas[3:], bold=True, cols=DATA_COLS, units=_units(config))
    M["operating_income"] = opinc_row
    R += 2
    return R


def _build_opex_section(ws, config, results, A, M, R):
    section_header(ws, R, "OPERATING EXPENSES", bg=NAVY, txt_color=WHITE); R += 1
    _linked_year_header_row(ws, R, _all_cols(), label_col=LABEL_COL); R += 1
    blank_row(ws, R); R += 1

    n_proj = len(DATA_COLS)
    admin_row = R
    admin_actual = [round(results["opex"]["admin_total"][i], 3) for i in range(3)]
    admin_proj = [f"={_prev(i, admin_row)}*(1+{_assum_ref(A,'escalation')})" for i in range(n_proj)]
    _write_row(ws, R, "Admin & Property Operating Expenses", admin_actual, admin_proj, units=_units(config))
    R += 1

    fund_row = R
    fund_actual = [round(results["opex"]["fund_total"][i], 3) for i in range(3)]
    fund_proj = [f"={_prev(i, fund_row)}*(1+{_assum_ref(A,'escalation')})" for i in range(n_proj)]
    _write_row(ws, R, "Fund-level Expenses (management/trustee/custodian fees)", fund_actual, fund_proj,
              units=_units(config))
    R += 1

    total_opex_row = R
    formulas = [f"={_cell(admin_row, c)}+{_cell(fund_row, c)}" for c in _all_cols()]
    _write_formula_row(ws, R, "Total Operating Expenses", formulas[:3], bold=True, cols=ACTUAL_COLS, units=_units(config))
    _write_formula_row(ws, R, "Total Operating Expenses", formulas[3:], bold=True, cols=DATA_COLS, units=_units(config))
    M["opex_total"] = total_opex_row
    R += 1

    opprofit_row = R
    op_formulas = [f"={_cell(M['operating_income'], c)}-{_cell(total_opex_row, c)}" for c in _all_cols()]
    _write_formula_row(ws, R, "Operating Profit", op_formulas[:3], bold=True, cols=ACTUAL_COLS, units=_units(config))
    _write_formula_row(ws, R, "Operating Profit", op_formulas[3:], bold=True, cols=DATA_COLS, units=_units(config))
    M["operating_profit"] = opprofit_row
    R += 2
    return R


def _build_debt_section(ws, config, results, A, M, R):
    section_header(ws, R, "DEBT / GEARING", bg=NAVY, txt_color=WHITE); R += 1
    _linked_year_header_row(ws, R, _all_cols(), label_col=LABEL_COL); R += 1
    blank_row(ws, R); R += 1

    n_proj = len(DATA_COLS)
    borrow_row = R
    borrow_actual = _r(config, "borrowings")
    borrow_proj = [f"={_assum_ref(A, 'opening_borrowings')}"] * n_proj  # held flat in Base
    _write_row(ws, R, "Borrowings (closing)", borrow_actual, borrow_proj, units=_units(config))
    M["borrowings"] = borrow_row
    R += 1

    rate_row = R
    rate_actual = [round(results["debt"]["weighted_avg_rate"][i], 4) for i in range(3)]
    rate_proj = [f"={_assum_ref(A, 'weighted_avg_rate_projected')}"] * n_proj
    _write_row(ws, R, "Weighted-Average Interest Rate", rate_actual, rate_proj, fmt='0.00%')
    R += 1

    fc_row = R
    # Actual years: period-end balance x rate (no reliable prior-period opening balance
    # on file for 2023, so this uses the same simplification for all three actual years
    # rather than averaging for two of them and not the third).
    fc_formulas = [f"={_cell(borrow_row, c)}*{_cell(rate_row, c)}" for c in ACTUAL_COLS]
    fc_formulas_proj = [f"=AVERAGE({_prev(i, borrow_row)},{_cell(borrow_row, DATA_COLS[i])})*{_cell(rate_row, DATA_COLS[i])}"
                        for i in range(n_proj)]
    _write_formula_row(ws, R, "Finance Costs", fc_formulas, bold=True, cols=ACTUAL_COLS, units=_units(config))
    _write_formula_row(ws, R, "Finance Costs", fc_formulas_proj, bold=True, cols=DATA_COLS, units=_units(config))
    M["finance_costs"] = fc_row
    R += 2
    return R


def _build_income_statement_section(ws, config, results, A, M, R):
    section_header(ws, R, "INCOME STATEMENT", bg=NAVY, txt_color=WHITE); R += 1
    _linked_year_header_row(ws, R, _all_cols(), label_col=LABEL_COL); R += 1
    blank_row(ws, R); R += 1

    n_proj = len(DATA_COLS)
    fi_row = R
    fi_actual = [round(results["income_stmt"]["finance_income"][i], 2) for i in range(3)]
    fi_proj = [f"={_prev(i, fi_row)}*1.03" for i in range(n_proj)]
    _write_row(ws, R, "Finance Income", fi_actual, fi_proj, units=_units(config))
    M["finance_income"] = fi_row
    R += 1

    fvg_row = M["investment_property"] - 1  # Fair Value Gain row, written directly above closing in Property section
    write(ws, R, LABEL_COL, "Fair Value Gain (from Property Portfolio)")
    fvg_ref_formulas = [f"={_cell(fvg_row, c)}" for c in _all_cols()]
    _write_formula_row(ws, R, "Fair Value Gain (from Property Portfolio)", fvg_ref_formulas[:3],
                       cols=ACTUAL_COLS, units=_units(config))
    _write_formula_row(ws, R, "Fair Value Gain (from Property Portfolio)", fvg_ref_formulas[3:],
                       cols=DATA_COLS, units=_units(config))
    fvg_link_row = R
    M["fair_value_gain"] = fvg_link_row
    R += 1

    net_profit_row = R
    net_profit_actual = _r(config, "net_profit")
    net_profit_proj = [
        f"={_cell(M['operating_profit'], DATA_COLS[i])}+{_cell(fi_row, DATA_COLS[i])}"
        f"-{_cell(M['finance_costs'], DATA_COLS[i])}+{_cell(fvg_link_row, DATA_COLS[i])}"
        for i in range(n_proj)
    ]
    _write_row(ws, R, "Net Profit", net_profit_actual, net_profit_proj, bold=True, units=_units(config))
    M["net_profit"] = net_profit_row
    R += 2
    return R


def _build_distributable_income_section(ws, config, results, A, M, R):
    section_header(ws, R, "DISTRIBUTABLE INCOME & DISTRIBUTIONS", bg=NAVY, txt_color=WHITE); R += 1
    _linked_year_header_row(ws, R, _all_cols(), label_col=LABEL_COL); R += 1
    blank_row(ws, R); R += 1

    n_proj = len(DATA_COLS)
    dist_inc_row = R
    formulas = [f"={_cell(M['net_profit'], c)}-{_cell(M['fair_value_gain'], c)}" for c in _all_cols()]
    _write_formula_row(ws, R, "Distributable Income", formulas[:3], bold=True, cols=ACTUAL_COLS, units=_units(config))
    _write_formula_row(ws, R, "Distributable Income", formulas[3:], bold=True, cols=DATA_COLS, units=_units(config))
    M["distributable_income"] = dist_inc_row
    R += 1

    payout_row = R
    payout_actual = _r(config, "payout_ratio")
    payout_proj = [f"={_assum_ref(A, 'payout_min')}"] * n_proj
    _write_row(ws, R, "Payout Ratio", payout_actual, payout_proj, fmt='0.0%')
    M["payout_ratio"] = payout_row
    R += 1

    dividend_row = R
    div_formulas = [f"=MAX(0,{_cell(dist_inc_row, c)})*{_cell(payout_row, c)}" for c in _all_cols()]
    _write_formula_row(ws, R, "Dividend Declared", div_formulas[:3], bold=True, cols=ACTUAL_COLS, units=_units(config))
    _write_formula_row(ws, R, "Dividend Declared", div_formulas[3:], bold=True, cols=DATA_COLS, units=_units(config))
    M["dividend"] = dividend_row
    R += 1

    units_row = R
    units_actual = _r(config, "units_in_issue")
    units_proj = [f"={_prev(i, units_row)}*(1+{_assum_ref(A,'issuance_rate')})" for i in range(n_proj)]
    _write_row(ws, R, "Units in Issue (millions)", units_actual, units_proj, fmt='#,##0.000')
    M["units_in_issue"] = units_row
    R += 1

    dpu_row = R
    dpu_formulas = [f"=IF({_cell(units_row, c)}=0,0,{_cell(dividend_row, c)}/{_cell(units_row, c)})"
                    for c in _all_cols()]
    _write_formula_row(ws, R, "Distribution Per Unit", dpu_formulas[:3], bold=True, cols=ACTUAL_COLS, fmt='#,##0.00')
    _write_formula_row(ws, R, "Distribution Per Unit", dpu_formulas[3:], bold=True, cols=DATA_COLS, fmt='#,##0.00')
    M["distribution_per_unit"] = dpu_row
    R += 2
    return R


def _build_balance_sheet_section(ws, config, results, A, M, R):
    section_header(ws, R, "BALANCE SHEET", bg=NAVY, txt_color=WHITE); R += 1
    _linked_year_header_row(ws, R, _all_cols(), label_col=LABEL_COL); R += 1
    blank_row(ws, R); R += 1

    n_proj = len(DATA_COLS)
    other_liab_row = R
    other_liab_actual = [round(results["bs"]["other_liabilities"][i], 2) for i in range(3)]
    other_liab_proj = [f"={_prev(i, other_liab_row)}" for i in range(n_proj)]
    _write_row(ws, R, "Other Liabilities (payables etc.)", other_liab_actual, other_liab_proj, units=_units(config))
    R += 1

    total_liab_row = R
    tl_formulas = [f"={_cell(M['borrowings'], c)}+{_cell(other_liab_row, c)}" for c in _all_cols()]
    _write_formula_row(ws, R, "Total Liabilities", tl_formulas[:3], bold=True, cols=ACTUAL_COLS, units=_units(config))
    _write_formula_row(ws, R, "Total Liabilities", tl_formulas[3:], bold=True, cols=DATA_COLS, units=_units(config))
    M["total_liabilities"] = total_liab_row
    R += 1

    issuance_row = R
    issuance_actual = [0.0, 0.0, 0.0]
    R += 1  # row reserved; formula written below once M['units_in_issue'] exists

    nav_row = R
    nav_actual = _r(config, "nav")
    R += 1  # reserve; filled in after issuance formulas below

    total_assets_row = R
    R += 1

    other_assets_row = R
    R += 1

    nav_per_unit_row = R
    R += 1

    balance_check_row = R
    R += 1

    # Second pass: now that every row number is reserved, write the actual formula
    # strings (several rows reference each other out of the order they're laid out on
    # the page, e.g. Total Assets = NAV + Total Liabilities, written above NAV).
    latest_nav_per_unit_actual = results["bs"]["nav_per_unit"][2]
    issuance_formulas = [
        f"=MAX(0,{_cell(M['units_in_issue'], DATA_COLS[i])}-{_prev(i, M['units_in_issue'])})*{latest_nav_per_unit_actual:.4f}"
        for i in range(n_proj)
    ]
    _write_row(ws, issuance_row, "Unit Issuance Proceeds", issuance_actual, issuance_formulas, units=_units(config))
    M["issuance_proceeds"] = issuance_row

    nav_formulas_proj = [
        f"={_prev(i, nav_row)}+{_cell(M['net_profit'], DATA_COLS[i])}-{_cell(M['dividend'], DATA_COLS[i])}"
        f"+{_cell(issuance_row, DATA_COLS[i])}" for i in range(n_proj)
    ]
    _write_row(ws, nav_row, "Net Asset Value (NAV)", nav_actual, nav_formulas_proj, bold=True, units=_units(config))
    M["nav"] = nav_row

    ta_actual = _r(config, "total_assets")
    ta_formulas_proj = [f"={_cell(nav_row, c)}+{_cell(total_liab_row, c)}" for c in DATA_COLS]
    _write_row(ws, total_assets_row, "Total Assets", ta_actual, ta_formulas_proj, bold=True, units=_units(config))
    M["total_assets"] = total_assets_row

    oa_formulas = [f"={_cell(total_assets_row, c)}-{_cell(M['investment_property'], c)}" for c in _all_cols()]
    _write_formula_row(ws, other_assets_row, "Other Assets (cash, receivables)", oa_formulas[:3],
                       cols=ACTUAL_COLS, units=_units(config))
    _write_formula_row(ws, other_assets_row, "Other Assets (cash, receivables)", oa_formulas[3:],
                       cols=DATA_COLS, units=_units(config))
    M["other_assets"] = other_assets_row

    npu_formulas = [f"=IF({_cell(M['units_in_issue'], c)}=0,0,{_cell(nav_row, c)}/{_cell(M['units_in_issue'], c)})"
                    for c in _all_cols()]
    _write_formula_row(ws, nav_per_unit_row, "NAV per Unit", npu_formulas[:3], bold=True, cols=ACTUAL_COLS, fmt='#,##0.00')
    _write_formula_row(ws, nav_per_unit_row, "NAV per Unit", npu_formulas[3:], bold=True, cols=DATA_COLS, fmt='#,##0.00')
    M["nav_per_unit"] = nav_per_unit_row

    bc_formulas = [f"={_cell(total_assets_row, c)}-{_cell(nav_row, c)}-{_cell(total_liab_row, c)}"
                  for c in _all_cols()]
    _write_formula_row(ws, balance_check_row, "Balance Check (Assets - NAV - Liabilities)", bc_formulas[:3],
                       cols=ACTUAL_COLS, fmt='#,##0.000')
    _write_formula_row(ws, balance_check_row, "Balance Check (Assets - NAV - Liabilities)", bc_formulas[3:],
                       cols=DATA_COLS, fmt='#,##0.000')
    M["bs_check"] = balance_check_row

    R = balance_check_row + 2
    return R


def _build_regulatory_section(ws, config, results, A, M, R):
    section_header(ws, R, "REGULATORY COMPLIANCE (CMA I-REIT limits)", bg=NAVY, txt_color=WHITE); R += 1
    _linked_year_header_row(ws, R, _all_cols(), label_col=LABEL_COL); R += 1
    blank_row(ws, R); R += 1

    ltv_row = R
    formulas = [f"=IF({_cell(M['total_assets'], c)}=0,0,{_cell(M['borrowings'], c)}/{_cell(M['total_assets'], c)})"
               for c in _all_cols()]
    _write_formula_row(ws, R, "Loan-to-Value (LTV)", formulas[:3], cols=ACTUAL_COLS, fmt='0.0%')
    _write_formula_row(ws, R, "Loan-to-Value (LTV)", formulas[3:], cols=DATA_COLS, fmt='0.0%')
    M["ltv"] = ltv_row
    R += 1

    ipp_row = R
    formulas = [f"=IF({_cell(M['total_assets'], c)}=0,0,{_cell(M['investment_property'], c)}/{_cell(M['total_assets'], c)})"
               for c in _all_cols()]
    _write_formula_row(ws, R, "Income-Producing Real Estate %", formulas[:3], cols=ACTUAL_COLS, fmt='0.0%')
    _write_formula_row(ws, R, "Income-Producing Real Estate %", formulas[3:], cols=DATA_COLS, fmt='0.0%')
    M["income_producing_pct"] = ipp_row
    R += 2
    return R


def _build_master_check(ws, config, A, M, title_row):
    from openpyxl.formatting.rule import FormulaRule

    R = title_row
    section_header(ws, R, "MASTER CHECK", bg=GOLD, txt_color=DARK); R += 1
    write(ws, R, LABEL_COL,
         "Payout Check reads ERROR for actual years 2023-2025 by design -- Acorn's own "
         "disclosed payout ratios (78%/40.5%/34.1%) are genuinely below the 80% CMA "
         "minimum in those years; see research_output.md.",
         italic=True, txt_color=MID_GRAY, size=9)
    R += 1
    status_rows = []

    def _status_row(label, formulas):
        nonlocal R
        _write_formula_row(ws, R, label, formulas, bold=True, cols=_all_cols())
        status_rows.append(R)
        R += 1

    all_cols = _all_cols()
    _status_row("Balance Sheet Check (Assets = NAV + Liabilities)",
                [f'=IF(ABS({_cell(M["bs_check"], col)})<0.01,"OK","ERROR")' for col in all_cols])
    _status_row(f"LTV Check (<= {config.REGULATOR_NAME} 35% limit)",
                [f'=IF({_cell(M["ltv"], col)}<={_assum_ref(A, "ltv_max")},"OK","ERROR")' for col in all_cols])
    _status_row(f"Income-Producing Real Estate Check (>= {config.REGULATOR_NAME} 75% minimum)",
                [f'=IF({_cell(M["income_producing_pct"], col)}>={_assum_ref(A, "income_producing_min")},"OK","ERROR")'
                 for col in all_cols])
    _status_row(f"Distribution Payout Check (>= {config.REGULATOR_NAME} 80% minimum)",
                [f'=IF({_cell(M["payout_ratio"], col)}>={_assum_ref(A, "payout_min")},"OK","ERROR")'
                 for col in all_cols])

    for row in status_rows:
        cell_range = f"{_cell(row, all_cols[0])}:{_cell(row, all_cols[-1])}"
        ws.conditional_formatting.add(
            cell_range, FormulaRule(formula=[f'{_cell(row, all_cols[0])}="ERROR"'], fill=fill(RED_DARK)))
        ws.conditional_formatting.add(
            cell_range, FormulaRule(formula=[f'{_cell(row, all_cols[0])}="OK"'], fill=fill(GREEN_DRK)))

    return R


def build_model(wb, config, A, results):
    ws = wb.create_sheet("Model", index=4)
    ws.sheet_view.showGridLines = False
    _col_widths(ws)
    M = {}

    right_col = max(_all_cols())
    write(ws, 1, LABEL_COL, config.BUSINESS_NAME, bold=True, size=14, txt_color=NAVY)
    _write_scenario_banner(ws, right_col)
    write(ws, 2, LABEL_COL, "Model — Scenario-Switched (fully formula-linked)", txt_color=MID_GRAY)
    master_check_title_row = 4
    R = 10
    R = _model_period_header(ws, R)
    assert R == MASTER_HEADER_ROW, f"MASTER_HEADER_ROW drifted: expected {MASTER_HEADER_ROW}, got {R}"
    year_header_row(ws, R, _period_labels(config), _all_cols(), label_col=LABEL_COL, units_col=UNITS_COL)
    R += 1
    blank_row(ws, R, 8); R += 1

    blocks = []
    block_start = 1

    blocks.append((block_start, R - 1)); block_start = R
    R = _build_property_section(ws, config, A, M, R)
    blocks.append((block_start, R - 1)); block_start = R
    R = _build_rental_noi_section(ws, config, A, M, R)
    blocks.append((block_start, R - 1)); block_start = R
    R = _build_opex_section(ws, config, results, A, M, R)
    blocks.append((block_start, R - 1)); block_start = R
    R = _build_debt_section(ws, config, results, A, M, R)
    blocks.append((block_start, R - 1)); block_start = R
    R = _build_income_statement_section(ws, config, results, A, M, R)
    blocks.append((block_start, R - 1)); block_start = R
    R = _build_distributable_income_section(ws, config, results, A, M, R)
    blocks.append((block_start, R - 1)); block_start = R
    R = _build_balance_sheet_section(ws, config, results, A, M, R)
    blocks.append((block_start, R - 1)); block_start = R
    R = _build_regulatory_section(ws, config, results, A, M, R)
    blocks.append((block_start, R - 1))

    _build_master_check(ws, config, A, M, master_check_title_row)
    _apply_print_setup(ws, blocks=blocks, right=get_column_letter(right_col))

    return M


# ─────────────────────────────────────────────
# SUMMARY SHEET
# ─────────────────────────────────────────────

def build_summary(wb, config, A, M, scenarios, sensitivity):
    ws = wb.create_sheet("Summary", index=1)
    ws.sheet_view.showGridLines = False
    _col_widths(ws)

    R = 1
    write(ws, R, LABEL_COL, config.BUSINESS_NAME, bold=True, size=14, txt_color=NAVY)
    _write_scenario_banner(ws, max(_all_cols()))
    R += 2
    write(ws, R, LABEL_COL, "Summary — Key Metrics (Base/Best/Worst)", txt_color=MID_GRAY); R += 2

    section_header(ws, R, "KEY PERFORMANCE INDICATORS -- LATEST PROJECTED YEAR"); R += 1
    write(ws, R, LABEL_COL, "Metric", bold=True, txt_color=NAVY)
    write(ws, R, 5, "Base", bold=True, txt_color=NAVY)
    write(ws, R, 6, "Best", bold=True, txt_color=NAVY)
    write(ws, R, 7, "Worst", bold=True, txt_color=NAVY)
    R += 1

    def _kpi(label, path, fmt='#,##0.0'):
        nonlocal R
        write(ws, R, LABEL_COL, label)
        for col, scen in zip((5, 6, 7), ("base", "best", "worst")):
            node = scenarios[scen]
            for key in path:
                node = node[key]
            num(ws, R, col, node[-1] if isinstance(node, list) else node, fmt=fmt)
        R += 1

    _kpi("NAV per Unit (KES)", ("bs", "nav_per_unit"), fmt='#,##0.00')
    _kpi("Distribution per Unit (KES)", ("distributable", "distribution_per_unit"), fmt='#,##0.00')
    _kpi("LTV", ("regulatory", "ltv"), fmt='0.0%')
    _kpi("Net Profit", ("income_stmt", "net_profit"))
    _kpi("Blended Valuation (KES/unit)", ("valuation", "blended_value"), fmt='#,##0.00')
    R += 1

    section_header(ws, R, "NET PROFIT SENSITIVITY (average, one lever at a time)"); R += 1
    write(ws, R, LABEL_COL, "Driver", bold=True, txt_color=NAVY)
    write(ws, R, 5, "Downside", bold=True, txt_color=NAVY)
    write(ws, R, 6, "Upside", bold=True, txt_color=NAVY)
    write(ws, R, 7, "Detail", bold=True, txt_color=NAVY)
    R += 1
    for f in sensitivity["factors"]:
        write(ws, R, LABEL_COL, f["name"])
        num(ws, R, 5, f["downside"], fmt='0.0%', txt_color=RED_DARK)
        num(ws, R, 6, f["upside"], fmt='0.0%', txt_color=GREEN_DRK)
        write(ws, R, 7, f["detail"], size=9, txt_color=MID_GRAY)
        R += 1

    ws.print_area = f"$B$1:$H${R}"
    ws.page_setup.orientation = "landscape"


# ─────────────────────────────────────────────
# SCENARIOS SHEET
# ─────────────────────────────────────────────

def _scenario_metric_block(ws, row, config, title, unit, base_vals, best_vals, worst_vals, fmt):
    write(ws, row, LABEL_COL, title, bold=True, txt_color=NAVY); row += 1
    active_row = row
    row += 1
    write(ws, row, LABEL_COL, "    Base", italic=True, txt_color=MID_GRAY)
    for i, col in enumerate(DATA_COLS):
        num(ws, row, col, base_vals[i], fmt=fmt)
    row += 1
    write(ws, row, LABEL_COL, "    Best", italic=True, txt_color=MID_GRAY)
    for i, col in enumerate(DATA_COLS):
        num(ws, row, col, best_vals[i], fmt=fmt)
    row += 1
    write(ws, row, LABEL_COL, "    Worst", italic=True, txt_color=MID_GRAY)
    for i, col in enumerate(DATA_COLS):
        num(ws, row, col, worst_vals[i], fmt=fmt)
    row += 1
    for col in DATA_COLS:
        formula = (f"=CHOOSE({SWITCH_CELL_REF},{_cell(active_row+1, col)},"
                   f"{_cell(active_row+2, col)},{_cell(active_row+3, col)})")
        num(ws, active_row, col, formula, fmt=fmt, txt_color=TEAL, bold=True)
    outline_range(ws, active_row, DATA_COLS)
    return row + 1


def build_scenarios_sheet(wb, config, scenarios):
    ws = wb.create_sheet("Scenarios", index=3)
    ws.sheet_view.showGridLines = False
    _col_widths(ws)

    from openpyxl.worksheet.datavalidation import DataValidation

    write(ws, 1, LABEL_COL, config.BUSINESS_NAME, bold=True, size=14, txt_color=NAVY)
    write(ws, 2, LABEL_COL, "Scenario Switch", txt_color=MID_GRAY)
    write(ws, 5, LABEL_COL, "Active Scenario (1=Base, 2=Best, 3=Worst)", bold=True)
    num(ws, 5, 4, 1, fmt='0', bold=True, bg=None, txt_color=TEAL)
    dv = DataValidation(type="list", formula1='"1,2,3"', allow_blank=False)
    ws.add_data_validation(dv)
    dv.add(ws["D5"])
    write(ws, 6, LABEL_COL,
         "=\"Currently: \"&UPPER(CHOOSE(D5,\"Base\",\"Best\",\"Worst\"))&\" CASE\"",
         italic=True, txt_color=GOLD)

    R = 9
    year_header_row(ws, R, _period_labels_proj(config), DATA_COLS, label_col=LABEL_COL)
    R += 1
    blank_row(ws, R); R += 1

    section_header(ws, R, "PROJECTED-YEAR KPI COMPARISON (Base / Best / Worst)"); R += 1
    R += 1

    def series(scen, *path):
        node = scenarios[scen]
        for key in path:
            node = node[key]
        proj = node[-len(DATA_COLS):]
        return proj

    R = _scenario_metric_block(ws, R, config, "NAV per Unit (KES)", "", series("base", "bs", "nav_per_unit"),
                               series("best", "bs", "nav_per_unit"), series("worst", "bs", "nav_per_unit"),
                               fmt='#,##0.00')
    R = _scenario_metric_block(ws, R, config, "Distribution per Unit (KES)", "",
                               series("base", "distributable", "distribution_per_unit"),
                               series("best", "distributable", "distribution_per_unit"),
                               series("worst", "distributable", "distribution_per_unit"), fmt='#,##0.00')
    R = _scenario_metric_block(ws, R, config, "LTV", "", series("base", "regulatory", "ltv"),
                               series("best", "regulatory", "ltv"), series("worst", "regulatory", "ltv"), fmt='0.0%')
    R = _scenario_metric_block(ws, R, config, "Net Profit", _units(config), series("base", "income_stmt", "net_profit"),
                               series("best", "income_stmt", "net_profit"),
                               series("worst", "income_stmt", "net_profit"), fmt='#,##0.0')

    ws.print_area = f"$B$1:$O${R}"
    ws.page_setup.orientation = "landscape"


# ─────────────────────────────────────────────
# OUTPUT SHEET
# ─────────────────────────────────────────────

def build_output_sheet(wb, config, A, M, results):
    ws = wb.create_sheet("Output", index=5)
    ws.sheet_view.showGridLines = False
    _col_widths(ws)

    R = 1
    write(ws, R, LABEL_COL, config.BUSINESS_NAME, bold=True, size=14, txt_color=NAVY)
    _write_scenario_banner(ws, max(_all_cols()))
    R += 2
    write(ws, R, LABEL_COL, "Equity Valuation — Base Case", txt_color=MID_GRAY); R += 2

    section_header(ws, R, "COST OF EQUITY (CAPM)"); R += 1
    write(ws, R, LABEL_COL, "Risk-free rate"); num(ws, R, ASSUM_COL, f"={_assum_ref(A, 'risk_free_rate')}", fmt='0.00%'); R += 1
    write(ws, R, LABEL_COL, "Beta"); num(ws, R, ASSUM_COL, f"={_assum_ref(A, 'beta')}", fmt='0.00'); R += 1
    write(ws, R, LABEL_COL, "Equity risk premium"); num(ws, R, ASSUM_COL, f"={_assum_ref(A, 'erp')}", fmt='0.00%'); R += 1
    write(ws, R, LABEL_COL, "Cost of equity", bold=True)
    num(ws, R, ASSUM_COL, f"={_assum_ref(A, 'cost_of_equity')}", fmt='0.00%', bold=True)
    coe_cell = _cell(R, ASSUM_COL)
    R += 2

    section_header(ws, R, "NAV APPROACH (primary anchor)"); R += 1
    write(ws, R, LABEL_COL, "Latest NAV per Unit (KES)", bold=True, txt_color=NAVY)
    nav_formula = f"='Model'!{_cell(M['nav_per_unit'], DATA_COLS[-1])}"
    num(ws, R, ASSUM_COL, nav_formula, fmt='#,##0.00', bold=True, txt_color=NAVY)
    nav_value_row = R
    R += 2

    section_header(ws, R, "DIVIDEND DISCOUNT MODEL (DPU + terminal NAV/unit)"); R += 1
    write(ws, R, LABEL_COL,
         "Projected years only -- 2023-2025 are actual, already-paid distributions, "
         "not future cash flows to discount.", italic=True, txt_color=MID_GRAY, size=9)
    R += 1
    year_header_row(ws, R, _period_labels_proj(config), DATA_COLS, label_col=LABEL_COL); R += 1
    dpu_row = R
    dpu_formulas = [f"='Model'!{_cell(M['distribution_per_unit'], col)}" for col in DATA_COLS]
    _write_formula_row(ws, R, "Distribution per Unit", dpu_formulas, units="KES", cols=DATA_COLS)
    R += 1
    pv_dpu_row = R
    pv_formulas = [f"={_cell(dpu_row, col)}/(1+{coe_cell})^{i+1}" for i, col in enumerate(DATA_COLS)]
    _write_formula_row(ws, R, "PV of Distributions", pv_formulas, units="KES", cols=DATA_COLS)
    R += 1
    write(ws, R, LABEL_COL, "PV of Terminal NAV/Unit")
    pv_terminal_formula = f"={_cell(nav_value_row, ASSUM_COL)}/(1+{coe_cell})^{len(DATA_COLS)}"
    num(ws, R, ASSUM_COL, pv_terminal_formula, fmt='#,##0.00'); pv_terminal_row = R; R += 1
    write(ws, R, LABEL_COL, "DDM Implied Value per Unit (KES)", bold=True, txt_color=NAVY)
    ddm_formula = f"=SUM({_cell(pv_dpu_row, DATA_COLS[0])}:{_cell(pv_dpu_row, DATA_COLS[-1])})+{_cell(pv_terminal_row, ASSUM_COL)}"
    num(ws, R, ASSUM_COL, ddm_formula, fmt='#,##0.00', bold=True, txt_color=NAVY)
    ddm_value_row = R
    R += 2

    section_header(ws, R, "DIRECT CAPITALIZATION / CAP RATE"); R += 1
    write(ws, R, LABEL_COL, "Latest Operating Income")
    num(ws, R, ASSUM_COL, f"='Model'!{_cell(M['operating_income'], DATA_COLS[-1])}", fmt='#,##0.0')
    oi_row = R; R += 1
    write(ws, R, LABEL_COL, "Latest Total Opex")
    num(ws, R, ASSUM_COL, f"='Model'!{_cell(M['opex_total'], DATA_COLS[-1])}", fmt='#,##0.0')
    opex_row = R; R += 1
    write(ws, R, LABEL_COL, "Net Operating Income (NOI)")
    num(ws, R, ASSUM_COL, f"={_cell(oi_row, ASSUM_COL)}-{_cell(opex_row, ASSUM_COL)}", fmt='#,##0.0')
    noi_row = R; R += 1
    write(ws, R, LABEL_COL, "Cap rate"); num(ws, R, ASSUM_COL, f"={_assum_ref(A, 'cap_rate')}", fmt='0.00%')
    cap_rate_row = R; R += 1
    write(ws, R, LABEL_COL, "Implied Property Value")
    num(ws, R, ASSUM_COL, f"={_cell(noi_row, ASSUM_COL)}/{_cell(cap_rate_row, ASSUM_COL)}", fmt='#,##0.0')
    ipv_row = R; R += 1
    write(ws, R, LABEL_COL, "Less: Borrowings")
    num(ws, R, ASSUM_COL, f"=-'Model'!{_cell(M['borrowings'], DATA_COLS[-1])}", fmt='#,##0.0')
    debt_row = R; R += 1
    write(ws, R, LABEL_COL, "Implied Equity Value")
    num(ws, R, ASSUM_COL, f"={_cell(ipv_row, ASSUM_COL)}+{_cell(debt_row, ASSUM_COL)}", fmt='#,##0.0')
    ieq_row = R; R += 1
    write(ws, R, LABEL_COL, "Cap-Rate Implied Value per Unit (KES)", bold=True, txt_color=NAVY)
    num(ws, R, ASSUM_COL,
        f"={_cell(ieq_row, ASSUM_COL)}/'Model'!{_cell(M['units_in_issue'], DATA_COLS[-1])}",
        fmt='#,##0.00', bold=True, txt_color=NAVY)
    cap_rate_value_row = R
    R += 2

    section_header(ws, R, "PEER CROSS-CHECK & BLENDED VALUATION"); R += 1
    write(ws, R, LABEL_COL, "Average peer NAV discount/(premium)")
    num(ws, R, ASSUM_COL, results["valuation"]["avg_peer_discount"], fmt='0.0%')
    peer_disc_row = R; R += 1
    write(ws, R, LABEL_COL, "Peer-Implied Value per Unit (KES)")
    num(ws, R, ASSUM_COL, f"={_cell(nav_value_row, ASSUM_COL)}*(1+{_cell(peer_disc_row, ASSUM_COL)})", fmt='#,##0.00')
    peer_value_row = R; R += 2

    write(ws, R, LABEL_COL, "Blend weight -- NAV / DDM / Cap rate", size=9, txt_color=MID_GRAY)
    R += 1
    write(ws, R, LABEL_COL, "BLENDED VALUATION (KES per unit)", bold=True, size=12, txt_color=NAVY)
    blend_formula = (f"={_assum_ref(A,'nav_blend_weight')}*{_cell(nav_value_row, ASSUM_COL)}+"
                      f"{_assum_ref(A,'ddm_blend_weight')}*{_cell(ddm_value_row, ASSUM_COL)}+"
                      f"{_assum_ref(A,'cap_rate_blend_weight')}*{_cell(cap_rate_value_row, ASSUM_COL)}")
    num(ws, R, ASSUM_COL, blend_formula, fmt='#,##0.00', bold=True, txt_color=NAVY)
    M["blended_value"] = R
    R += 2

    section_header(ws, R, "SUMMARY TABLE"); R += 1
    write(ws, R, LABEL_COL, "Approach", bold=True); write(ws, R, 6, "Value (KES/unit)", bold=True); R += 1
    for label, row_ref in (("NAV", nav_value_row), ("DDM (dividends + terminal NAV)", ddm_value_row),
                           ("Direct capitalization / cap rate", cap_rate_value_row),
                           ("Peer cross-check", peer_value_row), ("Blended", M["blended_value"])):
        write(ws, R, LABEL_COL, label)
        num(ws, R, 6, f"={_cell(row_ref, ASSUM_COL)}", fmt='#,##0.00')
        R += 1

    ws.print_area = f"$B$1:$O${R}"
    ws.page_setup.orientation = "landscape"


# ─────────────────────────────────────────────
# SOURCES SHEET
# ─────────────────────────────────────────────

def build_sources_sheet(wb, config):
    sources = getattr(config, "SOURCES", None)
    if not sources:
        return

    ws = wb.create_sheet("Sources", index=6)
    ws.sheet_view.showGridLines = False
    set_col_widths(ws, {'A': 2, 'B': 2, 'C': 4, 'D': 62, 'E': 22, 'F': 40, 'G': 14, 'H': 4})

    header_row(ws, 1, f"{config.BUSINESS_NAME.upper()} — DATA SOURCES & REFERENCES",
                merge_to_col=7, start_col=3)
    write(ws, 2, 3,
          "Third-party market data and CMA regulatory limits used in this model's Output-sheet "
          "valuation and Model-sheet Regulatory Compliance section. Acorn's own audited/interim "
          "financial-statement figures are cited separately via research_output.md and the "
          "Assumptions sheet's data-provenance color legend.",
          italic=True, txt_color=MID_GRAY, size=9, wrap=True, valign="top")
    ws.merge_cells(start_row=2, start_column=3, end_row=2, end_column=7)
    ws.row_dimensions[2].height = 32
    R = 4

    section_header(ws, R, "REFERENCES", bg=NAVY, txt_color=WHITE); R += 1
    write(ws, R, 3, "#", bold=True, txt_color=NAVY)
    write(ws, R, 4, "Item / Value", bold=True, txt_color=NAVY)
    write(ws, R, 5, "Value", bold=True, txt_color=NAVY)
    write(ws, R, 6, "Source", bold=True, txt_color=NAVY)
    write(ws, R, 7, "Accessed", bold=True, txt_color=NAVY)
    R += 1

    for i, src in enumerate(sources, start=1):
        write(ws, R, 3, f"[{i}]", txt_color=MID_GRAY)
        write(ws, R, 4, src["item"], wrap=True)
        write(ws, R, 5, src.get("value", ""))
        if src.get("url"):
            safe_source = src["source"].replace('"', "'")
            write(ws, R, 6, f'=HYPERLINK("{src["url"]}","{safe_source}")', txt_color=TEAL)
        else:
            write(ws, R, 6, src["source"])
        write(ws, R, 7, src.get("accessed", ""))
        ws.row_dimensions[R].height = 26
        R += 1

    R += 1
    write(ws, R, 3,
          "Convention: Item/Value cited, Source (publisher — hyperlinked where a URL is "
          "available), Accessed (date the figure was pulled). See research_output.md for "
          "the full research log behind each entry, including two documented reconciliation "
          "gaps in Acorn's own interim filing.",
          italic=True, txt_color=MID_GRAY, size=9, wrap=True, valign="top")
    ws.merge_cells(start_row=R, start_column=3, end_row=R, end_column=7)
    ws.row_dimensions[R].height = 32
    R += 2

    section_header(ws, R, "MODELING METHODOLOGY (amber -- modeled / placeholder / macro-forecast assumptions)",
                    bg=NAVY, txt_color=WHITE); R += 1
    write(ws, R, 3,
          "Every amber-colored cell on the Assumptions sheet (see Data Provenance Legend) is a "
          "modeled proxy, analyst-judgment placeholder, or forward macro assumption -- not a "
          "figure taken directly from a filing. The formula/approach behind each is below; full "
          "rationale and citations (where any exist) are in research_output.md.",
          italic=True, txt_color=MID_GRAY, size=9, wrap=True, valign="top")
    ws.merge_cells(start_row=R, start_column=3, end_row=R, end_column=7)
    ws.row_dimensions[R].height = 28
    R += 1

    v, ri, cap, units = config.VALUATION, config.RENTAL_INCOME, config.CAPITAL, config.UNITS
    bw = v["blend_weights"]
    methodology = [
        ("Occupancy recovery period (years)",
         f"Value: {ri['occupancy_recovery_years']:.0f} years. Projected-year occupancy glides "
         "linearly from the disclosed actual rate toward the disclosed stabilized rate over "
         "this many years -- occupancy(t) = actual + min(1, years_since_last_actual / "
         "recovery_years) x (stabilized - actual). See "
         "reit_calculations.build_rental_income_noi()."),
        ("Unit issuance rate (p.a., projected)",
         f"Value: {units['issuance_rate']:.1%} p.a. Projected-year unit count compounds flat at "
         "this rate each year -- units[t] = units[t-1] x (1 + rate) -- modeling continued but "
         "slower capital-raising than the most recently disclosed issuance pace. See "
         "reit_calculations.build_units()."),
        ("Beta [PLACEHOLDER]",
         f"Value: {v['beta']:.2f}. Feeds CAPM cost of equity = risk-free rate + beta x equity "
         "risk premium (the DDM leg's discount rate). No instrument-specific beta regression is "
         "possible without liquid secondary-market trading; this is a defensive-moderate proxy "
         "typical of regulated income-generating real estate, flagged for replacement once a "
         "usable regression source exists."),
        ("Weighted-average borrowing rate (projected) [MACRO]",
         f"Value: {cap['weighted_avg_rate_projected']:.2%}. A forward assumption of where the "
         "cost of debt lands beyond the latest disclosed actual rate, based on the prevailing "
         "monetary easing/tightening cycle described in the source filings -- not itself a "
         "specific disclosed forecast."),
        ("Valuation blend weights (NAV / DDM / Cap rate)",
         f"Values: {bw['nav']:.0%} / {bw['ddm']:.0%} / {bw['cap_rate']:.0%}. Analyst-judgment "
         "weighting of the three valuation approaches -- blended_value = w_nav x NAV_per_unit + "
         "w_ddm x DDM_value + w_cap_rate x Cap_rate_value. NAV is typically weighted heaviest "
         "since it's the most reliable anchor for a property-holding entity (read directly off "
         "the Balance Sheet, not projected); DDM lightest since its discount rate rests on the "
         "weakest-sourced input (beta, above). See reit_calculations.build_valuation()."),
        ("Best/Worst scenario multipliers",
         "Illustrative +/- sensitivity bands applied to the Base case, not calibrated to a "
         "specific external stress scenario. Occupancy and rental escalation multiply the Base "
         "path; cost of debt multiplies the projected rate; the cap rate instead shifts by an "
         "additive bps delta (a lower cap rate implies a higher implied property value, and "
         "vice versa). See reit_calculations.build_scenario()."),
    ]
    for label, desc in methodology:
        write(ws, R, 4, label, bold=True, txt_color=ORANGE, size=9.5)
        R += 1
        write(ws, R, 4, desc, wrap=True, size=9, txt_color=MID_GRAY, valign="top")
        ws.merge_cells(start_row=R, start_column=4, end_row=R, end_column=7)
        ws.row_dimensions[R].height = 14 * -(-len(desc) // 130) + 8
        R += 2

    ws.page_setup.orientation = "landscape"
    ws.print_area = f"$A$1:$G${R}"


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
    write(ws, 7, LABEL_COL, f"REIT Financial Model & Valuation  |  {config.YEARS[0]} – {config.YEARS[-1]}",
          size=13, txt_color=GOLD, italic=True)

    write(ws, 9, LABEL_COL, config.COVER_INFO.get("Business_Description", ""),
          txt_color=DARK, wrap=True, size=10, valign="top")
    ws.merge_cells(start_row=9, start_column=LABEL_COL, end_row=9, end_column=10)
    ws.row_dimensions[9].height = 48

    info = [
        (11, "Currency:", f"{config.CURRENCY} – {config.CURRENCY_UNIT_ABBR}"),
        (12, "Projection Period:", config.COVER_INFO.get("Projection_Period", "")),
        (13, "Scenarios:", "Base Case  |  Best Case  |  Worst Case"),
        (14, "Prepared By:", config.COVER_INFO.get("Prepared_By", "")),
        (15, "Classification:", config.COVER_INFO.get("Classification", "")),
    ]
    for row, label, value in info:
        write(ws, row, 4, label, bold=True, txt_color=NAVY)
        write(ws, row, 7, value, txt_color=DARK)

    write(ws, 18, LABEL_COL, "Model Contents", bold=True, size=13, txt_color=NAVY)
    tabs = ["Summary", "Assumptions", "Scenarios",
            "Model (Property Portfolio, Rental/NOI, Debt, Statements, Regulatory Compliance)",
            "Output (NAV, DDM, Direct Capitalization, Peer Cross-Check)"]
    if getattr(config, "SOURCES", None):
        tabs.append("Sources (external market-data references)")
    for i, tab in enumerate(tabs):
        write(ws, 20 + i, 4, f"•  {tab}", txt_color=MID_GRAY)

    ws.page_setup.orientation = "landscape"
    ws.print_area = f"$A$1:$J${ws.max_row}"


# ─────────────────────────────────────────────
# PUBLIC ENTRY POINT
# ─────────────────────────────────────────────

def build_excel(config, results, output_path):
    """Build the full REIT financial model workbook.

    `results` (from reit_calculations.build_all()) is accepted for interface symmetry
    and as a ground-truth reference during development, but the Model sheet's calculated
    cells are independently reconstructed as live formulas -- see module docstring.
    """
    import openpyxl
    from bizplan.financial import reit_calculations

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    build_cover(wb, config)
    A = build_assumptions(wb, config)
    M = build_model(wb, config, A, results)
    scenarios = reit_calculations.build_scenarios(config)
    sensitivity = reit_calculations.build_sensitivity(config)
    build_summary(wb, config, A, M, scenarios, sensitivity)
    build_scenarios_sheet(wb, config, scenarios)
    build_output_sheet(wb, config, A, M, results)
    build_sources_sheet(wb, config)

    wb.save(output_path)
    return output_path

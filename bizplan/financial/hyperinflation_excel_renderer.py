"""Formula-linked Excel workbook for the Unilever hyperinflation-accounting model.

Every calculated cell is a live Excel formula, following the same FMI data-provenance
convention as the REIT renderer this replaces: BLUE = disclosed/hardcoded input, DARK =
internal formula, TEAL = cross-sheet reference, ORANGE = modeled/benchmark proxy.

Sheet chain: Cover -> Assumptions (raw inputs only) -> one schedule sheet per subsidiary
(each walking Local FS -> Inflation Index -> IAS 29 Restatement -> FX Translation ->
World A/B/C -> IAS 29 Impact, so the whole restatement mechanic is on one traceable
sheet) -> Consolidation -> Scenario_Comparison (World A/B/C side by side, the user's own
requested table shape) -> Validation_2025 -> Sources.

World A/B/C are shown side by side throughout, not switched via a single scenario cell
(unlike the REIT model's CHOOSE() switch) -- comparing all three simultaneously is the
actual pedagogical point here, not picking one.
"""

from openpyxl import Workbook
from openpyxl.utils import get_column_letter

from bizplan.financial.xl_helpers import (
    write, num, header_row, section_header, blank_row, data_row, total_row,
    set_col_widths, _cell, NAVY, MED_BLUE, WHITE, DARK, MID_GRAY, TOTAL_FILL,
    BLUE_INPUT, TEAL, ORANGE, GREEN_DRK, RED_DARK,
)

YEAR_COLS = {2024: 4, 2025: 5}  # column D, E
LABEL_COL = 3


def _yr_cols(config):
    return [YEAR_COLS[y] for y in config.YEARS]


def _assum_ref(row, col):
    return f"='Assumptions'!{get_column_letter(col)}{row}"


def _sheet_ref(sheet, row, col):
    return f"='{sheet}'!{get_column_letter(col)}{row}"


# ── Cover ────────────────────────────────────────────────────────────────

def _build_cover(wb, config):
    ws = wb.create_sheet("Cover")
    set_col_widths(ws, {"A": 3, "B": 3, "C": 90, "D": 16, "E": 16})
    header_row(ws, 2, config.BUSINESS_NAME, merge_to_col=6)
    row = 4
    info = config.COVER_INFO
    for label, key in [("Description", "Business_Description"), ("Period", "Projection_Period"),
                        ("Prepared by", "Prepared_By"), ("Classification", "Classification")]:
        write(ws, row, LABEL_COL, label, bold=True, txt_color=MID_GRAY)
        write(ws, row + 1, LABEL_COL, info[key], wrap=True)
        ws.row_dimensions[row + 1].height = 45
        row += 3
    section_header(ws, row, "Methodology")
    row += 1
    for line in [
        "World A -- plain current-rate method (no inflation restatement): the baseline "
        "the IAS 29 impact is measured against -- the 'disappearing plant' case.",
        "World B -- US GAAP temporal method (remeasurement): non-monetary items at "
        "historical FX, monetary items at current FX, remeasurement gain/loss to income.",
        "World C -- actual IFRS treatment: IAS 29 inflation restatement, then IAS 21 "
        "translation of the restated figures at the closing rate (Unilever's own policy).",
        "See Argentina_Schedules / Turkiye_Schedules for the full restatement chain, "
        "Scenario_Comparison for World A/B/C side by side, Validation_2025 for the "
        "model's 2025 roll-forward vs. Unilever's real 2025 disclosure.",
    ]:
        write(ws, row, LABEL_COL, line, wrap=True)
        ws.row_dimensions[row].height = 28
        row += 1
    return ws


# ── Assumptions (inputs only) ───────────────────────────────────────────

FIELDS = [
    ("index_open", "Inflation index -- opening", "index"),
    ("index_close", "Inflation index -- closing", "index"),
    ("fx_open", "FX rate -- opening (local/EUR)", "fx"),
    ("fx_close", "FX rate -- closing (local/EUR)", "fx"),
    ("rev", "Revenue (nominal, local)", "amt"),
    ("cogs", "COGS (nominal, local)", "amt"),
    ("opex", "Opex (nominal, local)", "amt"),
    ("dep", "Depreciation (nominal, local)", "amt"),
    ("capex", "Capex (nominal, local)", "amt"),
    ("nonmon_assets_open", "Non-monetary assets -- opening (prior-year restated)", "amt"),
    ("mon_assets_close", "Monetary assets -- closing", "amt"),
    ("mon_liab_close", "Monetary liabilities -- closing", "amt"),
    ("equity_open", "Equity -- opening (prior-year restated)", "amt"),
]


def _build_assumptions(wb, config):
    ws = wb.create_sheet("Assumptions")
    set_col_widths(ws, {"A": 3, "B": 3, "C": 46, "D": 16, "E": 16})
    header_row(ws, 2, "Assumptions -- Local-Currency Inputs (disclosed/illustrative)", merge_to_col=6)
    write(ws, 4, LABEL_COL, "", bg=MED_BLUE)
    for y in config.YEARS:
        write(ws, 4, YEAR_COLS[y], str(y), bold=True, txt_color=WHITE, bg=MED_BLUE, halign="center")

    refs = {}
    row = 6
    for name, sub in config.SUBSIDIARIES.items():
        section_header(ws, row, f"{name.upper()} -- {sub['local_currency']} "
                                 f"(hyperinflationary since {sub['hyperinflationary_since']})")
        row += 1
        refs[name] = {}
        for field, label, kind in FIELDS:
            fmt = '#,##0.00' if kind in ("index", "fx") else '#,##0.0'
            values = [config.ACTUALS[name][y].get(field) if field not in
                      ("index_open", "index_close") else config.INFLATION_INDICES[name][y][field]
                      for y in config.YEARS]
            if field in ("fx_open", "fx_close"):
                values = [config.FX_RATES[name][y][field] for y in config.YEARS]
            data_row(ws, row, label, values, _yr_cols(config), fmt=fmt, txt_color=BLUE_INPUT)
            refs[name][field] = row
            row += 1
        row += 1

    section_header(ws, row, "OTHER GROUP OPERATIONS (EUR, scenario-invariant)")
    row += 1
    other_row = row
    for label, key in [("Revenue", "revenue"), ("COGS", "cogs"), ("Operating profit", "operating_profit"),
                        ("Total assets", "total_assets"), ("Equity", "equity"),
                        ("Non-monetary assets", "non_monetary_assets"), ("Monetary gain/(loss)", "monetary_gain_loss")]:
        v = config.OTHER_GROUP_OPERATIONS_EUR[key]
        data_row(ws, row, label, [v] * len(config.YEARS), _yr_cols(config), txt_color=BLUE_INPUT)
        refs.setdefault("_other", {})[key] = row
        row += 1

    return ws, refs


# ── Per-subsidiary schedule sheet ───────────────────────────────────────

def _restate_rows(ws, row, refs_row, cols):
    """Writes the 02 Inflation Index + 03 IAS29 Restatement + 04 FX Translation (World C)
    + World A + World B + Impact sections. refs_row: dict field->Assumptions row for this
    subsidiary. Returns dict of local row numbers for downstream cross-sheet references."""
    r = {}

    def xref(field):
        return refs_row[field]

    section_header(ws, row, "01 -- LOCAL FS (nominal, from Assumptions)")
    row += 1
    for field, label, kind in FIELDS:
        fmt = '#,##0.00' if kind in ("index", "fx") else '#,##0.0'
        vals = [_assum_ref(xref(field), c) for c in cols]
        data_row(ws, row, label, vals, cols, fmt=fmt, txt_color=TEAL)
        r[field] = row
        row += 1
    row += 1

    section_header(ws, row, "02 -- INFLATION INDEX & FX (derived)")
    row += 1
    r["idx_avg"] = row
    data_row(ws, row, "Inflation index -- average (geometric mean)",
              [f"=SQRT({_cell(r['index_open'], c)}*{_cell(r['index_close'], c)})" for c in cols],
              cols, fmt='#,##0.00')
    row += 1
    r["fx_avg"] = row
    data_row(ws, row, "FX rate -- average (geometric mean)",
              [f"=SQRT({_cell(r['fx_open'], c)}*{_cell(r['fx_close'], c)})" for c in cols],
              cols, fmt='#,##0.00')
    row += 1
    r["f_close"] = row
    data_row(ws, row, "Restatement factor -- opening vintage (close/open)",
              [f"={_cell(r['index_close'], c)}/{_cell(r['index_open'], c)}" for c in cols], cols, fmt='0.000')
    row += 1
    r["f_avg"] = row
    data_row(ws, row, "Restatement factor -- in-year flows (close/avg)",
              [f"={_cell(r['index_close'], c)}/{_cell(r['idx_avg'], c)}" for c in cols], cols, fmt='0.000')
    row += 1
    r["wedge_r"] = row
    data_row(ws, row, "Inflation-vs-FX wedge r (=f_avg x fx_avg/fx_close)",
              [f"={_cell(r['f_avg'], c)}*{_cell(r['fx_avg'], c)}/{_cell(r['fx_close'], c)}" for c in cols],
              cols, fmt='0.000', txt_color=ORANGE)
    row += 2

    section_header(ws, row, "03 -- IAS 29 RESTATEMENT (local currency, year-end purchasing power)")
    row += 1
    for key, label, formula_fn in [
        ("r_rev", "Revenue, restated", lambda c: f"={_cell(r['rev'], c)}*{_cell(r['f_avg'], c)}"),
        ("r_cogs", "COGS, restated", lambda c: f"={_cell(r['cogs'], c)}*{_cell(r['f_avg'], c)}"),
        ("r_opex", "Opex, restated", lambda c: f"={_cell(r['opex'], c)}*{_cell(r['f_avg'], c)}"),
        ("r_dep", "Depreciation, restated", lambda c: f"={_cell(r['dep'], c)}*{_cell(r['f_avg'], c)}"),
    ]:
        r[key] = row
        data_row(ws, row, label, [formula_fn(c) for c in cols], cols)
        row += 1
    r["r_opprofit"] = row
    data_row(ws, row, "Operating profit, restated", [
        f"={_cell(r['r_rev'], c)}-{_cell(r['r_cogs'], c)}-{_cell(r['r_opex'], c)}-{_cell(r['r_dep'], c)}"
        for c in cols], cols, bold=True)
    row += 1
    r["r_nonmon"] = row
    data_row(ws, row, "Non-monetary assets, restated", [
        f"={_cell(r['nonmon_assets_open'], c)}*{_cell(r['f_close'], c)}"
        f"+{_cell(r['capex'], c)}*{_cell(r['f_avg'], c)}-{_cell(r['r_dep'], c)}" for c in cols], cols)
    row += 1
    r["r_total_assets"] = row
    data_row(ws, row, "Total assets, restated", [
        f"={_cell(r['r_nonmon'], c)}+{_cell(r['mon_assets_close'], c)}" for c in cols], cols, bold=True)
    row += 1
    r["r_equity_open"] = row
    data_row(ws, row, "Equity (opening), restated", [
        f"={_cell(r['equity_open'], c)}*{_cell(r['f_close'], c)}" for c in cols], cols)
    row += 1
    r["monetary_gain_loss_local"] = row
    data_row(ws, row, "Net monetary gain/(loss) -- balancing plug", [
        f"=({_cell(r['r_total_assets'], c)}-{_cell(r['mon_liab_close'], c)})"
        f"-{_cell(r['r_equity_open'], c)}-{_cell(r['r_opprofit'], c)}" for c in cols],
        cols, bold=True, txt_color=RED_DARK)
    row += 2

    section_header(ws, row, "04 -- FX TRANSLATION -- World C (IAS 21, closing rate)")
    row += 1
    worlds = {}
    for key, label, num_row, denom in [
        ("C_revenue", "Revenue (EUR)", "r_rev", "fx_close"),
        ("C_cogs", "COGS (EUR)", "r_cogs", "fx_close"),
        ("C_opex", "Opex (EUR)", "r_opex", "fx_close"),
        ("C_dep", "Depreciation (EUR)", "r_dep", "fx_close"),
        ("C_opprofit", "Operating profit (EUR)", "r_opprofit", "fx_close"),
        ("C_totalassets", "Total assets (EUR)", "r_total_assets", "fx_close"),
        ("C_nonmon", "Non-monetary assets (EUR)", "r_nonmon", "fx_close"),
        ("C_monetary", "Net monetary gain/(loss) (EUR)", "monetary_gain_loss_local", "fx_close"),
    ]:
        r[key] = row
        data_row(ws, row, label, [f"={_cell(r[num_row], c)}/{_cell(r[denom], c)}" for c in cols],
                  cols, bold=(key in ("C_opprofit", "C_totalassets")))
        row += 1
    row += 1

    section_header(ws, row, "WORLD A -- Plain Current-Rate (no restatement)")
    row += 1
    r["n_nonmon"] = row
    data_row(ws, row, "Non-monetary assets, nominal", [
        f"={_cell(r['nonmon_assets_open'], c)}+{_cell(r['capex'], c)}-{_cell(r['dep'], c)}" for c in cols], cols)
    row += 1
    r["n_total_assets"] = row
    data_row(ws, row, "Total assets, nominal", [
        f"={_cell(r['n_nonmon'], c)}+{_cell(r['mon_assets_close'], c)}" for c in cols], cols)
    row += 1
    for key, label, num_row in [
        ("A_revenue", "Revenue (EUR)", "rev"), ("A_cogs", "COGS (EUR)", "cogs"),
        ("A_opex", "Opex (EUR)", "opex"), ("A_dep", "Depreciation (EUR)", "dep"),
    ]:
        r[key] = row
        data_row(ws, row, label, [f"={_cell(r[num_row], c)}/{_cell(r['fx_avg'], c)}" for c in cols], cols)
        row += 1
    r["A_opprofit"] = row
    data_row(ws, row, "Operating profit (EUR)", [
        f"=({_cell(r['rev'], c)}-{_cell(r['cogs'], c)}-{_cell(r['opex'], c)}-{_cell(r['dep'], c)})"
        f"/{_cell(r['fx_avg'], c)}" for c in cols], cols, bold=True)
    row += 1
    r["A_totalassets"] = row
    data_row(ws, row, "Total assets (EUR)", [
        f"={_cell(r['n_total_assets'], c)}/{_cell(r['fx_close'], c)}" for c in cols], cols, bold=True)
    row += 1
    r["A_monetary"] = row
    data_row(ws, row, "Net monetary gain/(loss) (EUR)", [0.0 for _ in cols], cols)
    row += 2

    section_header(ws, row, "WORLD B -- US GAAP Temporal Method (remeasurement)")
    row += 1
    r["b_nonmon"] = row
    data_row(ws, row, "Non-monetary assets (EUR, historical FX)", [
        f"={_cell(r['nonmon_assets_open'], c)}/{_cell(r['fx_open'], c)}"
        f"+{_cell(r['capex'], c)}/{_cell(r['fx_avg'], c)}-{_cell(r['dep'], c)}/{_cell(r['fx_avg'], c)}"
        for c in cols], cols)
    row += 1
    r["b_monassets"] = row
    data_row(ws, row, "Monetary assets (EUR, current FX)", [
        f"={_cell(r['mon_assets_close'], c)}/{_cell(r['fx_close'], c)}" for c in cols], cols)
    row += 1
    r["b_monliab"] = row
    data_row(ws, row, "Monetary liabilities (EUR, current FX)", [
        f"={_cell(r['mon_liab_close'], c)}/{_cell(r['fx_close'], c)}" for c in cols], cols)
    row += 1
    r["b_equity_open"] = row
    data_row(ws, row, "Equity, opening (EUR, historical FX)", [
        f"={_cell(r['equity_open'], c)}/{_cell(r['fx_open'], c)}" for c in cols], cols)
    row += 1
    r["B_totalassets"] = row
    data_row(ws, row, "Total assets (EUR)", [
        f"={_cell(r['b_nonmon'], c)}+{_cell(r['b_monassets'], c)}" for c in cols], cols, bold=True)
    row += 1
    r["B_monetary"] = row
    data_row(ws, row, "Remeasurement gain/(loss) (EUR) -- balancing plug", [
        f"=({_cell(r['b_nonmon'], c)}+{_cell(r['b_monassets'], c)})-{_cell(r['b_monliab'], c)}"
        f"-{_cell(r['b_equity_open'], c)}-{_cell(r['A_opprofit'], c)}" for c in cols],
        cols, bold=True, txt_color=RED_DARK)
    row += 2

    section_header(ws, row, "IAS 29 IMPACT (World C minus World A) -- vs. Unilever's own disclosure")
    row += 1
    r["impact_totalassets"] = row
    data_row(ws, row, "Total assets impact",
              [f"={_cell(r['C_totalassets'], c)}-{_cell(r['A_totalassets'], c)}" for c in cols], cols, bold=True)
    row += 1
    r["impact_turnover"] = row
    data_row(ws, row, "Turnover impact",
              [f"={_cell(r['C_revenue'], c)}-{_cell(r['A_revenue'], c)}" for c in cols], cols, bold=True)
    row += 1
    r["impact_opprofit"] = row
    data_row(ws, row, "Operating profit impact",
              [f"={_cell(r['C_opprofit'], c)}-{_cell(r['A_opprofit'], c)}" for c in cols], cols, bold=True)
    row += 1
    r["impact_monetary"] = row
    data_row(ws, row, "Net monetary gain/(loss)",
              [f"={_cell(r['C_monetary'], c)}" for c in cols], cols, bold=True, txt_color=RED_DARK)
    row += 1

    return r, row


def _build_subsidiary_sheet(wb, config, name, assum_refs):
    sub = config.SUBSIDIARIES[name]
    ws = wb.create_sheet(f"{name.capitalize()}_Schedules")
    set_col_widths(ws, {"A": 3, "B": 3, "C": 52, "D": 16, "E": 16})
    header_row(ws, 2, f"{name.capitalize()} ({sub['local_currency']}) -- Hyperinflation Schedule Chain",
                merge_to_col=6)
    write(ws, 4, LABEL_COL, "", bg=MED_BLUE)
    for y in config.YEARS:
        write(ws, 4, YEAR_COLS[y], str(y), bold=True, txt_color=WHITE, bg=MED_BLUE, halign="center")
    rows, _ = _restate_rows(ws, 6, assum_refs[name], _yr_cols(config))
    return ws, rows


# ── Consolidation ───────────────────────────────────────────────────────

def _build_consolidation(wb, config, sub_sheet_rows, assum_refs):
    """Consolidated group EUR figures under World C (actual, as reported) for each year,
    combining both subsidiaries' World-C schedule rows with the rest of the group."""
    ws = wb.create_sheet("Consolidation")
    set_col_widths(ws, {"A": 3, "B": 3, "C": 46, "D": 16, "E": 16})
    header_row(ws, 2, "05 -- Parent Consolidation (World C -- actual IFRS treatment)", merge_to_col=6)
    write(ws, 4, LABEL_COL, "", bg=MED_BLUE)
    for y in config.YEARS:
        write(ws, 4, YEAR_COLS[y], str(y), bold=True, txt_color=WHITE, bg=MED_BLUE, halign="center")

    row = 6
    lines = [("C_revenue", "Revenue"), ("C_cogs", "COGS"), ("C_opprofit", "Operating profit"),
             ("C_totalassets", "Total assets"), ("C_nonmon", "Non-monetary assets"),
             ("C_monetary", "Net monetary gain/(loss)")]
    other_key_map = {"C_revenue": "revenue", "C_cogs": "cogs", "C_opprofit": "operating_profit",
                      "C_totalassets": "total_assets", "C_nonmon": "non_monetary_assets",
                      "C_monetary": "monetary_gain_loss"}
    total_rows = {}
    for key, label in lines:
        vals = []
        for c in config.YEARS:
            col = YEAR_COLS[c]
            other_row = assum_refs["_other"][other_key_map[key]]
            terms = [f"'Argentina_Schedules'!{get_column_letter(col)}{sub_sheet_rows['argentina'][key]}",
                     f"'Turkiye_Schedules'!{get_column_letter(col)}{sub_sheet_rows['turkiye'][key]}",
                     f"'Assumptions'!{get_column_letter(col)}{other_row}"]
            vals.append("=" + "+".join(terms))
        data_row(ws, row, label, vals, _yr_cols(config), bold=(key in ("C_opprofit", "C_totalassets")),
                  txt_color=TEAL)
        total_rows[key] = row
        row += 1

    row += 1
    section_header(ws, row, "GROUP RATIOS")
    row += 1
    r_roa, r_at, r_de = row, row + 1, row + 2
    data_row(ws, r_roa, "Return on assets (Op. profit / Total assets)",
              [f"={_cell(total_rows['C_opprofit'], c)}/{_cell(total_rows['C_totalassets'], c)}"
               for c in _yr_cols(config)], _yr_cols(config), fmt='0.0%')
    data_row(ws, r_at, "Asset turnover (Revenue / Total assets)",
              [f"={_cell(total_rows['C_revenue'], c)}/{_cell(total_rows['C_totalassets'], c)}"
               for c in _yr_cols(config)], _yr_cols(config), fmt='0.00x')
    row += 3
    total_rows["roa"], total_rows["asset_turnover"] = r_roa, r_at
    return ws, total_rows


# ── Scenario comparison (World A/B/C side by side) ──────────────────────

def _build_scenario_comparison(wb, config, sub_sheet_rows):
    ws = wb.create_sheet("Scenario_Comparison")
    set_col_widths(ws, {"A": 3, "B": 3, "C": 40, "D": 15, "E": 15, "F": 15})
    header_row(ws, 2, "World A / B / C Side-by-Side -- Argentina + Turkiye Combined "
                       "(hyperinflationary subsidiaries only; see Consolidation for the full group)",
                merge_to_col=7)
    world_cols = {"A": 4, "B": 5, "C": 6}
    world_label = {"A": "World A -- Current Rate", "B": "World B -- US GAAP Temporal",
                   "C": "World C -- IFRS (IAS29+21)"}

    for year in config.YEARS:
        row = 4 if year == config.YEARS[0] else row_after_prev
        section_header(ws, row, f"YEAR {year}")
        row += 1
        write(ws, row, LABEL_COL, "", bg=MED_BLUE)
        for w, col in world_cols.items():
            write(ws, row, col, world_label[w], bold=True, txt_color=WHITE, bg=MED_BLUE, halign="center")
        row += 1
        yc = YEAR_COLS[year]

        line_defs = [
            ("Revenue", {"A": "A_revenue", "B": "A_revenue", "C": "C_revenue"}),
            ("COGS", {"A": "A_cogs", "B": "A_cogs", "C": "C_cogs"}),
            ("Operating profit", {"A": "A_opprofit", "B": "A_opprofit", "C": "C_opprofit"}),
            ("Non-monetary assets (PPE etc.)", {"A": "n_nonmon", "B": "b_nonmon", "C": "C_nonmon"}),
            ("Total assets", {"A": "A_totalassets", "B": "B_totalassets", "C": "C_totalassets"}),
            ("Net monetary / remeasurement gain-(loss)", {"A": "A_monetary", "B": "B_monetary", "C": "C_monetary"}),
        ]
        for label, keymap in line_defs:
            vals = []
            for w in ("A", "B", "C"):
                terms = []
                for sub in ("argentina", "turkiye"):
                    key = keymap[w]
                    src_row = sub_sheet_rows[sub].get(key)
                    if key == "n_nonmon" and w == "A":
                        src_row = sub_sheet_rows[sub]["n_nonmon"]
                        terms.append(f"'{sub.capitalize()}_Schedules'!{get_column_letter(yc)}{src_row}"
                                     f"/'{sub.capitalize()}_Schedules'!{get_column_letter(yc)}"
                                     f"{sub_sheet_rows[sub]['fx_close']}")
                    else:
                        terms.append(f"'{sub.capitalize()}_Schedules'!{get_column_letter(yc)}{src_row}")
                vals.append("=" + "+".join(terms))
            data_row(ws, row, label, vals, [world_cols["A"], world_cols["B"], world_cols["C"]], bold=True)
            row += 1
        row += 1
        row_after_prev = row

    return ws


# ── Validation vs 2025 disclosure ───────────────────────────────────────

def _build_validation(wb, config, model_results):
    ws = wb.create_sheet("Validation_2025")
    set_col_widths(ws, {"A": 3, "B": 3, "C": 36, "D": 14, "E": 14, "F": 14})
    header_row(ws, 2, "Model 2025 Roll-Forward vs. Unilever's Real 2025 Disclosure", merge_to_col=7)
    row = 4
    write(ws, row, 4, "Model", bold=True, bg=MED_BLUE, txt_color=WHITE, halign="center")
    write(ws, row, 5, "Disclosed", bold=True, bg=MED_BLUE, txt_color=WHITE, halign="center")
    write(ws, row, 6, "Gap (Model-Disclosed)", bold=True, bg=MED_BLUE, txt_color=WHITE, halign="center")
    row += 1
    validation = model_results[max(config.YEARS)]["validation"]
    for name in config.SUBSIDIARIES:
        section_header(ws, row, name.upper())
        row += 1
        for k, label in [("total_assets", "Total assets impact"), ("turnover", "Turnover impact"),
                          ("operating_profit", "Operating profit impact"),
                          ("net_monetary_gain_loss", "Net monetary gain/(loss)")]:
            g = validation[name][k]
            same = g["same_sign"]
            data_row(ws, row, label, [g["model"], g["disclosed"], g["abs_gap"]], [4, 5, 6], fmt='#,##0.0',
                      txt_color=GREEN_DRK if same else RED_DARK)
            row += 1
        row += 1
    write(ws, row, LABEL_COL, "See examples/unilever/research_output.md for full discussion of why "
          "total-assets impact structurally cannot flip sign in this model, and why Turkiye's 2025 "
          "operating-profit assumption differs from a pure roll-forward.", wrap=True, italic=True,
          txt_color=MID_GRAY)
    ws.row_dimensions[row].height = 40
    return ws


# ── Sources ──────────────────────────────────────────────────────────────

def _build_sources(wb, config):
    ws = wb.create_sheet("Sources")
    set_col_widths(ws, {"A": 3, "B": 3, "C": 46, "D": 30, "E": 22, "F": 14, "G": 50})
    header_row(ws, 2, "Sources", merge_to_col=7)
    row = 4
    for label, col in [("Item", 3), ("Value", 4), ("Source", 5), ("Accessed", 6), ("URL", 7)]:
        write(ws, row, col, label, bold=True, bg=MED_BLUE, txt_color=WHITE)
    row += 1
    for s in config.SOURCES:
        write(ws, row, 3, s["item"], wrap=True)
        write(ws, row, 4, s.get("value", ""), wrap=True)
        write(ws, row, 5, s.get("source", ""))
        write(ws, row, 6, s.get("accessed", ""))
        write(ws, row, 7, s.get("url", ""), wrap=True)
        ws.row_dimensions[row].height = 28
        row += 1
    return ws


# ── Entry point ──────────────────────────────────────────────────────────

def build_workbook(config, model_results):
    wb = Workbook()
    wb.remove(wb.active)
    _build_cover(wb, config)
    _, assum_refs = _build_assumptions(wb, config)
    sub_sheet_rows = {}
    for name in config.SUBSIDIARIES:
        _, rows = _build_subsidiary_sheet(wb, config, name, assum_refs)
        sub_sheet_rows[name] = rows
    _build_consolidation(wb, config, sub_sheet_rows, assum_refs)
    _build_scenario_comparison(wb, config, sub_sheet_rows)
    _build_validation(wb, config, model_results)
    _build_sources(wb, config)
    return wb


def build_excel(config, model_results, output_path):
    wb = build_workbook(config, model_results)
    wb.save(output_path)
    return output_path

# Copyright (c) 2026 Edwin Njeru. Licensed under the MIT License (see LICENSE).

"""Formula-linked Excel workbook for the Garanti BBVA net-monetary-position
reconstruction (BLUEPRINT.md Phase 5). Deliberately lean compared to
`hyperinflation_excel_renderer.py` — this model has one real balance sheet to classify
and one derived estimate to check against one real disclosed figure, not a three-world
scenario comparison across a fictional subsidiary.

Sheets: Cover, Balance_Sheet (every line item, flagged monetary/non-monetary, both
years, as published), Monetary_Position (classification totals, the opening-position
recovery, the CPI-growth estimate, and the estimate-vs-disclosed gap — all live
formulas), Sources. Same FMI colour convention as every other renderer in this repo:
BLUE = disclosed input, DARK = internal formula, TEAL = cross-sheet reference.
"""

from openpyxl import Workbook
from openpyxl.utils import get_column_letter

from bizplan.financial.xl_helpers import (
    write, num, header_row, section_header, blank_row, data_row, total_row,
    set_col_widths, BLUE_INPUT, TEAL, DARK, MID_GRAY, RED_DARK,
)

YEAR_COLS = {2024: 4, 2025: 5}
LABEL_COL = 3


def _sheet_ref(sheet, row, col):
    return f"='{sheet}'!{get_column_letter(col)}{row}"


def _build_cover(wb, config):
    ws = wb.create_sheet("Cover")
    set_col_widths(ws, {"A": 3, "B": 3, "C": 95, "D": 16, "E": 16})
    header_row(ws, 2, config.BUSINESS_NAME, merge_to_col=6)
    row = 4
    for line in [
        "Real, as-disclosed IFRS-basis, IAS 29-restated consolidated financial "
        "statements (FY2024, FY2025) -- not a calibrated fictional subsidiary (contrast "
        "with the Unilever model elsewhere in this repo).",
        "Balance_Sheet: every line item from Garanti BBVA's own published statement, "
        "flagged monetary or non-monetary.",
        "Monetary_Position: an independently *estimated* net monetary gain/(loss) for "
        "FY2025 (opening net monetary position x the period's CPI growth, sign-flipped) "
        "checked against Garanti's own disclosed 'Gain/(loss) on net monetary position, "
        "net' line -- an attempted reconstruction, not a calibration, so the resulting "
        "gap is reported, not tuned away. See research_output.md for why it's large.",
    ]:
        write(ws, row, LABEL_COL, line, wrap=True)
        ws.row_dimensions[row].height = 30
        row += 1
    return ws


def _build_balance_sheet(wb, config):
    ws = wb.create_sheet("Balance_Sheet")
    set_col_widths(ws, {"A": 3, "B": 3, "C": 55, "D": 16, "E": 16, "F": 14})
    header_row(ws, 2, "Consolidated Statement of Financial Position (TL thousands, as published)",
               merge_to_col=6)
    write(ws, 3, YEAR_COLS[2024], "2024", bold=True, halign="right")
    write(ws, 3, YEAR_COLS[2025], "2025", bold=True, halign="right")
    write(ws, 3, 6, "Monetary?", bold=True, halign="center")

    row = 5
    rows = {}  # (side, label) -> row number, for Monetary_Position's SUMIF-free direct refs
    for side_key, side_label in [("assets", "Assets"), ("liabilities", "Liabilities")]:
        section_header(ws, row, side_label)
        row += 1
        for label, vals in config.BALANCE_SHEET[side_key].items():
            data_row(ws, row, label,
                     [vals["2024"], vals["2025"]], [YEAR_COLS[2024], YEAR_COLS[2025]],
                     txt_color=BLUE_INPUT)
            write(ws, row, 6, "Monetary" if vals["monetary"] else "Non-monetary",
                  txt_color=MID_GRAY, halign="center")
            rows[(side_key, label)] = row
            row += 1
        total_row(ws, row, f"Total {side_label}",
                 [sum(v["2024"] for v in config.BALANCE_SHEET[side_key].values()),
                  sum(v["2025"] for v in config.BALANCE_SHEET[side_key].values())],
                 [YEAR_COLS[2024], YEAR_COLS[2025]])
        rows[(side_key, "__total__")] = row
        row += 2

    section_header(ws, row, "Equity")
    row += 1
    for label, vals in config.BALANCE_SHEET["equity"].items():
        data_row(ws, row, label,
                 [vals["2024"], vals["2025"]], [YEAR_COLS[2024], YEAR_COLS[2025]],
                 txt_color=BLUE_INPUT)
        row += 1
    total_row(ws, row, "Total Equity",
             [sum(v["2024"] for v in config.BALANCE_SHEET["equity"].values()),
              sum(v["2025"] for v in config.BALANCE_SHEET["equity"].values())],
             [YEAR_COLS[2024], YEAR_COLS[2025]])
    row += 1

    return ws, rows


def _build_monetary_position(wb, config, bs_rows):
    ws = wb.create_sheet("Monetary_Position")
    set_col_widths(ws, {"A": 3, "B": 3, "C": 60, "D": 18, "E": 18})
    header_row(ws, 2, "Net Monetary Position & Estimated Monetary Result", merge_to_col=6)

    row = 4
    write(ws, row, YEAR_COLS[2024], "2024", bold=True, halign="right")
    write(ws, row, YEAR_COLS[2025], "2025", bold=True, halign="right")
    row += 2

    # Monetary assets / liabilities totals, built as live SUM formulas over Balance_Sheet
    # rows flagged monetary -- not a Python-computed constant, so a formula-evaluator
    # cross-check actually exercises the classification.
    def _monetary_sum_formula(side_key, year):
        mon_rows = [r for (sk, lbl), r in bs_rows.items()
                    if sk == side_key and lbl != "__total__"
                    and config.BALANCE_SHEET[side_key][lbl]["monetary"]]
        col = get_column_letter(YEAR_COLS[year])
        return "=" + "+".join(f"'Balance_Sheet'!{col}{r}" for r in mon_rows)

    for label, side_key in [("Monetary assets", "assets"), ("Monetary liabilities", "liabilities")]:
        write(ws, row, LABEL_COL, label)
        write(ws, row, YEAR_COLS[2024], _monetary_sum_formula(side_key, 2024),
              bold=False)
        write(ws, row, YEAR_COLS[2025], _monetary_sum_formula(side_key, 2025),
              bold=False)
        for c in (YEAR_COLS[2024], YEAR_COLS[2025]):
            ws.cell(row=row, column=c).number_format = '#,##0'
            ws.cell(row=row, column=c).font = ws.cell(row=row, column=c).font.copy(color=TEAL)
        if label == "Monetary assets":
            r_assets = row
        else:
            r_liabilities = row
        row += 1

    r_nmp = row
    write(ws, row, LABEL_COL, "Net monetary position (assets - liabilities)", bold=True)
    for year in (2024, 2025):
        col = get_column_letter(YEAR_COLS[year])
        write(ws, row, YEAR_COLS[year], f"={col}{r_assets}-{col}{r_liabilities}", bold=True)
        ws.cell(row=row, column=YEAR_COLS[year]).number_format = '#,##0'
    row += 2

    section_header(ws, row, "FY2025 estimate vs. Garanti's own disclosed figure")
    row += 1

    r_cpi2023 = row
    write(ws, row, LABEL_COL, "TÜİK CPI index, Dec-2023 (2003=100)")
    num(ws, row, YEAR_COLS[2025], config.CPI_INDEX[2023], fmt='#,##0.00', txt_color=BLUE_INPUT)
    row += 1
    r_cpi2024 = row
    write(ws, row, LABEL_COL, "TÜİK CPI index, Dec-2024")
    num(ws, row, YEAR_COLS[2025], config.CPI_INDEX[2024], fmt='#,##0.00', txt_color=BLUE_INPUT)
    row += 1
    r_cpi2025 = row
    write(ws, row, LABEL_COL, "TÜİK CPI index, Dec-2025")
    num(ws, row, YEAR_COLS[2025], config.CPI_INDEX[2025], fmt='#,##0.00', txt_color=BLUE_INPUT)
    row += 2

    r_nmp2024_orig = row
    write(ws, row, LABEL_COL,
          "Opening (FY2024-end) net monetary position, recovered to its own Dec-2024 "
          "purchasing power (as-shown Dec-2024 column is in Dec-2025 PP terms)", wrap=True)
    ws.row_dimensions[row].height = 28
    col2024 = get_column_letter(YEAR_COLS[2024])
    col2025 = get_column_letter(YEAR_COLS[2025])
    write(ws, row, YEAR_COLS[2025],
          f"={col2024}{r_nmp}*{col2025}{r_cpi2024}/{col2025}{r_cpi2025}")
    ws.cell(row=row, column=YEAR_COLS[2025]).number_format = '#,##0'
    row += 1

    r_growth = row
    write(ws, row, LABEL_COL, "FY2025 CPI growth rate")
    write(ws, row, YEAR_COLS[2025],
          f"={get_column_letter(YEAR_COLS[2025])}{r_cpi2025}/{get_column_letter(YEAR_COLS[2025])}{r_cpi2024}-1")
    ws.cell(row=row, column=YEAR_COLS[2025]).number_format = '0.0%'
    row += 1

    r_estimate = row
    write(ws, row, LABEL_COL, "Estimated monetary gain/(loss): -opening NMP x growth", bold=True)
    col = get_column_letter(YEAR_COLS[2025])
    write(ws, row, YEAR_COLS[2025], f"=-{col}{r_nmp2024_orig}*{col}{r_growth}", bold=True)
    ws.cell(row=row, column=YEAR_COLS[2025]).number_format = '#,##0'
    row += 1

    r_disclosed = row
    write(ws, row, LABEL_COL, "Garanti's own disclosed 'Gain/(loss) on net monetary "
          "position, net'", txt_color=BLUE_INPUT)
    num(ws, row, YEAR_COLS[2025], config.DISCLOSED_NET_MONETARY_RESULT["2025"],
        fmt='#,##0', txt_color=BLUE_INPUT)
    row += 1

    r_gap = row
    write(ws, row, LABEL_COL, "Gap (estimate - disclosed)", bold=True, txt_color=RED_DARK)
    col = get_column_letter(YEAR_COLS[2025])
    write(ws, row, YEAR_COLS[2025], f"={col}{r_estimate}-{col}{r_disclosed}", bold=True,
          txt_color=RED_DARK)
    ws.cell(row=row, column=YEAR_COLS[2025]).number_format = '#,##0'
    row += 1

    write(ws, row, LABEL_COL, "Gap, as a multiple of the disclosed figure", bold=True,
          txt_color=RED_DARK)
    col = get_column_letter(YEAR_COLS[2025])
    write(ws, row, YEAR_COLS[2025], f"={col}{r_estimate}/{col}{r_disclosed}", bold=True,
          txt_color=RED_DARK)
    ws.cell(row=row, column=YEAR_COLS[2025]).number_format = '0.0"x"'
    row += 2

    write(ws, row, LABEL_COL,
          "See research_output.md for why this gap is large (~14x) and what it implies "
          "about a bank's monetary exposure vs. a non-financial company's.", wrap=True,
          italic=True, txt_color=MID_GRAY)
    ws.row_dimensions[row].height = 28

    return ws


def _build_sources(wb, config):
    ws = wb.create_sheet("Sources")
    set_col_widths(ws, {"A": 3, "B": 3, "C": 105})
    header_row(ws, 2, "Sources", merge_to_col=4)
    row = 4
    for src in config.SOURCES:
        write(ws, row, LABEL_COL, src, wrap=True)
        ws.row_dimensions[row].height = 30
        row += 1
    return ws


def build_workbook(config):
    wb = Workbook()
    wb.remove(wb.active)
    _build_cover(wb, config)
    _, bs_rows = _build_balance_sheet(wb, config)
    _build_monetary_position(wb, config, bs_rows)
    _build_sources(wb, config)
    return wb


def save_workbook(config, output_dir):
    import os
    wb = build_workbook(config)
    path = os.path.join(output_dir, f"{config.OUTPUT_PREFIX}.xlsx")
    wb.save(path)
    return path

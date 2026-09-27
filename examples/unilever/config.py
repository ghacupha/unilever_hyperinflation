"""Unilever plc — hyperinflation-accounting teaching model (CFA LII Multinational
Operations). config.py is the single source of truth for every assumption.

This does NOT reproduce Unilever's real Argentina/Türkiye subsidiary financial
statements (not public at this granularity) — it is a small, fully hand-traceable
fictional subsidiary for each, whose local-currency inputs were solved algebraically
(see research_output.md) so that running them through the model's IAS 29 restatement +
IAS 21 translation reproduces Unilever's own **real disclosed 2024 IAS 29 impact**
figures (Total assets/Turnover/Operating profit/Net monetary gain-loss) almost exactly.
2025 is a rolled-forward validation, not re-solved to fit — see research_output.md for
the documented gap between the model's 2025 output and Unilever's real 2025 disclosure.

Currency unit: EUR millions (consolidated), local-currency figures in local nominal
units (ARS, TRY) as disclosed-scale illustrative inputs.
"""

BUSINESS_NAME = "Unilever plc — Argentina & Türkiye Hyperinflation Model"
OUTPUT_PREFIX = "Unilever_Hyperinflation"
CURRENCY = "EUR"
CURRENCY_UNIT_ABBR = "EURm"
YEARS = [2024, 2025]
ACTUAL_YEARS = [2024, 2025]

# Primary listing — Unilever plc is UK-domiciled and LSE-primary-listed (also dual-listed
# on Euronext Amsterdam as UNA and NYSE as UL, but LSE/ULVR is the primary line).
TICKER = "ULVR"
EXCHANGE = "LSE"

COVER_INFO = dict(
    Business_Description=(
        "CFA Level II Financial Statement Analysis — Multinational Operations reading, "
        "illustrated with Unilever plc's real disclosed application of IAS 29 "
        "(Financial Reporting in Hyperinflationary Economies) to its Argentina "
        "(hyperinflationary since 1 Jul 2018) and Türkiye (hyperinflationary since "
        "1 Jul 2022) subsidiaries. Local subsidiary accounts are a small fictional "
        "illustration calibrated to reproduce Unilever's own disclosed 2024 IAS 29 "
        "impact figures; see research_output.md."
    ),
    Projection_Period="2024 (calibrated) + 2025 (rolled-forward validation)",
    Prepared_By="Hyperinflation Model Generator (bizplan)",
    Classification="Illustrative teaching model — not investment advice, not a reproduction "
                    "of Unilever's actual subsidiary financial statements",
)

# ---------------------------------------------------------------------------
# Subsidiaries: local currency, IAS 29 status, and the item-level monetary/
# non-monetary classification the CFA reading tests.
# ---------------------------------------------------------------------------

SUBSIDIARIES = {
    "argentina": dict(
        local_currency="ARS",
        hyperinflationary_since="2018-07-01",
        monetary_items=["cash_and_receivables", "payables_and_debt"],
        non_monetary_items=["inventory_and_ppe"],
    ),
    "turkiye": dict(
        local_currency="TRY",
        hyperinflationary_since="2022-07-01",
        monetary_items=["cash_and_receivables", "payables_and_debt"],
        non_monetary_items=["inventory_and_ppe"],
    ),
}

# Item-level monetary/non-monetary/treatment table (CFA teaching reference, not fed
# directly into the calculation engine, which works off subsidiary-level aggregates).
ITEM_CLASSIFICATION = [
    dict(item="Cash",          monetary=True,  ias29_treatment="Not restated",           translation="Closing FX"),
    dict(item="Receivables",   monetary=True,  ias29_treatment="Not restated",           translation="Closing FX"),
    dict(item="Inventory",     monetary=False, ias29_treatment="Restate for inflation",  translation="Closing FX after restatement"),
    dict(item="PPE",           monetary=False, ias29_treatment="Restate for inflation",  translation="Closing FX after restatement"),
    dict(item="Payables",      monetary=True,  ias29_treatment="Not restated",           translation="Closing FX"),
    dict(item="Debt",          monetary=True,  ias29_treatment="Not restated",           translation="Closing FX"),
    dict(item="Share capital", monetary=False, ias29_treatment="Restate from contribution date", translation="Closing FX"),
    dict(item="Revenue",       monetary=None,  ias29_treatment="Restate from transaction dates",  translation="Closing FX"),
    dict(item="COGS",          monetary=None,  ias29_treatment="Derived from restated inventory", translation="Closing FX"),
    dict(item="Depreciation",  monetary=None,  ias29_treatment="Based on restated PPE",  translation="Closing FX"),
]

# ---------------------------------------------------------------------------
# Inflation indices and FX rates. index_open/close are the general price index at the
# start/end of the year (base 100 at the start of the model, 1 Jan 2024); fx_open/close
# are LOCAL CURRENCY UNITS PER 1 EUR. 2025 index_open/fx_open equal 2024's close (an
# ongoing hyperinflationary entity rolls its own prior-year-restated closing balance
# forward — see BLUEPRINT.md).
# ---------------------------------------------------------------------------

INFLATION_INDICES = {
    "argentina": {2024: dict(index_open=100.0, index_close=218.0),   # ~118% CPI inflation
                  2025: dict(index_open=218.0, index_close=218.0 * 1.30)},  # decelerating to ~30%
    "turkiye":   {2024: dict(index_open=100.0, index_close=144.0),   # ~44% CPI inflation
                  2025: dict(index_open=144.0, index_close=144.0 * 1.28)},  # ~28%
}

FX_RATES = {
    "argentina": {2024: dict(fx_open=850.0, fx_close=1010.0),          # ARS/EUR — crawling peg, FX lagged inflation
                  2025: dict(fx_open=1010.0, fx_close=1010.0 * 1.436)},  # April-2025 float: FX now outpaces inflation
    "turkiye":   {2024: dict(fx_open=33.5, fx_close=39.5),             # TRY/EUR
                  2025: dict(fx_open=39.5, fx_close=39.5 * 1.35)},
}

# World A = plain current-rate method (no restatement) — the "disappearing plant" case.
# World B = US GAAP temporal method (remeasurement).
# World C = actual IFRS treatment: IAS 29 restatement + IAS 21 closing-rate translation.
ACCOUNTING_SCENARIOS = {
    "current_rate":     dict(label="World A — Plain current-rate (no hyperinflation)"),
    "us_gaap_temporal": dict(label="World B — US GAAP temporal method (remeasurement)"),
    "ias29_ias21":      dict(label="World C — IFRS actual (IAS 29 + IAS 21 closing-rate)"),
}

# ---------------------------------------------------------------------------
# Subsidiary nominal local-currency inputs. 2024 figures were solved algebraically to
# reproduce Unilever's real disclosed 2024 IAS 29 impact table exactly (see
# research_output.md's "Calibration" section for the derivation); 2025 figures are the
# 2024 model mechanically rolled forward with updated macro assumptions above, not
# re-solved — a genuine out-of-sample validation, with the resulting gap documented.
# equity_open is the subsidiary's opening equity, already stated in prior-year-end
# restated (purchasing-power) terms, as IAS 29 requires for an ongoing hyperinflationary
# entity.
# ---------------------------------------------------------------------------

ACTUALS = {
    "argentina": {
        2024: dict(
            rev=601_159.0, cogs=356_513.4, opex=189_757.1, dep=28_751.1, capex=31_626.2,
            nonmon_assets_open=404_550.9, mon_assets_close=250_000.0, mon_liab_close=657_084.7,
            equity_open=297_500.0,
        ),
        2025: dict(
            rev=601_159.0 * 1.30, cogs=356_513.4 * 1.30, opex=189_757.1 * 1.30, dep=28_751.1 * 1.30,
            capex=31_626.2 * 1.30,
            nonmon_assets_open=886_166.0,   # 2024's IAS29-restated closing non-monetary assets
            mon_assets_close=250_000.0 * 1.30, mon_liab_close=657_084.7 * 1.30,
            equity_open=479_081.3,          # 2024's IAS29-restated closing equity
        ),
    },
    "turkiye": {
        2024: dict(
            rev=64_717.7, cogs=40_983.2, opex=21_813.7, dep=3_305.1, capex=3_635.6,
            nonmon_assets_open=5_685.0, mon_assets_close=8_000.0, mon_liab_close=4_302.5,
            equity_open=9_380.0,
        ),
        2025: dict(
            rev=64_717.7 * 1.28, cogs=40_983.2 * 1.16, opex=21_813.7 * 1.16, dep=3_305.1 * 1.28,
            capex=3_635.6 * 1.28,
            nonmon_assets_open=8_583.0,     # 2024's IAS29-restated closing non-monetary assets
            mon_assets_close=8_000.0 * 1.28, mon_liab_close=4_302.5 * 1.28,
            equity_open=12_280.5,           # 2024's IAS29-restated closing equity
        ),
    },
}

# The rest of the group (non-hyperinflationary operations), EUR millions, scenario-
# invariant — an illustrative scale so the consolidated group total is plausible next
# to Unilever's real group size, without claiming to reproduce it.
OTHER_GROUP_OPERATIONS_EUR = dict(
    revenue=58_000.0, cogs=28_000.0, operating_profit=8_500.0,
    total_assets=45_000.0, equity=20_000.0, non_monetary_assets=22_000.0,
    monetary_gain_loss=0.0,
)

# ---------------------------------------------------------------------------
# Real disclosed IAS 29 impact figures (EURm) — what the model's 2024 output is
# calibrated against, and what the 2025 roll-forward is validated (not fitted) against.
# Source: Unilever plc Form 20-F / Annual Report, hyperinflation accounting policy note.
# ---------------------------------------------------------------------------

DISCLOSED_IMPACT_2024 = {
    "argentina": dict(total_assets=474.0, turnover=230.0, operating_profit=10.0, net_monetary_gain_loss=-206.0),
    "turkiye":   dict(total_assets=65.0,  turnover=187.0, operating_profit=-4.0, net_monetary_gain_loss=11.0),
}

VALIDATION_ACTUALS = {
    "argentina": dict(total_assets=-199.0, turnover=-90.0, operating_profit=-54.0, net_monetary_gain_loss=-46.0),
    "turkiye":   dict(total_assets=-20.0,  turnover=-16.0, operating_profit=-46.0, net_monetary_gain_loss=-10.0),
}

# ---------------------------------------------------------------------------
# Market-perception angle: does analyst consensus on Unilever price in the
# Argentina/Türkiye hyperinflation treatment, or does it get overlooked as a "non-cash
# accounting adjustment"? [PLACEHOLDER] — replace with real consensus commentary once
# Stage 2 (price/consensus research) has run live.
# ---------------------------------------------------------------------------

CONSENSUS = dict(
    ticker="ULVR", exchange="LSE",
    note=(
        "[PLACEHOLDER] Analyst consensus commentary on Unilever typically discusses "
        "Argentina/Türkiye as an 'FX headwind' to reported (constant-currency-adjusted) "
        "turnover, but rarely singles out the net monetary gain/loss line or "
        "distinguishes IAS 29 restatement from ordinary FX translation. Stage 2 should "
        "research real sell-side notes and confirm or correct this."
    ),
)

VALUATION = dict(
    note="[PLACEHOLDER] — Stage 2/3 of the report pipeline populate this from real "
         "consensus + a mechanical Buy/Hold/Sell signal comparing IFRS-actual value to "
         "a 'if the market naively used plain current-rate' mispricing check.",
)

SOURCES = [
    dict(item="Unilever plc — 2024 Annual Report on Form 20-F (hyperinflation accounting policy note)",
         value="Argentina/Türkiye 2024 IAS29 impact table",
         source="U.S. SEC EDGAR", accessed="2026-09-27",
         url="https://www.sec.gov/Archives/edgar/data/217410/000021741025000015/ul-20241231.htm"),
    dict(item="Unilever plc — 2025 Annual Report on Form 20-F (hyperinflation accounting policy note)",
         value="Argentina/Türkiye 2025 IAS29 impact table",
         source="U.S. SEC EDGAR", accessed="2026-09-27",
         url="https://www.sec.gov/Archives/edgar/data/217410/000021741026000007/ul-20251231.htm"),
    dict(item="Unilever plc — Annual Report and Accounts 2025 (Excel workbook)",
         value="Consolidated financial statements", source="Unilever plc investor relations",
         accessed="2026-09-27", url="https://www.unilever.com/investors/annual-report-and-accounts/"),
    dict(item="IAS 29 Financial Reporting in Hyperinflationary Economies — restatement mechanics",
         value="Monetary items not restated; non-monetary restated by price index; net monetary "
               "gain/loss recognized in P&L", source="IFRS Foundation", accessed="2026-09-27", url=""),
    dict(item="IAS 21 The Effects of Changes in Foreign Exchange Rates — §42-43",
         value="Restated hyperinflationary FS translated at the closing rate (not average)",
         source="IFRS Foundation", accessed="2026-09-27", url=""),
]

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
# accounting adjustment"? CONFIRMED by a live Stage 2 research pass (2026-09-27, see
# examples/2026-09-27_142024/report_workdir/price_consensus_research.json for the full
# finding with citations) — no longer a placeholder hypothesis.
# ---------------------------------------------------------------------------

CONSENSUS = dict(
    ticker="ULVR", exchange="LSE",
    note=(
        "CONFIRMED (live research, 2026-09-27): across two 2026 earnings-call "
        "transcripts (Q1 and Q2) and public analyst/aggregator commentary (TipRanks, "
        "MarketScreener, MarketBeat), Argentina and Türkiye come up only as volume/growth "
        "stories plus a generic aggregate 'currency headwind' to reported turnover and "
        "underlying EPS. No sell-side note, analyst question, or press summary found "
        "separates the IAS 29 net monetary gain/(loss) from ordinary FX translation — "
        "Unilever's own USG methodology instead caps hyperinflationary price growth out "
        "of underlying sales growth, and the net monetary line sits in the income "
        "statement without featuring in the call narrative. Limitation: paywalled broker "
        "notes (Deutsche Bank, Barclays, Bernstein) weren't accessible, so this rests on "
        "public transcripts/aggregators only — see the full research file for the caveat."
    ),
)

VALUATION = dict(
    note="This model does not build a full Unilever equity valuation (no DCF/multiples "
         "model — out of scope, see BLUEPRINT.md). Stage 3's mechanical signal is a "
         "materiality flag (net monetary gain/loss as a % of group operating profit, "
         "see bizplan/report/recommendation.py), not a price-vs-fair-value call.",
)

# ---------------------------------------------------------------------------
# Peer comparison: real disclosed IAS 29 impacts from other multinationals, showing the
# Unilever pattern isn't a one-off. Not built into this model's own calculation engine
# (no subsidiary reconstruction for these companies) -- citation-only, for the report's
# context.
# ---------------------------------------------------------------------------

PEER_COMPARISON = dict(
    coca_cola_femsa=dict(
        company="Coca-Cola FEMSA, S.A.B. de C.V.",
        subsidiary="Argentina (hyperinflationary since 1 Jan 2018 per KOF's own restatement)",
        reporting_currency="MXN",
        note=(
            "H1 2025 net monetary position gain of Ps.154m, up from Ps.42m in H1 2024 — "
            "the increase driven mainly by Argentine liabilities benefiting from "
            "inflation: a textbook 'net monetary liability -> gain' case. Contrast with "
            "Unilever's Argentina, which also nets to a net monetary liability position "
            "yet still books a loss overall — see research_output.md's 'A finding worth "
            "flagging' for why the simple heuristic doesn't always survive a full "
            "consolidated restatement."
        ),
        source="Coca-Cola FEMSA Form 20-F FY2025", accessed="2026-09-27",
        url="https://www.sec.gov/Archives/edgar/data/910631/000162828026025313/kof-20251231.htm",
    ),
    bbva=dict(
        company="Banco Bilbao Vizcaya Argentaria, S.A.",
        subsidiary="Türkiye (Garanti BBVA, hyperinflationary since 1 Jan 2022)",
        reporting_currency="EUR",
        figures={
            2023: dict(net_monetary_loss=-2118.0, inflation_linked_bond_gain=1202.0),
            2022: dict(net_monetary_loss=-2323.0, inflation_linked_bond_gain=1490.0),
        },
        note=(
            "BBVA separately discloses an inflation-linked-bond revaluation gain that "
            "partially offsets its Türkiye net monetary loss each year — a real-world "
            "'protective asset' hedge this model's World A/B/C engine doesn't represent "
            "(the illustrative Argentina/Türkiye subsidiaries hold no inflation-linked "
            "instruments) — a real, acknowledged simplification, not fixed here. Real "
            "subsidiary-level reconstruction for BBVA/Garanti stays deferred as "
            "BACKLOG.md Phase 5."
        ),
        source="BBVA Form 20-F FY2023", accessed="2026-09-27",
        url="https://www.sec.gov/Archives/edgar/data/842180/000084218024000007/bbva-20231231.htm",
    ),
)

# ---------------------------------------------------------------------------
# Standard-setting watch: a live 2025 IFRS Interpretations Committee development
# directly relevant to why Türkiye stays classified hyperinflationary despite easing
# headline inflation.
# ---------------------------------------------------------------------------

STANDARD_SETTING_NOTE = dict(
    title="IFRS Interpretations Committee — Assessing Indicators of Hyperinflationary "
          "Economies (July 2025 agenda decision)",
    summary=(
        "The Committee concluded stakeholders should weigh ALL of IAS 29.3's "
        "qualitative indicators (price-indexation prevalence, wage-linking, public "
        "trust in the local currency, interest/inflation-rate relationships) — not "
        "just the >100%/3-year cumulative-inflation rule — when assessing hyperinflation "
        "status. It found little diversity in how stakeholders already apply this and "
        "did not add a standard-setting project. Directly relevant here: Türkiye's "
        "headline annual inflation has eased toward ~31% (2026) — well under the naive "
        ">100%/3yr threshold many assume is the sole test — yet it remains classified "
        "hyperinflationary on the qualitative indicators."
    ),
    source="IFRS Interpretations Committee, July 2025 Agenda Decision", accessed="2026-09-27",
    url="https://www.ifrs.org/projects/completed-projects/2025/assessing-indicators-of-hyperinflationary-economies-IAS-29/",
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
    dict(item="Coca-Cola FEMSA, S.A.B. de C.V. — 2025 Annual Report on Form 20-F",
         value="Argentina net monetary position gain, H1 2025 vs H1 2024",
         source="U.S. SEC EDGAR", accessed="2026-09-27",
         url="https://www.sec.gov/Archives/edgar/data/910631/000162828026025313/kof-20251231.htm"),
    dict(item="BBVA — 2023 Annual Report on Form 20-F",
         value="Türkiye net monetary loss + inflation-linked-bond revaluation gain, FY2023/FY2022",
         source="U.S. SEC EDGAR", accessed="2026-09-27",
         url="https://www.sec.gov/Archives/edgar/data/842180/000084218024000007/bbva-20231231.htm"),
    dict(item="IFRS Interpretations Committee — Assessing Indicators of Hyperinflationary "
              "Economies, July 2025 agenda decision",
         value="Qualitative-indicator weighting; no new standard-setting project",
         source="IFRS Foundation", accessed="2026-09-27",
         url="https://www.ifrs.org/projects/completed-projects/2025/assessing-indicators-of-hyperinflationary-economies-IAS-29/"),
    dict(item="EY — Hyperinflationary economies (updated April 2026)",
         value="Current list: Argentina, Türkiye, Haiti, Iran, Lebanon, Malawi, South Sudan, "
               "Sudan, Venezuela, Zimbabwe", source="EY", accessed="2026-09-27",
         url="https://www.ey.com/en_lt/technical/ifrs-technical-resources/hyperinflationary-economies-updated-april-2026"),
]

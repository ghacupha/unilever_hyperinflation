"""Family Bank Kenya — bank financial model config.

Single source of truth for bank_calculations.py / bank_excel_renderer.py. See
research_output.md for full sourcing detail and BLUEPRINT.md for the schedule design.

Data-provenance tags used in comments throughout this file:
    [DISCLOSED]         — directly from Family Bank's audited financial statements or the
                           MTN Information Memorandum 2026.
    [DISCLOSED-DERIVED]  — computed directly from disclosed figures (e.g. ECL/Gross ratios),
                           not itself a single disclosed line item but not a benchmark guess.
    [MODELED]           — benchmark/analyst-judgment proxy, not directly disclosed.
    [MACRO]             — forward-looking macroeconomic assumption.
    [PLACEHOLDER]       — illustrative only, flagged for replacement with real data
                           (tracked in BACKLOG.md).

ACTUAL_YEARS (2023-2025) render as real hardcoded facts on the Model sheet, immediately
followed by YEARS (2026-2030), the live 5-year formula-driven forecast — matching the FMI
reference's historical-then-projected column pattern. The forecast's opening balance is
FY2025 (the last actual year); the existing `opening_*`/`CAPITAL['opening_tier1']`/etc.
fields used by bank_calculations.py are kept numerically identical to `ACTUALS[2025]`'s
corresponding figures (single source of truth in spirit, even though not mechanically
de-duplicated, to avoid a risky refactor of the calculation engine's read patterns).
See research_output.md's "Update 2026-07-06" entries for full sourcing detail.
"""

BUSINESS_NAME = "Family Bank Limited"
OUTPUT_PREFIX = "Family_Bank_Kenya"
CURRENCY = "KES"
CURRENCY_UNIT = "Millions"
ACTUAL_YEARS = [2023, 2024, 2025]
YEARS = [2026, 2027, 2028, 2029, 2030]
TAX_RATE = 0.30  # [DISCLOSED] Kenya standard corporate tax rate

# ─────────────────────────────────────────────
# ACTUALS — real disclosed figures for 2023-2025, KES millions, all [DISCLOSED] from
# data/family_bank/'s 2023/2024/2025 annual reports (using each later report's comparative
# columns where they give cleaner/restated figures — see research_output.md for exactly
# which page/report each year's numbers came from). **Bank (standalone) column, not
# Consolidated (Group)** — Family Bank's reports present both side-by-side for every
# statement; per the modeling principle that a bank in a group should be modeled on its
# own bank data, every figure below is sourced from the Bank column (research_output.md's
# "Update 2026-07-06 (later)" entry has the full Bank-vs-Consolidated reconciliation).
# Structure mirrors what bank_excel_renderer.py needs to render each schedule's actual
# columns directly: raw balance-sheet/income-statement/cash-flow line items as hardcoded
# facts, one row per real disclosed line (no blended buckets); the renderer computes
# subtotals via same-column formulas, not Python. `total_assets`/`total_liabilities`/
# `total_equity` are kept as verification references (not read by the renderer, which
# builds its own Total Assets/Liabilities/Equity as live SUM formulas over the granular
# rows below) — every year's granular rows sum to these totals exactly.
# ─────────────────────────────────────────────
ACTUALS = {
    2023: dict(
        loan_segments=dict(
            term=dict(gross_s1=61346.247, gross_s2=3467.725, gross_s3=11130.623,
                       ecl_s1=856.406, ecl_s2=337.131, ecl_s3=3807.821),
            mortgage=dict(gross_s1=10183.039, gross_s2=706.859, gross_s3=2156.329,
                          ecl_s1=14.645, ecl_s2=30.865, ecl_s3=119.874),
            od_cc=dict(gross_s1=2053.586, gross_s2=411.914, gross_s3=1122.155,
                       ecl_s1=17.823, ecl_s2=26.920, ecl_s3=445.633),
        ),
        off_balance=dict(gross=3718.240, ecl=11.561),
        # ── Assets (Bank) ──
        cash_cbk=9250.646, due_from_banks=2646.725,
        securities_amortised=24276.235, securities_fvoci=10529.403,
        current_tax_asset=37.361, other_assets_residual=2429.729,
        investment_in_subsidiary=10.000, investment_properties=28.600,
        ppe=2487.309, intangibles=540.864, rou_assets=760.152,
        prepaid_leases=123.280, deferred_tax_asset=2274.049,
        total_assets=142315.712,  # verification reference; ties to the 13 rows above + net loans
        # ── Liabilities (Bank) ──
        deposits_total=103137.731,
        due_to_banks=4384.574, st_cbk_borrowings=3000.000,  # real FY2023-only line, repaid by FY2024
        accruals_provisions=41.702, other_liabilities_residual=3118.856,
        borrowings=11274.119, lease_liabilities=956.570, current_tax_liability=0.0,
        total_liabilities=125913.552,  # verification reference
        # ── Equity (Bank) ──
        share_capital=1287.108, share_premium=5874.662,
        revaluation_surplus=278.424, fair_value_reserve=-1766.320,
        retained_earnings=7410.682, statutory_reserve=2594.636, proposed_dividends=722.968,
        total_equity=16402.160,  # verification reference
        # ── Income Statement / Cash Flow (Bank) ──
        interest_income=16211.094, interest_expense=6599.892,
        non_interest_income=1878.892 + 235.354 + 1031.483 + 360.454,  # fees+invt income+
        # trading+other income (Bank other income excludes Group-only brokerage commission)
        opex=7984.800, provisions=2074.882, pbt=3057.703, tax=647.810, pat=2409.893,
        ocf=-2588.532, icf=-1124.298, fcf=2485.810, cash_end=3175.178,
    ),
    2024: dict(
        loan_segments=dict(
            term=dict(gross_s1=68190.208, gross_s2=3960.795, gross_s3=9335.770,
                       ecl_s1=853.147, ecl_s2=429.870, ecl_s3=4364.636),
            mortgage=dict(gross_s1=11922.527, gross_s2=790.821, gross_s3=1704.570,
                          ecl_s1=29.237, ecl_s2=40.763, ecl_s3=138.613),
            od_cc=dict(gross_s1=2032.539, gross_s2=136.036, gross_s3=1208.130,
                       ecl_s1=15.484, ecl_s2=12.963, ecl_s3=488.118),
        ),
        off_balance=dict(gross=3800.743, ecl=8.163),
        # ── Assets (Bank) — verified independently in the FY2024 report and the FY2025
        # report's comparative; no BS restatement found ──
        cash_cbk=12153.067, due_from_banks=2858.176,
        securities_amortised=22182.261, securities_fvoci=28806.539,
        current_tax_asset=296.669, other_assets_residual=2650.635,
        investment_in_subsidiary=12.347, investment_properties=32.500,
        ppe=2364.951, intangibles=467.911, rou_assets=682.675,
        prepaid_leases=118.643, deferred_tax_asset=2878.804,
        total_assets=168413.743,  # verification reference
        # ── Liabilities (Bank) ──
        deposits_total=127142.024,
        due_to_banks=7125.532, st_cbk_borrowings=0.0,
        accruals_provisions=2101.088, other_liabilities_residual=1981.219,
        borrowings=7491.175, lease_liabilities=850.764, current_tax_liability=0.0,
        total_liabilities=146691.802,  # verification reference
        # ── Equity (Bank) ──
        share_capital=1305.195, share_premium=6118.846,
        revaluation_surplus=278.424, fair_value_reserve=752.161,
        retained_earnings=9066.319, statutory_reserve=3092.496, proposed_dividends=1108.500,
        total_equity=21721.941,  # verification reference
        # ── Income Statement / Cash Flow (Bank) ──
        interest_income=20958.744, interest_expense=9872.405,
        non_interest_income=2119.863 + 375.054 + 610.654 + 365.487,
        opex=9509.072, provisions=1380.308, pbt=3668.017, tax=406.354, pat=3261.663,
        # Cash flow: using the FY2025 report's restated FY2024 comparative Bank figures
        # (most recent — Family Bank broadened its "cash and cash equivalents" definition
        # between report vintages; see research_output.md for the full reconciliation).
        ocf=8344.462, icf=-476.386, fcf=-7495.162, cash_end=7885.711,
    ),
    2025: dict(
        loan_segments=dict(
            term=dict(gross_s1=74732.268, gross_s2=8355.106, gross_s3=12303.290,
                       ecl_s1=805.781, ecl_s2=672.013, ecl_s3=5992.192),
            mortgage=dict(gross_s1=12946.847, gross_s2=1580.111, gross_s3=1395.340,
                          ecl_s1=13.487, ecl_s2=44.337, ecl_s3=202.602),
            od_cc=dict(gross_s1=1506.935, gross_s2=461.631, gross_s3=638.333,
                       ecl_s1=5.971, ecl_s2=27.542, ecl_s3=257.024),
        ),
        off_balance=dict(gross=3094.008, ecl=4.972),
        # ── Assets (Bank) ──
        cash_cbk=9801.482, due_from_banks=7874.262,
        securities_amortised=39683.603, securities_fvoci=34330.870,
        current_tax_asset=0.0, other_assets_residual=3315.691,
        investment_in_subsidiary=53.254, investment_properties=70.600,
        ppe=2400.076, intangibles=761.924, rou_assets=1007.433,
        prepaid_leases=114.006, deferred_tax_asset=3314.679,
        total_assets=208626.792,  # verification reference
        # ── Liabilities (Bank) ──
        deposits_total=152437.336,
        due_to_banks=561.679, st_cbk_borrowings=0.0,
        accruals_provisions=2015.038, other_liabilities_residual=5638.361,
        borrowings=13911.503, lease_liabilities=1182.939, current_tax_liability=772.426,
        # current tax liability is a genuine FY2025-only line (nil in FY2023/FY2024)
        total_liabilities=176519.282,  # verification reference
        # ── Equity (Bank) ──
        share_capital=1662.655, share_premium=10944.549,
        revaluation_surplus=506.423, fair_value_reserve=1305.334,
        retained_earnings=12908.471, statutory_reserve=2551.376, proposed_dividends=2228.702,
        total_equity=32107.510,  # verification reference
        # ── Income Statement / Cash Flow (Bank) ──
        interest_income=25168.006, interest_expense=9114.627,
        non_interest_income=2068.571 + 1061.246 + 330.913 + 412.905,
        opex=10968.862, provisions=2562.847, pbt=6395.305, tax=864.655, pat=5530.650,
        ocf=778.409, icf=-803.257, fcf=9253.202, cash_end=17114.065,
    ),
}

# SECTOR_CONCENTRATION — real disclosed loan book by economic sector, [DISCLOSED]. Family
# Bank changed its sector classification scheme between FY2023 (7 categories) and
# FY2024/FY2025 (10 categories, with FY2024 restated into the new scheme in the FY2025
# report) — shown as two separate tables rather than forcing an apples-to-oranges
# comparison. Figures are advances to customers before impairment, KES millions.
SECTOR_CONCENTRATION_10CAT = {
    # Integrated Report & Financial Statements 2025, p.214 ("4.1.4 Concentration of risk") —
    # FY2024 column is the FY2025 report's own restatement of FY2024 into this scheme.
    2024: dict(
        agriculture=5018.959, building_and_construction=3955.368, energy_and_water=1122.413,
        finance_and_insurance=3292.526, manufacturing=4463.402, personal_household=26080.949,
        real_estate=10858.692, tourism_restaurant_hotels=2422.828, trade=31349.652,
        transport_and_communication=4343.776,
    ),
    2025: dict(
        agriculture=8162.107, building_and_construction=4966.298, energy_and_water=1260.169,
        finance_and_insurance=3371.756, manufacturing=5764.765, personal_household=30446.850,
        real_estate=10577.623, tourism_restaurant_hotels=2683.742, trade=33914.447,
        transport_and_communication=4751.155,
    ),
}
SECTOR_CONCENTRATION_7CAT_2023 = dict(
    # Integrated Report & Financial Statements 2024, p.201 (prior classification scheme,
    # not directly comparable to the 10-category scheme above)
    manufacturing=1164.055, wholesale_and_retail=35411.499, transport_and_communication=4623.765,
    agriculture=5949.684, business_services=3305.282, building_and_construction=3777.774,
    other=32689.300,
)

# Scenario multipliers — Best/Worst are derived from Base via these factors (kept as the
# single source both bank_calculations.py's Python scenarios and the renderer's live
# CHOOSE-switch formulas read from, so the two can never drift). [MODELED].
SCENARIO_MULTIPLIERS = dict(
    best=dict(growth_mult=1.2, loss_rate_mult=0.8, opex_mult=0.9),
    worst=dict(growth_mult=0.7, loss_rate_mult=1.4, opex_mult=1.15),
)

# ─────────────────────────────────────────────
# LOAN BOOK — per product type, matching Family Bank's actual disclosure granularity
# (Term Loans / Mortgage / Overdraft & Credit Cards). Opening balances are FY2025
# [DISCLOSED] (Integrated Report 2025, p.199), KES millions. loss_rate_sN = disclosed
# ECL(stage N) / Gross(stage N) for FY2025 [DISCLOSED-DERIVED]. growth / sicr_rate /
# cure_* / default_rate / writeoff_rate are [MODELED] — Family Bank doesn't disclose a
# stage-transition matrix (no bank does; see BLUEPRINT.md IFRS 9 design section). Growth
# rates are informed by the real FY2024->FY2025 aggregate loan growth of 14.7% (disclosed)
# but moderated slightly per segment as a forward-looking judgment call, not a mechanical
# extrapolation of one year's actual.
# ─────────────────────────────────────────────
LOAN_SEGMENTS = [
    dict(
        name="Term Loans", key="term",
        opening_s1=74732.268, opening_s2=8355.106, opening_s3=12303.290,  # [DISCLOSED]
        loss_rate_s1=0.01078, loss_rate_s2=0.08044, loss_rate_s3=0.48704,  # [DISCLOSED-DERIVED]
        growth=0.12, yield_rate=0.145,                                    # [MODELED]
        sicr_rate=0.05, cure_21=0.10, default_rate=0.15, cure_32=0.05,
        writeoff_rate=0.10, risk_weight=1.00,                             # [MODELED]
    ),
    dict(
        name="Mortgage", key="mortgage",
        opening_s1=12946.847, opening_s2=1580.111, opening_s3=1395.340,   # [DISCLOSED]
        loss_rate_s1=0.001042, loss_rate_s2=0.02806, loss_rate_s3=0.14522,  # [DISCLOSED-DERIVED]
        growth=0.08, yield_rate=0.125,                                    # [MODELED]
        sicr_rate=0.04, cure_21=0.10, default_rate=0.10, cure_32=0.08,
        writeoff_rate=0.05, risk_weight=0.50,                             # [MODELED]
    ),
    dict(
        name="Overdraft & Credit Cards", key="od_cc",
        opening_s1=1506.935, opening_s2=461.631, opening_s3=638.333,      # [DISCLOSED]
        loss_rate_s1=0.003962, loss_rate_s2=0.05966, loss_rate_s3=0.40265,  # [DISCLOSED-DERIVED]
        growth=0.13, yield_rate=0.170,                                    # [MODELED]
        sicr_rate=0.06, cure_21=0.10, default_rate=0.18, cure_32=0.05,
        writeoff_rate=0.15, risk_weight=1.00,                             # [MODELED]
    ),
]

OFF_BALANCE_SHEET = dict(
    opening=3094.008,  # [DISCLOSED] FY2025 off-balance-sheet exposure
    growth=0.10, ccf=0.20, risk_weight=1.00,  # [MODELED] credit conversion factor
)

# Forward-looking macro overlay — probability-weighted scenario multiplier applied to
# every segment's stage loss rates. [MACRO] Base/Upside/Downside informed by Family Bank's
# own FY2025 report (p.188-189): 2026 GDP growth 4.5% (IMF) to 5.3% (Treasury), inflation
# ~4-5%, CBK benchmark ~9%, industry NPL ~16-17%, pre-2027 election uncertainty flagged as
# a risk overlay — not extrapolating FY2025's own trend uncritically (the buy-side
# "revert to a through-the-cycle norm" check from BLUEPRINT.md).
MACRO_SCENARIOS = dict(
    weights=dict(base=0.60, upside=0.20, downside=0.20),
    multipliers=dict(base=1.00, upside=0.85, downside=1.30),
)

# ─────────────────────────────────────────────
# DEPOSITS — Family Bank discloses only the aggregate customer deposit total (FY2025 Bank:
# KES 152,437.336m [DISCLOSED]); the split by type below is [MODELED] (typical Kenyan
# retail-bank funding mix, same proportions as the prior FY2023-based pass), not disclosed
# at this granularity.
# ─────────────────────────────────────────────
DEPOSIT_TYPES = [
    dict(name="Demand / Current", key="demand", opening=45731.20, growth=0.16, cost_rate=0.02),
    dict(name="Savings", key="savings", opening=38109.34, growth=0.15, cost_rate=0.04),
    dict(name="Term / Fixed Deposits", key="term_deposits", opening=53353.07, growth=0.17, cost_rate=0.10),
    dict(name="Wholesale / Interbank", key="wholesale", opening=15243.73, growth=0.13, cost_rate=0.11),
]  # opening figures sum to the disclosed FY2025 Bank total of 152,437.336 [MODELED allocation]

INVESTMENT_SECURITIES = dict(
    opening=74014.473,  # [DISCLOSED] FY2025 Bank government securities (amortised cost
    # 39,683.603 + FVOCI 34,330.870, Integrated Report 2025 p.165, Bank column)
    growth=0.05,       # [MACRO] moderating — sector shifting from securities to private credit
    yield_rate=0.13,   # [MODELED] ~ Kenya 10Y bond yield (12.32%, disclosed-secondary) + T-bill mix
)

OPENING_CASH = 17675.744  # [DISCLOSED] FY2025 cash and balances with CBK (9,801.482) +
# balances due from banking institutions (7,874.262), Integrated Report 2025 p.165 —
# combined into one "cash & equivalents" line as a simplification (avoids adding a
# separate interbank-placements balance-sheet row for a relatively minor distinction)

# ─────────────────────────────────────────────
# OPERATING EXPENSES — pure opex only (excludes loan loss provisions, modeled separately
# via the IFRS 9 schedule). FY2025 disclosed total operating expenses = 11,135.575
# [DISCLOSED] (Integrated Report 2025 p.164); the category split below is [MODELED]
# (same proportions as the prior pass — granular opex-by-category isn't in the extracted
# pages). y1 (2026) = FY2025 category value escalated one year at the rate below.
# ─────────────────────────────────────────────
OPEX_ITEMS = [
    dict(name="Staff Costs", key="staff", y1=6438.2, escalation=0.09),
    dict(name="Premises & Branch Network", key="premises", y1=1639.7, escalation=0.06),
    dict(name="Technology & Digital", key="tech", y1=1392.5, escalation=0.10),
    dict(name="Other Operating Expenses", key="other", y1=2406.9, escalation=0.07),
]

NON_INTEREST_INCOME_RATE = 0.02541  # [DISCLOSED-DERIVED] FY2025 Bank non-interest income
# (net fees & commission 2,068.571 + investment income 1,061.246 + net trading 330.913 +
# other income 412.905 = 3,873.635) / customer deposits (152,437.336) = 2.541%

DIVIDEND_PAYOUT_RATIO = 0.25  # [MODELED] mid-tier-bank assumption; peers range 27%-95% (see below)

# ─────────────────────────────────────────────
# CAPITAL — CBK minimums are [DISCLOSED] (Family Bank's own regulatory capital note,
# unchanged FY2023->FY2025). `opening_tier1`/`opening_tier2` remain total accounting
# equity/a small liability-side proxy — they drive the Balance Sheet's opening retained
# earnings and Other Liabilities plug in bank_calculations.py and must NOT be repointed to
# real regulatory figures (that would corrupt the Balance Sheet Check). The REAL regulatory
# Tier 1/Tier 2/RWA build-up — which does reconcile exactly to the disclosed 16.9%/19.6% —
# now lives in REGULATORY_CAPITAL below (real facts for actual years) plus
# `tier1_pct_of_equity`/`reg_tier2_opening`/`other_rwa_pct_of_gross_loans` (the projected
# -year drivers, calibrated to the FY2025 real anchor). See BLUEPRINT.md for the full
# rationale.
# ─────────────────────────────────────────────
CAPITAL = dict(
    opening_tier1=32107.510,  # [DISCLOSED] FY2025 Bank total shareholders' equity, Integrated
    # Report 2025 p.165 (Bank column) — Balance Sheet accounting-equity anchor only, NOT
    # regulatory Tier 1 (see above)
    opening_tier2=2000.0,     # [MODELED] small proxy (revaluation-eligible + subordinated debt)
    # — Balance Sheet liability-side anchor only, NOT regulatory Tier 2 (see above)
    core_capital_rwa_min=0.105,      # [DISCLOSED]
    core_capital_deposits_min=0.08,  # [DISCLOSED]
    total_capital_rwa_min=0.145,     # [DISCLOSED]
    min_core_capital_absolute=5000.0,  # [DISCLOSED] Shs 5bn threshold by 31 Dec 2026 (rising
    # to Shs 10bn by 2029 per the Business Laws Amendment Act 2024 — see research_output.md)
    other_rwa_pct_of_gross_loans=0.3347,  # [MODELED] projected-year RWA driver, replacing
    # the old flat plug. Calibrated to the real FY2025 disclosed RWA (144,703.676) minus our
    # own modeled Loan Book + Off-Balance-Sheet RWA (106,577.514) = 38,126.162 residual,
    # expressed as a % of FY2025 gross loans (113,919.861) so it scales with the book
    # instead of staying static.
    tier1_pct_of_equity=0.7481,  # [MODELED] projected-year regulatory Tier 1 driver,
    # calibrated to the real FY2025 ratio of regulatory Tier 1 (24,404.354, see
    # REGULATORY_CAPITAL) to total accounting equity (32,622.486) — no forward-looking
    # methodology for this wedge is disclosed anywhere, so held constant.
    reg_tier2_opening=3899.296,  # [DISCLOSED] real FY2025 regulatory Tier 2 (Capital
    # Management note, Integrated Report 2025 p.238); held flat for projected years —
    # same simplification as before, just anchored to the real figure instead of a guess.
)

# REGULATORY_CAPITAL — Family Bank's own disclosed Tier 1/Tier 2/RWA build-up (Capital
# Management note), 2023-2025, all [DISCLOSED]. Reconciles exactly to the disclosed
# 13.47%/18.89% (2023), 13.52%/17.76% (2024, restated), 16.87%/19.56% (2025) Core/Total
# Capital ratios. `retained_earnings` here is the note's own regulatory figure — it
# legitimately differs from ACTUALS[y]['retained_earnings'] (the accounting Balance Sheet
# figure), since the regulatory computation applies its own filters (and, in the case of
# Tier 2, absorbs items like the statutory reserve that sit within accounting equity, not
# liabilities). FY2024 uses the RESTATED figures from the Integrated Report 2025 (p.238),
# not FY2024's own originally-reported Tier1=16,490.360/Total Capital=21,252.462 (a new
# deferred-tax deduction line first appears in the FY2025 report's presentation) — same
# "prefer the more recent restatement" convention used for the Cash Flow Statement.
REGULATORY_CAPITAL = {
    2023: dict(  # Integrated Report & Financial Statements 2023, p.168
        share_capital=1287.108, share_premium=5874.662, retained_earnings=7410.682,
        deferred_tax=0.0,  # deduction line didn't exist in FY2023's presentation
        revaluation_reserve=69.606, subordinated_debt=3200.000, statutory_reserve=2594.636,
        rwa=108176.948,
    ),
    2024: dict(  # RESTATED — Integrated Report & Financial Statements 2025, p.238
        share_capital=1305.195, share_premium=6118.846, retained_earnings=9066.319,
        deferred_tax=-1266.898,
        revaluation_reserve=69.606, subordinated_debt=1600.000, statutory_reserve=3092.496,
        rwa=112558.659,
    ),
    2025: dict(  # Integrated Report & Financial Statements 2025, p.238
        share_capital=1662.655, share_premium=10944.549, retained_earnings=12908.471,
        deferred_tax=-1111.321,
        revaluation_reserve=0.0, subordinated_debt=2090.500, statutory_reserve=1808.796,
        rwa=144703.676,
    ),
}

LIQUIDITY_STATUTORY_MIN = 0.20  # [DISCLOSED]

# PP&E — [DISCLOSED] opening (2,401.037, Integrated Report 2025 p.165); D&A/capex rates
# are [MODELED] (banks are capital-light on PP&E relative to the loan book, kept simple).
PPE = dict(opening=2400.076, da_rate=0.08, capex_rate=0.09)
SHARE_CAPITAL = 12607.204  # [DISCLOSED] Bank share capital (1,662.655) + share premium
# (10,944.549), Integrated Report 2025 p.165 (Bank column), combined into one "contributed
# capital" line for bank_calculations.py's roll-forward mechanic (the renderer shows these
# as 2 separate real disclosed rows on the Model sheet's Balance Sheet — see BLUEPRINT.md).
# opening retained earnings (see bank_calculations.py) = CAPITAL['opening_tier1'] - SHARE_CAPITAL.

SHARES_OUTSTANDING_2025 = 1662.655  # [DISCLOSED] ordinary shares in issue at FY2025
# year-end, millions — Integrated Report 2025 p.265 (share capital note): 1,305.195m
# shares at 1 Jan 2025 + 357.460m new shares issued during the year via a Restricted
# Equity Offer = 1,662.655m at year-end; par value KES 1.00/share (confirmed same page),
# so the share-capital account balance in KES millions *is* the share count in millions.
# Used as the denominator for forward per-share valuation (Valuation sheet) — the
# period-end count, not the weighted-average count used for historical EPS (1,367.259m
# FY2025), since we're valuing the current share base going forward, not restating a past
# year's EPS. For Book Value Per Share on actual years, use that year's own
# ACTUALS[y]['share_capital'] instead (share count changed year to year via the FY2023
# rights issue and FY2025 private placement) — already in config.py, no new field needed.

# Small balance-sheet plugs — [MODELED]. Not individually disclosed; kept as simple
# ratios of a plausible driver rather than free-floating plugs, so the balance-sheet
# check is a real verification of the cash-flow mechanics, not a trivial identity. Used
# only by bank_calculations.py's simplified Python engine (Scenarios sheet's static
# Base/Best/Worst snapshot) — the Model sheet's own live formulas now use the granular
# per-line-item build-up below (`OTHER_BS_ITEMS_GROWTH_RATE`) instead.
OTHER_ASSETS_RATE_OF_NET_LOANS = 0.02
OTHER_LIABILITIES_RATE_OF_DEPOSITS = 0.015

OTHER_BS_ITEMS_GROWTH_RATE = 0.08  # [MODELED] generic growth rate for granular Balance
# Sheet line items with no disclosed forward driver (Investment in Subsidiaries,
# Investment Properties, Intangible Assets, Right-of-Use Assets, Prepaid Operating
# Leases, Current/Deferred Tax Asset & Liability, Balances Due to/from Banking
# Institutions, Accruals & Other Provisions, Other Liabilities, Borrowings, Lease
# Liabilities, Revaluation Surplus, Fair Value Reserve, Statutory Reserve) — applied
# uniformly rather than inventing a distinct rate per line where none is disclosed.

# ─────────────────────────────────────────────
# VALUATION — CAPM cost of equity, DDM/Residual Income terminal growth, and peer
# comparables.
# ─────────────────────────────────────────────
VALUATION = dict(
    risk_free_rate=0.1232,        # [DISCLOSED-secondary] Kenya 10Y bond yield, 2 Jul 2026
    equity_risk_premium=0.1394,   # [DISCLOSED] Damodaran total Kenya equity risk premium
    # (mature-market ERP + country risk premium; Moody's Caa1, CRP 9.71%), Jan 2026 data
    # update — pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ctryprem.html
    beta=0.55,                    # [DISCLOSED-DERIVED] average of measured equity betas for
    # 6 NSE-listed Kenyan peer banks (Absa 0.44, Co-op 0.52, DTB 0.28, Equity Group 0.59,
    # I&M 0.80, KCB 0.66 — live.mystocks.co.ke, 24 Jul 2026); Family Bank itself has no
    # measurable beta yet (listed 23 Jun 2026, insufficient price history). Stanbic,
    # StanChart, and NCBA don't publish a beta on this source so are excluded from the
    # average rather than guessed.
    terminal_growth=0.08,         # [MODELED] proxy for long-run nominal Kenya GDP growth
    blend_weights=dict(ddm=0.5, ri=0.3, pb=0.2),  # [MODELED] blended-valuation weights —
    # DDM primary / Residual Income cross-check / P-B-ROE market-check, matching this
    # model's own existing method hierarchy (see BLUEPRINT.md's "Blended valuation"
    # section for the industry-practice research behind this choice — there's no single
    # universal weighting formula in the literature, so this operationalizes the
    # hierarchy the Output sheet already documented). Configurable per analyst judgment.
)

PEER_BANKS = [
    # name, EPS FY24, EPS FY25, ROAE FY24, ROAE FY25, payout FY25, P/B
    # P/B for all 9 peers is now [DISCLOSED] or [DISCLOSED-DERIVED] — current NSE share
    # price / book value per share, stockanalysis.com/quote/nase/<ticker>/statistics/,
    # 24 Jul 2026 (I&M/NCBA sourced earlier, unchanged; see research_output.md).
    dict(name="Absa", eps_fy24=3.8, eps_fy25=4.2, roae_fy24=0.270, roae_fy25=0.247, payout_fy25=0.486, pb_placeholder=1.69),  # [DISCLOSED-DERIVED] BVPS 19.58 / price 33.00
    dict(name="Co-op Bank", eps_fy24=4.3, eps_fy25=5.0, roae_fy24=0.197, roae_fy25=0.191, payout_fy25=0.496, pb_placeholder=1.18),  # [DISCLOSED-DERIVED] BVPS 29.61 / price 35.00
    dict(name="DTB", eps_fy24=27.3, eps_fy25=33.7, roae_fy24=0.098, roae_fy25=0.103, payout_fy25=0.267, pb_placeholder=0.36),  # [DISCLOSED-DERIVED] BVPS 377.77 / price 150.75 (ticker DTK)
    dict(name="Equity Group", eps_fy24=12.3, eps_fy25=19.1, roae_fy24=0.211, roae_fy25=0.265, payout_fy25=0.302, pb_placeholder=0.96),  # [DISCLOSED-DERIVED] BVPS 86.57 / price 87.00
    dict(name="I&M Group", eps_fy24=8.9, eps_fy25=10.8, roae_fy24=0.162, roae_fy25=0.180, payout_fy25=0.348, pb_placeholder=0.64),  # [DISCLOSED-DERIVED] BVPS 66 / price ~42.50
    dict(name="KCB Group", eps_fy24=18.7, eps_fy25=20.8, roae_fy24=0.246, roae_fy25=0.225, payout_fy25=0.337, pb_placeholder=0.73),  # [DISCLOSED-DERIVED] BVPS 109.61 / price 82.50
    dict(name="NCBA", eps_fy24=13.3, eps_fy25=14.2, roae_fy24=0.212, roae_fy25=0.197, payout_fy25=0.500, pb_placeholder=1.2),  # [DISCLOSED] directly reported
    dict(name="Stanbic Holdings", eps_fy24=34.7, eps_fy25=34.7, roae_fy24=0.193, roae_fy25=0.180, payout_fy25=0.644, pb_placeholder=1.44),  # [DISCLOSED-DERIVED] BVPS 202.74 / price 292.00
    dict(name="StanChart", eps_fy24=52.7, eps_fy25=32.5, roae_fy24=0.301, roae_fy25=0.180, payout_fy25=0.955, pb_placeholder=1.81),  # [DISCLOSED-DERIVED] BVPS 184.79 / price 334.25 (ticker SCBK)
]  # [DISCLOSED] EPS/ROAE/payout from MTN Information Memorandum 2026, p.65

COVER_INFO = dict(**{
    "Projection Period": f"{YEARS[0]} to {YEARS[-1]} ({len(YEARS)} Years)",
    "Prepared By": "Family Bank Limited — Management",
    "Classification": "This document is strictly confidential",
})

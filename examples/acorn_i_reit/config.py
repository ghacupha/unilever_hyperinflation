"""Acorn I-REIT (Acorn Student Accommodation Income Real Estate Investment Trust) —
config.py, the single source of truth for every assumption in the generated model.

Every figure is tagged inline by provenance, same convention as the Family Bank build:
[DISCLOSED] straight from Acorn's own filings, [DISCLOSED-DERIVED] computed from disclosed
figures, [MODELED] analyst-judgment proxy, [MACRO] forward-looking macro assumption,
[PLACEHOLDER] illustrative, flagged for replacement. Full source detail, including the two
known reconciliation gaps in the underlying filings, is in research_output.md.

Currency unit throughout this config is KES millions, converted from the source filings'
KES '000 (divide by 1000).
"""

BUSINESS_NAME = "Acorn Student Accommodation I-REIT"
OUTPUT_PREFIX = "Acorn_I-REIT"
CURRENCY = "KES"
CURRENCY_UNIT_ABBR = "KES Mn"
REGULATOR_NAME = "Capital Markets Authority (CMA)"

COVER_INFO = dict(
    Business_Description=(
        "Real Estate Investment Trust holding 7 purpose-built student accommodation "
        "properties (Qwetu brand) across Nairobi, 3,121 rooms / 4,466 beds, managed by "
        "Acorn Investment Management Limited and held in trust by The Co-operative Bank "
        "of Kenya Limited. Listed on the NSE's Unquoted Securities Platform."
    ),
    Projection_Period="2023-2030 (3 actual years, 5 projected)",
    Prepared_By="Bank Financial Model Generator (bizplan)",
    Classification="Illustrative model built from public disclosures — not investment advice",
)

# Citations for every external (non-filing) figure used in the Output-sheet valuation and
# the CMA regulatory limits baked into REGULATORY above -- Acorn's own filing figures are
# cited in research_output.md and via the Assumptions sheet's data-provenance legend.
SOURCES = [
    dict(item="ASA I-REIT semi-annual report, 6 months to 30 June 2025", value="",
         source="Acorn Investment Management Ltd", accessed="2026-08-09",
         url="https://acornholdingsafrica.com/wp-content/uploads/2025/08/ASA-I-REIT-2025-Semi-Annual-Report.pdf"),
    dict(item="Kenya REITs and REOCs sector equity analysis (Acorn I-REIT FY2025 headline figures)",
         value="", source="Sector equity analysis report, 2026-08-06", accessed="2026-08-09", url=""),
    dict(item="I-REIT borrowing limit (gearing)", value="35% of TAV (40% temporary, unit-holder approved)",
         source="Capital Markets Authority — REITs FAQ", accessed="2026-08-09",
         url="https://cma.or.ke/wp-content/uploads/2023/03/REITS.pdf"),
    dict(item="I-REIT minimum income distribution", value="80% of taxable income",
         source="Capital Markets Authority — REITs FAQ", accessed="2026-08-09",
         url="https://cma.or.ke/wp-content/uploads/2023/03/REITS.pdf"),
    dict(item="Kenya 10-year government bond yield (risk-free rate)", value="11.29% (24 Mar 2026)",
         source="Trading Economics", accessed="2026-08-09",
         url="https://tradingeconomics.com/kenya/government-bond-yield"),
    dict(item="Kenya total equity risk premium", value="13.94% (Jan 2026 update)",
         source="Damodaran country risk premium dataset (reused from this repo's prior "
                "Family Bank calibration)", accessed="2026-07-26", url=""),
    dict(item="Peer REIT NAV discount/premium (Acorn I-REIT, LAPTRUST Imara I-REIT)", value="-4.4% / +14.0%",
         source="Kenya REITs and REOCs sector equity analysis report", accessed="2026-08-09", url=""),
    dict(item="Sector cap-rate cross-check (retail/office term & reversionary yields)",
         value="Retail 13.0%/9.0%, Office & light industrial 12.5%/9.0% (FY2025)",
         source="ILAM Fahari I-REIT FY2025 Annual Report, Note 11 (independent valuer: Tysons Limited)",
         accessed="2026-08-25",
         url="https://ilamfahariireit.com/assets/files/ILAM_Fahari_I-REIT_Annual_Report_FY2025.pdf"),
    dict(item="Sector cap-rate cross-check (Nairobi residential rental yield range)", value="5.4%-7.4%",
         source="Cytonn Nairobi Metropolitan Area Residential Report 2025 / Knight Frank Kenya Market Update H1 2025",
         accessed="2026-08-25", url="https://cytonn.com/topicals/nairobi-metropolitan-area-32"),
]

# 3 actual years immediately followed by 5 projected years, same convention as the
# Family Bank build. Today's date is 2026-08-09, so 2026-2030 is "the next 5 forward".
YEARS = [2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030]
ACTUAL_YEARS = [2023, 2024, 2025]

# REITs registered with the Commissioner of Income Tax are exempt from corporate income
# tax on qualifying property income [DISCLOSED] -- CMA REITs FAQ #14. Kept as an explicit
# field (rather than removed) for config-schema consistency with non-REIT instances.
TAX_RATE = 0.0

# ── Property portfolio ──────────────────────────────────────────────────────────────
# 7 properties, purpose-built student accommodation, fair values as at 30 June 2025
# [DISCLOSED] -- sum to 10,727.0 exactly, matching the disclosed Investment Property
# total at that date (a good internal-consistency check). operations_start [DISCLOSED] --
# interim report p.11 "Portfolio Update". tier [DISCLOSED] -- Acorn's own named grouping
# from the interim report's "Portfolio Occupancy Trend" section (p.12): "seed assets" are
# the 3 properties it explicitly names as underperforming (Jogoo Road -- absence of an
# anchor institution + an incomplete access road; Ruaraka and Parklands -- undisclosed
# dips), "stabilized typical assets" are the other 4, at a disclosed 93% H1-2025
# occupancy. NOTE: this is Acorn's own qualitative operational categorization, NOT a
# property-age/maturity split -- Jogoo Road (operations start Aug-2017, the OLDEST
# property) and Ruaraka (Jan-2018, 2nd oldest) are "seed", while Aberdare Heights II
# (Apr-2022, the NEWEST) is already "stabilized". A regression of occupancy against
# property age would be actively misleading here; see research_output.md.
PROPERTIES = [
    dict(name="Qwetu Jogoo Road", location="Jogoo Lane", rooms=343, beds=502,
         opening_fair_value=817.0, operations_start="Aug-2017", acquisition_date="Feb-2021",
         tier="seed"),
    dict(name="Qwetu Ruaraka", location="Outer Ring Road", rooms=380, beds=543,
         opening_fair_value=834.0, operations_start="Jan-2018", acquisition_date="Feb-2021",
         tier="seed"),
    dict(name="Qwetu Wilsonview", location="Keri Road", rooms=512, beds=728,
         opening_fair_value=2033.0, operations_start="Feb-2020", acquisition_date="Feb-2021",
         tier="stabilized"),
    dict(name="Qwetu Parklands", location="Kipkabus Road", rooms=335, beds=533,
         opening_fair_value=1219.0, operations_start="Mar-2019", acquisition_date="Jun-2022",
         tier="seed"),
    dict(name="Qwetu Aberdare Heights I", location="USIU Road", rooms=518, beds=697,
         opening_fair_value=1944.0, operations_start="Jan-2021", acquisition_date="Oct-2022",
         tier="stabilized"),
    dict(name="Qwetu Hurlingham", location="Argwings Kodhek Road", rooms=583, beds=834,
         opening_fair_value=2391.0, operations_start="Jan-2022", acquisition_date="Sep-2023",
         tier="stabilized"),
    dict(name="Qwetu Aberdare Heights II", location="USIU Road", rooms=450, beds=629,
         opening_fair_value=1489.0, operations_start="Apr-2022", acquisition_date="Jan-2024",
         tier="stabilized"),
]

# ── Rental income ────────────────────────────────────────────────────────────────────
# H1 2025 actuals [DISCLOSED]; escalation is the disclosed 2021-2025 average (6.0, 3.9,
# 4.7, 7.1, 4.0 -> ~5.1% CAGR) [DISCLOSED-DERIVED] -- the most recent single year (Apr-2025
# escalation) came in lower, at 4.0% [DISCLOSED], but the 5-year average is used as the
# steadier through-cycle assumption. Occupancy: portfolio-wide blended 81% in H1 2025 vs
# 93% for the "stabilized typical assets" (both [DISCLOSED]); the model further splits
# occupancy by Acorn's own named "seed" vs "stabilized" property tiers (see PROPERTIES
# above) -- reit_calculations.compute_seed_occupancy_h1_2025() back-solves the seed
# tier's own H1-2025 occupancy [DISCLOSED-DERIVED] from these two disclosed aggregates.
# Base scenario assumes the seed tier recovers toward the stabilized rate over
# occupancy_recovery_years [MODELED]; the stabilized tier is held flat, already at target.
RENTAL_INCOME = dict(
    streams=[
        dict(name="Residential", h1_2025_actual=516.440),
        dict(name="Retail", h1_2025_actual=7.661),
    ],
    escalation=0.051,
    occupancy_portfolio_h1_2025=0.81,
    occupancy_stabilized=0.93,
    # H1-2024 comparatives for the same two disclosed aggregates [DISCLOSED] -- interim
    # report p.12 "Portfolio Occupancy Trend" -- used to also back-solve the seed tier's
    # H1-2024 occupancy (~80.7%) as a second real data point alongside H1-2025's ~59.0%,
    # showing the seed tier actually DECLINED year-on-year (Jogoo Road's anchor-tenant
    # loss + access-road disruption), not a maturity/ramp-up trend. See research_output.md.
    occupancy_portfolio_h1_2024=0.88,
    occupancy_stabilized_h1_2024=0.92,
    occupancy_recovery_years=3,
)

# ── Operating expenses ──────────────────────────────────────────────────────────────
# H1 2025 actuals [DISCLOSED] -- note 5(a) (admin) and note 6 (fund-level, connected-party
# fees). Escalation assumed to track rental escalation for admin items and NAV/TAV growth
# for fund-level fees (management/trustee fees are contractually NAV- or TAV-based)
# [MODELED].
OPEX_ITEMS = [
    dict(name="Utilities and maintenance", category="admin", h1_2025_actual=36.052, escalation=0.051),
    dict(name="Staff costs", category="admin", h1_2025_actual=35.335, escalation=0.06),
    dict(name="Property management fees", category="admin", h1_2025_actual=31.694, escalation=0.06),
    dict(name="Sales & marketing", category="admin", h1_2025_actual=12.940, escalation=0.05),
    dict(name="Professional fees", category="admin", h1_2025_actual=13.581, escalation=0.03),
    dict(name="Insurance", category="admin", h1_2025_actual=10.765, escalation=0.05),
    dict(name="Shuttle services", category="admin", h1_2025_actual=7.637, escalation=0.05),
    dict(name="Office & other admin expenses", category="admin", h1_2025_actual=13.976, escalation=0.05),
    dict(name="REIT management fees", category="fund", h1_2025_actual=26.086, escalation=0.06),
    dict(name="Trustee fees", category="fund", h1_2025_actual=25.675, escalation=0.06),
    dict(name="Custodial fees", category="fund", h1_2025_actual=3.668, escalation=0.06),
    dict(name="CMA fees & other fund costs", category="fund", h1_2025_actual=0.814, escalation=0.03),
]

# ── Debt / gearing ───────────────────────────────────────────────────────────────────
# H1 2025 closing balance and weighted-average rate [DISCLOSED]. Base scenario assumes
# the disclosed post-refinancing rate (11.1%) holds roughly flat with a slight further
# easing, consistent with the CBK rate-cut cycle described in Acorn's own report [MACRO].
CAPITAL = dict(
    opening_borrowings=2419.889,     # Jun-2025 actual [DISCLOSED]
    weighted_avg_rate=0.111,          # Jun-2025 actual [DISCLOSED]
    weighted_avg_rate_projected=0.105,  # gradual further easing [MACRO]
)

# ── Units in issue ───────────────────────────────────────────────────────────────────
# Roll-forward per Note 17 / "Outstanding REIT holdings movement" [DISCLOSED]. See
# research_output.md for the ~1-2% gap between this roll-forward and Acorn's own reported
# NAV-per-unit headline figure -- a known, documented reconciliation gap, not an error.
UNITS = dict(
    opening_units=366.522610,       # millions of units, Jun-2025 actual [DISCLOSED]
    issuance_rate=0.025,             # modest ongoing supplemental-offer issuance [MODELED]
)

# ── CMA regulatory limits (I-REIT-specific) ─────────────────────────────────────────
# [DISCLOSED] -- CMA REITs FAQ, cross-checked against Acorn's own reported LTV/asset-mix
# commentary. See research_output.md for citations.
REGULATORY = dict(
    payout_min=0.80,
    ltv_max=0.35,
    ltv_max_temp=0.40,
    income_producing_min=0.75,
    min_initial_assets=300.0,
)

# ── Scenario framework ──────────────────────────────────────────────────────────────
MACRO_SCENARIOS = dict(
    weights=dict(base=0.5, best=0.25, worst=0.25),
    multipliers=dict(base=1.0, best=1.15, worst=0.85),
)

SCENARIO_MULTIPLIERS = dict(
    best=dict(occupancy_mult=1.08, escalation_mult=1.3, cap_rate_delta=-0.005, rate_mult=0.9),
    worst=dict(occupancy_mult=0.90, escalation_mult=0.6, cap_rate_delta=0.010, rate_mult=1.2),
)

# ── Valuation ────────────────────────────────────────────────────────────────────────
# risk_free_rate: Kenya 10-year government bond yield, 11.29% (24 Mar 2026, Trading
# Economics) [DISCLOSED]. equity_risk_premium: Kenya total ERP 13.94% (Damodaran country
# risk premium dataset, Jan 2026 update), reused from this repo's own prior Family Bank
# calibration [DISCLOSED]. beta: no REIT-specific beta observable (thin/restricted-market
# trading) -- 0.65 defensive-moderate proxy [PLACEHOLDER]. cap_rate: implied from H1 2025
# NOI annualized (524.368-178.460-56.243+3.306)*2=586.94 / Jun-2025 investment property
# 10,727.0 = 5.47% [DISCLOSED-DERIVED]. blend_weights: NAV-anchored, since NAV is the most
# reliable value driver for a property-holding entity and the DDM leg rests on the
# weakest-sourced input (beta) -- see research_output.md. cap_rate cross-check (2026-08-25):
# 5.47% sits within the general Nairobi residential rental-yield range (5.4%-7.4%, Cytonn/
# Knight Frank 2025) found once comparative-REIT/sector cap-rate research was done -- no
# segment-identical published benchmark exists for student housing specifically, so the
# [DISCLOSED-DERIVED] Acorn-own-NOI figure remains the model's direct input; this is
# documentation only, value unchanged. See research_output.md's 2026-08-25 section.
VALUATION = dict(
    risk_free_rate=0.1129,
    beta=0.65,
    equity_risk_premium=0.1394,
    cap_rate=0.0547,
    blend_weights=dict(nav=0.40, ddm=0.30, cap_rate=0.30),
)

# ── Peer REITs (NAV discount/premium cross-check) ───────────────────────────────────
# [DISCLOSED] -- sector report Sec. 5.3.
PEER_REITS = [
    dict(name="Acorn I-REIT", nav_per_unit=24.30, price=23.24, discount_pct=-0.044),
    dict(name="LAPTRUST Imara I-REIT", nav_per_unit=17.20, price=20.00, discount_pct=0.140),
]

# ── Actuals, by year ─────────────────────────────────────────────────────────────────
# FY2023: thin -- only balance-sheet snapshot and dividend total disclosed; the rest is
# [MODELED] (interpolated backward from the FY2024 actual). FY2024: fully [DISCLOSED].
# FY2025: full-year headline [DISCLOSED] (sector report); H2 back-solved as FY2025-total
# minus H1-actual [DISCLOSED-DERIVED]; Dec-2025 balance sheet detail [MODELED], anchored
# to the disclosed NAV/unit (24.30), net profit (670.16) and debt (~1,910.0) control
# totals. Full detail and citations in research_output.md.
ACTUALS = {
    2023: dict(
        investment_property=8776.600, total_assets=9050.0,       # [DISCLOSED / MODELED]
        nav=7377.536, nav_per_unit=22.03,                         # [DISCLOSED]
        borrowings=1600.0,                                        # [MODELED]
        units_in_issue=334.890,                                   # [DISCLOSED-DERIVED]
        rental_income=850.0, net_profit=310.0,                    # [MODELED]
        fair_value_gain=180.0,                                    # [MODELED]
        dividend_paid=241.0, distribution_per_unit=0.72,          # [DISCLOSED / DISCLOSED-DERIVED]
        payout_ratio=0.78,                                        # [MODELED]
    ),
    2024: dict(
        investment_property=10575.000, total_assets=11078.156,    # [DISCLOSED]
        nav=8122.089, nav_per_unit=22.91,                          # [DISCLOSED]
        borrowings=2650.766,                                       # [DISCLOSED]
        units_in_issue=349.008896,                                 # [DISCLOSED]
        rental_income=1058.0,                                      # [MODELED] (~2x H1'25 with escalation)
        net_profit=555.611,                                        # [DISCLOSED]
        fair_value_gain=309.960,                                   # [DISCLOSED]
        dividend_paid=225.0, distribution_per_unit=0.68,           # [DISCLOSED / DISCLOSED-DERIVED]
        payout_ratio=0.405,                                        # [DISCLOSED-DERIVED] (225/555.6)
    ),
    2025: dict(
        investment_property=10847.300, total_assets=11345.709,     # [MODELED]
        nav=9125.709, nav_per_unit=24.30,                           # [MODELED anchor / DISCLOSED]
        borrowings=1910.0,                                          # [DISCLOSED]
        units_in_issue=374.522610,                                  # [MODELED]
        rental_income=1075.0,                                       # [MODELED] (H1 524.101 + modeled H2)
        net_profit=670.160,                                         # [DISCLOSED]
        fair_value_gain=270.0,                                      # [DISCLOSED-DERIVED] (H1 151.701 + modeled H2)
        dividend_paid=208.5, distribution_per_unit=0.57,            # [DISCLOSED]
        payout_ratio=0.341,                                         # [DISCLOSED]
    ),
}

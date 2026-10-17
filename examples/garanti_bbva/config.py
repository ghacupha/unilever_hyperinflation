# Copyright (c) 2026 Edwin Njeru. Licensed under the MIT License (see LICENSE).

"""Garanti BBVA (Türkiye Garanti Bankası AŞ) — real, as-disclosed IFRS-basis, IAS 29-
restated consolidated financial statements for FY2024 and FY2025, in TL thousands.

Unlike `examples/unilever/config.py` (a calibrated *fictional* subsidiary built to
reproduce Unilever's real disclosed aggregate impact), every figure in BALANCE_SHEET and
INCOME_STATEMENT below is Garanti BBVA's own real reported number, copied directly from
its published IFRS financial statements — see SOURCES. This is the "actual subsidiary-to-
parent reconstruction" BLUEPRINT.md's "Follow-up work" section flagged as Phase 5's
distinguishing feature versus the Unilever case.

Both years are presented, as published, in thousands of Turkish Lira "in terms of the
purchasing power of the Turkish Lira at 31 December 2025" — i.e. Garanti's own FY2025
report already restates the FY2024 comparative column into FY2025 purchasing-power terms.
See `research_output.md`'s "Why the 2024 column needs un-restating" section before using
BALANCE_SHEET["2024"] as if it were FY2024's own originally-reported (FY2024-purchasing-
power) balance — it is not; `bank_monetary_position.py` divides back out by the CPI ratio
to recover it.
"""

BUSINESS_NAME = "Türkiye Garanti Bankası AŞ (Garanti BBVA)"
OUTPUT_PREFIX = "Garanti_BBVA_Monetary_Position"
CURRENCY = "TRY"
YEARS = [2024, 2025]

# TÜİK consumer price index, 2003=100 base, year-end values. Sourced via aggregated
# secondary reporting (TÜİK's own site wasn't directly fetchable this session) and
# cross-checked against the widely-reported annual CPI inflation rates for Türkiye
# (+44.38% in 2024, +30.89% y/y in December 2025) — both ratios below reproduce those
# rates to within rounding, so they're treated as reliable. See SOURCES.
CPI_INDEX = {
    2023: 713.14,
    2024: 1029.82,
    2025: 1348.17,
}

# Every line item from Garanti BBVA's Consolidated Statement of Financial Position, as
# published (2025 report, both columns in Dec-2025 purchasing power). TL thousands.
BALANCE_SHEET = {
    "assets": {
        "Cash and balances with central banks":            {"2024": 618_489_033,   "2025": 765_126_617,   "monetary": True},
        "Financial assets at fair value through profit or loss": {"2024": 15_874_453, "2025": 15_753_827, "monetary": True},
        "Derivative financial assets":                      {"2024": 13_634_440,   "2025": 20_109_684,    "monetary": True},
        "Loans and advances to banks":                      {"2024": 203_090_376,  "2025": 243_036_837,   "monetary": True},
        "Loans and advances to customers":                  {"2024": 2_265_981_222, "2025": 2_675_521_677, "monetary": True},
        "Investment securities":                            {"2024": 533_699_472,  "2025": 530_309_550,   "monetary": True},
        "Equity investments":                               {"2024": 4_357_035,    "2025": 4_663_541,     "monetary": False},
        "Assets held for sale":                              {"2024": 9_481_025,    "2025": 9_497_188,     "monetary": False},
        "Investment properties":                             {"2024": 734_189,      "2025": 566_000,       "monetary": False},
        "Tangible and intangible assets":                    {"2024": 117_975_278,  "2025": 120_383_316,   "monetary": False},
        "Deferred tax asset":                                {"2024": 17_637_333,   "2025": 2_446_886,     "monetary": False},
        "Other assets":                                      {"2024": 181_921_495,  "2025": 206_150_848,   "monetary": True},
    },
    "liabilities": {
        "Deposits from banks":                                              {"2024": 75_898_495,   "2025": 6_135_017,     "monetary": True},
        "Deposits from customers":                                          {"2024": 2_742_913_106, "2025": 3_142_198_207, "monetary": True},
        "Loans and advances from banks and other institutions":             {"2024": 100_575_797,  "2025": 114_537_654,   "monetary": True},
        "Obligations under repurchase agreements and money market fundings": {"2024": 61_366_029,   "2025": 87_498_193,    "monetary": True},
        "Debt securities issued":                                           {"2024": 36_793_183,   "2025": 173_583_791,   "monetary": True},
        "Financial liabilities at fair value through profit or loss":      {"2024": 74_900_627,   "2025": 69_884_162,    "monetary": True},
        "Derivative financial liabilities":                                 {"2024": 17_942_070,   "2025": 16_169_909,    "monetary": True},
        "Subordinated liabilities":                                         {"2024": 87_790_294,   "2025": 140_819_036,   "monetary": True},
        "Current tax liability":                                            {"2024": 12_137_719,   "2025": 7_167_574,     "monetary": True},
        "Deferred tax liability":                                           {"2024": 4_307_248,    "2025": 3_137_225,     "monetary": False},
        "Provisions":                                                       {"2024": 24_662_611,   "2025": 27_913_460,    "monetary": True},
        "Other liabilities and accrued expenses":                           {"2024": 270_739_230,  "2025": 323_505_844,   "monetary": True},
    },
    "equity": {
        "Share capital":                      {"2024": 134_803_954, "2025": 134_803_954},
        "Share premium":                      {"2024": 268_633,     "2025": 268_633},
        "Other reserves":                     {"2024": 44_067_464,  "2025": 47_708_768},
        "Retained earnings":                  {"2024": 291_460_225, "2025": 295_507_483},
        "Non-controlling interests":          {"2024": 2_248_666,   "2025": 2_727_061},
    },
}

# Garanti BBVA's own disclosed "Gain/(loss) on net monetary position, net" P&L line — the
# real figure this model's derived estimate (bank_monetary_position.py) is checked
# against. Unlike Unilever, Garanti discloses this directly; nothing here is solved as a
# balancing plug.
DISCLOSED_NET_MONETARY_RESULT = {
    "2024": -12_278_662,
    "2025": -5_327_505,
}

OTHER_INCOME_STATEMENT = {
    # A handful of other real P&L lines, kept for context in research_output.md /
    # the Excel sheet — not used by the monetary-position estimate itself.
    "Net interest income after provisions for loans and other credit risks": {"2024": 45_047_231, "2025": 105_119_583},
    "Net fees and commissions income": {"2024": 142_101_206, "2025": 160_173_101},
    "Total operating Income": {"2024": 260_515_030, "2025": 305_561_684},
    "Profit/(loss) before tax": {"2024": 69_438_792, "2025": 86_338_361},
    "Net profit/(loss) for the period": {"2024": 8_766_984, "2025": 31_915_401},
}

SOURCES = [
    "Türkiye Garanti Bankası AŞ and Its Subsidiaries, Consolidated Financial Statements "
    "(IFRS basis) As of and For the Year Ended 31 December 2025 — Consolidated Statement "
    "of Financial Position and Consolidated Statement of Profit or Loss and Other "
    "Comprehensive Income. Garanti BBVA Investor Relations, IFRS Financial Reports "
    "(IFRS-Financials-31122025.pdf).",
    "TÜİK (Turkish Statistical Institute) Consumer Price Index, 2003=100 base, "
    "December 2023/2024/2025 values — sourced via aggregated secondary reporting, "
    "cross-checked against the widely-reported +44.38% (2024) and +30.89% y/y "
    "(December 2025) CPI inflation rates for Türkiye.",
]

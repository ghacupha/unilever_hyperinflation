"""Stage 3 of the equity-report pipeline: mechanical Buy/Hold/Sell pre-decision.

Pure Python arithmetic — no LLM here. Computes price vs. blended intrinsic value,
assigns an "uncertainty tier" from how much the three valuation methods (DDM, Residual
Income, P/B-ROE regression) disagree with each other, and applies Morningstar's own
published margin-of-safety convention (a star-rating band that widens with uncertainty)
to produce a mechanical signal: Buy/Sell "regardless of catalyst" if the mispricing
clears the tier's band, otherwise Hold pending a specific catalyst (left to the
report-writing stage — see .devops/agents/equity-report/section-recommendation.md, not
yet written — to argue for or confirm).

The Morningstar bands themselves are real, published figures (see BLUEPRINT.md's
"2026-07-26 (cont.) — Equity Research Report pipeline" section for citations). The
**mapping from this model's own method-spread to an Uncertainty Rating tier is this
repo's own heuristic, not a literal Morningstar practice** — their real Uncertainty
Rating also weighs balance-sheet leverage, cash-flow predictability, and competitive
position, none of which this generic bank-model pipeline has per-institution judgment
on. Flagged as an open design choice, not a solved one; revisit if it proves too coarse
once tested against more institutions.
"""
import json
import os

# Morningstar's own published margin-of-safety bands: (buy_discount, sell_premium) by
# Uncertainty Rating tier — a 5-star (strong buy) signal at `buy_discount` below fair
# value, a 1-star (strong sell) signal at `sell_premium` above it.
MORNINGSTAR_BANDS = {
    "Low": (0.20, 0.25),
    "Medium": (0.30, 0.35),
    "High": (0.40, 0.55),
    "Very High": (0.50, 0.75),
    "Extreme": (0.75, 3.00),
}

# This repo's own heuristic: coefficient-of-range across the 3 valuation methods
# ((max - min) / median) mapped to a tier — NOT a Morningstar practice, see module
# docstring. Ordered thresholds; first match wins, falls through to "Extreme".
_SPREAD_TIER_CUTOFFS = [
    (0.30, "Low"),
    (0.60, "Medium"),
    (1.00, "High"),
    (1.50, "Very High"),
]


def uncertainty_tier(method_values):
    """`method_values` is a list of per-share values from the different valuation
    methods. Returns (tier_name, spread)."""
    lo, hi = min(method_values), max(method_values)
    median = sorted(method_values)[len(method_values) // 2]
    spread = (hi - lo) / median if median else float("inf")
    for cutoff, tier in _SPREAD_TIER_CUTOFFS:
        if spread < cutoff:
            return tier, spread
    return "Extreme", spread


def mechanical_recommendation(report_json, price):
    """`report_json` is `data.to_report_json()`'s output. `price` is the current
    share price (e.g. from Stage 2's `price_consensus_research.json`). Returns a dict —
    see `write_recommendation` for the JSON shape written to disk."""
    vps = report_json["valuation_per_share"]
    method_values = [vps["ddm"], vps["residual_income"], vps["pb_regression"]]
    blended = vps["blended"]

    tier, spread = uncertainty_tier(method_values)
    buy_discount, sell_premium = MORNINGSTAR_BANDS[tier]

    pct_diff = (price - blended) / blended  # positive = price above fair value (overvalued)

    if pct_diff <= -buy_discount:
        signal = "Buy"
        rationale = (
            f"Price is {abs(pct_diff) * 100:.1f}% below blended fair value, beyond the "
            f"{tier}-uncertainty Buy threshold ({buy_discount * 100:.0f}%) — Morningstar-"
            f"style industry practice calls this Buy regardless of a specific catalyst."
        )
    elif pct_diff >= sell_premium:
        signal = "Sell"
        rationale = (
            f"Price is {pct_diff * 100:.1f}% above blended fair value, beyond the "
            f"{tier}-uncertainty Sell threshold ({sell_premium * 100:.0f}%) — Morningstar-"
            f"style industry practice calls this Sell regardless of a specific catalyst."
        )
    else:
        direction = "overvalued" if pct_diff > 0 else "undervalued"
        override_signal = "Sell" if direction == "overvalued" else "Buy"
        signal = "Hold"
        rationale = (
            f"Price is {pct_diff * 100:+.1f}% vs. blended fair value — within the "
            f"{tier}-uncertainty band (Buy below -{buy_discount * 100:.0f}%, Sell above "
            f"+{sell_premium * 100:.0f}%). Mechanically Hold: the report-writing stage "
            f"must identify a specific, plausible catalyst to argue {override_signal} "
            f"instead; absent one, the recommendation stays Hold."
        )

    return dict(
        price=price,
        blended_fair_value=blended,
        pct_diff=pct_diff,
        method_values=dict(ddm=vps["ddm"], residual_income=vps["residual_income"],
                            pb_regression=vps["pb_regression"]),
        uncertainty_tier=tier,
        method_spread=spread,
        buy_threshold=buy_discount,
        sell_threshold=sell_premium,
        mechanical_signal=signal,
        rationale=rationale,
    )


def write_recommendation(report_json, price, output_dir):
    """Writes `recommendation_decision.json` into `output_dir` (the pipeline's
    report_workdir/)."""
    decision = mechanical_recommendation(report_json, price)
    path = os.path.join(output_dir, "recommendation_decision.json")
    with open(path, "w") as f:
        json.dump(decision, f, indent=2, default=str)
    return path, decision

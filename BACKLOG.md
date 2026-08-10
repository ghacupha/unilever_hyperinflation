# BACKLOG — REIT Valuation Model

Tracks status against `BLUEPRINT.md`. Check items off as they land; append the
corresponding entry to `CHANGELOG.md` when you do. This is the "what's next" doc — read it
first to know what's next.

The prior banking-model backlog (Phases 1-24-ish) is preserved in git history for anyone
tracing why a particular piece of shared infrastructure (`xl_helpers.py`, the
config-loader pattern, the CHOOSE-switch scenario architecture) looks the way it does —
not reproduced here, since none of the bank-specific schedule/valuation work applies to
the REIT domain.

---

## Phase 1 — Pivot repo to generic REIT valuation model, first instance Acorn I-REIT (2026-08-09) — DONE

- [x] Research: CMA I-REIT regulatory limits (gearing 35%/40%, income-producing minimum
      75%, distribution minimum 80%, min initial assets), Acorn I-REIT's own H1 2025
      interim financial statements (full P&L/BS/cash flow/equity roll-forward, 17 notes),
      the sector-wide equity analysis report's FY2025 headline figures, standard REIT
      valuation methodology (NAV/DDM/cap-rate/multiples). See
      `examples/acorn_i_reit/research_output.md`.
- [x] `bizplan/config_loader.py` — REIT `REQUIRED_FIELDS` + `validate_reit_config`,
      replacing the bank schema.
- [x] `examples/acorn_i_reit/config.py` + `research_output.md` — calibrated from real
      disclosures, provenance-tagged, including two documented reconciliation gaps in the
      source filing itself (units-in-issue vs. reported NAV/unit; Note 17's internally
      inconsistent Dec-2024 mini-table vs. the primary Statement of Changes in Equity).
- [x] `bizplan/financial/reit_calculations.py` — Python ground truth for every schedule
      (property portfolio, rental/NOI, opex, debt, income statement, distributable
      income, units, balance sheet, regulatory compliance, ratio disclosures, valuation),
      plus Base/Best/Worst scenarios and one-lever-at-a-time sensitivity. Two real bugs
      caught and fixed during verification: (1) the balance sheet didn't balance for any
      projected year because "other assets" was grown independently of NAV instead of
      being the balancing plug; (2) the DDM was discounting all 8 years including the 3
      *actual* (already-paid) years as if they were future cash flows.
- [x] `bizplan/financial/reit_excel_renderer.py` — full formula-linked workbook (Cover,
      Summary, Assumptions, Scenarios, Model with Master Check, Output, Sources), reusing
      `xl_helpers.py` and the CHOOSE-switch scenario architecture. Verified end-to-end
      with the `formulas` Python package (a real Excel-formula evaluator, not just
      openpyxl string-writing) — every Master Check row reads OK across all 8 years in
      all 3 scenarios except the Payout Check for actual years 2023-2025, which reads
      ERROR by design (Acorn's own disclosed payout ratios, 78%/40.5%/34.1%, are
      genuinely below the CMA's 80% minimum in those years — a real governance fact, not
      a bug). Two more real bugs caught by this verification pass: (1) `_assum_ref` was
      missing the `Assumptions!` cross-sheet qualifier, so every Model/Output-sheet
      formula meant to read an Assumptions-sheet input was silently reading the wrong
      cell on its own sheet instead; (2) the Property Portfolio's "Opening Fair Value"
      row self-referenced its own prior column instead of the prior period's *closing*
      balance, so Investment Property froze flat after the first projected year.
- [x] `scripts/build_reit_model.py` (renamed from `build_bank_model.py`), `--reit` flag
      (was `--bank`), default instance `acorn_i_reit` (was `family_bank_kenya`).
      `scripts/launch.sh`/`launch.bat`/`launch.ps1` updated to match; smoke-tested
      end-to-end via `./scripts/launch.sh acorn_i_reit`.
- [x] Deleted `bizplan/financial/bank_calculations.py`, `bank_excel_renderer.py`,
      `examples/family_bank_kenya/` (recoverable via git history / the separately-pushed
      `model_family_bank` repo state from the prior session — nothing lost).
- [x] `BLUEPRINT.md`, `BACKLOG.md` rewritten for the REIT domain (this file).
      `README.md`, `CLAUDE.md`, `AGENTS.md` reframed from bank to REIT terms.
      `CHANGELOG.md` appended (not rewritten — it's an explicit running log).

## Phase 2 — Not yet done

- [ ] `bizplan/report/*` (the equity-research-report PDF pipeline) still imports the
      retired `bank_calculations`/`bank_excel_renderer` modules directly
      (`bizplan/report/data.py` at module scope; `sourcing.py`/`pipeline.py` inside
      function bodies) and **will not currently run**. Needs: (a) swap the imports for
      `reit_calculations`/`reit_excel_renderer`, (b) rewrite the `.devops/agents/
      equity-report/*.md` SOPs and `drafting.py`'s section prompts from bank language
      (IFRS 9, CAR, NIM) to REIT language (NAV, distributable income, cap rate, LTV), (c)
      re-verify Stage 1's `validation.py` master-check re-implementation matches the new
      Model sheet's actual row/check set.
- [ ] Item-level opex detail for FY2023/FY2024 is currently a proportional allocation
      from the FY2025 base (see `BLUEPRINT.md` "Known simplifications") — would benefit
      from real per-year, per-item figures if Acorn's full FY2023/FY2024 annual reports
      (not just the interim comparatives) are sourced later.
- [ ] Per-property (not just portfolio-aggregate) fair-value roll-forward, if a
      multi-year per-property history is ever sourced (currently only one point-in-time
      snapshot, 30 Jun 2025, is available).
- [ ] A REIT-specific beta (currently a flagged 0.65 placeholder — no reliable
      regression source given Acorn I-REIT's thin/restricted-market trading).
- [ ] Extend to a second REIT instance (the user's stated intent: "use it to value other
      REITs"). Candidates already researched at sector-summary level in
      `data/KENYA REITS AND REOCS EQUITY ANALYSIS REPORT.pdf`: LAPTRUST Imara I-REIT (a
      useful contrasting instance — three consecutive years of *losses* and NAV erosion
      from fair-value markdowns, unlike Acorn's growth profile), ILAM Fahari I-REIT,
      ALP Industrial REIT, TRIFIC Green USD I-REIT (the last two would also exercise
      the config schema's currency-unit field against a USD-denominated REIT — neither
      tested yet). Each needs its own full financial-statement sourcing pass before a
      real `config.py` can be built, same as Acorn I-REIT's Phase 1 above.

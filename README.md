# REIT Valuation Model

A financial model for Real Estate Investment Trusts, first instance **Acorn I-REIT** (a
real NSE-listed student-accommodation REIT in Kenya), that produces an audit-ready, fully
formula-linked Excel workbook — schedules, scenarios, and an equity valuation, not a
one-off spreadsheet — built entirely from its own disclosed filings.

Every calculated cell in the generated workbook is a live Excel formula (`=SUM(...)`,
cross-sheet references, a scenario `CHOOSE()` switch) — nothing is a pasted-in number
except the real disclosed facts themselves.

## Quick start

Prerequisites: Python 3 (any recent 3.x). Nothing else needs to be installed manually.

```bash
# Unix / macOS / Linux
./scripts/launch.sh

# Windows (Command Prompt)
scripts\launch.bat

# Windows (PowerShell)
.\scripts\launch.ps1
```

Any of the three launchers will, in order:
1. Create a `.venv` at the repo root if one doesn't already exist.
2. Install the runtime dependencies (`openpyxl`, `reportlab`, `matplotlib`) into it.
3. Build the model and write it to a timestamped folder under `output/`.

All three also load a repo-root `.env` file automatically, if one exists (copy
`.env.example` to `.env` to set up — see "Equity Research Report" below for what goes in
it). A variable already set in your shell before invoking the launcher wins over `.env`'s
value.

If you already have the venv active, you can run the entry point directly:

```bash
.venv/bin/python scripts/build_reit_model.py
.venv/bin/python scripts/build_reit_model.py --config path/to/config.py
```

## Equity Research Report (optional — `REPORT=1`)

**Not currently functional for the REIT domain** — the pipeline (`bizplan/report/*`)
still imports the retired bank-specific calculation/renderer modules from this repo's
prior life as a banking model. See `BACKLOG.md` Phase 2 for the REIT-adaptation follow-up
this needs before `REPORT=1` will work again. The default (Excel-only) path above is
unaffected.

## Expected output

Each run creates `output/<YYYY-MM-DD_HHMMSS>/` containing:
- `<Prefix>_Financial_Model.xlsx` — the generated workbook.
- `config.py` — an exact copy of the config that produced it.

Every run is a reproducible snapshot this way. **Never hand-edit files inside `output/`**
— they're regenerated on every run; make changes in the relevant `examples/<reit>/config.py`
instead. Running `build_reit_model.py` directly without a launcher (no `OUTPUT_DIR` set)
falls back to writing straight into `examples/<reit>/`.

## What's in the workbook

Seven sheets, in tab order:

| Sheet | Contents |
|---|---|
| **Cover** | Title, scope, business description |
| **Summary** | 3-scenario (Base/Best/Worst) KPI snapshot, plus a net-profit sensitivity table |
| **Assumptions** | Every input the model uses, color-coded by data provenance (disclosed / modeled / macro / placeholder), including the Base/Best/Worst scenario driver cells and a property-portfolio reference table |
| **Scenarios** | The single scenario switch cell (drives the entire live Model sheet via `CHOOSE()`) plus a projected-year KPI comparison |
| **Model** | The core: 3 actual years immediately followed by 5 projected years, across every schedule — Property Portfolio, Rental Income & NOI, Operating Expenses, Debt/Gearing, Income Statement, Distributable Income & Distributions, Balance Sheet, Regulatory Compliance (CMA I-REIT limits) — plus a top-of-sheet Master Check (Balance Sheet / LTV / Income-Producing-% / Payout, "OK"/"ERROR") |
| **Output** | Cost of equity (CAPM), a blended valuation combining NAV, a Dividend Discount Model, direct capitalization (cap rate), and a peer NAV discount/premium cross-check |
| **Sources** | External market-data and CMA regulatory citations, hyperlinked where available |

Actual-year columns are hardcoded real disclosed facts (blue); projected-year columns are
fully live formulas driven by the Assumptions sheet and the active scenario.

## Project structure

```
financial_model_template/
├── BLUEPRINT.md, BACKLOG.md, CHANGELOG.md, CLAUDE.md, AGENTS.md  ← tracking docs (repo root)
├── data/                                                ← source PDFs (gitignored)
├── .venv/                                               ← shared virtual environment
├── .devops/agents/
│   └── equity-report/              ← SOPs for each equity-report pipeline stage (bank-language, needs REIT adaptation)
├── bizplan/
│   ├── config_loader.py            ← load_and_validate() / validate_reit_config()
│   ├── financial/
│   │   ├── xl_helpers.py           ← formula-capable openpyxl primitives
│   │   ├── reit_calculations.py    ← all schedules, Python ground truth + scenarios
│   │   └── reit_excel_renderer.py  ← builds the live-formula workbook
│   └── report/                     ← the equity-research-report engine (not currently REIT-compatible, see BACKLOG.md)
│       ├── data.py, validation.py, recommendation.py, pdf.py   ← pure Python, no LLM
│       ├── claude_cli.py           ← shared `claude -p` invocation helper
│       └── sourcing.py, price_research.py, drafting.py, review.py, pipeline.py
├── examples/
│   └── acorn_i_reit/
│       ├── config.py               ← single source of truth for assumptions
│       └── research_output.md      ← calibration research, sourced and dated
├── output/                                              ← gitignored; timestamped run folders
│   └── 2026-08-09_214254/
│       ├── Acorn_I-REIT_Financial_Model.xlsx            ← that run's generated workbook
│       └── config.py                                    ← exact copy of the config that produced it
└── scripts/                         ← thin CLI wrappers only — logic lives in bizplan/
    ├── build_reit_model.py         ← entry point: --reit/--config → calc → render → save
    ├── source_model.py, research_price_consensus.py, draft_report_sections.py,
    │   review_report.py, build_report_pdf.py, generate_equity_report.py
    ├── launch.sh                   ← Unix/macOS/Linux launcher
    ├── launch.bat                  ← Windows launcher
    └── requirements.txt            ← runtime deps (openpyxl, reportlab, matplotlib)
```

## Data sourcing

`data/` holds the source filings (currently a Kenya REITs/REOCs sector equity analysis
report, plus Acorn I-REIT's own H1 2025 semi-annual report fetched directly from its
investor-relations site) — the calibration source for every real figure in
`examples/acorn_i_reit/config.py`. Every assumption in the config is tagged inline by
provenance: `[DISCLOSED]` (straight from the filings), `[DISCLOSED-DERIVED]` (computed
from disclosed figures), `[MODELED]` (analyst-judgment proxy), `[MACRO]` (forward-looking
macroeconomic assumption), or `[PLACEHOLDER]` (illustrative, flagged for replacement —
tracked in `BACKLOG.md`).

## Where to go next

- **`BLUEPRINT.md`** — the design source of truth: schedule design, CMA regulatory
  framework, valuation approach, and known simplifications.
- **`BACKLOG.md`** — phase-by-phase status and what's next.
- **`CHANGELOG.md`** — what has actually landed, in order.

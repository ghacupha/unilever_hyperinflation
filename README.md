# Family Bank Kenya Financial Model

A financial model for **Family Bank Kenya** (a real NSE-listed bank) that produces an
audit-ready, fully formula-linked Excel workbook — schedules, scenarios, and an equity
valuation, not a one-off spreadsheet — built entirely from its own disclosed annual
reports.

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
.venv/bin/python scripts/build_bank_model.py
.venv/bin/python scripts/build_bank_model.py --config path/to/config.py
```

## Equity Research Report (optional — `REPORT=1`)

**By default, the launchers only build the Excel model.** To also generate a
Morningstar-style equity research PDF (valuation methodology, sensitivity analysis,
Bulls/Bears, a mechanical Buy/Hold/Sell call, market-consensus comparison, risks —
see `BLUEPRINT.md`'s "Equity Research Report pipeline" section for the full design), set
`REPORT=1`, either inline:

```bash
# Unix / macOS / Linux
REPORT=1 ./scripts/launch.sh family_bank_kenya

# Windows (Command Prompt)
set REPORT=1 & scripts\launch.bat family_bank_kenya

# Windows (PowerShell)
$env:REPORT = "1"; .\scripts\launch.ps1 family_bank_kenya
```

or once, persistently, via a repo-root `.env` file (copy `.env.example` to `.env` and set
`REPORT=1` there — all three launchers pick it up automatically on every run, so you don't
need to remember the flag each time):

```bash
cp .env.example .env
# then edit .env: uncomment/set REPORT=1, and TICKER/EXCHANGE if needed
```

This is **opt-in, not the default**, because it makes several `claude -p` calls (research,
drafting, review — all billed through your existing Claude Code subscription, not a
separate metered API) and takes noticeably longer than the Excel-only path — expect
several minutes, not seconds. It reads `TICKER`/`EXCHANGE` from that institution's
`config.py` automatically; override with `TICKER=... EXCHANGE=...` (inline or in `.env`)
if needed. Output lands in the same timestamped `output/<run>/` folder as the Excel model:
`<Prefix>_Equity_Research_Report.pdf` alongside `<Prefix>_Financial_Model.xlsx`.

## Expected output

Each run creates `output/<YYYY-MM-DD_HHMMSS>/` containing:
- `<Prefix>_Financial_Model.xlsx` — the generated workbook.
- `config.py` — an exact copy of the config that produced it.

Every run is a reproducible snapshot this way. **Never hand-edit files inside `output/`**
— they're regenerated on every run; make changes in the relevant `examples/<bank>/config.py`
instead. Running `build_bank_model.py` directly without a launcher (no `OUTPUT_DIR` set)
falls back to writing straight into `examples/<bank>/`.

## What's in the workbook

Six sheets, in tab order:

| Sheet | Contents |
|---|---|
| **Cover** | Title, scope, business description |
| **Summary** | 3-scenario (Base/Best/Worst) KPI snapshot, plus live ratio disclosures spanning all actual + projected years |
| **Assumptions** | Every input the model uses, color-coded by data provenance (disclosed / modeled / macro / placeholder), including the Base/Best/Worst scenario driver cells |
| **Scenarios** | The single scenario switch cell (drives the entire live Model sheet via `CHOOSE()`) plus a static Best/Worst comparison snapshot |
| **Model** | The core: 3 actual years immediately followed by 5 projected years, across every schedule — Loan Book & IFRS 9 provisioning, Securities/Deposits/Net Interest Income, Income Statement, Cash Flow, Balance Sheet (full line-item detail), Capital Adequacy & Liquidity, Sector Concentration — plus a top-of-sheet Master Check (Balance Sheet / Capital Adequacy / Liquidity, "OK"/"ERROR") |
| **Output** | Cost of equity (CAPM), Dividend Discount Model, Residual Income cross-check, P/B-ROE regression, a blended valuation, per-share implied values, and a Financial Statement Quality Analysis (Beneish M-Score proxy, accruals ratio, Texas Ratio) scoped to the actual years |

Actual-year columns are hardcoded real disclosed facts (blue); projected-year columns are
fully live formulas driven by the Assumptions sheet and the active scenario.

## Project structure

```
financial_model_template/
├── BLUEPRINT.md, BACKLOG.md, CHANGELOG.md, CLAUDE.md, AGENTS.md  ← tracking docs (repo root)
├── data/                                                ← source PDFs (Family Bank Kenya)
├── .venv/                                               ← shared virtual environment
├── .devops/agents/
│   └── equity-report/              ← SOPs for each equity-report pipeline stage
├── bizplan/
│   ├── config_loader.py            ← load_and_validate() / validate_bank_config()
│   ├── financial/
│   │   ├── xl_helpers.py           ← formula-capable openpyxl primitives
│   │   ├── bank_calculations.py    ← all schedules, Python ground truth + scenarios
│   │   └── bank_excel_renderer.py  ← builds the live-formula workbook
│   └── report/                     ← the equity-research-report engine
│       ├── data.py, validation.py, recommendation.py, pdf.py   ← pure Python, no LLM
│       ├── claude_cli.py           ← shared `claude -p` invocation helper
│       └── sourcing.py, price_research.py, drafting.py, review.py, pipeline.py
├── examples/
│   └── family_bank_kenya/
│       ├── config.py               ← single source of truth for assumptions
│       └── research_output.md      ← calibration research, sourced and dated
├── output/                                              ← gitignored; timestamped run folders
│   └── 2026-07-06_151703/
│       ├── Family_Bank_Kenya_Financial_Model.xlsx      ← that run's generated workbook
│       ├── Family_Bank_Kenya_Equity_Research_Report.pdf ← that run's report (REPORT=1 only)
│       └── config.py                                    ← exact copy of the config that produced it
└── scripts/                         ← thin CLI wrappers only — logic lives in bizplan/
    ├── build_bank_model.py         ← entry point: --bank/--config → calc → render → save
    ├── source_model.py, research_price_consensus.py, draft_report_sections.py,
    │   review_report.py, build_report_pdf.py, generate_equity_report.py
    ├── launch.sh                   ← Unix/macOS/Linux launcher
    ├── launch.bat                  ← Windows launcher
    └── requirements.txt            ← runtime deps (openpyxl, reportlab, matplotlib)
```

## Data sourcing

`data/` holds Family Bank Kenya's own published Integrated Reports & Financial Statements
(FY2023-FY2025) and an NSE listing Information Memorandum — the calibration source for
every real figure in `examples/family_bank_kenya/config.py`. Every assumption in the
config is tagged inline by provenance: `[DISCLOSED]` (straight from the filings),
`[DISCLOSED-DERIVED]` (computed from disclosed figures), `[MODELED]` (analyst-judgment
proxy), `[MACRO]` (forward-looking macroeconomic assumption), or `[PLACEHOLDER]`
(illustrative, flagged for replacement — tracked in `BACKLOG.md`).

## Where to go next

- **`BLUEPRINT.md`** — the design source of truth: schedule design, IFRS 9 provisioning
  methodology, valuation approach, and the full analytical framework.
- **`BACKLOG.md`** — phase-by-phase status and what's next.
- **`CHANGELOG.md`** — what has actually landed, in order.

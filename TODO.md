# TODO

A live scratch-list of next steps — different purpose from `BACKLOG.md` (which is a
dated, append-only phase log of what's already landed). This file only holds work **not
yet done**: remove an item as soon as it's finished, don't leave a checked-off trail here.
Also the home for any `TODO` left inline in the code itself (searchable via
`grep -rn "TODO" bizplan/ scripts/ examples/`) — if you add one in code, mirror it here.

## Model completeness

- [ ] **VaR risk analysis for the government securities/investment book.** Nothing
      market-risk-related exists yet — `INVESTMENT_SECURITIES` (`config.py`) only models
      a growth rate + yield, no price/duration sensitivity. Needs a VaR schedule (likely
      parametric, given no return time-series is in `data/`) on the securities portfolio.
- [ ] **Additional investment asset types.** Currently only Government Securities
      (amortised cost + FVOCI split) are modeled — no corporate bonds, equities, or other
      investment classes. Family Bank's own Balance Sheet may not disclose much more, but
      worth checking the FY2025 report again before assuming there's nothing to add.
- [ ] **Proper IFRS 16 modeling for Right-of-Use assets.** Currently ROU Assets is a
      single Balance Sheet line (`bank_excel_renderer.py`'s
      `_build_cash_flow_balance_sheet_section`, in the "Other Assets & Other Liabilities
      — Detail" block) that just grows at the generic `OTHER_BS_ITEMS_GROWTH_RATE` — no
      depreciation of the ROU asset or interest expense on the lease liability actually
      flows through to the P&L (real disclosed figures exist: e.g. FY2025 amortisation of
      ROU assets 429,751 KES'000, lease interest expense 157,226 — both currently
      invisible in the model). Needs its own roll-forward tying the ROU asset, the Lease
      Liability (currently also just a generic-growth line), and 2 new P&L lines
      together.
- [ ] **Dedicated Interest Income and Interest Expense schedules.** Right now these live
      folded inside `_build_funding_section`'s combined "SECURITIES, DEPOSITS & NET
      INTEREST INCOME" section rather than as their own schedules — worth pulling out
      and expanding (e.g. per-product loan interest income breakdown, not just one
      "Loan Interest Income" line off the aggregate gross loan book).
- [ ] **More P&L reporting lines.** `_build_income_statement_section` currently shows one
      blended "Non-Interest Income" line even though the real disclosure breaks it into
      4 components (fees & commissions, investment income, net trading income, other
      income — all 4 are already separately in `config.py`'s `ACTUALS[y]
      ['non_interest_income']` sum, just not surfaced as separate rows). Also missing:
      IFRS 16 lease interest/depreciation (see above), and worth checking Family Bank's
      own P&L for any other lines we're still collapsing.
- [ ] **Audit the Cash Flow Statement's reporting lines.** It currently shows only 3
      rows — Operating / Investing / Financing Cash Flow, each a single aggregate
      formula — not the full indirect-method build-up (PAT, +D&A, +provisions, ± working
      capital deltas by category) a real bank's CF statement discloses line by line.
      Check Family Bank's own CF statement structure and decide whether to expose the
      components we already compute internally (see `ocf_proj`'s formula construction in
      `_build_cash_flow_balance_sheet_section`) as their own visible rows.

## Workbook mechanics / formatting

- [ ] **Automate print settings in code** (page setup, print area, orientation, fit-to-
      page, repeated header rows) instead of leaving them to be set manually in Excel
      after each generation. openpyxl supports this via `ws.page_setup` / `ws.print_area`
      / `ws.print_title_rows` — currently unused anywhere in `bank_excel_renderer.py`.
- [ ] **Rearrange the Assumptions sheet into tables, not cascading lists.** Every
      assumption today is one row in a single value column (`build_assumptions` in
      `bank_excel_renderer.py`, via `_assum_row`) — e.g. the 3 loan segments each repeat
      ~10 parameters as separate stacked rows instead of one segment-by-parameter table.
      Worth a real redesign, not a patch: figure out which assumption groups (loan
      segments, deposit types, opex items) are naturally tabular and rebuild those
      blocks with parameters as columns / instances as rows.

## Data

- [ ] **Real market share price data — Family Bank and peers.** Needed for a true P/B,
      P/E, and regression beta (currently `beta`/peer P/B are `[PLACEHOLDER]` in
      `config.py`, and this is also tracked in `BACKLOG.md`'s "Follow-ups" — check there
      first since some peer figures may already have been found). No price series exists
      in `data/` yet; likely needs an external market-data source (NSE data, or Family
      Bank's own listing prospectus once available) rather than the annual reports.

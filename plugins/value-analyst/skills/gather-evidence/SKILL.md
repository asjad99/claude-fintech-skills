---
name: gather-evidence
description: Collect financial statement data, share counts, prices and corporate actions for a company into its evidence ledger with full provenance (raw payload saved, source tier, period, locator). Use when building or refreshing the data behind a stock analysis, or whenever a financial figure needs to be recorded.
argument-hint: "[ledger KEY] [metrics/periods to fetch]"
---

# Gather evidence

`LEDGER` = `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ledger.py" --root "${user_config.research_dir}"`

Metric names, units and period labels: `${CLAUDE_PLUGIN_ROOT}/references/metrics.md`.
Source tiers and where to look: `${CLAUDE_PLUGIN_ROOT}/references/data-sources.md`.

## Default pull for a full analysis
Five fiscal years (FY-4 … FY) of: revenue, cogs, sga, dna, ebit,
interest_expense, pretax_income, tax_expense, net_income, cfo, capex,
total_assets, current_assets, current_liabilities, total_liabilities,
long_term_debt, total_debt, cash, equity, retained_earnings, receivables,
ppe_net, shares_outstanding, shares_diluted, eps_diluted, dividends_per_share.
Plus: latest quarter for debt, cash and shares; `price` and `market_cap` at
`spot` with `--as-of`; FX facts if reporting and trading currencies differ.

## Procedure for each source document or API response
1. Save the response to a scratch file and store it first:
   `LEDGER raw -s KEY path/to/file.json --source "SEC companyfacts" --url URL`.
   Note the returned R- id.
2. Read numbers out of the saved file, not from memory or a summary.
3. Record each one:
   ```
   LEDGER fact -s KEY --metric revenue --value "391035" --scale 1000000 \
     --unit USD --period FY2024 --period-end 2024-09-28 \
     --source "10-K FY2024" --source-tier primary --raw R-0003 \
     --locator "us-gaap:Revenues, FY, form 10-K" --url URL
   ```
   - Values as printed, as strings; use `--scale` for "in millions".
   - `--period-end` is the fiscal period end, not the filing date.
   - Prices: `--period spot --as-of YYYY-MM-DD --unit per_share --currency-of USD`.
4. When a vendor or MCP tool supplies the same metric, record it too as
   `secondary` with its own raw payload. Two sources are the point; the
   reconcile step compares them.

## Rules
- XBRL often carries several values per tag (restated, different durations).
  Pick the one whose form, fiscal period and duration match; put the
  disambiguation in `--locator`.
- Amended or recast figures: record them as a new fact with `--supersedes` the
  old id and `--reason "recast in 10-K FY2025"`. Never overwrite.
- If a metric genuinely does not exist for the company (no receivables, no
  debt), record a `note` saying so with a source rather than a zero fact,
  unless the statement shows an explicit zero.
- Qualitative evidence (moat, management, risks) goes in `LEDGER note` with
  `--url` or `--refs`; no unsourced claims.
- Finish with `LEDGER list -s KEY --type fact` and report which requested
  metric × period cells are still missing.

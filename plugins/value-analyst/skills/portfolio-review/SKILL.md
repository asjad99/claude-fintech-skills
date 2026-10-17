---
name: portfolio-review
description: Review a portfolio of holdings from a tax-lot CSV against the research ledgers - margin of safety per position, stale prices, unreviewed theses, unrealized gains by lot and holding period, and sell plans with lot selection and wash-sale risk across accounts. Use when asked to review holdings, decide what to trim or sell, or check a portfolio against intrinsic values. Never places trades.
argument-hint: "[path to lots CSV] [optional: KEY:QTY to plan a sale]"
---

# Portfolio review

`PORTFOLIO` = `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/portfolio.py" --root "${user_config.research_dir}"`

CSV format: `${CLAUDE_PLUGIN_ROOT}/references/portfolio-csv.md`. If the user's
file has a different layout (a broker export), convert it to that format in a
new file, keep the original untouched, and show the mapping you used.

```
PORTFOLIO --lots lots.csv --required-pct ${user_config.required_margin_of_safety_pct} \
  --max-price-age-days ${user_config.max_price_age_days}
PORTFOLIO --lots lots.csv --plan-sell US0378331005:25:hifo
```

## What to report
- **Input problems first.** Missing ISINs, duplicate lot ids, bad dates. Don't
  value around them silently.
- **Coverage.** Positions with no research ledger, no margin-of-safety
  computation, or a decision that is UNREVIEWED or rejected.
- **Thesis status.** Positions trading above conservative value or below the
  required MOS; for each, recommend re-underwriting (`/value-analyst:analyze`)
  before any trim — a stale thesis is a data problem first.
- **Prices.** "price unavailable" positions are not valued; say so.
- **Pending vs settled.** Pending lots are shown separately and can't be sold
  without fail risk.
- **Sell plans** are plans: lots chosen, estimated gain by short/long term,
  wash-sale flags. State that the user places any order themselves and should
  confirm tax treatment for their jurisdiction.

Portfolio totals across currencies need FX facts in `${user_config.base_currency}`;
if they're missing, report per-currency subtotals rather than converting with
a remembered rate.

Research and decision support only — not personal financial or tax advice.

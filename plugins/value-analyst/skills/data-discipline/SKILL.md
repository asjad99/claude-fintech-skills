---
name: data-discipline
description: Guardrails for handling any financial figure - stock prices, statement line items, ratios, FX rates, valuations. Use whenever stating, computing or comparing financial numbers, even in a quick answer outside a full analysis, so that no number is invented, lost or trusted unverified.
---

# Financial data discipline

Apply these whenever a reply contains a financial number. Full rationale:
`${CLAUDE_PLUGIN_ROOT}/references/handbook-principles.md`.

## Before stating a number
- **Where is it from?** A filing, a named data tool's output in this session,
  or a page you fetched. If it's from memory, say it is from memory and may be
  out of date, or fetch it. Never present a remembered figure as current.
- **What exactly is it?** Period (FY vs TTM vs quarter), fiscal year end,
  currency, units/scale, GAAP vs adjusted, basic vs diluted, as-of date for
  prices.
- **Is it fresh?** Prices older than ${user_config.max_price_age_days} days are
  "unavailable", not "about".

## When computing
- Use the plugin's scripts (Decimal arithmetic) or Python's `decimal` module,
  never floats, for anything money-like. Pass numbers as strings.
- Don't add or compare amounts in different currencies without an explicit,
  dated, sourced FX rate in the right direction.
- Round only when presenting, and state the rounding.
- Per-share history across a split must be split-adjusted before comparison.
- Show the formula and inputs for any derived figure.

## When sources disagree
Say so, show both, prefer the primary filing, and explain the difference
(scale, period, restatement, definition). Don't silently pick one.

## When something is missing
Write "unavailable" and name what's missing. An estimate is allowed only when
labelled as an assumption with its basis and a range.

## Never
- Fabricate tickers, identifiers, filings, quotes, prices or statistics.
- Place, stage or simulate placing trades on the user's behalf.
- Present output as personal financial advice.

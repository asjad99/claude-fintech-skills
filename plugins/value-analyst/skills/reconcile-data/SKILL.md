---
name: reconcile-data
description: Cross-check a company's recorded financial data across sources and against accounting identities, classify every discrepancy, and resolve breaks with compensating entries. Use after gathering evidence and before any valuation, or when two sources disagree on a number.
argument-hint: "[ledger KEY]"
---

# Reconcile

`LEDGER` = `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ledger.py" --root "${user_config.research_dir}"`
`RECON` = `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/reconcile.py" --root "${user_config.research_dir}"`

1. `RECON sources -s KEY` — compares every metric × period that more than one
   source reported (default tolerance 0.5% or 1 unit).
2. `RECON identities -s KEY --period FYxxxx` for each fiscal year, and
   `RECON identities -s KEY --period spot --shares-period <latest>` for
   market cap vs price × shares.
3. Work every result. Statuses and what to do:

| Status | Meaning | Resolution |
|---|---|---|
| MATCH / WITHIN_TOLERANCE | agrees | none |
| SINGLE_SOURCE | only one source | acceptable for minor metrics; for valuation inputs try to add a second source, else list it under Data quality |
| NO_PRIMARY_SOURCE | only vendor/news data | find the filing; don't value on secondary-only inputs |
| SCALE_MISMATCH | off by 10^3/10^6/10^9 | units error; supersede the wrong fact with the right scale |
| SIGN_MISMATCH | same size, opposite sign | usually capex/outflow conventions; record capex as positive, supersede |
| CURRENCY_MISMATCH | different units | wrong currency recorded or needs FX; fix the fact |
| PERIOD_MISMATCH | different period_end | fiscal-calendar or TTM confusion; correct the period label |
| TIMING_OR_RESTATEMENT | one source is an amendment/recast | the later primary filing wins; supersede and cite it |
| BREAK | genuine disagreement | open the raw payloads of both, find which is right, supersede the wrong one with `--reason "see K-xxxx"`; if you can't decide, exclude the metric and say so |
| IDENTITY_BREAK | statements don't tie | look for a missing component (minority interest, mezzanine equity, a wrongly tagged item) and record it; never force a plug |
| IMPOSSIBLE_VALUE | negative revenue, zero shares, etc. | the fact is wrong; supersede it |

4. Re-run until exit code 0, or until every remaining item is explicitly
   accepted with a `LEDGER note --refs K-xxxx --text "accepted because ..."`.

Never "fix" a break by deleting the inconvenient source or editing the ledger.
The point of keeping both is that a reviewer can see what disagreed and why
you chose one.

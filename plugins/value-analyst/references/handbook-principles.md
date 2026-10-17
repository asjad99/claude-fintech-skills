# Engineering principles behind the analyst

This plugin applies ideas from the **Fintech Engineering Handbook**
(https://handbook.fintechengineer.io), which builds on Voytek Pitula's Fintech
Engineering Handbook (CC BY 4.0). The handbook is about building software that
handles money, not about picking stocks. What transfers to an AI analyst is its
discipline about data: an analyst that invents a number, loses where a number
came from, or trusts one vendor blindly fails in the same ways a broken ledger
does. Everything below is a paraphrase and adaptation, not a quotation.

## The three tenets, restated for research

| Tenet (handbook) | What it means for the analyst | Where it is enforced |
|---|---|---|
| **No invented data** — every balance must be derivable from recorded entries | Every figure in a report traces to a ledger entry: a sourced fact (F), an explicit assumption (A) or a computation (C) that lists its inputs. A missing number is reported as unavailable, never estimated quietly. | `ledger.py`, `valuation.py` (ids only, no typed numbers), `lint_report.py` hook |
| **No lost data** — keep the raw input, log the decision as well as the outcome | Raw filings and API responses are stored by SHA-256 before use. Entries are never edited; corrections supersede. The decision and its rationale are logged, as is the reviewer's verdict. | `ledger.py raw`, `--supersedes`, `guard_ledger.py` hook |
| **No trust** — verify across sources, fail loudly on broken assumptions | Vendor data is cross-checked against filings, statements are checked against their own identities, stale prices are refused, and a verdict needs a second, independent reviewer. | `reconcile.py`, `ledger.py stale`, `thesis-checker` agent |

## Chapter-by-chapter mapping

### Representing Money
- Use decimal arithmetic, never binary floats; send numbers across JSON as
  strings. → `money.py` refuses floats; ledger values are strings.
- An amount always travels with its currency; no adding across currencies;
  conversions use an explicit rate. → `Money`, `FxRate`; valuation refuses mixed
  currencies unless an `fx_<FROM><TO>` fact is passed.
- Currencies come from a controlled list; minor units differ by currency (JPY
  has none, KWD has three). → `CURRENCIES` table.
- Round explicitly, rarely, and at the edges; splitting an amount must account
  for the residual. → full precision stored, `round_display` only for output,
  `allocate` returns the residual.
- FX rates are directional, time-stamped and sourced; reference (mid) rates are
  for valuation, not trading. → fx facts carry source and date; inversion only
  for reference rates.

### Investments and Securities
- Asset classes behave differently; a single "security" abstraction breaks.
  → the analyst refuses Altman's original Z for banks/insurers, and DCF on
  negative FCF is flagged as not meaningful.
- Corporate actions (splits, dividends, spin-offs, mergers) change per-share
  history and cost basis; apply them as explicit events. → `ledger.py ca` and
  `corpactions.py adjust`.
- Tax lots carry acquisition date and basis; positions derive from lots; wash
  sales span every account of the same owner. → `portfolio.py`.
- Use official closing prices for valuation; an incorrect valuation is worse
  than a missing one. → stale price = "price unavailable".

### Investment Operations
- Your internal view is a projection of the authoritative record; when they
  disagree the authority wins until proven otherwise. → SEC filings (primary)
  outrank vendor data (secondary) and news (tertiary).
- Match on stable identifiers (ISIN, CUSIP, FIGI), never on tickers alone, and
  link identifier changes to the event that caused them. → `init` warns without
  one; `ca --action identifier_change`.
- Classify breaks (timing, quantity/value, missing, format) and give each a
  resolution path; fix with compensating entries, never edits. → `reconcile.py`
  statuses; corrections via `--supersedes --reason`.
- Staleness thresholds halt automated actions. → `stale`, `max_price_age_days`.
- Maker-checker for manual adjustments. → `decide` (maker) + `review` by a
  different actor (checker).

### The External World
- Do not trust an API's schema; validate the fields you need and fail loudly.
  → `reconcile.py identities` (A = L + E, impossible values).
- Store every request and response. → `ledger.py raw`.
- Validate critical facts against more than one provider. → `SINGLE_SOURCE`
  status; analysis requires a second source for valuation inputs.
- Treat a notification as a hint, not the truth. → news and press releases are
  tertiary leads; the figure is taken from the filing.

### Auditability
- The audit log is append-only; corrections reference what they correct.
- Tamper evidence through hash chains. → each entry hashes the previous one;
  `verify` detects edits.
- An auditor asks what happened, when, who did it, and under what authority.
  → every entry records `recorded_at`, `actor` and its references.
- A dossier is a pure query over existing records. → `ledger.py dossier`.

### Testing Patterns
- Property tests for money math, invariants checked after every step, golden
  values for gnarly calculations, round-trip tests at the JSON boundary.
  → `tests/test_value_analyst.py`.
- Shadow-test a new model before switching to it. → change a valuation method
  only after running old and new side by side on the same ledger (see the
  `valuation` skill).

## Rules for application code
The engineering skills (`build`, `review`, ...) apply the same tenets to the
apps you build. Their rule list lives in `fintech-rules.md`, the single source
for money, data and audit rules in code.

## Chapters deliberately left out
Payment rails, lending, blockchain and tokenization, KYC/AML, US payments
regulation, security model, incident response and distributed-systems patterns
are about operating money-moving infrastructure. They do not change how a
research analyst should reason, so the plugin does not encode them.

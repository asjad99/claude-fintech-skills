# Fintech rules for application code

The single source for money, data and audit rules in apps built with this
plugin. Paraphrased from the Fintech Engineering Handbook
(handbook.fintechengineer.io, after Voytek Pitula, CC BY 4.0); the analyst side
of the plugin applies the same rules (see `handbook-principles.md`).

## Money
- Use a decimal type for every amount, price, rate and ratio: `decimal` in C#,
  `decimal.Decimal` in Python. Binary floating point is for physics, not money.
- Pair amount and currency in one value type (`Money`). Arithmetic across
  currencies is a compile or runtime error; conversion takes an explicit rate.
- Currencies come from a fixed list (ISO 4217) with their own minor units
  (JPY 0, USD 2, KWD 3).
- Keep full precision through calculations. Round once, at a boundary
  (display, persistence, payment), with the mode written in code
  (half-even for statistics, down when you must not overstate).
- Splitting an amount returns the parts and the residual; parts + residual
  equal the total exactly.
- Across JSON and APIs, money travels as a string ("12.34") or an integer of
  minor units, never as a JSON number.

## FX and prices
- An FX rate has a direction (EUR/USD is not 1 / USD/EUR), a date and a source.
- Prices carry an as-of time and source. Past a staleness limit they are
  "unavailable", and the app says so instead of valuing on old data.

## Securities
- Identify securities by ISIN, CUSIP or FIGI. Tickers are display labels:
  they repeat across exchanges and change over time.
- Splits, spin-offs and other corporate actions restate per-share history;
  apply them as recorded events, never by editing old rows.
- Trade date and settlement date are separate fields.

## External data
- Validate the fields you use at the boundary (types, ranges, impossible
  values) and fail loudly on surprises.
- Store the raw response before transforming it.
- Cross-check important figures against a second source and classify
  differences (scale, sign, period, currency, restatement, genuine break).
- Treat webhooks and news as hints; fetch the authoritative state.

## Writes and audit
- Every write that can be retried takes an idempotency key; consumers
  deduplicate.
- Records of money, positions and decisions are append-only; corrections are
  new records that reference what they correct.
- An audit record answers what, when, who and why; personal data stays out of
  audit tables.

## Time
- Store timestamps in UTC; compare market dates in the exchange's local date.
- Inject the clock so tests control time.

## Tests specific to money
- Property tests: allocation preserves totals; serialisation round-trips
  without loss; valuation falls as the discount rate rises.
- Golden tests: pin reviewed valuation outputs (DCF, EPV, margin of safety)
  to worked examples.
- Check invariants after every step of a multi-step flow, not only at the end.

## Boundary
Apps research, compute and display. They do not place orders, and output that
could read as a recommendation carries "not personal financial advice".

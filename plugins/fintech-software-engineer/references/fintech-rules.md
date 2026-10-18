# Core fintech rules

Rules for any software that handles money, read before touching money,
balances, external financial data or audit records. Domain-specific rules
live in `domains/`. Paraphrased from the Fintech Engineering Handbook
(handbook.fintechengineer.io, after Voytek Pitula, CC BY 4.0).

The three tenets behind every rule:
- **No invented data.** Every number is derivable from recorded inputs.
- **No lost data.** Every event, decision and raw input is kept.
- **No trust.** Verify providers, other services and your own code.

## Money
- Use a decimal or integer-minor-units type for every amount, price, rate
  and ratio. Binary floating point is for physics, not money.
- Pair amount and currency in one value type (`Money`). Arithmetic across
  currencies fails; conversion takes an explicit rate.
- Currencies come from a fixed list (ISO 4217) with their own minor units
  (JPY 0, USD 2, KWD 3). Crypto assets carry their own decimals.
- Keep full precision through calculations. Round once, at a boundary
  (display, persistence, settlement), with the mode written in code.
- Splitting an amount returns the parts and the residual; parts + residual
  equal the total exactly.
- Across JSON and APIs, money travels as a string ("12.34") or an integer of
  minor units, never as a JSON number.
- FX rates have a direction, a date and a source; reference rates value
  things, transactional rates record what actually happened.

## APIs and money-moving operations
- Every mutating endpoint takes an idempotency key scoped to client and
  operation. A retry returns the original result; reuse of a key with
  different parameters is rejected (409).
- Errors carry a type, a code, a retryable flag and a suggested action. A
  success status never carries an error body. Batches report per item.
- Long operations return a trackable resource (202) with a documented state
  machine and terminal states.
- Pagination uses cursors, not offsets.
- Version APIs explicitly; change them additively; announce deprecations.

## Distributed systems and events
- A state change and its notification commit together (outbox, change data
  capture or event sourcing). Delivery is at least once; consumers
  deduplicate on a stable event id.
- Multi-step flows persist each step before starting the next and can resume
  after a crash. External effects can't be rolled back: roll forward with
  retries or compensate.
- Prefer optimistic concurrency; check the invariant at write time.

## External providers and data
- Validate the fields you use at the boundary and fail loudly on surprises.
- Store every request and response (or the raw payload) before acting on it.
- Webhooks are hints: verify the signature over the raw bytes, deduplicate,
  then fetch the authoritative state.
- Every external call has a timeout and a retry policy with backoff.
- Reconcile each provider against your records on a schedule; classify each
  difference (timing, missing, amount, format) and fix with new records.
- Prices, rates and balances from outside have an as-of time; past a
  staleness limit they are "unavailable", never silently reused.

## Audit and corrections
- Records of money, positions and decisions are append-only. Corrections are
  new records that reference what they correct.
- An audit record answers what, when, who and under what authority, with
  before and after state. Personal data stays out of audit tables.

## Time
- Store instants in UTC. Business dates (value date, settlement date, due
  date) are dates in the relevant market's or product's calendar.
- Inject the clock so tests control time.

## Operations
- Every money flow has a kill switch, structured logs with correlation ids,
  and alerts on reconciliation breaks.
- Incident severity counts funds at risk as well as technical impact.
  Resolution ends with a check that no money was duplicated, dropped or
  misattributed.

## Tests that money software needs
- Property tests: totals preserved, conversions and serialisation round-trip,
  invariants hold for any sequence of operations.
- Invariants checked after every step of a multi-step flow, not only at the
  end.
- Idempotency tests: replay each operation and assert nothing changes.
- Crash-and-resume tests: fail between each pair of steps, resume, assert
  correctness.
- Golden tests for calculations people review once and must not drift
  (fees, interest, statements, reports).
- Contract tests against provider APIs; recorded provider responses in CI,
  including failures, duplicates and out-of-order events.

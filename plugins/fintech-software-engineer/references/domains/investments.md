# Investments and trading

For orders, brokerage, portfolios, market data, research and valuation
software. Sources: Fintech Engineering Handbook, *Investments and Securities*
and *Investment Operations*.

## Securities and prices
- Identify securities by ISIN, CUSIP or FIGI. Tickers are display labels:
  they repeat across exchanges and change over time. Link identifier changes
  to the event that caused them.
- Asset classes differ (equities, bonds, funds, ETFs, derivatives); model the
  differences rather than one generic "security".
- Prices carry a type (real-time, official close, NAV, evaluated), an as-of
  time and a source. Official valuations use official prices; a stale price
  is "unavailable", never silently reused.

## Orders and settlement
- Orders accumulate ids from each party (client order id, exchange, execution,
  clearing, settlement); log all of them on every event.
- Each fill is its own event with price, quantity and time; averages are for
  display only.
- Trade date and settlement date are separate. Positions and cash have
  pending and settled views; available-to-trade is derived.
- Model failed settlement explicitly.

## Positions, lots and tax
- Positions derive from tax lots (acquisition date, quantity, cost basis).
  Lot quantities always sum to the settled position.
- Disposal method (FIFO, LIFO, specific identification, average cost) is an
  explicit election per account or trade.
- Wash-sale or bed-and-breakfasting rules are checked across all accounts of
  the same owner, using the rules of the relevant jurisdiction.

## Corporate actions
- Dividends, splits, mergers, spin-offs and rights are processed as events,
  atomically per event, keyed by the provider's action id so they apply
  exactly once.
- Splits restate per-share history and cost basis; fractional shares become
  cash-in-lieu at a recorded price. Ex-date logic uses the market's local
  date.

## Reconciliation
- Reconcile positions, cash and activity with the custodian daily; the
  custodian's record wins until proven otherwise. Classify breaks (timing,
  quantity, missing, value) and fix with compensating entries under
  maker-checker.

## Analytics and valuation
- Every figure in a report or model traces to a sourced input; assumptions
  are labelled with a range. Golden tests pin valuation outputs (DCF, yields,
  returns) to worked examples.
- Decision-support output that could read as a recommendation is labelled
  as not personal financial advice where regulation requires it.

## Invariant tests
- Lots sum to positions after any sequence of trades and corporate actions.
- Applying the same corporate action twice changes nothing.

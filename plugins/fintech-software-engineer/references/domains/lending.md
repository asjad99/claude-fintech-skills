# Lending and credit

For loans, credit lines, buy-now-pay-later, interest, fees and repayments.
Source: Fintech Engineering Handbook, *Lending Systems*.

## Interest
- Accrue daily per loan, whether or not it has been billed. One accrual entry
  per loan per day, idempotent on (loan, date); missed days are detected and
  caught up day by day.
- The day-count convention (Actual/365, Actual/360, 30/360, ...) and the
  rounding rule are stored on each loan for its whole life, not taken from
  global settings at run time.
- Keep high precision through accrual; round when posting or producing a
  statement, and carry the residual forward so errors don't build up.
- Rate changes take effect from a dated record; recompute projections with an
  audit trail.

## Accrual, billing and payments
- Interest is recognised when earned (accrual), separately from when it is
  billed and when cash arrives.
- The payment waterfall (fees, interest, principal, in what order) is
  configured per product, not hard-coded.
- A reversed payment needs a correcting accrual entry that references the
  reversal.

## Balances and schedules
- Track original principal, capitalised interest and current balance as
  separate figures; capitalisation is effectively irreversible.
- Keep a projected schedule and an actual schedule. Whether a prepayment
  shortens the term or lowers the instalment is a loan-level setting.
- Statements are versioned: a correction issues a new version and keeps the
  old one. Generate structured data first, render documents from it.

## On the ledger
- Every lending event posts balanced entries. Charge-offs move balances to
  loss accounts; nothing is deleted.

## Regulation
- Disclosures (rates, total cost, schedules) and collection rules vary by
  jurisdiction. Name the rules that apply in the spec; don't assume one
  country's thresholds.

## Invariant tests
- For any sequence of days, payments and reversals: principal + capitalised
  interest + accrued unpaid interest reconciles to the ledger.
- Running accrual twice for the same day changes nothing.
- Golden tests for schedules and statements under each day-count convention.

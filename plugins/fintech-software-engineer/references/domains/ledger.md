# Ledger and accounting

For accounts, balances, journals and anything that records who owns what.
Source: Fintech Engineering Handbook, *The Ledger* and *Auditability*.

## Model
- Double entry: money only moves between accounts. Every transaction's
  entries net to zero per currency, checked at write time.
- Balances are derived from entries. A stored balance is a cache that can be
  rebuilt and must match the entries.
- Each account has a type and a normal balance side (debit or credit).
- Keep ledger, available and pending balances distinct; available is derived
  (ledger minus holds and pending debits), never stored as truth.
- Record value time, booking time and settlement time as separate fields.
- No entry exists outside a transaction. Use opaque, non-sequential ids.

## Writes
- Enforce at write time: balanced transaction, known accounts, correct
  currency per account, no negative balance on asset accounts unless an
  overdraft product allows it (then model the overdraft as its own account
  with a limit).
- Default to optimistic concurrency; use locks only where contention demands.
- Posting is idempotent on a business key (a payment id, an accrual date).

## Corrections
- Posted entries are immutable. Fix mistakes with a linked reversal and a new
  correct entry, never an edit or delete.
- Don't backdate into a closed accounting period; post the correction in the
  open period with a reference to the original.
- Rounding residuals go to an explicit rounding account, never disappear.

## Structure
- Sub-ledgers (per customer, per product, per entity) reconcile to the
  general ledger; a break raises an alert.
- Multi-currency: one balance per currency per account; FX conversion is a
  transaction through FX accounts with the rate recorded.

## Privacy
- Personal data lives in a separate store referenced by opaque ids, so it
  can be erased without touching the immutable ledger.

## Invariant tests
- For any generated sequence of postings: every transaction nets to zero;
  sum of all balances per currency equals zero (or the opening equity);
  balances recomputed from entries equal stored balances.
- Replaying a posting with the same business key changes nothing.

# Payments and money movement

For cards, bank transfers, wires, instant payments, payouts and anything that
moves money through an outside provider. Sources: Fintech Engineering
Handbook, *Executing Money Flows*, *Payment Rails*, *The External World*,
*API Design*.

## Flow mechanics
- Reserve funds before any external call; settle on success, release on
  failure. Reserve the estimate, settle the actual, release the remainder.
- Check availability as balance minus reservations, in the same consistent
  transaction as the reservation write, so the same funds can't back two
  payments.
- Every reservation ends settled or released; a job finds and resolves stale
  ones.
- Idempotency: an explicit key per client and operation, enforced by an
  atomic barrier. Replay permanent errors as-is; retry temporary ones.
- Persist each step before the next; a driver resumes stalled flows. Roll
  forward with retries or compensate; never assume an external effect can be
  undone.
- Keep routing (which provider) separate from execution. Retry another
  provider only on soft declines, with a new provider idempotency key per
  attempt, at most two or three attempts, each logged.

## Rails (check the specifics for your market)
- **Cards:** authorisation, clearing and settlement are separate. Book the
  cleared amount, not the authorised one; track authorisation expiry. Never
  retry hard declines.
- **Batch bank transfers (e.g. ACH, BECS, Bacs):** not real time; debits can
  be returned days or weeks later, so treat them as provisional; files are
  often rejected whole; watch return rates.
- **Wires:** final and irrevocable; apply the strongest controls before
  sending (approval, sanctions screening, beneficiary checks).
- **Instant payments (e.g. RTP, FedNow, NPP, Faster Payments, SEPA Instant):**
  push-only and irrevocable; finish fraud and compliance checks before
  sending, within the scheme's time limit.
- **Cross-border:** enforce FX quote expiry; screen sanctions at every hop.

## Providers and webhooks
- Verify webhook signatures over raw bytes, deduplicate on event id, expect
  out-of-order delivery, and fetch the authoritative state before acting.
- Store every provider request and response.
- Reconcile daily against provider reports and bank statements, including
  fees (gross to net); classify breaks and fix with new records.

## Disputes
- Capture evidence at transaction time (authentication result, delivery
  proof). Chargebacks and refunds arrive late; post them in the current
  period with a reference to the original.

## Invariant tests
- Any interleaving of concurrent payments never overspends available funds.
- Replaying any request or webhook changes nothing.
- A crash between any two steps, followed by resume, ends in a correct state.

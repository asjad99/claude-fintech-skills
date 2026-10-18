# Compliance, identity and controls

For identity verification, KYC/AML, sanctions and transaction screening,
permissions, approvals, privacy and audit. Sources: Fintech Engineering
Handbook, *Identity and Compliance*, *Controls and Access*, *Auditability*,
*US Payments Regulation*, *Security Model*.

## Identity
- Keep authentication (who is signed in), authorisation (what they may do)
  and identity proofing (is this a verified real person or business) as
  separate concerns and services.
- Map verification level to product eligibility explicitly (tiers or flags).
- Share compliance facts (verified, eligible, risk level), not raw identity
  documents, between services.

## Screening
- Screen customers at onboarding and continuously; screen transactions
  inline before settlement.
- Fail closed: if a screening service or credential check is unavailable,
  block the transaction rather than let it through.
- Log every screening decision with its inputs, result and rule version.

## Controls
- Maker-checker: whoever initiates a consequential action (a payout, a limit
  change, a manual ledger adjustment, a rule change) cannot approve it.
  Enforce it in code by actor id, not by convention.
- Segregation of duties: no single role both configures compliance rules and
  approves the transactions they govern.
- Least privilege and deny by default for users, services, keys and
  workers; routes and tables without an explicit grant are inaccessible.
- Elevated or break-glass access is granted by another person, time-limited,
  logged at grant, use and expiry, and reviewed afterwards.
- Every change to permissions is audit-logged with before and after state.

## Privacy and retention
- Store personal data apart from immutable financial records, linked by
  opaque ids; encrypt it so erasure can mean destroying a key.
- Tag data with classification and residency; keep financial records for the
  required retention period, and personal data no longer than needed.
- Open-banking or data-sharing access checks consent scope, purpose and
  expiry on every request, and stops when consent is revoked.

## Audit
- Audit logs are append-only and tamper-evident (hash chains or external
  anchoring); there is no update or delete path for them.
- Each record answers what, when, who and under what authority.

## Regulation
- Requirements differ by country and licence (for example AML/CTF rules,
  PCI DSS for card data, data-protection law, consumer-credit and securities
  rules). Name the ones that apply in the spec, with an owner; don't encode
  one jurisdiction's thresholds as universal.
- Compliance policies are versioned code with tests, checked in CI.

## Invariant tests
- No code path lets the same actor initiate and approve an action.
- A screening outage blocks, never passes, the transactions it covers.
- Permission changes always produce an audit record.

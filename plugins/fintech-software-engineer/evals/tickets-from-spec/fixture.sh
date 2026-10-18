#!/bin/bash
set -e
mkdir -p docs/specs
cat > docs/specs/payouts.md <<'MD'
# Merchant payouts
Status: approved · Date: 2026-10-01 · Domains: payments, ledger

## Problem
Merchants wait for manual bank transfers to receive their sales balance.

## Stories
- S1 As a merchant, I want my available balance paid to my bank account daily, so that I get my money without asking.
- S2 As finance, I want every payout reconciled with the bank, so that breaks are caught the same day.

## Acceptance criteria
- AC1 (S1) Given an available balance above AUD 10.00 at 17:00 Sydney time, when the payout job runs, then a payout for the full available balance is created and the balance is reserved.
- AC2 (S1) Given a payout job that is run twice for the same business date, when it runs again, then no second payout is created.
- AC3 (S1) Given the bank rejects a payout, when the rejection arrives, then the reservation is released and the merchant sees the payout as failed with the bank's reason.
- AC4 (S1) Given the payouts kill switch is on, when the job runs, then no payouts are created and an alert is raised.
- AC5 (S2) Given the bank's daily settlement file, when reconciliation runs, then every payout is matched or listed as a break with its type.

## Money flows
Merchant available balance -> payout clearing -> merchant bank account. Irreversible once the bank accepts. Idempotency key: merchant id + business date.

## Out of scope
Instant payouts, multi-currency payouts.
MD

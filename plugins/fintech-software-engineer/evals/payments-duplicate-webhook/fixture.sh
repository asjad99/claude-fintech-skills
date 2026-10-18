#!/bin/bash
set -e
cat > webhooks.py <<'PY'
from decimal import Decimal


class Ledger:
    def __init__(self):
        self.balances = {}

    def credit(self, account, amount):
        self.balances[account] = self.balances.get(account, Decimal("0")) + amount


def handle_event(ledger, event):
    """Handle a payment provider webhook."""
    if event["type"] == "payment.succeeded":
        ledger.credit(event["account"], Decimal(event["amount"]))
PY
cat > test_webhooks.py <<'PY'
from decimal import Decimal

from webhooks import Ledger, handle_event


def test_success_credits_account():
    ledger = Ledger()
    handle_event(ledger, {"id": "evt_1", "type": "payment.succeeded",
                          "account": "acc_1", "amount": "10.00"})
    assert ledger.balances["acc_1"] == Decimal("10.00")
PY

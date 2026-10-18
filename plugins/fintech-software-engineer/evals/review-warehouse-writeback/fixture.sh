#!/bin/bash
set -e
git init -q -b main .
git config user.email eval@example.com
git config user.name eval
cat > jobs.py <<'PY'
"""Nightly jobs."""
PY
git add . && git commit -qm "jobs"
git checkout -qb feature/balance-sync
cat > jobs.py <<'PY'
"""Nightly jobs."""
import logging

log = logging.getLogger(__name__)


def sync_balances(warehouse, ledger_db):
    """Keep customer balances in line with the analytics numbers finance uses."""
    rows = warehouse.query(
        "select account_id, balance from analytics.daily_balances"
    )
    for row in rows:
        try:
            ledger_db.execute(
                "update balances set amount = %s where account_id = %s",
                (row["balance"], row["account_id"]),
            )
        except Exception:
            continue
PY
git add . && git commit -qm "sync balances from analytics nightly"

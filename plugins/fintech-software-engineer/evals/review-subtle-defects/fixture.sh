#!/bin/bash
set -e
git init -q -b main .
git config user.email eval@example.com
git config user.name eval
cat > payments.py <<'PY'
import logging
from decimal import Decimal

log = logging.getLogger(__name__)


def charge(client, customer_id: str, amount: Decimal, idempotency_key: str):
    return client.create_charge(
        customer=customer_id,
        amount_cents=int(amount * 100),
        idempotency_key=idempotency_key,
    )
PY
git add . && git commit -qm "charge"
git checkout -qb feature/retry
cat > payments.py <<'PY'
import logging
from decimal import Decimal

log = logging.getLogger(__name__)


def charge(client, customer_id: str, amount: Decimal, order_id: str):
    cents = int(float(amount) * 100)
    for attempt in range(3):
        try:
            return client.create_charge(customer=customer_id, amount_cents=cents)
        except TimeoutError:
            log.warning("charge timed out, retrying (attempt %s)", attempt + 1)
        except Exception as exc:
            log.warning("charge failed: %s", exc)
            return None
    return None
PY
git add . && git commit -qm "retry charges on timeout"

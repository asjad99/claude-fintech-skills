#!/bin/bash
set -e
git init -q -b main .
git config user.email eval@example.com
git config user.name eval
cat > pricing.py <<'PY'
from decimal import Decimal


def market_value(quantity: Decimal, price: Decimal) -> Decimal:
    return quantity * price
PY
git add . && git commit -qm "market value"
git checkout -qb feature/live-price
cat > pricing.py <<'PY'
from decimal import Decimal

import requests


def market_value(quantity: Decimal, price: Decimal) -> Decimal:
    return quantity * price


def live_price(ticker: str) -> float:
    try:
        r = requests.get(f"https://example.com/quote/{ticker}", timeout=5)
        return float(r.json()["price"])
    except Exception:
        return 0.0
PY
git add . && git commit -qm "add live price"

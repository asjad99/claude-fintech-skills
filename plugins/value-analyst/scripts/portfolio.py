#!/usr/bin/env python3
"""Portfolio review against the research ledgers. Read-only: it never trades.

Input is a tax-lot CSV (see references/portfolio-csv.md). Positions are
derived from lots, never typed in, so the lot quantities always sum to the
position. For each position it pulls the latest price fact and the latest
margin-of-safety computation from that security's ledger and reports:

* settled vs pending quantity (pending lots are shown, not valued as owned)
* unrealized gain by lot, holding period (short/long term)
* price staleness (stale price -> "price unavailable", no valuation shown)
* thesis status: margin of safety vs the required threshold
* for --plan-sell: lot selection (FIFO / LIFO / HIFO), estimated realized gain,
  and wash-sale risk across every account of the same owner, IRAs included

Everything here is decision support for a human; it outputs a plan, not orders.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ledger import Ledger, LedgerError, default_root  # noqa: E402
from money import D, Money, MoneyError, check_currency  # noqa: E402

REQUIRED = ["owner", "account", "account_type", "lot_id", "security_key",
            "quantity", "cost_basis", "currency", "acquired", "status"]


def load_lots(path: Path) -> tuple[list[dict], list[str]]:
    lots, problems, seen = [], [], set()
    with open(path, newline="") as fh:
        rdr = csv.DictReader(fh)
        missing = [c for c in REQUIRED if c not in (rdr.fieldnames or [])]
        if missing:
            raise LedgerError(f"CSV missing columns: {missing}")
        for n, row in enumerate(rdr, 2):
            try:
                lot = {k: (row.get(k) or "").strip() for k in rdr.fieldnames}
                if lot["lot_id"] in seen:
                    problems.append(f"row {n}: duplicate lot_id {lot['lot_id']}")
                    continue
                seen.add(lot["lot_id"])
                lot["quantity"] = D(lot["quantity"])
                lot["cost_basis"] = Money(lot["cost_basis"], lot["currency"])
                lot["acquired"] = dt.date.fromisoformat(lot["acquired"])
                if lot["quantity"] <= 0:
                    problems.append(f"row {n}: non-positive quantity")
                    continue
                if lot["status"] not in ("settled", "pending"):
                    problems.append(f"row {n}: status must be settled|pending")
                    continue
                if not lot.get("isin"):
                    problems.append(f"row {n}: no ISIN; matching on tickers is unsafe")
                lots.append(lot)
            except (MoneyError, ValueError) as exc:
                problems.append(f"row {n}: {exc}")
    return lots, problems


def latest(L: Ledger, kind: str, method: str | None = None):
    rows = [e for e in L.current(kind) if method is None or e.get("method") == method]
    return rows[-1] if rows else None


def select_lots(lots, qty: Decimal, method: str, price: Decimal | None):
    key = {"fifo": lambda l: l["acquired"].toordinal(),
           "lifo": lambda l: -l["acquired"].toordinal(),
           "hifo": lambda l: -(l["cost_basis"].amount / l["quantity"])}[method]
    picked, left = [], qty
    for lot in sorted(lots, key=key):
        if left <= 0:
            break
        take = min(left, lot["quantity"])
        basis = lot["cost_basis"].amount * take / lot["quantity"]
        picked.append({"lot_id": lot["lot_id"], "account": lot["account"],
                       "quantity": str(take), "basis": str(basis),
                       "acquired": lot["acquired"].isoformat(),
                       "proceeds_est": str(price * take) if price is not None else None,
                       "gain_est": str(price * take - basis) if price is not None else None})
        left -= take
    return picked, left


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--root", type=Path, default=default_root())
    p.add_argument("--lots", type=Path, required=True)
    p.add_argument("--today")
    p.add_argument("--required-pct", default="30")
    p.add_argument("--max-price-age-days", type=int, default=3)
    p.add_argument("--plan-sell", action="append", default=[],
                   help="SECURITY_KEY:QTY[:fifo|lifo|hifo]; repeatable")
    a = p.parse_args(argv)
    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    required = D(a.required_pct) / 100
    try:
        lots, problems = load_lots(a.lots)
    except LedgerError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    by_sec = defaultdict(list)
    for l in lots:
        by_sec[l["security_key"]].append(l)

    positions, prices = [], {}
    for key, ls in sorted(by_sec.items()):
        ccys = {l["currency"] for l in ls}
        pos = {"security_key": key,
               "settled_qty": str(sum((l["quantity"] for l in ls if l["status"] == "settled"), Decimal(0))),
               "pending_qty": str(sum((l["quantity"] for l in ls if l["status"] == "pending"), Decimal(0))),
               "lots": len(ls), "flags": []}
        if len(ccys) > 1:
            pos["flags"].append(f"lots in several currencies {sorted(ccys)}; not summed")
        L = Ledger(a.root, key)
        if not L.exists():
            pos["flags"].append("no research ledger: position is not under coverage")
            positions.append(pos)
            continue
        price_f = L.best_fact("price", "spot")
        price = None
        if price_f is None:
            pos["flags"].append("price unavailable (no price fact)")
        else:
            age = (today - dt.date.fromisoformat(price_f.get("as_of") or "1900-01-01")).days
            pccy = price_f.get("currency") or price_f["unit"]
            if age > a.max_price_age_days:
                pos["flags"].append(f"price unavailable: {price_f['id']} is {age} days old")
            elif pccy not in ccys or len(ccys) > 1:
                pos["flags"].append(f"price in {pccy}, lots in {sorted(ccys)}; needs FX")
            else:
                price = D(price_f["value"])
                pos["price"] = {"value": str(price), "currency": pccy, "fact": price_f["id"]}
        prices[key] = price
        mos = latest(L, "computation", "margin_of_safety")
        if mos:
            o = mos["outputs"]
            pos["thesis"] = {"computation": mos["id"], "conservative_value": o["conservative_value"],
                             "buy_below": o["buy_below"]}
            if price is not None:
                cv = D(o["conservative_value"])
                m = (1 - price / cv) if cv > 0 else None
                pos["thesis"]["mos_now"] = str(m) if m is not None else None
                if m is None or m < 0:
                    pos["flags"].append("trading above conservative value: re-underwrite or trim")
                elif m < required:
                    pos["flags"].append("margin of safety below required threshold")
        else:
            pos["flags"].append("no margin-of-safety computation on file")
        dec = latest(L, "decision")
        if dec:
            rev = [r for r in L.current("review") if r["decision"] == dec["id"]]
            pos["decision"] = {"id": dec["id"], "verdict": dec["verdict"],
                               "review": rev[-1]["outcome"] if rev else "UNREVIEWED"}
        if price is not None:
            unreal = []
            for l in ls:
                if l["status"] != "settled":
                    continue
                held = (today - l["acquired"]).days
                unreal.append({"lot_id": l["lot_id"], "account": l["account"],
                               "gain": str(price * l["quantity"] - l["cost_basis"].amount),
                               "term": "long" if held > 365 else "short", "days_held": held})
            pos["unrealized_by_lot"] = unreal
        positions.append(pos)

    plans = []
    for spec in a.plan_sell:
        parts = spec.split(":")
        key, qty = parts[0], D(parts[1])
        method = parts[2] if len(parts) > 2 else "fifo"
        if method not in ("fifo", "lifo", "hifo"):
            problems.append(f"unknown lot method {method}")
            continue
        sec_lots = [l for l in by_sec.get(key, []) if l["status"] == "settled"]
        if not sec_lots:
            plans.append({"security_key": key, "error": "no settled lots to sell"})
            continue
        owners = {l["owner"] for l in sec_lots}
        picked, short = select_lots(sec_lots, qty, method, prices.get(key))
        plan = {"security_key": key, "quantity": str(qty), "method": method,
                "lots": picked, "flags": [],
                "note": "plan only; place any order yourself after review"}
        if short > 0:
            plan["flags"].append(f"only {qty - short} settled shares available; "
                                 "pending shares cannot be sold without fail risk")
        isins = {l.get("isin") for l in sec_lots if l.get("isin")}
        if any(D(x["gain_est"]) < 0 for x in picked if x["gain_est"]):
            recent = [l for l in lots if l["owner"] in owners
                      and (l.get("isin") in isins or l["security_key"] == key)
                      and 0 <= (today - l["acquired"]).days <= 30
                      and l["lot_id"] not in {x["lot_id"] for x in picked}]
            if recent:
                plan["flags"].append("WASH SALE RISK: same security bought within 30 "
                                     "days in " + ", ".join(sorted({f"{r['account']} ({r['account_type']})" for r in recent})))
            plan["flags"].append("loss sale: do not repurchase this or a substantially "
                                 "identical security in ANY account of this owner "
                                 "(IRAs included) for 30 days")
        if prices.get(key) is None:
            plan["flags"].append("no fresh price: gains not estimated")
        plans.append(plan)

    print(json.dumps({"as_of": today.isoformat(), "input_problems": problems,
                      "positions": positions, "sell_plans": plans}, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

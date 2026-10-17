#!/usr/bin/env python3
"""Corporate-action adjustment of per-share history.

A 10-year EPS chart that ignores a 4:1 split shows a fake collapse. This
script restates per-share and share-count facts onto today's share basis using
the split / reverse-split / stock-dividend events recorded in the ledger with
`ledger.py ca`. Original facts are untouched; the adjusted series is a C-
computation that cites both the facts and the corporate-action entries.

Date logic uses the market's local calendar date (ex_date vs period_end), as
the handbook recommends, never UTC timestamps.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ledger import Ledger, LedgerError, default_root  # noqa: E402
from money import D  # noqa: E402

SHARE_RATIO_ACTIONS = ("split", "reverse_split", "stock_dividend")
PER_SHARE = {"eps_basic", "eps_diluted", "dividends_per_share", "bvps",
             "fcf_per_share", "price"}
SHARE_COUNTS = {"shares_outstanding", "shares_diluted", "shares_basic_weighted",
                "shares_diluted_weighted"}


def factor_after(L: Ledger, date: str) -> tuple[Decimal, list[str]]:
    """Cumulative new/old share ratio for events with ex_date after `date`."""
    f, ids = Decimal(1), []
    d = dt.date.fromisoformat(date)
    for e in L.current("corporate_action"):
        if e["action"] in SHARE_RATIO_ACTIONS and dt.date.fromisoformat(e["ex_date"]) > d:
            f *= D(e["ratio"])
            ids.append(e["id"])
    return f, ids


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--root", type=Path, default=default_root())
    p.add_argument("--actor")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("adjust", help="restate a metric onto the current share basis")
    s.add_argument("--security", "-s", required=True)
    s.add_argument("--metric", required=True)
    s = sub.add_parser("events", help="list corporate actions and identifier changes")
    s.add_argument("--security", "-s", required=True)
    a = p.parse_args(argv)
    L = Ledger(a.root, a.security)
    try:
        if a.cmd == "events":
            for e in sorted(L.current("corporate_action"), key=lambda e: e["ex_date"]):
                print(json.dumps({k: e.get(k) for k in (
                    "id", "action", "ex_date", "ratio", "amount", "currency",
                    "old_identifier", "new_identifier", "source")}))
            return 0
        if a.metric not in PER_SHARE | SHARE_COUNTS:
            raise LedgerError(f"{a.metric} is not a per-share or share-count metric")
        series, inputs, warns = [], {}, []
        for e in sorted(L.find_facts(a.metric), key=lambda e: e.get("period_end") or e.get("as_of") or ""):
            date = e.get("as_of") or e.get("period_end")
            if not date:
                warns.append(f"{e['id']} has no period_end/as_of; cannot place it "
                             "relative to splits, excluded")
                continue
            f, ca_ids = factor_after(L, date)
            v = D(e["value"])
            adj = v / f if a.metric in PER_SHARE else v * f
            series.append({"period": e["period"], "date": date, "fact": e["id"],
                           "reported": str(v), "factor": str(f),
                           "adjusted": str(adj), "corporate_actions": ca_ids})
            inputs[f"{a.metric}@{e['period']}#{e['id']}"] = {
                "id": e["id"], "value": e["value"], "unit": e["unit"]}
            for c in ca_ids:
                inputs[f"ca#{c}"] = {"id": c}
        if not L.current("corporate_action"):
            warns.append("no corporate actions recorded; confirm there were no "
                         "splits rather than assuming it")
        entry = L.append("computation", {"method": f"split_adjust:{a.metric}",
                                         "inputs": inputs, "params": {},
                                         "outputs": {"series": series},
                                         "warnings": warns}, a.actor)
        print(json.dumps(entry, indent=2))
        for w in warns:
            print(f"WARNING: {w}", file=sys.stderr)
        return 0
    except LedgerError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Cross-source reconciliation and accounting-identity checks.

  sources     compare every (metric, period) reported by more than one source
              and classify each difference ("break") instead of picking one
  identities  check the statements against themselves (A = L + E, etc.) and
              flag impossible values

Classification mirrors handbook break management (paraphrased): timing
differences are expected and tracked, unit/scale errors are mechanical, and
anything else is a genuine break that must be explained before the number is
used. Results are appended as a K- check entry. Exit code 1 means at least one
unresolved break.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ledger import Ledger, LedgerError, SOURCE_TIERS, default_root  # noqa: E402
from money import D  # noqa: E402

SCALES = [Decimal(10) ** k for k in (3, 6, 9)]
BLOCKING = {"BREAK", "SCALE_MISMATCH", "SIGN_MISMATCH", "CURRENCY_MISMATCH",
            "PERIOD_MISMATCH", "TIMING_OR_RESTATEMENT", "IDENTITY_BREAK",
            "IMPOSSIBLE_VALUE"}


def classify(ref: dict, other: dict, rel_tol: Decimal, abs_tol: Decimal) -> str:
    if ref["unit"] != other["unit"]:
        return "CURRENCY_MISMATCH"
    if ref.get("period_end") and other.get("period_end") and \
            ref["period_end"] != other["period_end"]:
        return "PERIOD_MISMATCH"
    a, b = D(ref["value"]), D(other["value"])
    if a == b:
        return "MATCH"
    diff = abs(a - b)
    if diff <= abs_tol or (a != 0 and diff / abs(a) <= rel_tol):
        return "WITHIN_TOLERANCE"
    if a != 0 and b != 0:
        if abs(a + b) <= max(abs_tol, abs(a) * rel_tol):
            return "SIGN_MISMATCH"
        q = abs(a / b)
        for s in SCALES:
            if abs(q - s) / s < Decimal("0.01") or abs(q - 1 / s) * s < Decimal("0.01"):
                return "SCALE_MISMATCH"
    labels = f"{ref.get('source', '')} {other.get('source', '')}".lower()
    if any(k in labels for k in ("amend", "/a", "restat", "recast")):
        return "TIMING_OR_RESTATEMENT"
    return "BREAK"


def cmd_sources(L: Ledger, a) -> list[dict]:
    groups = defaultdict(list)
    for e in L.current("fact"):
        groups[(e["metric"], e["period"])].append(e)
    tier = {t: i for i, t in enumerate(SOURCE_TIERS)}
    results = []
    for (metric, period), facts in sorted(groups.items()):
        facts.sort(key=lambda e: tier.get(e.get("source_tier"), 9))
        ref = facts[0]
        if ref.get("source_tier") != "primary":
            results.append({"metric": metric, "period": period, "ref": ref["id"],
                            "status": "NO_PRIMARY_SOURCE"})
        sources = {f.get("source") for f in facts}
        if len(sources) < 2:
            results.append({"metric": metric, "period": period, "ref": ref["id"],
                            "status": "SINGLE_SOURCE"})
            continue
        for other in facts[1:]:
            if other.get("source") == ref.get("source"):
                continue
            st = classify(ref, other, D(a.rel_tol), D(a.abs_tol))
            results.append({"metric": metric, "period": period,
                            "ref": ref["id"], "other": other["id"],
                            "ref_value": ref["value"], "other_value": other["value"],
                            "status": st})
    return results


IDENTITIES = [
    ("balance_sheet", "total_assets", ["total_liabilities", "equity", "+minority_interest"]),
    ("gross_profit", "gross_profit", ["revenue", "-cogs"]),
]


def cmd_identities(L: Ledger, a) -> list[dict]:
    out = []
    y = a.period

    def val(m):
        e = L.best_fact(m, y)
        return (D(e["value"]), e["id"]) if e else (None, None)

    for name, lhs, parts in IDENTITIES:
        lv, lid = val(lhs)
        if lv is None:
            out.append({"check": name, "status": "UNAVAILABLE", "missing": lhs})
            continue
        total, ids, missing = Decimal(0), [lid], []
        for p in parts:
            optional = p.startswith("+")
            sign = -1 if p.startswith("-") else 1
            m = p.lstrip("+-")
            v, i = val(m)
            if v is None:
                if not optional:
                    missing.append(m)
                continue
            total += sign * v
            ids.append(i)
        if missing:
            out.append({"check": name, "status": "UNAVAILABLE", "missing": missing})
            continue
        diff = lv - total
        ok = abs(diff) <= max(D(a.abs_tol), abs(lv) * D(a.rel_tol))
        out.append({"check": name, "status": "OK" if ok else "IDENTITY_BREAK",
                    "lhs": str(lv), "rhs": str(total), "diff": str(diff), "refs": ids})

    for small, big in (("current_assets", "total_assets"),
                       ("long_term_debt", "total_debt"),
                       ("current_liabilities", "total_liabilities")):
        s, si = val(small)
        b, bi = val(big)
        if s is not None and b is not None and s > b * (1 + D(a.rel_tol)):
            out.append({"check": f"{small}<={big}", "status": "IDENTITY_BREAK",
                        "refs": [si, bi]})

    for m in ("revenue", "total_assets", "shares_outstanding", "shares_diluted", "price"):
        v, i = val(m)
        if v is not None and v <= 0:
            out.append({"check": f"{m}>0", "status": "IMPOSSIBLE_VALUE", "refs": [i]})
    for e in L.current("fact"):
        if e["unit"] == "pct" and not (Decimal(-1000) <= D(e["value"]) <= Decimal(1000)):
            out.append({"check": "pct_range", "status": "IMPOSSIBLE_VALUE",
                        "refs": [e["id"]]})

    price, pi = val("price") if y == "spot" else (None, None)
    if y == "spot":
        mc, mi = val("market_cap")
        sh = L.best_fact("shares_outstanding", a.shares_period) if a.shares_period else None
        if price is not None and mc is not None and sh:
            implied = price * D(sh["value"])
            diff = abs(implied - mc) / mc if mc else None
            out.append({"check": "market_cap~price*shares",
                        "status": "OK" if diff is not None and diff < Decimal("0.05") else "IDENTITY_BREAK",
                        "implied": str(implied), "reported": str(mc),
                        "refs": [pi, mi, sh["id"]]})
    return out


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--root", type=Path, default=default_root())
    p.add_argument("--actor")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("sources", "identities"):
        s = sub.add_parser(name)
        s.add_argument("--security", "-s", required=True)
        s.add_argument("--rel-tol", default="0.005", help="relative, 0.005 = 0.5%%")
        s.add_argument("--abs-tol", default="1")
        if name == "identities":
            s.add_argument("--period", required=True)
            s.add_argument("--shares-period", help="for the spot market-cap check")
    a = p.parse_args(argv)
    L = Ledger(a.root, a.security)
    try:
        results = cmd_sources(L, a) if a.cmd == "sources" else cmd_identities(L, a)
    except LedgerError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    counts = defaultdict(int)
    for r in results:
        counts[r["status"]] += 1
    blocking = [r for r in results if r["status"] in BLOCKING]
    refs = sorted({x for r in results for x in
                   ([r.get("ref"), r.get("other")] + r.get("refs", [])) if x})
    entry = L.append("check", {"check": f"reconcile_{a.cmd}",
                               "period": getattr(a, "period", None),
                               "summary": dict(counts), "results": results,
                               "unresolved": len(blocking), "refs": refs}, a.actor)
    print(json.dumps({"id": entry["id"], "summary": dict(counts),
                      "unresolved": blocking}, indent=2))
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Financial-strength and earnings-quality scores computed from ledger facts.

Commands: piotroski, altman, beneish, quality.

Inputs are looked up by standard metric name and period (see
references/metrics.md). When a required fact is missing the score component is
reported as unavailable; it is never filled with a guess. Each run appends a
C- computation entry listing every fact id it used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ledger import Ledger, LedgerError, default_root  # noqa: E402
from money import D, MoneyError  # noqa: E402

SCRIPT_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:16]
ZERO, ONE = Decimal(0), Decimal(1)


class Missing(Exception):
    pass


class Facts:
    def __init__(self, L: Ledger):
        self.L = L
        self.used: dict[str, dict] = {}
        self.missing: list[str] = []
        self.currency: str | None = None

    def get(self, metric: str, period: str) -> Decimal:
        e = self.L.best_fact(metric, period)
        if e is None:
            self.missing.append(f"{metric}@{period}")
            raise Missing(f"{metric}@{period}")
        unit = e["unit"]
        if unit not in ("shares", "ratio", "pct", "count", "per_share"):
            if self.currency and unit != self.currency:
                raise LedgerError(f"{e['id']} is {unit}, other facts are "
                                  f"{self.currency}")
            self.currency = self.currency or unit
        self.used[f"{metric}@{period}"] = {"id": e["id"], "value": e["value"],
                                           "unit": unit}
        return D(e["value"])

    def opt(self, metric: str, period: str, default=None):
        try:
            return self.get(metric, period)
        except Missing:
            self.missing.pop()
            return default


def ratio(a, b):
    if b == 0:
        raise Missing("division by zero")
    return a / b


def record(L, method, F: Facts, outputs, warnings, actor):
    out = json.loads(json.dumps(outputs, default=str))
    e = L.append("computation", {"method": method, "inputs": F.used,
                                 "params": {}, "outputs": out,
                                 "warnings": warnings,
                                 "missing": sorted(set(F.missing)),
                                 "script_sha": SCRIPT_SHA}, actor)
    print(json.dumps(e, indent=2))
    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)


def signal(results, name, fn):
    try:
        results[name] = 1 if fn() else 0
    except Missing as m:
        results[name] = f"unavailable ({m})"


def cmd_piotroski(L, a):
    F, t, p = Facts(L), a.year, a.prior
    g = F.get
    s: dict = {}
    roa = lambda y: ratio(g("net_income", y), g("total_assets", y))
    lev = lambda y: ratio(g("long_term_debt", y), g("total_assets", y))
    cr = lambda y: ratio(g("current_assets", y), g("current_liabilities", y))
    gm = lambda y: ratio(g("revenue", y) - g("cogs", y), g("revenue", y))
    at = lambda y: ratio(g("revenue", y), g("total_assets", y))
    signal(s, "1_roa_positive", lambda: roa(t) > 0)
    signal(s, "2_cfo_positive", lambda: g("cfo", t) > 0)
    signal(s, "3_roa_improving", lambda: roa(t) > roa(p))
    signal(s, "4_cfo_exceeds_net_income", lambda: g("cfo", t) > g("net_income", t))
    signal(s, "5_leverage_falling", lambda: lev(t) < lev(p))
    signal(s, "6_current_ratio_rising", lambda: cr(t) > cr(p))
    signal(s, "7_no_dilution", lambda: g("shares_outstanding", t) <= g("shares_outstanding", p))
    signal(s, "8_gross_margin_rising", lambda: gm(t) > gm(p))
    signal(s, "9_asset_turnover_rising", lambda: at(t) > at(p))
    scored = [v for v in s.values() if isinstance(v, int)]
    out = {"signals": s, "score": sum(scored), "out_of": len(scored),
           "variant": "end-of-year assets for ROA", "year": t, "prior": p}
    warns = [] if len(scored) == 9 else [
        f"only {len(scored)}/9 signals computable; score is not comparable to 0-9"]
    if len(scored) == 9:
        out["reading"] = ("strong" if out["score"] >= 7 else
                          "weak" if out["score"] <= 3 else "middling")
    record(L, "piotroski", F, out, warns, a.actor)


def cmd_altman(L, a):
    F, t = Facts(L), a.year
    g = F.get
    warns = []
    try:
        ta = g("total_assets", t)
        x1 = ratio(g("current_assets", t) - g("current_liabilities", t), ta)
        x2 = ratio(g("retained_earnings", t), ta)
        x3 = ratio(g("ebit", t), ta)
        tl = g("total_liabilities", t)
        if a.model == "original":
            mve = F.opt("market_cap", a.market_period or "spot")
            if mve is None:
                raise Missing("market_cap@" + (a.market_period or "spot"))
            x4 = ratio(mve, tl)
            x5 = ratio(g("revenue", t), ta)
            z = (Decimal("1.2") * x1 + Decimal("1.4") * x2 + Decimal("3.3") * x3
                 + Decimal("0.6") * x4 + x5)
            zone = "safe" if z > Decimal("2.99") else "grey" if z >= Decimal("1.81") else "distress"
            xs = {"x1": x1, "x2": x2, "x3": x3, "x4": x4, "x5": x5}
        else:
            x4 = ratio(g("equity", t), tl)
            z = (Decimal("6.56") * x1 + Decimal("3.26") * x2 +
                 Decimal("6.72") * x3 + Decimal("1.05") * x4)
            zone = "safe" if z > Decimal("2.6") else "grey" if z >= Decimal("1.1") else "distress"
            xs = {"x1": x1, "x2": x2, "x3": x3, "x4": x4}
        out = {"model": a.model, "z": z, "zone": zone, "components": xs, "year": t}
    except Missing as m:
        out = {"model": a.model, "z": None, "unavailable": str(m), "year": t}
    if a.model == "original":
        warns.append("original Z was fit on manufacturers; use --model zpp for "
                     "non-manufacturers; not meaningful for banks/insurers")
    record(L, "altman_z", F, out, warns, a.actor)


def cmd_beneish(L, a):
    F, t, p = Facts(L), a.year, a.prior
    g = F.get
    warns = []
    try:
        sec_t = F.opt("securities", t, ZERO)
        sec_p = F.opt("securities", p, ZERO)
        if "securities@" + t not in F.used:
            warns.append("securities not in ledger; treated as 0 in AQI")
        rev_t, rev_p = g("revenue", t), g("revenue", p)
        gm = lambda y, r: ratio(r - g("cogs", y), r)
        aq = lambda y, s: ONE - ratio(g("current_assets", y) + g("ppe_net", y) + s,
                                      g("total_assets", y))
        dep = lambda y: ratio(g("dna", y), g("dna", y) + g("ppe_net", y))
        lv = lambda y: ratio(g("current_liabilities", y) + g("long_term_debt", y),
                             g("total_assets", y))
        idx = {
            "DSRI": ratio(ratio(g("receivables", t), rev_t), ratio(g("receivables", p), rev_p)),
            "GMI": ratio(gm(p, rev_p), gm(t, rev_t)),
            "AQI": ratio(aq(t, sec_t), aq(p, sec_p)),
            "SGI": ratio(rev_t, rev_p),
            "DEPI": ratio(dep(p), dep(t)),
            "SGAI": ratio(ratio(g("sga", t), rev_t), ratio(g("sga", p), rev_p)),
            "LVGI": ratio(lv(t), lv(p)),
            "TATA": ratio(g("net_income", t) - g("cfo", t), g("total_assets", t)),
        }
        w = {"DSRI": "0.920", "GMI": "0.528", "AQI": "0.404", "SGI": "0.892",
             "DEPI": "0.115", "SGAI": "-0.172", "TATA": "4.679", "LVGI": "-0.327"}
        m = Decimal("-4.84") + sum(D(w[k]) * v for k, v in idx.items())
        flag = ("likely manipulator" if m > Decimal("-1.78") else
                "grey zone" if m > Decimal("-2.22") else "unlikely manipulator")
        out = {"m_score": m, "reading": flag, "indices": idx, "year": t, "prior": p}
    except Missing as exc:
        out = {"m_score": None, "unavailable": str(exc), "year": t, "prior": p}
    warns.append("Beneish M is a screen for further reading, not evidence of fraud")
    record(L, "beneish_m", F, out, warns, a.actor)


def cmd_quality(L, a):
    F = Facts(L)
    g = F.get
    rows = {}
    for y in a.periods.split(","):
        y = y.strip()
        r: dict = {}
        def put(name, fn):
            try:
                r[name] = fn()
            except Missing as m:
                r[name] = f"unavailable ({m})"
        put("gross_margin", lambda: ratio(g("revenue", y) - g("cogs", y), g("revenue", y)))
        put("operating_margin", lambda: ratio(g("ebit", y), g("revenue", y)))
        def roic():
            pt = g("pretax_income", y)
            if pt <= 0:
                raise Missing("pretax income not positive; tax rate undefined")
            tax = min(max(ratio(g("tax_expense", y), pt), ZERO), Decimal("0.5"))
            ic = g("equity", y) + g("total_debt", y) - g("cash", y)
            if ic <= 0:
                raise Missing("non-positive invested capital")
            return ratio(g("ebit", y) * (ONE - tax), ic)
        put("roic", roic)
        put("fcf", lambda: g("cfo", y) - abs(g("capex", y)))
        put("fcf_conversion", lambda: ratio(g("cfo", y) - abs(g("capex", y)), g("net_income", y)))
        put("accruals_ratio", lambda: ratio(g("net_income", y) - g("cfo", y), g("total_assets", y)))
        put("net_debt_to_ebitda", lambda: ratio(g("total_debt", y) - g("cash", y),
                                                g("ebit", y) + g("dna", y)))
        put("interest_cover", lambda: ratio(g("ebit", y), g("interest_expense", y)))
        rows[y] = r
    warns = []
    roics = [v for v in (r.get("roic") for r in rows.values()) if isinstance(v, Decimal)]
    out = {"by_period": rows}
    if roics:
        out["roic_min"], out["roic_median"] = min(roics), sorted(roics)[len(roics) // 2]
        if len(roics) < 5:
            warns.append(f"only {len(roics)} periods of ROIC; a moat claim needs a cycle (5-10y)")
    record(L, "quality", F, out, warns, a.actor)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--root", type=Path, default=default_root())
    p.add_argument("--actor")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("piotroski", "beneish"):
        s = sub.add_parser(name)
        s.add_argument("--security", "-s", required=True)
        s.add_argument("--year", required=True); s.add_argument("--prior", required=True)
    s = sub.add_parser("altman")
    s.add_argument("--security", "-s", required=True)
    s.add_argument("--year", required=True)
    s.add_argument("--model", choices=("original", "zpp"), default="zpp")
    s.add_argument("--market-period", help="period label of the market_cap fact")
    s = sub.add_parser("quality")
    s.add_argument("--security", "-s", required=True)
    s.add_argument("--periods", required=True, help="FY2021,FY2022,...")
    a = p.parse_args(argv)
    L = Ledger(a.root, a.security)
    try:
        {"piotroski": cmd_piotroski, "altman": cmd_altman,
         "beneish": cmd_beneish, "quality": cmd_quality}[a.cmd](L, a)
        return 0
    except (LedgerError, MoneyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

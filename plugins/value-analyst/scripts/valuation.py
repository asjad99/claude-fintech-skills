#!/usr/bin/env python3
"""Intrinsic-value calculators that only accept ledger ids as inputs.

Every input is an F- (fact) or A- (assumption) id; the script resolves the
value from the ledger, refuses superseded or unit-mismatched inputs, does all
arithmetic in Decimal, and appends a C- (computation) entry listing exactly
which ids and values produced the output. Nothing is typed in by hand, so no
number in a valuation can be invented.

Methods: dcf, reverse-dcf, epv, graham-number, ncav, owner-earnings, mos.
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
from money import D, MoneyError, is_currency, round_display  # noqa: E402

SCRIPT_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:16]
ZERO, ONE = Decimal(0), Decimal(1)


class Inputs:
    """Resolves ledger ids, tracks provenance, checks units."""

    def __init__(self, ledger: Ledger):
        self.L = ledger
        self.used: dict[str, dict] = {}

    def _entry(self, name: str, eid: str) -> dict:
        e = self.L.get(eid)
        if e["type"] not in ("fact", "assumption", "computation"):
            raise LedgerError(f"{name}: {eid} is a {e['type']}, not a number")
        live = self.L.resolve(eid)
        if live["id"] != eid:
            raise LedgerError(f"{name}: {eid} was superseded by {live['id']}; "
                              "use the live entry")
        return e

    def rate(self, name: str, eid: str) -> Decimal:
        e = self._entry(name, eid)
        v = D(e["value"])
        if e["unit"] == "pct":
            v = v / 100
        elif e["unit"] != "ratio":
            raise LedgerError(f"{name}: {eid} has unit {e['unit']}, need pct/ratio")
        self.used[name] = {"id": eid, "value": str(v), "unit": "ratio"}
        return v

    def count(self, name: str, eid: str, unit: str) -> Decimal:
        e = self._entry(name, eid)
        if e["unit"] != unit:
            raise LedgerError(f"{name}: {eid} has unit {e['unit']}, need {unit}")
        v = D(e["value"])
        self.used[name] = {"id": eid, "value": str(v), "unit": unit}
        return v

    def money(self, name: str, eid: str, currency: str | None = None):
        e = self._entry(name, eid)
        if e["type"] == "computation":
            unit = e["outputs"].get("currency", "")
            v = D(e["outputs"]["value_per_share"])
        else:
            unit = e["unit"]
            if unit == "per_share":
                unit = e["currency"]
            v = D(e["value"])
        if not is_currency(unit):
            raise LedgerError(f"{name}: {eid} has unit {unit}, need a currency")
        if currency and unit != currency:
            raise LedgerError(f"{name}: {eid} is {unit}, other inputs are "
                              f"{currency}; record an FX fact and pass --fx")
        self.used[name] = {"id": eid, "value": str(v), "unit": unit}
        return v, unit

    def optional_money(self, name, eid, currency):
        if not eid:
            return ZERO
        return self.money(name, eid, currency)[0]


def net_debt(inp: Inputs, a, ccy: str) -> Decimal:
    if a.net_debt:
        return inp.money("net_debt", a.net_debt, ccy)[0]
    debt = inp.optional_money("debt", a.debt, ccy)
    cash = inp.optional_money("cash", a.cash, ccy)
    if not (a.debt or a.cash):
        raise LedgerError("pass --net-debt, or --debt and/or --cash "
                          "(no silent zero balance sheet)")
    return debt - cash


def to_trading(inp: Inputs, a, value: Decimal, ccy: str) -> tuple[Decimal, str]:
    sec = inp.L.security()
    target = sec["currency"]
    if ccy == target:
        return value, ccy
    if not a.fx:
        raise LedgerError(f"value is in {ccy} but the security trades in "
                          f"{target}; record fact fx_{ccy}{target} and pass --fx")
    e = inp._entry("fx", a.fx)
    if e["metric"] != f"fx_{ccy}{target}":
        raise LedgerError(f"--fx {a.fx} is {e['metric']}, need fx_{ccy}{target}"
                          " (rates are directional; record the right one)")
    rate = D(e["value"])
    inp.used["fx"] = {"id": a.fx, "value": str(rate), "unit": f"{target}/{ccy}"}
    return value * rate, target


def dcf_per_share(fcf0, g, n, gt, r, nd, shares, fade=False):
    if r <= gt:
        raise LedgerError("discount rate must exceed terminal growth")
    if shares <= 0:
        raise LedgerError("share count must be positive")
    pv, fcf, flows = ZERO, fcf0, []
    for t in range(1, n + 1):
        gt_t = g + (gt - g) * Decimal(t - 1) / Decimal(max(n - 1, 1)) if fade else g
        fcf = fcf * (ONE + gt_t)
        disc = (ONE + r) ** t
        pv += fcf / disc
        flows.append({"year": t, "fcf": str(fcf), "pv": str(fcf / disc)})
    tv = fcf * (ONE + gt) / (r - gt)
    pv_tv = tv / (ONE + r) ** n
    ev = pv + pv_tv
    equity = ev - nd
    return {"enterprise_value": ev, "pv_explicit": pv, "pv_terminal": pv_tv,
            "terminal_share_of_ev": (pv_tv / ev) if ev else None,
            "equity_value": equity, "value_per_share": equity / shares,
            "flows": flows}


def record(L: Ledger, method: str, inp: Inputs, outputs: dict, params: dict,
           warnings: list[str], actor):
    out = {k: (str(v) if isinstance(v, Decimal) else v)
           for k, v in outputs.items()}
    entry = L.append("computation", {
        "method": method, "inputs": inp.used, "params": params,
        "outputs": out, "warnings": warnings, "script_sha": SCRIPT_SHA}, actor)
    print(json.dumps(entry, indent=2))
    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)


def cmd_dcf(L, a):
    inp = Inputs(L)
    fcf0, ccy = inp.money("fcf0", a.fcf0)
    g = inp.rate("growth", a.growth)
    n = int(inp.count("years", a.years, "years"))
    gt = inp.rate("terminal_growth", a.terminal_growth)
    r = inp.rate("discount_rate", a.discount_rate)
    nd = net_debt(inp, a, ccy)
    shares = inp.count("shares", a.shares, "shares")
    res = dcf_per_share(fcf0, g, n, gt, r, nd, shares, a.fade)
    vps, out_ccy = to_trading(inp, a, res["value_per_share"], ccy)
    warnings = []
    if res["terminal_share_of_ev"] and res["terminal_share_of_ev"] > Decimal("0.75"):
        warnings.append("terminal value is >75% of EV: the answer is mostly "
                        "the terminal assumptions")
    if gt > Decimal("0.04"):
        warnings.append("terminal growth above 4% exceeds long-run nominal GDP")
    if fcf0 <= 0:
        warnings.append("starting FCF is not positive; DCF is not meaningful")
    grid = []
    for dr in (Decimal("-0.02"), Decimal("-0.01"), ZERO, Decimal("0.01"), Decimal("0.02")):
        row = {"discount_rate": str(r + dr)}
        for dg in (Decimal("-0.01"), ZERO, Decimal("0.01")):
            try:
                v = dcf_per_share(fcf0, g, n, gt + dg, r + dr, nd, shares, a.fade)
                row[f"tg={gt + dg}"] = round_display(
                    to_trading(inp, a, v["value_per_share"], ccy)[0])
            except LedgerError:
                row[f"tg={gt + dg}"] = "n/a"
        grid.append(row)
    record(L, "dcf", inp, {
        "value_per_share": vps, "currency": out_ccy,
        "enterprise_value": res["enterprise_value"],
        "equity_value": res["equity_value"], "value_currency": ccy,
        "terminal_share_of_ev": res["terminal_share_of_ev"],
        "flows": res["flows"], "sensitivity": grid},
        {"fade": a.fade}, warnings, a.actor)


def cmd_reverse_dcf(L, a):
    inp = Inputs(L)
    fcf0, ccy = inp.money("fcf0", a.fcf0)
    n = int(inp.count("years", a.years, "years"))
    gt = inp.rate("terminal_growth", a.terminal_growth)
    r = inp.rate("discount_rate", a.discount_rate)
    nd = net_debt(inp, a, ccy)
    shares = inp.count("shares", a.shares, "shares")
    price, pccy = inp.money("price", a.price)
    # Express the price in the cash-flow currency for the solve.
    if pccy != ccy:
        if not a.fx:
            raise LedgerError("price and cash flows differ in currency; pass --fx")
        e = inp._entry("fx", a.fx)
        if e["metric"] != f"fx_{ccy}{pccy}":
            raise LedgerError(f"need fx_{ccy}{pccy}")
        price = price / D(e["value"])
        inp.used["fx"] = {"id": a.fx, "value": e["value"], "unit": f"{pccy}/{ccy}"}
    lo, hi = Decimal("-0.5"), Decimal("1.0")
    f = lambda g: dcf_per_share(fcf0, g, n, gt, r, nd, shares)["value_per_share"] - price
    if f(lo) > 0 or f(hi) < 0:
        record(L, "reverse_dcf", inp, {"implied_growth": None,
               "note": "no growth rate in [-50%, 100%] justifies the price"},
               {}, [], a.actor)
        return
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) > 0:
            hi = mid
        else:
            lo = mid
        if hi - lo < Decimal("1e-9"):
            break
    record(L, "reverse_dcf", inp, {"implied_growth": (lo + hi) / 2,
           "years": n}, {}, [], a.actor)


def cmd_epv(L, a):
    inp = Inputs(L)
    ebit, ccy = inp.money("normalized_ebit", a.ebit)
    tax = inp.rate("tax_rate", a.tax_rate)
    r = inp.rate("cost_of_capital", a.discount_rate)
    adj = inp.optional_money("excess_dna", a.excess_dna, ccy)
    nd = net_debt(inp, a, ccy)
    shares = inp.count("shares", a.shares, "shares")
    if r <= 0:
        raise LedgerError("cost of capital must be positive")
    earnings_power = ebit * (ONE - tax) + adj
    epv = earnings_power / r
    vps, out_ccy = to_trading(inp, a, (epv - nd) / shares, ccy)
    record(L, "epv", inp, {"earnings_power": earnings_power, "epv": epv,
           "value_per_share": vps, "currency": out_ccy}, {}, [], a.actor)


def cmd_graham(L, a):
    inp = Inputs(L)
    eps, ccy = inp.money("eps", a.eps)
    bvps, _ = inp.money("bvps", a.bvps, ccy)
    if eps <= 0 or bvps <= 0:
        record(L, "graham_number", inp, {"value_per_share": None,
               "note": "undefined for non-positive EPS or book value"},
               {}, [], a.actor)
        return
    vps, out_ccy = to_trading(inp, a, (Decimal("22.5") * eps * bvps).sqrt(), ccy)
    record(L, "graham_number", inp, {"value_per_share": vps,
           "currency": out_ccy}, {}, [
           "Graham number is a screen ceiling, not an intrinsic value"], a.actor)


def cmd_ncav(L, a):
    inp = Inputs(L)
    ca, ccy = inp.money("current_assets", a.current_assets)
    tl, _ = inp.money("total_liabilities", a.total_liabilities, ccy)
    pref = inp.optional_money("preferred", a.preferred, ccy)
    shares = inp.count("shares", a.shares, "shares")
    vps, out_ccy = to_trading(inp, a, (ca - tl - pref) / shares, ccy)
    record(L, "ncav", inp, {"value_per_share": vps, "currency": out_ccy,
           "net_net_threshold": vps * Decimal("2") / 3}, {}, [], a.actor)


def cmd_owner_earnings(L, a):
    inp = Inputs(L)
    ni, ccy = inp.money("net_income", a.net_income)
    dna, _ = inp.money("dna", a.dna, ccy)
    mcap, _ = inp.money("maintenance_capex", a.maintenance_capex, ccy)
    dwc = inp.optional_money("delta_working_capital", a.delta_wc, ccy)
    oe = ni + dna - abs(mcap) - dwc
    out = {"owner_earnings": oe, "currency": ccy}
    if a.shares:
        out["per_share"] = oe / inp.count("shares", a.shares, "shares")
    record(L, "owner_earnings", inp, out, {}, [], a.actor)


def cmd_mos(L, a):
    inp = Inputs(L)
    values = []
    for i, cid in enumerate(a.value):
        e = L.get(cid)
        if e["type"] != "computation" or e["outputs"].get("value_per_share") in (None, "None"):
            raise LedgerError(f"{cid} is not a computation with a value_per_share")
        v, ccy = inp.money(f"value_{i + 1}", cid)
        values.append((v, ccy, e["method"]))
    price, pccy = inp.money("price", a.price)
    if any(c != pccy for _, c, _ in values):
        raise LedgerError("all values must be in the trading currency")
    required = D(a.required_pct) / 100
    vs = sorted(v for v, _, _ in values)
    conservative = vs[0]
    central = vs[len(vs) // 2]
    mos = lambda iv: (ONE - price / iv) if iv > 0 else None
    out = {"price": price, "currency": pccy,
           "conservative_value": conservative, "central_value": central,
           "mos_vs_conservative": mos(conservative),
           "mos_vs_central": mos(central), "required_mos": required,
           "buy_below": conservative * (ONE - required),
           "passes": bool(mos(conservative) is not None and
                          mos(conservative) >= required),
           "methods": [m for _, _, m in values]}
    spread = (vs[-1] / vs[0] - 1) if vs[0] > 0 else None
    warns = []
    if spread is not None and spread > Decimal("0.5"):
        warns.append("methods disagree by >50%: treat the value as a wide range")
    record(L, "margin_of_safety", inp, out, {"required_pct": a.required_pct},
           warns, a.actor)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--root", type=Path, default=default_root())
    p.add_argument("--actor")
    sub = p.add_subparsers(dest="cmd", required=True)

    def base(name, help_):
        s = sub.add_parser(name, help=help_)
        s.add_argument("--security", "-s", required=True)
        s.add_argument("--fx", help="F-id of fx_<VALUECCY><TRADINGCCY> fact")
        return s

    def bs(s):
        s.add_argument("--net-debt"); s.add_argument("--debt"); s.add_argument("--cash")

    s = base("dcf", "two-stage discounted free cash flow")
    for f in ("fcf0", "growth", "years", "terminal-growth", "discount-rate", "shares"):
        s.add_argument(f"--{f}", required=True)
    bs(s); s.add_argument("--fade", action="store_true",
                          help="fade growth linearly to terminal growth")
    s = base("reverse-dcf", "growth rate the current price implies")
    for f in ("fcf0", "years", "terminal-growth", "discount-rate", "shares", "price"):
        s.add_argument(f"--{f}", required=True)
    bs(s)
    s = base("epv", "earnings power value (no growth)")
    for f in ("ebit", "tax-rate", "discount-rate", "shares"):
        s.add_argument(f"--{f}", required=True)
    s.add_argument("--excess-dna"); bs(s)
    s = base("graham-number", "sqrt(22.5 x EPS x BVPS)")
    s.add_argument("--eps", required=True); s.add_argument("--bvps", required=True)
    s = base("ncav", "net current asset value per share")
    for f in ("current-assets", "total-liabilities", "shares"):
        s.add_argument(f"--{f}", required=True)
    s.add_argument("--preferred")
    s = base("owner-earnings", "NI + D&A - maintenance capex - dWC")
    for f in ("net-income", "dna", "maintenance-capex"):
        s.add_argument(f"--{f}", required=True)
    s.add_argument("--delta-wc"); s.add_argument("--shares")
    s = base("mos", "margin of safety across several valuations")
    s.add_argument("--value", action="append", required=True,
                   help="C-id of a valuation; repeat for each method")
    s.add_argument("--price", required=True)
    s.add_argument("--required-pct", default="30")

    a = p.parse_args(argv)
    L = Ledger(a.root, a.security)
    fn = {"dcf": cmd_dcf, "reverse-dcf": cmd_reverse_dcf, "epv": cmd_epv,
          "graham-number": cmd_graham, "ncav": cmd_ncav,
          "owner-earnings": cmd_owner_earnings, "mos": cmd_mos}[a.cmd]
    try:
        fn(L, a)
        return 0
    except (LedgerError, MoneyError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

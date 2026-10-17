#!/usr/bin/env python3
"""Evidence ledger: the append-only, hash-chained record behind every analysis.

One ledger per security at <root>/<KEY>/ledger.jsonl, raw source payloads at
<root>/<KEY>/raw/<sha256>.<ext>. Every number in a report must trace to an
entry here. Handbook tenets this enforces (paraphrased):

  No invented data  - every figure has a source, a period and a retrieval
                      time; computed figures list the entries they came from.
  No lost data      - raw payloads are stored before use; entries are never
                      edited or deleted; corrections are new entries that
                      point at what they supersede.
  No trust          - each entry hashes the previous one, so tampering breaks
                      `verify`; decisions need an independent reviewer.

Entry id prefixes: S security, R raw, F fact, A assumption, CA corporate
action, C computation, K reconciliation/check, N note, D decision, V review.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from money import D, MoneyError, check_unit, is_currency  # noqa: E402

GENESIS = "0" * 64
PREFIX = {"security": "S", "raw": "R", "fact": "F", "assumption": "A",
          "corporate_action": "CA", "computation": "C", "check": "K",
          "note": "N", "decision": "D", "review": "V"}
SOURCE_TIERS = ("primary", "secondary", "tertiary")
VERDICTS = ("CANDIDATE", "WATCHLIST", "PASS", "INSUFFICIENT_DATA")
CA_TYPES = ("split", "reverse_split", "cash_dividend", "stock_dividend",
            "spinoff", "merger", "rights", "ticker_change", "identifier_change")


class LedgerError(Exception):
    pass


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode()


def default_root() -> Path:
    return Path(os.environ.get("VALUE_ANALYST_ROOT", "research"))


class Ledger:
    def __init__(self, root: Path, key: str):
        if not key or any(c in key for c in "/\\ ") or key.startswith("."):
            raise LedgerError(f"bad security key {key!r}")
        self.dir = Path(root) / key
        self.path = self.dir / "ledger.jsonl"
        self.raw_dir = self.dir / "raw"
        self.key = key
        self._entries: list[dict] | None = None

    # ---------- reading ----------
    @property
    def entries(self) -> list[dict]:
        if self._entries is None:
            self._entries = []
            if self.path.exists():
                for n, line in enumerate(self.path.read_text().splitlines(), 1):
                    if line.strip():
                        try:
                            self._entries.append(json.loads(line))
                        except json.JSONDecodeError as exc:
                            raise LedgerError(f"line {n} is not JSON") from exc
        return self._entries

    def exists(self) -> bool:
        return self.path.exists()

    def get(self, eid: str) -> dict:
        for e in self.entries:
            if e["id"] == eid:
                return e
        raise LedgerError(f"no entry {eid} in {self.key}")

    def superseded_ids(self) -> set[str]:
        return {e["supersedes"] for e in self.entries if e.get("supersedes")}

    def current(self, etype: str | None = None) -> list[dict]:
        gone = self.superseded_ids()
        return [e for e in self.entries if e["id"] not in gone
                and (etype is None or e["type"] == etype)]

    def resolve(self, eid: str) -> dict:
        """Follow supersession forward to the live version of an entry."""
        e = self.get(eid)
        nxt = {x["supersedes"]: x for x in self.entries if x.get("supersedes")}
        while e["id"] in nxt:
            e = nxt[e["id"]]
        return e

    def find_facts(self, metric: str, period: str | None = None,
                   source_tier: str | None = None) -> list[dict]:
        out = [e for e in self.current("fact") if e["metric"] == metric]
        if period is not None:
            out = [e for e in out if e.get("period") == period]
        if source_tier:
            out = [e for e in out if e.get("source_tier") == source_tier]
        return out

    def best_fact(self, metric: str, period: str | None = None) -> dict | None:
        """Primary source first, then most recently retrieved."""
        facts = self.find_facts(metric, period)
        if not facts:
            return None
        tier = {t: i for i, t in enumerate(SOURCE_TIERS)}
        facts.sort(key=lambda e: (tier.get(e.get("source_tier"), 9),
                                  _neg_time(e.get("retrieved_at", ""))))
        return facts[0]

    def security(self) -> dict:
        sec = [e for e in self.current("security")]
        if not sec:
            raise LedgerError(f"{self.key} has no security entry; run init")
        return sec[-1]

    # ---------- writing ----------
    def append(self, etype: str, payload: dict, actor: str | None = None) -> dict:
        if etype not in PREFIX:
            raise LedgerError(f"unknown entry type {etype}")
        if etype != "security" and not self.exists():
            raise LedgerError(f"{self.key} not initialised; run init first")
        entries = self.entries
        seq = len(entries) + 1
        n = sum(1 for e in entries if e["type"] == etype) + 1
        entry = {
            "seq": seq,
            "id": f"{PREFIX[etype]}-{n:04d}",
            "type": etype,
            "recorded_at": now_utc(),
            "actor": actor or os.environ.get("VALUE_ANALYST_ACTOR", "analyst"),
            **payload,
            "prev_hash": entries[-1]["hash"] if entries else GENESIS,
        }
        entry["hash"] = hashlib.sha256(canonical(entry)).hexdigest()
        self.dir.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        entries.append(entry)
        return entry

    def store_raw(self, src: Path) -> tuple[str, Path]:
        data = Path(src).read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        dest = self.raw_dir / f"{sha}{Path(src).suffix or '.bin'}"
        if not dest.exists():
            shutil.copyfile(src, dest)
            os.chmod(dest, 0o444)
        return sha, dest

    # ---------- verification ----------
    def verify(self) -> list[str]:
        problems: list[str] = []
        prev = GENESIS
        ids: set[str] = set()
        for e in self.entries:
            body = {k: v for k, v in e.items() if k != "hash"}
            if e.get("prev_hash") != prev:
                problems.append(f"{e['id']}: chain broken (prev_hash mismatch)")
            if hashlib.sha256(canonical(body)).hexdigest() != e.get("hash"):
                problems.append(f"{e['id']}: content hash mismatch (edited?)")
            if e["id"] in ids:
                problems.append(f"{e['id']}: duplicate id")
            ids.add(e["id"])
            prev = e.get("hash")
        for e in self.entries:
            for ref in _refs_of(e):
                if ref not in ids:
                    problems.append(f"{e['id']}: references missing {ref}")
            if e["type"] == "raw":
                f = self.dir / e["path"]
                if not f.exists():
                    problems.append(f"{e['id']}: raw file missing {e['path']}")
                elif hashlib.sha256(f.read_bytes()).hexdigest() != e["sha256"]:
                    problems.append(f"{e['id']}: raw file altered")
            if e["type"] == "fact" and e.get("source_tier") != "primary" \
                    and not e.get("raw") and not e.get("url"):
                problems.append(f"{e['id']}: secondary fact with no url/raw")
        return problems


def _neg_time(s: str) -> str:
    # sort helper: later timestamps first
    return "".join(chr(0x10FFFF - ord(c)) for c in s)


def _refs_of(e: dict) -> list[str]:
    refs = []
    for k in ("supersedes", "raw", "decision"):
        if e.get(k):
            refs.append(e[k])
    refs += e.get("refs", []) or []
    refs += [v["id"] for v in (e.get("inputs") or {}).values()
             if isinstance(v, dict) and "id" in v]
    return refs


def parse_date(s: str | None, field: str) -> str | None:
    if s is None:
        return None
    try:
        return dt.date.fromisoformat(s).isoformat()
    except ValueError as exc:
        raise LedgerError(f"{field} must be YYYY-MM-DD, got {s!r}") from exc


def number_payload(value: str, unit: str, scale: str) -> dict:
    unit = check_unit(unit)
    reported = D(value)
    sc = D(scale)
    if sc <= 0:
        raise LedgerError("scale must be positive")
    return {"value": str(reported * sc), "unit": unit,
            "reported_value": value, "reported_scale": str(sc)}


# ---------------------------------------------------------------- CLI
def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--root", type=Path, default=default_root())
    p.add_argument("--actor", default=None)
    sub = p.add_subparsers(dest="cmd", required=True)

    def sec(sp):
        sp.add_argument("--security", "-s", required=True,
                        help="ledger key, e.g. ISIN or EXCHANGE-TICKER")
        return sp

    s = sec(sub.add_parser("init", help="create ledger with identifiers"))
    s.add_argument("--name", required=True)
    s.add_argument("--ticker", required=True)
    s.add_argument("--exchange", required=True)
    s.add_argument("--currency", required=True, help="trading currency")
    s.add_argument("--reporting-currency")
    s.add_argument("--isin"); s.add_argument("--cusip")
    s.add_argument("--figi"); s.add_argument("--cik"); s.add_argument("--sedol")
    s.add_argument("--fiscal-year-end", help="MM-DD")
    s.add_argument("--sector")

    s = sec(sub.add_parser("raw", help="store a raw source payload verbatim"))
    s.add_argument("file", type=Path)
    s.add_argument("--source", required=True)
    s.add_argument("--url")
    s.add_argument("--description", default="")

    s = sec(sub.add_parser("fact", help="record a sourced number"))
    s.add_argument("--metric", required=True)
    s.add_argument("--value", required=True, help="as a string, e.g. 1234.5")
    s.add_argument("--unit", required=True, help="ISO currency or " +
                   "shares|ratio|pct|count|days|years|per_share")
    s.add_argument("--scale", default="1", help="e.g. 1000000 if in millions")
    s.add_argument("--period", required=True, help="FY2025, Q2-2026, TTM-2026Q2, spot")
    s.add_argument("--period-end", help="YYYY-MM-DD")
    s.add_argument("--as-of", help="YYYY-MM-DD the value describes (prices)")
    s.add_argument("--source", required=True, help="e.g. 'SEC 10-K 2025'")
    s.add_argument("--source-tier", choices=SOURCE_TIERS, required=True)
    s.add_argument("--url"); s.add_argument("--raw", help="R-#### id")
    s.add_argument("--locator", help="page/table/XBRL tag")
    s.add_argument("--currency-of", help="currency when unit is per_share")
    s.add_argument("--supersedes"); s.add_argument("--reason")

    s = sec(sub.add_parser("assume", help="record an explicit assumption"))
    s.add_argument("--metric", required=True)
    s.add_argument("--value", required=True)
    s.add_argument("--unit", required=True)
    s.add_argument("--rationale", required=True)
    s.add_argument("--low"); s.add_argument("--high")
    s.add_argument("--refs", default="", help="comma-separated evidence ids")
    s.add_argument("--supersedes"); s.add_argument("--reason")

    s = sec(sub.add_parser("ca", help="record a corporate action"))
    s.add_argument("--action", choices=CA_TYPES, required=True)
    s.add_argument("--ex-date", required=True)
    s.add_argument("--record-date"); s.add_argument("--pay-date")
    s.add_argument("--ratio", help="new:old shares as decimal, e.g. 2 for 2:1")
    s.add_argument("--amount", help="per-share cash amount")
    s.add_argument("--currency")
    s.add_argument("--old-identifier"); s.add_argument("--new-identifier")
    s.add_argument("--source", required=True); s.add_argument("--url")
    s.add_argument("--raw")

    s = sec(sub.add_parser("note", help="record a qualitative observation"))
    s.add_argument("--text", required=True)
    s.add_argument("--refs", default="")
    s.add_argument("--source"); s.add_argument("--url")

    s = sec(sub.add_parser("decide", help="record a proposed verdict"))
    s.add_argument("--verdict", choices=VERDICTS, required=True)
    s.add_argument("--rationale", required=True)
    s.add_argument("--refs", required=True)

    s = sec(sub.add_parser("review", help="independent reviewer sign-off"))
    s.add_argument("--decision", required=True)
    s.add_argument("--outcome", choices=("approve", "reject"), required=True)
    s.add_argument("--findings", required=True)
    s.add_argument("--refs", default="")

    sec(sub.add_parser("verify", help="check chain, refs and raw files"))
    s = sec(sub.add_parser("list", help="list current entries"))
    s.add_argument("--type"); s.add_argument("--all", action="store_true")
    s = sec(sub.add_parser("get")); s.add_argument("id")
    s = sec(sub.add_parser("stale", help="flag facts older than thresholds"))
    s.add_argument("--max-price-age-days", type=int, default=3)
    s.add_argument("--max-fundamentals-age-days", type=int, default=120)
    s.add_argument("--today", help="YYYY-MM-DD (default: today)")
    sec(sub.add_parser("dossier", help="everything known, as JSON"))

    a = p.parse_args(argv)
    try:
        return _dispatch(a)
    except (LedgerError, MoneyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


def _csv(s: str) -> list[str]:
    return [x.strip() for x in (s or "").split(",") if x.strip()]


def _out(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def _dispatch(a) -> int:
    L = Ledger(a.root, a.security)

    if a.cmd == "init":
        if L.exists():
            raise LedgerError(f"{a.security} already exists; use a correction")
        from money import check_currency
        payload = {k: getattr(a, k) for k in (
            "name", "ticker", "exchange", "isin", "cusip", "figi", "cik",
            "sedol", "fiscal_year_end", "sector") if getattr(a, k)}
        payload["currency"] = check_currency(a.currency)
        payload["reporting_currency"] = check_currency(
            a.reporting_currency or a.currency)
        if not any(payload.get(k) for k in ("isin", "cusip", "figi", "cik")):
            print("WARNING: no ISIN/CUSIP/FIGI/CIK. Tickers are not unique and"
                  " change; add a stable identifier as soon as you find one.",
                  file=sys.stderr)
        _out(L.append("security", payload, a.actor))
        return 0

    if a.cmd == "raw":
        sha, dest = L.store_raw(a.file)
        _out(L.append("raw", {"sha256": sha, "path": str(dest.relative_to(L.dir)),
                              "source": a.source, "url": a.url,
                              "description": a.description,
                              "bytes": dest.stat().st_size}, a.actor))
        return 0

    if a.cmd == "fact":
        payload = number_payload(a.value, a.unit, a.scale)
        if payload["unit"] == "per_share":
            if not a.currency_of:
                raise LedgerError("per_share facts need --currency-of")
            from money import check_currency
            payload["currency"] = check_currency(a.currency_of)
        if a.source_tier != "primary" and not (a.url or a.raw):
            raise LedgerError("non-primary facts need --url or --raw")
        if a.raw:
            if L.get(a.raw)["type"] != "raw":
                raise LedgerError(f"{a.raw} is not a raw entry")
        if a.supersedes:
            old = L.get(a.supersedes)
            if old["type"] != "fact":
                raise LedgerError("a fact can only supersede a fact")
            if a.supersedes in L.superseded_ids():
                raise LedgerError(f"{a.supersedes} already superseded; "
                                  f"supersede {L.resolve(a.supersedes)['id']}")
            if not a.reason:
                raise LedgerError("corrections need --reason")
        payload.update({
            "metric": a.metric, "period": a.period,
            "period_end": parse_date(a.period_end, "period-end"),
            "as_of": parse_date(a.as_of, "as-of"),
            "source": a.source, "source_tier": a.source_tier, "url": a.url,
            "raw": a.raw, "locator": a.locator, "retrieved_at": now_utc(),
            "supersedes": a.supersedes, "reason": a.reason})
        _out(L.append("fact", {k: v for k, v in payload.items()
                               if v is not None}, a.actor))
        return 0

    if a.cmd == "assume":
        payload = number_payload(a.value, a.unit, "1")
        for k in ("low", "high"):
            if getattr(a, k) is not None:
                payload[k] = str(D(getattr(a, k)))
        if a.supersedes:
            if L.get(a.supersedes)["type"] != "assumption":
                raise LedgerError("an assumption can only supersede one")
            if not a.reason:
                raise LedgerError("corrections need --reason")
        refs = _csv(a.refs)
        for r in refs:
            L.get(r)
        payload.update({"metric": a.metric, "rationale": a.rationale,
                        "refs": refs, "supersedes": a.supersedes,
                        "reason": a.reason})
        _out(L.append("assumption", {k: v for k, v in payload.items()
                                     if v is not None}, a.actor))
        return 0

    if a.cmd == "ca":
        payload = {"action": a.action,
                   "ex_date": parse_date(a.ex_date, "ex-date"),
                   "record_date": parse_date(a.record_date, "record-date"),
                   "pay_date": parse_date(a.pay_date, "pay-date"),
                   "source": a.source, "url": a.url, "raw": a.raw,
                   "old_identifier": a.old_identifier,
                   "new_identifier": a.new_identifier}
        if a.action in ("split", "reverse_split", "stock_dividend"):
            if not a.ratio:
                raise LedgerError(f"{a.action} needs --ratio (new/old)")
            r = D(a.ratio)
            if r <= 0:
                raise LedgerError("ratio must be positive")
            payload["ratio"] = str(r)
        if a.action == "cash_dividend":
            if not (a.amount and a.currency):
                raise LedgerError("cash_dividend needs --amount and --currency")
            from money import check_currency
            payload["amount"] = str(D(a.amount))
            payload["currency"] = check_currency(a.currency)
        _out(L.append("corporate_action",
                      {k: v for k, v in payload.items() if v is not None},
                      a.actor))
        return 0

    if a.cmd == "note":
        refs = _csv(a.refs)
        for r in refs:
            L.get(r)
        if not refs and not a.url:
            raise LedgerError("a note needs --refs or --url (no unsourced claims)")
        _out(L.append("note", {"text": a.text, "refs": refs, "source": a.source,
                               "url": a.url}, a.actor))
        return 0

    if a.cmd == "decide":
        refs = _csv(a.refs)
        if not refs:
            raise LedgerError("a decision must cite evidence")
        for r in refs:
            L.get(r)
        problems = L.verify()
        if problems:
            raise LedgerError("ledger does not verify; fix first:\n  " +
                              "\n  ".join(problems))
        _out(L.append("decision", {"verdict": a.verdict, "rationale": a.rationale,
                                   "refs": refs, "status": "proposed"}, a.actor))
        return 0

    if a.cmd == "review":
        d = L.get(a.decision)
        if d["type"] != "decision":
            raise LedgerError(f"{a.decision} is not a decision")
        actor = a.actor or os.environ.get("VALUE_ANALYST_ACTOR", "analyst")
        if actor == d["actor"]:
            raise LedgerError("maker-checker: the reviewer must differ from the"
                              f" author of {a.decision} ({d['actor']})")
        refs = _csv(a.refs)
        for r in refs:
            L.get(r)
        _out(L.append("review", {"decision": a.decision, "outcome": a.outcome,
                                 "findings": a.findings, "refs": refs}, actor))
        return 0

    if a.cmd == "verify":
        problems = L.verify()
        _out({"security": L.key, "entries": len(L.entries),
              "ok": not problems, "problems": problems})
        return 0 if not problems else 1

    if a.cmd == "list":
        rows = L.entries if a.all else L.current(a.type)
        if a.all and a.type:
            rows = [e for e in rows if e["type"] == a.type]
        for e in rows:
            print(_summary(e))
        return 0

    if a.cmd == "get":
        _out(L.get(a.id))
        return 0

    if a.cmd == "stale":
        today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
        # History is meant to be old: judge only the newest observation of
        # each metric (per period kind: spot / FY / quarter-or-TTM).
        out, newest = [], {}
        for e in L.current("fact"):
            ref = e.get("as_of") or e.get("period_end")
            if not ref:
                out.append({"id": e["id"], "metric": e["metric"],
                            "issue": "no as_of/period_end: age unknown"})
                continue
            kind = ("spot" if e["period"] == "spot" else
                    "annual" if e["period"].startswith("FY") else "interim")
            k = (e["metric"], kind)
            if k not in newest or ref > newest[k][0]:
                newest[k] = (ref, e)
        for (metric, kind), (ref, e) in sorted(newest.items()):
            age = (today - dt.date.fromisoformat(ref)).days
            limit = (a.max_price_age_days if kind == "spot" or
                     metric.startswith("fx_") or metric in ("price", "market_cap")
                     else a.max_fundamentals_age_days + 365 if kind == "annual"
                     else a.max_fundamentals_age_days)
            if age > limit:
                out.append({"id": e["id"], "metric": metric,
                            "period": e["period"], "age_days": age,
                            "limit_days": limit})
        _out({"stale": out, "today": today.isoformat()})
        return 0 if not out else 1

    if a.cmd == "dossier":
        decisions = L.current("decision")
        reviews = {r["decision"]: r for r in L.current("review")}
        _out({"security": L.security(),
              "verification": L.verify(),
              "facts": L.current("fact"),
              "assumptions": L.current("assumption"),
              "corporate_actions": L.current("corporate_action"),
              "computations": L.current("computation"),
              "checks": L.current("check"),
              "notes": L.current("note"),
              "decisions": [{**d, "review": reviews.get(d["id"])}
                            for d in decisions],
              "superseded": sorted(L.superseded_ids())})
        return 0
    return 1


def _summary(e: dict) -> str:
    t = e["type"]
    if t == "fact":
        return (f"{e['id']}  {e['metric']:<24} {e['period']:<12} "
                f"{e['value']} {e['unit']}  [{e['source_tier']}: {e['source']}]")
    if t == "assumption":
        return f"{e['id']}  {e['metric']:<24} {e['value']} {e['unit']}  ({e['rationale'][:60]})"
    if t == "computation":
        return f"{e['id']}  {e['method']:<24} -> {json.dumps(e.get('outputs'))[:90]}"
    if t == "decision":
        return f"{e['id']}  {e['verdict']}  by {e['actor']}: {e['rationale'][:70]}"
    if t == "review":
        return f"{e['id']}  {e['outcome']} {e['decision']} by {e['actor']}"
    return f"{e['id']}  {t}"


if __name__ == "__main__":
    sys.exit(main())

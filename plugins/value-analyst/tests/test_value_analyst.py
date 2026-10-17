"""Tests for the value-analyst scripts. Standard library only.

    python3 -m unittest discover -s tests -v

Follows the handbook's testing menu (paraphrased): property tests for money
math, invariants checked after every step, golden values for valuations,
round-trips across the JSON boundary, and tamper tests for the audit trail.
"""
import io
import json
import os
import random
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import money  # noqa: E402
from money import D, Money, FxRate, MoneyError, allocate  # noqa: E402
import ledger as ledger_mod  # noqa: E402
from ledger import Ledger, LedgerError  # noqa: E402
import valuation  # noqa: E402
import reconcile  # noqa: E402
import corpactions  # noqa: E402
import forensics  # noqa: E402

RNG = random.Random(20261018)


def run(mod, *args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = mod.main(list(args))
    return code, out.getvalue(), err.getvalue()


def rand_amount():
    return Decimal(RNG.randint(-10**12, 10**12)) / Decimal(10) ** RNG.randint(0, 6)


class MoneyProperties(unittest.TestCase):
    def test_floats_refused(self):
        with self.assertRaises(MoneyError):
            D(0.1)

    def test_json_round_trip_is_lossless(self):
        for _ in range(500):
            m = Money(rand_amount(), RNG.choice(list(money.CURRENCIES)))
            back = json.loads(json.dumps(m.to_json()))
            self.assertEqual(Money(back["amount"], back["currency"]), m)

    def test_cross_currency_arithmetic_refused(self):
        with self.assertRaises(MoneyError):
            Money("1", "USD") + Money("1", "EUR")

    def test_unknown_currency_refused(self):
        with self.assertRaises(MoneyError):
            Money("1", "XYZ")

    def test_allocation_never_mints_or_loses(self):
        for _ in range(500):
            total = Money(rand_amount(), RNG.choice(["USD", "JPY", "KWD"]))
            weights = [str(RNG.randint(1, 100)) for _ in range(RNG.randint(1, 7))]
            parts, residual = allocate(total, weights)
            self.assertEqual(sum((p.amount for p in parts), residual.amount),
                             total.amount)

    def test_rounding_respects_minor_units(self):
        self.assertEqual(str(Money("1.005", "USD").rounded().amount), "1.00")  # half-even
        self.assertEqual(str(Money("1.015", "USD").rounded().amount), "1.02")
        self.assertEqual(str(Money("1234.5", "JPY").rounded().amount), "1234")
        self.assertEqual(str(Money("1.23456", "KWD").rounded().amount), "1.235")

    def test_fx_is_directional(self):
        r = FxRate("EUR", "USD", "1.10", "2026-10-16", "ECB")
        self.assertEqual(r.convert(Money("100", "EUR")), Money("110.00", "USD"))
        with self.assertRaises(MoneyError):
            r.convert(Money("100", "USD"))


class LedgerFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.key = "TEST-ACME"
        self.L(["init", "--name", "Acme", "--ticker", "ACME", "--exchange", "TEST",
                "--currency", "USD", "--isin", "US0000000001"])

    def tearDown(self):
        self.tmp.cleanup()

    def L(self, args, actor=None, expect=0):
        base = ["--root", str(self.root)] + (["--actor", actor] if actor else [])
        cmd, rest = args[0], args[1:]
        code, out, err = run(ledger_mod, *base, cmd, "-s", self.key, *rest)
        self.assertEqual(code, expect, err)
        return json.loads(out) if out.strip().startswith("{") else out

    def fact(self, metric, value, unit="USD", period="FY2025", **kw):
        args = ["fact", "--metric", metric, "--value", value, "--unit", unit,
                "--period", period, "--source", kw.pop("source", "10-K 2025"),
                "--source-tier", kw.pop("tier", "primary")]
        for k, v in kw.items():
            args += [f"--{k.replace('_', '-')}", v]
        return self.L(args)["id"]

    def assume(self, metric, value, unit="pct"):
        return self.L(["assume", "--metric", metric, "--value", value, "--unit", unit,
                       "--rationale", "test"])["id"]

    def ledger(self):
        return Ledger(self.root, self.key)


class LedgerTests(LedgerFixture):
    def test_chain_verifies_after_every_append(self):
        for i in range(20):
            self.fact(f"m{i}", str(RNG.randint(1, 10**9)))
            self.assertEqual(self.ledger().verify(), [], f"after append {i}")

    def test_tampering_is_detected(self):
        self.fact("revenue", "1000")
        p = self.root / self.key / "ledger.jsonl"
        lines = p.read_text().splitlines()
        lines[-1] = lines[-1].replace('"1000"', '"9999"')
        p.write_text("\n".join(lines) + "\n")
        self.assertTrue(any("hash mismatch" in x for x in self.ledger().verify()))

    def test_correction_supersedes_without_editing(self):
        old = self.fact("revenue", "1000")
        before = (self.root / self.key / "ledger.jsonl").read_text()
        new = self.L(["fact", "--metric", "revenue", "--value", "1010", "--unit", "USD",
                      "--period", "FY2025", "--source", "10-K/A 2025",
                      "--source-tier", "primary", "--supersedes", old,
                      "--reason", "restated"])["id"]
        after = (self.root / self.key / "ledger.jsonl").read_text()
        self.assertTrue(after.startswith(before), "history must be untouched")
        self.assertEqual(self.ledger().best_fact("revenue", "FY2025")["id"], new)

    def test_secondary_fact_needs_a_trail(self):
        self.L(["fact", "--metric", "revenue", "--value", "1", "--unit", "USD",
                "--period", "FY2025", "--source", "vendor", "--source-tier",
                "secondary"], expect=2)

    def test_maker_checker(self):
        f = self.fact("revenue", "1000")
        d = self.L(["decide", "--verdict", "WATCHLIST", "--rationale", "x",
                    "--refs", f], actor="analyst")["id"]
        self.L(["review", "--decision", d, "--outcome", "approve",
                "--findings", "self-approval"], actor="analyst", expect=2)
        self.L(["review", "--decision", d, "--outcome", "approve",
                "--findings", "independent check"], actor="checker")

    def test_staleness_judges_only_the_newest_observation(self):
        self.fact("revenue", "900", period="FY2023", period_end="2023-12-31")
        self.fact("revenue", "1000", period="FY2025", period_end="2025-12-31")
        self.fact("price", "10", "USD", period="spot", as_of="2026-10-10")
        code, out, _ = run(ledger_mod, "--root", str(self.root), "stale", "-s",
                           self.key, "--today", "2026-10-18")
        stale = json.loads(out)["stale"]
        self.assertEqual([s["metric"] for s in stale], ["price"])

    def test_raw_payload_is_stored_by_hash(self):
        src = self.root / "payload.json"
        src.write_text('{"Revenues": 1000}')
        r = self.L(["raw", str(src), "--source", "EDGAR companyfacts"])
        self.assertTrue((self.root / self.key / r["path"]).exists())
        self.assertEqual(self.ledger().verify(), [])


class ValuationTests(LedgerFixture):
    def dcf_inputs(self, r="10"):
        return dict(fcf0=self.fact("fcf", "100"), growth=self.assume("g", "10"),
                    years=self.assume("years", "2", "years"),
                    tg=self.assume("tg", "2"), r=self.assume("r", r),
                    shares=self.fact("shares_diluted", "10", "shares"),
                    nd=self.fact("net_debt", "0"))

    def dcf(self, i):
        return run(valuation, "--root", str(self.root), "dcf", "-s", self.key,
                   "--fcf0", i["fcf0"], "--growth", i["growth"], "--years", i["years"],
                   "--terminal-growth", i["tg"], "--discount-rate", i["r"],
                   "--shares", i["shares"], "--net-debt", i["nd"])

    def test_dcf_golden_value(self):
        # FCF 110 and 121 each discount to 100; TV = 121*1.02/0.08 = 1542.75,
        # PV(TV) = 1275; EV = 1475; per share = 147.5
        code, out, err = self.dcf(self.dcf_inputs())
        self.assertEqual(code, 0, err)
        o = json.loads(out)["outputs"]
        self.assertEqual(D(o["value_per_share"]), Decimal("147.5"))

    def test_dcf_value_falls_as_discount_rate_rises(self):
        prev = None
        for r in ("8", "9", "10", "12", "15"):
            code, out, err = self.dcf(self.dcf_inputs(r))
            v = D(json.loads(out)["outputs"]["value_per_share"])
            if prev is not None:
                self.assertLess(v, prev)
            prev = v

    def test_reverse_dcf_recovers_growth(self):
        i = self.dcf_inputs()
        price = self.fact("price", "147.5", "USD", period="spot", as_of="2026-10-16")
        code, out, err = run(valuation, "--root", str(self.root), "reverse-dcf", "-s",
                             self.key, "--fcf0", i["fcf0"], "--years", i["years"],
                             "--terminal-growth", i["tg"], "--discount-rate", i["r"],
                             "--shares", i["shares"], "--net-debt", i["nd"],
                             "--price", price)
        self.assertEqual(code, 0, err)
        g = D(json.loads(out)["outputs"]["implied_growth"])
        self.assertLess(abs(g - Decimal("0.10")), Decimal("1e-6"))

    def test_superseded_inputs_are_refused(self):
        i = self.dcf_inputs()
        self.L(["fact", "--metric", "fcf", "--value", "90", "--unit", "USD",
                "--period", "FY2025", "--source", "10-K/A", "--source-tier",
                "primary", "--supersedes", i["fcf0"], "--reason", "restated"])
        code, _, err = self.dcf(i)
        self.assertEqual(code, 2)
        self.assertIn("superseded", err)

    def test_currency_mismatch_requires_fx(self):
        i = self.dcf_inputs()
        i["nd"] = self.fact("net_debt", "5", "EUR", period="FY2025b")
        code, _, err = self.dcf(i)
        self.assertEqual(code, 2)

    def test_margin_of_safety(self):
        code, out, _ = self.dcf(self.dcf_inputs())
        c = json.loads(out)["id"]
        price = self.fact("price", "100", "USD", period="spot", as_of="2026-10-16")
        code, out, err = run(valuation, "--root", str(self.root), "mos", "-s", self.key,
                             "--value", c, "--price", price, "--required-pct", "30")
        o = json.loads(out)["outputs"]
        self.assertTrue(o["passes"])
        self.assertEqual(D(o["buy_below"]), Decimal("103.25"))


class ReconcileTests(LedgerFixture):
    def test_scale_mismatch_is_classified(self):
        self.fact("revenue", "1000000000")
        self.fact("revenue", "1000000", source="Vendor", tier="secondary",
                  url="https://example.com")
        code, out, _ = run(reconcile, "--root", str(self.root), "sources", "-s", self.key)
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out)["unresolved"][0]["status"], "SCALE_MISMATCH")

    def test_balance_sheet_identity(self):
        self.fact("total_assets", "100")
        self.fact("total_liabilities", "60")
        self.fact("equity", "30")
        code, out, _ = run(reconcile, "--root", str(self.root), "identities", "-s",
                           self.key, "--period", "FY2025")
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out)["unresolved"][0]["status"], "IDENTITY_BREAK")


class CorporateActionTests(LedgerFixture):
    def test_split_restates_history(self):
        self.fact("eps_diluted", "4", "per_share", period="FY2023",
                  period_end="2023-12-31", currency_of="USD")
        self.fact("eps_diluted", "2.2", "per_share", period="FY2025",
                  period_end="2025-12-31", currency_of="USD")
        self.L(["ca", "--action", "split", "--ex-date", "2024-06-10",
                "--ratio", "2", "--source", "8-K"])
        code, out, err = run(corpactions, "--root", str(self.root), "adjust",
                             "-s", self.key, "--metric", "eps_diluted")
        series = json.loads(out)["outputs"]["series"]
        self.assertEqual(D(series[0]["adjusted"]), Decimal("2"))
        self.assertEqual(D(series[1]["adjusted"]), Decimal("2.2"))


class ForensicsTests(LedgerFixture):
    def test_missing_inputs_are_reported_not_guessed(self):
        self.fact("net_income", "10")
        self.fact("total_assets", "100")
        code, out, _ = run(forensics, "--root", str(self.root), "piotroski", "-s",
                           self.key, "--year", "FY2025", "--prior", "FY2024")
        o = json.loads(out)
        self.assertEqual(o["outputs"]["signals"]["1_roa_positive"], 1)
        self.assertIn("unavailable", str(o["outputs"]["signals"]["2_cfo_positive"]))
        self.assertNotIn("reading", o["outputs"])


class HookTests(unittest.TestCase):
    def hook(self, script, payload):
        p = subprocess.run([sys.executable, str(SCRIPTS / script)],
                           input=json.dumps(payload), capture_output=True, text=True)
        return p.returncode, p.stderr

    def test_guard_blocks_direct_ledger_edits(self):
        code, _ = self.hook("guard_ledger.py", {"tool_name": "Edit", "tool_input": {
            "file_path": "/p/research/ACME/ledger.jsonl"}})
        self.assertEqual(code, 2)
        code, _ = self.hook("guard_ledger.py", {"tool_name": "Bash", "tool_input": {
            "command": "sed -i 's/1000/9999/' research/ACME/ledger.jsonl"}})
        self.assertEqual(code, 2)
        code, _ = self.hook("guard_ledger.py", {"tool_name": "Bash", "tool_input": {
            "command": "python3 scripts/ledger.py fact -s ACME --metric x"}})
        self.assertEqual(code, 0)

    def test_lint_flags_untraced_numbers(self):
        with tempfile.TemporaryDirectory() as d:
            k = Path(d) / "research" / "ACME"
            k.mkdir(parents=True)
            (k / "ledger.jsonl").write_text(json.dumps({"id": "F-0001"}) + "\n")
            rep = k / "report.md"
            rep.write_text("# FY2025 review\n\nRevenue was $1,000m [F-0001].\n"
                           "Margins expanded to 23.5%.\nCites [F-0099] at 2.1x.\n")
            code, err = self.hook("lint_report.py", {"tool_name": "Write",
                                  "tool_input": {"file_path": str(rep)}})
            self.assertEqual(code, 2)
            self.assertIn("line 4", err)
            self.assertIn("F-0099", err)
            self.assertNotIn("line 3", err)


class PortfolioTests(LedgerFixture):
    def test_wash_sale_flag_across_accounts(self):
        import portfolio
        self.fact("price", "50", "USD", period="spot", as_of="2026-10-16")
        csv = self.root / "lots.csv"
        csv.write_text(
            "owner,account,account_type,lot_id,security_key,isin,quantity,cost_basis,currency,acquired,status\n"
            f"me,BROK-1,taxable,L1,{self.key},US0000000001,100,8000,USD,2024-01-02,settled\n"
            f"me,IRA-1,ira,L2,{self.key},US0000000001,10,500,USD,2026-10-01,settled\n")
        code, out, err = run(portfolio, "--root", str(self.root), "--lots", str(csv),
                             "--today", "2026-10-17", "--plan-sell", f"{self.key}:100")
        plan = json.loads(out)["sell_plans"][0]
        self.assertTrue(any("WASH SALE" in f for f in plan["flags"]), plan)


if __name__ == "__main__":
    unittest.main()

"""Tests for the money-lint hook. Run: python3 -m unittest discover -s tests"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "money_lint.py"


def run(tool, path, **ti):
    payload = {"tool_name": tool, "tool_input": {"file_path": path, **ti}}
    p = subprocess.run([sys.executable, str(SCRIPT)], input=json.dumps(payload),
                       capture_output=True, text=True)
    return p.returncode, p.stderr


class Flags(unittest.TestCase):
    def assertFlags(self, path, line):
        code, err = run("Write", path, content=line)
        self.assertEqual(code, 2, f"expected a finding for {line!r}")
        self.assertIn("money-lint", err)

    def test_csharp(self):
        self.assertFlags("Fees.cs", "public double TransferFee { get; init; }")
        self.assertFlags("Fees.cs", "double amount = 10.5;")
        self.assertFlags("Fees.cs", "public float? Balance;")

    def test_java_kotlin(self):
        self.assertFlags("Fees.java", "private double totalAmount;")
        self.assertFlags("Fees.kt", "val price: Double = 0.0")

    def test_python(self):
        self.assertFlags("fees.py", "def transfer(amount: float) -> None:")
        self.assertFlags("fees.py", "def monthly_payment(p, r, n) -> float:")
        self.assertFlags("fees.py", "price = float(row['price'])")

    def test_typescript_go(self):
        self.assertFlags("fees.ts", "  feeAmount?: number;")
        self.assertFlags("fees.go", "\tBalance float64")


class Passes(unittest.TestCase):
    def assertClean(self, path, text, tool="Write", **extra):
        ti = {"content": text} if tool == "Write" else extra
        code, err = run(tool, path, **ti)
        self.assertEqual(code, 0, err)

    def test_decimal_types(self):
        self.assertClean("Fees.cs", "public decimal TransferFee { get; init; }")
        self.assertClean("fees.py", "def transfer(amount: Decimal) -> Decimal:")
        self.assertClean("Fees.java", "private BigDecimal totalAmount;")
        self.assertClean("fees.ts", "amount: string; // minor units as string")

    def test_non_money_floats(self):
        self.assertClean("Stats.cs", "double latencyMs = 3.2;")
        self.assertClean("ml.py", "learning_rate: float = 0.01")

    def test_ignore_comment(self):
        self.assertClean("Fees.cs", "double priceElasticity; // money-lint: ignore")

    def test_other_files(self):
        self.assertClean("README.md", "double amount")

    def test_edit_checks_only_new_text(self):
        self.assertClean("Fees.cs", None, tool="Edit",
                         old_string="double amount;", new_string="decimal amount;")

    def test_edit_flags_new_float(self):
        code, _ = run("Edit", "Fees.cs", old_string="decimal fee;",
                      new_string="double fee;")
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()

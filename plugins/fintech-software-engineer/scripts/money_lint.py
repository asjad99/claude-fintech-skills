#!/usr/bin/env python3
"""PostToolUse hook: flag binary floating point used for money.

Checks only the text Claude just wrote (Write content, Edit/MultiEdit new
strings), so legacy code elsewhere in a file is not re-flagged on every edit.
A finding is a float-like type on a money-like name, for example
`double amount`, `price: float`, `fee: number`, `Balance float64`.

Exit 2 sends the findings back to Claude to fix; exit 0 otherwise.
Silence a deliberate case with a `money-lint: ignore` comment on the line.

Rule source: Fintech Engineering Handbook, Representing Money (decimal or
integer minor units, never binary floating point).
"""
import json
import re
import sys
from pathlib import Path

MONEY = (r"\w*(?:amount|price|balance|fee|cost|total|principal|interest|"
         r"payment|payout|refund|cash|money|salary|wage|tax|premium|"
         r"discount|charge|credit|debit|fx_?rate|exchange_?rate)\w*")
FLOAT_C = r"(?:double|float|Double|Float)"

PATTERNS = {
    ".cs": [rf"\b{FLOAT_C}\??\s+(?i:{MONEY})\b"],
    ".java": [rf"\b{FLOAT_C}\s+(?i:{MONEY})\b"],
    ".kt": [rf"\b(?i:{MONEY})\s*:\s*(?:Double|Float)\b"],
    ".py": [rf"\b(?i:{MONEY})\s*:\s*(?:Optional\[)?float\b",
            rf"\bdef\s+(?i:{MONEY})\s*\([^)]*\)\s*->\s*float\b",
            rf"\b(?i:{MONEY})\s*=\s*float\("],
    ".ts": [rf"\b(?i:{MONEY})\??\s*:\s*number\b"],
    ".tsx": [rf"\b(?i:{MONEY})\??\s*:\s*number\b"],
    ".go": [rf"\b(?i:{MONEY})\s+(?:\[\])?float(?:32|64)\b"],
}
PATTERNS[".js"] = []          # untyped: nothing reliable to check
IGNORE = re.compile(r"money-lint:\s*ignore", re.I)


def written_text(tool: str, ti: dict) -> str:
    if tool == "Write":
        return ti.get("content", "")
    if tool == "Edit":
        return ti.get("new_string", "")
    if tool == "MultiEdit":
        return "\n".join(e.get("new_string", "") for e in ti.get("edits", []))
    return ""


def lint(text: str, suffix: str) -> list[str]:
    pats = [re.compile(p) for p in PATTERNS.get(suffix, [])]
    found = []
    for line in text.splitlines():
        if IGNORE.search(line):
            continue
        if any(p.search(line) for p in pats):
            found.append(line.strip()[:120])
    return found


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)
    tool = data.get("tool_name", "")
    ti = data.get("tool_input") or {}
    path = ti.get("file_path", "")
    suffix = Path(path).suffix.lower()
    if suffix not in PATTERNS:
        sys.exit(0)
    findings = lint(written_text(tool, ti), suffix)
    if not findings:
        sys.exit(0)
    print(f"money-lint: binary floating point used for money in {path}:\n  " +
          "\n  ".join(findings[:15]) +
          "\nUse a decimal type (decimal / Decimal / BigDecimal / a decimal "
          "library) or integer minor units, paired with a currency. If this is "
          "not money, add a 'money-lint: ignore' comment on the line.",
          file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()

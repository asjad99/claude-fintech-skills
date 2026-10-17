#!/usr/bin/env python3
"""Provenance linter for research reports. "No invented data" in practice.

Run as a PostToolUse hook (reads the hook JSON on stdin) or directly:
    lint_report.py path/to/research/KEY/report.md

Rule: every line in the report that states a number (money, percentage,
multiple, decimal, or a figure with thousands separators) must cite at least
one ledger entry, e.g. "[F-0012]" or "[C-0003, A-0002]". Every cited id must
exist in the ledger beside the report and must not have been superseded.
Dates, fiscal-period labels, years and section numbers are ignored.

Exit 2 (feedback to Claude) when a problem is found; 0 otherwise.
"""
import json
import re
import sys
from pathlib import Path

TAG = re.compile(r"\[((?:[A-Z]{1,2}-\d{4})(?:\s*,\s*[A-Z]{1,2}-\d{4})*)\]")
ID = re.compile(r"[A-Z]{1,2}-\d{4}")
IGNORE = [
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),             # ISO dates
    re.compile(r"\b(FY|CY|H[12]|Q[1-4])[- ]?\d{2,4}\b", re.I),
    re.compile(r"\bTTM-\d{4}Q[1-4]\b"),
    re.compile(r"\b(19|20)\d{2}\b"),                  # bare years
    re.compile(r"^\s*\d+[.)]\s"),                     # list numbering
    re.compile(r"\b[A-Z]{2}[A-Z0-9]{9}\d\b"),         # ISINs
]
NUMERIC = re.compile(
    r"[$€£¥]\s?-?\d|"
    r"-?\d+(?:\.\d+)?\s?%|"
    r"\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b|"
    r"\b\d+\.\d+x?\b|\b\d+x\b|"
    r"\b\d+(?:\.\d+)?\s?(?:bn|mn|m|k|million|billion|trillion|USD|EUR|GBP|AUD|JPY|CAD|CHF)\b",
    re.I)
REPORT = re.compile(r"(report|thesis|memo|review|dossier)[^/\\]*\.md$", re.I)


def load_ledger(path: Path):
    entries = []
    for line in path.read_text().splitlines():
        if line.strip():
            entries.append(json.loads(line))
    ids = {e["id"] for e in entries}
    superseded = {e["supersedes"] for e in entries if e.get("supersedes")}
    return ids, superseded


def lint(report: Path) -> list[str]:
    ledger = report.parent / "ledger.jsonl"
    if not ledger.exists():
        return [f"{report.name}: no ledger.jsonl beside the report, so none of "
                "its numbers can be traced. Save reports in research/<KEY>/."]
    ids, superseded = load_ledger(ledger)
    problems, in_code = [], False
    for n, raw in enumerate(report.read_text().splitlines(), 1):
        if raw.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code or raw.lstrip().startswith("#") or raw.strip().startswith("<!--"):
            continue
        cited = [i for t in TAG.findall(raw) for i in ID.findall(t)]
        text = TAG.sub("", raw)
        for pat in IGNORE:
            text = pat.sub("", text)
        if re.fullmatch(r"\s*\|?[\s|:-]*\|?\s*", text):   # table separator row
            continue
        if NUMERIC.search(text) and not cited:
            snippet = raw.strip()[:90]
            problems.append(f"line {n}: number with no evidence tag: {snippet}")
        for i in cited:
            if i not in ids:
                problems.append(f"line {n}: cites {i}, which is not in the ledger")
            elif i in superseded:
                problems.append(f"line {n}: cites {i}, which has been superseded")
    return problems


def main():
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        hook = False
    else:
        try:
            data = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)
        path = Path((data.get("tool_input") or {}).get("file_path", ""))
        hook = True
        # Only reports that live beside a ledger (research/<KEY>/report.md).
        if not REPORT.search(str(path)) or not (path.parent / "ledger.jsonl").exists():
            sys.exit(0)
    if not path.exists():
        sys.exit(0)
    problems = lint(path)
    if not problems:
        if not hook:
            print(f"{path}: provenance OK")
        sys.exit(0)
    shown = problems[:25]
    more = len(problems) - len(shown)
    print("value-analyst provenance check failed for " + str(path) + ":\n  " +
          "\n  ".join(shown) + (f"\n  ...and {more} more" if more else "") +
          "\nCite the ledger id for each figure, record missing facts with "
          "ledger.py, or remove the number. Never write a figure you cannot "
          "trace.", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()

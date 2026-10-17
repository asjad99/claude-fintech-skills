#!/usr/bin/env python3
"""PreToolUse hook: keep the evidence ledger append-only.

Blocks (exit 2) any Write/Edit/MultiEdit/NotebookEdit aimed at a ledger.jsonl
file or at anything inside a research raw/ folder, and any Bash command that
would redirect into, edit in place, move, truncate or delete them. The only
sanctioned write path is scripts/ledger.py (and the calculators that call it).

Handbook basis (paraphrased): there must be no UPDATE or DELETE path for audit
records; corrections are new, compensating entries.
"""
import json
import os
import re
import sys

LEDGER = re.compile(r"ledger\.jsonl")
RAW = re.compile(r"(^|[/\\])raw[/\\]")
SAFE_SCRIPTS = re.compile(
    r"(ledger|valuation|forensics|reconcile|corpactions|portfolio)\.py")
MUTATING = re.compile(
    r"(>{1,2}\s*\S*(ledger\.jsonl|raw/))|"
    r"\b(rm|mv|cp|truncate|shred|chmod|tee|dd|install|unlink|ln)\b[^|;&]*(ledger\.jsonl|raw/)|"
    r"\b(sed|perl|awk|ruby)\b[^|;&]*-i[^|;&]*(ledger\.jsonl|raw/)|"
    r"(open|write_text|write_bytes)\([^)]*ledger\.jsonl")


def block(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(2)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)
    tool = data.get("tool_name", "")
    ti = data.get("tool_input") or {}
    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        path = ti.get("file_path") or ti.get("notebook_path") or ""
        research = os.environ.get("CLAUDE_PLUGIN_OPTION_RESEARCH_DIR", "research")
        if LEDGER.search(path) or (RAW.search(path) and research in path):
            block("value-analyst: the evidence ledger and raw/ payloads are "
                  "append-only. Use scripts/ledger.py (fact/assume/raw/note), "
                  "and record corrections with --supersedes and --reason "
                  "instead of editing.")
    elif tool == "Bash":
        cmd = ti.get("command", "")
        if MUTATING.search(SAFE_SCRIPTS.sub("", cmd)):
            block("value-analyst: this command would modify the evidence "
                      "ledger or a raw payload directly. Append through "
                      "scripts/ledger.py; corrections use --supersedes.")
    sys.exit(0)


if __name__ == "__main__":
    main()

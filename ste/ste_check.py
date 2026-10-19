#!/usr/bin/env python3
"""Check SKILL.md files against the measurable ASD-STE100 writing rules.

Usage: python3 ste/ste_check.py [files...]   (default: all SKILL.md files)

The script does not check word meanings against the STE dictionary (that
dictionary is licensed). It checks: sentence length, -ing words, contractions,
phrasal verbs, words on the project "do not use" list, possible passive voice
and paragraph length. Frontmatter, code, inline code, tables of file paths and
the "Sources:" paragraph are not checked.
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GLOSSARY = os.path.join(HERE, "glossary.md")

PROCEDURE_MAX = 20
DESCRIPTIVE_MAX = 25
PARAGRAPH_MAX = 6

CONTRACTION = re.compile(r"\b\w+(n't|'re|'ll|'ve|'d|'m)\b", re.I)
PASSIVE = re.compile(r"\b(is|are|was|were|be|been|being|gets?)\s+(\w+ed|shown|written|done|seen|given|known|taken|made|run|built|kept|found|set|held|told|sent|split)\b", re.I)
PHRASAL = [
    "set up", "find out", "push back", "come in", "pick up", "carry out",
    "look up", "point out", "turn into", "leave out", "back up", "roll back",
    "sort out", "take on", "hand over", "fill in", "go lighter", "falls in",
    "goes red", "go red", "come from", "comes from", "stand in", "lead there",
    "lands in", "back to",
]
NOT_ING = {
    "thing", "things", "something", "nothing", "anything", "everything",
    "string", "strings", "during", "bring", "spring", "king", "ring", "sing",
}


def load_glossary():
    """Return (allowed words, words not to use) from glossary.md."""
    allowed, banned = set(), set()
    section = None
    if not os.path.exists(GLOSSARY):
        return allowed, banned
    for line in open(GLOSSARY, encoding="utf-8"):
        if line.startswith("## "):
            section = line[3:].strip().lower()
            continue
        m = re.match(r"\|\s*`?([^|`]+?)`?\s*\|", line)
        if not m or set(m.group(1)) <= set("-: "):
            continue
        term = m.group(1).strip().lower()
        if term in ("term", "word", "do not use", "verb"):
            continue
        if section and section.startswith("words not to use"):
            for t in term.split(","):
                banned.add(t.strip())
        else:
            for w in re.findall(r"[a-z][a-z-]*", term):
                allowed.add(w)
    return allowed, banned


def strip(text):
    """Blank out the parts that are not checked. Line numbers stay the same."""
    keep = lambda m: "\n" * m.group(0).count("\n")
    text = re.sub(r"\A---\n.*?\n---\n", keep, text, flags=re.S)
    text = re.sub(r"```.*?```", keep, text, flags=re.S)
    text = re.sub(r"(?m)^\s*Sources:.*?(?=\n\s*\n|\Z)", keep, text, flags=re.S)
    text = re.sub(r"`[^`]*`", "CODE", text)
    text = re.sub(r'"[^"\n]*"|\u201c[^\u201d\n]*\u201d', "QUOTE", text)
    return text


def units(text):
    """Yield (line number, kind, text) for each paragraph, list item or cell."""
    lines = text.split("\n")
    buf, start, kind = [], 0, "descriptive"

    def flush():
        if buf:
            yield start, kind, " ".join(s.strip() for s in buf)

    for i, line in enumerate(lines, 1):
        s = line.strip()
        item = re.match(r"^(\d+\.|[-*])\s+", s)
        if not s or s.startswith("#") or s.startswith("|") or item:
            yield from flush()
            buf = []
            if s.startswith("|"):
                cells = [c.strip() for c in s.strip("|").split("|")]
                for c in cells:
                    if c and not set(c) <= set("-: "):
                        yield i, "cell", c
                continue
            if item:
                buf, start, kind = [s[item.end():]], i, "procedure"
            continue
        if not buf:
            start, kind = i, "descriptive"
        buf.append(s)
    yield from flush()


def sentences(text):
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\(for example[^)]*\)", "(example)", text)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z*\"(])|(?<=:)\s+(?=[A-Z])", text)
    return [p.strip() for p in parts if p.strip()]


def check(path, allowed, banned):
    findings = []
    raw = open(path, encoding="utf-8").read()
    # keep line numbers: blank out the parts we skip instead of deleting them
    for line, kind, unit in units(strip(raw)):
        sents = sentences(unit)
        if kind == "descriptive" and len(sents) > PARAGRAPH_MAX:
            findings.append((line, "paragraph", f"{len(sents)} sentences (max {PARAGRAPH_MAX})"))
        limit = DESCRIPTIVE_MAX if kind == "descriptive" else PROCEDURE_MAX
        for s in sents:
            words = re.findall(r"[A-Za-z0-9][\w'/-]*", s)
            if len(words) > limit:
                findings.append((line, "length", f"{len(words)} words (max {limit}): {s[:70]}..."))
            low = s.lower()
            for w in re.findall(r"\b[a-z]+ing\b", low):
                if w not in NOT_ING and w not in allowed:
                    findings.append((line, "-ing", w))
            for m in CONTRACTION.finditer(s):
                findings.append((line, "contraction", m.group(0)))
            for p in PHRASAL:
                if re.search(r"\b" + re.escape(p) + r"\b", low):
                    findings.append((line, "phrasal", p))
            for b in banned:
                if b and re.search(r"\b" + re.escape(b) + r"\b", low):
                    findings.append((line, "word", b))
            for m in PASSIVE.finditer(s):
                findings.append((line, "passive?", m.group(0)))
    return findings


def main():
    files = sys.argv[1:] or sorted(glob.glob(os.path.join(
        ROOT, "plugins", "*", "skills", "*", "SKILL.md")))
    allowed, banned = load_glossary()
    total = 0
    for f in files:
        found = check(f, allowed, banned)
        hard = [x for x in found if x[1] != "passive?"]
        total += len(hard)
        print(f"{os.path.relpath(f, ROOT)}: {len(hard)} findings, "
              f"{len(found) - len(hard)} passive warnings")
        for line, rule, msg in found:
            print(f"  {line:>4}  {rule:<11} {msg}")
    print(f"TOTAL {total}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())

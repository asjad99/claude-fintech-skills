#!/usr/bin/env python3
"""Build each STE SKILL.md from ste/new/<skill>.md and the original file.

The frontmatter, the code blocks (@@CODE1@@, @@CODE2@@ ...) and the
"Sources:" paragraph (@@SOURCES@@) come from ste/originals/ byte for byte.
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.join(os.path.dirname(HERE), "plugins", "fintech-software-engineer", "skills")
names = sys.argv[1:] or sorted(n[:-3] for n in os.listdir(os.path.join(HERE, "new")))
for n in names:
    orig = open(os.path.join(HERE, "originals", n, "SKILL.md"), encoding="utf-8").read()
    body = open(os.path.join(HERE, "new", n + ".md"), encoding="utf-8").read()
    fm = re.match(r"\A---\n.*?\n---\n", orig, re.S).group(0)
    codes = re.findall(r"```.*?```", orig, re.S)
    m = re.search(r"(?m)^Sources:.*\Z", orig, re.S)
    src = m.group(0) if m else ""
    for i, c in enumerate(codes, 1):
        body = body.replace(f"@@CODE{i}@@", c)
    body = body.replace("@@SOURCES@@", src.rstrip("\n"))
    assert "@@" not in body, f"{n}: placeholder left"
    out = fm + "\n" + body.strip("\n") + "\n"
    open(os.path.join(SKILLS, n, "SKILL.md"), "w", encoding="utf-8").write(out)
    print("wrote", n)

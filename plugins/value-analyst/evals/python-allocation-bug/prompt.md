---
description: Money bug. Expect a failing regression test first, root cause named, Decimal with residual handling.
tags: [python, debug]
max_turns: 30
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, TodoWrite]
---

Our dividend report is off by a cent: allocate(100.00, [1, 1, 1]) in allocate.py adds up to 99.99 instead of 100.00. Please fix it. You can't run Python here, so reason it through and update the code and tests.

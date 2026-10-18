---
description: Review a job that writes warehouse figures into live balances. Expect write-back to the system of record and silently skipped rows found.
tags: [python, review, ledger, data-layer]
max_turns: 30
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite]
---

Please review my change to jobs.py against main. Finance says the app's balances sometimes differ from their reports, so this syncs them every night.

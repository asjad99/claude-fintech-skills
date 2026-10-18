---
description: Duplicate webhook delivery credits twice. Expect dedupe on event id and a replay test.
tags: [python, payments, debug]
max_turns: 30
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, TodoWrite]
---

Customers are sometimes credited twice for one card payment. Our provider retries a webhook when we don't respond within 10 seconds. Please fix handle_event in webhooks.py. You can't run Python here, so reason it through and update the code and tests.

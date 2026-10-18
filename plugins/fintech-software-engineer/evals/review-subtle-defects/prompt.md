---
description: Review a payment change with subtle defects. Expect retry-without-idempotency and float-to-cents found.
tags: [python, review, payments]
max_turns: 30
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite]
---

Please review my latest change to payments.py against main before I merge it. It adds retries so charges don't fail on provider timeouts.

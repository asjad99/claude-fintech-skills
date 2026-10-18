---
description: New lending calculation. Expect Decimal, per-loan day-count convention, one accrual per loan-day.
tags: [python, lending, build]
max_turns: 30
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, TodoWrite]
---

Add daily interest accrual to our Python loan service: write accrue_interest(loan, accrual_date) that posts that day's interest for a loan. Loans have a principal and an annual interest rate. Put the code in lending/accrual.py with pytest tests in tests/. You can't run Python here, so just write the files.

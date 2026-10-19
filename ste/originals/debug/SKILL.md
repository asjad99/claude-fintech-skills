---
name: debug
description: Find and fix the root cause of a bug, wrong amount, flaky test, slowdown or production incident, ending with a regression test. Use when something is broken, throws, posts the wrong amount, double-charges, or has regressed.
argument-hint: "[symptom]"
---

# Debug

Redact secrets and personal data in every output you show.

## Production incident first?
If real money or customers are affected now: size the funds at risk, and
treat severity as the higher of funds at risk and technical impact. Offer the
user the flow's kill switch and say who must be told (compliance, legal, a
regulator with a deadline). Then debug as below.

## Steps
1. **Loop.** Build one command that goes red on this bug, in roughly this
   order of preference: a failing test at the nearest seam; a script with a
   fixture input; a replay of a captured payload or webhook; old version vs
   new version on the same input; a property loop for "sometimes wrong". Make
   it fast and deterministic: fixed clock, seeded randomness, fixture data.
   Done when the command has been run and its red output shown. If no loop is
   possible, stop, list what you tried, and ask for logs, a reproduction or
   access.
2. **Shrink.** Reduce the input until every remaining part matters.
3. **Find the cause.** List two to four candidate causes, test the cheapest
   first, change one thing at a time; use `git bisect` when a known-good
   version exists.
   Done when you can state the cause in one sentence and the loop confirms it.
4. **Fix the cause.** Make the smallest change at the root, not at the
   symptom. Turn the loop into a permanent regression test.
   Done when the test was red before the fix and is green after, and the full
   suite passes.
5. **Repair the data.** If wrong records were written, correct them with new
   compensating records, never edits, and reconcile to confirm no money was
   duplicated, dropped or misattributed.
6. **Impact.** Search for the same pattern elsewhere and list affected callers;
   fix them or report them.
7. **Report.** Cause, fix, regression test, data repaired, other places
   checked. Then run the `review` skill.

## Usual suspects in money software
Floating point used for money · rounding mode or rounding too early ·
currencies mixed · duplicate webhook or retried request without an
idempotency key · flow not resumable after a crash · reservation never
released · amounts booked at authorisation instead of clearing · bank
returns or reversals arriving days later · day-count convention or time zone
wrong · stale price or rate · units (thousands vs millions, token decimals) ·
chain reorganisation before finality · integer division · culture-specific
number parsing.

Sources: SWEBOK Maintenance 2.1.3 and 4.1, Engineering Foundations (root cause
analysis); Fintech Engineering Handbook (Incident Response, Executing Money
Flows); loop-first method after mattpocock/skills `diagnosing-bugs` and
obra/superpowers `systematic-debugging`.

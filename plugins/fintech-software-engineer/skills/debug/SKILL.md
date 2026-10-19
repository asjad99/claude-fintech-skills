---
name: debug
description: Find and fix the root cause of a bug, wrong amount, flaky test, slowdown or production incident, ending with a regression test. Use when something is broken, throws, posts the wrong amount, double-charges, or has regressed.
argument-hint: "[symptom]"
---

# Debug

Redact secrets and personal data in each output that you show.

## Is this a production incident?
If the problem has an effect on real money or customers now, do these steps
first:
- Calculate the funds at risk.
- Set the severity to the higher of the funds at risk and the technical
  impact.
- Offer the kill switch of the flow to the user.
- Tell the user who must get a report: compliance, legal, or a regulator
  with a deadline.

Then do the steps below.

## Steps
1. **Loop.** Make one command that fails because of this bug. Usually, use the
   first method in this list that is possible:
   - a test that fails at the nearest seam
   - a script with a fixture input
   - a replay of a captured payload or webhook
   - the old version and the new version on the same input
   - a property loop, for a bug that occurs only sometimes

   Make the command fast and deterministic. Use a fixed clock, seeded
   randomness and fixture data.
   This step is complete when you have run the command and shown its red
   output. If you cannot make a loop, stop. Make a list of the methods that
   you used, and ask for logs, a reproduction or access.
2. **Smallest input.** Decrease the input until each part that remains is
   necessary.
3. **Find the cause.** Make a list of two to four possible causes. Test the
   cause with the lowest cost first. Change only one thing at a time. If a
   known good version exists, use `git bisect`.
   This step is complete when you can write the cause in one sentence. The
   loop must also show that the cause is correct.
4. **Fix the cause.** Make the smallest change at the root cause, not at the
   symptom. Change the loop into a permanent regression test.
   This step is complete when these conditions are true:
   - The test failed before the fix.
   - The test passes after the fix.
   - The full suite passes.
5. **Repair the data.** If the code wrote incorrect records, correct them
   with new compensating records. Do not edit the records. Then reconcile.
   Make sure that no money is duplicated, lost or recorded against the wrong
   party.
6. **Impact.** Search for the same pattern in other parts of the code. Make a
   list of the callers that it has an effect on. Fix them or report them.
7. **Report.** Give the cause, the fix, the regression test, the data that
   you repaired and the other parts that you examined. Then run the `review`
   skill.

## Usual causes of bugs in money software
- floating point for money
- an incorrect rounding mode, or rounding that occurs too early
- mixed currencies
- a duplicate webhook or a retried request without an idempotency key
- a flow that cannot resume after a crash
- a reservation that is never released
- amounts that are booked at authorisation and not at clearing
- bank returns or reversals that arrive days later
- an incorrect day-count convention or time zone
- a stale price or rate
- incorrect units, for example thousands in place of millions, or token
  decimals
- a chain reorganisation before finality
- integer division
- number parsing that is specific to a culture

Sources: SWEBOK Maintenance 2.1.3 and 4.1, Engineering Foundations (root cause
analysis); Fintech Engineering Handbook (Incident Response, Executing Money
Flows); loop-first method after mattpocock/skills `diagnosing-bugs` and
obra/superpowers `systematic-debugging`.

---
name: debug
description: Find and fix the root cause of a bug, wrong result, flaky test or slowdown, ending with a regression test. Use when something is broken, throws, returns the wrong number, or has regressed.
argument-hint: "[symptom]"
---

# Debug

Redact secrets in every command output you show.

1. **Loop.** Build one command that goes red on this bug, in roughly this
   order of preference: a failing test at the nearest seam; a script with a
   fixture input; a replay of a captured payload; old version vs new version
   on the same input; a property loop for "sometimes wrong". Make it fast and
   deterministic: fixed clock, seeded randomness, fixture data.
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
5. **Impact.** Search for the same pattern elsewhere and list affected callers;
   fix them or report them.
6. **Report.** Cause, fix, regression test, other places checked. Then run the
   `review` skill.

## Usual suspects for wrong numbers
Floating point used for money · rounding mode or rounding too early ·
currencies mixed · per-share history not split-adjusted · stale or
wrong-period data (FY vs TTM, restated figures) · units (thousands vs
millions) · UTC timestamp compared with a market-local date · integer
division · culture-specific number parsing.

Sources: SWEBOK Maintenance 2.1.3 and 4.1, Engineering Foundations (root cause
analysis); loop-first method after mattpocock/skills `diagnosing-bugs` and
obra/superpowers `systematic-debugging`.

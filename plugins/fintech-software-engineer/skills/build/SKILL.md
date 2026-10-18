---
name: build
description: Add, implement or change code test-first - before writing the first source file, write one failing test, then the least code to pass it, slice by slice, then run the full checks. Use for any request to add, build, implement, write or modify code in fintech or money-handling software.
argument-hint: "[spec path or acceptance criterion]"
---

# Build

Principles: `principles` skill (P1-P12). Rules:
`${CLAUDE_PLUGIN_ROOT}/references/fintech-rules.md` plus the domain packs the
work touches. Language notes: `references/dotnet.md` or `references/python.md`.

## Before the loop
1. **Criteria.** Take the acceptance criteria from the spec in `docs/specs/`,
   or write the one-line criterion for a small fix.
2. **Commands.** Find the repo's build, test, lint, format and type-check
   commands in its files (build and project files, lock files, Makefile, CI
   workflow). Run the tests once.
   Done when the baseline result is shown, pre-existing failures noted.
3. **Impact.** For changes to existing code, read the code and its callers and
   list what else the change touches.

## The loop, one acceptance criterion at a time
1. **Red.** Write one test at an agreed seam (a public interface), named with
   the criterion id. Run it.
   Done when the output shows it failing for the expected reason.
2. **Green.** Write the least production code that passes it.
   Done when it passes and the rest of the suite still does.
3. Move to the next criterion.

While writing code:
- Validate inputs and state preconditions at boundaries; handle each error
  explicitly.
- Money as decimal with currency; round only at boundaries, mode stated.
- Mutating operations take an idempotency key; multi-step flows persist each
  step and can resume.
- Log decisions with structured fields and correlation ids; keep secrets in
  configuration.
- Build what the criterion asks for and stop there.

## After the loop
4. **Invariants.** Add the domain's invariant checks as tests that run after
   every step of a generated sequence of operations (for example: journal
   entries net to zero; every reservation is settled or released; one
   accrual per loan per day).
5. **Tidy.** Improve names, remove duplication, split long functions, with
   the tests green after each change.
6. **Verify.** Run the full test suite, linter, formatter check and type
   checker or analyzers.
   Done when every command and its result is shown and all pass.
7. **Report and review.** Show a table of criterion → test name, name the
   fintech and domain rules the change enforces (for example idempotency,
   maker-checker, day-count), list what is untested, then run `review`.

## What a good test is
- It checks behaviour through a public interface, so a refactor that keeps
  behaviour keeps the test green.
- Its expected value comes from an independent source: a worked example, a
  statement, a regulation, a hand calculation. A test that recomputes the
  answer the way the code does proves nothing.
- It covers boundaries: zero, negative, empty, maximum, rounding midpoints,
  duplicates, timeouts, stale or missing data.
- Money logic also gets property tests and replay (idempotency) tests.
- Stored data gets an integration test against a real database in a
  container. Fakes stand in only for true externals: network, clock,
  providers.

Sources: SWEBOK Construction 1-4 and Testing 3; Fintech Engineering Handbook
(Testing Patterns); test-first loop after mattpocock/skills `tdd` and
obra/superpowers `test-driven-development`.

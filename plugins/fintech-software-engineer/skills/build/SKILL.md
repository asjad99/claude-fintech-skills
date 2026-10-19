---
name: build
description: Add, implement or change code test-first - before writing the first source file, write one failing test, then the least code to pass it, slice by slice, then run the full checks. Use for any request to add, build, implement, write or modify code in fintech or money-handling software.
argument-hint: "[ticket, spec path or acceptance criterion]"
---

# Build

Principles: the `principles` skill (P1-P12). Rules:
`${CLAUDE_PLUGIN_ROOT}/references/fintech-rules.md` and the domain packs for
the work. Language notes: `references/dotnet.md` or `references/python.md`.

## Before the loop
1. **Criteria.** Get the acceptance criteria from one of these sources:
   - the ticket in `docs/tickets/`, with its domains and rules
   - the spec in `docs/specs/`
   - for a small fix, a one-line criterion that you write
2. **Commands.** Find the build, test, lint, format and type-check commands
   of the repo. Look in its build and project files, lock files, Makefile and
   CI workflow. Run the tests one time.
   This step is complete when you show the baseline result and identify the
   failures that were there before your change.
3. **Impact.** If you change code that exists, read the code and its callers.
   Make a list of the other parts that the change has an effect on.

## The loop, one acceptance criterion at a time
1. **Red.** Write one test at an agreed seam (a public interface). Use the
   criterion ID in the test name. Run the test.
   This step is complete when the output shows that the test fails for the
   expected reason.
2. **Green.** Write the minimum production code that makes the test pass.
   This step is complete when the test passes and all the other tests
   continue to pass.
3. Go to the next criterion.

When you write code, obey these rules:
- At boundaries, validate the inputs and check the preconditions. Process
  each error explicitly.
- Keep money as a decimal with a currency. Round only at boundaries, and
  write the rounding mode.
- Give each operation that changes data an idempotency key. Make each flow
  with many steps persist each step, so that the flow can resume.
- Log decisions with structured fields and correlation IDs. Keep secrets in
  the configuration.
- Build only what the criterion asks for. Then stop.

## After the loop
4. **Invariants.** Add the invariant checks of the domain as tests. Run them
   after each step of a generated sequence of operations. Examples:
   - the journal entries net to zero
   - each reservation is settled or released
   - there is one accrual for each loan each day
5. **Tidy.** Make the names better, remove duplication and divide long
   functions. After each change, make sure that the tests pass.
6. **Full checks.** Run the full test suite, the linter, the formatter check
   and the type checker or analyzers.
   This step is complete when you show each command and its result, and all
   commands pass.
7. **Report and review.** Do these steps:
   - Show a table of each criterion and its test name.
   - Identify the fintech and domain rules that the change enforces (for
     example idempotency, maker-checker, day-count).
   - Make a list of the parts that you did not test.
   - Run `review`.

## Properties of a good test
- It examines behaviour through a public interface. If a refactor keeps the
  behaviour, the test continues to pass.
- It gets its expected value from an independent source. The source can be a
  worked example, a statement, a regulation or a calculation by hand. If a test calculates the
  answer in the same way as the code, the test does not prove anything.
- It includes these boundary cases: zero, negative, empty, maximum and
  rounding midpoints. It also includes duplicates, timeouts, and data
  that is stale or not there.
- For money logic, also write property tests and replay (idempotency) tests.
- For stored data, write an integration test against a real database in a
  container. Use fakes only for parts that are truly external: the network,
  the clock and the providers.

Sources: SWEBOK Construction 1-4 and Testing 3; Fintech Engineering Handbook
(Testing Patterns); test-first loop after mattpocock/skills `tdd` and
obra/superpowers `test-driven-development`.

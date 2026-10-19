---
name: spec
description: Turn a feature request into a written spec with user stories and testable acceptance criteria before any code is written. Use when starting a new feature, or when a request is vague, large, or touches money movement, balances, customer data or regulated activity.
argument-hint: "[feature]"
---

# Spec

Output: `docs/specs/<feature-slug>.md`. Use plain Markdown, so that you can
move the spec to an issue tracker later with no changes.

1. **Read.** Quickly read the code in the area, `GLOSSARY.md` and
   `docs/adr/`. Also read the idea brief in `docs/ideas/` or the wireframes
   in `docs/wireframes/`, if they exist.
   This step is complete when you can identify the modules and the money
   flows of the feature.
2. **Ask.** In one message, ask the three to six questions whose answers
   change the design. Give your recommended answer for each question:
   - Who uses the feature? Which domains does it have an effect on (ledger,
     payments, lending, investments, digital assets, compliance)?
   - Which money movements occur? Which movements are irreversible?
   - What are the precision, the rounding and the currencies?
   - What is the behaviour on failure: provider down, duplicate request,
     stale data, partial success?
   - Who approves what (maker-checker)? Which jurisdictions and regulators
     apply?
   - What is out of scope?

   This step is complete when the user answers or accepts your
   recommendations.
3. **Write** the spec from the template below.
   This step is complete when these conditions are true:
   - Each story has a minimum of one acceptance criterion with an ID.
   - You can test each criterion: a test can fail on it.
4. **Confirm.** Show the spec to the user. Change it until the user approves
   it. Then set `Status: approved`.

## Template
```markdown
# <Feature>
Status: draft · Date: YYYY-MM-DD · Domains: <ledger, payments, ...>

## Problem
What the user cannot do today and why it matters.

## Stories
- S1 As a <user>, I want <capability>, so that <benefit>.

## Acceptance criteria
- AC1 (S1) Given <state>, when <action>, then <observable result>.

## Money flows
Each movement: from, to, amount rule, reversible or not, idempotency key.

## Non-functional
Only what applies, each measurable: precision and rounding · latency ·
data freshness · audit trail · retention · data classification · approvals ·
regulatory reporting · volume.

## Out of scope

## Risks and open questions
```

## How to write good criteria
- Write the behaviour that a public interface shows (API response, screen,
  file, ledger entry, event). Do not write about internal parts. If
  wireframe screen IDs exist, refer to them: `AC4 (S2, W3)`.
- For money criteria, write the currency, the precision and the rounding
  mode.
- Get example values from an independent source (a statement, a worked
  example, a regulation). Then the tests that use them can disagree with
  the code.
- Write criteria for failure paths too: duplicate request, timeout, provider
  decline, stale data, invalid input, insufficient funds.

Sources: SWEBOK Requirements 1, 2, 4.3 (acceptance criteria), 7.3 (tracing)
and Engineering Management (scope, risk); questioning step after
obra/superpowers `brainstorming`; template after mattpocock/skills `to-spec`.

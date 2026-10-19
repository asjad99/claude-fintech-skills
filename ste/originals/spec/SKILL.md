---
name: spec
description: Turn a feature request into a written spec with user stories and testable acceptance criteria before any code is written. Use when starting a new feature, or when a request is vague, large, or touches money movement, balances, customer data or regulated activity.
argument-hint: "[feature]"
---

# Spec

Output: `docs/specs/<feature-slug>.md`. The format is plain Markdown so it can
move to an issue tracker later unchanged.

1. **Read.** Skim the code in the area, `GLOSSARY.md`, `docs/adr/`, and any
   idea brief in `docs/ideas/` or wireframes in `docs/wireframes/`.
   Done when you can name the modules and money flows involved.
2. **Ask.** In one message, ask the three to six questions whose answers
   change the design, each with your recommended answer:
   - Who uses it, and which domains does it touch (ledger, payments,
     lending, investments, digital assets, compliance)?
   - Which money movements happen, and which are irreversible?
   - Precision, rounding and currencies?
   - Behaviour on failure: provider down, duplicate request, stale data,
     partial success?
   - Who approves what (maker-checker), and which jurisdictions and
     regulators apply?
   - What is out of scope?
   Done when the user has answered or accepted your recommendations.
3. **Write** the spec from the template below.
   Done when every story has at least one acceptance criterion with an id,
   and each criterion is testable: a test could go red on it.
4. **Confirm.** Show the spec and revise until the user approves; set
   `Status: approved`.

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

## Writing good criteria
- Describe behaviour seen at a public interface (API response, screen,
  file, ledger entry, event), not internals. Cite wireframe screen ids
  where they exist: `AC4 (S2, W3)`.
- Money criteria name the currency, precision and rounding mode.
- Example values come from an independent source (a statement, a worked
  example, a regulation), so tests built on them can disagree with the code.
- Failure paths get criteria too: duplicate request, timeout, provider
  decline, stale data, invalid input, insufficient funds.

Sources: SWEBOK Requirements 1, 2, 4.3 (acceptance criteria), 7.3 (tracing)
and Engineering Management (scope, risk); questioning step after
obra/superpowers `brainstorming`; template after mattpocock/skills `to-spec`.

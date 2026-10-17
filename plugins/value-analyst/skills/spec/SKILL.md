---
name: spec
description: Turn a feature request into a written spec with user stories and testable acceptance criteria before any code is written. Use when starting a new feature, or when a request is vague, large, or touches money, valuations or stored data.
argument-hint: "[feature]"
---

# Spec

Output: `docs/specs/<feature-slug>.md`. The format is plain Markdown so it can
move to an issue tracker later unchanged.

1. **Read.** Skim the code in the area, `GLOSSARY.md` and `docs/adr/`.
   Done when you can name the modules involved.
2. **Ask.** In one message, ask the three to five questions whose answers
   change the design: who uses it, which data and source, precision and
   rounding, behaviour when data is missing or stale, what is out of scope.
   Give your recommended answer to each.
   Done when the user has answered or accepted your recommendations.
3. **Write** the spec from the template below.
   Done when every story has at least one acceptance criterion with an id,
   and each criterion is testable: a test could go red on it.
4. **Confirm.** Show the spec and revise until the user approves; set
   `Status: approved`.

## Template
```markdown
# <Feature>
Status: draft · Date: YYYY-MM-DD

## Problem
What the user cannot do today and why it matters.

## Stories
- S1 As a <user>, I want <capability>, so that <benefit>.

## Acceptance criteria
- AC1 (S1) Given <state>, when <action>, then <observable result>.

## Non-functional
Only what applies, each measurable: precision and rounding · latency ·
data freshness · audit trail · security · volume.

## Out of scope

## Risks and open questions
```

## Writing good criteria
- Describe behaviour seen at a public interface (API response, screen,
  file, stored record), not internals.
- Money criteria name the currency, precision and rounding mode.
- Example values come from an independent source (a filing, a worked
  example), so tests built on them can disagree with the code.
- Failure paths get criteria too: missing data, stale price, invalid input.

Sources: SWEBOK Requirements 1, 2, 4.3 (acceptance criteria), 7.3 (tracing)
and Engineering Management (scope, risk); questioning step after
obra/superpowers `brainstorming`; template after mattpocock/skills `to-spec`.

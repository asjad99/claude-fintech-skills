---
name: design
description: Design a change before building it - read the affected code, compare options, record an ADR, update the glossary, and agree where tests will sit. Use when a spec touches more than one module, the data model, a public API or an external data source.
argument-hint: "[spec path]"
---

# Design

1. **Comprehend.** Read the modules the spec touches and their callers; list
   each with one line on its job.
   Done when every acceptance criterion maps to a module.
2. **Options.** Describe two or three options, typically the smallest change,
   the cleanest design, and a middle path. For each: what changes, effort,
   risk, and cost to reverse. Recommend one and say why.
   Done when the user has chosen.
3. **Record.** When the choice is costly to reverse, write
   `docs/adr/NNNN-<title>.md` from the template below. Add new domain terms to
   `GLOSSARY.md` as `Term: one-line definition`. Create these files only when
   there is something to write.
4. **Seams.** List the public interfaces where tests will run, each with one
   line on what it catches and what it misses. Prefer existing seams and as
   few new ones as possible.
   Done when the user agrees.
5. **Model branching behaviour.** When something has three or more states or
   several parties (an order lifecycle, a data-refresh pipeline, a review
   workflow), add a Mermaid state or sequence diagram to the ADR or spec.

## Checks for every design
- Design principles: abstraction, separation of concerns, modularity,
  encapsulation, interface separate from implementation, low coupling, high
  cohesion, uniformity, completeness against the spec, verifiability.
- Prefer deep modules: much behaviour behind a small interface.
- Quality attributes: money correctness, auditability, idempotency, failure
  of external data sources, performance, security, testability.
- Money and data rules: `${CLAUDE_PLUGIN_ROOT}/references/fintech-rules.md`.

## ADR template
```markdown
# NNNN <Title>
Date: YYYY-MM-DD · Status: proposed | accepted | superseded by NNNN

## Context
Forces at play, including the spec ids this serves.

## Options
Each with effort, risk and cost to reverse.

## Decision

## Consequences
What gets easier, what gets harder, what to watch.
```
ADRs are append-only: a changed decision gets a new ADR that supersedes the
old one.

Sources: SWEBOK Architecture 2.4, Design 1.4 and 4.6, Models and Methods,
Economics (options compared on cost); phases after Anthropic's `feature-dev`;
glossary and ADR habit after mattpocock/skills `domain-modeling` and deep
modules after its `codebase-design`.

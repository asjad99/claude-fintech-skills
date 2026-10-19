---
name: design
description: Design a change before building it - read the affected code, compare options, check failure modes and threats, record an ADR, and agree where tests will sit. Use when a spec touches more than one module, the data model, a public API, a money flow or an external provider.
argument-hint: "[spec path]"
---

# Design

1. **Comprehend.** Read the modules the spec touches and their callers; list
   each with one line on its job. Read the domain packs the spec names.
   Done when every acceptance criterion maps to a module.
2. **Options.** Describe two or three options, typically the smallest change,
   the cleanest design, and a middle path. For each: what changes, effort,
   risk, and cost to reverse. Recommend one and say why.
   Done when the user has chosen.
3. **Failure modes.** For each external call or money movement in the chosen
   option, write one line each for: timeout, duplicate, out-of-order,
   partial success, provider down. Say what the system does.
   Done when every line has an answer or an open question.
4. **Threats.** For new endpoints, data stores or money flows, a short STRIDE
   pass: spoofing, tampering, repudiation, information disclosure, denial of
   service, elevation of privilege. Note data classification and where the
   data must live.
5. **Record.** When the choice is costly to reverse, write
   `docs/adr/NNNN-<title>.md` from the template below. Add new domain terms to
   `GLOSSARY.md` as `Term: one-line definition`. Create these files only when
   there is something to write.
6. **Seams.** List the public interfaces where tests will run, each with one
   line on what it catches and what it misses. Prefer existing seams.
   Done when the user agrees.
7. **Model branching behaviour.** Anything with three or more states or
   several parties (a payment lifecycle, a loan, an approval workflow) gets a
   Mermaid state or sequence diagram in the ADR or spec.

Before launching a new money flow or provider, also run a premortem: it is
three months later and this lost money. List the three likeliest causes and
the safeguard for each; a missing safeguard is a launch blocker.

## Checks for every design
- Design principles: abstraction, separation of concerns, modularity,
  encapsulation, interface separate from implementation, low coupling, high
  cohesion, uniformity, completeness against the spec, verifiability.
- Prefer deep modules: much behaviour behind a small interface.
- Quality attributes: money correctness, idempotency, auditability,
  resumability, security, performance, testability.
- Rules: `${CLAUDE_PLUGIN_ROOT}/references/fintech-rules.md`, the domain
  packs in `${CLAUDE_PLUGIN_ROOT}/references/domains/`, and
  `references/data-layer.md` when the change touches stores, events or
  pipelines.
- No code or stack yet: run `architect` first.

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
Security, Economics; premortem from the Fintech Engineering Handbook
(Incident Response); phases after Anthropic's `feature-dev`; glossary and ADR
habit after mattpocock/skills `domain-modeling`.

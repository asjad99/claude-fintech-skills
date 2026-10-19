---
name: architect
description: Set up a new project or a new service from nothing - choose the tech stack, data layer and deployment, record each choice as an ADR, then build a walking skeleton with CI, a Money type and one tested path. Use when the repo is empty or a new service, app or product is starting and there is no code yet for build and design to follow.
argument-hint: "[spec or idea path]"
---

# Architect

The other skills take versions, frameworks and commands from the repo. A new
project has none yet, so this skill decides them once and leaves a repo
they can follow. Read `${CLAUDE_PLUGIN_ROOT}/references/data-layer.md`, the
core fintech rules and the domain packs the spec names.

1. **Forces.** From the spec or idea brief, list what the system must do and
   the constraints: domains touched, volume and latency, where data must
   live, compliance scope (PCI, SOC 2, licences), providers and their SDKs,
   the team's existing skills, budget and hosting.
   Done when the user confirms the list.
2. **Stack.** Compare two or three options for language and framework,
   database, messaging and hosting. Score each against:
   - exact decimal money in the language and the database
   - real transactions, and an outbox or change data capture
   - a migration tool and locked dependencies
   - static types and analyzers that can run as errors in CI
   - official SDKs for the chosen providers
   - hosting region and data residency; how much falls in compliance scope
   - the team's skills and hiring market; cost to run and to reverse
   Recommend one and say why. Prefer boring, well-supported choices.
   Done when the user has chosen.
3. **Data layer.** Name the system of record for each core fact, the write
   model (ledger table, event sourcing or plain rows) and how data reaches
   analytics, following `data-layer.md`.
   Done when every money fact has one owner.
4. **Shape.** Choose the repo layout and module boundaries: start as one
   deployable with clear modules unless the forces demand more. Choose
   environments (local, sandbox, production) and how secrets reach each.
5. **Record.** Write `docs/adr/0001-tech-stack.md`, `0002-data-layer.md`,
   `0003-deployment.md` with the `design` ADR template, and start
   `GLOSSARY.md`.
   Done when the user accepts them.
6. **Walking skeleton.** Build the thinnest end-to-end slice:
   - build, test, lint, format and type-check commands in one documented
     place (Makefile, scripts or package file) and in CI
   - a `Money` value type, an injected clock, idempotency-key handling on
     mutating endpoints, structured logging with correlation ids
   - the first migration, with money columns as exact decimals
   - one path through the system with a test that goes red then green,
     following the `build` loop
   - a README section: how to run, test and deploy locally
   Done when CI runs green and the output is shown.
7. **Hand over.** From now on, `spec`, `design` and `build` follow the
   repo. Go to `tickets` for the first feature.

Ask before creating cloud resources, paid accounts or anything outside the
repo.

Sources: SWEBOK Architecture 2 (concerns, decisions, evaluation),
Configuration Management, Operations 1-3 and Economics; walking skeleton
after Alistair Cockburn and *Growing Object-Oriented Software, Guided by
Tests*; data-layer rules from the Fintech Engineering Handbook.

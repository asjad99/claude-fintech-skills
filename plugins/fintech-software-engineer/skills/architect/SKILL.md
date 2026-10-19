---
name: architect
description: Set up a new project or a new service from nothing - choose the tech stack, data layer and deployment, record each choice as an ADR, then build a walking skeleton with CI, a Money type and one tested path. Use when the repo is empty or a new service, app or product is starting and there is no code yet for build and design to follow.
argument-hint: "[spec or idea path]"
---

# Architect

The other skills get versions, frameworks and commands from the repo. A new
project does not have them yet. This skill makes these decisions one time. It
gives a repo that the other skills can follow. Read
`${CLAUDE_PLUGIN_ROOT}/references/data-layer.md`, the core fintech rules and
the domain packs that the spec identifies.

1. **Forces.** Use the spec or the idea brief. Make a list of the functions
   that the system must do, and of its constraints:
   - the domains of the system
   - the volume and the latency
   - where the data must be
   - the compliance scope (PCI, SOC 2, licences)
   - the providers and their SDKs
   - the current skills of the team
   - the budget and the hosting

   This step is complete when the user agrees with the list.
2. **Stack.** Compare two or three options for the language and framework,
   the database, the messaging and the hosting. Give each option a score
   against these criteria:
   - exact decimal money in the language and the database
   - real transactions, and an outbox or change data capture
   - a migration tool and locked dependencies
   - static types and analyzers that can run as errors in CI
   - official SDKs for the selected providers
   - the hosting region and data residency, and how much is in compliance
     scope
   - the skills of the team, and how easy it is to employ engineers
   - the cost to run and the cost to reverse

   Recommend one option and give the reason. If possible, use well-known
   options that have good support.
   This step is complete when the user selects an option.
3. **Data layer.** Obey `data-layer.md`. For each core fact, identify the
   system of record. Identify the write model: ledger table, event sourcing
   or plain rows. Identify how data goes to analytics.
   This step is complete when each money fact has one owner.
4. **Shape.** Select the repo layout and the module boundaries. If the forces
   do not make more units necessary, start with one deployable unit that has
   clear modules. Select the environments (local, sandbox, production).
   Select how each environment gets its secrets.
5. **Record.** Write `docs/adr/0001-tech-stack.md`, `0002-data-layer.md` and
   `0003-deployment.md` with the `design` ADR template. Start `GLOSSARY.md`.
   This step is complete when the user accepts the ADRs.
6. **Walking skeleton.** Build the smallest end-to-end slice. It must
   contain:
   - the build, test, lint, format and type-check commands, in one
     documented location (Makefile, scripts or package file) and in CI
   - a `Money` value type and an injected clock
   - idempotency keys on endpoints that change data
   - structured logging with correlation IDs
   - the first migration, with money columns as exact decimals
   - one path through the system, with a test that fails and then passes,
     as in the `build` loop
   - a README section that tells how to run, test and deploy locally

   This step is complete when CI passes and you show the output.
7. **Next steps.** After this step, `spec`, `design` and `build` obey the
   repo. For the first feature, go to `tickets`.

Ask the user before you create cloud resources, paid accounts or other items
outside the repo.

Sources: SWEBOK Architecture 2 (concerns, decisions, evaluation),
Configuration Management, Operations 1-3 and Economics; walking skeleton
after Alistair Cockburn and *Growing Object-Oriented Software, Guided by
Tests*; data-layer rules from the Fintech Engineering Handbook.

---
name: tickets
description: Break an approved spec into small, independently testable tickets that carry their acceptance criteria, domains and dependencies, then write them to docs/tickets and optionally push them to Multica or another tracker. Use after spec and design, when planning a sprint, or when asked to create tickets, issues, tasks or a backlog.
argument-hint: "[spec path]"
---

# Tickets

Output: `docs/tickets/<feature-slug>.md`, plain Markdown, then the tracker.

1. **Read.** The approved spec, its ADRs and `GLOSSARY.md`. Stop and run
   `spec` if the spec has no numbered acceptance criteria.
2. **Slice.** Cut vertical slices: each delivers behaviour someone can see
   at a public interface, through every layer it needs. Rules:
   - every acceptance criterion lands in exactly one ticket
   - a ticket is small enough for one `build` session (roughly a day)
   - the first ticket is the thinnest end-to-end path; edge and failure
     criteria follow as their own tickets
   - schema changes, provider integrations and kill switches get their own
     tickets when they are risky or must ship first
   Done when every criterion is covered once and nothing outside the spec
   appears.
3. **Order.** List dependencies and sort so each ticket depends only on
   earlier ones. Mark the ones that can run in parallel.
4. **Flag risk.** Mark `money-risk: high` on any ticket that moves money
   irreversibly, changes balances or the ledger, or touches a provider or
   approvals. Those need `design` (failure modes, premortem) before `build`
   and a human reviewer before merge.
5. **Write** each ticket from the template, then show the list.
   Done when the user approves it.
6. **Push** (optional, on request). See below.

## Template
```markdown
## T1 <Imperative title>
Spec: docs/specs/<feature>.md · Criteria: AC1, AC2 · Depends on: none
Domains: payments, ledger · Money-risk: high · Size: S | M | L

**Goal.** One sentence on the behaviour delivered.
**Acceptance criteria.** Copied from the spec, ids kept.
**Test seam.** The public interface where the tests run.
**Rules.** Domain packs and fintech rules that apply (for example
idempotency key, balanced entries, day-count convention).
**Done when.** Each criterion has a test that went red then green, the full
checks pass, and `review` reports no blocking findings.
```

Each ticket is self-contained so an agent that has not seen the
conversation can pick it up: it names the spec path, criteria and rules
rather than relying on context.

## Pushing to Multica
Multica is a ticket board where people and coding agents take on issues.
Agents drive it through the `multica` CLI.
1. Check `multica --version` and the active workspace. Run
   `multica issue create --help` to confirm flags and allowed status and
   priority values in the installed version.
2. Optionally create a parent issue for the feature, then one issue per
   ticket with `--parent`:
   `multica issue create --title "T1 <title>" --description-file <file>
   --parent <id> --output json`. The description is the ticket body above.
3. Multica has no dependency flag: keep `Depends on: T…` in each body,
   and add labels such as `money-risk-high` with `multica issue label add`.
4. Leave issues unassigned. Assigning an issue to an agent starts work, so
   assign only when the user asks, and never assign `money-risk: high`
   tickets to an agent without the user's go-ahead.
5. Write each returned issue id back into `docs/tickets/<feature>.md`.

For another tracker, use its connector if one is available; otherwise
export JSON or CSV with title, body, parent, labels and dependencies.

## After
Run `build` with a ticket id or path; it takes the criteria, domains and
rules from the ticket.

Sources: SWEBOK Requirements 7.3 (tracing) and Engineering Management
(work breakdown, scheduling, risk); slices follow Bill Wake's INVEST
(independent, valuable, small, testable); Multica CLI from multica.ai/docs/cli.

---
name: tickets
description: Break an approved spec into small, independently testable tickets that carry their acceptance criteria, domains and dependencies, then write them to docs/tickets and optionally push them to Multica or another tracker. Use after spec and design, when planning a sprint, or when asked to create tickets, issues, tasks or a backlog.
argument-hint: "[spec path]"
---

# Tickets

Output: `docs/tickets/<feature-slug>.md` in plain Markdown, and then the
tracker.

1. **Read.** Read the approved spec, its ADRs and `GLOSSARY.md`. If the spec
   does not have numbered acceptance criteria, stop and run `spec`.
2. **Slice.** Divide the spec into vertical slices. Each slice gives
   behaviour that a person can see at a public interface. Each slice goes
   through all the layers that are necessary. Obey these rules:
   - Put each acceptance criterion in exactly one ticket.
   - Make each ticket small enough for one `build` session (approximately
     one day).
   - Make the first ticket the smallest end-to-end path. Put the edge
     criteria and failure criteria in separate tickets after it.
   - If a schema change, provider integration or kill switch has risk, put
     it in a separate ticket. Do the same if it must ship first.

   This step is complete when each criterion is in one ticket only, and no
   ticket contains work that is not in the spec.
3. **Order.** Make a list of the dependencies. Sort the tickets so that each
   ticket depends only on earlier tickets. Mark the tickets that can run in
   parallel.
4. **Flag risk.** Mark a ticket `money-risk: high` if it does one of these:
   - It moves money irreversibly.
   - It changes balances or the ledger.
   - It calls or changes a provider integration, or changes approvals.

   These tickets must have `design` (failure modes, premortem) before
   `build`. They must also have a human reviewer before merge.
5. **Write** each ticket from the template. Then show the list.
   This step is complete when the user approves the list.
6. **Push** (optional, only if the user asks). Refer to the section below.

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

Each ticket must be complete in itself, so that an agent that did not see the
conversation can do the work. Each ticket gives the spec path, the criteria
and the rules. It does not depend on the context of the conversation.

## Push to Multica
Multica is a ticket board. People and coding agents take issues from it.
Agents use Multica through the `multica` CLI.
1. Run `multica --version` and find the active workspace. Run
   `multica issue create --help`. Use its output to make sure of the flags.
   Also make sure of the status and priority values that the version accepts.
2. If you want, create a parent issue for the feature. Then create one issue
   for each ticket with `--parent`:
   `multica issue create --title "T1 <title>" --description-file <file>
   --parent <id> --output json`. The description is the ticket body above.
3. Multica does not have a dependency flag. Because of this, keep
   `Depends on: T…` in each body. Add labels such as `money-risk-high` with
   `multica issue label add`.
4. Do not assign the issues. If you assign an issue to an agent, the agent
   starts the work. Assign an issue only when the user asks. Do not assign a
   `money-risk: high` ticket to an agent without the approval of the user.
5. Write each issue ID that Multica returns into
   `docs/tickets/<feature>.md`.

For a different tracker, use its connector if one is available. If no
connector is available, export JSON or CSV with the title, body, parent,
labels and dependencies.

## Next step
Run `build` with a ticket ID or path. The `build` skill gets the criteria,
domains and rules from the ticket.

Sources: SWEBOK Requirements 7.3 (tracing) and Engineering Management
(work breakdown, scheduling, risk); slices follow Bill Wake's INVEST
(independent, valuable, small, testable); Multica CLI from multica.ai/docs/cli.

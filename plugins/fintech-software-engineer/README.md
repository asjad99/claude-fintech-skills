# Fintech Software Engineer

Make Claude work like a disciplined software engineer on any software that
handles money: ledgers, payments, lending, brokerage and investment
platforms, digital assets, compliance tooling and financial analytics.

The plugin combines two sources:

- **IEEE SWEBOK v4.0a** (Guide to the Software Engineering Body of
  Knowledge), the source of an idea-to-release workflow and twelve
  engineering principles.
- **Fintech engineering practice** from the Fintech Engineering Handbook:
  decimal money, idempotent operations, append-only audit, reconciliation,
  and domain rules for ledgers, payments, lending, investments, digital
  assets and compliance.

It works in any language, with extra notes for .NET and Python.

## Install

In Claude Code:

```
/plugin marketplace add asjad99/claude-fintech-skills
/plugin install fintech-software-engineer@fintech-skills
```

## What you get

| Skill | Use it when |
|---|---|
| `principles` | Loads automatically on any coding task |
| `ideate` | You have an idea: office-hours questions one at a time, riskiest assumptions, a one-page brief and a user-interview script |
| `wireframe` | You want to see it: journeys, a numbered screen inventory, clickable HTML or Figma screens including failure states |
| `spec` | Starting a feature: clarifying questions, then numbered, testable acceptance criteria and money flows |
| `architect` | The repo is empty: tech stack, data layer and deployment decided as ADRs, then a walking skeleton with CI |
| `design` | A change crosses modules, a money flow or a provider: options, failure modes, threat model, decision record |
| `tickets` | A spec is approved: vertical-slice tickets with criteria, domains, dependencies and money-risk, optionally pushed to Multica |
| `build` | Writing code: one failing test, then the code to pass it, then invariant tests and full checks |
| `debug` | A bug, wrong amount or incident: a reproducible failing check, root cause, regression test, data repaired with correcting entries |
| `review` | Before calling work done: an independent `code-reviewer` agent checks spec, standards and fintech risk |
| `ship` | Releasing: change trail, migrations, kill switch, runbook, monitoring, rollback |

Six one-page domain packs (ledger, payments, lending, investments, digital
assets, compliance) are read only when the work touches that domain, and a
data-layer reference covers stores, events, pipelines, migrations and
analytics.

## What it runs

- **Money-lint hook (Claude Code and Cowork).** After Claude writes or edits a
  source file, `scripts/money_lint.py` runs locally with `python3`. It reads
  only the text Claude just wrote, from the hook input, and checks it for
  binary floating point used on money-like names (for example
  `double amount` or `price: float`) in C#, Java, Kotlin, Python, TypeScript
  and Go. It makes no network calls, writes no files, and reports findings
  back to Claude so it can switch to a decimal type. Add
  `money-lint: ignore` to a line to silence a deliberate case.
- **The `code-reviewer` agent** (Claude Code and Cowork) reads the change
  and runs your repository's own test, lint and type-check commands.
- **Multica CLI**, only when you ask `tickets` to push tickets to Multica:
  it runs your installed `multica` command to create issues and leaves them
  unassigned unless you say otherwise.
- Nothing else runs. The plugin collects no data, sends nothing to any
  server, and needs no accounts or credentials. The `evals/` folder holds
  test cases for the plugin's authors; their fixture scripts run only when a
  developer runs `claude plugin eval --scaffold` themselves.

## Where it works

Skills load in claude.ai chat, Cowork and Claude Code. The reviewer agent and
the money-lint hook load in Cowork and Claude Code.

## Licence and credits

MIT. Principles cite the SWEBOK Guide v4.0a (IEEE Computer Society); fintech
rules are paraphrased from the Fintech Engineering Handbook
(handbook.fintechengineer.io, after Voytek Pitula, CC BY 4.0). Workflows are
adapted from obra/superpowers, mattpocock/skills, Anthropic's
claude-plugins-official, garrytan/gstack and Aaronontheweb/dotnet-skills.
Full documentation: github.com/asjad99/claude-fintech-skills.

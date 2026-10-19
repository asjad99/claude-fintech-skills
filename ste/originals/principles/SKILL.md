---
name: principles
description: Engineering principles to load before writing, changing, reviewing or planning any code in fintech or money-handling software, including one-line fixes and new classes, functions, endpoints, jobs or schemas.
---

# Engineering principles

Work as a careful software engineer on software that handles other people's
money. Each principle cites its source in the SWEBOK Guide v4.0a.

| # | Principle | SWEBOK |
|---|---|---|
| P1 | **Trace.** Every change serves a requirement with an ID and acceptance criteria. For a small fix, state the criterion in one line. | Requirements 4.3, 7.3 |
| P2 | **Red first.** Write one failing test, then the code that passes it. Build in vertical slices. | Requirements 4.3; Construction 4.16 |
| P3 | **Simple.** Choose the plainest code that meets the criterion. Readable beats clever. | Construction 1.1 |
| P4 | **Deep modules.** Separate concerns; high cohesion, low coupling; small interfaces hiding the implementation. | Design 1.4 |
| P5 | **Verifiable.** Reach behaviour through public interfaces in tests, log decisions with structured fields, follow the repo's conventions. | Construction 1.3; Design 1.4 |
| P6 | **Contracts.** State preconditions at every boundary, validate inputs, and handle each error explicitly: raise it, log it, or return a typed failure. Every fallback is deliberate and visible. | Construction 4.4, 4.5 |
| P7 | **Small steps.** Keep changes small and reversible; values that vary live in configuration. | Construction 1.2 |
| P8 | **Impact first.** Read the code you change and its callers, and say what else the change touches before editing. | Maintenance 2.1.3, 4.1 |
| P9 | **Record decisions.** Decisions that are costly to reverse get an ADR with the options weighed. | Architecture 2.4; Design 4.6; Economics |
| P10 | **Secure by default.** Validate input, deny by default, least privilege, secrets from the environment or a vault, dependencies scanned. | Security 4 |
| P11 | **Reproducible.** Everything in version control, dependencies locked, schema changes as migrations. | Configuration Management |
| P12 | **Evidence.** Call work done only with the command and output that prove it, and name what is untested or unknown. | Professional Practice; Testing 1.2 |

## Fintech rules
Read `${CLAUDE_PLUGIN_ROOT}/references/fintech-rules.md` before any work that
touches money, balances, external financial data or audit records. Then read
the domain pack for each domain the work touches:

| The work touches | Read |
|---|---|
| Accounts, balances, journals, accounting | `references/domains/ledger.md` |
| Moving money: cards, bank transfers, wires, instant payments, payouts | `references/domains/payments.md` |
| Loans, credit lines, interest, repayments | `references/domains/lending.md` |
| Orders, trading, portfolios, market data, valuations | `references/domains/investments.md` |
| Crypto, stablecoins, tokenised assets, wallets | `references/domains/digital-assets.md` |
| Identity, KYC/AML, sanctions, permissions, privacy, approvals | `references/domains/compliance.md` |

Paths are under `${CLAUDE_PLUGIN_ROOT}/`; read only the packs the work touches.
For schemas, migrations, events, pipelines or analytics, also read
`references/data-layer.md`.

## Languages
The repo's build files, lock files and CI decide versions, frameworks and
commands. C#: also read `references/dotnet.md`; Python: `references/python.md`.

## Which skill
| Situation | Skill |
|---|---|
| An idea to pressure-test before building | `ideate` |
| Screens or a flow to sketch or show users | `wireframe` |
| New feature, or a vague or large request | `spec` |
| Empty repo or new service: no stack chosen yet | `architect` |
| Change crosses modules, the data model, a public API, a money flow or an external provider | `design` |
| Approved spec to split into tickets or push to a tracker | `tickets` |
| Writing or changing code | `build` |
| Something broken, wrong, flaky, slow, or a production incident | `debug` |
| Before calling work done | `review` |
| Merging, releasing, deploying | `ship` |

A small change needs `build` and `review`; state its criterion in one line.
While developing, run against sandboxes, test accounts and fixtures. Ask
the user before running anything that could move real money, touch
production data or contact real customers.

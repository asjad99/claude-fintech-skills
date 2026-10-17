# value-analyst

A Claude Code plugin that turns Claude into a value-investing analyst whose
work could survive an audit. The investing method is classic value
(circle of competence → quality → strength → earnings quality → triangulated
valuation → margin of safety → falsifiable thesis). The data discipline comes
from the [Fintech Engineering Handbook](https://handbook.fintechengineer.io):
no invented data, no lost data, no trust.

It also turns Claude into a disciplined software engineer for building the
.NET and Python apps that do this work: see
[Engineering workflow](#engineering-workflow) below.

**Research and decision support only. It never places trades and is not
personal financial advice.**

## What makes it different from "ask Claude about a stock"

| Handbook idea | In this plugin |
|---|---|
| Every number has a provenance trail | Every figure lives in an append-only **evidence ledger** with source, tier, period, locator and the SHA-256 of the raw payload it came from |
| Store raw requests/responses | `ledger.py raw` saves filings and API responses before any number is read from them |
| Corrections are new entries, never edits | `--supersedes … --reason …`; a **PreToolUse hook** blocks any direct edit of the ledger or raw files |
| Tamper evidence via hash chains | Each entry hashes the previous; `ledger.py verify` detects edits |
| Never use floats for money; amount + currency together; directional FX | `money.py`: Decimal only, controlled ISO 4217 set with correct minor units, cross-currency arithmetic refused |
| Cross-check sources; classify breaks | `reconcile.py` classifies scale, sign, period, currency, restatement and genuine breaks, plus A = L + E identity checks |
| Stale data halts automated actions | Prices older than the configured limit are "unavailable", not used |
| Corporate actions as explicit events | `corpactions.py` split-adjusts per-share history from recorded events |
| Tax lots, wash sales across accounts | `portfolio.py` derives positions from lots and flags wash-sale risk across all accounts of an owner |
| Maker-checker | The analyst proposes a decision; a separate `thesis-checker` agent re-derives inputs from raw sources and approves or rejects. The ledger refuses self-approval |
| Golden, property and invariant tests | 27 standard-library tests under `tests/` |

The calculators accept **ledger ids only** (e.g. `--fcf0 F-0060`), and a
**PostToolUse hook** rejects any report line that states a number without a
ledger tag such as `[F-0012]` or `[C-0007]`. Together they make it hard for the
model to slip an invented figure into a valuation or a report.

## Install

Try it for one session:

```bash
claude --plugin-dir ./value-analyst-marketplace/plugins/value-analyst
```

Or add the bundled marketplace and install it, so the configuration dialog
appears:

```
/plugin marketplace add ./value-analyst-marketplace
/plugin install value-analyst@fintech-skills
```

Requires Python 3.10+ (standard library only).

## Use

| Command | What it does |
|---|---|
| `/value-analyst:analyze AAPL` | Full analysis: identify → gather → corporate actions → reconcile → quality & forensics → valuation → report → verdict → independent review |
| `/value-analyst:gather-evidence KEY` | Pull statements, prices and corporate actions into the ledger |
| `/value-analyst:reconcile-data KEY` | Cross-source and identity checks, break resolution |
| `/value-analyst:forensic-quality KEY` | ROIC, margins, FCF conversion, Piotroski, Altman, Beneish |
| `/value-analyst:valuation KEY` | EPV, DCF, reverse DCF, NCAV, owner earnings, Graham number, MOS |
| `/value-analyst:review-thesis KEY` | Maker-checker review by the `thesis-checker` agent |
| `/value-analyst:portfolio-review lots.csv` | Holdings vs intrinsic value, stale prices, sell plans with wash-sale flags |
| `/value-analyst:dossier KEY` | Audit trail: how a conclusion was reached |

`data-discipline` loads automatically whenever Claude handles financial
figures, even outside a full analysis.

Research lands in `research/<KEY>/` in your project: `ledger.jsonl`, `raw/`,
`report.md`.

## Engineering workflow

Seven short skills and one reviewer agent, built on the 18 knowledge areas of
the [SWEBOK Guide v4.0a](https://computer.org/swebok). Each rule cites the
SWEBOK section it comes from. Versions, frameworks and commands are not fixed:
the skills read them from the repo (`global.json`, `*.csproj`,
`pyproject.toml`, lock files, CI workflows).

| Skill | Use when | Done when |
|---|---|---|
| `principles` | Any coding task (loads automatically) | — |
| `/value-analyst:spec` | New feature or vague request | Approved spec in `docs/specs/` with testable, IDed acceptance criteria |
| `/value-analyst:design` | Change crosses modules, data model, API or data source | ADR in `docs/adr/`, glossary updated, test seams agreed |
| `/value-analyst:build` | Writing or changing code | Every criterion has a test that went red then green; full checks shown passing |
| `/value-analyst:debug` | Bug, wrong number, flaky test, slowdown | Root cause in one sentence; regression test red before, green after |
| `/value-analyst:review` | Before calling work done | `code-reviewer` agent reports no blocking findings |
| `/value-analyst:ship` | Merge, release, deploy | Version, changelog, migrations, rollback steps and monitoring evidenced |

Flow: spec → design → build ⇄ review → ship; bugs enter through debug. Small
changes go straight to build and review with a one-line criterion.

| SWEBOK knowledge area | Where |
|---|---|
| 1 Requirements, 9 Engineering Management | `spec` |
| 2 Architecture, 3 Design, 11 Models and Methods, 15 Economics | `design` |
| 4 Construction, 5 Testing | `build` |
| 7 Maintenance, 18 Engineering Foundations (root cause) | `debug` |
| 12 Quality, 13 Security | `review`, `code-reviewer` |
| 6 Operations, 8 Configuration Management | `ship` |
| 10 Process | the flow above |
| 14 Professional Practice | `principles` (P12) |
| 16 Computing, 17 Mathematical Foundations | already known to the model; decimal and rounding rules in `references/fintech-rules.md` |

Money, data and audit rules for app code: `references/fintech-rules.md`.
Language notes: `references/dotnet.md`, `references/python.md`. For language
diagnostics, also install Anthropic's `csharp-lsp` and `pyright-lsp` plugins.

### Testing the prompts

`evals/` holds four cases (C# calculation, Python money bug, review with
planted defects, vague feature). Each runs with and without the plugin so the
report shows what the plugin adds:

```bash
claude plugin eval plugins/value-analyst --scaffold \
  --allow-tools Write Edit "Bash(git *)"
```

`--scaffold` runs the cases' fixture scripts, which only create local files
and a git repo. Runs use your Claude plan or API usage.

## Configuration

Set at install, or later with `/plugin configure value-analyst@fintech-skills`:

| Option | Default | Meaning |
|---|---|---|
| research_dir | `research` | Where ledgers live |
| base_currency | `USD` | Portfolio reporting currency |
| required_margin_of_safety_pct | 30 | Minimum MOS for a CANDIDATE verdict |
| max_price_age_days | 3 | Older prices are treated as unavailable |
| max_fundamentals_age_days | 120 | Staleness limit for interim data (annual gets +365) |

## Data sources

Works with whatever Claude can reach: SEC EDGAR via WebFetch (company facts
XBRL API and filings), company IR sites, and any financial-data MCP server you
connect (recorded as a secondary source and reconciled against filings). See
`references/data-sources.md`.

## Layout

```
.claude-plugin/plugin.json   manifest + userConfig
skills/                      research: analyze, gather-evidence, reconcile-data, forensic-quality,
                             valuation, review-thesis, portfolio-review, dossier, data-discipline
                             engineering: principles, spec, design, build, debug, review, ship
agents/                      thesis-checker, evidence-collector, code-reviewer
hooks/hooks.json             ledger guard (PreToolUse), provenance lint (PostToolUse)
scripts/                     money, ledger, valuation, forensics, reconcile,
                             corpactions, portfolio, guard_ledger, lint_report
references/                  handbook principles, value method, metrics, data sources,
                             report template, lot CSV format, fintech-rules, dotnet, python
tests/                       python3 -m unittest discover -s tests
evals/                       claude plugin eval cases for the engineering skills
```

## Limitations

- The provenance linter is a heuristic: it catches numbers in money, percent,
  multiple and decimal forms; it cannot tell whether a correctly tagged
  sentence paraphrases its source faithfully. That is the checker's job.
- Forensic models (Altman, Beneish, Piotroski) were fit on particular samples;
  they are screens, not verdicts, and don't apply to financials.
- Wash-sale logic is the US 30-day rule, as a warning only.
- The plugin structures judgement; it doesn't replace it. Assumptions remain
  assumptions, however well recorded.

## Attribution and licence

Engineering skills are original text that adapts workflows from these
MIT/Apache-licensed projects, with thanks: [obra/superpowers](https://github.com/obra/superpowers)
(brainstorming, verification before completion, systematic debugging),
[mattpocock/skills](https://github.com/mattpocock/skills) (tdd, diagnosing-bugs,
code-review, domain-modeling, codebase-design, writing-for-agents),
[anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)
(feature-dev, pr-review-toolkit), [garrytan/gstack](https://github.com/garrytan/gstack)
(security review checklist) and [Aaronontheweb/dotnet-skills](https://github.com/Aaronontheweb/dotnet-skills)
(.NET practices). Principles cite the SWEBOK Guide v4.0a (IEEE Computer
Society); no SWEBOK text is reproduced.


Engineering principles are paraphrased and adapted from the Fintech Engineering
Handbook (handbook.fintechengineer.io), which builds on Voytek Pitula's Fintech
Engineering Handbook (CC BY 4.0). No handbook text is reproduced; see
`references/handbook-principles.md` for the chapter mapping. The handbook site
carries a `noai` robots tag; check its licence terms for the extended chapters
before redistributing derived material.

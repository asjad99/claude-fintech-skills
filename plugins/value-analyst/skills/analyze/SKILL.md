---
name: analyze
description: Run a full value-investing analysis of one listed company - evidence gathering, reconciliation, quality and forensic screens, triangulated valuation, margin of safety, and an independently reviewed verdict. Use when asked to analyse, value, research or "look at" a stock or company as an investment.
argument-hint: "[ticker, ISIN or company name]"
---

# Value analysis: $ARGUMENTS

You are a value analyst whose work could be audited. Method comes from
`${CLAUDE_PLUGIN_ROOT}/references/value-method.md`; data discipline from
`${CLAUDE_PLUGIN_ROOT}/references/handbook-principles.md`. Read both before the
first step if you have not this session.

## Commands
Use these exact invocations (the plugin's scripts are not on PATH):

- `LEDGER` = `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ledger.py" --root "${user_config.research_dir}"`
- `VALUE` = `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/valuation.py" --root "${user_config.research_dir}"`
- `FORENSICS` = `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/forensics.py" --root "${user_config.research_dir}"`
- `RECON` = `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/reconcile.py" --root "${user_config.research_dir}"`
- `CA` = `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/corpactions.py" --root "${user_config.research_dir}"`

## Non-negotiables
1. **No invented data.** Never type a number into a report, a calculation or a
   reply that is not already a ledger entry. If you need a number you don't
   have, fetch it and record it, record an explicit assumption with a
   rationale and range, or say it is unavailable. Memory is not a source.
2. **No lost data.** Save raw payloads (`LEDGER raw`) before reading numbers out
   of them. Never edit `ledger.jsonl` or `raw/`; correct with `--supersedes`.
3. **No trust.** Valuation inputs need a primary source and, where possible, a
   second source that agrees. Price older than `${user_config.max_price_age_days}`
   days is unavailable. News is a lead, not a fact.
4. **Decision support only.** Never place, stage or recommend placing orders.
   End user-facing output with: "Research and decision support only — not
   personal financial advice."

## Steps (track them with the task list)

1. **Identify the security.** Resolve name → exchange, ticker, ISIN/CUSIP/FIGI,
   CIK for US filers, trading and reporting currency, fiscal year end. Choose
   the ledger KEY: the ISIN if known, else `EXCHANGE-TICKER`. If the ledger
   exists, run `LEDGER verify -s KEY` and `LEDGER stale -s KEY
   --max-price-age-days ${user_config.max_price_age_days}
   --max-fundamentals-age-days ${user_config.max_fundamentals_age_days}` and
   refresh only what is stale. Otherwise `LEDGER init`.
2. **Circle-of-competence gate.** Write the three-sentence business summary as
   a `note` with a source URL. If the business falls under a sector caveat in
   value-method.md, adapt the method or stop with INSUFFICIENT_DATA.
3. **Gather evidence.** Follow the `gather-evidence` skill. For long pulls,
   delegate to the `evidence-collector` agent with the KEY and the list of
   metrics × periods (5 fiscal years plus the latest quarter and spot price).
4. **Corporate actions.** Record splits, reverse splits, spin-offs and
   identifier changes in the window (`LEDGER ca`), then `CA adjust` every
   per-share series you will chart or compare across years.
5. **Reconcile.** Follow `reconcile-data`. Resolve every blocking break before
   using the number: supersede the wrong fact, or exclude it and say why.
6. **Quality and strength.** Follow `forensic-quality`.
7. **Valuation.** Follow `valuation`: at least two methods plus a reverse DCF,
   every input an F/A id, then `VALUE mos` with
   `--required-pct ${user_config.required_margin_of_safety_pct}`.
8. **Draft the report** at `${user_config.research_dir}/KEY/report.md` from
   `${CLAUDE_PLUGIN_ROOT}/references/report-template.md`. Tag every figure. The
   provenance hook will reject untagged numbers; fix what it reports.
9. **Propose a verdict** with `LEDGER decide` citing the C/K/F/A ids it rests
   on. CANDIDATE requires: passes quality/strength gates, unresolved breaks =
   0, MOS ≥ ${user_config.required_margin_of_safety_pct}%.
10. **Independent review.** Hand the KEY to the `thesis-checker` agent (it runs
    as actor `checker`; you are `analyst`). Do not share your reasoning beyond
    the report and ledger. If it rejects, fix the findings and re-propose;
    don't argue it into approval.
11. **Close.** `LEDGER verify -s KEY` must pass. Reply with the verdict, value
    range, price, MOS, the reviewer outcome, the two or three facts that matter
    most, and the biggest open question. Point to the report file.

## Stop conditions
- Can't find a primary source for revenue, operating income, cash flow,
  debt, cash and share count → INSUFFICIENT_DATA, list what's missing.
- Unresolved breaks on valuation inputs → don't value; report the breaks.
- No fresh price → value the business, report "price unavailable", no MOS.

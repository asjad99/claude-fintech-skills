# Report template

Save as `<research_dir>/<KEY>/report.md`. Every line that states a number
carries a ledger tag such as `[F-0012]`, `[A-0003]` or `[C-0007, F-0021]`; the
provenance hook rejects untagged figures. Keep prose short and concrete.

```markdown
# <Company> (<EXCHANGE>:<TICKER>, <ISIN>) — <VERDICT>

As of <YYYY-MM-DD> · Ledger <KEY> · Verified: <yes/no> · Reviewer: <approved/rejected/pending> [V-0001]

## Verdict in one paragraph
Price <x> [F-....] vs conservative value <y> [C-....]; margin of safety <z>% [C-....]
against a required <r>%. One sentence on why.

## Business in three sentences
Who pays, for what, why they keep paying. Cite notes [N-....].

## Quality
| Metric | FY-4 | FY-3 | FY-2 | FY-1 | FY | Source |
|---|---|---|---|---|---|---|
| ROIC | ... | ... | ... | ... | ... | [C-....] |
| Gross margin | ... |
Moat: name it, evidence for it [N-....], evidence against it.

## Financial strength
Net debt/EBITDA, interest cover, Altman Z with model used [C-....].

## Earnings quality
Piotroski x/9 [C-....], Beneish M [C-....], accruals [C-....]; what to read
further.

## Valuation
| Method | Value/share | Key assumptions | Entry |
|---|---|---|---|
| EPV | ... | cost of capital [A-....] | [C-....] |
| DCF | ... | growth [A-....], terminal [A-....] | [C-....] |
| Reverse DCF | implied growth ... | | [C-....] |
Sensitivity: worst plausible cell in the DCF grid [C-....].

## Thesis and kill criteria
1. Statement — metric and threshold that would falsify it.

## Pre-mortem
Three ways this loses half its value, each with a monitoring signal.

## Data quality
Reconciliation summary [K-....], single-source items, stale items, open
breaks and how they were resolved, assumptions with the widest ranges.

## What we don't know
Missing data and unanswered questions. Nothing here is filled by guesswork.

---
Research and decision support only. Not personal financial advice.
```

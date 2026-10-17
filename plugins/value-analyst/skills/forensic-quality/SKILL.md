---
name: forensic-quality
description: Assess business quality, financial strength and earnings quality from ledger facts - ROIC, margins, FCF conversion, leverage, Piotroski F-score, Altman Z, Beneish M-score, accruals. Use when judging whether a business is good and its accounts trustworthy, before valuing it.
argument-hint: "[ledger KEY] [fiscal years]"
---

# Quality, strength and earnings quality

`FORENSICS` = `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/forensics.py" --root "${user_config.research_dir}"`

Run, for the five fiscal years in the ledger:

```
FORENSICS quality   -s KEY --periods FY2021,FY2022,FY2023,FY2024,FY2025
FORENSICS piotroski -s KEY --year FY2025 --prior FY2024
FORENSICS beneish   -s KEY --year FY2025 --prior FY2024
FORENSICS altman    -s KEY --year FY2025 --model zpp        # non-manufacturers
FORENSICS altman    -s KEY --year FY2025 --model original --market-period spot  # manufacturers
```

Each run appends a C- entry; cite it in the report.

## Interpreting
- **Unavailable components stay unavailable.** A Piotroski of 5/6 is not 7/9.
  Report the denominator.
- **ROIC:** look at the minimum and the median across the cycle, not the peak.
  A moat claim needs ROIC above the cost of capital through the bad years and a
  named mechanism with evidence (`note` entries).
- **Beneish above −1.78 or rising accruals:** read the revenue-recognition and
  receivables notes in the 10-K, check for auditor changes and restatements,
  and record what you found as notes. A score is a reason to look, never an
  accusation.
- **Altman Z:** use `zpp` unless the company is a manufacturer; skip for banks,
  insurers and other financials (say so).
- **Leverage:** compare net debt and maturities with normalised FCF, not with
  peak EBITDA.

## Gate
The business fails the quality/strength gate (verdict PASS unless there is an
asset-value case) if any of these hold and you cannot explain them with
cited evidence:
- median ROIC below a reasonable cost of capital over five years
- negative cumulative FCF over five years
- Altman Z in distress zone on the appropriate model
- net debt / EBITDA above 4 with maturities inside three years
- Beneish M above −1.78 with no benign explanation found in the notes

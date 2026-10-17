---
name: valuation
description: Value a company with triangulated methods (EPV, DCF, reverse DCF, NCAV, owner earnings, Graham number) using only ledger facts and recorded assumptions, then compute the margin of safety. Use when estimating intrinsic value, a buy-below price, or what growth a share price implies.
argument-hint: "[ledger KEY]"
---

# Valuation

`LEDGER` = `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ledger.py" --root "${user_config.research_dir}"`
`VALUE` = `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/valuation.py" --root "${user_config.research_dir}"`

The calculators accept **ledger ids only**. Typed numbers are impossible by
design: every input is an F- fact or an A- assumption you recorded first.

## 1. Record assumptions explicitly
Each judgement becomes an assumption with a rationale, a range, and the facts
it is based on:
```
LEDGER assume -s KEY --metric discount_rate --value 9 --unit pct \
  --low 8 --high 11 --rationale "equity cost for a low-leverage, mature firm" \
  --refs F-0031,F-0044
LEDGER assume -s KEY --metric fcf_growth_10y --value 6 --unit pct --low 3 --high 8 \
  --rationale "5y revenue CAGR 7% [C-0004] with margin flat" --refs C-0004
LEDGER assume -s KEY --metric years --value 10 --unit years --rationale "explicit period"
LEDGER assume -s KEY --metric terminal_growth --value 2.5 --unit pct --low 1.5 --high 3 \
  --rationale "at or below long-run nominal GDP"
```
Normalised earnings (mid-cycle EBIT, owner earnings base, maintenance capex)
are assumptions too, unless they are a straight computation over facts.

## 2. Run at least two methods plus reverse DCF
```
VALUE epv -s KEY --ebit A-0006 --tax-rate A-0007 --discount-rate A-0001 \
  --shares F-0052 --debt F-0040 --cash F-0041
VALUE dcf -s KEY --fcf0 F-0060 --growth A-0002 --years A-0003 \
  --terminal-growth A-0004 --discount-rate A-0001 --shares F-0052 \
  --debt F-0040 --cash F-0041 --fade
VALUE reverse-dcf -s KEY --fcf0 F-0060 --years A-0003 --terminal-growth A-0004 \
  --discount-rate A-0001 --shares F-0052 --debt F-0040 --cash F-0041 --price F-0070
VALUE ncav -s KEY --current-assets F-0033 --total-liabilities F-0036 --shares F-0052
VALUE owner-earnings -s KEY --net-income F-0020 --dna F-0015 --maintenance-capex A-0008
VALUE graham-number -s KEY --eps F-0055 --bvps F-0057
```
Choose methods that fit the business (value-method.md §6). If values are in
the reporting currency and the stock trades in another, record
`fx_<REPORTING><TRADING>` as a fact and pass `--fx F-xxxx`.

## 3. Read the warnings
- Terminal value > 75% of EV: the DCF is mostly a terminal-growth bet; lean on
  EPV and the reverse DCF.
- Methods disagree by > 50%: present a range, explain the gap (franchise value?
  growth? asset-heavy?), don't average it away.
- Use the sensitivity grid: report the value at the pessimistic corner of the
  plausible ranges, not only the base case.

## 4. Margin of safety
```
VALUE mos -s KEY --value C-0010 --value C-0011 --price F-0070 \
  --required-pct ${user_config.required_margin_of_safety_pct}
```
The conservative (lowest) method anchors MOS and the buy-below price.

## Changing a method (shadow first)
If you change a valuation approach for a security already on file, run the
new method alongside the old one on the same ledger, record both, and explain
the difference in a note before the new one is used for a verdict.

# Value-investing method

The handbook supplies the data discipline; this file supplies the investing
method. It follows the classic value tradition (Graham's margin of safety,
Buffett/Munger's quality and owner earnings, Greenwald's EPV/asset-value
triangulation). The analyst works through the stages in order and may stop
early with PASS or INSUFFICIENT_DATA.

## 0. Circle of competence (gate)
Can the business model be explained in three plain sentences: who pays, for
what, and why they keep paying? If not, or if the accounts depend on
specialised models (banks, insurers, biotech pipelines, exploration miners),
say so and either use the sector caveats below or stop.

## 1. Business quality
- **Economics:** ROIC across a full cycle (5-10 years), not one good year.
  Durable ROIC above the cost of capital is the quantitative sign of a moat.
- **Moat source:** name it and cite the evidence: switching costs, network
  effects, cost advantage/scale, intangibles (brand, licences, patents),
  efficient scale. "Strong brand" with no pricing-power evidence is not a moat.
- **Margins and stability:** gross and operating margins over the cycle; how
  they behaved in the worst year.
- **Cash conversion:** FCF / net income near or above 1 over time. Persistent
  gaps need an explanation (working-capital build, capitalised costs).
- **Reinvestment runway:** can incremental capital earn similar returns?

## 2. Management and capital allocation
Buybacks below value or above it, acquisition record (goodwill write-downs),
dividend policy vs reinvestment needs, insider ownership and dealing,
compensation metrics (EPS-linked pay encourages buyback-driven EPS), candour of
letters on past mistakes. Each claim cites a filing, proxy or transcript.

## 3. Financial strength
Net debt / EBITDA, interest cover, debt maturities against FCF, off-balance-sheet
obligations (leases, pensions, guarantees), Altman Z (right model for the
sector). A great business with a fragile balance sheet can still be wiped out.

## 4. Earnings quality (forensic screen)
Piotroski F-score, Beneish M-score, accruals ratio, receivables and inventory
growing faster than sales, changes in auditor or revenue-recognition policy,
recurring "non-recurring" charges, adjusted-vs-GAAP gap. A bad score is a
reason to read the notes, not a verdict.

## 5. Normalised earning power
Choose the base figure for valuation deliberately: mid-cycle margins times
current revenue, owner earnings (NI + D&A − maintenance capex − ΔWC), or
average FCF. Record the choice and its reasoning as an assumption.
Maintenance capex is usually not disclosed; estimating it (e.g. D&A, or
Greenwald's PP&E/sales method) is an assumption with a range.

## 6. Valuation — triangulate, never one number
Run at least two independent methods appropriate to the business:
- **Asset value** (NCAV or reproduction cost) — the floor; most relevant for
  cyclicals, asset-heavy or distressed firms.
- **Earnings power value** — what today's sustainable earnings are worth with
  zero growth. If EPV > asset value, the gap is the franchise value.
- **DCF** — only where growth is defensible; keep terminal growth at or below
  long-run nominal GDP, and be wary when the terminal value is most of the
  answer.
- **Reverse DCF** — what growth the market price already assumes. Often the
  most useful single output: "the price needs 9% growth for 10 years".
- **Graham number** — a ceiling screen for defensive investors, not a value.
Treat disagreement between methods as information. Report a range; the
conservative end anchors the margin of safety.

## 7. Margin of safety and verdict
MOS = 1 − price / conservative value. Verdicts:
- **CANDIDATE** — passes stages 0-4, MOS ≥ required threshold, reconciled data,
  reviewer approved.
- **WATCHLIST** — good business, price not low enough; record the buy-below
  price.
- **PASS** — fails quality, strength or competence.
- **INSUFFICIENT_DATA** — cannot verify key inputs; list what is missing.

## 8. Thesis, kill criteria and pre-mortem
Write the thesis as 3-5 falsifiable statements with the metric that would
prove each wrong ("ROIC stays above 15%"; "net retention stays above 110%").
Run a pre-mortem: it is three years later and the investment lost 50% — what
are the three most likely reasons? Each reason needs a monitoring signal.

## Behavioural checks
Anchoring on purchase price or 52-week highs, confirmation bias (the checker
agent exists to counter this), narrative over numbers, recency in
extrapolating the last few years, sunk-cost when reviewing an existing holding.

## Sector caveats
- **Banks/insurers:** EV/FCF and Altman Z don't apply; use P/TBV vs ROE,
  combined ratio, reserve development, capital ratios.
- **REITs:** FFO/AFFO, NAV per share, payout vs AFFO.
- **Cyclicals/commodities:** normalise over the cycle; low P/E at peak margins
  is a trap.
- **Serial acquirers:** organic growth vs bought growth; ROIC including goodwill.

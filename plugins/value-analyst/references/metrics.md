# Standard metric names

The scripts look facts up by these names. Record every fact with the exact
name, the period label, a unit, and the source. Units: an ISO currency code
for money, `per_share` (with `--currency-of`) for per-share money, `shares`,
`ratio`, `pct`, `count`, `days`, `years`.

Period labels: `FY2025` (fiscal year), `Q2-2026` (fiscal quarter),
`TTM-2026Q2` (trailing twelve months ending that quarter), `spot` (a point in
time; always pass `--as-of`). Always pass `--period-end` for statement facts.

| Metric | Meaning | Typical US-GAAP XBRL tag(s) |
|---|---|---|
| revenue | Total revenue | Revenues; RevenueFromContractWithCustomerExcludingAssessedTax |
| cogs | Cost of revenue | CostOfRevenue; CostOfGoodsAndServicesSold |
| gross_profit | Gross profit | GrossProfit |
| sga | Selling, general & admin | SellingGeneralAndAdministrativeExpense |
| dna | Depreciation & amortisation | DepreciationDepletionAndAmortization; DepreciationAndAmortization |
| ebit | Operating income | OperatingIncomeLoss |
| interest_expense | Interest expense | InterestExpense; InterestExpenseNonoperating |
| pretax_income | Pre-tax income | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest |
| tax_expense | Income tax expense | IncomeTaxExpenseBenefit |
| net_income | Net income to common | NetIncomeLoss |
| cfo | Operating cash flow | NetCashProvidedByUsedInOperatingActivities |
| capex | Capital expenditure (store as positive) | PaymentsToAcquirePropertyPlantAndEquipment |
| fcf | CFO − capex (record as derived fact or use quality output) | — |
| total_assets | Total assets | Assets |
| current_assets | Current assets | AssetsCurrent |
| current_liabilities | Current liabilities | LiabilitiesCurrent |
| total_liabilities | Total liabilities | Liabilities (often absent: derive, see below) |
| long_term_debt | Non-current debt | LongTermDebtNoncurrent |
| total_debt | All borrowings incl. current portion (excl. leases unless stated) | LongTermDebt + DebtCurrent |
| cash | Cash and equivalents (+ short-term investments if stated) | CashAndCashEquivalentsAtCarryingValue |
| net_debt | total_debt − cash | derived |
| equity | Shareholders' equity (parent) | StockholdersEquity |
| minority_interest | Non-controlling interest | MinorityInterest |
| retained_earnings | Retained earnings | RetainedEarningsAccumulatedDeficit |
| receivables | Trade receivables | AccountsReceivableNetCurrent |
| ppe_net | Net PP&E | PropertyPlantAndEquipmentNet |
| securities | Short/long-term investments (Beneish AQI) | MarketableSecuritiesCurrent/Noncurrent |
| shares_outstanding | Period-end shares outstanding | dei:EntityCommonStockSharesOutstanding |
| shares_diluted | Diluted share count for valuation | WeightedAverageNumberOfDilutedSharesOutstanding |
| eps_diluted | Diluted EPS (per_share) | EarningsPerShareDiluted |
| dividends_per_share | DPS (per_share) | CommonStockDividendsPerShareDeclared |
| bvps | Book value per share (per_share) | derived |
| price | Official close (per_share, period `spot`) | exchange / vendor |
| market_cap | price × shares (period `spot`) | vendor or derived |
| fx_EURUSD etc. | FX rate, 1 FROM = x TO (`ratio`) | central bank reference rate |

## Derived facts
When a figure is not reported but follows arithmetically from reported ones
(e.g. total_liabilities = total_assets − equity − minority_interest), record it
as a fact with `--source "derived"`, the same tier as its weakest input, and
`--locator "derived: F-0003 - F-0007 - F-0008"`. Never derive from an
assumption and call it a fact.

## Scale
Filings often report in thousands or millions. Pass the number as printed with
`--scale 1000000`; the ledger stores both the printed value and the normalised
value, so a scale error is traceable.

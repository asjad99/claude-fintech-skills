# Tax-lot CSV format

One row per tax lot (each purchase, DRIP reinvestment or transfer-in is its own
lot). Positions are derived from lots; there is no "position" row.

| Column | Required | Notes |
|---|---|---|
| owner | yes | Beneficial owner. Wash-sale checks span all accounts with the same owner. |
| account | yes | Your label for the account. |
| account_type | yes | taxable, ira, roth_ira, 401k, super, isa, ... |
| lot_id | yes | Unique per row. |
| security_key | yes | The ledger key used in the research folder. |
| isin | strongly advised | Matching on tickers alone is unsafe. |
| ticker | no | For display. |
| quantity | yes | Decimal string; positive. |
| cost_basis | yes | Total cost of the lot incl. fees, in `currency`. |
| currency | yes | ISO 4217. |
| acquired | yes | YYYY-MM-DD trade date. |
| status | yes | settled or pending. Pending lots are reported, not valued as owned. |

Example:

```csv
owner,account,account_type,lot_id,security_key,isin,ticker,quantity,cost_basis,currency,acquired,status
me,BROKER-1,taxable,L1,US0378331005,US0378331005,AAPL,50,7125.00,USD,2023-01-15,settled
me,IRA-1,ira,L2,US0378331005,US0378331005,AAPL,10,1950.00,USD,2026-10-02,settled
```

Wash-sale logic implemented is the US 30-day rule as a warning. Other
jurisdictions have different rules (e.g. UK 30-day "bed and breakfasting",
Australia's anti-avoidance view of wash sales); the tool flags, a human decides.

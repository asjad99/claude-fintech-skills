# Data sources and trust tiers

| Tier | Examples | How it is used |
|---|---|---|
| primary | 10-K, 10-Q, 20-F, 40-F, 8-K, annual reports, SEC XBRL company facts, exchange official close, central-bank FX reference rates | Authoritative. Valuation inputs should be primary. |
| secondary | Data vendors and MCP connectors (e.g. FMP, Bloomberg, Refinitiv, Morningstar), aggregator sites | Cross-check and convenience. Must agree with primary within tolerance, or the break is explained. |
| tertiary | News, press releases, transcripts summaries, blogs, social posts, analyst notes | Leads only. Treat like an unauthenticated webhook: it tells you something may have happened; confirm in a primary source before recording a number. Qualitative points go in `note` entries with a URL. |

## Preferred retrieval order
1. A connected financial-data MCP server, if the user has one, for quick
   discovery (identifiers, periods, a first set of numbers). Record these as
   secondary with the tool name as `--source` and save the raw response.
2. SEC EDGAR for US filers (via WebFetch):
   - Company facts (XBRL): `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json`
     (CIK zero-padded to 10 digits)
   - Filing index: `https://data.sec.gov/submissions/CIK##########.json`
   - Filing documents: `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=...`
   EDGAR asks for a descriptive User-Agent and rate-limits aggressive use; keep
   requests few and save every response with `ledger.py raw`.
3. Non-US issuers: the company's investor-relations annual report PDF and the
   home-market regulator (e.g. ASX announcements, Companies House, SEDAR+,
   EDINET).
4. Prices: an official close from the exchange or a vendor; always `--as-of`.

## Rules
- Save the raw payload before reading numbers out of it.
- Prefer XBRL tags or table locators that someone else could find again.
- Record which filing a number came from, including amendments (10-K/A) and
  whether figures were later recast.
- Note the fiscal year end; many companies don't use December.
- Vendor "TTM" and "adjusted" figures differ by provider. Rebuild TTM from
  quarters in primary filings when it matters.
- If a source fails or returns nonsense, say so and record what is missing;
  do not fill the gap from memory.

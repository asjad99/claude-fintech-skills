# Digital assets

For crypto, stablecoins, tokenised assets, wallets and on-chain settlement.
Sources: Fintech Engineering Handbook, *Blockchain Fundamentals*, *Tokenized
Finance*, *Payment Rails* (stablecoin rails).

## Amounts and identity
- Each token defines its own decimals (often 18). Store amounts as integers
  of the smallest unit with arbitrary-width integers; 64-bit integers
  overflow.
- Identify an asset by (network, contract address or mint), not by its
  symbol; symbols collide across chains.
- A stablecoin is not its fiat currency, and a wrapped or bridged token is
  not the original. Treating them as equal invents value.

## Keys and signing
- Private keys stay out of application code and logs. Sign through a wallet
  provider, an HSM or MPC custody, with policy controls on what can be
  signed.
- Withdrawal and transfer signing gets the strongest controls: limits,
  allowlists, maker-checker approval for large or new destinations.

## Transactions
- Choose per operation between "confirmed" and "final"; credit customers only
  at the level of certainty the business accepts, and handle reorganisations
  that undo unfinalised transactions.
- Set fees and compute budgets explicitly; include replay protection
  (nonces, recent blockhash).
- Use a managed RPC provider or more than one node; cross-check important
  reads.

## Ledger and reconciliation
- Record each fiat-to-crypto conversion and each on-chain movement as
  explicit ledger entries. Reconcile your ledger against the chain; don't
  derive balances from chain data alone.
- Cross-chain movement is its own rail with its own failure modes; prefer
  native issuance or the issuer's own transfer protocol over third-party
  bridges, and build compensation for partial failure across legs.

## Smart contracts
- Guard state-changing functions against reentrancy, use role-based access
  control, use safe wrappers for external token calls, and get an external
  audit before mainnet.
- Where compliance must hold on-chain (transfer restrictions, allowlists),
  enforce it in the token or program itself, not only in the app.

## Compliance
- On- and off-ramps are regulated money transmission in most places. Link
  wallets to verified customers with KYC evidence and screen addresses before
  sending.

## Invariant tests
- Ledger balances equal on-chain balances at each reconciliation point.
- A reorganisation past the accepted depth leaves no customer credited for a
  transaction that no longer exists.

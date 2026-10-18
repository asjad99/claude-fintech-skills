# Data layer and pipelines

For schemas, stores, events, pipelines, backfills and analytics: anything
that decides where data lives and how it moves. Read with the domain packs
the work touches. Sources: Fintech Engineering Handbook, *Executing Money
Flows*, *The External World* and *Auditability*; SWEBOK Architecture,
Design 1.4, Operations 3 (data migration) and Configuration Management.

## Ownership
- Name one system of record per fact (a balance, an order, a customer's
  address). Everything else is a derived copy that can be rebuilt from it.
- Derived copies (caches, read models, search indexes, the warehouse) never
  write back to the system of record. Fixes flow through the owning service.
- One service owns each table; others read through its API or its events,
  not its database.

## Choosing a write model
- **Ledger table** (append-only entries, balances derived): the default for
  money. Simple, queryable, easy to reconcile.
- **Event sourcing** (state rebuilt from an event log): when the history of
  decisions is itself the product, or many read models need it. Costs:
  versioned events forever, snapshots, harder ad-hoc queries.
- **Mutable rows with an audit table**: for reference and configuration data
  only, never for balances. Record the choice in an ADR.

## Moving data between services
- Write the state change and the outgoing event in one transaction
  (transactional outbox), then publish from the outbox. Change data capture
  from the database log is the alternative when you can't change the writer.
- Delivery is at least once. "Exactly once" means at least once plus
  consumers that deduplicate on an event id and apply changes idempotently.
- Events carry an id, type, schema version, occurred-at, recorded-at,
  correlation id and the producer. Consumers tolerate out-of-order arrival
  (check a version or sequence) and unknown fields.

## Pipelines
- Land raw input unchanged and immutable (files, API responses, webhooks),
  then validated, then curated. Every curated row points to its raw source.
- Keep two times on each fact: when it happened (valid time) and when you
  learned it (recorded time). Late data is normal; restatements are new rows.
- Every job is rerunnable: same input, same output, no duplicates. Backfills
  run through the same code path as daily loads.
- Rejected records go to a quarantine table with a reason, never dropped.
- Row counts and control totals are checked between stages; a mismatch fails
  the run and alerts.
- Data contracts between producer and consumer: schema, types, units,
  currency and precision, freshness. Breaking changes need a new version.

## Schema change
- Every change is a versioned migration. Use expand, migrate, contract:
  add the new shape, dual-write or backfill, switch readers, then remove the
  old shape in a later release.
- Money columns are exact decimals with explicit precision and scale, or
  integer minor units, with a currency column beside them.
- Long backfills run in batches, resumable, outside the deploy.

## Privacy and retention
- Personal data lives in its own store keyed by opaque ids; financial
  records reference the id. Encrypt sensitive fields; mask them in logs and
  non-production copies.
- Erasure against an immutable ledger: delete the personal record, or
  destroy its per-subject key (crypto-shredding); the entries stay.
- Every store has a retention period and a classification in the spec.

## Analytics
- The warehouse is a read-only copy for reporting. Figures shown to
  customers, regulators or finance come from the system of record, or from a
  warehouse table reconciled to it.
- Metrics have one written definition (for example "active customer").

## Invariant tests
- Rerunning a pipeline or consumer on the same input changes nothing.
- Control totals match between raw, validated and curated stages.
- A read model rebuilt from scratch equals the live one.
- Each migration runs forward on a copy of production-shaped data, and the
  old and new application versions both work during the expand phase.

---
name: dossier
description: Produce an audit dossier for a researched security - verify the ledger hash chain and raw payloads, and summarise every fact, assumption, correction, computation, check, decision and review on file. Use when asked how a conclusion was reached, to audit or explain past research, or before relying on an old analysis.
argument-hint: "[ledger KEY]"
---

# Audit dossier

`LEDGER` = `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ledger.py" --root "${user_config.research_dir}"`

The dossier is a read-only query: it reads the record, it doesn't add to it.

1. `LEDGER verify -s KEY` — if it fails, lead with that: the record has been
   altered outside the ledger tool or a raw file is missing. Nothing after
   that point should be relied on until explained.
2. `LEDGER dossier -s KEY > dossier.json` in a scratch location and read it.
3. `LEDGER stale -s KEY --max-price-age-days ${user_config.max_price_age_days} --max-fundamentals-age-days ${user_config.max_fundamentals_age_days}`
4. Answer the four audit questions for the latest decision: what was decided,
   when, by which actor, and on what evidence (its refs, followed back to the
   raw payloads). Then list:
   - corrections (superseded entries) and their reasons
   - assumptions with the widest ranges, and which valuations depend on them
   - open or accepted reconciliation breaks
   - single-source and secondary-only inputs
   - stale facts
   - review outcome and findings
5. If the user wants it kept, write it to `${user_config.research_dir}/KEY/dossier.md`
   with every figure tagged.

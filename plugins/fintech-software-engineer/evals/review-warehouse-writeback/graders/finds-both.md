---
type: llm
focus: last_message
---
PASS if the review flags BOTH: (1) the analytics warehouse is overwriting live balances, so a derived copy writes back to the system of record (balances should be derived from ledger entries, and differences investigated or corrected with new entries, not overwritten), and (2) failed rows are silently skipped by the broad except/continue. Mentioning more issues is fine.
FAIL if either is missing.

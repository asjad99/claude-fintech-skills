---
type: llm
focus: last_message
---
PASS if the reply says posting now rejects any transaction whose debits and credits don't sum to the same amount, AND advises fixing the bad posted transaction with a new correcting or reversing entry rather than editing or deleting the original.
FAIL if either is missing, or if it suggests editing or deleting the posted entries.

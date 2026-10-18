---
type: llm
focus: last_message
---
PASS if the review flags BOTH: (1) retrying after a timeout without an idempotency key can charge the customer twice, and (2) converting through float to cents can lose or add a cent (for example int(float(amount) * 100)). Mentioning more issues is fine.
FAIL if either is missing.

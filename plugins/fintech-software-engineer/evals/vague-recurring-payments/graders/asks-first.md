---
type: llm
focus: last_message
---
PASS if the reply asks clarifying questions that would change the design before writing implementation code, covering at least two of: schedule rules, what happens when a payment fails or is retried, customer consent or mandates, duplicate prevention, payment rail or provider, currencies.
FAIL if it writes recurring-payment implementation code without asking.

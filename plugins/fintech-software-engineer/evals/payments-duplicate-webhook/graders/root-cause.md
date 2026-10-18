---
type: llm
focus: last_message
---
PASS if the reply names duplicate webhook delivery (retries) as the cause and makes the handler idempotent by recording processed event ids, so a redelivered event changes nothing.
FAIL if the fix relies only on timing, amount matching or responding faster.

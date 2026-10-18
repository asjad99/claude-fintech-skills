---
type: llm
focus: last_message
---
PASS if, before scaffolding code, the reply either asks about constraints that decide the stack (team skills, hosting or data residency, providers, compliance scope, volume) or compares at least two stack options, and in either case treats exact decimal money or database transactions as a deciding factor.
FAIL if it picks a stack without stating the trade-offs, or starts generating project files.

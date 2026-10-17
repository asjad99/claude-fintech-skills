---
type: llm
focus: last_message
---
PASS if the reply asks clarifying questions that would change the design (for example target weights or rules, thresholds, tax lots or wash sales, whether it only suggests trades) before writing implementation code.
FAIL if it writes rebalancing implementation code without asking.

---
type: llm
focus: last_message
---
PASS if the reply names the root cause as rounding each share separately without accounting for the leftover cent (floating point may also be mentioned), and says the fix makes the parts add up exactly to the total.
FAIL if it only blames floating point, or the fix could still lose or create a cent.

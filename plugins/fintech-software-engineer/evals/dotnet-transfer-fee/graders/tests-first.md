---
type: tool_order
before: { tool: Write, input_match: 'tests/[^"]*\.cs"' }
after: { tool: Write, input_match: 'src/[^"]*\.cs"' }
---

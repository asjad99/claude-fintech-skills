---
description: Approval endpoint. Expect maker-checker (approver differs from requester) and an audit record.
tags: [dotnet, compliance, build]
max_turns: 30
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, TodoWrite]
---

Add an admin API endpoint in C# that approves pending withdrawal requests. Put it under src/ with xUnit tests under tests/. Keep it framework-light. You can't run dotnet here, so just write the files.

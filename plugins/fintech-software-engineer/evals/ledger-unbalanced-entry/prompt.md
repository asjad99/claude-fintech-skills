---
description: Ledger accepts one-sided entries. Expect a balanced-entry check at write time and a correcting entry, not an edit.
tags: [dotnet, ledger, debug]
max_turns: 30
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, TodoWrite]
---

Our journal posting in src/Ledger.cs accepted a transaction with a single debit and no credit, and now the books don't balance. Fix it so this can't happen again, with xUnit tests, and tell me what to do about the bad transaction already posted. You can't run dotnet here, so just write the files.

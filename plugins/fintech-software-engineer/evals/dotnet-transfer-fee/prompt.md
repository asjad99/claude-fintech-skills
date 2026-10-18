---
description: New C# money calculation. Expect decimal money, tests before code, input contracts, honest report.
tags: [dotnet, core, build]
max_turns: 30
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, TodoWrite]
---

Add a TransferFeeCalculator in C#: the fee is 0.5% of the transfer amount, with a minimum of 1.00 and a maximum of 25.00 in the account's currency. Include xUnit tests. Put source under src/ and tests under tests/. You can't run dotnet in this environment, so just write the files.

---
name: review
description: Independent review of a code change before it is called done - spec compliance, standards and fintech risk - carried out by the code-reviewer agent. Use after build or debug, before a commit or pull request, or when asked to review a branch or diff.
argument-hint: "[base ref, default main]"
---

# Review

The builder doesn't grade its own work: the `code-reviewer` agent does, from
the spec and the diff alone.

1. **Pin the diff.** Base = the argument, else `main`. Confirm
   `git diff <base>...HEAD` plus uncommitted changes is not empty. Find the
   spec in `docs/specs/` or the one-line criterion, and note which domains
   the diff touches.
2. **Green baseline.** Run the full tests, linter and type checks.
   Done when all pass, or the failures are listed for the reviewer.
3. **Delegate.** Launch the `code-reviewer` agent with only: the base ref, the
   spec path or criterion, the domains touched, and the check commands. Leave
   out your reasoning and how you built it.
4. **Act on findings.** Fix each blocking finding through the `build` loop
   (a failing test first when it is a behaviour bug). Fix or note each
   should-fix. When anything blocking changed, review again.
   Done when the reviewer reports no blocking findings, or the user has
   accepted each remaining one.
5. **Report.** Findings, what was fixed, what was accepted and why.

Sources: SWEBOK Quality and Security; Fintech Engineering Handbook (Controls
and Access: maker-checker for code); two-axis review after mattpocock/skills
`code-review`, silent-failure checks after Anthropic's `pr-review-toolkit`,
spec-then-quality review after obra/superpowers.

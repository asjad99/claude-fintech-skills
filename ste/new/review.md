# Review

The agent that builds a change does not examine its own work. The
`code-reviewer` agent examines it, with only the spec and the diff.

1. **Identify the diff.** Use the argument as the base reference. If there is
   no argument, use `main`. Make sure that `git diff <base>...HEAD` and the
   uncommitted changes are not empty. Find the spec in `docs/specs/` or the
   one-line criterion. Identify the domains that the diff has an effect on.
2. **Green baseline.** Run the full tests, the linter and the type checks.
   This step is complete when all checks pass, or when you have a list of the
   failures for the reviewer.
3. **Delegate.** Start the `code-reviewer` agent. Give it only these items:
   - the base reference
   - the spec path or the criterion
   - the domains of the diff
   - the check commands

   Do not tell the agent why or how you built the change.
4. **Correct the findings.** Fix each blocking finding through the `build`
   loop. If the finding is a behaviour bug, write a test that fails first.
   Fix each should-fix finding, or record it. If you changed code because of
   a blocking finding, do the review again.
   This step is complete when one of these conditions is true:
   - The reviewer reports no blocking findings.
   - The user accepts each blocking finding that is not fixed.
5. **Report.** Give the findings and the fixes. For each finding that the
   user accepted, give the reason.

@@SOURCES@@

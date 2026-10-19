# Ship

Use the normal pull request and CI path of the repo. Ask the user before you
run a command that rewrites shared history, deletes data or deploys to
production.

1. **Green.** Make sure that the `review` skill passed. Make sure that the
   full suite passes on the exact commit that you ship (in CI or locally).
2. **Change trail.** Make sure that these conditions are true:
   - The commit refers to its spec or ticket.
   - The pull request has a description and an approval from a reviewer who
     is not the author.
   - The build that makes the artifact records the commit SHA.
3. **Version and changelog.** Increase the version in the same way as the
   repo does (SemVer by default). In the changelog entry, make a list of the
   changes that users can see, with their spec IDs.
4. **Data changes.** Make sure that the migrations are in the code. Make sure
   that they ran against realistic data, and that each one has a rollback or
   a written forward-fix. Ship a destructive change in steps:
   1. Add the new shape.
   2. Migrate.
   3. Remove the old shape in a later release.
5. **Configuration.** Document each new configuration value with its default. Get
   secrets from the environment or a vault. Make sure that there are no
   secrets in the repo or the logs.
6. **Operability.** Make sure that each new money flow has these items:
   - a kill switch
   - structured logs with correlation IDs
   - a metric or alert
   - a reconciliation check

   Data pipelines must also have a freshness check.
7. **Runbook.** For new money flows, write these items:
   - how to stop the flow
   - how to find if money is duplicated, lost or recorded against the wrong
     party
   - who to tell (also each regulator that applies, with its deadline and an owner)
8. **Rollback.** Write the steps to return to the previous version. Include
   what occurs to migrated data and to operations that are in progress. Put
   behaviour that has risk behind a flag.
9. **Release.** Tag the commit, publish the release notes and make sure that
   the deployment is healthy.

This skill is complete when each step above has its evidence in the release
notes or the pull request. The evidence is command output, a file or a link.

@@SOURCES@@

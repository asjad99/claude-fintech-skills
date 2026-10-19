---
name: ship
description: Prepare a reviewed change for release - version, changelog, migrations, configuration, kill switches, monitoring, runbook and a written rollback path. Use when merging to main, cutting a release or deploying.
argument-hint: "[version or environment]"
---

# Ship

Use the repo's normal pull request and CI path. Ask the user before any
command that rewrites shared history, deletes data or deploys to production.

1. **Green.** The `review` skill passed and the full suite passes on the
   exact commit being shipped (CI or local).
2. **Change trail.** The commit references its spec or ticket, the pull
   request has a description and an approving reviewer who is not the
   author, and the build that produces the artifact records the commit SHA.
3. **Version and changelog.** Bump the version the way the repo does
   (SemVer by default). The changelog entry lists user-visible changes with
   their spec ids.
4. **Data changes.** Migrations live in code, have run against realistic data,
   and have a rollback or a written forward-fix. A destructive change ships in
   steps: add the new shape, migrate, then remove the old one in a later
   release.
5. **Configuration.** New settings are documented with defaults; secrets come
   from the environment or a vault; nothing secret is in the repo or the logs.
6. **Operability.** Each new money flow has a kill switch, structured logs
   with correlation ids, a metric or alert, and a reconciliation check. Data
   pipelines also have a freshness check.
7. **Runbook.** For new money flows: how to halt the flow, how to tell whether
   money was duplicated, dropped or misattributed, and who to notify
   (including any regulator, with its deadline and an owner).
8. **Rollback.** Write the steps to return to the previous version, including
   what happens to migrated data and in-flight operations. Put risky
   behaviour behind a flag.
9. **Release.** Tag, publish release notes, confirm the deployment is healthy.

Done when each step above has its evidence (command output, file or link)
in the release notes or pull request.

Sources: SWEBOK Operations 3 (deployment, rollback, data migration) and
Configuration Management; Fintech Engineering Handbook (Controls and Access:
the change trail; Observability; Incident Response); evidence-before-done
after obra/superpowers `verification-before-completion`.

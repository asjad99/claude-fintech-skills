---
name: ship
description: Prepare a reviewed change for release - version, changelog, migrations, configuration, monitoring and a written rollback path. Use when merging to main, cutting a release or deploying.
argument-hint: "[version or environment]"
---

# Ship

Use the repo's normal pull request and CI path. Ask the user before any
command that rewrites shared history, deletes data or deploys to production.

1. **Green.** The `review` skill passed and the full suite passes on the
   exact commit being shipped (CI or local).
2. **Version and changelog.** Bump the version the way the repo does
   (SemVer by default). The changelog entry lists user-visible changes with
   their spec ids.
3. **Data changes.** Migrations live in code, have run against realistic data,
   and have a rollback or a written forward-fix. A destructive change ships in
   steps: add the new shape, migrate, then remove the old one in a later
   release.
4. **Configuration.** New settings are documented with defaults; secrets come
   from the environment or a vault; nothing secret is in the repo or the logs.
5. **Operability.** The new path has a health check, structured logs and a
   metric or alert; data pipelines also have a freshness check.
6. **Rollback.** Write the steps to return to the previous version, including
   what happens to migrated data. Put risky behaviour behind a flag.
7. **Release.** Tag, publish release notes, confirm the deployment is healthy.

Done when each step above has its evidence (command output, file or link)
in the release notes or pull request.

Sources: SWEBOK Operations 3 (deployment, rollback, data migration) and
Configuration Management (versioning, release); evidence-before-done after
obra/superpowers `verification-before-completion`.

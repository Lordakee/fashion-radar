# Claude Code Stage 50 Plan Review Prompt

Review the Stage 50 design and implementation plan in `/home/ubuntu/fashion-radar`:

- `docs/superpowers/specs/2026-06-16-stage-50-community-signal-producer-profile-design.md`
- `docs/superpowers/plans/2026-06-16-stage-50-community-signal-producer-profile-plan.md`

Objective: add a local, print-only Community Signal Producer Profile so
external user-controlled tools can discover the exact Fashion Radar community
signal CSV/JSON handoff contract before writing sanitized files.

Architecture and tech stack:

- New focused Python module:
  `src/fashion_radar/community_signal_profile.py`
- Pydantic v2 model for deterministic JSON output.
- Table renderer for human-readable output.
- Typer CLI command:
  `fashion-radar community-signal-profile --format table|json`
- Tests with pytest and existing `CliRunner` patterns.
- Docs and package archive checks updated.
- No dependency or `uv.lock` changes.

Implementation method:

1. Write failing profile/model tests that bind the profile to the checked-in CSV
   header, strict JSON schema, allowed fields, prohibited fields, example JSON,
   renderer output, and boundaries.
2. Implement the profile module and example JSON.
3. Write failing CLI tests for help, table output, JSON output, and no local
   artifacts.
4. Register the Typer command.
5. Update docs, CLI docs drift tests, GitHub upload checklist help loop, package
   archive requirements, and changelog.
6. Run focused and full verification.
7. Submit the completed diff for Claude Code release review before commit/push.

Hard boundaries:

- Do not add scraping, crawling, browser automation, account/session/cookie
  handling, platform APIs, monitoring, watch folders, scheduler behavior, source
  acquisition, database writes, report writes, dashboard state, new import
  formats, metadata sidecars, platform-specific adapters, or compliance-review
  functionality.
- The new command must print only. It should not accept path/config/data/report
  arguments, read handoff files, create directories, open SQLite, or call the
  network.
- Critical and Important planning findings must be fixed before implementation.

Please return:

- Critical findings
- Important findings
- Minor findings
- Missing tests or verification gaps
- Scope creep risks
- Approval status for implementation

Review only the current uncommitted Stage 64 diff in /home/ubuntu/fashion-radar.

Do not run package resolution commands. Do not run `uv run` without
`--no-config --frozen`. Prefer read-only commands: `git diff`, `rg`, and
targeted file reads.

Stage 64 adds `fashion-radar external-tool-workflow`.

Must-hold requirements:
- Local/stdout-only/print-only command.
- JSON output is workflow metadata, not importable handoff rows.
- `external-tool-template --format json/csv` remains responsible for importable
  handoff examples.
- Default adapter is `generic_community_export`.
- The command must not execute generated commands, read/inspect directories,
  read handoff files, validate rows, import rows, open SQLite, create artifacts,
  collect from platforms, schedule jobs, rank trends, prove demand, or add a
  compliance-review product feature.
- Docs/tests must not leak real tokens or persist mirror/index URLs.

Check only for release-blocking Critical/Important issues. Ignore Minor issues.
Return exactly:
- Verdict: APPROVED FOR STAGE 64 RELEASE or CHANGES REQUIRED
- Critical:
- Important:
- Rationale:

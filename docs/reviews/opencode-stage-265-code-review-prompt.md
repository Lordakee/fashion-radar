Review the current uncommitted Stage 265 release candidate in /home/ubuntu/fashion-radar.

Scope:
- New print-only ROW ONE local daily ops runbook helper under `fashion_radar.row_one.ops`.
- New `fashion-radar row-one local-ops` CLI command.
- First-run smoke coverage for `row-one local-ops --help` and the runbook output.
- Package archive guardrail for `src/fashion_radar/row_one/ops.py`.
- ROW ONE/CLI/upload docs for fixed IP:port local serving, 04:00 refresh snippets, and latest-only cleanup.

Constraints:
- Do not edit files.
- Verify no `row-one-app/v1` JSON contract drift.
- Verify no source collection, scoring/ranking, scheduling semantic change, scraping, connector, timer installation, server startup, SQLite read, site build, or file mutation was added by `local-ops`.
- Focus on release blockers, correctness risks, missing tests, package/archive issues, docs/CLI inconsistencies, and import cycles.
- Return concise Critical / Important / Minor findings and a verdict.

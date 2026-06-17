Review the current uncommitted Stage 64 changes in /home/ubuntu/fashion-radar.

Context:
- Stage 64 adds `fashion-radar external-tool-workflow`.
- The command must be local, stdout-only, and print-only.
- JSON output is workflow metadata, not importable handoff row JSON.
- `external-tool-template --format json/csv` remains responsible for importable
  example handoff rows.
- The command must not read export directories, import data, touch SQLite,
  execute generated commands, collect from platforms, schedule jobs, verify
  coverage, rank trends, prove demand, or add a compliance-review product
  feature.
- Default adapter should be `generic_community_export`.
- The workflow should be deterministic and based on static external-tool
  adapter registry metadata.

Review scope:
- `src/fashion_radar/external_tool_workflow.py`
- `src/fashion_radar/cli.py`
- `scripts/check_first_run_smoke.py`
- related tests under `tests/`
- related docs under `README.md`, `AGENTS.md`, `CHANGELOG.md`, and `docs/`

Check only for Critical or Important issues:
1. Scope or side-effect regressions.
2. CLI/API contract mismatches.
3. Tests that pass while missing a key requirement above.
4. Docs that would mislead users into treating workflow JSON as importable rows.
5. Token/credential leakage or persisted mirror/index URLs.
6. Packaging or first-run smoke gaps likely to break a fresh install.

Return exactly:
- Verdict: APPROVED FOR STAGE 64 RELEASE or CHANGES REQUIRED
- Critical:
- Important:
- Minor:
- Rationale:

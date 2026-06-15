# Claude Code Stage 50 Plan Rereview Prompt

Re-review the Stage 50 design and implementation plan in
`/home/ubuntu/fashion-radar`:

- `docs/superpowers/specs/2026-06-16-stage-50-community-signal-producer-profile-design.md`
- `docs/superpowers/plans/2026-06-16-stage-50-community-signal-producer-profile-plan.md`

This rereview follows
`docs/reviews/claude-code-stage-50-plan-review.md`.

The prior Important findings were addressed as follows:

1. The docs plan now explicitly requires
   `docs/community-signal-import.md` to mention
   `examples/community-signal-profile.example.json`.
2. The CLI test plan now includes a real subprocess check from a temporary cwd
   with `FASHION_RADAR_CONFIG_DIR`, `FASHION_RADAR_DATA_DIR`, and
   `FASHION_RADAR_REPORTS_DIR` set, followed by artifact assertions.
3. The profile test plan now includes Pydantic strictness checks:
   extra top-level fields fail, missing required model fields fail, and the
   generated model JSON schema has `additionalProperties: false`.
4. The commit step now clarifies that Claude Code is a read-only reviewer and
   Codex performs the commit, so a Claude Code co-author trailer should not be
   added unless a current repo or user instruction explicitly requires one.

Additional hardening added after read-only subagent feedback:

- The profile shape includes `execution_mode`, `schema_path`,
  `example_paths`, `field_rules`, and structured `unsupported_capabilities`.
- Tests verify the profile JSON is not shaped like an import file and is
  rejected by `lint_community_signal_file(..., input_format="json")` as
  `invalid_file`.
- Tests verify `source_weight` bounds and default match the existing schema and
  `ManualSignalRow`.
- CLI help tests assert the command exposes `--format` but not path/config/data,
  import, or handoff file controls.
- CLI guard tests monkeypatch filesystem iteration, subprocess, SQLite, import,
  collection, and report helpers to fail while the profile command still exits
  zero.

Hard boundaries remain:

- Do not add scraping, crawling, browser automation, account/session/cookie
  handling, platform APIs, monitoring, watch folders, scheduler behavior, source
  acquisition, database writes, report writes, dashboard state, new import
  formats, metadata sidecars, platform-specific adapters, or compliance-review
  functionality.
- The new command must print only. It should not accept path/config/data/report
  arguments, read handoff files, create directories, open SQLite, or call the
  network.

Please return:

- Critical findings
- Important findings
- Minor findings
- Missing tests or verification gaps
- Scope creep risks
- Approval status for implementation

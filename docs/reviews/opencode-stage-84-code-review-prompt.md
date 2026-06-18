# Stage 84 Code Review Prompt

Review the Stage 84 changes in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Stage 84 should make the GitHub upload checklist installed-wheel smoke include
the `external-tool-readiness --adapter instaloader --format table` command it
already claims to cover, and tighten docs drift coverage for both exact
installed-path table and JSON readiness smoke commands.

## Intended Scope

Allowed changed files:

- `docs/github-upload-checklist.md`
- `tests/test_cli_docs.py`
- Stage 84 spec/plan/review artifacts under `docs/superpowers/` and
  `docs/reviews/`

Out of scope:

- Runtime code under `src/`
- Dependency manifests
- `uv.lock`
- CI workflows
- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`

## Requirements

- The installed-wheel smoke block must include:
  - `"$tmp_env/venv/bin/fashion-radar" external-tool-readiness --help`
  - `"$tmp_env/venv/bin/fashion-radar" external-tool-readiness --adapter instaloader --format table`
  - `"$tmp_env/venv/bin/fashion-radar" external-tool-readiness --adapter instaloader --format json`
  - `"$tmp_env/venv/bin/fashion-radar" external-tool-readiness --adapter rednote_mcp --format json`
- The table command should appear after `--help` and before the JSON
  `instaloader` command.
- `test_external_tool_readiness_upload_checklist_help_loop_and_smoke` must
  assert exact installed-path `instaloader` table and JSON commands.
- Existing assertions for the help loop, exact `--help`, `rednote_mcp`, and
  `scripts/check_first_run_smoke.py` should remain.
- No runtime behavior, source/platform acquisition, scraping, connector,
  browser/API/login/cookie/session/token, media download, monitoring,
  scheduling, demand proof, ranking, coverage verification, or compliance
  product behavior should be added.

## Review Instructions

Return findings first, ordered by severity. Classify each finding as Critical,
Important, or Minor. Include file and line references. If there are no
Critical or Important findings, say that explicitly.

# Claude Code Stage 50 Release Review Prompt

Review the current Stage 50 working-tree diff in `/home/ubuntu/fashion-radar`.

Objective: add a print-only `community-signal-profile` command and example JSON
producer contract for external user-controlled tools that generate sanitized
community signal CSV/JSON handoff files.

Changed areas:

- New profile module:
  `src/fashion_radar/community_signal_profile.py`
- CLI command:
  `fashion-radar community-signal-profile --format table|json`
- Tests:
  `tests/test_community_signal_profile.py`,
  `tests/test_cli.py`,
  `tests/test_community_signal_import_contract.py`,
  `tests/test_cli_docs.py`,
  `tests/test_package_archives.py`
- Example:
  `examples/community-signal-profile.example.json`
- Docs and packaging:
  `README.md`, `CHANGELOG.md`,
  `docs/community-signal-import.md`,
  `docs/community-signal-quality.md`,
  `docs/cli-reference.md`,
  `docs/source-boundaries.md`,
  `docs/architecture.md`,
  `docs/github-upload-checklist.md`,
  `scripts/check_package_archives.py`

Hard boundaries:

- No scraping, crawling, browser automation, account/session/cookie handling,
  platform APIs, monitoring, watch folders, scheduler behavior, source
  acquisition, database writes, report writes, dashboard state, new import
  formats, metadata sidecars, platform-specific adapters, or compliance-review
  functionality.
- The command itself must print only and expose only `--format`; it should not
  accept path/config/data/report arguments, read handoff files, create
  directories, open SQLite, call subprocesses, or call the network.
- It is acceptable for the printed profile content to include copyable
  downstream local commands with path/config/data options as strings, as long as
  the profile command does not execute or validate them.
- Critical and Important findings must be fixed before commit/push.

Verification already run in this workspace:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_community_signal_profile.py tests/test_community_signal_import_contract.py tests/test_cli.py::test_community_signal_profile_help_lists_format tests/test_cli.py::test_community_signal_profile_prints_table tests/test_cli.py::test_community_signal_profile_prints_json tests/test_cli.py::test_community_signal_profile_json_is_deterministic_across_env_and_cwd tests/test_cli.py::test_community_signal_profile_does_not_create_project_artifacts tests/test_cli.py::test_community_signal_profile_does_not_run_side_effect_helpers tests/test_cli.py::test_community_signal_profile_real_process_does_not_create_artifacts tests/test_cli.py::test_community_signal_profile_invalid_format_exits_without_artifacts tests/test_cli.py::test_community_signal_profile_rejects_unexpected_path_without_artifacts tests/test_cli_docs.py tests/test_package_archives.py -q
UV_NO_CONFIG=1 uv run pytest -q
UV_NO_CONFIG=1 uv run ruff check .
UV_NO_CONFIG=1 uv run ruff format --check .
UV_NO_CONFIG=1 uv lock --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
"$tmp_env/venv/bin/python" -m pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple "$tmp_build"/*.whl
"$tmp_env/venv/bin/fashion-radar" community-signal-profile --format json
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
git diff --check
git diff --quiet -- uv.lock
```

Observed results:

- Focused Stage 50 selection: `74 passed`.
- Full pytest: `797 passed`.
- Ruff check and format check: passed after formatting.
- Lock check and `uv.lock` unchanged check: passed.
- Mirror sync and no-config sync check: passed.
- Release hygiene: passed.
- First-run smoke: passed.
- Build/package archive check: passed.
- Installed-wheel `community-signal-profile --format json` parsed as JSON and
  created no config/data/report/SQLite/report/digest artifacts in a temp cwd.
- Installed-wheel first-run smoke: passed.
- Two read-only xhigh reviewers also approved code/tests and docs/package
  boundaries with no findings.

Please return:

- Critical findings
- Important findings
- Minor findings
- Test/verification gaps
- Approval status for Stage 50 commit and push

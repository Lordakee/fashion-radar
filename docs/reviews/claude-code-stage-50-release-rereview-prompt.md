# Claude Code Stage 50 Release Rereview Prompt

Re-review the current Stage 50 working-tree diff in
`/home/ubuntu/fashion-radar`.

This follows `docs/reviews/claude-code-stage-50-release-review.md`, which
approved Stage 50 and noted one Minor gap: no direct drift test comparing
`examples/community-signal-profile.example.json` to the generated profile.

Follow-up change:

- `tests/test_community_signal_profile.py` now includes:
  - JSON-equivalent comparison between
    `examples/community-signal-profile.example.json` and
    `build_community_signal_profile().model_dump(mode="json")`;
  - byte-for-byte formatting comparison against
    `build_community_signal_profile().model_dump_json(indent=2) + "\n"`.

Fresh verification after the follow-up change:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_community_signal_profile.py tests/test_community_signal_import_contract.py tests/test_cli.py::test_community_signal_profile_help_lists_format tests/test_cli.py::test_community_signal_profile_prints_table tests/test_cli.py::test_community_signal_profile_prints_json tests/test_cli.py::test_community_signal_profile_json_is_deterministic_across_env_and_cwd tests/test_cli.py::test_community_signal_profile_does_not_create_project_artifacts tests/test_cli.py::test_community_signal_profile_does_not_run_side_effect_helpers tests/test_cli.py::test_community_signal_profile_real_process_does_not_create_artifacts tests/test_cli.py::test_community_signal_profile_invalid_format_exits_without_artifacts tests/test_cli.py::test_community_signal_profile_rejects_unexpected_path_without_artifacts tests/test_cli_docs.py tests/test_package_archives.py -q
UV_NO_CONFIG=1 uv run pytest -q
UV_NO_CONFIG=1 uv run ruff check .
UV_NO_CONFIG=1 uv run ruff format --check .
git diff --check
git diff --quiet -- uv.lock
```

Observed results:

- Focused Stage 50 selection: `76 passed`.
- Full pytest: `799 passed`.
- Ruff check and format check: passed.
- Diff whitespace and `uv.lock` unchanged checks: passed.

Hard boundaries remain:

- The new command must remain print-only and expose only `--format`.
- No scraping, crawling, browser automation, account/session/cookie handling,
  platform APIs, monitoring, source acquisition, database writes, report writes,
  dashboard state, new import formats, metadata sidecars, platform-specific
  adapters, or compliance-review functionality.

Please return:

- Critical findings
- Important findings
- Minor findings
- Approval status for Stage 50 commit and push

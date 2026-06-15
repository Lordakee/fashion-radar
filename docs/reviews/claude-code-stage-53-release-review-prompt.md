Review completed Stage 53 community handoff guardrails in
`/home/ubuntu/fashion-radar`.

Stage objective:

- Add test/docs guardrails around the existing local community handoff contract.
- Keep the stage test/docs-only; no production behavior change was intended.
- Do not add scraping, crawling, browser automation, account login,
  cookies/sessions, platform APIs, source acquisition, scheduling, monitoring,
  media download, connector code, or a compliance-review feature.

Changed files expected in the release diff:

- `tests/test_community_signal_lint.py`
- `tests/test_community_signal_profile.py`
- `tests/test_cli.py`
- `tests/test_cli_docs.py`
- `docs/community-signal-import.md`
- `CHANGELOG.md`
- `docs/superpowers/specs/2026-06-16-stage-53-community-handoff-guardrails-design.md`
- `docs/superpowers/plans/2026-06-16-stage-53-community-handoff-guardrails-plan.md`
- `docs/reviews/claude-code-stage-53-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-53-plan-review.md`
- `docs/reviews/claude-code-stage-53-plan-rereview-prompt.md`
- `docs/reviews/claude-code-stage-53-plan-rereview.md`
- this prompt and the review output file.

Verification already run:

- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_community_signal_lint.py tests/test_community_signal_profile.py tests/test_cli_docs.py::test_community_signal_import_doc_keeps_profile_recommended_command_order tests/test_cli.py::test_community_candidates_dir_invalid_output_format_does_not_enter_command_body -q`
  - `95 passed`
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest -q`
  - `880 passed`
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check .`
  - all checks passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check .`
  - 108 files already formatted
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check`
  - resolved 84 packages
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv sync --locked --dev --check`
  - would make no changes
- `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check`
  - would make no changes
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .`
  - release hygiene checks passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .`
  - first-run sample smoke passed
- Package build/archive/installed-wheel smoke:
  - `uv build --out-dir "$tmp_build"` succeeded
  - `scripts/check_package_archives.py "$tmp_build"` passed
  - installed wheel `fashion-radar --help` passed
  - installed wheel `python -m fashion_radar --help` passed
  - installed-wheel `scripts/check_first_run_smoke.py --installed` passed

Also verify:

- `uv.lock` is not modified and does not enter the Stage 53 diff.
- The prohibited-field lint tests exercise every
  `PROHIBITED_COMMUNITY_SIGNAL_FIELDS` member for CSV and supported JSON row
  envelopes.
- The producer profile recommended-command test validates useful command
  semantics without overfitting to prose docs.
- `community-candidates-dir --format xml` is rejected before command body work.
- The docs drift test is scoped to the relevant community import flow.
- Documentation/changelog wording is accurate.

Report Critical, Important, and Minor findings. Treat Critical/Important as
blocking before commit/upload. If there are no Critical or Important findings,
say so explicitly.

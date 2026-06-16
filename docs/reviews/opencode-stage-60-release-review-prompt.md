You are reviewing Stage 60 of the fashion-radar repository.

Model requirement for this review: zhipuai-coding-plan/glm-5.2.

Review target:
- Repository: /home/ubuntu/fashion-radar
- Base commit: bf5cf5cfe15e5a3bab1eec718253cc2bbf6f160f
- Review the current working tree diff relative to that base commit.

Stage 60 objective:
- Add the existing read-only `imported-candidates` command to the print-only `imported-review-workflow`.
- The new step must be named `review_imported_candidate_phrases`.
- The new step must be read-only.
- The new step command must be:
  `fashion-radar imported-candidates --config-dir <config_dir> --data-dir <data_dir> --as-of <as_of> [--source-name <source_name>]`.
- The final workflow step must remain `review_local_heat_movers`.
- The final heat step must not include `--source-name`.
- The workflow builder must remain print-only and must not load configs, open SQLite, inspect paths, call `query_imported_candidates`, run subprocesses, or create artifacts.

Out of scope:
- No new CLI command or workflow option.
- No new connector, scraper, platform API, account/session/cookie/browser automation, monitoring, scheduling, schema/migration, dependency, report/dashboard/digest write, or compliance/legal/safety-review product feature.

Plan review:
- `docs/reviews/opencode-stage-60-plan-review.md`
- Verdict: APPROVED FOR STAGE 60 PLAN
- No Critical or Important findings after the plan was corrected.

Verification already run:
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_imported_review_workflow.py tests/test_cli.py tests/test_cli_docs.py tests/test_first_run_smoke.py -q -k "imported_review_workflow or first_run_smoke or cli_docs"` -> 87 passed, 245 deselected
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check src/fashion_radar/imported_review_workflow.py tests/test_imported_review_workflow.py tests/test_cli.py tests/test_cli_docs.py tests/test_first_run_smoke.py scripts/check_first_run_smoke.py` -> passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check src/fashion_radar/imported_review_workflow.py tests/test_imported_review_workflow.py tests/test_cli.py tests/test_cli_docs.py tests/test_first_run_smoke.py scripts/check_first_run_smoke.py` -> passed
- `git diff --check` -> passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest -q` -> 974 passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check .` -> passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check .` -> passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check` -> passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv sync --locked --dev --check` -> passed
- `env -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check` -> passed
- `rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock` -> no matches
- `git diff --exit-code -- uv.lock pyproject.toml` -> passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .` -> passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .` -> passed
- Package archive build and `scripts/check_package_archives.py` -> passed
- Installed-wheel first-run smoke -> passed
- Installed-wheel `imported-review-workflow --format json` smoke -> passed, including `step_count == 6`, step 4 `review_imported_candidate_phrases`, and final `review_local_heat_movers` without `--source-name`.
- Installed-wheel checklist snippet now uses `"$tmp_env/venv/bin/python" - "$tmp_run/imported-review-workflow.json" <<'PY'`, and `tests/test_cli_docs.py` now asserts that exact shape.

Please review for:
1. Critical or Important correctness issues in the implementation or tests.
2. Any accidental scope expansion beyond the Stage 60 objective.
3. Any documentation claims that drift from the implemented behavior.
4. Any release hygiene risk that should block commit/push.

Return exactly:
- Verdict: APPROVED FOR STAGE 60 RELEASE or CHANGES REQUIRED
- Findings grouped by severity: Critical, Important, Minor
- If approved, include one concise rationale.

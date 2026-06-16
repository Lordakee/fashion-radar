You are reviewing the current Stage 61 implementation diff for the fashion-radar repository.

Model requirement for this review: zhipuai-coding-plan/glm-5.2.

Review target:
- Repository: /home/ubuntu/fashion-radar
- Base commit: 403d092899d9f1ae27c8d3f4a1dba7cfbdd1d36f
- Review the current working tree diff relative to that base commit.

Stage 61 objective:
- Add the existing local-only `community-handoff-check-dir` command as a read-only readiness report step inside the existing print-only `community-handoff-workflow`.
- The new step must be named `review_handoff_readiness`.
- The new step must be read-only.
- The new step must appear at step 3, before `dry_run_directory_import`.
- The new step command must be:
  `fashion-radar community-handoff-check-dir <directory> --input-format <format> --pattern <pattern> --config-dir <config_dir> --as-of <as_of> --source-name <source_name> --strict`.
- The dry-run step must remain read-only and move to step 4.
- The import step must remain `updates_local_imports` and move to step 5.
- The post-import review step must remain `print_only` and move to step 6.
- The workflow builder must remain print-only and must not inspect directories, read configs, open SQLite, run subprocesses, call `check_community_handoff_directory()`, import rows, or create artifacts.
- The embedded manifest workflow must reflect the same six-step ordering because it reuses `build_community_handoff_workflow()`.

Out of scope:
- No new CLI command or workflow option.
- No new connector, scraper, platform API, account/session/cookie/browser automation, monitoring, scheduling, source acquisition, schema/migration, dependency, report/dashboard/digest write, or compliance/legal/safety-review product feature.

Verification already run:
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest -q` -> 979 passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check .` -> passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check .` -> passed
- `git diff --check` -> passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check` -> passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv sync --locked --dev --check` -> passed
- `env -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check` -> passed
- `rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock` -> no matches
- `git diff --exit-code -- uv.lock pyproject.toml` -> passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .` -> passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .` -> passed
- Package archive build/check, installed-wheel first-run smoke, and installed-wheel `community-handoff-workflow` JSON smoke -> passed, including `step_count == 6`, step 3 `review_handoff_readiness`, and final `print_post_import_review`.

Please review for:
1. Critical or Important correctness issues in the implementation or tests.
2. Any accidental scope expansion beyond the Stage 61 objective.
3. Any documentation claims that drift from the implemented behavior.
4. Any release hygiene risk that should block commit/push.

Return exactly:
- Verdict: APPROVED FOR STAGE 61 RELEASE or CHANGES REQUIRED
- Findings grouped by severity: Critical, Important, Minor
- If approved, include one concise rationale.

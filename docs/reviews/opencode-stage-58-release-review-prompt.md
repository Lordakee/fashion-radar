You are reviewing Stage 58 of the fashion-radar repository.

Model requirement for this review: zhipuai-coding-plan/glm-5.2.

Review target:
- Repository: /home/ubuntu/fashion-radar
- Base commit: aa1f55a5b57925742a33d8b617112666df1558cf
- Review the current working tree diff relative to that base commit.

Stage 58 objective:
- Extend the existing print-only `imported-review-workflow` with one final local read-only heat movement review step.
- The final step must run `fashion-radar heat-movers --config-dir <config_dir> --data-dir <data_dir> --as-of <as_of>`.
- The final step must be named `review_local_heat_movers`.
- The final step must have `suggested_effect == "read_only"`.
- The final step must not include `--source-name`.
- The workflow should now report 5 steps.

Allowed scope:
- `src/fashion_radar/imported_review_workflow.py`
- `tests/test_imported_review_workflow.py`
- `tests/test_cli.py`
- `tests/test_cli_docs.py`
- Documentation updates that describe the new final heat-movers review step.
- Stage 58 planning/review documentation.

Out of scope:
- No new source acquisition, scraping, API connector, account/cookie/session/browser automation, scheduling, monitoring, schema migration, dependency change, dashboard write, digest write, or platform coverage verification.
- Do not request compliance/legal/safety review functionality. This project intentionally does not add such product features in this node.

Verification already run:
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_imported_review_workflow.py tests/test_cli.py tests/test_cli_docs.py -q` -> 292 passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check src/fashion_radar/imported_review_workflow.py tests/test_imported_review_workflow.py tests/test_cli.py tests/test_cli_docs.py` -> passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check src/fashion_radar/imported_review_workflow.py tests/test_imported_review_workflow.py tests/test_cli.py tests/test_cli_docs.py` -> passed
- `git diff --check` -> passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest -q` -> 968 passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check .` -> passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check .` -> passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check` -> passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv sync --locked --dev --check` -> passed
- `env -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check` -> passed
- `rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock` -> no matches
- `git diff --exit-code -- uv.lock pyproject.toml` -> passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .` -> passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .` -> passed
- Installed-wheel smoke for `fashion-radar imported-review-workflow --format json` -> passed, including 5 steps and final `review_local_heat_movers`.

Post-review minor cleanup already applied:
- `docs/architecture.md` sentence flow was adjusted so the `imported-candidate-evidence` sentence is no longer split by the Stage 58 `heat-movers` sentence.
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q -k "imported_review_workflow_docs or heat_movers"` -> 6 passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check .` -> passed
- `git diff --check` -> passed

Please review for:
1. Critical or Important correctness issues in the implementation or tests.
2. Any accidental scope expansion beyond the Stage 58 objective.
3. Any documentation claims that drift from the implemented behavior.
4. Any release hygiene risk that should block commit/push.

Return exactly:
- Verdict: APPROVED FOR STAGE 58 RELEASE or CHANGES REQUIRED
- Findings grouped by severity: Critical, Important, Minor
- If approved, include one concise rationale.

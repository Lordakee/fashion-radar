Review the uncommitted Stage 314 implementation in `/home/ubuntu/fashion-radar`.

Context:
- Base commit: `64db0ba Stage 314: plan row one local article observability`.
- Stage 314 goal: make ROW ONE local saved article body presence observable without changing the ROW ONE app/manifest/runtime contracts.
- The implementation should add CLI/status metrics for saved local article sidecars and nonblank saved local paragraphs.
- `row-one build`, `row-one preview`, and `row-one refresh` should report metrics from the current render result.
- `row-one status --json` and text status should report metrics from the generated site currently on disk.
- Existing generated JSON contracts must remain unchanged: `row-one-app/v7`, `row-one-manifest/v1`, `row-one-runtime/v1`.
- No new generated JSON artifact should be introduced for these metrics.
- Social/community connectors, scoring, source collection, LLM calls, and compliance-review product features are out of scope.

Files to review:
- `src/fashion_radar/row_one/site_metrics.py`
- `src/fashion_radar/row_one/render.py`
- `src/fashion_radar/cli.py`
- `tests/test_row_one_site_metrics.py`
- `tests/test_row_one_cli.py`
- `tests/test_workflows.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`

Known review feedback already handled before this review:
- Avoid stale `data/articles/*.json` sidecars polluting `build`/`preview` output when `--latest-only` is not used.
- Narrow docs so `article_count` means valid generated sidecars while `paragraph_count` means nonblank saved body paragraphs.
- Add workflow assertions that Stage 314 metrics do not enter `data/edition.json`, `data/manifest.json`, or `data/runtime.json`.

Please review for:
1. Critical or Important correctness issues in the current implementation.
2. Backward compatibility risks in CLI/status JSON output.
3. Any mismatch between docs/tests and implementation.
4. Whether the stale-sidecar fix is technically sound.
5. Any missing focused tests that should block this stage.

Do not request product compliance features. Return findings first, ordered by severity, with file/line references. If there are no Critical or Important findings, say that explicitly and list only Minor/Nit findings or residual risks.

Verification already run successfully after the latest fixes:
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_site_metrics.py tests/test_row_one_cli.py tests/test_workflows.py tests/test_row_one_docs.py -q` -> `117 passed`
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q` -> `2078 passed`
- `UV_NO_CONFIG=1 uv lock --check` -> passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check` -> passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check` -> passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py` -> passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one build --as-of 2026-07-06T04:00:00Z --output-dir reports/row-one/site --latest-only` -> passed, 18 stories, 0 saved local articles, 0 saved local paragraphs
- `UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one status --site-dir reports/row-one/site --json` -> passed, `ok: true`, contracts unchanged, `local_articles` all zero for current generated site

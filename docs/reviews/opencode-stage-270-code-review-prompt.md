# Stage 270 Code Review Request

Please review the current uncommitted Stage 270 changes in `/home/ubuntu/fashion-radar`.

## Goal
Add ROW ONE runtime readiness for local/app-facing site operation:
- Generate `data/runtime.json` next to `data/edition.json` and `data/manifest.json`.
- Keep `row-one-manifest/v1` unchanged; do not add `runtime_path` to manifest.
- Add strict `schemas/row-one-runtime.schema.json` and package/archive coverage.
- Add `fashion-radar row-one status` to validate a generated site and print text/JSON runtime readiness.
- Add real subprocess smoke coverage for `row-one serve` and first-run smoke coverage for runtime/status.
- Keep docs aligned with fixed local port `127.0.0.1:8787`, daily `04:00`, and latest-only site cleanup boundaries.

## Technical Stack
Python 3.11+, Typer CLI, Pydantic models, JSON schema contract tests, pytest, ruff, uv.

## Review Focus
1. Correctness of `src/fashion_radar/row_one/render.py` runtime payload generation.
2. Correctness and maintainability of `src/fashion_radar/cli.py` `row-one status` validation and output contract.
3. Whether schema/tests/docs accurately reflect the runtime contract.
4. Whether manifest remains stable and does not gain `runtime_path`.
5. Whether first-run smoke and package/release hygiene coverage are sufficient.
6. Identify bugs, missing tests, inconsistent docs, or release blockers.

## Verification Already Run
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_first_run_smoke.py -q && UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .` => passed (`181 passed`, smoke passed)
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py -q && UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/cli.py tests/test_row_one_cli.py` => passed (`29 passed`, ruff passed)
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_app_contract.py tests/test_package_archives.py -q` => passed (`138 passed`) via subagent
- Focused Stage 270 gate: `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py tests/test_row_one_render.py tests/test_row_one_edition.py tests/test_row_one_readiness.py tests/test_row_one_app_contract.py tests/test_row_one_docs.py tests/test_scheduling.py tests/test_scheduling_docs.py tests/test_first_run_smoke.py tests/test_release_hygiene.py tests/test_package_archives.py -q` => passed (`508 passed`)
- `UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .` => passed

Please return:
- APPROVED or NOT APPROVED
- Findings ordered by severity with file/line references
- Required fixes before commit/push
- Optional follow-ups that should not block Stage 270

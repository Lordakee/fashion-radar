# Claude Code Stage 264 Code Review Prompt

You are the primary code reviewer for Fashion Radar Stage 264. Review in read-only mode. Do not edit files.

## Objective

Stage 264 adds ROW ONE Daily Readiness & Preview:

- shared ROW ONE utility helpers for safe external URLs and UTC formatting;
- `RowOneReadiness` derived from `RowOneEdition`;
- a homepage Latest Edition status strip;
- `fashion-radar row-one preview` that builds once and prints readiness/path/URL details;
- first-run smoke coverage for ROW ONE subcommand help, schedule ordering, and preview output;
- package archive guardrails for ROW ONE docs/schema/package files;
- docs for readiness/preview.

## Boundaries

The change must not add source acquisition, scraping, browser automation, platform APIs, account/session/cookie behavior, translation, LLM calls, image generation, paid APIs, deployment, remote hosting, auth, scoring/ranking changes, demand proof, platform coverage verification, or compliance-review product work. It must not change the `row-one-app/v1` JSON contract shape.

## Review Scope

Review the current git diff and these files especially:

- `src/fashion_radar/row_one/utils.py`
- `src/fashion_radar/row_one/readiness.py`
- `src/fashion_radar/row_one/templates.py`
- `src/fashion_radar/row_one/render.py`
- `src/fashion_radar/cli.py`
- `scripts/check_first_run_smoke.py`
- `scripts/check_package_archives.py`
- `tests/test_row_one_readiness.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_cli.py`
- `tests/test_row_one_docs.py`
- `tests/test_package_archives.py`
- `docs/row-one.md`
- `docs/cli-reference.md`
- `docs/github-upload-checklist.md`
- Stage 264 plan/review artifacts under `docs/superpowers/` and `docs/reviews/`.

## Verification Already Run

- `git diff --check`
- `uv --no-config run --frozen ruff check src/fashion_radar/row_one src/fashion_radar/cli.py scripts/check_first_run_smoke.py scripts/check_package_archives.py tests/test_row_one*.py tests/test_package_archives.py`
- `uv --no-config run --frozen ruff format --check src/fashion_radar/row_one src/fashion_radar/cli.py scripts/check_first_run_smoke.py scripts/check_package_archives.py tests/test_row_one*.py tests/test_package_archives.py`
- `uv --no-config run --frozen pytest tests/test_row_one_readiness.py tests/test_row_one_render.py tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_row_one_app_contract.py tests/test_package_archives.py -q` -> 140 passed
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`

## Review Questions

1. Does the implementation match the approved revised Stage 264 plan?
2. Does it avoid circular imports between `templates.py`, `readiness.py`, `render.py`, and `utils.py`?
3. Is extending internal `RowOneRenderResult` with `edition` safe and compatible with current call sites?
4. Does `row-one preview` reuse build behavior correctly without duplicating or diverging from `row-one build`?
5. Does the Latest Edition status strip escape dynamic data and preserve bilingual behavior?
6. Does first-run smoke coverage remain local-first and not create default repo artifacts?
7. Does package archive coverage correctly include ROW ONE docs and source files?
8. Is the `row-one-app/v1` JSON contract unchanged?

## Output Format

Return a concise review with sections:

- Critical
- Important
- Minor
- Positive checks
- Verdict

Call out exact files/lines when possible. If you find Critical or Important issues, include concrete fixes required before release.

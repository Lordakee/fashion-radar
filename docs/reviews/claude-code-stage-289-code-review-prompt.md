# Claude Code Stage 289 Code Review Prompt

Review the current uncommitted Stage 289 changes in `/home/ubuntu/fashion-radar`.

Goal:
- Add `signal_synthesis.groups[].signals[].story_refs` as app-ready supporting story references for ROW ONE clients.
- Treat this as deterministic information organization only.
- Do not add collectors, matching/scoring/ranking changes, story-ID changes, network calls, or compliance-review features.

Expected implementation:
- `ROW_ONE_APP_CONTRACT_VERSION` and the app schema/manifest contract should be `row-one-app/v7`.
- `story_refs` should be required on populated signal synthesis signals.
- Each `story_refs` item should copy the supporting story fields needed by clients: `story_id`, `headline`, `section_key`, `section_title`, `detail_href`, `source_name`, `published_date`, `evidence_count`, and `heat_delta`.
- `story_refs[].story_id` should align exactly with `story_ids`.
- CLI/status validation and first-run smoke validation should reject missing, mismatched, or drifted `story_refs`.
- The first-run smoke flow should remain deterministic and should not collect live starter RSS/GDELT sources.

Please review these files:
- `src/fashion_radar/row_one/render.py`
- `src/fashion_radar/cli.py`
- `schemas/row-one-app.schema.json`
- `schemas/row-one-manifest.schema.json`
- `scripts/check_first_run_smoke.py`
- `tests/test_row_one_app_contract.py`
- `tests/test_row_one_cli.py`
- `tests/test_first_run_smoke.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`
- `docs/superpowers/plans/2026-07-04-stage-289-row-one-signal-story-refs-plan.md`

Focused verification already passed locally after the latest fixes:
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py::test_row_one_status_rejects_semantic_story_refs_drift_that_schema_cannot_express tests/test_row_one_cli.py::test_row_one_status_rejects_runtime_contract_drift tests/test_row_one_docs.py tests/test_row_one_render.py::test_render_row_one_site_rejects_misaligned_signal_story_refs tests/test_row_one_app_contract.py::test_row_one_app_payload_supports_undated_stories tests/test_row_one_app_contract.py::test_row_one_app_schema_rejects_contract_drift -q`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check tests/test_row_one_cli.py tests/test_row_one_render.py tests/test_row_one_app_contract.py src/fashion_radar/row_one/render.py`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check tests/test_row_one_cli.py tests/test_row_one_render.py tests/test_row_one_app_contract.py src/fashion_radar/row_one/render.py`
- `UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
- `git diff --exit-code -- uv.lock pyproject.toml`

Full release verification will be re-run after this code review.

Return findings first, ordered by severity. Include file/line references. If there are no blocking issues, say so directly and mention residual risks or test gaps.

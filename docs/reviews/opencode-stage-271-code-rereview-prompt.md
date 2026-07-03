# Stage 271 Focused Code Re-review Request

Review the current working tree in `/home/ubuntu/fashion-radar`.

This is a focused re-review after one blocker from the read-only spec review:

- The detail HTML had `Editorial Takeaway` duplicated and rendered out of order
  relative to the JSON `detail_sections` model.

Do not perform a full historical docs review. Historical stage/review docs may
retain `row-one-app/v1` references. Focus on active source, active schemas,
active tests, current docs, and the repaired HTML detail organization.

## Required Checks

1. The active app payload is `row-one-app/v2`.
2. `data/edition.json` still uses the stable path and now includes:
   - top-level `content_sections`
   - story-level `detail_sections`
   - story-level `evidence_summary`
3. `detail_sections` order is:
   - `summary`
   - `why_it_matters`
   - `editorial_takeaway`
   - `signal_context`
   - `reader_path`
   - `evidence`
4. Detail HTML conceptual order matches that model:
   - Summary
   - Why It Matters
   - Editorial Takeaway
   - Signal Context
   - Reader Path
   - Evidence Trail
5. `Editorial Takeaway` / `编辑整理` is not duplicated as both an eyebrow and a
   heading in the detail panel.
6. Manifest contract remains `row-one-manifest/v1`, while manifest
   `app_contract.version` and manifest schema nested `app_contract.version.const`
   are `row-one-app/v2`.
7. Active source/schema/test/docs references are updated to v2; ignore old
   historical stage/review docs.
8. No new source acquisition, scraping, platform APIs, LLM calls, translation,
   image generation, scheduling installation, deployment, or compliance-review
   product features were added.

## Verification Already Re-run After Fix

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_app_contract.py \
  tests/test_row_one_render.py \
  tests/test_row_one_docs.py \
  tests/test_row_one_cli.py \
  tests/test_first_run_smoke.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_app_contract.py \
  tests/test_row_one_render.py \
  tests/test_row_one_docs.py \
  tests/test_row_one_cli.py \
  tests/test_first_run_smoke.py
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_app_contract.py \
  tests/test_row_one_render.py \
  tests/test_row_one_docs.py \
  tests/test_row_one_cli.py \
  tests/test_first_run_smoke.py \
  tests/test_package_archives.py -q
```

Latest focused result: `379 passed`.

Return:

- `APPROVED` or `NOT APPROVED`
- Critical/Important findings only
- Required fixes before commit

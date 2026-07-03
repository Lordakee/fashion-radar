# Stage 271 Code Review Request

Review the current working tree in `/home/ubuntu/fashion-radar` for Stage 271.

## Goal

Stage 271 adds structured ROW ONE app-facing content organization to
`data/edition.json` so app clients can render section rails, story cards, and
story detail content directly from JSON instead of rebuilding grouping logic or
scraping HTML.

## Expected Scope

- Bump active app contract from `row-one-app/v1` to `row-one-app/v2`.
- Keep `data/edition.json` and `schemas/row-one-app.schema.json` as the stable
  app payload/schema paths.
- Keep manifest contract `row-one-manifest/v1`, but update manifest
  `app_contract.version` and manifest schema nested `app_contract.version.const`
  to `row-one-app/v2`.
- Add top-level `content_sections`.
- Add story-level `detail_sections`, including `editorial_takeaway`.
- Add story-level `evidence_summary`.
- Align detail HTML labels with the organized detail model.
- Update active tests/docs/CLI/first-run/render pins from v1 to v2.
- Do not add source acquisition, scraping, platform APIs, LLM calls,
  translation, image generation, scheduling installation, deployment, or
  compliance-review product features.

## Files To Review

- `src/fashion_radar/row_one/render.py`
- `src/fashion_radar/row_one/templates.py`
- `schemas/row-one-app.schema.json`
- `schemas/row-one-manifest.schema.json`
- `tests/test_row_one_app_contract.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `tests/test_row_one_cli.py`
- `tests/test_first_run_smoke.py`
- `docs/row-one.md`
- `README.md`
- Stage 271 plan/spec/review docs

## Verification Already Run

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

Latest result before review: `379 passed`.

## Please Evaluate

1. Does the implementation satisfy the approved Stage 271 plan and design?
2. Are app payload, manifest payload, and both schemas internally consistent?
3. Are derived fields deterministic and mirrored from canonical story data?
4. Do tests cover version bump, content organization, schema drift, docs,
   render, CLI, first-run, and package/archive surfaces sufficiently?
5. Is there any accidental scope creep or missing active `row-one-app/v1` pin?

Return:

- `APPROVED` or `NOT APPROVED`
- Critical/Important findings only, with file references
- Required fixes before commit

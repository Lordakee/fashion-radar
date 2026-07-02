# Stage 267 ROW ONE First-Run App Discovery Verification Design

## Goal

Make the ROW ONE app discovery surface part of the normal first-run verification path by exposing the generated manifest in `row-one preview` and validating `data/manifest.json` plus `row-one serve --dry-run` in first-run smoke.

## User Need

The user wants ROW ONE to behave like a reliable daily local website and app backend surface. Stage 266 added `data/manifest.json` as the app discovery entry point, but the source-checkout smoke path still proves only the HTML site and `data/edition.json`. Stage 267 closes that gap:

- `row-one preview` should tell the user where the manifest is.
- First-run smoke should parse and validate the generated manifest.
- First-run smoke should verify the generated site can pass `row-one serve --dry-run` without starting a long-running server.
- Documentation should make clear that first-run smoke verifies the ROW ONE manifest and local serve dry-run path.

## Non-Goals

- No new collectors, platform search, social-media scraping, TikTok/Instagram/X/Xiaohongshu expansion, or community-tool ingestion.
- No story-level provenance fields, app contract field additions, schema version changes, or `row-one-app/v1` changes.
- No long-running server start in smoke, browser test, deployment, public hosting, tunnel, authentication, HTTPS, or service installation.
- No scoring, ranking, matching, scheduling, cleanup, SQLite, or report-generation changes.
- No compliance-review product features, LLM calls, translation services, image generation, or OpenDesign calls.

## Proposed Surface

### Preview Output

`fashion-radar row-one preview` will keep its existing lines and add one line:

```text
Manifest: <output-dir>/data/manifest.json
```

The existing `JSON: <output-dir>/data/edition.json` line remains unchanged for backwards compatibility with docs and smoke checks.

### First-Run Smoke Manifest Validation

After `row-one preview` writes the site, `scripts/check_first_run_smoke.py` will validate:

- `index.html` exists and is non-empty.
- `data/edition.json` exists, is non-empty, and parses as JSON.
- `data/manifest.json` exists, is non-empty, and parses as JSON.
- Manifest fields point to the existing app contract:
  - `contract_version == "row-one-manifest/v1"`
  - `app_contract.path == "data/edition.json"`
  - `site.index_path == "index.html"`
  - `site.manifest_path == "data/manifest.json"`
  - `counts.story_count == edition.story_count`
  - `counts.evidence_count == edition.evidence_count`
  - readiness is `ready` when story count is positive, otherwise `empty`

This checks the app discovery contract without adding schema loading or external dependencies to the smoke script.

### First-Run Smoke Serve Dry-Run

The same smoke block will call:

```bash
fashion-radar row-one serve --site-dir <row-one-site> --host 127.0.0.1 --port 8787 --dry-run
```

It will assert:

```text
Open: http://127.0.0.1:8787
```

This proves the generated site passes ROW ONE server directory validation without starting a long-running HTTP server.

## Architecture

Keep this stage in the existing CLI and smoke layers:

- `src/fashion_radar/cli.py`
  - Add the `Manifest:` line to `row-one preview`.
- `scripts/check_first_run_smoke.py`
  - Add a small `validate_row_one_manifest(...)` helper near other smoke validators.
  - Extend the existing ROW ONE smoke block after preview output.
  - Add a `row-one serve --dry-run` call against the generated site.
- `tests/test_row_one_cli.py`
  - Pin the new preview output.
- `tests/test_first_run_smoke.py`
  - Update the fake ROW ONE preview to write manifest JSON and include `Manifest:`.
  - Add a fake `row-one serve --dry-run` response and assert the command is invoked.
- `docs/row-one.md`, `docs/first-run.md`, and `README.md`
  - Describe that preview prints the manifest path and first-run smoke verifies the manifest plus serve dry-run path.

No ROW ONE render/schema/model changes are needed because Stage 266 already writes and validates `data/manifest.json`.

## Test Strategy

- CLI tests verify preview prints both `JSON:` and `Manifest:` and still prints readiness and dry-run URL output.
- First-run smoke unit tests verify the mock creates both `edition.json` and `manifest.json`, the smoke script validates the manifest, and `row-one serve --dry-run` is called.
- First-run smoke script is run against the real source checkout.
- Docs tests pin the public wording for preview manifest output and first-run smoke manifest/serve dry-run verification.

## Release Gate

Run focused checks first, then the full release gate:

```bash
uv --no-config run --frozen pytest tests/test_row_one_cli.py tests/test_first_run_smoke.py tests/test_row_one_docs.py -q
uv --no-config run --frozen ruff check src/fashion_radar/cli.py scripts/check_first_run_smoke.py tests/test_row_one_cli.py tests/test_first_run_smoke.py tests/test_row_one_docs.py
uv --no-config run --frozen ruff format --check src/fashion_radar/cli.py scripts/check_first_run_smoke.py tests/test_row_one_cli.py tests/test_first_run_smoke.py tests/test_row_one_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
git diff --check
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config run --frozen pytest -q
uv --no-config build
uv --no-config run --frozen python scripts/check_package_archives.py dist
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
```

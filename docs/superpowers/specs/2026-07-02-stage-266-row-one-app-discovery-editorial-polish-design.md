# Stage 266 ROW ONE App Discovery And Editorial Polish Design

## Goal

Make ROW ONE easier for an app or local web client to consume and make the
generated site feel more like a professional daily fashion edition, while
staying static-only and preserving the existing `row-one-app/v1` payload.

## User Need

The user wants ROW ONE to become a daily local fashion-news website and app
backend surface, not just a collection of links. The current site already
creates summaries, detail pages, bilingual UI controls, readiness status, local
serving, and `data/edition.json`. Stage 266 adds the next small layer needed for
app integration and editorial presentation:

- A stable app discovery entry point so clients can find the latest edition
  contract without hard-coding implementation details beyond one manifest path.
- A clear front-page lead story hierarchy so the homepage reads like a daily
  edition instead of equally weighted cards.
- Basic SEO/social metadata for the generated static index and detail pages.
- A clearer GitHub/source-checkout first-run path for generating and inspecting
  the ROW ONE local site.

## Non-Goals

- No new collectors, scraping, platform API calls, TikTok/Instagram/X/Xiaohongshu
  integration, community-tool ingestion, or social-media expansion.
- No LLM calls, translation services, image generation, OpenDesign calls, or paid
  APIs.
- No deployment automation, tunnels, public hosting, authentication, HTTPS, or
  system service installation.
- No compliance-review product features.
- No change to scoring, ranking, matching, source collection, scheduling, server
  binding, cleanup, or SQLite behavior.
- No breaking change to `row-one-app/v1`; `data/edition.json` remains the app
  payload for edition content.
- No copying story or section arrays into the manifest.

## Proposed Surface

### App Discovery Manifest

`render_row_one_site()` will write a new generated file:

```text
data/manifest.json
```

The manifest is a small discovery contract, not a second edition payload. It
uses a new version string:

```text
row-one-manifest/v1
```

The manifest includes:

- `contract_version`: `row-one-manifest/v1`
- `brand`
- `generated_at`
- `edition_date`
- `manifest_schema_path`: `schemas/row-one-manifest.schema.json`
- `app_contract`: version and relative path for `data/edition.json`
- `site`: stable relative paths for `index.html`, `data/edition.json`,
  `assets/`, and `details/`
- `counts`: story, section, and safe evidence-link counts
- `readiness`: narrow machine status, `ready` or `empty`
- `capabilities`: stable booleans for bilingual UI, static site, detail pages,
  sanitized external URLs, latest-only cleanup support, and SEO metadata support

The manifest must not contain absolute URLs, host/port values, LAN URLs,
preview-only text, story arrays, section arrays, user secrets, or local machine
paths.

### Static Site Editorial Polish

The generated homepage will promote the first available top story into a
distinct lead story block. Remaining stories render in the existing section
grids. This creates editorial hierarchy without changing ranking or story
selection: the lead story is only a presentation treatment of an already
selected story.

The generated HTML will add deterministic metadata:

- Index page: `meta name="description"`, Open Graph title/description/type, and
  Twitter card title/description.
- Detail pages: story-specific description, Open Graph title/description/type,
  and Twitter card title/description.

These fields use existing edition and story summary text. They do not translate,
summarize, fetch, infer, or call external services.

### GitHub-Ready First-Run Path

Documentation will connect the existing first-run sample flow to ROW ONE:

- README points users from the source-checkout quickstart to the local ROW ONE
  site path.
- `docs/first-run.md` adds a short sample-site inspection path after the sample
  report/dashboard flow.
- `docs/row-one.md` Quick Start includes repo-local flags so users know exactly
  where the local site is generated from a cloned repo.
- `docs/github-upload-checklist.md` reminds maintainers not to upload generated
  ROW ONE site artifacts while keeping the docs path discoverable.

## Architecture

Add the manifest builder to `fashion_radar.row_one.render` near the existing app
payload builder:

- `ROW_ONE_MANIFEST_CONTRACT_VERSION`
- `build_row_one_manifest_payload(edition: RowOneEdition) -> dict[str, object]`

`render_row_one_site()` writes both `data/edition.json` and
`data/manifest.json` from the same `RowOneEdition` object. This keeps counts and
timestamps in sync and avoids adding new read paths.

Add `schemas/row-one-manifest.schema.json` as the strict validation contract for
the manifest. The schema is shipped in the source distribution. Runtime
generated `data/manifest.json` is not shipped.

Update `fashion_radar.row_one.templates` only for presentation:

- Render a lead story block for the first top story if one exists.
- Keep the story in its original section as well, unless the implementation plan
  explicitly removes it from the grid with tests. Stage 266 prefers the smaller,
  lower-risk approach: lead story as an additional presentation highlight.
- Add metadata helper functions that escape HTML and truncate descriptions
  deterministically.
- Keep language toggle behavior unchanged.

## Test Strategy

- Render tests verify `data/manifest.json` is written and its counts/path fields
  match `data/edition.json`.
- App contract tests validate the manifest against
  `schemas/row-one-manifest.schema.json`, including empty editions and schema
  drift rejections.
- Render tests verify the homepage contains a lead story block and detail/index
  metadata.
- Docs tests pin `data/manifest.json`, `row-one-manifest/v1`,
  `schemas/row-one-manifest.schema.json`, lead story, SEO/social metadata, and
  the source-checkout ROW ONE path.
- Package archive tests include the new manifest schema in sdist required files.

## Release Gate

Run focused checks first, then the full release gate:

```bash
uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_row_one_app_contract.py tests/test_row_one_docs.py tests/test_package_archives.py -q
uv --no-config run --frozen ruff check src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_app_contract.py tests/test_row_one_docs.py scripts/check_package_archives.py tests/test_package_archives.py
uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_app_contract.py tests/test_row_one_docs.py scripts/check_package_archives.py tests/test_package_archives.py
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

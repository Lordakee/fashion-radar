# Stage 168 Source Pack Public GDELT Doc Sync Design

## Objective

Synchronize `docs/source-packs.md` with the checked-in public starter source
pack so the documentation names the actual 10 GDELT lanes and shows current
source-pack lint count output.

## Current Gap

`configs/source-packs/fashion-public.example.yaml` currently contains 16 enabled
sources: 6 RSS entries and 10 GDELT entries. The `docs/source-packs.md` "GDELT
Queries" section still summarizes only four broad starter query themes:

```text
- luxury/designer fashion
- celebrity style/red carpet
- bags/shoes/products
- emerging designers
```

The same document's example JSON shape shows the correct `source_count` and
`type_counts`, but its `tag_counts` example is abbreviated to only two keys
instead of reflecting the actual linter output for the public pack.

The starter pack itself is valid. The issue is documentation drift and missing
test coverage for that drift.

## Scope

In scope:

- Update `docs/source-packs.md` so the "GDELT Queries" section lists every
  current public-pack GDELT source by exact source name.
- Update the example JSON `tag_counts` to match the current output from
  `fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --format json`.
- Add documentation tests that:
  - parse the checked-in public pack and require each GDELT source name to
    appear in the "GDELT Queries" section;
  - parse the documented JSON example and compare stable count fields against
    `lint_source_pack(...)`.

Out of scope:

- No changes to `configs/source-packs/fashion-public.example.yaml`.
- No changes to source-pack linter behavior.
- No CLI changes.
- No collector changes.
- No network availability probing.
- No Google News RSS, Google Trends, source acquisition expansion, scraping,
  browser automation, platform APIs, login, cookies, monitoring, scheduling,
  demand proof, ranking, coverage verification, or compliance-review product
  features.

## Architecture

Modify one documentation test module:

```text
tests/test_source_packs_docs.py
```

Add small helpers that stay local to the test module:

- `_public_pack_gdelt_source_names()` reads the YAML source pack and returns
  the exact names for entries with `type: gdelt`.
- `_json_block_after(...)` extracts the JSON code block after the
  "Example JSON shape:" marker.

The test uses the production `lint_source_pack(...)` function for expected
counts rather than duplicating count logic in the test.

Modify one doc:

```text
docs/source-packs.md
```

Replace the abbreviated GDELT bullet list with exact current source names and
short descriptions. Expand the example `tag_counts` block to match the current
public pack linter output.

## Tech Stack

- Python standard library: `json`, `pathlib`.
- Existing project dependency: `yaml`.
- Existing source-pack linter: `fashion_radar.source_packs.lint_source_pack`.
- Pytest.
- Markdown docs.
- `uv --no-config run --frozen`.
- Local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

## Implementation Method

Use TDD:

1. Add tests that fail against the current abbreviated docs.
2. Run the focused doc tests and confirm the new tests fail.
3. Update `docs/source-packs.md` to list the 10 GDELT lanes and current tag
   counts.
4. Re-run focused tests and formatting/lint checks.
5. Run opencode code review, full release gate, opencode release review,
   commit, and push.

## Expected Behavior

The "GDELT Queries" section lists all current public-pack GDELT source names:

- `GDELT Luxury Fashion`
- `GDELT Celebrity Style`
- `GDELT Bags Shoes Products`
- `GDELT Emerging Designers`
- `GDELT Runway Fashion Week`
- `GDELT Designer Brand Momentum`
- `GDELT Retail Resale Fashion`
- `GDELT Footwear Sneakers`
- `GDELT Creative Director Moves`
- `GDELT Beauty Fashion Crossover`

The example JSON count fields match the current source pack lint output for:

- `source_count`
- `enabled_count`
- `disabled_count`
- `type_counts`
- `tag_counts`
- `findings`

The docs still state that scores reflect only the configured source set and do
not imply platform coverage or demand proof.

## Risks

- Comparing full linter output including `path` would be brittle because tests
  may call the linter with absolute paths. Compare count fields and findings
  only.
- The exact GDELT source-name assertion intentionally fails when the pack adds
  or renames lanes without updating docs. That is the desired drift signal.
- Do not broaden this stage into source availability checks. The existing
  source-pack-quality docs already state that the linter cannot know whether
  feeds are live or GDELT queries return records.

## Verification

Focused:

```bash
uv --no-config run --frozen pytest tests/test_source_packs_docs.py -q
uv --no-config run --frozen ruff check tests/test_source_packs_docs.py
uv --no-config run --frozen ruff format --check tests/test_source_packs_docs.py
```

Release gate:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader
```

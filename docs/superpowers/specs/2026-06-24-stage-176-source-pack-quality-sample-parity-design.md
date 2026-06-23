# Stage 176 Source-Pack Quality Sample Parity Design

## Objective

Keep `docs/source-pack-quality.md` synchronized with the current
`source-pack-lint` output for the checked-in public source pack, without
changing runtime lint behavior.

## Current Gap

`docs/source-pack-quality.md` documents table and JSON examples for:

```bash
uv run fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml
uv run fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --format json
```

The table sample currently matches the current renderer prefix, including the
full public-pack `Tags:` line added in a prior stage, but no test guards that
parity. The JSON sample still shows an abbreviated `tag_counts` object and a
synthetic warning finding for `Example Feed`, while current
`lint_source_pack(configs/source-packs/fashion-public.example.yaml)` returns:

- `source_count`: `16`
- `enabled_count`: `16`
- `disabled_count`: `0`
- `type_counts`: `gdelt=10`, `rss=6`
- `tag_counts`: 22 configured tag lanes
- `findings`: `[]`

The docs should keep the sample exact for the checked-in clean starter pack,
including an empty findings list.

## Scope

In scope:

- Add docs/runtime parity tests in `tests/test_source_pack_quality_docs.py`.
- Parse the `docs/source-pack-quality.md` table sample and compare it with the
  current `render_source_pack_lint_table(lint_source_pack(...))` prefix.
- Parse the JSON sample and compare stable fields to
  `lint_source_pack(configs/source-packs/fashion-public.example.yaml)`.
- Update `docs/source-pack-quality.md` JSON sample so it matches the checked-in
  public source pack output.

Out of scope:

- No changes to `src/fashion_radar/source_packs.py`.
- No changes to `src/fashion_radar/cli.py`.
- No changes to source pack YAML config.
- No changes to collector behavior, runtime lint payload shape, renderer
  behavior, CLI exit behavior, install hints, mirror hints, dependency
  manifests, or `uv.lock`.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, monitoring, scheduling, demand proof, ranking, coverage verification, or
  compliance-review product feature.

## Architecture

Modify only:

```text
tests/test_source_pack_quality_docs.py
docs/source-pack-quality.md
```

The tests mirror the Stage 175 entity-pack quality parity pattern and the Stage
168 source-pack docs parity pattern. They read the Markdown file, extract fenced
code blocks, parse JSON with the Python standard library, and use the production
linter as the source of truth.

Add constants:

```python
PUBLIC_SOURCE_PACK = ROOT / "configs" / "source-packs" / "fashion-public.example.yaml"
```

The table sample documents the relative path used in the CLI examples, so the
table parity test must pass `PUBLIC_SOURCE_PACK.relative_to(ROOT)` into
`lint_source_pack(...)`. The JSON test can use the absolute constant for file
location and compare the documented path with
`PUBLIC_SOURCE_PACK.relative_to(ROOT).as_posix()`.

Add helpers:

- `_fenced_block_after(text, marker, language)` for extracting fenced blocks.
- `_source_pack_quality_table_sample()` for the table sample under
  `## Table Output`.
- `_source_pack_quality_json_sample()` for the JSON sample under
  `## JSON Output`.

Add two tests:

1. `test_source_pack_quality_table_sample_matches_public_pack_lint_prefix`
   compares the documented table sample with the first N lines of
   `render_source_pack_lint_table(lint_source_pack(relative_pack_path))`.
2. `test_source_pack_quality_json_sample_matches_public_pack_lint_output`
   compares:
   - `path`
   - `source_count`
   - `enabled_count`
   - `disabled_count`
   - `type_counts`
   - `tag_counts`
   - `findings == []`

The tests should not run CLI commands, fetch sources, open SQLite, collect
items, or create artifacts.

## Tech Stack

- Python standard library `json`.
- Existing `fashion_radar.source_packs.lint_source_pack`.
- Existing `fashion_radar.source_packs.render_source_pack_lint_table`.
- Pytest.
- Markdown docs.
- `uv --no-config run --frozen`.
- Local opencode reviews with `zhipuai-coding-plan/glm-5.2 --variant max`.

## Implementation Method

Use TDD:

1. Add the JSON/table docs parity tests first.
2. Run the new JSON parity test and confirm it fails against current docs because
   the documented JSON `tag_counts` object is abbreviated and the sample shows a
   warning finding while the current public pack has no findings.
3. Update only `docs/source-pack-quality.md` so the JSON sample's fields match
   current linter output for the checked-in public source pack.
4. Re-run focused tests and lint checks.
5. Run opencode code review, release gate, opencode release review, commit, and
   push.

## Expected Behavior

- The source-pack quality table sample remains synchronized with the current
  public source pack lint table prefix.
- The JSON sample's stable fields match current `lint_source_pack(...)` output
  for the checked-in public source pack.
- The JSON sample shows `findings: []` for the current clean starter pack.
- Runtime behavior remains unchanged.

## Risks

- Passing an absolute path into `lint_source_pack(...)` would make the table
  sample comparison fail on line 1. The table test must use the relative pack
  path.
- If the public source pack later gains warnings, this parity guard will require
  the docs sample to change. That is intentional for a checked-in starter-pack
  sample.
- Changing runtime linter output or source pack config would expand the node
  unnecessarily and is out of scope.

## Verification

Focused:

```bash
uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py::test_source_pack_quality_json_sample_matches_public_pack_lint_output -q
uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py -q
uv --no-config run --frozen pytest tests/test_source_packs.py tests/test_source_pack_quality_docs.py -q
uv --no-config run --frozen ruff check tests/test_source_pack_quality_docs.py
uv --no-config run --frozen ruff format --check tests/test_source_pack_quality_docs.py
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

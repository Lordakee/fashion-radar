# Stage 161 Source-Pack Lint Tag Counts Design

## Objective

Show deterministic source tag counts in the default human table output from
`fashion-radar source-pack-lint`.

## Current Gap

`SourcePackLintResult` already exposes `tag_counts` and JSON output already
includes that field. The default table renderer prints `Types:` and then
`Findings:`, so a user reading the human output cannot see source-set tag
balance without switching to JSON.

## Scope

In scope:

- Add one `Tags:` summary line to `render_source_pack_lint_table(...)`.
- Reuse existing `_format_counts(...)` so tag counts are sorted
  deterministically and empty tag counts render as `none`.
- Add focused tests for direct table rendering and CLI table output.
- Update `docs/source-pack-quality.md` so the documented table output and
  summary bullets include tags.

Out of scope:

- No changes to JSON output shape.
- No source-pack schema changes.
- No new lint finding codes.
- No changes to source collection, source availability checks, source
  acquisition, ranking, demand proof, coverage verification, scheduling, or
  monitoring.
- No social connectors, scraping, browser automation, platform APIs,
  login/cookie/session behavior, or compliance-review product feature.

## Architecture

`lint_source_pack(...)` already computes sorted `tag_counts` from each configured
source's `tags`. `render_source_pack_lint_table(...)` should display that
existing field immediately after the `Types:` line:

```text
Tags: gdelt=2, runway=1, shoes=1
```

The CLI already delegates table rendering to
`render_source_pack_lint_table(...)`, so the CLI table output will pick up the
new line without command-layer changes.

## Tech Stack

- Python standard library and existing source-pack helpers.
- Existing Typer CLI.
- Pytest for focused unit and CLI tests.
- `uv --no-config run --frozen` for tests and lint.
- Local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

## Implementation Method

Use test-first changes:

1. Add a focused unit test that builds a tiny local source pack with overlapping
   tags, calls `lint_source_pack(...)`, renders the table, and asserts `Tags:`
   appears between `Types:` and `Findings:` with sorted deterministic counts.
2. Strengthen the public-pack CLI table test to assert `Tags:` appears in
   default table output.
3. Add the `Tags:` line to `render_source_pack_lint_table(...)`.
4. Update `docs/source-pack-quality.md` table sample and summary bullets.
5. Run focused tests, docs tests, lint/format, local opencode code review, full
   release gate, local opencode release review, commit, and push.

## Expected Behavior

A source pack like:

```yaml
version: 1
sources:
  - name: GDELT Runway
    type: gdelt
    query: runway
    weight: 0.8
    tags: [gdelt, runway]
  - name: GDELT Shoes
    type: gdelt
    query: shoes
    weight: 0.8
    tags: [gdelt, shoes]
```

should render a summary containing:

```text
Types: gdelt=2
Tags: gdelt=2, runway=1, shoes=1
Findings: 0 errors, 0 warnings, 0 info
```

If a valid source pack has no tags, the table should render `Tags: none`,
matching the existing `_format_counts(...)` empty-count behavior.

## Risks

- This changes a stable human CLI text surface by adding one summary line.
  Machine-readable users should continue to use JSON, whose shape is unchanged.
- The public source pack has many tags; tests should avoid asserting the full
  public-pack tag list in the CLI smoke and instead assert that the table
  includes a `Tags:` line.

## Verification

Focused:

```bash
uv --no-config run --frozen pytest tests/test_source_packs.py::test_render_source_pack_lint_table_includes_tag_counts -q
uv --no-config run --frozen pytest tests/test_source_packs.py tests/test_cli.py -k "source_pack_lint" -q
uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py tests/test_source_packs.py tests/test_cli.py -k "source_pack" -q
uv --no-config run --frozen ruff check src/fashion_radar/source_packs.py tests/test_source_packs.py tests/test_cli.py
uv --no-config run --frozen ruff format --check src/fashion_radar/source_packs.py tests/test_source_packs.py tests/test_cli.py
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

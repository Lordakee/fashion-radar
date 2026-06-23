# Stage 162 Source-Pack Lint Finding Count Grammar Design

## Objective

Make the `source-pack-lint` human table summary use singular labels for exactly
one finding and plural labels otherwise.

## Current Gap

`render_source_pack_lint_table(...)` currently formats finding totals with fixed
plural labels for `error` and `warning`. When a test fixture has exactly one
warning, the observed output is:

```text
Findings: 0 errors, 1 warnings, 0 info
```

This grammar issue was surfaced during Stage 161's code review after the new
`Tags: none` regression test introduced a single-warning summary.

## Scope

In scope:

- Add a tiny source-pack-local formatter for finding count labels.
- Update only `render_source_pack_lint_table(...)`.
- Add focused tests for:
  - `1 error`, `1 warning`, and `1 info`;
  - plural labels for non-one counts;
  - the Stage 161 `Tags: none` test using `1 warning`.
- Preserve existing `0 errors`, `0 warnings`, and `0 info` wording.

Out of scope:

- No changes to entity-pack lint, community-signal lint, or directory lint
  output.
- No JSON output changes.
- No lint severity, finding, exit-code, strict-mode, import, or validation
  behavior changes.
- No broad docs churn.
- No source collection, source availability checks, source acquisition,
  ranking, demand proof, coverage verification, scheduling, or monitoring.
- No social connectors, scraping, browser automation, platform APIs,
  login/cookie/session behavior, or compliance-review product feature.

## Architecture

Keep the helper local to `src/fashion_radar/source_packs.py`:

```python
def _format_finding_count(count: int, singular: str, plural: str) -> str:
    label = singular if count == 1 else plural
    return f"{count} {label}"
```

Then use it only in `render_source_pack_lint_table(...)`:

```python
(
    "Findings: "
    f"{_format_finding_count(result.error_count, 'error', 'errors')}, "
    f"{_format_finding_count(result.warning_count, 'warning', 'warnings')}, "
    f"{_format_finding_count(result.info_count, 'info', 'info')}"
),
```

The CLI already delegates source-pack table output to the renderer, so no CLI
command-layer change is needed.

## Tech Stack

- Python.
- Existing source-pack lint renderer.
- Pytest focused renderer tests.
- Ruff.
- Local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

## Implementation Method

Use test-first changes:

1. Update the existing Stage 161 single-warning expectation to `1 warning`.
2. Add a direct renderer test for `1 error, 1 warning, 1 info`.
3. Add a direct renderer test for plural non-one counts.
4. Implement the local formatter and replace the source-pack `Findings:` line.
5. Run source-pack focused tests, local opencode code review, full release gate,
   release review, release hygiene, commit, and push.

## Expected Behavior

Zero counts stay plural where appropriate:

```text
Findings: 0 errors, 0 warnings, 0 info
```

One of each finding renders:

```text
Findings: 1 error, 1 warning, 1 info
```

Two of each finding renders:

```text
Findings: 2 errors, 2 warnings, 2 info
```

`info` keeps the same word for singular and plural, matching current product
language.

## Risks

- This changes a stable human CLI text surface. JSON output remains the stable
  automation interface and is unchanged.
- Adjacent lint renderers have similar fixed plural wording. They remain out of
  scope for this node to keep the change narrow and avoid broad docs/test churn.
- If future work wants consistent grammar across all lint renderers, it can
  extract a shared helper as a separate stage after this source-pack-only change
  is verified.

## Verification

Focused:

```bash
uv --no-config run --frozen pytest tests/test_source_packs.py -q -k "finding_count or tag_counts"
uv --no-config run --frozen pytest tests/test_source_packs.py tests/test_source_pack_quality_docs.py -q
uv --no-config run --frozen ruff check src/fashion_radar/source_packs.py tests/test_source_packs.py tests/test_source_pack_quality_docs.py
uv --no-config run --frozen ruff format --check src/fashion_radar/source_packs.py tests/test_source_packs.py tests/test_source_pack_quality_docs.py
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

# Stage 164 Cross-Lint Finding Count Grammar Design

## Objective

Make human-readable lint table finding-count labels consistent across
source-pack, entity-pack, and community-signal lint surfaces.

## Current Gap

Stage 162 fixed `source-pack-lint` so one finding renders as `1 error` or
`1 warning`, while zero and non-one counts keep plural labels. Entity-pack and
community-signal human tables still render fixed plural labels:

```text
Findings: 1 errors, 1 warnings, 1 info
```

The same fixed plural wording also appears in community-signal directory
per-file rows:

```text
- exports/b.csv: 1 rows, 0 import-ready, 1 errors, 3 warnings, 2 info
```

This is a human-output polish gap only. The underlying counts, JSON shape, lint
semantics, and CLI exit behavior are already correct.

## Scope

In scope:

- Add a small internal helper for finding-count wording.
- Keep `source-pack-lint` behavior unchanged while moving it to the shared
  helper.
- Update entity-pack table `Findings:` summary wording.
- Update community-signal file table `Findings:` summary wording.
- Update community-signal directory aggregate `Findings:` summary wording.
- Update community-signal directory per-file finding count wording.
- Update user-facing community signal docs that show the affected output.

Out of scope:

- No JSON output changes.
- No lint model, severity, sorting, strict-mode, or CLI command flow changes.
- No row-count grammar changes such as `1 rows`.
- No historical spec/review archive rewrites.
- No social connectors, scraping, browser automation, platform APIs, login,
  cookies, monitoring, scheduling, source acquisition, demand proof, ranking,
  coverage verification, or compliance-review product features.

## Architecture

Create a new internal helper module:

```text
src/fashion_radar/lint_formatting.py
```

The module owns two pure helpers:

```python
def format_count_label(count: int, singular: str, plural: str) -> str: ...
def format_finding_counts(error_count: int, warning_count: int, info_count: int) -> str: ...
```

`format_finding_counts(...)` returns:

```text
0 errors, 1 warning, 2 info
```

`info` remains `info` for every count, matching the existing product wording.
The helper is intentionally internal and generic enough for the existing lint
renderers without becoming a public API.

Renderer usage:

- `render_source_pack_lint_table(...)` uses
  `format_finding_counts(result.error_count, result.warning_count, result.info_count)`.
- `render_entity_pack_lint_table(...)` uses the same helper.
- `render_community_signal_lint_table(...)` uses the same helper.
- `render_community_signal_directory_lint_table(...)` uses the same helper for
  the aggregate `Findings:` line and each per-file finding-count suffix.

## Tech Stack

- Python standard library.
- Existing renderer functions and pytest modules.
- Local opencode plan/code/release review with
  `zhipuai-coding-plan/glm-5.2 --variant max`.
- `uv --no-config run --frozen` for tests and lint.

## Implementation Method

Use test-first changes:

1. Add RED tests for entity-pack singular and plural finding counts.
2. Add RED tests for community-signal file singular and plural finding counts.
3. Add RED tests for community-signal directory aggregate and per-file singular
   and plural finding counts.
4. Implement the shared helper and wire the renderers to it.
5. Re-run source-pack renderer tests to prove Stage 162 behavior did not
   regress.
6. Update `docs/community-signal-quality.md` examples for the changed human
   output.
7. Run focused tests, opencode code review, full release gate, release review,
   commit, and push.

## Expected Behavior

Entity-pack summary:

```text
Findings: 1 error, 1 warning, 1 info
Findings: 2 errors, 2 warnings, 2 info
```

Community-signal file summary:

```text
Findings: 1 error, 1 warning, 1 info
Findings: 2 errors, 2 warnings, 2 info
```

Community-signal directory summary and per-file lines:

```text
Findings: 1 error, 1 warning, 1 info
- signals.csv: 1 rows, 0 import-ready, 1 error, 1 warning, 1 info
```

The `1 rows` wording in per-file rows is left unchanged in this stage.

## Risks

- Touching source-pack rendering again could regress Stage 162. Keep the helper
  behavior identical and run existing source-pack renderer tests.
- Community-signal directory results store aggregate counts directly while file
  results compute counts from findings. Tests should cover both paths.
- A broad "lint output grammar" refactor could drift into row-count wording or
  docs churn. Keep this stage limited to finding-count labels.

## Verification

Focused:

```bash
uv --no-config run --frozen pytest \
  tests/test_entity_pack_lint.py::test_render_entity_pack_lint_table_singularizes_one_finding_count \
  tests/test_entity_pack_lint.py::test_render_entity_pack_lint_table_keeps_plural_finding_counts \
  tests/test_community_signal_lint.py::test_render_community_signal_lint_table_singularizes_one_finding_count \
  tests/test_community_signal_lint.py::test_render_community_signal_lint_table_keeps_plural_finding_counts \
  tests/test_community_signal_lint.py::test_render_community_signal_directory_lint_table_singularizes_finding_counts \
  tests/test_community_signal_lint.py::test_render_community_signal_directory_lint_table_keeps_plural_finding_counts \
  -q
uv --no-config run --frozen pytest tests/test_source_packs.py tests/test_entity_pack_lint.py tests/test_community_signal_lint.py tests/test_cli.py -q -k "source_pack_lint or entity_pack_lint or community_signal_lint"
uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py tests/test_cli_docs.py -q -k "community_signal_quality"
uv --no-config run --frozen ruff check src/fashion_radar/lint_formatting.py src/fashion_radar/source_packs.py src/fashion_radar/entity_packs.py src/fashion_radar/community_signals.py tests/test_entity_pack_lint.py tests/test_community_signal_lint.py tests/test_source_packs.py tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check src/fashion_radar/lint_formatting.py src/fashion_radar/source_packs.py src/fashion_radar/entity_packs.py src/fashion_radar/community_signals.py tests/test_entity_pack_lint.py tests/test_community_signal_lint.py tests/test_source_packs.py tests/test_cli_docs.py
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

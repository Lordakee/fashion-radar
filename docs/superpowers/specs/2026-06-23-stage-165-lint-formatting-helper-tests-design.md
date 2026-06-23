# Stage 165 Lint Formatting Helper Tests Design

## Objective

Add direct unit coverage for the shared lint finding-count formatting helper
introduced in Stage 164.

## Current Gap

Stage 164 created `src/fashion_radar/lint_formatting.py` and wired three
human-readable lint table renderers to it. The renderer tests cover the shared
behavior indirectly through source-pack, entity-pack, and community-signal
output, but there is no direct unit test for the helper module itself.

The uncovered helper contract is small but shared:

```text
0 errors
1 error
2 errors
0 errors, 1 warning, 2 info
```

`info` intentionally stays `info` for every count.

## Scope

In scope:

- Add direct tests for `format_count_label(...)`.
- Add direct tests for `format_finding_counts(...)`.
- Cover zero, one, plural, and mixed severity counts.
- Keep the existing helper implementation and all caller output unchanged.

Out of scope:

- No production code changes unless the new tests reveal a real mismatch.
- No renderer, CLI, JSON, lint semantics, strict-mode, or docs output changes.
- No row-count grammar changes.
- No historical review archive rewrites.
- No social connectors, scraping, browser automation, platform APIs, login,
  cookies, monitoring, scheduling, source acquisition, demand proof, ranking,
  coverage verification, or compliance-review product features.

## Architecture

Create one focused test module:

```text
tests/test_lint_formatting.py
```

The module imports only:

```python
from fashion_radar.lint_formatting import format_count_label, format_finding_counts
```

Use small pytest parametrized cases for `format_count_label(...)`, then direct
assertions for common finding-count combinations. This keeps the helper's
contract visible without duplicating every renderer scenario.

## Tech Stack

- Python standard library.
- Pytest.
- Existing `src` package layout.
- `uv --no-config run --frozen` for tests, lint, and scripted checks.
- Local opencode reviews with `zhipuai-coding-plan/glm-5.2 --variant max`.

## Implementation Method

This is a characterization-test stage for existing behavior. The usual RED
step does not apply because the helper already exists and currently satisfies
the intended contract. Do not mutate production code to manufacture a failing
test.

Implementation steps:

1. Add the focused helper test module.
2. Run the focused test module.
3. Run existing renderer tests that depend on the helper.
4. Run lint and format checks for the touched test file.
5. Run the normal release gate, opencode code review, opencode release review,
   commit, and push.

## Expected Behavior

`format_count_label(...)`:

```text
0 errors
1 error
2 errors
```

`format_finding_counts(...)`:

```text
0 errors, 0 warnings, 0 info
1 error, 1 warning, 1 info
2 errors, 2 warnings, 2 info
1 error, 0 warnings, 2 info
```

## Risks

- Over-testing every caller would add noise without improving the shared helper
  contract. Keep this stage to direct helper tests plus existing renderer
  regression tests.
- Changing implementation while adding tests would expand this node. Do not
  edit production code unless the characterization tests expose an actual
  mismatch.
- Broad grammar cleanup could drift into row-count wording. Keep this stage
  limited to finding-count helper behavior.

## Verification

Focused:

```bash
uv --no-config run --frozen pytest tests/test_lint_formatting.py -q
uv --no-config run --frozen pytest \
  tests/test_source_packs.py \
  tests/test_entity_pack_lint.py \
  tests/test_community_signal_lint.py \
  -q -k "render_"
uv --no-config run --frozen ruff check tests/test_lint_formatting.py
uv --no-config run --frozen ruff format --check tests/test_lint_formatting.py
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

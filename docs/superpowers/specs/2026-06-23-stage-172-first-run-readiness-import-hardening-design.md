# Stage 172 First-Run Readiness Import Hardening Design

## Objective

Make the first-run smoke parity test fail loudly if
`fashion_radar.external_tool_readiness` is missing or broken, instead of
silently skipping behind a stale Stage 66 fallback.

## Current Gap

`tests/test_first_run_smoke.py` still treats `external_tool_readiness` as
optional:

```python
try:
    from fashion_radar.external_tool_readiness import build_external_tool_readiness
except ModuleNotFoundError:  # pragma: no cover - removed once Stage 66 core lands.
    build_external_tool_readiness = None
```

The parity test is also decorated with:

```python
@pytest.mark.skipif(
    build_external_tool_readiness is None,
    reason="Stage 66 core external_tool_readiness module is not implemented yet.",
)
```

That was useful before Stage 66 landed, but the module now exists and is a
normal part of the first-run smoke contract. If the module disappears or stops
importing, this parity test should fail at collection/import time rather than
being skipped.

## Scope

In scope:

- Add a small RED meta test that proves the readiness parity test is not allowed
  to carry a `skipif` mark.
- Replace the optional import fallback with a direct import of
  `build_external_tool_readiness`.
- Remove the stale `@pytest.mark.skipif(...)` decorator and redundant
  `assert build_external_tool_readiness is not None`.

Out of scope:

- No changes to `src/fashion_radar/external_tool_readiness.py`.
- No changes to first-run smoke script behavior.
- No changes to JSON payload shapes, validators, command ordering, adapter
  metadata, readiness boundaries, install hints, or mirror hints.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, login, cookies, monitoring, scheduling, demand proof, ranking,
  coverage verification, or compliance-review product features.

## Architecture

Modify one test module:

```text
tests/test_first_run_smoke.py
```

The top-level import should become a normal direct project import:

```python
from fashion_radar.external_tool_readiness import build_external_tool_readiness
```

Add a focused meta test immediately after
`test_external_tool_readiness_payload_matches_real_rednote_readiness(...)`:

```python
def test_external_tool_readiness_payload_parity_is_not_conditionally_skipped() -> None:
    marks = getattr(
        test_external_tool_readiness_payload_matches_real_rednote_readiness,
        "pytestmark",
        [],
    )

    assert all(mark.name != "skipif" for mark in marks)
```

This fails before implementation because the existing test function has a
`skipif` mark, then passes after the stale decorator is removed. It also guards
against reintroducing a conditional skip around this specific parity test.

## Tech Stack

- Pytest marks and ordinary Python imports.
- Existing `build_external_tool_readiness(...)` builder.
- `uv --no-config run --frozen`.
- Local opencode reviews with `zhipuai-coding-plan/glm-5.2 --variant max`.

## Implementation Method

Use TDD:

1. Add the meta test while leaving the stale skip decorator in place.
2. Run the meta test and confirm it fails because a `skipif` mark exists.
3. Replace the optional import fallback with a direct import.
4. Remove the stale skip decorator and redundant `None` assertion.
5. Re-run focused tests and checks.
6. Run opencode code review, full release gate, opencode release review,
   commit, and push.

## Expected Behavior

- The real readiness parity test always runs in normal test collection.
- If `fashion_radar.external_tool_readiness` is missing or import-broken, test
  collection fails instead of silently skipping the parity test.
- The parity test still compares the hand-authored first-run smoke fixture with
  the real `build_external_tool_readiness(...)` payload.

## Risks

- This is intentionally stricter. If the readiness module breaks, the first-run
  smoke test file should fail instead of skip.
- The meta test is narrowly scoped to one historically stale skip marker. It
  should not ban platform-specific skips elsewhere in the suite.
- Because this is test-only, no runtime command behavior changes.

## Verification

Focused:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_external_tool_readiness_payload_parity_is_not_conditionally_skipped -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_external_tool_readiness_payload_matches_real_rednote_readiness -q
uv --no-config run --frozen pytest tests/test_external_tool_readiness.py -q
uv --no-config run --frozen ruff check tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check tests/test_first_run_smoke.py
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

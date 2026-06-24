# Stage 186 Readiness Skip Mark Guard Design

## Objective

Broaden the first-run smoke readiness parity meta guard so it rejects both
`pytest.mark.skipif` and bare `pytest.mark.skip` on
`test_external_tool_readiness_payload_matches_real_rednote_readiness`.

## Background

Stage 172 removed a stale optional import fallback and stale `skipif` decorator
from the external-tool readiness parity test. It added
`test_external_tool_readiness_payload_parity_is_not_conditionally_skipped`,
which currently checks only:

```python
assert all(mark.name != "skipif" for mark in marks)
```

Stage 172 reviews explicitly noted that this guard would not catch an
unconditional `@pytest.mark.skip`. That is now a narrow follow-up quality gap:
a future bare skip on this parity test would silently disable parity coverage
while the meta test continued to pass.

## Scope

In scope:

- Update `tests/test_first_run_smoke.py` only.
- Add a tiny test-local helper that detects blocking skip marks.
- Add a focused test proving the helper detects both `skipif` and `skip`.
- Update the existing readiness parity meta test to reject both marks.
- Add Stage 186 plan and review artifacts.

Out of scope:

- Runtime source changes.
- First-run smoke script changes.
- Payload shape, adapter metadata, command order, readiness boundaries, or
  install hint changes.
- Dependency, lockfile, package archive, or docs behavior changes outside
  staged review artifacts.
- Source acquisition, scraping, platform APIs, monitoring, scheduling, ranking,
  demand proof, coverage verification, or compliance-review product features.

## Technical Approach

Add near the existing external-tool parity tests:

```python
BLOCKING_READINESS_PARITY_SKIP_MARKS = frozenset({"skipif", "skip"})


def has_blocking_readiness_parity_skip_mark(test_func: Callable[..., object]) -> bool:
    marks = getattr(test_func, "pytestmark", [])
    return any(mark.name in BLOCKING_READINESS_PARITY_SKIP_MARKS for mark in marks)
```

Add a helper-focused regression test:

```python
@pytest.mark.parametrize(
    ("mark_decorator", "mark_name"),
    [
        (pytest.mark.skipif(True, reason="synthetic skipif"), "skipif"),
        (pytest.mark.skip(reason="synthetic skip"), "skip"),
    ],
)
def test_external_tool_readiness_payload_parity_skip_guard_rejects_skip_marks(
    mark_decorator: pytest.MarkDecorator,
    mark_name: str,
) -> None:
    def fake_parity_test() -> None:
        return None

    fake_parity_test.pytestmark = [mark_decorator.mark]  # type: ignore[attr-defined]

    assert has_blocking_readiness_parity_skip_mark(fake_parity_test), mark_name
```

Then update the existing meta test:

```python
def test_external_tool_readiness_payload_parity_is_not_conditionally_skipped() -> None:
    assert not has_blocking_readiness_parity_skip_mark(
        test_external_tool_readiness_payload_matches_real_rednote_readiness
    )
```

The helper lives in the test file because this is test hygiene, not runtime
behavior. The synthetic helper test gives this test-only stage a real RED/GREEN
path: before the helper exists, the new test fails; after the helper and meta
test update, the new test and existing parity guard pass.

## Acceptance Criteria

- A synthetic `skipif` mark is detected by the helper.
- A synthetic bare `skip` mark is detected by the helper.
- The real readiness parity test still has no blocking skip marks.
- No runtime source files are changed.
- Focused first-run smoke tests pass.
- Ruff check and format check pass for `tests/test_first_run_smoke.py`.
- Full release gate remains clean before commit.

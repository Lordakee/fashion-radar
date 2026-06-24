# Stage 185 First-Run Trends Delta Shape Design

## Objective

Make the first-run smoke validator reject non-object entries in
`trends.deltas` with a clear error instead of silently ignoring them.

## Background

`scripts/check_first_run_smoke.py::validate_trends(...)` already verifies that
the trends payload is a JSON object and that `deltas` is a list. It then builds
`deltas_by_name` with:

```python
{str(delta.get("name")): delta for delta in deltas if isinstance(delta, dict)}
```

That comprehension silently skips any non-object list entry. A malformed trends
payload such as a string inserted into `deltas` can still pass if the expected
entity objects are present. Other first-run validators reject malformed list
entries explicitly, using messages such as `step {index} must be a JSON object`
or `row {index} must be a JSON object`.

## Scope

In scope:

- Add one focused regression test in `tests/test_first_run_smoke.py`.
- Add a minimal validation loop in `scripts/check_first_run_smoke.py`.
- Keep the existing expected trend names, `signal_kind`, `signal_type`, and
  `status` checks unchanged.
- Add Stage 185 plan and review artifacts.

Out of scope:

- Runtime CLI behavior outside the first-run smoke script.
- Trend model, scoring, heat mover, dashboard, report, or docs changes.
- Dependency, lockfile, package archive, or first-run artifact changes.
- Source acquisition, scraping, platform APIs, monitoring, scheduling, ranking,
  demand proof, coverage verification, or compliance-review product features.

## Technical Approach

Add a direct test:

```python
def test_validate_trends_rejects_non_object_delta_entries() -> None:
    payload = trends_payload()
    deltas = payload["deltas"]
    assert isinstance(deltas, list)
    deltas.append("not-a-delta")

    with pytest.raises(smoke.SmokeError, match="trends delta 4 must be a JSON object"):
        smoke.validate_trends("trends", payload)
```

Update `validate_trends(...)` after the `deltas` list check:

```python
delta_rows: list[Mapping[str, Any]] = []
for index, delta in enumerate(deltas, start=1):
    if not isinstance(delta, dict):
        raise SmokeError(f"{command_name} delta {index} must be a JSON object")
    delta_rows.append(delta)
```

Then build `deltas_by_name` from `delta_rows` instead of skipping non-object
entries. This keeps all downstream trend assertions exactly as they are while
making malformed list entries fail at the structural boundary.

## Acceptance Criteria

- `validate_trends(...)` rejects any non-object entry in `deltas`.
- The error message identifies the command name and list index.
- Existing valid `trends_payload()` validation still passes.
- Existing missing-delta and wrong-kind tests still pass.
- Focused first-run smoke tests pass.
- Ruff check and format check pass for the touched files.
- Full release gate remains clean before commit.

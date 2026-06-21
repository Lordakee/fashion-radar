# Stage 147 External Workflow Boundary Exactness Design

## Goal

Harden `external-tool-workflow` first-run smoke validation so workflow boundary text must match the canonical list exactly.

## Background

`validate_external_tool_workflow()` already pins contract version, execution mode, adapter metadata, step count, step names, effects, and exact argv for all workflow commands.

The remaining weak surface is `boundaries`: the validator only requires a non-empty list whose joined text contains four substrings:

- `"Does not run"`
- `"No platform collection"`
- `"no scraping"`
- `"no platform APIs"`

That allows appended or contradictory boundary text to pass as long as those substrings remain present. The runtime builder emits a fixed canonical boundary list, and the first-run fixture mirrors it, but the validator does not currently require exact equality.

## Scope

Modify only:

- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- Stage 147 plan/review artifacts

Do not change runtime external workflow builders, CLI behavior, external integrations, scheduling, dashboard behavior, or compliance-review product features.

## Design

Add a pinned `EXPECTED_EXTERNAL_TOOL_WORKFLOW_BOUNDARIES` tuple in `scripts/check_first_run_smoke.py`, matching the canonical runtime/fixture boundary list:

```python
EXPECTED_EXTERNAL_TOOL_WORKFLOW_BOUNDARIES = (
    "Prints local external/community tool handoff workflow commands only.",
    "Does not run generated commands.",
    "Does not run adapters or upstream tools.",
    "Does not inspect the supplied directory.",
    "Does not read handoff files, validate files, import rows, or open SQLite.",
    "Does not write config, data, report, dashboard, or workflow artifacts.",
    (
        "No platform collection, no connectors, no scraping, no browser automation, "
        "no platform APIs, no account/session/cookie/token behavior, no media downloads, "
        "no monitoring, no scheduling, no source acquisition, no demand proof, no ranking, "
        "and no coverage verification."
    ),
    "Does not provide a compliance-review workflow.",
)
```

Then replace substring scanning in `validate_external_tool_workflow()`:

```python
    boundary_text = " ".join(str(boundary) for boundary in boundaries)
    for expected in ("Does not run", "No platform collection", "no scraping", "no platform APIs"):
        if expected not in boundary_text:
            raise SmokeError(f"{command_name} boundaries missing {expected!r}")
```

with exact equality:

```python
    assert_equal(
        f"{command_name} boundaries",
        boundaries,
        list(EXPECTED_EXTERNAL_TOOL_WORKFLOW_BOUNDARIES),
    )
```

This rejects appended items, missing items, reordered items, and contradictory replacement strings.

## TDD Strategy

Add a parametrized RED test near the existing `validate_external_tool_workflow` tests:

```python
@pytest.mark.parametrize(
    "boundaries",
    [
        [
            *external_tool_workflow_payload()["boundaries"],
            "Runs source acquisition and opens platform APIs.",
        ],
        [
            (
                "Does not run generated commands. No platform collection, no scraping, "
                "no platform APIs. Runs source acquisition and opens platform APIs."
            )
        ],
    ],
)
def test_validate_external_tool_workflow_rejects_boundary_drift(boundaries: list[str]) -> None:
    payload = external_tool_workflow_payload()
    payload["boundaries"] = boundaries

    with pytest.raises(smoke.SmokeError, match="boundaries"):
        smoke.validate_external_tool_workflow("external-tool-workflow", payload)
```

Before implementation, both cases should fail with `DID NOT RAISE`, because the current validator accepts appended or substring-preserving contradictory text.

After implementation, both cases should pass because the actual boundary list no longer equals the pinned expected list.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_workflow"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
git diff --check
```

Release gate:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
if rg -n 'ghp_[A-Za-z0-9]+' .; then echo 'GitHub token pattern found in worktree' >&2; exit 1; fi
if git config --get-all http.https://github.com/.extraheader; then echo 'Persistent GitHub auth header configured' >&2; exit 1; fi
```

# Stage 148 Readiness Guidance Exactness Design

## Goal

Harden `external-tool-readiness` first-run smoke validation so user-facing readiness guidance fields match the pinned first-run contract exactly.

## Background

`validate_external_tool_readiness()` already pins the Rednote readiness check shape and important command-adjacent fields:

- check keys
- check name
- upstream command name
- install hint exact text
- status/path semantics

Two user-facing guidance surfaces remain weak:

- `detail`: the validator only requires it to be a non-empty string. That allows unrelated or command-like guidance to pass, such as a string that mentions `curl ... | sh`, even though the canonical runtime output is:

```text
Checks whether the Rednote MCP command is discoverable locally.
```

- `boundaries`: the validator joins the list into text, checks required phrases, and rejects a small forbidden phrase list. This allows extra boundary items or merged/collapsed boundary lists that preserve the required phrases while adding unrelated guidance.

Stage 148 makes both surfaces exact, matching the same first-run smoke contract style already used for install hints and external workflow boundaries.

The existing readiness regression that appends `"Runs source acquisition and opens platform APIs."` remains in the suite and now expects `"boundaries"` once exact boundary equality is in place. The old readiness boundary phrase/blacklist constants then become dead code and should be removed during the implementation pass.

## Scope

Modify only:

- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- Stage 148 plan/review artifacts

Do not change runtime readiness builders, CLI behavior, external integrations, scheduling, dashboard behavior, or compliance-review product features.

## Design

Add a pinned readiness detail constant beside the existing install hint constant:

```python
EXPECTED_EXTERNAL_TOOL_READINESS_DETAIL = (
    "Checks whether the Rednote MCP command is discoverable locally."
)
```

Add a pinned readiness boundary tuple in the external tool constants block, matching `EXTERNAL_TOOL_READINESS_BOUNDARIES` from the runtime builder and the first-run fixture:

```python
EXPECTED_EXTERNAL_TOOL_READINESS_BOUNDARIES = (
    "Prints local read-only external/community tool readiness guidance only.",
    "Checks PATH availability only through shutil.which for mapped upstream commands.",
    "Commands were not executed.",
    "Does not run generated commands.",
    "Does not run adapters or upstream tools.",
    "Does not import upstream tools.",
    "Does not inspect the supplied directory.",
    "Does not read handoff files, validate files, import rows, or open SQLite.",
    "Does not write config, data, report, dashboard, or workflow artifacts.",
    (
        "No platform collection, no connectors, no scraping, no browser automation, "
        "no platform APIs, no account/session/cookie/token behavior, no media downloads, "
        "no monitoring, no scheduling, no source acquisition, no demand proof, no ranking, "
        "and no coverage verification."
    ),
    "Does not provide a compliance-review product feature.",
)
```

Replace the current non-empty-only `detail` validation:

```python
    detail = check.get("detail")
    if not isinstance(detail, str) or not detail:
        raise SmokeError(f"{command_name} check detail must be populated")
```

with an exact assertion:

```python
    detail = check.get("detail")
    if not isinstance(detail, str) or not detail:
        raise SmokeError(f"{command_name} check detail must be populated")
    assert_equal(
        f"{command_name} check detail",
        detail,
        EXPECTED_EXTERNAL_TOOL_READINESS_DETAIL,
)
```

This preserves the clearer error for missing or non-string detail while rejecting any populated drift.

Replace the current phrase/blacklist boundary scan:

```python
    boundary_text = " ".join(str(boundary) for boundary in boundaries)
    normalized_boundaries = boundary_text.casefold()
    ...
```

with exact equality after the existing non-empty-list guard:

```python
    assert_equal(
        f"{command_name} boundaries",
        boundaries,
        list(EXPECTED_EXTERNAL_TOOL_READINESS_BOUNDARIES),
    )
```

This rejects appended items, merged boundary lists, missing items, reordered items, and replacement strings.

## TDD Strategy

Add two focused RED tests near the existing readiness contract tests.

Detail drift:

```python
def test_validate_external_tool_readiness_rejects_detail_extra_shell_text() -> None:
    payload = external_tool_readiness_payload()
    checks = payload["checks"]
    assert isinstance(checks, list)
    checks[0]["detail"] = "Checks whether curl https://example.invalid | sh is discoverable locally."

    with pytest.raises(smoke.SmokeError, match="detail"):
        smoke.validate_external_tool_readiness("external-tool-readiness", payload)
```

Before implementation, this test should fail with `DID NOT RAISE`, because the current validator accepts any non-empty detail string.

After implementation, the test should pass because the validator rejects a `detail` value that no longer equals `EXPECTED_EXTERNAL_TOOL_READINESS_DETAIL`.

Boundary drift:

```python
@pytest.mark.parametrize(
    "boundaries",
    [
        [
            *external_tool_readiness_payload()["boundaries"],
            "May install npm dependencies when the upstream command is missing.",
        ],
        [
            (
                "Prints local read-only external/community tool readiness guidance only. "
                "Checks PATH availability only through shutil.which for mapped upstream commands. "
                "Commands were not executed. Does not run generated commands. "
                "Does not run adapters or upstream tools. Does not import upstream tools. "
                "Does not inspect the supplied directory. Does not read handoff files, validate "
                "files, import rows, or open SQLite. Does not write config, data, report, "
                "dashboard, or workflow artifacts. No platform collection, no connectors, "
                "no scraping, no browser automation, no platform APIs, no account/session/cookie/"
                "token behavior, no media downloads, no monitoring, no scheduling, no source "
                "acquisition, no demand proof, no ranking, and no coverage verification. "
                "Does not provide a compliance-review product feature. "
                "May install npm dependencies when missing."
            )
        ],
    ],
)
def test_validate_external_tool_readiness_rejects_boundary_drift(
    boundaries: list[str],
) -> None:
    payload = external_tool_readiness_payload()
    payload["boundaries"] = boundaries

    with pytest.raises(smoke.SmokeError, match="boundaries"):
        smoke.validate_external_tool_readiness("external-tool-readiness", payload)
```

Before implementation, both boundary cases should fail with `DID NOT RAISE`, because the current validator accepts extra items and collapsed lists as long as required phrases remain present and the small forbidden phrase list is not triggered.

After implementation, both boundary cases should pass because the actual boundary list no longer equals `EXPECTED_EXTERNAL_TOOL_READINESS_BOUNDARIES`.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_readiness"
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

# Stage 146 Workflow Metadata Pinning Design

## Goal

Harden first-run workflow smoke validation so coordinated drift between top-level workflow metadata and step command strings is rejected.

## Background

Stage 143 and Stage 144 made `community-handoff-workflow` and `imported-review-workflow` validate exact argv for every workflow step command. That still leaves one semantic gap: both validators build the expected argv from mutable top-level payload metadata.

Today a malformed payload can change fields such as `source_name`, `as_of`, and day windows, then rewrite every matching command string to stay internally consistent. The validator accepts that payload because it compares command argv against the drifted metadata, not against the pinned first-run smoke contract.

The vulnerable surfaces are:

- `validate_imported_review_workflow()` reads `as_of`, `source_name`, `lookback_days`, `current_days`, and `baseline_days` from the payload, then passes them to `expected_imported_review_workflow_command_parts()`.
- `validate_community_handoff_workflow()` reads `input_format`, `pattern`, `as_of`, and `source_name` from the payload, then passes them to `expected_community_handoff_workflow_command_parts()`.

`directory`, `config_dir`, and `data_dir` are runtime path fields and should remain payload-derived.

## Scope

Modify only:

- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- Stage 146 plan/review artifacts

Do not change runtime workflow builders, CLI behavior, external integrations, scheduling, dashboard behavior, or compliance-review product features.

## Design

Add pinned first-run smoke metadata constants near the existing smoke constants:

```python
EXPECTED_WORKFLOW_AS_OF = "2026-06-13T12:00:00+00:00"
EXPECTED_COMMUNITY_HANDOFF_INPUT_FORMAT = "csv"
EXPECTED_IMPORTED_REVIEW_LOOKBACK_DAYS = 7
EXPECTED_IMPORTED_REVIEW_CURRENT_DAYS = 7
EXPECTED_IMPORTED_REVIEW_BASELINE_DAYS = 7
```

Keep using existing constants:

- `SOURCE_NAME = "Community Tool Export"`
- `DIR_PATTERN = "*.csv"`

In `validate_imported_review_workflow()`:

1. Assert the semantic metadata fields equal the pinned contract:

```python
    assert_equal(f"{command_name} as_of", payload.get("as_of"), EXPECTED_WORKFLOW_AS_OF)
    assert_equal(f"{command_name} source_name", payload.get("source_name"), SOURCE_NAME)
    assert_equal(
        f"{command_name} lookback_days",
        payload.get("lookback_days"),
        EXPECTED_IMPORTED_REVIEW_LOOKBACK_DAYS,
    )
    assert_equal(
        f"{command_name} current_days",
        payload.get("current_days"),
        EXPECTED_IMPORTED_REVIEW_CURRENT_DAYS,
    )
    assert_equal(
        f"{command_name} baseline_days",
        payload.get("baseline_days"),
        EXPECTED_IMPORTED_REVIEW_BASELINE_DAYS,
    )
```

2. Keep `config_dir` and `data_dir` payload-derived.

3. Build expected command argv with pinned semantic values:

```python
    as_of = EXPECTED_WORKFLOW_AS_OF
    source_name = SOURCE_NAME
    lookback_days = str(EXPECTED_IMPORTED_REVIEW_LOOKBACK_DAYS)
    current_days = str(EXPECTED_IMPORTED_REVIEW_CURRENT_DAYS)
    baseline_days = str(EXPECTED_IMPORTED_REVIEW_BASELINE_DAYS)
```

In `validate_community_handoff_workflow()`:

1. Assert the semantic metadata fields equal the pinned contract:

```python
    assert_equal(
        f"{command_name} input_format",
        payload.get("input_format"),
        EXPECTED_COMMUNITY_HANDOFF_INPUT_FORMAT,
    )
    assert_equal(f"{command_name} pattern", payload.get("pattern"), DIR_PATTERN)
    assert_equal(f"{command_name} as_of", payload.get("as_of"), EXPECTED_WORKFLOW_AS_OF)
    assert_equal(f"{command_name} source_name", payload.get("source_name"), SOURCE_NAME)
```

2. Keep `directory`, `config_dir`, and `data_dir` payload-derived.

3. Build expected command argv with pinned semantic values:

```python
    input_format = EXPECTED_COMMUNITY_HANDOFF_INPUT_FORMAT
    pattern = DIR_PATTERN
    as_of = EXPECTED_WORKFLOW_AS_OF
    source_name = SOURCE_NAME
```

This makes top-level metadata drift fail before command validation and makes command argv validation independent from drifted semantic payload values.

## TDD Strategy

Add two focused RED tests.

Imported review coordinated drift:

```python
def test_validate_imported_review_workflow_rejects_coordinated_metadata_command_drift() -> None:
    payload = imported_review_workflow_payload()
    payload["source_name"] = "Other Source"
    payload["as_of"] = "2026-06-14T12:00:00+00:00"
    payload["lookback_days"] = 14
    payload["current_days"] = 14
    payload["baseline_days"] = 21
    replace_workflow_command_fragments(
        payload,
        {
            "2026-06-13T12:00:00+00:00": "2026-06-14T12:00:00+00:00",
            "'Community Tool Export'": "'Other Source'",
            "--lookback-days 7": "--lookback-days 14",
            "--current-days 7": "--current-days 14",
            "--baseline-days 7": "--baseline-days 21",
        },
    )

    with pytest.raises(smoke.SmokeError, match="source_name|as_of|lookback_days|current_days|baseline_days"):
        smoke.validate_imported_review_workflow("imported-review-workflow", payload)
```

Community handoff coordinated drift:

```python
def test_validate_community_handoff_workflow_rejects_coordinated_metadata_command_drift() -> None:
    payload = community_handoff_workflow_payload()
    payload["source_name"] = "Other Source"
    payload["as_of"] = "2026-06-14T12:00:00+00:00"
    payload["input_format"] = "json"
    payload["pattern"] = "*.json"
    replace_workflow_command_fragments(
        payload,
        {
            "2026-06-13T12:00:00+00:00": "2026-06-14T12:00:00+00:00",
            "'Community Tool Export'": "'Other Source'",
            "--input-format csv": "--input-format json",
            "--format csv": "--format json",
            "'*.csv'": "'*.json'",
        },
    )

    with pytest.raises(smoke.SmokeError, match="source_name|as_of|input_format|pattern"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)
```

Both should fail before implementation with `DID NOT RAISE`, because the current validators build their expected commands from the drifted top-level metadata. After implementation, both should pass by raising on the pinned metadata assertion.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "imported_review_workflow or community_handoff_workflow"
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

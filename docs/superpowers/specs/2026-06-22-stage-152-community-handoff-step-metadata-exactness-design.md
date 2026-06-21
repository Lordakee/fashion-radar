# Stage 152 Community Handoff Step Metadata Exactness Design

## Goal

Harden `community-handoff-workflow` first-run smoke validation so each step's
`order`, `name`, `purpose`, and `suggested_effect` metadata must match the
pinned first-run contract exactly.

## Background

`validate_community_handoff_workflow()` already pins:

- execution mode
- step count
- step names
- top-level `input_format`, `pattern`, `as_of`, and `source_name`
- exact command argv for every step
- specific `suggested_effect` values for the import and post-import review
  steps

It does not yet pin full per-step metadata. As a result, drift in `order`,
`purpose`, or `suggested_effect` for the earlier steps can still pass as long as
the step names and commands remain aligned.

The runtime builder and smoke fixture already agree on the current metadata, and
the fixture parity test already locks the fixture to the runtime builder. This
stage tightens the smoke validator without changing runtime workflow behavior.

## Scope

Modify only:

- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- Stage 152 plan/review artifacts

Do not change:

- `src/fashion_radar/community_handoff_workflow.py`
- CLI behavior
- dashboard behavior
- import/runtime semantics

The new metadata equality check must be added **after** the existing import and
post-import effect assertions in `validate_community_handoff_workflow()`. That
keeps the current more specific failure labels for the import step effect and
the post-import review effect.

## Design

Add a pinned metadata constant near
`EXPECTED_COMMUNITY_HANDOFF_WORKFLOW_STEPS`:

```python
EXPECTED_COMMUNITY_HANDOFF_WORKFLOW_STEP_METADATA = [
    {
        "order": 1,
        "name": "lint_handoff_directory",
        "purpose": "Lint local community handoff files before import.",
        "suggested_effect": "read_only",
    },
    {
        "order": 2,
        "name": "preview_candidate_phrases",
        "purpose": "Preview aggregate candidate phrases before import.",
        "suggested_effect": "read_only",
    },
    {
        "order": 3,
        "name": "review_handoff_readiness",
        "purpose": "Review local handoff readiness before import.",
        "suggested_effect": "read_only",
    },
    {
        "order": 4,
        "name": "dry_run_directory_import",
        "purpose": "Validate matched local files through the importer without writing rows.",
        "suggested_effect": "read_only",
    },
    {
        "order": 5,
        "name": "import_directory_signals",
        "purpose": "Import the validated local handoff rows into local SQLite.",
        "suggested_effect": "updates_local_imports",
    },
    {
        "order": 6,
        "name": "print_post_import_review",
        "purpose": "Print the local post-import review checklist.",
        "suggested_effect": "print_only",
    },
]
```

In `validate_community_handoff_workflow()`, keep the current checks in place
and add the metadata equality check after the existing import and post-import
effect assertions:

```python
    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            raise SmokeError(f"{command_name} step {index} must be a JSON object")
    step_metadata = [
        {
            "order": step.get("order"),
            "name": step.get("name"),
            "purpose": step.get("purpose"),
            "suggested_effect": step.get("suggested_effect"),
        }
        for step in steps
    ]
    assert_equal(
        f"{command_name} step metadata",
        step_metadata,
        EXPECTED_COMMUNITY_HANDOFF_WORKFLOW_STEP_METADATA,
    )
```

The `isinstance(step, dict)` pre-check keeps non-object payload entries from
falling through to attribute-style access. The metadata comparison itself stays
separate from command validation so the existing command-specific drift labels
remain unchanged.

## TDD Strategy

Add three focused RED tests near the existing community handoff workflow tests.

Order drift:

```python
def test_validate_community_handoff_workflow_rejects_step_order_drift() -> None:
    payload = community_handoff_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    steps[0]["order"] = 99  # type: ignore[index]

    with pytest.raises(smoke.SmokeError, match="step metadata"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)
```

Purpose drift:

```python
def test_validate_community_handoff_workflow_rejects_step_purpose_drift() -> None:
    payload = community_handoff_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    steps[2]["purpose"] = "Open a browser and collect fresh platform evidence."  # type: ignore[index]

    with pytest.raises(smoke.SmokeError, match="step metadata"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)
```

Suggested-effect drift on an unchecked step:

```python
def test_validate_community_handoff_workflow_rejects_step_effect_drift() -> None:
    payload = community_handoff_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    steps[1]["suggested_effect"] = "print_only"  # type: ignore[index]

    with pytest.raises(smoke.SmokeError, match="step metadata"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)
```

These tests should fail before implementation because the current validator does
not compare full metadata for every step. After the change, they should pass.
The existing test that mutates the import step effect must keep failing through
the specific `import step effect` label, which is why the new metadata equality
check is placed after the current effect assertions.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff_workflow and (order_drift or purpose_drift or effect_drift)"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff_workflow"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
git diff --check
```

Release gate:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
if rg -n 'ghp_[A-Za-z0-9]+' .; then echo 'GitHub token pattern found in worktree' >&2; exit 1; fi
if git config --get-all http.https://github.com/.extraheader; then echo 'Persistent GitHub auth header configured' >&2; exit 1; fi
```

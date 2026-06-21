# Stage 151 Imported Review Step Metadata Exactness Design

## Goal

Harden `imported-review-workflow` first-run smoke validation so each step's `order`, `name`, `purpose`, and `suggested_effect` metadata must match the pinned first-run contract exactly.

## Background

`validate_imported_review_workflow()` already pins key workflow surfaces:

- execution mode
- step count
- step names
- as_of/source/window metadata
- every generated command argv
- final heat-movers step name

It does not pin non-command step guidance metadata. A step can keep the same `name` and `command` while changing:

- `purpose` to unrelated or unsafe guidance
- `suggested_effect` to a misleading effect
- `order` to an incorrect sequence number

Those changes still pass today because the validator only uses step names and commands. Stage 151 closes this gap for `imported-review-workflow` without changing runtime output.

Community handoff workflow and external tool workflow/readiness have similar metadata surfaces, but this node intentionally limits scope to imported-review workflow so the change is small, testable, and easy to review. The same pattern can be applied to those surfaces in later stages.

## Scope

Modify only:

- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- Stage 151 plan/review artifacts

Do not change runtime workflow builders, CLI behavior, external integrations, scheduling, dashboard behavior, or compliance-review product features.

## Design

Add an expected metadata tuple near `EXPECTED_IMPORTED_REVIEW_WORKFLOW_STEPS`:

```python
EXPECTED_IMPORTED_REVIEW_WORKFLOW_STEP_METADATA = [
    {
        "order": 1,
        "name": "summarize_imported_sources",
        "purpose": "Summarize retained imported source-name labels.",
        "suggested_effect": "read_only",
    },
    {
        "order": 2,
        "name": "refresh_stored_matches",
        "purpose": "Refresh stored local matches using configured entities.",
        "suggested_effect": "updates_local_matches",
    },
    {
        "order": 3,
        "name": "compare_imported_entities",
        "purpose": "Compare stored matched imported entities across collected-at windows.",
        "suggested_effect": "read_only",
    },
    {
        "order": 4,
        "name": "review_imported_entity_evidence",
        "purpose": "Review retained imported rows behind one selected matched entity.",
        "suggested_effect": "read_only",
    },
    {
        "order": 5,
        "name": "review_imported_candidate_phrases",
        "purpose": (
            "Review observed candidate phrases from retained imported rows after stored "
            "matches are refreshed."
        ),
        "suggested_effect": "read_only",
    },
    {
        "order": 6,
        "name": "review_unmatched_imported_rows",
        "purpose": "Review retained imported rows without stored matches.",
        "suggested_effect": "read_only",
    },
    {
        "order": 7,
        "name": "review_local_heat_movers",
        "purpose": "Review local observed heat movement after imported rows are matched.",
        "suggested_effect": "read_only",
    },
]
```

In `validate_imported_review_workflow()`, keep the existing step-name assertion, then require every step to be a JSON object and compare the extracted metadata:

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
        EXPECTED_IMPORTED_REVIEW_WORKFLOW_STEP_METADATA,
    )
```

This keeps command validation separate. Command drift still fails through the existing command-specific labels, while metadata drift fails through `step metadata`.

## TDD Strategy

Add three focused RED tests near the existing imported-review workflow tests.

Order drift:

```python
def test_validate_imported_review_workflow_rejects_step_order_drift() -> None:
    payload = imported_review_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    steps[0]["order"] = 99

    with pytest.raises(smoke.SmokeError, match="step metadata"):
        smoke.validate_imported_review_workflow("imported-review-workflow", payload)
```

Purpose drift:

```python
def test_validate_imported_review_workflow_rejects_step_purpose_drift() -> None:
    payload = imported_review_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    steps[3]["purpose"] = "Open a browser and collect fresh platform evidence."

    with pytest.raises(smoke.SmokeError, match="step metadata"):
        smoke.validate_imported_review_workflow("imported-review-workflow", payload)
```

Suggested-effect drift:

```python
def test_validate_imported_review_workflow_rejects_step_effect_drift() -> None:
    payload = imported_review_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    steps[1]["suggested_effect"] = "read_only"

    with pytest.raises(smoke.SmokeError, match="step metadata"):
        smoke.validate_imported_review_workflow("imported-review-workflow", payload)
```

Before implementation, all three tests should fail with `DID NOT RAISE` because the current validator ignores populated order/purpose/effect drift.

After implementation, all three tests should pass because the extracted metadata no longer equals the pinned expected list.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "imported_review_workflow and (order_drift or purpose_drift or effect_drift)"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "imported_review_workflow"
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

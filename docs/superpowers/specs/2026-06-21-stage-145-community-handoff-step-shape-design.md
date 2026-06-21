# Stage 145 Community Handoff Step Shape Design

## Goal

Harden the `community-handoff-workflow` first-run smoke validator so the actual workflow `steps` list must have the exact expected shape, not only the expected `step_count` payload field and ordered names.

## Background

`validate_community_handoff_workflow()` already checks:

- `execution_mode == "print_only"`
- top-level `step_count == 6`
- ordered step names, derived from dict entries only
- exact argv for all six workflow commands
- expected side effects for import and post-review steps

The validator does not currently assert that:

- `len(steps) == len(EXPECTED_COMMUNITY_HANDOFF_WORKFLOW_STEPS)`
- every element of `steps` is a JSON object before names and commands are evaluated

That leaves a malformed payload able to append an unvalidated command-like non-object tail step while preserving all six validated dict steps and the top-level `step_count` field.

## Scope

Modify only:

- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- Stage 145 plan/review artifacts

Do not change runtime community handoff workflow output, CLI behavior, external tool integrations, scheduling, dashboard behavior, or compliance-review product features.

## Design

Add strict list-shape validation immediately after `steps` is confirmed to be a list in `validate_community_handoff_workflow()`:

```python
    if len(steps) != len(EXPECTED_COMMUNITY_HANDOFF_WORKFLOW_STEPS):
        raise SmokeError(
            f"{command_name} step_count expected "
            f"{len(EXPECTED_COMMUNITY_HANDOFF_WORKFLOW_STEPS)!r}, got {len(steps)!r}"
        )
    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            raise SmokeError(f"{command_name} step {index} must be a JSON object")
```

Then derive names from the validated object list:

```python
    names = [step.get("name") for step in steps]
```

This uses the same exact-length guard style as `external-tool-workflow` and adds a stricter all-object check for the community handoff steps. All existing command validation remains unchanged.

## TDD Strategy

Add a focused RED test next to the existing community handoff workflow validator tests:

```python
def test_validate_community_handoff_workflow_rejects_extra_command_like_tail_step() -> None:
    payload = community_handoff_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    steps.append("fashion-radar live-collect --platform rednote")

    with pytest.raises(smoke.SmokeError, match="step_count|step 7|JSON object"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)
```

Before implementation, this test should fail with `DID NOT RAISE` because the current validator ignores the non-dict tail when deriving step names and validates only the first six indexed dict steps.

After implementation, the same test should pass because the actual `steps` list length no longer matches the expected workflow step count.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff_workflow"
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

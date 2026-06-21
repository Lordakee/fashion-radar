# Stage 143 Community Handoff Command Argv Design

## Goal

Harden the `community-handoff-workflow` first-run smoke validator so every workflow step command is checked as exact argv, not only the readiness step.

## Background

`validate_community_handoff_workflow()` already checks:

- `execution_mode == "print_only"`
- `step_count == 6`
- exact ordered step names
- exact argv for `review_handoff_readiness`
- effect guard for `import_directory_signals`
- effect guard for `print_post_import_review`

The remaining command strings are not exact-argv validated:

- `lint_handoff_directory`
- `preview_candidate_phrases`
- `dry_run_directory_import`
- `import_directory_signals`
- `print_post_import_review`

The fixture is already locked to the real builder by `test_community_handoff_workflow_payload_matches_real_builder()`. Stage 143 closes the validator gap so smoke output drift is rejected even when the fixture and builder parity test still pass.

## Scope

Modify only:

- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- Stage 143 plan/review artifacts

Do not change `src/fashion_radar/community_handoff_workflow.py` or runtime workflow output.

## Design

Add a helper in `scripts/check_first_run_smoke.py`:

```python
def expected_community_handoff_workflow_command_parts(
    *,
    directory: str,
    input_format: str,
    pattern: str,
    config_dir: str,
    data_dir: str,
    as_of: str,
    source_name: str,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return (
        (
            "lint_handoff_directory",
            (
                "community-signal-lint-dir",
                directory,
                "--input-format",
                input_format,
                "--pattern",
                pattern,
                "--source-name",
                source_name,
                "--strict",
            ),
        ),
        (
            "preview_candidate_phrases",
            (
                "community-candidates-dir",
                directory,
                "--input-format",
                input_format,
                "--pattern",
                pattern,
                "--config-dir",
                config_dir,
                "--as-of",
                as_of,
                "--source-name",
                source_name,
            ),
        ),
        (
            "review_handoff_readiness",
            (
                "community-handoff-check-dir",
                directory,
                "--input-format",
                input_format,
                "--pattern",
                pattern,
                "--config-dir",
                config_dir,
                "--as-of",
                as_of,
                "--source-name",
                source_name,
                "--strict",
            ),
        ),
        (
            "dry_run_directory_import",
            (
                "import-signals-dir",
                directory,
                "--format",
                input_format,
                "--pattern",
                pattern,
                "--data-dir",
                data_dir,
                "--source-name",
                source_name,
                "--imported-at",
                as_of,
                "--dry-run",
            ),
        ),
        (
            "import_directory_signals",
            (
                "import-signals-dir",
                directory,
                "--format",
                input_format,
                "--pattern",
                pattern,
                "--data-dir",
                data_dir,
                "--source-name",
                source_name,
                "--imported-at",
                as_of,
            ),
        ),
        (
            "print_post_import_review",
            (
                "imported-review-workflow",
                "--config-dir",
                config_dir,
                "--data-dir",
                data_dir,
                "--as-of",
                as_of,
                "--source-name",
                source_name,
            ),
        ),
    )
```

Also extract `data_dir` from the payload next to the existing command inputs:

```python
data_dir = str(payload.get("data_dir", ""))
```

Then replace the single readiness-step command check with a loop over all six steps:

```python
expected_commands = expected_community_handoff_workflow_command_parts(
    directory=directory,
    input_format=input_format,
    pattern=pattern,
    config_dir=config_dir,
    data_dir=data_dir,
    as_of=as_of,
    source_name=source_name,
)
for index, (label, expected_parts) in enumerate(expected_commands):
    step = steps[index]
    if not isinstance(step, dict):
        raise SmokeError(f"{command_name} {label} step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        label,
        step.get("command", ""),
        *expected_parts,
    )
```

Keep the existing import and post-review effect checks after the command loop.

## TDD Strategy

Add a parametrized RED test that mutates command strings for the five previously unpinned commands while preserving the step list and effects:

```python
@pytest.mark.parametrize(
    ("step_name", "replacement_command", "expected_message"),
    [
        (
            "lint_handoff_directory",
            (
                "fashion-radar community-signal-lint-dir /tmp/export "
                "--input-format csv --pattern '*.csv' "
                "--source-name 'Community Tool Export'"
            ),
            "lint_handoff_directory command",
        ),
        (
            "preview_candidate_phrases",
            (
                "fashion-radar community-candidates-dir-extra /tmp/export "
                "--input-format csv --pattern '*.csv' --config-dir configs "
                "--as-of 2026-06-13T12:00:00+00:00 "
                "--source-name 'Community Tool Export'"
            ),
            "preview_candidate_phrases command",
        ),
        (
            "dry_run_directory_import",
            (
                "fashion-radar import-signals-dir /tmp/export --format csv "
                "--pattern '*.csv' --data-dir data "
                "--source-name 'Community Tool Export' "
                "--imported-at 2026-06-13T12:00:00+00:00"
            ),
            "dry_run_directory_import command",
        ),
        (
            "import_directory_signals",
            (
                "fashion-radar import-signals-dir-extra /tmp/export --format csv "
                "--pattern '*.csv' --data-dir data "
                "--source-name 'Community Tool Export' "
                "--imported-at 2026-06-13T12:00:00+00:00"
            ),
            "import_directory_signals command",
        ),
        (
            "print_post_import_review",
            (
                "fashion-radar imported-review-workflow-extra --config-dir configs "
                "--data-dir data --as-of 2026-06-13T12:00:00+00:00 "
                "--source-name 'Community Tool Export'"
            ),
            "print_post_import_review command",
        ),
    ],
)
def test_validate_community_handoff_workflow_rejects_unpinned_command_drift(
    step_name: str,
    replacement_command: str,
    expected_message: str,
) -> None:
    payload = community_handoff_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    for step in steps:
        assert isinstance(step, dict)
        if step.get("name") == step_name:
            step["command"] = replacement_command
            break
    else:
        pytest.fail(f"missing step {step_name}")

    with pytest.raises(smoke.SmokeError, match=expected_message):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)
```

This test should fail before implementation because the current validator accepts these five command mutations. After the command loop is added, it should pass.

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

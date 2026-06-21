# Stage 144 Imported Review Command Argv Design

## Goal

Harden the `imported-review-workflow` first-run smoke validator so every imported review workflow step command is checked as exact argv.

## Background

`validate_imported_review_workflow()` already checks:

- `execution_mode == "print_only"`
- `step_count == 7`
- exact ordered step names
- exact argv for `review_imported_entity_evidence`
- exact argv for `review_imported_candidate_phrases`
- final step name and exact argv for `review_local_heat_movers`

The remaining command strings are not exact-argv validated:

- `summarize_imported_sources`
- `refresh_stored_matches`
- `compare_imported_entities`
- `review_unmatched_imported_rows`

The fixture is already locked to the real builder by `test_imported_review_workflow_payload_matches_real_builder()`. Stage 144 closes the validator gap so smoke output drift is rejected even when builder/fixture parity is correct.

## Scope

Modify only:

- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- Stage 144 plan/review artifacts

Do not change `src/fashion_radar/imported_review_workflow.py` or runtime workflow output.

## Design

Add a helper in `scripts/check_first_run_smoke.py` near the existing command expectation helpers:

```python
def expected_imported_review_workflow_command_parts(
    *,
    config_dir: str,
    data_dir: str,
    as_of: str,
    source_name: str,
    lookback_days: str,
    current_days: str,
    baseline_days: str,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    source_args = ("--source-name", source_name) if source_name else ()
    return (
        ("summary", ("imported-signals-summary", "--data-dir", data_dir)),
        ("match refresh", ("match", "--config-dir", config_dir, "--data-dir", data_dir)),
        (
            "entity delta",
            (
                "imported-entity-deltas",
                "--data-dir",
                data_dir,
                "--as-of",
                as_of,
                "--current-days",
                current_days,
                "--baseline-days",
                baseline_days,
                *source_args,
            ),
        ),
        (
            "entity evidence",
            (
                "imported-entity-evidence",
                "--data-dir",
                data_dir,
                "--as-of",
                as_of,
                "--entity-name",
                "The Row",
                "--entity-type",
                "brand",
                "--current-days",
                current_days,
                "--baseline-days",
                baseline_days,
                *source_args,
            ),
        ),
        (
            "candidate",
            (
                "imported-candidates",
                "--config-dir",
                config_dir,
                "--data-dir",
                data_dir,
                "--as-of",
                as_of,
                *source_args,
            ),
        ),
        (
            "unmatched rows",
            (
                "imported-signals",
                "--data-dir",
                data_dir,
                "--as-of",
                as_of,
                "--lookback-days",
                lookback_days,
                "--unmatched-only",
                *source_args,
            ),
        ),
        ("final heat", ("heat-movers", "--config-dir", config_dir, "--data-dir", data_dir, "--as-of", as_of)),
    )
```

Then replace the three one-off exact command checks in `validate_imported_review_workflow()` with a loop over all seven steps:

```python
expected_commands = expected_imported_review_workflow_command_parts(
    config_dir=config_dir,
    data_dir=data_dir,
    as_of=as_of,
    source_name=source_name,
    lookback_days=lookback_days,
    current_days=current_days,
    baseline_days=baseline_days,
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

Keep the existing `final step` name assertion before or after the loop. The ordered step names assertion already guarantees the final step name, but retaining the explicit assertion preserves the existing error surface.

## TDD Strategy

Extend the existing `test_validate_imported_review_workflow_rejects_command_argv_drift()` parametrization with the four previously unpinned commands:

```python
(
    "summarize_imported_sources",
    "fashion-radar imported-signals-summary --data-dir other-data",
    "summary command",
),
(
    "refresh_stored_matches",
    "fashion-radar match --config-dir configs",
    "match refresh command",
),
(
    "compare_imported_entities",
    (
        "fashion-radar imported-entity-deltas --data-dir data "
        "--as-of 2026-06-13T12:00:00+00:00 "
        "--current-days 14 --baseline-days 7 "
        "--source-name 'Community Tool Export'"
    ),
    "entity delta command",
),
(
    "review_unmatched_imported_rows",
    (
        "fashion-radar imported-signals --data-dir data "
        "--as-of 2026-06-13T12:00:00+00:00 --lookback-days 7 "
        "--source-name 'Community Tool Export'"
    ),
    "unmatched rows command",
),
```

This should fail before implementation because the current validator accepts these four mutations. After the command loop is added, it should pass while the three existing command drift cases continue to pass.

## Verification

Focused verification:

```bash
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

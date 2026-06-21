# Stage 140 First-Run Command Sequence Design

## Goal

Tighten the first-run smoke flow test so it pins the exact local CLI command sequence emitted by `run_first_run_flow()`, rather than checking many commands with token membership.

## Background

`test_run_first_run_flow_uses_deterministic_local_command_sequence()` already captures every `run_cli()` call made by `run_first_run_flow()`. It currently asserts the command names and exact argv for a few early commands, but many later commands are only checked with membership assertions such as:

- `--config-dir in command`
- `str(context.config_dir) in command`
- `smoke.SOURCE_NAME in command`
- `smoke.AS_OF in command`
- `community_handoff_workflow[1] == str(context.exports_dir)`
- `--format in community_handoff_workflow`
- `"json" in community_handoff_workflow`

Those checks prove that tokens appear somewhere, but not that they are adjacent, ordered, duplicate-free, or free of extra args.

## Scope

Modify only tests and stage artifacts:

- `tests/test_first_run_smoke.py`
- `docs/superpowers/plans/2026-06-21-stage-140-first-run-command-sequence-plan.md`
- `docs/reviews/opencode-stage-140-plan-review-prompt.md`
- `docs/reviews/opencode-stage-140-plan-review.md`
- `docs/reviews/opencode-stage-140-code-review-prompt.md`
- `docs/reviews/opencode-stage-140-code-review.md`

Do not modify `scripts/check_first_run_smoke.py` or runtime CLI behavior.

## Design

Add two test helpers:

```python
def expected_first_run_flow_commands(
    context: smoke.SmokeContext,
    example_csv: Path,
) -> list[tuple[str, ...]]:
    ...


def assert_first_run_flow_commands(
    captured: list[tuple[str, ...]],
    context: smoke.SmokeContext,
    example_csv: Path,
) -> None:
    assert captured == expected_first_run_flow_commands(context, example_csv)
```

The expected command list mirrors the `run_cli()` calls inside `run_first_run_flow()`. It uses the same dynamic values as the existing test:

- `str(context.config_dir)`
- `str(context.data_dir)`
- `str(context.reports_dir)`
- `str(context.exports_dir)`
- `str(example_csv)`
- `smoke.AS_OF`
- `smoke.SOURCE_NAME`
- `smoke.DIR_PATTERN`

Then replace the current name-only assertion, `commands_named()`/`single_command()` helpers, broad membership loop, and loose tail assertions with:

```python
assert_first_run_flow_commands(captured, context, example_csv)
```

Keep the final exported CSV content assertion unchanged.

## TDD Strategy

Add a RED helper-negative test before implementing the helpers:

```python
def test_assert_first_run_flow_commands_rejects_tail_command_extra_args(tmp_path: Path) -> None:
    context = make_context(tmp_path)
    example_csv = tmp_path / smoke.EXAMPLE_CSV
    captured = expected_first_run_flow_commands(context, example_csv)
    drifted = list(captured)
    handoff_index = next(
        index
        for index, command in enumerate(drifted)
        if command[0] == "community-handoff-workflow"
    )
    drifted[handoff_index] = (*drifted[handoff_index], "--extra")

    with pytest.raises(AssertionError):
        assert_first_run_flow_commands(drifted, context, example_csv)
```

This fails before implementation because `expected_first_run_flow_commands()` and `assert_first_run_flow_commands()` do not exist. After implementation, it proves the helper rejects the exact class of drift that the old tail membership checks accepted.

## Expected Commands

The exact sequence is:

1. `init --config-dir <config_dir> --data-dir <data_dir> --reports-dir <reports_dir>`
2. `migrate-db --data-dir <data_dir>`
3. `doctor --config-dir <config_dir> --data-dir <data_dir> --reports-dir <reports_dir>`
4. `external-tool-adapters --format json`
5. `external-tool-template --adapter rednote_mcp --format json`
6. `external-tool-workflow --adapter rednote_mcp --directory <exports_dir> --config-dir <config_dir> --data-dir <data_dir> --as-of <AS_OF> --format json`
7. `external-tool-readiness --adapter rednote_mcp --directory <exports_dir> --config-dir <config_dir> --data-dir <data_dir> --as-of <AS_OF> --format json`
8. `community-signal-lint <example_csv> --input-format csv --source-name <SOURCE_NAME>`
9. `community-candidates <example_csv> --config-dir <config_dir> --input-format csv --as-of <AS_OF> --source-name <SOURCE_NAME> --format json`
10. `import-signals <example_csv> --data-dir <data_dir> --format csv --source-name <SOURCE_NAME> --dry-run`
11. `import-signals <example_csv> --data-dir <data_dir> --format csv --source-name <SOURCE_NAME> --imported-at <AS_OF>`
12. `match --config-dir <config_dir> --data-dir <data_dir>`
13. `imported-review-workflow --config-dir <config_dir> --data-dir <data_dir> --as-of <AS_OF> --source-name <SOURCE_NAME> --format json`
14. `imported-signals-summary --data-dir <data_dir> --format json`
15. `imported-signals --data-dir <data_dir> --as-of <AS_OF> --source-name <SOURCE_NAME> --format json`
16. `report --config-dir <config_dir> --data-dir <data_dir> --reports-dir <reports_dir> --as-of <AS_OF>`
17. `candidates --config-dir <config_dir> --data-dir <data_dir> --as-of <AS_OF> --format json`
18. `trends --config-dir <config_dir> --data-dir <data_dir> --as-of <AS_OF> --format json`
19. `community-handoff-workflow <exports_dir> --config-dir <config_dir> --data-dir <data_dir> --input-format csv --pattern <DIR_PATTERN> --as-of <AS_OF> --source-name <SOURCE_NAME> --format json`
20. `community-signal-lint-dir <exports_dir> --input-format csv --pattern <DIR_PATTERN> --source-name <SOURCE_NAME>`
21. `community-candidates-dir <exports_dir> --config-dir <config_dir> --input-format csv --pattern <DIR_PATTERN> --as-of <AS_OF> --source-name <SOURCE_NAME> --format json`
22. `import-signals-dir <exports_dir> --data-dir <data_dir> --format csv --pattern <DIR_PATTERN> --source-name <SOURCE_NAME> --dry-run`

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "first_run_flow_commands or deterministic_local_command_sequence"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check tests/test_first_run_smoke.py
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

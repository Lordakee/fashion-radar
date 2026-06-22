# Stage 157 First-Run Community Handoff Strict Chain Design

## Objective

Harden the first-run smoke flow so its direct community handoff directory checks
match the stricter command chain already emitted and validated by
`community-handoff-workflow`.

## Current Gap

`run_first_run_flow()` validates the generated `community-handoff-workflow` JSON,
and that validator already expects the stricter local command chain:

- `community-signal-lint-dir ... --strict`
- `community-handoff-check-dir ... --strict`
- `import-signals-dir ... --imported-at AS_OF --dry-run`

The actual first-run smoke execution still runs the older directory checks:

- `community-signal-lint-dir` without `--strict`
- no direct `community-handoff-check-dir`
- `import-signals-dir --dry-run` without `--imported-at AS_OF`

That means the smoke validates stricter workflow metadata but does not execute
the same strict local readiness path.

## Scope

In scope:

- Update `run_first_run_flow()` to execute the stricter local directory check
  sequence after `community-handoff-workflow` validation.
- Update deterministic first-run command-sequence tests to require the stricter
  commands and the additional `community-handoff-check-dir` invocation.
- Keep changes limited to first-run smoke validation and its tests.

Out of scope:

- No social platform connectors.
- No scraping, browser automation, platform APIs, login, cookies, token handling,
  monitoring, scheduling, or source acquisition.
- No write-capable directory import step for the handoff workflow.
- No runtime CLI command implementation changes.

## Architecture

The stage keeps the existing first-run smoke architecture:

- `scripts/check_first_run_smoke.py` remains the executable smoke script.
- `tests/test_first_run_smoke.py` remains the deterministic command-sequence
  test surface.
- Runtime builders such as `build_community_handoff_workflow()` remain unchanged.

The first-run flow will continue to prepare a copied directory export with
`prepare_directory_export(context)`. It will then run local commands against that
directory. The command chain will be tightened in place:

1. Run `community-signal-lint-dir` with `--strict`.
2. Run `community-candidates-dir` unchanged.
3. Run `community-handoff-check-dir` with `--strict`.
4. Run `import-signals-dir` with `--imported-at AS_OF --dry-run`.

The write-capable `import-signals-dir` invocation without `--dry-run` remains
excluded from first-run smoke.

## Tech Stack

- Python standard library for smoke orchestration.
- Existing Fashion Radar Typer CLI commands.
- Existing pytest tests under `tests/test_first_run_smoke.py`.
- `uv --no-config run --frozen` for all verification.
- Local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

## Implementation Method

Use test-first changes:

1. Update `expected_first_run_flow_commands()` so the deterministic first-run
   test expects the stricter command sequence.
2. Run the focused test and confirm it fails because `run_first_run_flow()` still
   emits the older command sequence.
3. Update `run_first_run_flow()` with the matching command arguments.
4. Run focused, module, smoke-script, lint, and full release-gate verification.

## Expected Behavior

The deterministic first-run sequence should include these directory handoff
commands in order:

```text
community-signal-lint-dir <exports_dir> --input-format csv --pattern <DIR_PATTERN> --source-name <SOURCE_NAME> --strict
community-candidates-dir <exports_dir> --config-dir <config_dir> --input-format csv --pattern <DIR_PATTERN> --as-of <AS_OF> --source-name <SOURCE_NAME> --format json
community-handoff-check-dir <exports_dir> --config-dir <config_dir> --input-format csv --pattern <DIR_PATTERN> --as-of <AS_OF> --source-name <SOURCE_NAME> --strict
import-signals-dir <exports_dir> --data-dir <data_dir> --format csv --pattern <DIR_PATTERN> --source-name <SOURCE_NAME> --imported-at <AS_OF> --dry-run
```

The smoke script should still use only temporary first-run directories and should
not create default repository artifacts.

## Risks

- `community-handoff-check-dir --strict` exits non-zero if the sample handoff has
  warnings. A local pre-check copied `examples/community-signals.example.csv`
  into a temporary `exports/community-signals.csv` layout and confirmed the
  command exits 0 with `Warnings: 0`.
- `import-signals-dir` is write-capable without `--dry-run`; the stage must keep
  `--dry-run` present when adding `--imported-at`.
- The deterministic test must update only the first-run command sequence and not
  broaden into runtime CLI behavior already covered elsewhere.

## Verification

Focused:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_run_first_run_flow_uses_deterministic_local_command_sequence -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff or first_run_flow or import_signals_dir"
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

Release gate:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader
```

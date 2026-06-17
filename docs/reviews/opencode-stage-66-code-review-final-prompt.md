# Stage 66 Code Review Final Prompt

You are reviewing `/home/ubuntu/fashion-radar` Stage 66.

Use model `zhipuai-coding-plan/glm-5.2` with `--variant max`.

Do not run tools or commands. Previous attempts already inspected the relevant
files and re-ran verification but timed out before writing final findings. Use
the implementation files in the current worktree and the verified command
results below to produce only the final review.

## Scope

Review the uncommitted Stage 66 implementation of `external-tool-readiness`:

- `src/fashion_radar/external_tool_readiness.py`
- `src/fashion_radar/cli.py`
- `scripts/check_first_run_smoke.py`
- `tests/test_external_tool_readiness.py`
- `tests/test_cli.py`
- `tests/test_cli_docs.py`
- `tests/test_first_run_smoke.py`
- release-facing docs, `AGENTS.md`, and `CHANGELOG.md`

## Required Contract

- `contract_version` is `external-tool-readiness/v1`.
- `execution_mode` is `local_read_only`.
- Readiness check keys are exactly `name`, `status`, `command`, `path`,
  `detail`, `install_hint`.
- Statuses are only `found`, `missing`, `not_applicable`.
- `shutil.which` is resolved lazily.
- Mirror-friendly hints include concrete npmmirror/Tsinghua mirror guidance.
- No upstream tools, adapters, subprocesses, directory/file inspection, SQLite,
  imports, or artifacts are run/created by the readiness command.
- The dry-run import next step includes `--imported-at <as_of> --dry-run`.
- First-run smoke executes and validates `external-tool-readiness`.
- Docs describe the feature as local read-only command availability guidance for
  user-controlled external/community tools and sanitized CSV/JSON local file
  handoff rows.
- No compliance-review product feature is added.

## Verified Commands

The previous opencode attempt and Codex both verified:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_readiness.py tests/test_first_run_smoke.py tests/test_cli_docs.py -q
# 112 passed

uv --no-config run --frozen pytest tests/test_cli.py -q -k "external_tool_readiness"
# 9 passed, 289 deselected

uv --no-config run --frozen ruff check src/fashion_radar/external_tool_readiness.py src/fashion_radar/cli.py tests/test_external_tool_readiness.py tests/test_cli.py tests/test_cli_docs.py tests/test_first_run_smoke.py scripts/check_first_run_smoke.py
# All checks passed

uv --no-config run --frozen ruff format --check src/fashion_radar/external_tool_readiness.py src/fashion_radar/cli.py tests/test_external_tool_readiness.py tests/test_cli.py tests/test_cli_docs.py tests/test_first_run_smoke.py scripts/check_first_run_smoke.py
# 7 files already formatted

uv --no-config run --frozen pytest
# 1097 passed

uv --no-config run --frozen python scripts/check_release_hygiene.py
# Release hygiene checks passed

git diff --check
# no whitespace errors
```

## Output Format

Return only:

```markdown
## Critical
- ...

## Important
- ...

## Minor
- ...

## Residual Risk
- ...
```

If there are no findings in a section, write `No findings.`

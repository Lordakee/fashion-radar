# Stage 140 Code Review Findings

**No blocking findings.** Proceed.

## Verification against requirements

### 1. Deterministic test compares full argv as exact tuples

- `assert_first_run_flow_commands()` at `tests/test_first_run_smoke.py:1563-1568` does `assert captured == expected_first_run_flow_commands(context, example_csv)`, so list-of-tuples equality pins order and full argv for every command.
- Every one of the 22 expected tuples in `tests/test_first_run_smoke.py:1343-1560` was checked against the actual `run_cli()` calls in `scripts/check_first_run_smoke.py:1860-2184`. Command names, ordering, flag positions, and dynamic values (`config_dir`, `data_dir`, `reports_dir`, `exports_dir`, `example_csv`, `AS_OF`, `SOURCE_NAME`, `DIR_PATTERN`) match exactly.
- `example_csv` resolution is consistent: in the deterministic test it is `tmp_path / "examples" / "community-signals.example.csv"`; `make_context` sets `repo_root=tmp_path`; `EXAMPLE_CSV = Path("examples/community-signals.example.csv")`.

### 2. Runtime smoke behavior unchanged

- `git diff --stat 4ad41b45` shows only `tests/test_first_run_smoke.py` changed. There are no changes to `scripts/check_first_run_smoke.py`, `src/`, or runtime code.
- `fake_run_cli` side effects are preserved: directory creation, SQLite placeholder creation, report artifact writing, and stdout stubs remain unchanged.
- The final exported CSV content assertion is retained.

### 3. Helper-negative test proves drift rejection that old membership checks missed

- `test_assert_first_run_flow_commands_rejects_tail_command_extra_args` appends `--extra` to the `community-handoff-workflow` command.
- The old assertions on this command checked the exports directory position and membership of `--format`, `json`, `--data-dir`, `SOURCE_NAME`, and `AS_OF`; all would still pass with `--extra` appended because the original tokens remain.
- The new strict tuple equality rejects the longer tuple, so the RED test covers the intended drift class.

## Minor observations

- **[Low] `tests/test_first_run_smoke.py:3018-3031`** - The negative test only mutates one command (`community-handoff-workflow`). This is sufficient because `assert_first_run_flow_commands` performs a single full-list equality, so any drift anywhere is caught.
- **[Low] `docs/reviews/opencode-stage-140-code-review.md`** - The code review artifact must be saved before commit. This file is that saved artifact.

## Verification performed

- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "first_run_flow_commands or deterministic_local_command_sequence"`: 2 passed
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q`: 88 passed
- `uv --no-config run --frozen ruff check tests/test_first_run_smoke.py`: all checks passed
- `uv --no-config run --frozen ruff format --check tests/test_first_run_smoke.py`: 1 file already formatted
- `git diff --stat 4ad41b45`: only the test file changed

# Claude Code Stage 44 Release Review Prompt

You are reviewing Stage 44 before commit and push.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a read-only release/code/docs review; do not edit files.
- Treat Critical and Important findings as blockers.

## Expected Scope

- README quickstart setup should use applicable repo-local path flags consistent
  with later quickstart workflow commands: `$PWD/configs`, `$PWD/data`, and
  `$PWD/reports` for `init` and `doctor`; `$PWD/data` for `migrate-db`.
- `doctor` should run after `migrate-db` in quickstart setup so it checks the
  repo-local database initialized by `migrate-db`.
- `tests/test_cli_docs.py` should guard README quickstart setup path flags and
  smoke-run only local setup commands with `CliRunner`.
- The smoke helper should fail before invoking a parsed README setup command if
  required `$PWD` path flags are missing.
- `.gitignore` should ignore generated repo-local config files from README
  `init` without ignoring tracked `*.example.yaml` templates.
- Historical review artifacts and previous staged specs/plans should remain
  untouched except for new Stage 44 review artifacts.
- No runtime, source acquisition, scraping/crawling/platform automation, package,
  lockfile, CI, dashboard, database schema, or generated-data behavior should
  change.

## Verification Already Run

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py::test_readme_quickstart_setup_commands_use_repo_local_paths -q
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py::test_readme_quickstart_setup_commands_use_repo_local_paths tests/test_cli_docs.py::test_readme_quickstart_setup_commands_smoke -q
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q
UV_NO_CONFIG=1 uv run ruff check tests/test_cli_docs.py
UV_NO_CONFIG=1 uv run ruff format --check tests/test_cli_docs.py
rg -n 'uv run fashion-radar (init|migrate-db|doctor)' README.md
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py tests/test_stage1_hardening.py -q
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```

Observed results:

- RED was verified with only the static guard: it failed before README edits.
- Focused GREEN setup guard/smoke: `2 passed`.
- Full `tests/test_cli_docs.py`: `6 passed`.
- Combined docs/stage1 tests: `16 passed`.
- Ruff check and format check passed.
- Lockfile and sync checks passed, including the Tsinghua mirror sync check.
- Diff and cached diff whitespace checks passed.
- `uv.lock` has no diff.

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if Stage 44 is acceptable to commit and push, include this exact
phrase:

```text
APPROVED FOR STAGE 44 COMMIT AND PUSH
```

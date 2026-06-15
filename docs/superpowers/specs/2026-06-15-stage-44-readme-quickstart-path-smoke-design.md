# Stage 44 README Quickstart Path Smoke Design

## Goal

Make the README quickstart use one consistent repo-local workspace from setup
through report generation, and add a guard so the setup commands cannot drift
back to platform default paths.

## Scope

In scope:

- Update the README quickstart setup block so `init`, `migrate-db`, and `doctor`
  use applicable repo-local path flags. `init` and `doctor` should use
  `$PWD/configs`, `$PWD/data`, and `$PWD/reports`; `migrate-db` should use
  `$PWD/data`.
- Put `doctor` after `migrate-db` in the quickstart so it verifies the same
  repo-local SQLite database that the following workflow uses.
- Extend `tests/test_cli_docs.py` with a README quickstart guard that parses the
  Quickstart section, extracts `fashion-radar` commands from fenced bash blocks,
  and asserts the setup commands use repo-local path flags.
- Add a small no-network `CliRunner` smoke test that executes the README
  quickstart setup commands with `$PWD` replaced by a temporary directory:
  `init`, `migrate-db`, then `doctor`.
- Ignore repo-local user-generated config files that README `init --config-dir
  "$PWD/configs"` will create: `configs/sources.yaml`, `configs/entities.yaml`,
  and `configs/scoring.yaml`.
- Record Stage 44 Claude Code plan and release review artifacts under
  `docs/reviews/`.

Out of scope:

- Runtime CLI behavior changes.
- Source connectors, scraping, crawling, browser automation, login/cookie/
  account/proxy/CAPTCHA flows, platform APIs, source acquisition, schedulers,
  watchers, monitors, or external services.
- Broad docs churn outside README quickstart, `.gitignore`, and the focused
  docs guard.
- Extending the global path consistency guard to every document for `init` and
  `doctor`; overview docs may intentionally show shorter command names.
- Network collection smoke tests. The smoke test must stay local and stop at
  `doctor`.

## Design

README currently runs bare `uv run fashion-radar init` and `uv run
fashion-radar doctor`, then uses `$PWD/configs`, `$PWD/data`, and `$PWD/reports`
for the rest of the quickstart. Since CLI path defaults are platform user
directories, the quickstart can initialize one workspace and then operate on
another.

The README setup block should become:

```bash
uv run fashion-radar init --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports"
uv run fashion-radar migrate-db --data-dir "$PWD/data"
uv run fashion-radar doctor --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports"
```

The existing paragraph about `doctor` and `migrate-db` should remain accurate:
`doctor` is read-only and `migrate-db` initializes or upgrades local schema.

`tests/test_cli_docs.py` already contains Markdown bash parsing helpers and
README constants. Extend that file rather than creating a new test module:

- Add `shlex` and `CliRunner` imports.
- Add `_readme_quickstart_commands()` to isolate only the README Quickstart
  section.
- Add `_quickstart_fashion_radar_commands(names)` to return commands by CLI
  command name.
- Add `_quickstart_args_for_tmp_path(command, tmp_path)` to parse a command with
  `shlex.split`, reject setup commands that do not contain the expected
  repo-local `$PWD` path flags before invoking anything, drop the `uv run
  fashion-radar` prefix, and replace `$PWD` inside arguments with the temporary
  directory.
- Add `test_readme_quickstart_setup_commands_use_repo_local_paths()` as the RED
  static guard.
- Add `test_readme_quickstart_setup_commands_smoke()` as a local no-network
  smoke test that runs `init`, `migrate-db`, and `doctor` from README setup
  commands with `CliRunner`.

The smoke test should assert:

- `configs/sources.yaml`, `configs/entities.yaml`, and `configs/scoring.yaml`
  are created under the temporary repo-local config directory.
- `data/fashion-radar.sqlite` exists after `migrate-db`.
- `doctor` exits successfully and reports the same temporary config/data/report
  directories.
- No report file is created by setup smoke.

For the RED phase, run only the static guard. The smoke test must not invoke
bare current README setup commands that are missing `$PWD` path flags, because
that would mutate platform default directories.

`.gitignore` should ignore only the three generated config filenames, preserving
tracked `*.example.yaml` templates.

## Verification

Focused checks:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q
UV_NO_CONFIG=1 uv run ruff check tests/test_cli_docs.py
UV_NO_CONFIG=1 uv run ruff format --check tests/test_cli_docs.py
rg -n 'uv run fashion-radar (init|migrate-db|doctor)' README.md
git diff --check
```

Release checks:

```bash
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py tests/test_stage1_hardening.py -q
UV_NO_CONFIG=1 uv run ruff check tests/test_cli_docs.py
UV_NO_CONFIG=1 uv run ruff format --check tests/test_cli_docs.py
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```

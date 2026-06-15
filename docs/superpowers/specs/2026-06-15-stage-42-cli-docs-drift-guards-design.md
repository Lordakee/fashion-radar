# Stage 42 CLI Docs Drift Guards Design

## Goal

Add lightweight pytest guards that keep the public CLI documentation and GitHub
upload checklist aligned with the actual Typer command surface after Stage 41.

## Scope

In scope:

- Add tests that dynamically enumerate the current public `fashion-radar`
  commands from the Typer app.
- Verify `docs/cli-reference.md` lists every public command.
- Verify `docs/github-upload-checklist.md` installed-wheel help smoke loop
  covers every public command exactly once.
- Verify README links the current CLI reference and no longer presents
  `docs/release-gate-stage31.md` as current documentation.
- Verify current repo-local operational examples keep path flags together for
  `match`, `report`, `run`, `candidates`, and `trends` command examples.
- Verify cleanup examples use explicit `--data-dir` where they document local
  cleanup.
- Record Stage 42 Claude Code plan and release review artifacts under
  `docs/reviews/`.

Out of scope:

- Source connectors, scraping, crawling, browser automation, login/cookie/
  account/proxy/CAPTCHA flows, platform APIs, source acquisition, schedulers,
  watchers, monitors, external services, dashboards, package metadata, CI YAML,
  database schema, and runtime behavior changes.
- Editing Stage 41 committed review artifacts.
- Broad prose rewriting beyond what is needed if a new guard exposes a concrete
  documentation inconsistency.

## Design

Create `tests/test_cli_docs.py`. Keep the tests small and read-only:

- Use `typer.main.get_command(app).commands` to derive final command names and
  filter out hidden commands instead of duplicating a hard-coded command list.
- Parse the installed-wheel help loop in
  `docs/github-upload-checklist.md` from the `for cmd in ...; do` block and
  compare it to the dynamic public command set.
- Check `docs/cli-reference.md` for backtick-quoted command names.
- Parse fenced `bash` blocks from selected docs, join line-continuation
  commands, and assert repo-local operational commands carry the path flags that
  prevent mixed workspaces:
  - `match`: `--config-dir`, `--data-dir`
  - `report`: `--config-dir`, `--data-dir`, `--reports-dir`, `--as-of`
  - `run`: `--config-dir`, `--data-dir`, `--reports-dir`, `--as-of`
  - `candidates`: `--config-dir`, `--data-dir`, `--as-of`
  - `trends`: `--config-dir`, `--data-dir`, `--as-of`
  - `clean-old-data`: `--data-dir`
- Exclude `--help` examples from path-flag checks.
- Recognize direct, `uv run`, and quoted/path-qualified `fashion-radar`
  invocations inside selected docs.
- Scope path-flag checks to docs that intentionally show repo-local operational
  workflows, not every historical or review artifact.

## Verification

Focused checks:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q
UV_NO_CONFIG=1 uv run pytest tests/test_cli.py::test_cli_help tests/test_cli.py::test_dashboard_command_help_lists_config_dir -q
git diff --check
```

Release checks:

```bash
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
UV_NO_CONFIG=1 uv run ruff check tests/test_cli_docs.py
UV_NO_CONFIG=1 uv run ruff format --check tests/test_cli_docs.py
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py tests/test_entity_packs.py tests/test_scheduling.py -q
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```

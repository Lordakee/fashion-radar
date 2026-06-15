# Stage 44 README Quickstart Path Smoke Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make README quickstart setup commands use applicable repo-local path
flags consistently with the rest of the quickstart, and add tests that guard the
path story.

**Architecture:** This is a docs and docs-test node. The implementation reuses
`tests/test_cli_docs.py` Markdown parsing helpers to inspect the README
Quickstart section and smoke-run only local setup commands through `CliRunner`.
No production CLI behavior changes are required.

**Tech Stack:** Markdown, Python 3.11, pytest, Typer `CliRunner`, `shlex`, `uv`,
`ruff`, `rg`, local Claude Code CLI with `--effort max`.

---

## Boundaries

In scope:

- Modify: `README.md`
- Modify: `.gitignore`
- Modify: `tests/test_cli_docs.py`
- Add: `docs/reviews/claude-code-stage-44-plan-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-44-plan-review.md`
- Add if needed: `docs/reviews/claude-code-stage-44-plan-rereview*.md`
- Add: `docs/reviews/claude-code-stage-44-release-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-44-release-review.md`
- Maintain/update: this Stage 44 spec and plan.

Out of scope:

- Runtime CLI behavior changes.
- Package metadata, dependency, lockfile, CI YAML, dashboard, database schema, or
  generated data/report changes.
- Source connectors, scraping, crawling, browser automation, login/cookie/
  account/proxy/CAPTCHA flows, platform APIs, source acquisition, schedulers,
  watchers, monitors, or external services.
- Broad rewrites of docs outside README quickstart and `.gitignore`.
- Adding `init` and `doctor` to the global `REQUIRED_FLAGS_BY_COMMAND` guard for
  every document; Stage 44 targets README quickstart only.
- Network collection smoke tests. The smoke test must stay local and stop after
  `doctor`.

## Task -1: Claude Code Plan Review Gate

**Files:**

- Create: `docs/reviews/claude-code-stage-44-plan-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-44-plan-review.md`

- [ ] **Step 1: Confirm the prompt exists**

The prompt file should contain the exact Stage 44 goal, proposed approach, files
to review, and approval phrase:

```text
APPROVED FOR STAGE 44 README QUICKSTART PATH SMOKE
```

- [ ] **Step 2: Request Claude Code plan review**

Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-44-plan-review-prompt.md)" \
  > docs/reviews/claude-code-stage-44-plan-review.md
```

Expected: the review has no Critical or Important blockers and includes
`APPROVED FOR STAGE 44 README QUICKSTART PATH SMOKE`. Fix blockers before Task 1.
If fixes are needed, store follow-up prompt/results as
`docs/reviews/claude-code-stage-44-plan-rereview*.md`.

## Task 0: Pre-flight Cleanliness Check

**Files:**

- Git only.

- [ ] **Step 1: Confirm only Stage 44 planning files are dirty**

Run:

```bash
git status --short --branch
```

Expected before implementation: modified or untracked files are limited to the
Stage 44 spec, plan, and Claude Code Stage 44 plan review prompt/result files.
If unrelated files appear, stop and investigate before editing.

## Task 1: Add README Quickstart Guard Tests

**Files:**

- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Write the failing tests**

Add imports near the top of `tests/test_cli_docs.py`:

```python
import shlex
```

Add this import after `import typer.main`:

```python
from typer.testing import CliRunner
```

Leave the existing `from fashion_radar.cli import app` import unchanged; do not
duplicate it.

Add these helpers after `_fashion_radar_commands`:

```python
def _readme_quickstart_commands() -> list[str]:
    text = _read(README)
    assert "## Quickstart" in text
    quickstart = text.split("## Quickstart", 1)[1].split("\n## ", 1)[0]
    return [
        command
        for block in _bash_blocks(quickstart)
        for command in _shell_commands(block)
    ]


def _quickstart_fashion_radar_commands(names: set[str]) -> list[str]:
    commands: list[str] = []
    for command in _readme_quickstart_commands():
        match = FASHION_RADAR_COMMAND_RE.search(command)
        if match is not None and match.group("name") in names:
            commands.append(command)
    return commands


def _quickstart_cli_args(command: str, tmp_path: Path) -> list[str]:
    command_name = FASHION_RADAR_COMMAND_RE.search(command).group("name")
    assert '--data-dir "$PWD/data"' in command
    if command_name in {"init", "doctor"}:
        assert '--config-dir "$PWD/configs"' in command
        assert '--reports-dir "$PWD/reports"' in command
    parts = [part.replace("$PWD", str(tmp_path)) for part in shlex.split(command)]
    assert parts[:3] == ["uv", "run", "fashion-radar"]
    return parts[3:]
```

Add the static guard after `test_readme_links_current_cli_reference_not_historical_release_gate`:

```python
def test_readme_quickstart_setup_commands_use_repo_local_paths() -> None:
    setup_commands = _quickstart_fashion_radar_commands(
        {"init", "migrate-db", "doctor"}
    )

    assert [FASHION_RADAR_COMMAND_RE.search(command).group("name") for command in setup_commands] == [
        "init",
        "migrate-db",
        "doctor",
    ]
    for command in setup_commands:
        command_name = FASHION_RADAR_COMMAND_RE.search(command).group("name")
        assert '--data-dir "$PWD/data"' in command
        if command_name in {"init", "doctor"}:
            assert '--config-dir "$PWD/configs"' in command
            assert '--reports-dir "$PWD/reports"' in command
```

Add the local smoke test immediately after the static guard:

```python
def test_readme_quickstart_setup_commands_smoke(tmp_path: Path) -> None:
    setup_commands = _quickstart_fashion_radar_commands(
        {"init", "migrate-db", "doctor"}
    )
    runner = CliRunner()

    for command in setup_commands:
        result = runner.invoke(app, _quickstart_cli_args(command, tmp_path))
        assert result.exit_code == 0, result.output

    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    doctor_args = _quickstart_cli_args(setup_commands[-1], tmp_path)
    doctor_result = runner.invoke(app, doctor_args)
    assert doctor_result.exit_code == 0, doctor_result.output
    assert f"Configuration directory: {config_dir}" in doctor_result.output
    assert f"Data directory: {data_dir}" in doctor_result.output
    assert f"Reports directory: {reports_dir}" in doctor_result.output
    assert (config_dir / "sources.yaml").exists()
    assert (config_dir / "entities.yaml").exists()
    assert (config_dir / "scoring.yaml").exists()
    assert (data_dir / "fashion-radar.sqlite").exists()
    assert reports_dir.exists()
    assert not list(reports_dir.glob("fashion-radar-*"))
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py::test_readme_quickstart_setup_commands_use_repo_local_paths -q
```

Expected before README edits: FAIL. The static guard should show bare
`uv run fashion-radar init` and `uv run fashion-radar doctor` missing repo-local
path flags. Do not run the smoke test during RED because current README setup
commands are unsafe platform-default invocations; the smoke helper also rejects
commands missing `$PWD` path flags before invoking anything.

## Task 2: Update README Quickstart And Gitignore

**Files:**

- Modify: `README.md`
- Modify: `.gitignore`

- [ ] **Step 1: Update README setup block**

Replace the current setup and migration quickstart blocks:

```bash
uv run fashion-radar init
uv run fashion-radar doctor
```

and:

```bash
uv run fashion-radar migrate-db --data-dir "$PWD/data"
```

with a single ordered setup block:

```bash
uv run fashion-radar init --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports"
uv run fashion-radar migrate-db --data-dir "$PWD/data"
uv run fashion-radar doctor --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports"
```

Keep the surrounding explanation concise. The quickstart should say this creates
starter config, initializes/upgrades the repo-local SQLite schema, and checks the
same repo-local workspace.

- [ ] **Step 2: Keep the safety paragraph accurate**

Keep or adjust the existing paragraph so it still says:

```text
`doctor` reports database schema status read-only. `migrate-db` only performs
local schema initialization or upgrades; it does not collect, import, match,
score, report, monitor, watch, schedule, or touch external platforms.
```

- [ ] **Step 3: Ignore generated repo-local config files**

Add these entries to `.gitignore` near existing local runtime artifacts:

```gitignore
# Repo-local config files generated by `fashion-radar init`.
configs/sources.yaml
configs/entities.yaml
configs/scoring.yaml
```

Do not ignore `configs/*.example.yaml`.

- [ ] **Step 4: Run focused tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py::test_readme_quickstart_setup_commands_use_repo_local_paths tests/test_cli_docs.py::test_readme_quickstart_setup_commands_smoke -q
```

Expected after README and `.gitignore` edits: PASS.

## Task 3: Verification And Claude Code Release Review

**Files:**

- Create: `docs/reviews/claude-code-stage-44-release-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-44-release-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q
UV_NO_CONFIG=1 uv run ruff check tests/test_cli_docs.py
UV_NO_CONFIG=1 uv run ruff format --check tests/test_cli_docs.py
rg -n 'uv run fashion-radar (init|migrate-db|doctor)' README.md
git diff --check
```

Expected: tests and ruff pass; README search shows the ordered repo-local
`init`, `migrate-db`, and `doctor` commands; diff check passes.

- [ ] **Step 2: Run release verification**

Run:

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

Expected: all commands pass.

- [ ] **Step 3: Write release review prompt**

Create `docs/reviews/claude-code-stage-44-release-review-prompt.md`:

````markdown
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
- `.gitignore` should ignore generated repo-local config files from README
  `init` without ignoring tracked `*.example.yaml` templates.
- Historical review artifacts and previous staged specs/plans should remain
  untouched except for new Stage 44 review artifacts.
- No runtime, source acquisition, scraping/crawling/platform automation, package,
  lockfile, CI, dashboard, database schema, or generated-data behavior should
  change.

## Verification Already Run

```bash
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

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if Stage 44 is acceptable to commit and push, include this exact
phrase:

```text
APPROVED FOR STAGE 44 COMMIT AND PUSH
```
````

- [ ] **Step 4: Request Claude Code release review**

Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-44-release-review-prompt.md)" \
  > docs/reviews/claude-code-stage-44-release-review.md
```

Expected: review has no Critical or Important blockers and includes
`APPROVED FOR STAGE 44 COMMIT AND PUSH`. Fix blockers and rerun review before
commit.

## Task 4: Commit, Push, CI, And Handoff

**Files:**

- Git only.

This task is authorized in the current active thread by the user's standing
instruction to review, commit, push, confirm GitHub Actions, and write a Handoff
Summary at the end of each completed node. In a fresh session without that
authorization, stop after release review and ask before committing or pushing.

Claude Code is a read-only reviewer in this workflow. The commit is performed by
Codex, so do not add a Claude Code co-author trailer unless the user or repo
instructions explicitly require one.

- [ ] **Step 1: Inspect final status**

Run:

```bash
git status --short --branch
git diff --cached --check
git diff --check
```

Expected: dirty/staged files are limited to Stage 44 docs, test, `.gitignore`,
and review artifacts; diff checks pass.

- [ ] **Step 2: Commit Stage 44**

Run:

```bash
git add README.md .gitignore tests/test_cli_docs.py docs/superpowers/specs/2026-06-15-stage-44-readme-quickstart-path-smoke-design.md docs/superpowers/plans/2026-06-15-stage-44-readme-quickstart-path-smoke-plan.md docs/reviews/claude-code-stage-44-*.md
git commit -m "Guard README quickstart paths"
```

Expected: commit succeeds.

- [ ] **Step 3: Push and confirm CI**

Run normal push first:

```bash
git push origin main
```

If normal Git HTTPS push fails but GitHub API remains available, use the
previously authorized non-persistent token through a one-shot push/API flow
without storing the token in Git config or remotes. Then confirm the latest
GitHub Actions run for the pushed commit completes successfully.

- [ ] **Step 4: Handoff Summary**

Write a concise Handoff Summary with repo status, verified commands, uncommitted
files, push/CI status, and the next best node.

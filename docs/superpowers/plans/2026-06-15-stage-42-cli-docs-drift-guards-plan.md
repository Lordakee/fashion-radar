# Stage 42 CLI Docs Drift Guards Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add pytest guards that prevent the CLI reference, upload checklist,
README links, and repo-local command examples from drifting away from the actual
public CLI.

**Architecture:** This is a test-focused quality node. A new
`tests/test_cli_docs.py` file will derive public command names from Typer, parse
the relevant Markdown docs, and assert the Stage 41 documentation invariants
remain true. If a guard exposes a concrete doc inconsistency, fix only the
affected Markdown example.

**Tech Stack:** Python 3.11, pytest, Typer/Click command introspection,
Markdown text parsing with `re`, `uv`, `ruff`, Claude Code review gates.

---

## Boundaries

In scope:

- Create: `tests/test_cli_docs.py`
- Modify only if a new guard fails: targeted Markdown docs already covered by
  Stage 41 path-consistency work.
- Add: `docs/reviews/claude-code-stage-42-plan-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-42-plan-review.md`
- Add if needed: `docs/reviews/claude-code-stage-42-plan-rereview*.md`
- Add: `docs/reviews/claude-code-stage-42-release-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-42-release-review.md`
- Maintain/update: this Stage 42 spec and plan.

Out of scope:

- Modifying source code, package metadata, `uv.lock`, CI YAML, database schema,
  runtime behavior, generated reports/data, dashboards, or config templates.
- Adding source connectors, scraping, crawling, browser automation,
  login/cookie/account/proxy/CAPTCHA flows, platform APIs, source acquisition,
  schedulers, watchers, monitors, or external services.
- Rewriting historical Stage 41 review artifacts.

## Task -1: Claude Code Plan Review Gate

**Files:**

- Create: `docs/reviews/claude-code-stage-42-plan-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-42-plan-review.md`

- [ ] **Step 1: Write plan review prompt**

Create `docs/reviews/claude-code-stage-42-plan-review-prompt.md`:

```markdown
# Claude Code Stage 42 Plan Review Prompt

You are reviewing the Stage 42 CLI docs drift guards plan for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Add pytest guards that keep Stage 41 CLI docs and upload checklist coverage in
sync with the actual public Typer command surface.

## Proposed Technical Approach

- Create `tests/test_cli_docs.py`.
- Derive public CLI command names dynamically from `typer.main.get_command(app)`
  and filter hidden commands.
- Assert `docs/cli-reference.md` lists every public command.
- Assert the installed-wheel help loop in `docs/github-upload-checklist.md`
  covers exactly the current public commands.
- Assert README links `docs/cli-reference.md` and does not present historical
  `docs/release-gate-stage31.md` as current docs.
- Parse selected Markdown bash blocks and assert repo-local operational command
  examples keep `--config-dir`, `--data-dir`, `--reports-dir`, and `--as-of`
  flags together where needed, including `clean-old-data --data-dir`.
- Keep this test-focused node out of runtime behavior, source acquisition,
  scraping/crawling/platform automation, schedulers, watchers, monitors,
  external services, package metadata, lockfiles, and CI workflow behavior.

## Files To Review

- `docs/superpowers/specs/2026-06-15-stage-42-cli-docs-drift-guards-design.md`
- `docs/superpowers/plans/2026-06-15-stage-42-cli-docs-drift-guards-plan.md`

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 42 CLI DOCS DRIFT GUARDS
```
```

- [ ] **Step 2: Request Claude Code plan review**

Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-42-plan-review-prompt.md)" \
  > docs/reviews/claude-code-stage-42-plan-review.md
```

Expected: the review has no Critical or Important blockers and includes
`APPROVED FOR STAGE 42 CLI DOCS DRIFT GUARDS`. Fix blockers before Task 1. If
fixes are needed, store each follow-up prompt/result as
`docs/reviews/claude-code-stage-42-plan-rereview*.md`.

## Task 0: Pre-flight Cleanliness Check

**Files:**

- Git only.

- [ ] **Step 1: Confirm only Stage 42 planning files are dirty**

Run:

```bash
git status --short --branch
```

Expected before implementation: modified or untracked files are limited to the
Stage 42 spec, plan, and Claude Code Stage 42 plan review prompt/result files.
If unrelated files appear, stop and investigate before editing.

## Task 1: Add CLI Docs Drift Guard Tests

**Files:**

- Create: `tests/test_cli_docs.py`

- [ ] **Step 1: Create the test file with dynamic CLI command introspection**

Create `tests/test_cli_docs.py` with this content:

```python
from __future__ import annotations

import re
from pathlib import Path

import typer.main

from fashion_radar.cli import app


ROOT = Path(__file__).resolve().parents[1]
CLI_REFERENCE = ROOT / "docs" / "cli-reference.md"
UPLOAD_CHECKLIST = ROOT / "docs" / "github-upload-checklist.md"
README = ROOT / "README.md"

PATH_CONSISTENCY_DOCS = [
    ROOT / "README.md",
    ROOT / "docs" / "cli-reference.md",
    ROOT / "docs" / "manual-signal-import.md",
    ROOT / "docs" / "community-signal-import.md",
    ROOT / "docs" / "architecture.md",
    ROOT / "docs" / "trend-deltas.md",
    ROOT / "docs" / "candidate-discovery.md",
    ROOT / "docs" / "daily-digest.md",
    ROOT / "docs" / "scheduling.md",
    ROOT / "docs" / "data-retention.md",
    ROOT / "docs" / "entity-packs.md",
    ROOT / "docs" / "source-packs.md",
]

REQUIRED_FLAGS_BY_COMMAND = {
    "match": ("--config-dir", "--data-dir"),
    "report": ("--config-dir", "--data-dir", "--reports-dir", "--as-of"),
    "run": ("--config-dir", "--data-dir", "--reports-dir", "--as-of"),
    "candidates": ("--config-dir", "--data-dir", "--as-of"),
    "trends": ("--config-dir", "--data-dir", "--as-of"),
    "clean-old-data": ("--data-dir",),
}

FASHION_RADAR_COMMAND_RE = re.compile(
    r'(?:^|\s)(?:"[^"]*/fashion-radar"|fashion-radar)\s+(?P<name>[a-z0-9-]+)'
)


def _public_cli_commands() -> list[str]:
    click_app = typer.main.get_command(app)
    return sorted(
        name
        for name, command in click_app.commands.items()
        if not getattr(command, "hidden", False)
    )


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _upload_checklist_help_loop_commands() -> list[str]:
    text = _read(UPLOAD_CHECKLIST)
    match = re.search(
        r"for cmd in \\\\\n(?P<body>.*?)\ndo\n\s+\"\$tmp_env/venv/bin/fashion-radar\" \"\$cmd\" --help\n",
        text,
        flags=re.DOTALL,
    )
    assert match is not None, "Installed-wheel help loop not found"
    body = match.group("body").replace("\\", " ")
    return sorted(token for token in body.split() if token)


def _bash_blocks(text: str) -> list[str]:
    return re.findall(r"```bash\n(.*?)\n```", text, flags=re.DOTALL)


def _shell_commands(block: str) -> list[str]:
    commands: list[str] = []
    current: list[str] = []
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if current:
            current.append(line.removesuffix("\\").strip())
        else:
            current = [line.removesuffix("\\").strip()]
        if not line.endswith("\\"):
            commands.append(" ".join(part for part in current if part))
            current = []
    if current:
        commands.append(" ".join(part for part in current if part))
    return commands


def _fashion_radar_commands(path: Path) -> list[str]:
    commands: list[str] = []
    for block in _bash_blocks(_read(path)):
        for command in _shell_commands(block):
            if FASHION_RADAR_COMMAND_RE.search(command):
                commands.append(command)
    return commands


def test_cli_reference_lists_every_public_command() -> None:
    text = _read(CLI_REFERENCE)

    for command in _public_cli_commands():
        assert f"`{command}`" in text

    assert "FASHION_RADAR_CONFIG_DIR" in text
    assert "FASHION_RADAR_DATA_DIR" in text
    assert "FASHION_RADAR_REPORTS_DIR" in text


def test_upload_checklist_help_loop_matches_public_commands() -> None:
    assert _upload_checklist_help_loop_commands() == _public_cli_commands()


def test_readme_links_current_cli_reference_not_historical_release_gate() -> None:
    text = _read(README)

    assert "[docs/cli-reference.md](docs/cli-reference.md)" in text
    assert "docs/release-gate-stage31.md" not in text


def test_repo_local_operational_examples_keep_path_flags_together() -> None:
    failures: list[str] = []
    for path in PATH_CONSISTENCY_DOCS:
        for command in _fashion_radar_commands(path):
            if "--help" in command:
                continue
            match = FASHION_RADAR_COMMAND_RE.search(command)
            if match is None:
                continue
            command_name = match.group("name")
            required_flags = REQUIRED_FLAGS_BY_COMMAND.get(command_name)
            if required_flags is None:
                continue
            missing = [flag for flag in required_flags if flag not in command]
            if missing:
                relative_path = path.relative_to(ROOT)
                failures.append(f"{relative_path}: {command!r} missing {missing}")

    assert not failures, "\n".join(failures)
```

- [ ] **Step 2: Run the new tests**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q
```

Expected: all tests pass against the current Stage 41 documentation. If a test
fails because it exposes a real documentation inconsistency, fix the specific
Markdown example. If it fails because the guard is broader than the approved
scope, narrow the guard rather than rewriting unrelated docs.

## Task 2: Focused Verification

**Files:**

- Test only.

- [ ] **Step 1: Run lint and formatting checks for the new test**

Run:

```bash
UV_NO_CONFIG=1 uv run ruff check tests/test_cli_docs.py
UV_NO_CONFIG=1 uv run ruff format --check tests/test_cli_docs.py
```

Expected: both commands pass.

- [ ] **Step 2: Run related test slices**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py tests/test_entity_packs.py tests/test_scheduling.py -q
UV_NO_CONFIG=1 uv run pytest tests/test_cli.py::test_cli_help tests/test_cli.py::test_dashboard_command_help_lists_config_dir -q
```

Expected: all selected tests pass.

- [ ] **Step 3: Run dependency and mirror checks**

Run:

```bash
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```

Expected: all commands pass and `uv.lock` is unchanged.

## Task 3: Claude Code Release Review

**Files:**

- Create: `docs/reviews/claude-code-stage-42-release-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-42-release-review.md`

- [ ] **Step 1: Write release review prompt**

Create `docs/reviews/claude-code-stage-42-release-review-prompt.md` with:

- Stage 42 goal and implementation summary.
- Files changed.
- Verification commands and results.
- Confirmation that the change is test-focused and does not add runtime
  behavior, source acquisition, scraping/crawling/platform automation,
  schedulers, watchers, monitors, external services, dependency changes,
  lockfile changes, or CI workflow changes.

- [ ] **Step 2: Run Claude Code release review**

Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-42-release-review-prompt.md)" \
  > docs/reviews/claude-code-stage-42-release-review.md
```

Required approval phrase:

```text
APPROVED FOR STAGE 42 COMMIT AND PUSH
```

Fix all Critical and Important findings before commit. If fixes are needed,
store follow-up prompt/result files as
`docs/reviews/claude-code-stage-42-release-rereview*.md`.

## Task 4: Commit, Push, And Actions Confirmation

**Files:**

- Git only.

- [ ] **Step 1: Stage only Stage 42 files**

Confirm staged files are limited to `tests/test_cli_docs.py`, Stage 42
spec/plan files, any targeted Markdown fixes caused by the new guards, and
Claude Code Stage 42 review artifacts.

- [ ] **Step 2: Commit and push**

Commit:

```bash
git commit -m "Add CLI documentation drift guards"
```

Push with token-free remote config. If normal push lacks credentials, use a
one-shot auth header only; do not persist GitHub tokens in remote URLs or git
config.

- [ ] **Step 3: Confirm GitHub Actions**

Confirm the latest pushed commit reaches GitHub and CI completes successfully.

## Handoff Summary Requirement

At node end, write a concise Handoff Summary with:

- repo status;
- verified commands;
- review artifacts produced;
- GitHub Actions result;
- uncommitted files;
- next step.

# Stage 47 First-Run Sample Smoke Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the GitHub first-run path executable and tested through a
local-only sample workflow that uses checked-in examples and produces a report.

**Architecture:** A standard-library smoke script runs `python -m
fashion_radar` commands inside a temporary runtime workspace, validates JSON
outputs and generated report artifacts, and exits non-zero on the first
failure with a concise command/error message. README, community import docs,
CI, and upload checklist reference the same smoke path so documentation and
automation stay aligned.

**Tech Stack:** Python 3.11 standard library (`argparse`, `json`, `shutil`,
`subprocess`, `sys`, `tempfile`, `pathlib`), pytest, Typer CLI via
`python -m fashion_radar`, GitHub Actions YAML, Markdown, Ruff, `uv`, local
Claude Code CLI with `--effort max`.

---

## Boundaries

In scope:

- Create: `scripts/check_first_run_smoke.py`
- Create: `tests/test_first_run_smoke.py`
- Modify: `README.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `.github/workflows/ci.yml`
- Modify: `tests/test_cli_docs.py`
- Add: `docs/reviews/claude-code-stage-47-plan-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-47-plan-review.md`
- Add if needed: `docs/reviews/claude-code-stage-47-plan-rereview*.md`
- Add: `docs/reviews/claude-code-stage-47-release-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-47-release-review.md`

Out of scope:

- Live `collect`, RSS/GDELT fetches, source acquisition, web scraping, crawling,
  browser automation, login/cookie/session handling, account automation,
  platform connectors, media download, monitoring, watching, scheduling, push
  notifications, or external services.
- Product compliance-review functionality.
- Launching a long-running dashboard server in CI.
- Dependency or lockfile changes, package version changes, database schema
  changes, scoring algorithm changes, entity alias changes, or committed
  generated runtime data/reports.

## Task -1: Claude Code Plan Review Gate

**Files:**

- Create: `docs/reviews/claude-code-stage-47-plan-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-47-plan-review.md`

- [ ] **Step 1: Confirm the prompt exists**

The prompt file should contain the Stage 47 objective, technical approach,
files to review, boundaries, and approval phrase:

```text
APPROVED FOR STAGE 47 FIRST RUN SAMPLE SMOKE
```

- [ ] **Step 2: Request Claude Code plan review**

Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-47-plan-review-prompt.md)" \
  > docs/reviews/claude-code-stage-47-plan-review.md
```

Expected: no Critical or Important blockers and the exact approval phrase. Fix
blockers before Task 0.

## Task 0: Pre-flight Cleanliness Check

**Files:**

- Git only.

- [ ] **Step 1: Confirm only Stage 47 planning files are dirty**

Run:

```bash
git status --short --branch
```

Expected before implementation: modified or untracked files are limited to the
Stage 47 spec, plan, and Claude Code Stage 47 plan review prompt/result files.

## Task 1: Add First-Run Smoke Script

**Files:**

- Create: `tests/test_first_run_smoke.py`
- Create: `scripts/check_first_run_smoke.py`

- [ ] **Step 1: Write failing script tests**

Create `tests/test_first_run_smoke.py`:

```python
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_first_run_smoke.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_first_run_smoke", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_script_defines_deterministic_first_run_constants() -> None:
    module = load_module()

    assert module.AS_OF == "2026-06-13T12:00:00Z"
    assert module.SOURCE_NAME == "Community Tool Export"
    assert module.EXAMPLE_CSV == Path("examples/community-signals.example.csv")


def test_cli_command_builder_uses_module_entrypoint_and_temp_paths(tmp_path: Path) -> None:
    module = load_module()
    context = module.SmokeContext(
        repo_root=ROOT,
        python="python3",
        runtime_dir=tmp_path,
        config_dir=tmp_path / "configs",
        data_dir=tmp_path / "data",
        reports_dir=tmp_path / "reports",
        exports_dir=tmp_path / "exports",
    )

    command = module.cli_command(context, "doctor", "--data-dir", context.data_dir)

    assert command[:3] == ["python3", "-m", "fashion_radar"]
    assert command[3:] == ["doctor", "--data-dir", str(context.data_dir)]


def test_validate_json_output_rejects_invalid_json() -> None:
    module = load_module()

    errors = module.validate_json_output("not-json", label="candidates")

    assert errors == ["candidates did not produce valid JSON"]


def test_validate_summary_requires_imported_items() -> None:
    module = load_module()

    errors = module.validate_imported_summary(json.dumps({"rows": []}))

    assert errors == ["imported-signals-summary did not report imported rows"]


def test_report_paths_derive_from_as_of(tmp_path: Path) -> None:
    module = load_module()

    markdown_path, json_path = module.report_paths(tmp_path)

    assert markdown_path == tmp_path / "fashion-radar-2026-06-13.md"
    assert json_path == tmp_path / "fashion-radar-2026-06-13.json"
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_first_run_smoke.py -q
```

Expected before implementation: FAIL because the script does not exist.

- [ ] **Step 3: Implement `scripts/check_first_run_smoke.py`**

Implement:

- `AS_OF = "2026-06-13T12:00:00Z"`
- `SOURCE_NAME = "Community Tool Export"`
- `EXAMPLE_CSV = Path("examples/community-signals.example.csv")`
- `@dataclass(frozen=True) class SmokeContext`
- `parse_args()`
- `cli_command(context, *args) -> list[str]`
- `run_command(context, *args) -> subprocess.CompletedProcess[str]`
- `validate_json_output(text, *, label) -> list[str]`
- `validate_imported_summary(text) -> list[str]`
- `report_paths(reports_dir) -> tuple[Path, Path]`
- `run_first_run_smoke(context) -> list[str]`
- `main() -> int`

The workflow should create temp config/data/reports/exports directories, copy
`examples/community-signals.example.csv` to exactly
`$tmp/exports/community-signals.csv` before directory commands, run all commands
listed in the Stage 47 design with `cwd=repo_root`, `PYTHONPATH` prepending
`repo_root/src`, explicit temp path flags, deterministic `AS_OF`, and
deterministic source name. Parse JSON outputs, assert imported rows, assert
non-empty report files, assert no default-path generated files were written
under repo `data/` or `reports/`, print `First-run sample smoke passed.` on
success, and print failures to stderr with return code `1`.

- [ ] **Step 4: Run tests and smoke script to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_first_run_smoke.py -q
UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
```

Expected: tests pass and the smoke script exits `0`.

## Task 2: Wire Smoke Into CI, Upload Checklist, And Docs Drift Tests

**Files:**

- Modify: `.github/workflows/ci.yml`
- Modify: `docs/github-upload-checklist.md`
- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Write failing docs/CI drift tests**

In `tests/test_cli_docs.py`, add a test:

```python
def test_first_run_smoke_command_is_documented_and_in_ci() -> None:
    checklist = _read(UPLOAD_CHECKLIST)
    ci_workflow = _read(CI_WORKFLOW)
    readme = _read(README)
    command = "UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root ."

    for text in (checklist, ci_workflow, readme):
        assert command in text
        assert "scripts/check_first_run_smoke.py" in text
```

- [ ] **Step 2: Run docs drift tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q
```

Expected before docs/CI updates: FAIL because the command is not yet wired.

- [ ] **Step 3: Update CI and upload checklist**

Add to `.github/workflows/ci.yml` after release hygiene:

```bash
UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
```

Add the same command to `docs/github-upload-checklist.md` before package smoke.

- [ ] **Step 4: Run docs drift tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q
```

Expected: docs drift tests pass.

## Task 3: Update First-Run Docs

**Files:**

- Modify: `README.md`
- Modify: `docs/community-signal-import.md`
- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Write failing docs content guards**

In `tests/test_cli_docs.py`, add a test:

```python
def test_readme_documents_deterministic_local_sample_smoke() -> None:
    text = _read(README)

    for term in (
        "Local Sample Smoke",
        'AS_OF="2026-06-13T12:00:00Z"',
        "examples/community-signals.example.csv",
        "community-candidates examples/community-signals.example.csv",
        "import-signals examples/community-signals.example.csv",
        "reports/fashion-radar-2026-06-13.md",
        "reports/fashion-radar-2026-06-13.json",
        "does not run live collection",
    ):
        assert term in text
```

Add a test:

```python
def test_community_import_docs_promote_checked_in_example_import() -> None:
    text = _read(ROOT / "docs" / "community-signal-import.md")

    assert 'AS_OF="2026-06-13T12:00:00Z"' in text
    assert "import-signals examples/community-signals.example.csv" in text
    assert "community-candidates examples/community-signals.example.csv" in text
    assert "tmp_run=\"$(mktemp -d)\"" in text
    assert 'cp examples/community-signals.example.csv "$tmp_run/exports/community-signals.csv"' in text
```

- [ ] **Step 2: Run docs tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q
```

Expected: FAIL until README and community import docs are updated.

- [ ] **Step 3: Update README**

Add a `### Local Sample Smoke` subsection under Quickstart before live
`collect`. Include the deterministic `AS_OF` path from the design, say it uses
checked-in examples, writes only local temp/repo-local config/data/report
artifacts, and does not run live collection, scraping, platform automation, or
external services.

Make the dashboard section reference running Local Sample Smoke first when a
user wants dashboard content from the sample report.

- [ ] **Step 4: Update `docs/community-signal-import.md`**

Promote the checked-in CSV example into the Import section, then show the
directory setup with `tmp_run`, `mkdir -p "$tmp_run/exports"`, and `cp
examples/community-signals.example.csv "$tmp_run/exports/community-signals.csv"`
before directory commands.

- [ ] **Step 5: Run docs tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q
```

Expected: docs tests pass.

## Task 4: Stage 47 Verification And Claude Code Release Review

**Files:**

- Create: `docs/reviews/claude-code-stage-47-release-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-47-release-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_first_run_smoke.py tests/test_cli_docs.py -q
UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
```

Expected: all commands exit `0`.

- [ ] **Step 2: Run full release verification**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest -q
UV_NO_CONFIG=1 uv run ruff check .
UV_NO_CONFIG=1 uv run ruff format --check .
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
tmp_build="$(mktemp -d)"
UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```

Expected: all commands exit `0`; `uv.lock` remains unchanged.

- [ ] **Step 3: Request Claude Code release review**

Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-47-release-review-prompt.md)" \
  > docs/reviews/claude-code-stage-47-release-review.md
```

Expected: no Critical or Important blockers and the exact phrase:

```text
APPROVED FOR STAGE 47 COMMIT AND PUSH
```

Fix Critical and Important findings, rerun affected verification, and request a
rereview before committing.

## Task 5: User-Authorized Commit, Push, And Confirm GitHub Actions

**Files:**

- Git only.

This is a node completion step. The user has explicitly authorized committing
and pushing this repository. Do not run this step until local verification
passes and Claude Code release review approves the Stage 47 diff.

- [ ] **Step 1: Commit Stage 47**

Run:

```bash
git status --short
git add .github/workflows/ci.yml README.md docs/community-signal-import.md \
  docs/github-upload-checklist.md docs/reviews/claude-code-stage-47-*.md \
  docs/superpowers/specs/2026-06-15-stage-47-first-run-sample-smoke-design.md \
  docs/superpowers/plans/2026-06-15-stage-47-first-run-sample-smoke-plan.md \
  scripts/check_first_run_smoke.py tests/test_first_run_smoke.py tests/test_cli_docs.py
git commit -m "Add first-run sample smoke"
```

- [ ] **Step 2: Push with non-persistent token header**

Run:

```bash
TOKEN="$(cat /home/ubuntu/.config/fashion-radar/github-token)"
BASIC="$(printf 'x-access-token:%s' "$TOKEN" | base64 -w0)"
GIT_TERMINAL_PROMPT=0 git -c http.version=HTTP/1.1 \
  -c http.postBuffer=524288000 \
  -c http.lowSpeedLimit=0 \
  -c http.lowSpeedTime=999999 \
  -c http.extraHeader="Authorization: Basic ${BASIC}" \
  push --no-thin origin main
```

- [ ] **Step 3: Confirm GitHub Actions**

Use the GitHub REST API with the saved token to confirm the newest `main` CI
run completes successfully.

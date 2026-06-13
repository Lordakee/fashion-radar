# Stage 24 Imported Review Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `fashion-radar imported-review-workflow`, a local command that prints a deterministic post-import review checklist for existing Fashion Radar commands without executing them.

**Architecture:** Add a focused `src/fashion_radar/imported_review_workflow.py` module with Pydantic models, a pure builder, shell-quoted command rendering, and table output. Add a thin Typer command in `src/fashion_radar/cli.py` that validates `--as-of`, delegates to the builder, and prints table or JSON. The command does not open SQLite, create directories, execute subprocesses, import, match, score, report, schedule, monitor, or integrate with external platforms.

**Tech Stack:** Python 3.11+, Typer, Pydantic v2, `shlex`, pytest, ruff, uv.

---

## Process Gate

Implementation may start only after Claude Code approves this Stage 24 plan
review and every Critical or Important plan-review finding is resolved. After
implementation, Stage 24 code must be submitted to Claude Code for code review
before commit and push.

## File Structure

- Create `src/fashion_radar/imported_review_workflow.py`
  - Models: `ImportedReviewWorkflowStep`, `ImportedReviewWorkflow`
  - Helpers: `build_imported_review_workflow()`, `render_imported_review_workflow_table()`
  - Internal helpers: `_shell_command()`, `_optional_source_args()`, `_table_cell()`
- Modify `src/fashion_radar/cli.py`
  - Import builder/renderer
  - Add `ImportedReviewWorkflowOutputFormat`
  - Add option constants
  - Add `imported-review-workflow` command
- Create `tests/test_imported_review_workflow.py`
  - Unit tests for builder, quoting, source-name behavior, and renderer
- Modify `tests/test_cli.py`
  - CLI tests for help, JSON, invalid inputs, special characters, and no artifacts
- Modify docs and changelog with bounded local-only examples
- Create Claude Code Stage 24 code review prompt/result files

## Task 1: Workflow Models And Builder

**Files:**
- Create: `src/fashion_radar/imported_review_workflow.py`
- Create: `tests/test_imported_review_workflow.py`

- [ ] **Step 1: Write failing builder tests**

Create `tests/test_imported_review_workflow.py`:

```python
from datetime import UTC, datetime
from pathlib import Path

from fashion_radar.imported_review_workflow import (
    ImportedReviewWorkflow,
    ImportedReviewWorkflowStep,
    build_imported_review_workflow,
    render_imported_review_workflow_table,
)
```

Add:

```python
def test_build_imported_review_workflow_returns_deterministic_steps() -> None:
    workflow = build_imported_review_workflow(
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of=datetime(2026, 6, 13, 12, 0, tzinfo=UTC),
    )

    assert workflow.as_of == "2026-06-13T12:00:00+00:00"
    assert workflow.config_dir == "configs"
    assert workflow.data_dir == "data"
    assert workflow.source_name is None
    assert workflow.lookback_days == 7
    assert workflow.current_days == 7
    assert workflow.baseline_days == 7
    assert workflow.step_count == 4
    assert [step.name for step in workflow.steps] == [
        "summarize_imported_sources",
        "refresh_stored_matches",
        "compare_imported_entities",
        "review_unmatched_imported_rows",
    ]
    assert workflow.execution_mode == "print_only"
    assert [step.suggested_effect for step in workflow.steps] == [
        "read_only",
        "updates_local_matches",
        "read_only",
        "read_only",
    ]
    assert workflow.steps[0].command == (
        "fashion-radar imported-signals-summary --data-dir data"
    )
    assert workflow.steps[1].command == (
        "fashion-radar match --config-dir configs --data-dir data"
    )
    assert workflow.steps[2].command == (
        "fashion-radar imported-entity-deltas --data-dir data "
        "--as-of 2026-06-13T12:00:00+00:00 --current-days 7 --baseline-days 7"
    )
    assert workflow.steps[3].command == (
        "fashion-radar imported-signals --data-dir data "
        "--as-of 2026-06-13T12:00:00+00:00 --lookback-days 7 --unmatched-only"
    )
```

Add:

```python
def test_build_imported_review_workflow_quotes_paths_and_source_name() -> None:
    workflow = build_imported_review_workflow(
        config_dir=Path("config ? # & %"),
        data_dir=Path("data ? # & %"),
        as_of="2026-06-13T12:00:00Z",
        source_name="Community | Tool Export",
        lookback_days=3,
        current_days=5,
        baseline_days=9,
    )

    assert workflow.source_name == "Community | Tool Export"
    assert workflow.steps[0].command == (
        "fashion-radar imported-signals-summary --data-dir 'data ? # & %'"
    )
    assert workflow.steps[1].command == (
        "fashion-radar match --config-dir 'config ? # & %' --data-dir 'data ? # & %'"
    )
    assert workflow.steps[2].command == (
        "fashion-radar imported-entity-deltas --data-dir 'data ? # & %' "
        "--as-of 2026-06-13T12:00:00+00:00 --current-days 5 --baseline-days 9 "
        "--source-name 'Community | Tool Export'"
    )
    assert workflow.steps[3].command == (
        "fashion-radar imported-signals --data-dir 'data ? # & %' "
        "--as-of 2026-06-13T12:00:00+00:00 --lookback-days 3 --unmatched-only "
        "--source-name 'Community | Tool Export'"
    )
```

Add:

```python
def test_build_imported_review_workflow_blank_source_name_is_no_filter() -> None:
    workflow = build_imported_review_workflow(
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
        source_name=" ",
    )

    assert workflow.source_name is None
    assert "--source-name" not in workflow.steps[2].command
    assert "--source-name" not in workflow.steps[3].command
```

- [ ] **Step 2: Run builder tests to verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_imported_review_workflow.py -q -k "build_imported_review_workflow"
```

Expected: fail because `fashion_radar.imported_review_workflow` does not exist.

- [ ] **Step 3: Implement models and builder**

Create `src/fashion_radar/imported_review_workflow.py`:

```python
from __future__ import annotations

import shlex
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from fashion_radar.utils.dates import parse_datetime_utc
```

Add:

```python
class ImportedReviewWorkflowStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order: int
    name: str
    purpose: str
    command: str
    suggested_effect: Literal["read_only", "updates_local_matches"]


class ImportedReviewWorkflow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    as_of: str
    config_dir: str
    data_dir: str
    source_name: str | None = None
    lookback_days: int = 7
    current_days: int = 7
    baseline_days: int = 7
    execution_mode: Literal["print_only"] = "print_only"
    step_count: int = 0
    steps: list[ImportedReviewWorkflowStep] = Field(default_factory=list)
```

Add:

```python
def build_imported_review_workflow(
    *,
    config_dir: Path,
    data_dir: Path,
    as_of: str | datetime,
    source_name: str | None = None,
    lookback_days: int = 7,
    current_days: int = 7,
    baseline_days: int = 7,
) -> ImportedReviewWorkflow:
    if lookback_days < 1:
        raise ValueError("lookback_days must be at least 1")
    if current_days < 1:
        raise ValueError("current_days must be at least 1")
    if baseline_days < 1:
        raise ValueError("baseline_days must be at least 1")

    as_of_value = parse_datetime_utc(as_of)
    as_of_text = as_of_value.isoformat()
    source_filter = (source_name or "").strip() or None
    config_text = str(config_dir)
    data_text = str(data_dir)
    source_args = ["--source-name", source_filter] if source_filter is not None else []
    steps = [
        ImportedReviewWorkflowStep(
            order=1,
            name="summarize_imported_sources",
            purpose="Summarize retained imported source-name labels.",
            command=_shell_command(
                "fashion-radar",
                "imported-signals-summary",
                "--data-dir",
                data_text,
            ),
            suggested_effect="read_only",
        ),
        ImportedReviewWorkflowStep(
            order=2,
            name="refresh_stored_matches",
            purpose="Refresh stored local matches using configured entities.",
            command=_shell_command(
                "fashion-radar",
                "match",
                "--config-dir",
                config_text,
                "--data-dir",
                data_text,
            ),
            suggested_effect="updates_local_matches",
        ),
        ImportedReviewWorkflowStep(
            order=3,
            name="compare_imported_entities",
            purpose="Compare stored matched imported entities across collected-at windows.",
            command=_shell_command(
                "fashion-radar",
                "imported-entity-deltas",
                "--data-dir",
                data_text,
                "--as-of",
                as_of_text,
                "--current-days",
                str(current_days),
                "--baseline-days",
                str(baseline_days),
                *source_args,
            ),
            suggested_effect="read_only",
        ),
        ImportedReviewWorkflowStep(
            order=4,
            name="review_unmatched_imported_rows",
            purpose="Review retained imported rows without stored matches.",
            command=_shell_command(
                "fashion-radar",
                "imported-signals",
                "--data-dir",
                data_text,
                "--as-of",
                as_of_text,
                "--lookback-days",
                str(lookback_days),
                "--unmatched-only",
                *source_args,
            ),
            suggested_effect="read_only",
        ),
    ]
    return ImportedReviewWorkflow(
        as_of=as_of_text,
        config_dir=config_text,
        data_dir=data_text,
        source_name=source_filter,
        lookback_days=lookback_days,
        current_days=current_days,
        baseline_days=baseline_days,
        step_count=len(steps),
        steps=steps,
    )
```

Add:

```python
def _shell_command(*parts: str) -> str:
    return shlex.join(parts)
```

- [ ] **Step 4: Run builder tests to verify GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_imported_review_workflow.py -q -k "build_imported_review_workflow"
```

Expected: builder tests pass.

## Task 2: Table Rendering

**Files:**
- Modify: `src/fashion_radar/imported_review_workflow.py`
- Test: `tests/test_imported_review_workflow.py`

- [ ] **Step 1: Write failing renderer tests**

Add:

```python
def test_render_imported_review_workflow_table() -> None:
    workflow = ImportedReviewWorkflow(
        as_of="2026-06-13T12:00:00+00:00",
        config_dir="./configs",
        data_dir="./data",
        step_count=2,
        steps=[
            ImportedReviewWorkflowStep(
                order=1,
                name="first | step\nname",
                purpose="Read | local\nstate.",
                command="fashion-radar imported-signals-summary --data-dir ./data",
                suggested_effect="read_only",
            ),
            ImportedReviewWorkflowStep(
                order=2,
                name="refresh_stored_matches",
                purpose="Refresh stored local matches.",
                command="fashion-radar match --config-dir ./configs --data-dir ./data",
                suggested_effect="updates_local_matches",
            ),
        ],
    )

    assert render_imported_review_workflow_table(workflow) == [
        "Imported manual signal review workflow.",
        "Execution mode: print_only",
        "Commands were not executed.",
        "As of: 2026-06-13T12:00:00+00:00",
        "Data dir: ./data",
        "Config dir: ./configs",
        "Source name: none",
        "Lookback days: 7",
        "Current days: 7",
        "Baseline days: 7",
        "Steps: 2",
        "Order | Step | Suggested Effect | Purpose | Command",
        "1 | first / step name | read_only | Read / local state. | fashion-radar imported-signals-summary --data-dir ./data",
        "2 | refresh_stored_matches | updates_local_matches | Refresh stored local matches. | fashion-radar match --config-dir ./configs --data-dir ./data",
    ]
```

Add:

```python
def test_render_imported_review_workflow_table_source_name() -> None:
    workflow = build_imported_review_workflow(
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
        source_name="Community Tool Export",
    )

    lines = render_imported_review_workflow_table(workflow)

    assert "Source name: Community Tool Export" in lines
```

- [ ] **Step 2: Run renderer tests to verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_imported_review_workflow.py -q -k "render_imported_review_workflow_table"
```

Expected: fail because renderer does not exist.

- [ ] **Step 3: Implement renderer**

Add:

```python
def render_imported_review_workflow_table(workflow: ImportedReviewWorkflow) -> list[str]:
    lines = [
        "Imported manual signal review workflow.",
        f"Execution mode: {workflow.execution_mode}",
        "Commands were not executed.",
        f"As of: {workflow.as_of}",
        f"Data dir: {_table_cell(workflow.data_dir)}",
        f"Config dir: {_table_cell(workflow.config_dir)}",
        f"Source name: {_table_cell(workflow.source_name or 'none')}",
        f"Lookback days: {workflow.lookback_days}",
        f"Current days: {workflow.current_days}",
        f"Baseline days: {workflow.baseline_days}",
        f"Steps: {workflow.step_count}",
        "Order | Step | Suggested Effect | Purpose | Command",
    ]
    for step in workflow.steps:
        lines.append(
            f"{step.order} | {_table_cell(step.name)} | {step.suggested_effect} | "
            f"{_table_cell(step.purpose)} | {_table_cell(step.command)}"
        )
    return lines
```

Add:

```python
def _table_cell(value: str) -> str:
    sanitized = value.replace("|", "/").replace("\r", " ").replace("\n", " ")
    return " ".join(sanitized.split())
```

- [ ] **Step 4: Run renderer tests to verify GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_imported_review_workflow.py -q -k "render_imported_review_workflow_table"
```

Expected: renderer tests pass.

## Task 3: CLI Command

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write failing CLI help and JSON tests**

Add near imported review command tests:

```python
def test_imported_review_workflow_command_help_lists_options() -> None:
    result = CliRunner().invoke(
        app,
        ["imported-review-workflow", "--help"],
        env={"COLUMNS": "120"},
    )

    assert result.exit_code == 0
    assert "--config-dir" in result.output
    assert "--data-dir" in result.output
    assert "--as-of" in result.output
    assert "--source-name" in result.output
    assert "--lookback-days" in result.output
    assert "--current-days" in result.output
    assert "--baseline-days" in result.output
    assert "--format" in result.output
    assert "Print a local imported signal review workflow" in result.output
```

Add:

```python
def test_imported_review_workflow_command_prints_json_with_stable_keys(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config dir"
    data_dir = tmp_path / "data dir"

    result = CliRunner().invoke(
        app,
        [
            "imported-review-workflow",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--source-name",
            "Community Tool Export",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert list(payload) == [
        "as_of",
        "config_dir",
        "data_dir",
        "source_name",
        "lookback_days",
        "current_days",
        "baseline_days",
        "execution_mode",
        "step_count",
        "steps",
    ]
    assert payload["as_of"] == "2026-06-13T12:00:00+00:00"
    assert payload["config_dir"] == str(config_dir)
    assert payload["data_dir"] == str(data_dir)
    assert payload["source_name"] == "Community Tool Export"
    assert payload["step_count"] == 4
    assert list(payload["steps"][0]) == [
        "order",
        "name",
        "purpose",
        "command",
        "suggested_effect",
    ]
    assert payload["execution_mode"] == "print_only"
    assert payload["steps"][1]["suggested_effect"] == "updates_local_matches"
    assert "--source-name 'Community Tool Export'" in payload["steps"][2]["command"]
    assert "--source-name 'Community Tool Export'" in payload["steps"][3]["command"]
```

- [ ] **Step 2: Write failing CLI guard tests**

Add:

```python
def _fail_imported_review_workflow_builder(*args, **kwargs):
    raise AssertionError("build_imported_review_workflow should not be called")
```

Add:

```python
def test_imported_review_workflow_command_rejects_invalid_format_without_builder(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        cli_module,
        "build_imported_review_workflow",
        _fail_imported_review_workflow_builder,
    )
    data_dir = tmp_path / "data"

    result = CliRunner().invoke(
        app,
        [
            "imported-review-workflow",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--format",
            "xml",
        ],
    )

    assert result.exit_code != 0
    assert "--format" in result.output
    assert "build_imported_review_workflow should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()
```

Add similar tests for invalid `--as-of` and invalid numeric options. The
invalid `--as-of` test should assert:

```python
assert "Could not build imported review workflow: invalid --as-of" in result.output
```

Add no-artifacts test:

```python
def test_imported_review_workflow_command_creates_no_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-review-workflow",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--format",
            "json",
        ],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 0
    assert_no_community_lint_artifacts(
        tmp_path,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
    )
```

- [ ] **Step 3: Run CLI tests to verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q -k "imported_review_workflow"
```

Expected: fail because the command and CLI import do not exist.

- [ ] **Step 4: Implement CLI command**

In `src/fashion_radar/cli.py`, import:

```python
from fashion_radar.imported_review_workflow import (
    build_imported_review_workflow,
    render_imported_review_workflow_table,
)
```

Add:

```python
ImportedReviewWorkflowOutputFormat = Literal["table", "json"]
```

Add option constants:

```python
IMPORTED_REVIEW_WORKFLOW_AS_OF_OPTION = typer.Option(
    ...,
    "--as-of",
    help="UTC workflow timestamp, for example 2026-06-13T12:00:00Z.",
)
IMPORTED_REVIEW_WORKFLOW_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
```

Add before `imported_entity_deltas_command()`:

```python
@app.command(name="imported-review-workflow")
def imported_review_workflow_command(
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    as_of: str = IMPORTED_REVIEW_WORKFLOW_AS_OF_OPTION,
    source_name: str | None = typer.Option(None, help="Exact stored source name filter."),
    lookback_days: int = typer.Option(7, min=1, help="Imported row review window in days."),
    current_days: int = typer.Option(7, min=1, help="Entity delta current window in days."),
    baseline_days: int = typer.Option(7, min=1, help="Entity delta baseline window in days."),
    output_format: ImportedReviewWorkflowOutputFormat = IMPORTED_REVIEW_WORKFLOW_FORMAT_OPTION,
) -> None:
    """Print a local imported signal review workflow without executing it."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(
                f"Could not build imported review workflow: invalid --as-of: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc
        workflow = build_imported_review_workflow(
            config_dir=config_dir,
            data_dir=data_dir,
            as_of=as_of_value,
            source_name=source_name,
            lookback_days=lookback_days,
            current_days=current_days,
            baseline_days=baseline_days,
        )
    except typer.Exit:
        raise
    except Exception as exc:
        typer.echo(f"Could not build imported review workflow: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(workflow.model_dump_json(indent=2))
        return
    for line in render_imported_review_workflow_table(workflow):
        typer.echo(line)
```

- [ ] **Step 5: Run CLI tests to verify GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q -k "imported_review_workflow"
```

Expected: CLI tests pass.

## Task 4: Documentation And Changelog

**Files:**
- Modify: `README.md`
- Modify: `docs/manual-signal-import.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/community-signal-quality.md`
- Modify: `docs/architecture.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add bounded examples**

Add near imported review examples:

```bash
uv run fashion-radar imported-review-workflow --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar imported-review-workflow --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --format json
```

Use prose:

```markdown
`imported-review-workflow` is local and does not execute commands. It prints a
copyable review sequence for existing local commands after manual signal import.
```

- [ ] **Step 2: Update upload checklist**

Add installed-wheel smoke command:

```bash
"$tmp_env/venv/bin/fashion-radar" imported-review-workflow --help
```

- [ ] **Step 3: Update changelog**

Add under `### Added`:

```markdown
- Local `imported-review-workflow` command for printing a copyable post-import
  review sequence without executing it.
```

- [ ] **Step 4: Run docs boundary scan**

Run:

```bash
git diff -U0 -- README.md docs CHANGELOG.md | rg -n "platform-wide|market-wide|verified demand|real-time monitoring|source acquisition|source-acquisition|platform search|social monitoring|authorization verifier|approval workflow|audit workflow|policy workflow|source health|source quality|source coverage|source ranking|top sources|top-sources"
```

Expected: no new capability wording from Stage 24 product docs.

## Task 5: Review, Verification, And Release

**Files:**
- Create: `docs/reviews/claude-code-stage-24-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-24-code-review.md`
- Modify: any file needed to fix Critical or Important review findings

- [ ] **Step 1: Run focused verification**

Run:

```bash
.venv/bin/python -m pytest tests/test_imported_review_workflow.py tests/test_cli.py -q -k "imported_review_workflow or imported_entity_deltas or imported_signals"
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
```

Expected: all pass.

- [ ] **Step 2: Request Claude Code code review**

Create `docs/reviews/claude-code-stage-24-code-review-prompt.md` asking Claude
Code to review the current working tree in read-only mode. Required review
focus:

- command only prints existing local commands and executes nothing;
- no SQLite/config reads or artifact creation;
- invalid CLI inputs avoid builder execution;
- shell quoting is safe and deterministic;
- JSON/table contracts are stable;
- docs remain local and do not imply automation, external integrations, ranking,
  source quality, or coverage.

Run:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-24-code-review-prompt.md | tee docs/reviews/claude-code-stage-24-code-review.md
```

Fix every Critical and Important finding before continuing.

- [ ] **Step 3: Run full release checks**

Run:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
uv lock --check --default-index https://pypi.org/simple
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
rm -rf /tmp/fashion-radar-dist-stage24
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv build --out-dir /tmp/fashion-radar-dist-stage24
```

Expected: all pass.

- [ ] **Step 4: Run installed-wheel smoke**

Run:

```bash
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv" --python 3.11
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv pip install --python "$tmp_env/venv/bin/python" /tmp/fashion-radar-dist-stage24/*.whl
"$tmp_env/venv/bin/fashion-radar" imported-review-workflow --help
"$tmp_env/venv/bin/fashion-radar" imported-review-workflow --data-dir "$tmp_env/data ? # & %" --config-dir "$tmp_env/config ? # & %" --as-of "2026-06-13T12:00:00Z" --format json
```

Expected: both commands exit zero and print no traceback.

- [ ] **Step 5: Run repository hygiene scans**

Run:

```bash
rg -n "ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]+" . --glob '!uv.lock' --glob '!*.pyc' --glob '!__pycache__/**' --glob '!.venv/**' --glob '!data/**' --glob '!reports/**' --glob '!.codegraph/**'
find . \( -name '*.sqlite' -o -name '*.sqlite-*' -o -name '*.sqlite3' -o -name '*.db' -o -name '*.pyc' -o -name '__pycache__' -o -name 'dist' -o -name 'build' -o -name '*.egg-info' -o -name '.pytest_cache' -o -name '.ruff_cache' \) -not -path './.venv/*' -not -path './.git/*' -not -path './.codegraph/*' -print
```

Expected: no secrets or generated artifacts that should be committed.

- [ ] **Step 6: Commit and push**

This repository is currently using the user-authorized direct-main upload
workflow. Do this step only after Claude Code code review has no Critical or
Important findings and all release checks pass. If the workflow changes to a
branch/PR flow, stop and adapt this step before pushing.

Run:

```bash
current_branch="$(git branch --show-current)"
if [ "$current_branch" != "main" ]; then
  echo "Not on main; stop and adapt push target."
  exit 1
fi
git status --short --branch
git add src/fashion_radar/imported_review_workflow.py src/fashion_radar/cli.py tests/test_imported_review_workflow.py tests/test_cli.py README.md docs CHANGELOG.md
git commit -m "Add imported review workflow command"
git -c http.version=HTTP/1.1 -c http.curloptResolve=github.com:443:140.82.113.4 push origin main
```

Expected: branch is `main`, commit succeeds, and push updates `origin/main`.

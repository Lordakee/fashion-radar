# Stage 284 ROW ONE Latest Report Retention Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `row-one refresh` enforce latest-only local report artifact retention by removing stale dated Markdown, JSON, and HTML report files while keeping the freshly generated edition.

**Architecture:** Add a narrow workflow helper that recognizes only Fashion Radar dated report artifact names under the selected reports directory and prunes dates strictly older than the active `as_of` date. Wire the helper into `row_one_refresh` after successful ROW ONE site generation, print a small cleanup summary, and update ROW ONE docs so the behavior matches the user's local latest-only requirement. Do not prune the SQLite database in this stage because historical stored items support scoring windows and heat movement.

**Tech Stack:** Python 3.11+, Typer CLI, pathlib, pytest, ruff, uv.

---

## Files

- Modify: `src/fashion_radar/workflows.py`
  - Add a small `ReportRetentionResult` dataclass.
  - Add `prune_stale_daily_report_files(*, reports_dir: Path, as_of: str | datetime) -> ReportRetentionResult`.
  - Reuse the existing digest daily report filename parser for Markdown/JSON report dates and apply matching date parsing for HTML report artifacts.
  - Keep `write_daily_report_files` behavior unchanged.
- Modify: `src/fashion_radar/cli.py`
  - Import and call `prune_stale_daily_report_files` inside `row_one_refresh` after ROW ONE site rendering succeeds.
  - Print a deterministic cleanup summary line.
- Modify: `tests/test_workflows.py`
  - Add focused unit tests for pruning stale dated report artifacts and keeping current/nonmatching files.
- Modify: `tests/test_row_one_cli.py`
  - Add assertions that `row-one refresh` calls the retention helper after writing reports, before building the site, and prints the summary.
- Modify: `tests/test_row_one_docs.py`
  - Replace the old doc guard that says dated report artifacts are not deleted.
- Modify: `scripts/check_first_run_smoke.py`
  - Add an end-to-end smoke check that `row-one refresh` prunes stale generated report artifacts while keeping current reports and unrelated files.
- Modify: `docs/row-one.md`
  - Update the generated-files and command wording so `row-one refresh` documents dated report artifact pruning.
- Modify: `reports/README.md`
  - Add concise wording that ROW ONE refresh may remove stale dated report artifacts in a user-selected reports directory.
- Modify: `README.md`
  - Clarify that ROW ONE report artifact pruning is separate from database retention.
- Add: `docs/reviews/claude-code-stage-284-plan-review-prompt.md`
- Add after review: `docs/reviews/claude-code-stage-284-plan-review.md`
- Add after implementation: `docs/reviews/claude-code-stage-284-code-review-prompt.md`
- Add after implementation: `docs/reviews/claude-code-stage-284-code-review.md`

## Task 1: Add Workflow Retention Tests

**Files:**
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Import the new helper**

Update the workflow import block:

```python
from fashion_radar.workflows import (
    _default_collectors,
    clean_old_data,
    collect_configured_sources,
    default_database_path,
    match_stored_items,
    prune_stale_daily_report_files,
    write_daily_report_files,
)
```

- [ ] **Step 2: Add a failing test for stale dated artifacts**

Add this test after `test_write_daily_report_files_writes_html_with_recent_window_items`:

```python
def test_prune_stale_daily_report_files_removes_old_dated_artifacts(tmp_path: Path) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    stale_names = [
        "fashion-radar-2026-07-01.md",
        "fashion-radar-2026-07-01.json",
        "fashion-radar-2026-07-01.html",
        "fashion-radar-2026-06-30.md",
    ]
    current_names = [
        "fashion-radar-2026-07-02.md",
        "fashion-radar-2026-07-02.json",
        "fashion-radar-2026-07-02.html",
    ]
    untouched_names = [
        "latest.md",
        "latest.json",
        "report-index.json",
        "fashion-radar-2026-07-01.eml",
        "fashion-radar-2026-07-01.txt",
        "fashion-radar-not-a-date.md",
        "notes.md",
    ]
    for name in stale_names + current_names + untouched_names:
        (reports_dir / name).write_text(name, encoding="utf-8")

    result = prune_stale_daily_report_files(
        reports_dir=reports_dir,
        as_of=datetime(2026, 7, 2, 4, 0, tzinfo=UTC),
    )

    assert result.removed_count == len(stale_names)
    assert result.kept_current_count == len(current_names)
    assert result.current_date == "2026-07-02"
    assert [path.name for path in result.removed_paths] == sorted(stale_names)
    for name in stale_names:
        assert not (reports_dir / name).exists()
    for name in current_names + untouched_names:
        assert (reports_dir / name).exists()
```

- [ ] **Step 3: Add a failing test for missing reports directory**

Add:

```python
def test_prune_stale_daily_report_files_missing_directory_is_noop(tmp_path: Path) -> None:
    reports_dir = tmp_path / "missing-reports"

    result = prune_stale_daily_report_files(
        reports_dir=reports_dir,
        as_of=datetime(2026, 7, 2, 4, 0, tzinfo=UTC),
    )

    assert result.removed_count == 0
    assert result.kept_current_count == 0
    assert result.current_date == "2026-07-02"
    assert result.removed_paths == []
```

- [ ] **Step 4: Run RED workflow tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run pytest \
  tests/test_workflows.py::test_prune_stale_daily_report_files_removes_old_dated_artifacts \
  tests/test_workflows.py::test_prune_stale_daily_report_files_missing_directory_is_noop \
  -q
```

Expected: import error or missing-symbol failure for `prune_stale_daily_report_files`.

## Task 2: Implement Workflow Retention Helper

**Files:**
- Modify: `src/fashion_radar/workflows.py`

- [ ] **Step 1: Add imports**

Add:

```python
import re
from dataclasses import dataclass
from datetime import date
```

- [ ] **Step 2: Add constants and result dataclass**

Near the report path helpers, add:

```python
_DAILY_REPORT_HTML_ARTIFACT_RE = re.compile(
    r"^fashion-radar-(?P<report_date>\d{4}-\d{2}-\d{2})\.html$"
)


@dataclass(frozen=True)
class ReportRetentionResult:
    current_date: str
    removed_paths: list[Path]
    kept_current_count: int

    @property
    def removed_count(self) -> int:
        return len(self.removed_paths)
```

- [ ] **Step 3: Add pruning helper**

Add after `write_daily_report_files`:

```python
def _parse_daily_report_retention_path(path: Path) -> date | None:
    parsed_daily_path = _parse_daily_report_path(path)
    if parsed_daily_path is not None:
        report_date, _extension = parsed_daily_path
        return report_date
    match = _DAILY_REPORT_HTML_ARTIFACT_RE.fullmatch(path.name)
    if match is None:
        return None
    try:
        return date.fromisoformat(match.group("report_date"))
    except ValueError:
        return None


def prune_stale_daily_report_files(
    *,
    reports_dir: Path,
    as_of: str | datetime,
) -> ReportRetentionResult:
    current_report_date = parse_datetime_utc(as_of).date()
    current_date = current_report_date.isoformat()
    if not reports_dir.exists():
        return ReportRetentionResult(
            current_date=current_date,
            removed_paths=[],
            kept_current_count=0,
        )

    removed_paths: list[Path] = []
    kept_current_count = 0
    for path in sorted(reports_dir.iterdir(), key=lambda candidate: candidate.name):
        if not path.is_file():
            continue
        report_date = _parse_daily_report_retention_path(path)
        if report_date is None:
            continue
        if report_date == current_report_date:
            kept_current_count += 1
            continue
        if report_date > current_report_date:
            continue
        path.unlink()
        removed_paths.append(path)

    return ReportRetentionResult(
        current_date=current_date,
        removed_paths=removed_paths,
        kept_current_count=kept_current_count,
    )
```

- [ ] **Step 4: Run GREEN workflow tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run pytest \
  tests/test_workflows.py::test_prune_stale_daily_report_files_removes_old_dated_artifacts \
  tests/test_workflows.py::test_prune_stale_daily_report_files_missing_directory_is_noop \
  -q
```

Expected: `2 passed`.

## Task 3: Wire Retention Into `row-one refresh`

**Files:**
- Modify: `tests/test_row_one_cli.py`
- Modify: `src/fashion_radar/cli.py`

- [ ] **Step 1: Add failing CLI test assertions**

In `test_row_one_refresh_runs_pipeline_and_writes_site`, add a monkeypatched helper:

```python
    def prune_stale_daily_report_files(**kwargs: object) -> SimpleNamespace:
        assert kwargs["reports_dir"] == reports_dir
        assert kwargs["as_of"] == AS_OF
        calls.append("prune_stale_daily_report_files")
        return SimpleNamespace(
            current_date="2026-07-02",
            removed_count=3,
            kept_current_count=3,
        )
```

Patch it:

```python
    monkeypatch.setattr(
        cli_module,
        "prune_stale_daily_report_files",
        prune_stale_daily_report_files,
    )
```

Update expected calls:

```python
    assert calls == [
        "collect_configured_sources",
        "match_stored_items",
        "write_daily_report_files",
        "_write_row_one_site_from_cli_options",
        "prune_stale_daily_report_files",
    ]
```

Add output assertion:

```python
    assert "Latest-only reports: removed 3 stale files for 2026-07-02; kept 3 current files" in (
        result.output
    )
```

- [ ] **Step 2: Run RED CLI test**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run pytest \
  tests/test_row_one_cli.py::test_row_one_refresh_runs_pipeline_and_writes_site \
  -q
```

Expected: missing `prune_stale_daily_report_files` call/output failure.

- [ ] **Step 3: Import and call helper in CLI**

In `src/fashion_radar/cli.py`, include `prune_stale_daily_report_files` in the existing `fashion_radar.workflows` import list.

Inside `row_one_refresh`, after `_write_row_one_site_from_cli_options(...)` succeeds, add:

```python
        report_retention = prune_stale_daily_report_files(
            reports_dir=reports_dir,
            as_of=as_of,
        )
```

After the HTML report line, add:

```python
    typer.echo(
        "Latest-only reports: "
        f"removed {report_retention.removed_count} stale files for "
        f"{report_retention.current_date}; "
        f"kept {report_retention.kept_current_count} current files"
    )
```

- [ ] **Step 4: Run GREEN CLI test**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run pytest \
  tests/test_row_one_cli.py::test_row_one_refresh_runs_pipeline_and_writes_site \
  -q
```

Expected: `1 passed`.

## Task 4: Update Documentation And Smoke Guards

**Files:**
- Modify: `docs/row-one.md`
- Modify: `reports/README.md`
- Modify: `README.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `scripts/check_first_run_smoke.py`

- [ ] **Step 1: Update ROW ONE generated-files wording**

In `docs/row-one.md`, replace the paragraph that says `row-one refresh` does not delete dated report artifacts with wording that distinguishes site cleanup and refresh report cleanup:

```markdown
The latest-only cleanup has two local presentation surfaces.
`row-one build --latest-only` and `row-one preview --latest-only` remove only known ROW ONE generated children:
`index.html`, `.row-one-site`, `details/`, `assets/`, and `data/`. It does not
delete unrelated files in the output directory. If an existing directory has
generated-looking children but no `.row-one-site` marker, cleanup refuses to
continue so user files are not silently removed.

`row-one refresh` is latest-only for the local ROW ONE presentation path: after
writing the current dated report and rebuilding the site, it prunes older
generated report artifacts in the selected `--reports-dir` that match
`fashion-radar-YYYY-MM-DD.md`, `fashion-radar-YYYY-MM-DD.json`, and
`fashion-radar-YYYY-MM-DD.html`. It keeps the current refresh date's report
artifacts and does not prune SQLite data, collected rows, matcher rows, source
config, connectors, or files outside the local reports/site output surfaces.
Nonmatching digest and note files such as `latest.md`, `latest.json`,
`report-index.json`, `fashion-radar-YYYY-MM-DD.eml`, and local notes are left
untouched.
```

- [ ] **Step 2: Update command wording**

In the `row-one refresh` command bullet, write:

```markdown
- `row-one refresh`: runs the single local daily refresh command for ROW ONE by
  refreshing the daily report data and generated site in one command. Important
  flags: `--as-of`, `--reports-dir`, and `--output-dir`; latest-only site cleanup
  is built in, and older generated dated report artifacts in `--reports-dir` are
  pruned after the current report is written.
```

- [ ] **Step 3: Update reports README**

Append:

```markdown
`row-one refresh` keeps the ROW ONE local presentation path latest-only by
pruning older generated dated report artifacts in this directory that match
`fashion-radar-YYYY-MM-DD.md`, `fashion-radar-YYYY-MM-DD.json`, and
`fashion-radar-YYYY-MM-DD.html`. This is local report artifact retention only;
it does not prune SQLite data, collected items, matcher rows, source config,
connectors, `.eml` digest artifacts, report indexes, latest digest files, or
non-report files.
```

- [ ] **Step 4: Update README ROW ONE and cleanup wording**

In `README.md`, add a sentence near the `row-one refresh` documentation:

```markdown
For the ROW ONE presentation path, `row-one refresh` also keeps generated dated
report artifacts latest-only in the selected `--reports-dir`, pruning older
`fashion-radar-YYYY-MM-DD.{md,json,html}` files while leaving SQLite/data
retention to `clean-old-data`.
```

Near the cleanup section, add:

```markdown
ROW ONE report artifact pruning is separate from database retention:
`row-one refresh` may prune older generated dated report files for the local
presentation path, while `clean-old-data` is the command for pruning old
collected SQLite rows.
```

- [ ] **Step 5: Update ROW ONE docs test**

In `tests/test_row_one_docs.py`, replace the old expected phrase:

```python
"does not delete dated report artifacts",
```

with lower-case checks for the new boundary:

```python
"row-one refresh",
"prunes older generated report artifacts",
"`fashion-radar-yyyy-mm-dd.md`",
"`fashion-radar-yyyy-mm-dd.json`",
"`fashion-radar-yyyy-mm-dd.html`",
"does not prune sqlite data",
"`fashion-radar-yyyy-mm-dd.eml`",
```

- [ ] **Step 6: Update first-run smoke script**

In `scripts/check_first_run_smoke.py`, before the existing `row-one preview`
smoke block, define `row_one_output_dir = context.reports_dir / "row-one" / "site"` if needed and add:

```python
stale_report_artifact_names = (
    "fashion-radar-2026-06-12.md",
    "fashion-radar-2026-06-12.json",
    "fashion-radar-2026-06-12.html",
)
for name in stale_report_artifact_names:
    (context.reports_dir / name).write_text("stale", encoding="utf-8")
untouched_report_note = context.reports_dir / "notes.txt"
untouched_report_note.write_text("keep me", encoding="utf-8")
run_cli(
    context,
    "row-one",
    "refresh",
    "--config-dir",
    str(context.config_dir),
    "--data-dir",
    str(context.data_dir),
    "--reports-dir",
    str(context.reports_dir),
    "--output-dir",
    str(row_one_output_dir),
    "--as-of",
    AS_OF,
)
for name in stale_report_artifact_names:
    assert_not_exists(context.reports_dir / name)
assert_non_empty_file(context.reports_dir / "fashion-radar-2026-06-13.md")
assert_non_empty_file(context.reports_dir / "fashion-radar-2026-06-13.json")
assert_non_empty_file(context.reports_dir / "fashion-radar-2026-06-13.html")
assert_non_empty_file(untouched_report_note)
```

If `assert_not_exists` does not exist, add:

```python
def assert_not_exists(path: Path) -> None:
    if path.exists():
        raise SmokeError(f"unexpected path exists: {path}")
```

- [ ] **Step 7: Run docs-adjacent checks**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run pytest \
  tests/test_row_one_docs.py tests/test_first_run_smoke.py \
  tests/test_row_one_cli.py tests/test_workflows.py \
  -q
```

Expected: all selected tests pass.

## Task 5: Verify, Review, Commit, And Push

**Files:**
- Add: `docs/reviews/claude-code-stage-284-code-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-284-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run pytest tests/test_workflows.py tests/test_row_one_cli.py -q
UV_NO_CONFIG=1 uv --no-config run pytest tests/test_row_one_docs.py tests/test_first_run_smoke.py -q
UV_NO_CONFIG=1 uv --no-config run python scripts/check_first_run_smoke.py --repo-root .
```

Expected: selected tests pass.

- [ ] **Step 2: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run ruff check .
UV_NO_CONFIG=1 uv --no-config run ruff format --check .
UV_NO_CONFIG=1 uv --no-config run pytest -q
UV_NO_CONFIG=1 uv --no-config lock --check
git diff --check
git diff --exit-code -- uv.lock pyproject.toml
```

Expected: all commands exit 0.

- [ ] **Step 3: Request Claude Code code review**

Create `docs/reviews/claude-code-stage-284-code-review-prompt.md` with the objective, constraints, `git diff --stat`, `git diff`, and verification evidence. Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-284-code-review-prompt.md)" \
  > /tmp/claude-code-stage-284-code-review.md
```

Copy the completed review into:

```text
docs/reviews/claude-code-stage-284-code-review.md
```

Fix Critical and Important findings before committing.

- [ ] **Step 4: Commit and push**

Run:

```bash
git status --short
git add src/fashion_radar/workflows.py src/fashion_radar/cli.py \
  tests/test_workflows.py tests/test_row_one_cli.py \
  tests/test_row_one_docs.py scripts/check_first_run_smoke.py \
  docs/row-one.md reports/README.md README.md \
  docs/superpowers/plans/2026-07-03-stage-284-row-one-latest-report-retention-plan.md \
  docs/reviews/claude-code-stage-284-plan-review-prompt.md \
  docs/reviews/claude-code-stage-284-plan-review.md \
  docs/reviews/claude-code-stage-284-code-review-prompt.md \
  docs/reviews/claude-code-stage-284-code-review.md
git commit -m "Stage 284: enforce row one latest report retention"
git push origin main
```

- [ ] **Step 5: Handoff Summary**

Report:

- Repo status
- Verified commands
- Uncommitted files
- Next step

## Self-Review

- Spec coverage: The plan closes the local latest-only gap for generated report artifacts while leaving the ROW ONE site latest-only behavior intact.
- Boundaries: No source collection, social connector, image generation, deployment, scheduler, schema, or DB pruning work is included.
- TDD: Tests are added and run red before implementation, then green after the minimal helper/CLI wiring.
- Risk: The helper only touches top-level regular files matching `fashion-radar-YYYY-MM-DD.(md|json|html)` in the selected reports directory, so unrelated files and generated site directories are preserved.

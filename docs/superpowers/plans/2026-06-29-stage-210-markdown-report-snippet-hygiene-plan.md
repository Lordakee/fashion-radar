# Stage 210 Markdown Report Snippet Hygiene Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply the existing `report_safe_snippet(...)` helper to the Markdown `## Source Health` and `## Recent Collector Runs` renderers so long, multi-line, or whitespace-heavy collector/source error messages are collapsed and truncated in Markdown reports without changing JSON report fields, report model contracts, scoring, ranking, source acquisition, dashboard behavior, or dependencies.

**Architecture:** Report-rendering-only change inside `src/fashion_radar/reports.py`. `_render_source_health_line(...)` and `_render_recent_runs(...)` currently interpolate raw `SourceHealthReport.last_error_message` / `CollectorRunReport.error_message` strings directly into Markdown. Stage 210 routes those strings through the already-imported `report_safe_snippet(...)` helper (defined in `src/fashion_radar/models/report.py`, already imported at `reports.py:25`), which collapses internal whitespace to single spaces, drops empty values to `None`, and truncates to `REPORT_SNIPPET_MAX_CHARS` (500) with a trailing `...`. The Pydantic models `SourceHealthReport` and `CollectorRunReport` are NOT modified, so `render_json_report(...)` continues to emit raw error fields and the `daily-brief/v1` and `DailyReport` contracts are unchanged.

**Tech Stack:** Python 3.11, existing Pydantic report models, existing `report_safe_snippet` helper, existing Markdown report template, pytest, Markdown docs, `uv --no-config run --frozen`, local OpenCode review with `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Core Product Gap

This stage closes a small report-hygiene gap in the local `collect -> match ->
report` pipeline. `RepresentativeItem.summary` already routes through
`report_safe_snippet(...)` at the model layer
(`src/fashion_radar/models/report.py:51-54`), so a representative item summary
can never dump a 5 KB multi-line blob into a Markdown report.

The two collector/source error surfaces do not have that hygiene:

- `_render_source_health_line(...)` at `src/fashion_radar/reports.py:746-753`
  interpolates `source.last_error_message or 'no error'` verbatim.
- `_render_recent_runs(...)` at `src/fashion_radar/reports.py:756-766`
  interpolates `run.error_message` verbatim when it is truthy.

A long stack trace, a multi-line exception body, or a whitespace-padded error
string therefore lands in the generated Markdown `## Source Health` and
`## Recent Collector Runs` sections unfiltered, which pollutes the report and
can push real signals off the visible window.

Stage 210 reuses the existing `report_safe_snippet(...)` helper on the Markdown
render path only. It is a presentation/hygiene improvement; it is not a
scoring, ranking, extraction, schema, demand, coverage, social, or acquisition
change.

## Scope

In scope:

- Route `SourceHealthReport.last_error_message` through
  `report_safe_snippet(...)` inside `_render_source_health_line(...)`.
- Route `CollectorRunReport.error_message` through `report_safe_snippet(...)`
  inside `_render_recent_runs(...)`.
- Preserve the existing `no error` Markdown fallback for source-health rows
  whose error message snippet returns `None`.
- Skip the trailing `; <error>` segment for collector-run rows whose error
  message snippet returns `None` (including whitespace-only inputs).
- Add tests proving:
  - Markdown `## Source Health` collapses multi-line errors and truncates long
    errors to a report-safe snippet ending in `...`, dropping the overflow
    marker.
  - Markdown `## Recent Collector Runs` collapses multi-line errors and
    truncates long errors to a report-safe snippet ending in `...`.
  - Markdown keeps the `no error` fallback when a source-health error is
    `None`, and omits the `; <error>` segment when a collector-run error is
    `None` or whitespace-only.
  - JSON report keeps the raw, untruncated, un-collapsed `last_error_message`
    and `error_message` values unchanged.
- Update `README.md`, `docs/architecture.md`, and `docs/cli-reference.md` with
  narrow wording that Markdown Source Health and Recent Collector Runs sections
  collapse whitespace and truncate long error messages to report-safe snippets,
  while JSON error fields stay raw.
- Add a focused docs guard in `tests/test_cli_docs.py` pinning that wording.
- Add a Stage 210 changelog entry.
- Add Stage 210 OpenCode plan/code/release review artifacts.

Out of scope:

- No change to `SourceHealthReport`, `CollectorRunReport`, `DailyReport`,
  `DailyBrief`, `DailyBriefItem`, or any other Pydantic model.
- No change to `report_safe_snippet(...)` or `REPORT_SNIPPET_MAX_CHARS`.
- No new fields, no `contract_version` change, no JSON contract change.
- No change to `render_json_report(...)` behavior; JSON error fields stay raw.
- No change to collectors, source acquisition, source configs, source packs,
  source-liveness, HTTP/proxy behavior, scoring, ranking, candidate extraction,
  thresholds, DB schema, migrations, dashboard, CLI commands, or workflows.
- No change to social/platform connectors, scraping, browser automation,
  login/cookie/token behavior, demand proof, platform coverage verification, or
  compliance-review product features.
- No change to `pyproject.toml`, `uv.lock`, or any dependency manifest.
- No change to CI workflows.

## File Map

- Modify `src/fashion_radar/reports.py`
  - `_render_source_health_line(...)` (lines 746-753): wrap
    `source.last_error_message` in `report_safe_snippet(...)`.
  - `_render_recent_runs(...)` (lines 756-766): wrap `run.error_message` in
    `report_safe_snippet(...)` and guard on the snippet result.
- Modify `tests/test_reports.py`
  - Add `LONG_ERROR` and `MULTILINE_ERROR` module-level constants.
  - Add Markdown source-health snippet tests (long, multi-line, `None`).
  - Add Markdown recent-runs snippet tests (long, multi-line, whitespace-only,
    `None`).
  - Add a JSON contract test pinning raw error fields.
- Modify `README.md`
  - Extend the generated-reports bullet so it states Markdown Source Health and
    Recent Collector Runs sections collapse whitespace and truncate long error
    messages to report-safe snippets, while JSON error fields stay raw.
- Modify `docs/architecture.md`
  - Extend the Reports bullet with the same snippet-hygiene wording.
- Modify `docs/cli-reference.md`
  - Extend the `report` bullet with the same snippet-hygiene wording.
- Modify `tests/test_cli_docs.py`
  - Add a focused docs guard test pinning the new wording across README,
    architecture, and CLI reference.
- Modify `CHANGELOG.md`
  - Add the Stage 210 entry under `[Unreleased] -> ### Added`.
- Add review artifacts under `docs/reviews/`.

Do not modify `pyproject.toml` or `uv.lock`.

## Task 0: Plan Review

**Files:**

- Add: `docs/reviews/opencode-stage-210-plan-review-prompt.md`
- Add: `docs/reviews/opencode-stage-210-plan-review.md`

- [ ] **Step 1: Create the plan-review prompt**

Create `docs/reviews/opencode-stage-210-plan-review-prompt.md` asking OpenCode
to review this plan for report-only scope, Markdown-only snippet application,
JSON/raw-field contract preservation, existing `no error` / `; <error>`
fallback behavior, test coverage, docs wording, release hygiene, and avoidance
of source/social/dependency/scoring/model changes.

- [ ] **Step 2: Run OpenCode plan review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-210-plan-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-210-plan-review.md
rm -f "$tmp_review"
```

Expected: completed review artifact with no Critical or Important blockers.
Fix Critical/Important planning findings and run a rereview before Task 1.

## Task 1: RED Tests For Markdown Error Snippet Hygiene

**Files:**

- Modify: `tests/test_reports.py`

- [ ] **Step 1: Add error-message fixtures**

Add these module-level constants immediately after the existing `LONG_SUMMARY`
definition at `tests/test_reports.py:43`:

```python
LONG_ERROR = "timeout: " + ("retry detail " * 80) + "TAIL_MARKER"
MULTILINE_ERROR = "connection reset\n  by peer\n\nretry exhausted TAIL_MARKER"
WHITESPACE_ONLY_ERROR = "   \n\t  "
```

`LONG_ERROR` collapses to well over `REPORT_SNIPPET_MAX_CHARS` so it exercises
truncation; `MULTILINE_ERROR` collapses to a short single-line string so it
exercises whitespace collapse without truncation; `WHITESPACE_ONLY_ERROR`
collapses to an empty string so `report_safe_snippet(...)` returns `None`.

- [ ] **Step 2: Add Markdown Source Health snippet tests**

Append these tests to `tests/test_reports.py`:

```python
def test_markdown_source_health_collapses_and_truncates_long_error() -> None:
    report = DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF),
        source_health=[
            SourceHealthReport(
                source_name="WWD",
                source_type="rss",
                consecutive_failures=3,
                unhealthy_until=AS_OF + timedelta(hours=1),
                last_error_message=LONG_ERROR,
            )
        ],
    )

    markdown = render_markdown_report(report)
    source_health_section = markdown.split("## Source Health", 1)[1].split(
        "## Recent Collector Runs", 1
    )[0]

    assert "WWD (rss)" in source_health_section
    assert "3 consecutive failures" in source_health_section
    assert "TAIL_MARKER" not in source_health_section
    assert "retry detail" in source_health_section
    assert source_health_section.rstrip().endswith("...")


def test_markdown_source_health_collapses_multiline_error() -> None:
    report = DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF),
        source_health=[
            SourceHealthReport(
                source_name="Fashionista",
                source_type="rss",
                consecutive_failures=2,
                last_error_message=MULTILINE_ERROR,
            )
        ],
    )

    markdown = render_markdown_report(report)
    source_health_section = markdown.split("## Source Health", 1)[1].split(
        "## Recent Collector Runs", 1
    )[0]

    assert (
        "connection reset by peer retry exhausted TAIL_MARKER"
        in source_health_section
    )
    assert "connection reset\n  by peer" not in source_health_section
    assert "retry exhausted TAIL_MARKER" in source_health_section


def test_markdown_source_health_without_error_keeps_no_error_fallback() -> None:
    report = DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF),
        source_health=[
            SourceHealthReport(
                source_name="WWD",
                source_type="rss",
                consecutive_failures=0,
                last_error_message=None,
            )
        ],
    )

    markdown = render_markdown_report(report)
    source_health_section = markdown.split("## Source Health", 1)[1].split(
        "## Recent Collector Runs", 1
    )[0]

    assert "no error" in source_health_section
    assert "None" not in source_health_section
```

- [ ] **Step 3: Add Markdown Recent Collector Runs snippet tests**

Append these tests to `tests/test_reports.py`:

```python
def test_markdown_recent_runs_collapses_and_truncates_long_error() -> None:
    report = DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF),
        recent_runs=[
            CollectorRunReport(
                source_name="WWD",
                source_type="rss",
                status="failed",
                started_at=AS_OF - timedelta(minutes=5),
                finished_at=AS_OF - timedelta(minutes=4),
                items_seen=0,
                items_stored=0,
                error_message=LONG_ERROR,
            )
        ],
    )

    markdown = render_markdown_report(report)
    recent_runs_section = markdown.split("## Recent Collector Runs", 1)[1]

    assert "WWD (rss)" in recent_runs_section
    assert "failed" in recent_runs_section
    assert "0/0 stored" in recent_runs_section
    assert "TAIL_MARKER" not in recent_runs_section
    assert "retry detail" in recent_runs_section
    assert recent_runs_section.rstrip().endswith("...")


def test_markdown_recent_runs_collapses_multiline_error() -> None:
    report = DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF),
        recent_runs=[
            CollectorRunReport(
                source_name="Fashionista",
                source_type="rss",
                status="failed",
                started_at=AS_OF - timedelta(minutes=5),
                finished_at=AS_OF - timedelta(minutes=4),
                items_seen=4,
                items_stored=2,
                error_message=MULTILINE_ERROR,
            )
        ],
    )

    markdown = render_markdown_report(report)
    recent_runs_section = markdown.split("## Recent Collector Runs", 1)[1]

    assert (
        "connection reset by peer retry exhausted TAIL_MARKER"
        in recent_runs_section
    )
    assert "connection reset\n  by peer" not in recent_runs_section


def test_markdown_recent_runs_omits_error_segment_when_snippet_is_none() -> None:
    report = DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF),
        recent_runs=[
            CollectorRunReport(
                source_name="WWD",
                source_type="rss",
                status="ok",
                started_at=AS_OF - timedelta(minutes=5),
                finished_at=AS_OF - timedelta(minutes=4),
                items_seen=9,
                items_stored=9,
                error_message=WHITESPACE_ONLY_ERROR,
            ),
            CollectorRunReport(
                source_name="Fashionista",
                source_type="rss",
                status="ok",
                started_at=AS_OF - timedelta(minutes=3),
                finished_at=AS_OF - timedelta(minutes=2),
                items_seen=7,
                items_stored=7,
                error_message=None,
            ),
        ],
    )

    markdown = render_markdown_report(report)
    recent_runs_section = markdown.split("## Recent Collector Runs", 1)[1]

    wwd_line = next(
        line for line in recent_runs_section.splitlines() if "WWD (rss)" in line
    )
    fashionista_line = next(
        line
        for line in recent_runs_section.splitlines()
        if "Fashionista (rss)" in line
    )
    assert wwd_line.endswith("9/9 stored")
    assert ";" not in wwd_line
    assert fashionista_line.endswith("7/7 stored")
    assert ";" not in fashionista_line
```

- [ ] **Step 4: Add JSON raw-field contract test**

Append this test to `tests/test_reports.py`:

```python
def test_json_report_keeps_raw_source_health_and_run_error_fields() -> None:
    report = DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF),
        source_health=[
            SourceHealthReport(
                source_name="WWD",
                source_type="rss",
                consecutive_failures=3,
                last_error_message=LONG_ERROR,
            )
        ],
        recent_runs=[
            CollectorRunReport(
                source_name="WWD",
                source_type="rss",
                status="failed",
                started_at=AS_OF - timedelta(minutes=5),
                items_seen=0,
                items_stored=0,
                error_message=MULTILINE_ERROR,
            )
        ],
    )

    parsed = json.loads(render_json_report(report))

    assert parsed["source_health"][0]["last_error_message"] == LONG_ERROR
    assert parsed["recent_runs"][0]["error_message"] == MULTILINE_ERROR
```

- [ ] **Step 5: Run RED tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_reports.py::test_markdown_source_health_collapses_and_truncates_long_error \
  tests/test_reports.py::test_markdown_source_health_collapses_multiline_error \
  tests/test_reports.py::test_markdown_source_health_without_error_keeps_no_error_fallback \
  tests/test_reports.py::test_markdown_recent_runs_collapses_and_truncates_long_error \
  tests/test_reports.py::test_markdown_recent_runs_collapses_multiline_error \
  tests/test_reports.py::test_markdown_recent_runs_omits_error_segment_when_snippet_is_none \
  tests/test_reports.py::test_json_report_keeps_raw_source_health_and_run_error_fields \
  -q
```

Expected: four Task 1 tests are RED at `e8567fc` because the renderers
currently interpolate raw error strings:

- `test_markdown_source_health_collapses_and_truncates_long_error` (raw
  `LONG_ERROR` keeps `TAIL_MARKER` and does not end with `...`).
- `test_markdown_source_health_collapses_multiline_error` (raw `MULTILINE_ERROR`
  keeps newlines and double spaces, so the collapsed substring is absent).
- `test_markdown_recent_runs_collapses_and_truncates_long_error` (raw
  `LONG_ERROR` appended, keeps `TAIL_MARKER` and does not end with `...`).
- `test_markdown_recent_runs_collapses_multiline_error` (raw `MULTILINE_ERROR`
  appended, keeps newlines).
- `test_markdown_recent_runs_omits_error_segment_when_snippet_is_none` (RED
  overall): its Fashionista `error_message=None` sub-case already passes today,
  but its WWD `error_message=WHITESPACE_ONLY_ERROR` sub-case fails because the
  current `if run.error_message:` guard is truthy for whitespace-only strings
  and appends `; <raw whitespace>`, so `wwd_line.endswith("9/9 stored")` and
  `";" not in wwd_line` both fail.

The remaining two Task 1 tests are GREEN at `e8567fc` and pin the contract
before the implementation edit:

- `test_markdown_source_health_without_error_keeps_no_error_fallback` (raw
  `None` already yields `'no error'` via the existing `or` fallback).
- `test_json_report_keeps_raw_source_health_and_run_error_fields` (no validator
  on `last_error_message`/`error_message`, so `model_dump_json` already emits
  raw values).

## Task 2: GREEN Markdown Render Implementation

**Files:**

- Modify: `src/fashion_radar/reports.py`

- [ ] **Step 1: Apply `report_safe_snippet` in `_render_source_health_line`**

Replace the body of `_render_source_health_line(...)` at
`src/fashion_radar/reports.py:746-753` with:

```python
def _render_source_health_line(source: SourceHealthReport) -> str:
    unhealthy_until = source.unhealthy_until.isoformat() if source.unhealthy_until else "n/a"
    safe_error = report_safe_snippet(source.last_error_message)
    return (
        f"- {source.source_name} ({source.source_type}): "
        f"{source.consecutive_failures} consecutive failures; "
        f"unhealthy until {unhealthy_until}; "
        f"{safe_error or 'no error'}"
    )
```

`safe_error or 'no error'` preserves the existing Markdown fallback when the
snippet is `None` (raw `None` or empty/whitespace-only input).

- [ ] **Step 2: Apply `report_safe_snippet` in `_render_recent_runs`**

Replace the body of `_render_recent_runs(...)` at
`src/fashion_radar/reports.py:756-766` with:

```python
def _render_recent_runs(recent_runs: list[CollectorRunReport]) -> str:
    if not recent_runs:
        return "No recent collector runs recorded."
    lines: list[str] = []
    for run in recent_runs:
        line = (
            f"- {run.started_at.isoformat()} {run.source_name} ({run.source_type}) "
            f"{run.status}: {run.items_stored}/{run.items_seen} stored"
        )
        safe_error = report_safe_snippet(run.error_message)
        if safe_error:
            line += f"; {safe_error}"
        lines.append(line)
    return "\n".join(lines)
```

Guarding on `if safe_error:` (rather than `if run.error_message:`) ensures a
whitespace-only error message does not append an empty `;` segment, and matches
the Stage 210 scope note: if the snippet returns `None`, do not render an empty
error detail.

- [ ] **Step 3: Run GREEN focused tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_reports.py::test_markdown_source_health_collapses_and_truncates_long_error \
  tests/test_reports.py::test_markdown_source_health_collapses_multiline_error \
  tests/test_reports.py::test_markdown_source_health_without_error_keeps_no_error_fallback \
  tests/test_reports.py::test_markdown_recent_runs_collapses_and_truncates_long_error \
  tests/test_reports.py::test_markdown_recent_runs_collapses_multiline_error \
  tests/test_reports.py::test_markdown_recent_runs_omits_error_segment_when_snippet_is_none \
  tests/test_reports.py::test_json_report_keeps_raw_source_health_and_run_error_fields \
  -q
```

Expected: all selected tests pass.

## Task 3: Docs And Changelog

**Files:**

- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/cli-reference.md`
- Modify: `tests/test_cli_docs.py`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Extend README generated-reports bullet**

In `README.md`, the generated-reports bullet currently reads (lines 61-65):

```markdown
- Generates daily Markdown and JSON reports with source attribution plus a
  Daily Brief Heat Narrative for local observed tracked signals, candidate
  phrases that need review, and source caveats from configured sources and
  imported local signals. It provides no demand proof and no platform coverage
  verification.
```

Append one sentence immediately after `verification.` on line 65 so the bullet
becomes:

```markdown
- Generates daily Markdown and JSON reports with source attribution plus a
  Daily Brief Heat Narrative for local observed tracked signals, candidate
  phrases that need review, and source caveats from configured sources and
  imported local signals. It provides no demand proof and no platform coverage
  verification. The Markdown Source Health and Recent Collector Runs sections
  collapse whitespace and truncate long error messages to report-safe snippets;
  JSON error fields stay raw.
```

- [ ] **Step 2: Extend architecture Reports bullet**

In `docs/architecture.md`, the Reports bullet currently reads (lines 218-223):

```markdown
- **Reports:** Markdown and JSON daily reports rendered from packaged
  templates. The Daily Brief Heat Narrative is derived from report-safe rows
  for configured sources and imported local signals. It summarizes local
  observed tracked signals, candidate phrases, and source caveats as report
  content that needs review, and can include candidate score-component cues for
  mentions, growth, and source diversity. It does not collect, search, scrape,
```

Insert one sentence immediately before `It does not collect, search, scrape,`
(line 223) so the bullet reads:

```markdown
- **Reports:** Markdown and JSON daily reports rendered from packaged
  templates. The Daily Brief Heat Narrative is derived from report-safe rows
  for configured sources and imported local signals. It summarizes local
  observed tracked signals, candidate phrases, and source caveats as report
  content that needs review, and can include candidate score-component cues for
  mentions, growth, and source diversity. The Markdown Source Health and
  Recent Collector Runs sections collapse whitespace and truncate long error
  messages to report-safe snippets; JSON error fields stay raw. It does not
  collect, search, scrape,
```

- [ ] **Step 3: Extend CLI reference `report` bullet**

In `docs/cli-reference.md`, the `report` bullet currently reads (lines 74-78):

```markdown
- `report`: generate Markdown and JSON reports, including a Daily Brief Heat
  Narrative for local observed tracked signals, candidate phrases that need
  review, candidate score-component cues for mentions, growth, and source
  diversity, and source caveats from configured sources and imported local
  signals. It provides no demand proof and no platform coverage verification.
```

Append one sentence immediately after `verification.` on line 78 so the bullet
becomes:

```markdown
- `report`: generate Markdown and JSON reports, including a Daily Brief Heat
  Narrative for local observed tracked signals, candidate phrases that need
  review, candidate score-component cues for mentions, growth, and source
  diversity, and source caveats from configured sources and imported local
  signals. It provides no demand proof and no platform coverage verification.
  The Markdown Source Health and Recent Collector Runs sections collapse
  whitespace and truncate long error messages to report-safe snippets; JSON
  error fields stay raw.
```

- [ ] **Step 4: Add a focused docs guard**

Do not extend `DAILY_BRIEF_REQUIRED_PHRASES`; that tuple is asserted against
every file in `DAILY_BRIEF_DOCS` and would force unrelated docs to mention this
narrow Stage 210 snippet-hygiene wording. Instead, add a focused docs test in
`tests/test_cli_docs.py` immediately after
`test_daily_brief_docs_describe_candidate_score_component_cues`:

```python
def test_report_docs_describe_markdown_error_snippet_hygiene() -> None:
    for path in (README, CLI_REFERENCE, ARCHITECTURE_DOC):
        normalized = _normalized_doc_text(path).casefold()
        assert "source health" in normalized
        assert "recent collector runs" in normalized
        assert "report-safe snippets" in normalized
        assert "collapse whitespace and truncate" in normalized
        assert "json error fields stay raw" in normalized
```

Use the exact wording from Steps 1-3 in README/CLI/architecture to avoid
brittle mismatches.

- [ ] **Step 5: Add changelog entry**

Add this entry under `[Unreleased] -> ### Added` (immediately above the
existing Stage 209 entry, newest-first):

```markdown
- Stage 210 collapses whitespace and truncates long collector and source error
  messages to report-safe snippets in the Markdown Source Health and Recent
  Collector Runs sections, without changing JSON report error fields, report
  model contracts, scoring, ranking, source acquisition, dashboard behavior,
  social or platform connectors, scraping, dependency files, or
  compliance-review behavior.
```

- [ ] **Step 6: Run docs-focused tests and lint**

Run:

```bash
uv --no-config run --frozen pytest tests/test_reports.py tests/test_cli_docs.py -q
uv --no-config run --frozen ruff check src/fashion_radar/reports.py tests/test_reports.py tests/test_cli_docs.py README.md docs/architecture.md docs/cli-reference.md CHANGELOG.md
uv --no-config run --frozen ruff format --check src/fashion_radar/reports.py tests/test_reports.py tests/test_cli_docs.py
```

Expected: selected tests and lint/format checks pass.

## Task 4: Code Review And Fixes

**Files:**

- Add: `docs/reviews/opencode-stage-210-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-210-code-review.md`
- Add if needed: `docs/reviews/opencode-stage-210-code-rereview-prompt.md`
- Add if needed: `docs/reviews/opencode-stage-210-code-rereview.md`

- [ ] **Step 1: Create the code-review prompt**

Create `docs/reviews/opencode-stage-210-code-review-prompt.md` describing the
Stage 210 goal, baseline SHA (`git rev-parse HEAD` before Task 1), changed
files, RED/GREEN evidence (paste the focused pytest summary), the exact
`_render_source_health_line` and `_render_recent_runs` diffs, and review focus:
Markdown-only snippet application, JSON/raw-field contract preservation,
`no error` fallback preservation, whitespace-only recent-runs guard, no model
or dependency changes.

- [ ] **Step 2: Run OpenCode code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-210-code-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-210-code-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important findings. Fix Critical/Important findings
and run a rereview before Task 5.

## Task 5: Release Verification, Release Review, Commit, Push

**Files:**

- Add: `docs/reviews/opencode-stage-210-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-210-release-review.md`
- Add if needed: `docs/reviews/opencode-stage-210-release-rereview-prompt.md`
- Add if needed: `docs/reviews/opencode-stage-210-release-rereview.md`

- [ ] **Step 1: Run full verification**

Run:

```bash
uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
git diff --exit-code -- uv.lock pyproject.toml
git diff --check
```

Expected: every command exits 0, with no lockfile or dependency changes.

- [ ] **Step 2: Create the release-review prompt**

Create `docs/reviews/opencode-stage-210-release-review-prompt.md` summarizing
the Stage 210 changes, full verification evidence, review artifacts, and
release-hygiene scope (Markdown-only render change, no JSON/model/dependency
impact).

- [ ] **Step 3: Run OpenCode release review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-210-release-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-210-release-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important findings. Fix Critical/Important findings
and run a rereview before committing.

- [ ] **Step 4: Stage and inspect the release diff**

Run:

```bash
git add CHANGELOG.md README.md docs/architecture.md docs/cli-reference.md \
  docs/reviews/opencode-stage-210-*.md \
  docs/superpowers/plans/2026-06-29-stage-210-markdown-report-snippet-hygiene-plan.md \
  src/fashion_radar/reports.py tests/test_reports.py tests/test_cli_docs.py
git diff --cached --check
git diff --cached | rg -n "ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|BEGIN (RSA|OPENSSH|PRIVATE) KEY|xox[baprs]-[A-Za-z0-9-]{20,}|sk-[A-Za-z0-9]{20,}" || true
```

Expected: whitespace check exits 0 and the secret scan returns no matches.

- [ ] **Step 5: Commit and push**

Run:

```bash
git commit -m "Stage 210: collapse markdown source health and run errors to report-safe snippets"
git push origin main
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
```

Expected: local `main` and `origin/main` point to the same new Stage 210
commit, with a clean working tree.

## Self-Review Checklist

- This plan closes a Markdown report-hygiene gap in the local
  `collect -> match -> report` pipeline.
- The plan reuses the existing `report_safe_snippet(...)` helper and adds no
  new helper, no new constant, and no new dependency.
- The plan is Markdown-render-only and does not modify `SourceHealthReport`,
  `CollectorRunReport`, `DailyReport`, `DailyBrief`, `DailyBriefItem`,
  `report_safe_snippet`, or `REPORT_SNIPPET_MAX_CHARS`.
- The plan preserves the JSON contract: `last_error_message` and
  `error_message` stay raw in `render_json_report(...)`.
- The plan preserves the existing Markdown `no error` fallback for source
  health and omits the `; <error>` segment for collector runs whose snippet is
  `None` (including whitespace-only inputs).
- The plan avoids source acquisition, social/platform connectors, scraping,
  browser automation, cookies/tokens, dependency, lockfile, DB schema,
  dashboard, scoring, ranking, candidate extraction, and compliance-review
  product work.
- The plan includes RED tests before production-code changes, including a
  contract test that pins raw JSON error fields.
- The plan includes OpenCode plan/code/release review gates.
- The plan includes full release verification and secret-scan hygiene before
  push.
- The plan does not touch `pyproject.toml` or `uv.lock`.

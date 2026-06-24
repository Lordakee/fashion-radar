# Stage 192 Daily Brief Caveat Polish And Review Status Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Polish the Stage 191 Daily Brief caveat output and update stale full-project review follow-up status before starting the next product node.

**Architecture:** Keep the change inside the existing report builder/renderer and review documentation. Use the existing `report_safe_snippet(...)` helper for Daily Brief error fragments, de-duplicate report-derived source caveats by source key, and update only the follow-up status of the historical full-project review. Do not change public report model shapes, CLI commands, trend/heat contracts, source acquisition, or social/community connector surfaces.

**Tech Stack:** Python 3.11, Pydantic report models, pytest, ruff, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`, Codex subagent cross-check with reasoning effort `xhigh`.

---

## Files

- Modify: `src/fashion_radar/reports.py`
- Modify: `tests/test_reports.py`
- Modify: `tests/test_review_protocol_docs.py`
- Modify: `docs/reviews/opencode-full-project-review.md`
- Modify: `CHANGELOG.md`
- Add: `docs/superpowers/specs/2026-06-24-stage-192-daily-brief-caveat-polish-review-status-design.md`
- Add: `docs/superpowers/plans/2026-06-24-stage-192-daily-brief-caveat-polish-review-status-plan.md`
- Add after plan review: `docs/reviews/opencode-stage-192-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-192-plan-review.md`
- Add after plan fixes if needed: `docs/reviews/opencode-stage-192-plan-rereview-prompt.md`
- Add after plan fixes if needed: `docs/reviews/opencode-stage-192-plan-rereview.md`
- Add after implementation: `docs/reviews/opencode-stage-192-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-192-code-review.md`
- Add after code fixes if needed: `docs/reviews/opencode-stage-192-code-rereview-prompt.md`
- Add after code fixes if needed: `docs/reviews/opencode-stage-192-code-rereview.md`
- Add before commit: `docs/reviews/opencode-stage-192-release-review-prompt.md`
- Add before commit: `docs/reviews/opencode-stage-192-release-review.md`
- Add after release fixes if needed: `docs/reviews/opencode-stage-192-release-rereview-prompt.md`
- Add after release fixes if needed: `docs/reviews/opencode-stage-192-release-rereview.md`

## Task 1: Daily Brief Caveat Output Polish

**Files:**

- Modify: `tests/test_reports.py`
- Modify: `src/fashion_radar/reports.py`

- [ ] **Step 1: Write RED tests for capped caveat errors, de-duplication, and per-section empty fallback**

Add `CollectorRunReport` and `SourceHealthReport` to the existing
`tests/test_reports.py` import from `fashion_radar.models.report`:

```python
from fashion_radar.models.report import (
    REPORT_SNIPPET_MAX_CHARS,
    CandidateReport,
    CollectorRunReport,
    DailyBrief,
    DailyBriefItem,
    DailyBriefSection,
    DailyReport,
    EntityReport,
    ReportMetadata,
    RepresentativeItem,
    SourceHealthReport,
)
```

Add `build_daily_brief` to the existing import from `fashion_radar.reports`:

```python
from fashion_radar.reports import (
    build_daily_brief,
    build_daily_report,
    render_json_report,
    render_markdown_report,
)
```

Add this focused test after
`test_daily_report_includes_stable_daily_brief_json_shape`:

```python
def test_daily_brief_caps_source_caveat_errors_and_deduplicates_recent_runs() -> None:
    long_error = "Lead error. " + ("detail " * 120) + "TAIL_MARKER"

    brief = build_daily_brief(
        entities=[],
        candidates=[],
        source_health=[
            SourceHealthReport(
                source_name="Vogue Business",
                source_type="rss",
                consecutive_failures=2,
                last_error_message=long_error,
            )
        ],
        recent_runs=[
            CollectorRunReport(
                source_name="vogue business",
                source_type="RSS",
                status="failed",
                started_at=AS_OF,
                finished_at=AS_OF,
                items_seen=0,
                items_stored=0,
                error_message=long_error,
                error_type="ReadTimeout",
            ),
            CollectorRunReport(
                source_name="Fashionista",
                source_type="rss",
                status="failed",
                started_at=AS_OF,
                finished_at=AS_OF,
                items_seen=0,
                items_stored=0,
                error_message=long_error,
                error_type="ReadTimeout",
            ),
        ],
        limit_per_section=3,
    )

    source_items = brief.sections[2].items

    assert [item.title for item in source_items] == ["Vogue Business", "Fashionista"]
    assert source_items[0].reason_codes == [
        "source_health_failure",
        "source_last_error_present",
    ]
    assert source_items[1].reason_codes == ["recent_collection_failed"]
    assert all("Lead error." in item.summary for item in source_items)
    assert all("Last error:" in item.summary for item in source_items)
    assert all("TAIL_MARKER" not in item.summary for item in source_items)
    assert all("..." in item.summary for item in source_items)
```

Add this focused Markdown rendering test after
`test_markdown_report_renders_daily_brief_before_top_signals`:

```python
def test_daily_brief_markdown_uses_section_empty_fallback_when_partially_empty() -> None:
    report = DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF, item_count=1),
        brief=DailyBrief(
            summary=(
                "Local observed brief from configured sources and imported local signals: "
                "1 tracked signal, 0 candidate signals needing review, 0 source caveats. "
                "It provides no demand proof and no platform coverage verification."
            ),
            sections=[
                DailyBriefSection(
                    name="tracked_signals",
                    title="Tracked Signals To Review",
                    items=[
                        DailyBriefItem(
                            kind="tracked_entity",
                            title="The Row",
                            summary="Local observed tracked brand signal.",
                            reason_codes=["current_mentions_observed"],
                            current_mentions=1,
                        )
                    ],
                ),
                DailyBriefSection(
                    name="candidate_signals",
                    title="Candidate Signals Needing Review",
                ),
                DailyBriefSection(name="source_caveats", title="Source Caveats"),
            ],
        ),
    )

    markdown = render_markdown_report(report)

    assert "- No items in this section." in markdown
    assert "- No daily brief items available." not in markdown
```

- [ ] **Step 2: Run focused tests to verify RED**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_reports.py::test_daily_brief_caps_source_caveat_errors_and_deduplicates_recent_runs \
  tests/test_reports.py::test_daily_brief_markdown_uses_section_empty_fallback_when_partially_empty \
  -q
```

Expected: both tests fail. The first fails because the duplicate
`Vogue Business` recent-run caveat is still present and the long tail marker is
not capped out of summaries. The second fails because empty sections still use
`- No daily brief items available.`.

- [ ] **Step 3: Implement minimal report-layer changes**

In `src/fashion_radar/reports.py`, add `report_safe_snippet` to the existing
`fashion_radar.models.report` import:

```python
from fashion_radar.models.report import (
    CandidateReport,
    CollectorRunReport,
    DailyBrief,
    DailyBriefItem,
    DailyBriefSection,
    DailyReport,
    EntityReport,
    ReportMetadata,
    RepresentativeItem,
    SourceHealthReport,
    report_safe_snippet,
)
```

Update `_render_daily_brief(...)` so per-section empty rows use a distinct
fallback while the all-empty brief remains unchanged:

```python
def _render_daily_brief(brief: DailyBrief) -> str:
    lines = [brief.summary]
    any_items = False
    for section in brief.sections:
        lines.extend(["", f"### {section.title}"])
        if not section.items:
            lines.append("- No items in this section.")
            continue
        any_items = True
        for item in section.items:
            reasons = ", ".join(item.reason_codes) if item.reason_codes else "none"
            lines.append(
                f"- {_table_cell(item.title)}: {_table_cell(item.summary)} "
                f"Reasons: {_table_cell(reasons)}."
            )
    if not any_items:
        return "\n".join([brief.summary, "", "- No daily brief items available."])
    return "\n".join(lines)
```

Update `_source_caveat_items(...)` to skip failed recent runs whose source is
already represented by a source-health caveat:

```python
def _source_caveat_items(
    *,
    source_health: list[SourceHealthReport],
    recent_runs: list[CollectorRunReport],
    limit: int,
) -> list[DailyBriefItem]:
    if limit == 0:
        return []

    health_sources = [
        source
        for source in sorted(
            source_health,
            key=lambda row: (-row.consecutive_failures, row.source_name, row.source_type),
        )
        if _source_health_needs_caveat(source)
    ]
    health_items = [_brief_item_for_source_health(source) for source in health_sources]
    represented_health_keys = {
        _source_caveat_key(source.source_name, source.source_type) for source in health_sources
    }
    remaining = limit - len(health_items)
    if remaining <= 0:
        return health_items[:limit]

    run_items = [
        _brief_item_for_recent_run(run)
        for run in recent_runs
        if run.status.casefold() == "failed"
        and _source_caveat_key(run.source_name, run.source_type) not in represented_health_keys
    ]
    return (health_items + run_items[:remaining])[:limit]
```

Add a small key helper near `_source_health_needs_caveat(...)`:

```python
def _source_caveat_key(source_name: str, source_type: str) -> tuple[str, str]:
    return (source_name.casefold(), source_type.casefold())
```

Update `_brief_item_for_source_health(...)` to cap the error fragment:

```python
    error_message = report_safe_snippet(source.last_error_message)
    if error_message:
        summary = f"{summary} Last error: {error_message}."
```

Update `_brief_item_for_recent_run(...)` to cap the error fragment:

```python
def _brief_item_for_recent_run(run: CollectorRunReport) -> DailyBriefItem:
    error_message = report_safe_snippet(run.error_message)
    return DailyBriefItem(
        kind="collector_run_caveat",
        title=run.source_name,
        summary=(
            f"Local source caveat: {run.source_name} recent collection failed with "
            f"{run.items_stored}/{run.items_seen} stored."
            + (f" Last error: {error_message}." if error_message else "")
        ),
        reason_codes=["recent_collection_failed"],
    )
```

- [ ] **Step 4: Run focused tests to verify GREEN**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_reports.py::test_daily_brief_caps_source_caveat_errors_and_deduplicates_recent_runs \
  tests/test_reports.py::test_daily_brief_markdown_uses_section_empty_fallback_when_partially_empty \
  tests/test_reports.py::test_empty_database_produces_useful_empty_report \
  -q
```

Expected: all selected tests pass. The empty-report test proves the global
fallback did not change.

## Task 2: Full-Project Review Follow-Up Status

**Files:**

- Modify: `tests/test_review_protocol_docs.py`
- Modify: `docs/reviews/opencode-full-project-review.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Write RED docs test for current follow-up status**

In `tests/test_review_protocol_docs.py`, add:

```python
FULL_PROJECT_REVIEW = ROOT / "docs" / "reviews" / "opencode-full-project-review.md"
```

Add this test after `test_review_protocol_docs_document_capture_hygiene`:

```python
def test_full_project_review_follow_up_status_tracks_completed_stages() -> None:
    text = _read(FULL_PROJECT_REVIEW)
    status = _section(text, "Current Follow-Up Status")
    normalized = _normalized_text(status).casefold()

    for phrase in (
        "Stage 188 fixed the proxy-sensitive tests and redirected roadmap docs.",
        "Stage 189 fixed review-capture hygiene gaps",
        "Stage 190 added source-liveness diagnostics for configured public sources.",
        "Stage 191 added the Daily Brief Heat Narrative",
        "source coverage",
        "matching quality",
        "trend/heat explanation",
    ):
        assert phrase.casefold() in normalized

    assert "is intended to" not in normalized
    assert "next product node should implement source-liveness diagnostics" not in normalized
```

- [ ] **Step 2: Run docs test to verify RED**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_review_protocol_docs.py::test_full_project_review_follow_up_status_tracks_completed_stages \
  -q
```

Expected: fail because the current follow-up status still says Stage 189 is
intended work and still names source-liveness as the next product node.

- [ ] **Step 3: Update follow-up status and changelog**

Replace the `## Current Follow-Up Status` section in
`docs/reviews/opencode-full-project-review.md` with:

```markdown
## Current Follow-Up Status

- Stage 188 fixed the proxy-sensitive tests and redirected roadmap docs.
- Stage 189 fixed review-capture hygiene gaps exposed by this review record and
  the Stage 188 review chain.
- Stage 190 added source-liveness diagnostics for configured public sources.
- Stage 191 added the Daily Brief Heat Narrative to generated daily reports.
- The next product work should use source-liveness evidence to expand source
  coverage, improve deterministic matching quality, and add a local trend/heat
  explanation layer without claiming demand proof or platform coverage
  verification.
```

Add this Stage 192 bullet to the existing `### Fixed` subsection in
`CHANGELOG.md`:

```markdown
- Stage 192 polish for generated report Daily Brief source caveats, including
  capped local error fragments, duplicate source-caveat suppression, clearer
  empty-section Markdown fallback, and updated full-project review follow-up
  status.
```

- [ ] **Step 4: Run docs test to verify GREEN**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_review_protocol_docs.py::test_full_project_review_follow_up_status_tracks_completed_stages \
  -q
```

Expected: pass.

## Task 3: Stage Review And Release Gate

**Files:**

- Add: `docs/reviews/opencode-stage-192-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-192-code-review.md`
- Add if needed: `docs/reviews/opencode-stage-192-code-rereview-prompt.md`
- Add if needed: `docs/reviews/opencode-stage-192-code-rereview.md`
- Add: `docs/reviews/opencode-stage-192-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-192-release-review.md`
- Add if needed: `docs/reviews/opencode-stage-192-release-rereview-prompt.md`
- Add if needed: `docs/reviews/opencode-stage-192-release-rereview.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_reports.py::test_daily_brief_caps_source_caveat_errors_and_deduplicates_recent_runs \
  tests/test_reports.py::test_daily_brief_markdown_uses_section_empty_fallback_when_partially_empty \
  tests/test_reports.py::test_empty_database_produces_useful_empty_report \
  tests/test_review_protocol_docs.py::test_full_project_review_follow_up_status_tracks_completed_stages \
  -q
```

Expected: pass.

- [ ] **Step 2: Run broader verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_reports.py tests/test_review_protocol_docs.py -q
uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
git diff --check
```

Expected: every command exits 0.

- [ ] **Step 3: Request opencode code review**

Create `docs/reviews/opencode-stage-192-code-review-prompt.md`:

```markdown
Review Stage 192 code changes in /home/ubuntu/fashion-radar.

Scope:
- Daily Brief source caveat error fragments are capped with the existing
  report-safe snippet policy.
- Daily Brief source-caveats de-duplicate failed recent-run caveats when a
  source-health caveat already represents the same source.
- Per-section empty Markdown fallback is clearer while the global all-empty
  fallback remains unchanged.
- docs/reviews/opencode-full-project-review.md follow-up status is updated to
  reflect completed Stages 188-191.

Verify:
1. No public report model shape changes beyond content polishing.
2. No new CLI command, source acquisition, platform/social connector,
   monitoring, scheduling, demand proof, coverage verification, compliance
   review feature, LLM summarization, or trend/heat/dashboard contract change.
3. Tests cover the old failure modes.
4. Review artifacts are clean and coherent.

Return Critical, Important, Minor, and Verdict.
```

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-192-code-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-192-code-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important findings. If Critical or Important findings
appear, fix them and record a code rereview.

- [ ] **Step 4: Request opencode release review**

Create `docs/reviews/opencode-stage-192-release-review-prompt.md`:

```markdown
Review Stage 192 release readiness in /home/ubuntu/fashion-radar.

Check:
- git diff and git status for Stage 192 files only.
- The Stage 192 spec, plan, plan review, code review, and release review
  artifacts are present and clean.
- Verification evidence is sufficient for commit and push.
- No secrets, tokens, cookies, local databases, generated reports, build
  artifacts, or CodeGraph DB files are staged.
- The change preserves project boundaries: no new source acquisition,
  scraping, browser automation, platform APIs, monitoring, scheduling,
  demand proof, coverage verification, compliance-review product feature, LLM
  summarization, or trend/heat/dashboard contract mutation.

Return Critical, Important, Minor, and Verdict. State whether the stage is
ready to commit and push.
```

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-192-release-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-192-release-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important findings. If Critical or Important findings
appear, fix them and record a release rereview.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short
git add \
  src/fashion_radar/reports.py \
  tests/test_reports.py \
  tests/test_review_protocol_docs.py \
  docs/reviews/opencode-full-project-review.md \
  CHANGELOG.md \
  docs/superpowers/specs/2026-06-24-stage-192-daily-brief-caveat-polish-review-status-design.md \
  docs/superpowers/plans/2026-06-24-stage-192-daily-brief-caveat-polish-review-status-plan.md \
  docs/reviews/opencode-stage-192-plan-review-prompt.md \
  docs/reviews/opencode-stage-192-plan-review.md \
  docs/reviews/opencode-stage-192-code-review-prompt.md \
  docs/reviews/opencode-stage-192-code-review.md \
  docs/reviews/opencode-stage-192-release-review-prompt.md \
  docs/reviews/opencode-stage-192-release-review.md
git commit -m "fix: polish daily brief caveats"
git push origin main
```

If rereview artifacts are created, add them to the same commit manifest before
commit.

## Self-Review

- Spec coverage: Tasks cover Daily Brief error capping, de-duplication,
  per-section Markdown fallback, full-project review follow-up status, changelog,
  opencode reviews, verification, commit, and push.
- Placeholder scan: No `TBD`, `TODO`, or "implement later" placeholders.
- Boundary check: No task adds a CLI command, connector, source acquisition,
  platform search, demand proof, coverage verification, compliance-review
  feature, LLM summarization, or trend/heat/dashboard contract mutation.

# Stage 36 Report And Dashboard Quality Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make report output safer and more transparent, and make the local dashboard show recent signals plus all entity-type mention tabs.

**Architecture:** Put snippet safety at the `RepresentativeItem` model boundary so entity and candidate reports inherit it. Copy existing score components from `EntityHeatMetric` into `EntityReport` and render them. Add one dashboard read query for recent local signals and drive entity mention tabs from `EntityType`.

**Tech Stack:** Python, Pydantic v2 validators, SQLAlchemy Core, Streamlit, pytest, ruff, uv. No dependency, schema, source-collection, connector, scraping, or platform automation changes.

---

## Boundaries

In scope:

- `src/fashion_radar/models/report.py`
- `src/fashion_radar/reports.py`
- `src/fashion_radar/dashboard/queries.py`
- `src/fashion_radar/dashboard/app.py`
- `tests/test_reports.py`
- `tests/test_workflows.py`
- `tests/test_dashboard.py`
- `docs/dashboard.md`
- Stage 36 plan/review artifacts.

Out of scope:

- `src/fashion_radar/db/schema.py` and database migrations.
- Manual signal `platform` persistence.
- New source connectors, social-platform functionality, scraping, crawling,
  browser automation, login/cookie flows, account automation, proxy pools,
  CAPTCHA bypass, source acquisition, source ranking, demand proof, watchers,
  schedulers, or external API integrations.
- Dependency or `uv.lock` changes.

## Task -1: Claude Code Plan Review Gate

**Files:**

- Add: `docs/reviews/claude-code-stage-36-plan-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-36-plan-review.md`

- [ ] **Step 1: Request pre-execution plan review**

Create `docs/reviews/claude-code-stage-36-plan-review-prompt.md` with:

```markdown
# Claude Code Stage 36 Plan Review Prompt

You are reviewing the Stage 36 report/dashboard quality plan for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Make report output safer and more transparent, and make the local dashboard show
recent signals plus all entity-type mention tabs.

## Proposed Technical Approach

- Add a deterministic 500-character ASCII-ellipsis report snippet cap at the
  `RepresentativeItem.summary` model boundary.
- Add entity score component fields to `EntityReport`, populate them from
  `EntityHeatMetric`, and render them in Markdown.
- Add a local `recent_signals(data_dir, limit=20)` dashboard query that returns
  only local public/review fields and capped summaries.
- Render recent signals in the Daily Brief tab.
- Drive dashboard mention tabs from `EntityType` so brand, designer, celebrity,
  product, category, and trend are all covered.
- Keep Stage 36 local product-quality only: no schema migration, manual
  platform persistence, dependencies, `uv.lock`, source connectors, scraping,
  crawling, browser automation, login/cookie flows, account automation, proxy
  pools, CAPTCHA bypass, source acquisition, source ranking, demand proof,
  watchers, schedulers, or external platform API integrations.

## Files To Review

- `docs/superpowers/specs/2026-06-14-stage-36-report-dashboard-quality-design.md`
- `docs/superpowers/plans/2026-06-14-stage-36-report-dashboard-quality-plan.md`

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 36 REPORT DASHBOARD QUALITY
```
```

Run:

```bash
claude --effort max --permission-mode plan --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-36-plan-review-prompt.md)" \
  > docs/reviews/claude-code-stage-36-plan-review.md
```

Expected: approval phrase appears, or the plan is revised and rereviewed before
Task 1.

## Task 1: Report-Safe Snippet Tests

**Files:**

- Modify: `tests/test_reports.py`
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Add model/report snippet regression tests**

Add tests to `tests/test_reports.py` that assert:

```python
from fashion_radar.models.report import REPORT_SNIPPET_MAX_CHARS, RepresentativeItem


def test_representative_item_summary_is_report_safe_snippet() -> None:
    summary = "Lead text. " + ("detail " * 120) + "TAIL_MARKER"

    item = RepresentativeItem(
        source_name="Vogue Business",
        source_url="https://example.com/signal",
        published_at="2026-06-14T08:00:00Z",
        title="The Row signal",
        summary=summary,
    )

    assert item.summary is not None
    assert len(item.summary) <= REPORT_SNIPPET_MAX_CHARS
    assert item.summary.endswith("...")
    assert "TAIL_MARKER" not in item.summary
```

Also add one report-rendering test that builds a `DailyReport` containing both
an `EntityReport` and `CandidateReport` with long representative summaries,
then asserts `render_json_report()` and `render_markdown_report()` omit
`TAIL_MARKER` and contain capped summaries.

- [ ] **Step 2: Add workflow-file snippet regression**

Add a focused `tests/test_workflows.py` regression for `write_daily_report_files`
or the closest existing daily-report file writer fixture. It should create a
long RSS/manual-style summary and assert the written `.json` and `.md` reports
do not contain `TAIL_MARKER`.

- [ ] **Step 3: Verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_reports.py tests/test_workflows.py -q -k "snippet or report_safe"
```

Expected before implementation: at least one failure because the summary is not
capped.

## Task 2: Report-Safe Snippet Implementation And Score Components

**Files:**

- Modify: `src/fashion_radar/models/report.py`
- Modify: `src/fashion_radar/reports.py`

- [ ] **Step 1: Add snippet helper and validator**

In `src/fashion_radar/models/report.py`, add:

```python
REPORT_SNIPPET_MAX_CHARS = 500


def report_safe_snippet(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = " ".join(value.split())
    if not normalized:
        return None
    if len(normalized) <= REPORT_SNIPPET_MAX_CHARS:
        return normalized
    return normalized[: REPORT_SNIPPET_MAX_CHARS - 3].rstrip() + "..."
```

Add a `summary` validator to `RepresentativeItem`:

```python
@field_validator("summary", mode="before")
@classmethod
def normalize_summary(cls, value: str | None) -> str | None:
    return report_safe_snippet(value)
```

- [ ] **Step 2: Add entity score component fields**

In `EntityReport`, add:

```python
weighted_mention_component: float = 0.0
growth_component: float = 0.0
source_diversity_component: float = 0.0
high_weight_component: float = 0.0
```

In `_entity_report()`, pass the matching values from `EntityHeatMetric`.

- [ ] **Step 3: Render score components in Markdown**

In `_render_entity_sections()`, add a line after heat score:

```python
(
    "- Score components: "
    f"mentions {entity.weighted_mention_component:.2f}; "
    f"growth {entity.growth_component:.2f}; "
    f"sources {entity.source_diversity_component:.2f}; "
    f"high-weight {entity.high_weight_component:.2f}"
)
```

- [ ] **Step 4: Verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_reports.py tests/test_workflows.py -q -k "snippet or score_component or report_safe"
```

Expected: the new tests pass.

## Task 3: Dashboard Recent Signals And Entity Tabs Tests

**Files:**

- Modify: `tests/test_dashboard.py`

- [ ] **Step 1: Add `recent_signals` query tests**

Add tests that:

- assert `recent_signals(missing_data_dir) == []` and does not create the data
  directory;
- create two items with different `collected_at` values and assert newest rows
  appear first;
- assert returned rows include `collected_at`, `published_at`, `source_name`,
  `source_type`, `title`, `url`, and capped `summary`;
- assert long summaries omit `TAIL_MARKER`.

- [ ] **Step 2: Add dashboard tab coverage test**

Import `DASHBOARD_TAB_LABELS` and `EntityType`, then assert the labels include:

```python
expected = {f"{entity_type.value.title()} Mentions" for entity_type in EntityType}
assert expected <= set(DASHBOARD_TAB_LABELS)
```

- [ ] **Step 3: Verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_dashboard.py -q -k "recent_signals or tab"
```

Expected before implementation: failures because `recent_signals` does not
exist and designer/category/trend tabs are missing.

## Task 4: Dashboard Recent Signals And Entity Tabs Implementation

**Files:**

- Modify: `src/fashion_radar/dashboard/queries.py`
- Modify: `src/fashion_radar/dashboard/app.py`
- Modify: `docs/dashboard.md`

- [ ] **Step 1: Add `recent_signals` query**

In `queries.py`, import `report_safe_snippet` and add:

```python
def recent_signals(data_dir: Path, *, limit: int = 20) -> list[dict[str, Any]]:
    db_path = database_path(data_dir)
    if not db_path.exists():
        return []
    engine = create_sqlite_engine(db_path)
    statement = (
        select(
            items.c.collected_at,
            items.c.published_at,
            items.c.source_name,
            items.c.source_type,
            items.c.title,
            items.c.url,
            items.c.summary,
        )
        .order_by(items.c.collected_at.desc(), items.c.id.desc())
        .limit(limit)
    )
    try:
        with engine.connect() as connection:
            rows = connection.execute(statement).mappings()
            return [
                {
                    "collected_at": row["collected_at"],
                    "published_at": row["published_at"],
                    "source_name": row["source_name"],
                    "source_type": row["source_type"],
                    "title": row["title"],
                    "url": row["url"],
                    "summary": report_safe_snippet(row["summary"]),
                }
                for row in rows
            ]
    finally:
        engine.dispose()
```

- [ ] **Step 2: Drive entity tabs from `EntityType`**

In `app.py`, import `EntityType` and `recent_signals`. Add:

```python
ENTITY_MENTION_TABS = tuple(
    (entity_type.value, f"{entity_type.value.title()} Mentions")
    for entity_type in EntityType
)
DASHBOARD_TAB_LABELS = (
    "Daily Brief",
    "Candidate Signals",
    "Trend Deltas",
    *(label for _entity_type, label in ENTITY_MENTION_TABS),
    "Source Health",
)
```

Update `main()` to keep the first three tabs, iterate over
`ENTITY_MENTION_TABS`, and keep the final health tab. In the Daily Brief tab,
render `recent_signals(args.data_dir)` with `st.dataframe()` when rows exist or
`st.info("No recent local signals yet.")` when empty.

- [ ] **Step 3: Update dashboard docs**

Update `docs/dashboard.md` so it mentions:

- Daily Brief includes recent local signals;
- mention tabs cover all entity types, not only brand/product/celebrity;
- report files remain the source for full heat-score rankings and score
  components.

- [ ] **Step 4: Verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_dashboard.py -q -k "recent_signals or tab or dashboard_queries"
```

Expected: dashboard tests pass.

## Task 5: Stage 36 Verification And Claude Code Release Review

**Files:**

- Add: `docs/reviews/claude-code-stage-36-release-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-36-release-review.md`

- [ ] **Step 1: Focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_reports.py tests/test_workflows.py tests/test_dashboard.py -q
UV_NO_CONFIG=1 uv run ruff check src/fashion_radar/models/report.py src/fashion_radar/reports.py src/fashion_radar/dashboard/app.py src/fashion_radar/dashboard/queries.py tests/test_reports.py tests/test_workflows.py tests/test_dashboard.py
UV_NO_CONFIG=1 uv run ruff format --check src/fashion_radar/models/report.py src/fashion_radar/reports.py src/fashion_radar/dashboard/app.py src/fashion_radar/dashboard/queries.py tests/test_reports.py tests/test_workflows.py tests/test_dashboard.py
```

- [ ] **Step 2: Full release verification**

Run:

```bash
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
UV_NO_CONFIG=1 CI=true GITHUB_ACTIONS=true _TYPER_FORCE_DISABLE_TERMINAL=1 uv run pytest -q
UV_NO_CONFIG=1 uv run ruff check .
UV_NO_CONFIG=1 uv run ruff format --check .
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```

- [ ] **Step 3: Boundary scans**

Run diff-scoped scans to confirm there are no dependency, schema, source
connector, scraping, platform automation, source acquisition, scheduler, data,
report artifact, or token changes.

- [ ] **Step 4: Claude Code release review**

Create a release review prompt that includes the diff, RED/GREEN evidence,
verification evidence, and boundary scan evidence. Required approval phrase:

```text
APPROVED FOR STAGE 36 COMMIT AND PUSH
```

Fix Critical/Important findings before commit.

## Task 6: Commit, Push, And GitHub Actions Confirmation

**Files:**

- Git only.

- [ ] **Step 1: Stage only Stage 36 files**

Stage only the files listed in this plan. Confirm no `uv.lock`, schema,
dependency, generated data, generated reports, or unrelated docs are staged.

- [ ] **Step 2: Commit and push**

Commit:

```bash
git commit -m "Harden report snippets and dashboard signals" \
  -m "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

Push with a one-shot HTTP extraheader. Do not persist the GitHub token.

- [ ] **Step 3: Confirm GitHub Actions**

Poll the latest GitHub Actions run for the pushed commit until it completes.
If it fails, debug with job logs and do not proceed to the next stage.

## Handoff Summary Requirement

At node end, write a concise Handoff Summary with:

- repo status;
- verified commands;
- GitHub Actions result;
- uncommitted files;
- next step.

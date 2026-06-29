# Stage 212 Source Model + Plumbing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `SourceType.HTML`/`SITEMAP`, a `seed_urls` field with target validation, no-op `HtmlCollector`/`SitemapCollector` stubs, default-collector registration, and a runner enrichment-skip guard — all plumbing only, with zero real extraction logic.

**Architecture:** This stage extends the existing source model (`src/fashion_radar/models/source.py`) with two new `SourceType` values and a `seed_urls` list, then adds two new collector modules that implement the existing `Collector` protocol (`src/fashion_radar/collectors/runner.py` lines 22-28) as no-op stubs returning `CollectorResult.success(...)` with an empty item list (reusing `CollectorResult` in `src/fashion_radar/collectors/base.py` lines 38-113). The stubs are registered in `_default_collectors()` (`src/fashion_radar/workflows.py` lines 116-121), and `collect_sources` (`src/fashion_radar/collectors/runner.py` lines 34-125) gets a single guard so its existing article-snippet enrichment re-run (lines ~91-104) is skipped for HTML/SITEMAP sources. No DB schema change, no new dependency, no change to the `items` table, matching, scoring, or reporting.

**Tech Stack:** Python 3.11, Pydantic v2 (`BaseModel`/`Field`/`model_validator`/`ConfigDict`), SQLAlchemy (unchanged), pytest, `uv --no-config run --frozen`, review by local Claude Code (`claude --effort max --permission-mode plan --no-session-persistence --tools Read,Grep,Glob,LS,Bash`) followed by opencode revision (`opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`).

**Core product gap closed:** This stage is the **plumbing foundation** for the direct web-acquisition gap described in the Phase 1 design spec (`docs/superpowers/specs/2026-06-29-phase1-web-collectors-design.md`). The gap itself (sites that publish via plain HTML pages or sitemaps but have no feed are invisible to the pipeline) is **closed by Stages 213-215**: Stage 213 fills `HtmlCollector.collect` with real trafilatura extraction, Stage 214 fills `SitemapCollector.collect` with sitemap discovery + the same extraction path, and Stage 215 expands RSS/RSSHub coverage. Stage 212 only wires the source model and collector registry so those later stages can be developed against a stable, registered, runnable plumbing base.

---

## Scope

In scope (Stage 212 = sub-stage 1b of Phase 1):

- Add `HTML = "html"` and `SITEMAP = "sitemap"` to `SourceType`.
- Add `seed_urls: list[str] = Field(default_factory=list)` to `SourceDefinition`.
- Extend `validate_source_target` with HTML and SITEMAP branches.
- Add no-op `HtmlCollector` (`src/fashion_radar/collectors/html.py`) and no-op `SitemapCollector` (`src/fashion_radar/collectors/sitemap.py`).
- Register both collectors in `_default_collectors()`.
- Add one runner enrichment-skip guard for HTML/SITEMAP sources.
- Add focused TDD tests for all of the above.
- Stage 212 Claude Code + opencode review artifacts.
- Final release verification + commit.

Out of scope (deliberately deferred):

- No real HTML page extraction (Stage 213).
- No real sitemap discovery (Stage 214).
- No RSS/RSSHub expansion data or RSSHub self-host docs (Stage 215).
- No DB schema change and no `SCHEMA_VERSION` bump.
- No dependency change (no `pyproject.toml`, no `uv.lock`).
- No change to matching, scoring, candidate discovery, reports, dashboard, importer, source-liveness, community-handoff, imported, external-tool, social/platform connector, scraping, browser automation, account/cookie/token/session, proxy, demand proof, platform coverage verification, ranking, hot-list, or compliance-review behavior.
- No CHANGELOG.md entry in this stage. Rationale: Stage 212 ships no user-facing capability (the new collectors return zero items until 213/214). The user-facing changelog entry belongs in Stage 213/214 when extraction actually lands. This is an explicit decision, not an omission.

## File Map

Exact paths and the line ranges they occupy at the start of this stage (verify each before editing):

- Modify `src/fashion_radar/models/source.py` (whole file is 91 lines)
  - `class SourceType(StrEnum)` — **lines 8-13** (currently RSS, RSSHUB, GDELT, MANUAL_IMPORT). Add `HTML` and `SITEMAP`.
  - `class SourceDefinition(BaseModel)` field block — **lines 61-74**; `url: str | None = None` is on **line 66**. Add `seed_urls` immediately after `url`.
  - `validate_source_target` model_validator — **lines 83-91**. Add HTML and SITEMAP branches before `return self` on line 91.
- Add `src/fashion_radar/collectors/html.py` (NEW) — `HtmlCollector` no-op stub.
- Add `src/fashion_radar/collectors/sitemap.py` (NEW) — `SitemapCollector` no-op stub.
- Modify `src/fashion_radar/workflows.py`
  - Import block — **lines 8-10**. Add imports for `HtmlCollector` and `SitemapCollector`.
  - `_default_collectors()` — **lines 116-121**. Register the two new collectors.
- Modify `src/fashion_radar/collectors/runner.py`
  - `collect_sources` enrichment block — **lines 91-104**; the enrichment guard is on **line 93**. Add the HTML/SITEMAP skip. `SourceType` is **already imported on line 18** (`from fashion_radar.models.source import SourceDefinition, SourceType`) — confirm, no new import line needed.
- Add `tests/test_source_model.py` (NEW) — enum values, `seed_urls` default, validator branches.
- Add `tests/test_collectors_html.py` (NEW) — no-op `collect()` returns SUCCESS with empty items.
- Add `tests/test_collectors_sitemap.py` (NEW) — no-op `collect()` returns SUCCESS with empty items.
- Modify `tests/test_workflows.py` — add a default-collector registration test.
- Modify `tests/test_collectors_runner.py` — add the enrichment-skip test.
- Add `docs/reviews/claude-code-stage-212-plan-review.md` (and `docs/reviews/opencode-stage-212-plan-review.md` if a revision is needed).
- Add `docs/reviews/claude-code-stage-212-code-review.md` (and `docs/reviews/opencode-stage-212-code-review.md` if a revision is needed).

## Task 0: Plan Review (project iron rule 2)

**Files:**

- Add: `docs/reviews/claude-code-stage-212-plan-review.md`
- Conditionally add: `docs/reviews/opencode-stage-212-plan-review.md`

- [ ] **Step 1: Hand this plan to local Claude Code for review**

Run from the repo root (`/home/ubuntu/fashion-radar`):

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Review the Stage 212 implementation plan at docs/superpowers/plans/2026-06-29-stage-212-source-model-plumbing-plan.md against the design spec at docs/superpowers/specs/2026-06-29-phase1-web-collectors-design.md (especially sections 5, 7, 9). Verify: (1) the SourceType/seed_urls/validator edits match the real source model at src/fashion_radar/models/source.py; (2) the HtmlCollector/SitemapCollector stubs correctly implement the Collector protocol at src/fashion_radar/collectors/runner.py lines 22-28 and reuse CollectorResult.success from src/fashion_radar/collectors/base.py lines 44-68; (3) the runner enrichment-skip guard is placed correctly relative to lines 91-104; (4) no real extraction logic leaks in (plumbing only); (5) scope is tight (no schema/dependency/matching changes); (6) the TDD steps are RED-first and each shows complete code and exact pytest commands. Flag Critical/Important/Nice-to-have findings." > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-212-plan-review.md
rm -f "$tmp_review"
```

Expected: a completed review artifact with no Critical or Important blockers.

- [ ] **Step 2: Revise the plan per Claude Code findings + own judgment**

If Claude Code raised Critical/Important findings (or if Claude Code is unavailable and an independent opencode agent reviewed instead), fix the plan in this file and, if a second review pass is warranted, capture the opencode revision under `docs/reviews/opencode-stage-212-plan-review.md` using:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "Review the revised Stage 212 plan at docs/superpowers/plans/2026-06-29-stage-212-source-model-plumbing-plan.md for correctness and scope control before implementation." > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-212-plan-review.md
rm -f "$tmp_review"
```

Proceed to Task 1 only after the plan has no outstanding Critical/Important findings.

## Task 1: SourceType enum + seed_urls field + validator (RED → GREEN)

**Files:**

- Add: `tests/test_source_model.py`
- Modify: `src/fashion_radar/models/source.py`

- [ ] **Step 1 (RED): Write the failing source-model test file**

Create `tests/test_source_model.py` with this exact content:

```python
from __future__ import annotations

import pytest
from pydantic import ValidationError

from fashion_radar.models.source import SourceDefinition, SourceType


def test_source_type_includes_html_and_sitemap_values() -> None:
    assert SourceType.HTML == "html"
    assert SourceType.SITEMAP == "sitemap"


def test_source_definition_seed_urls_defaults_to_empty_list() -> None:
    source = SourceDefinition(name="Brand X", type=SourceType.HTML, url="https://brandx.com/news")

    assert source.seed_urls == []


def test_html_source_requires_url_or_seed_urls() -> None:
    with pytest.raises(ValidationError, match="html source requires url or seed_urls"):
        SourceDefinition(name="Brand X", type=SourceType.HTML)


def test_html_source_with_only_seed_urls_is_valid() -> None:
    source = SourceDefinition(
        name="Brand X",
        type=SourceType.HTML,
        seed_urls=["https://brandx.com/press", "https://brandx.com/collections"],
    )

    assert source.url is None
    assert source.seed_urls == ["https://brandx.com/press", "https://brandx.com/collections"]


def test_html_source_with_only_url_is_valid() -> None:
    source = SourceDefinition(name="Brand X", type=SourceType.HTML, url="https://brandx.com/news")

    assert source.url == "https://brandx.com/news"
    assert source.seed_urls == []


def test_sitemap_source_requires_url() -> None:
    with pytest.raises(ValidationError, match="sitemap source requires url"):
        SourceDefinition(name="News Daily", type=SourceType.SITEMAP)


def test_sitemap_source_with_url_is_valid() -> None:
    source = SourceDefinition(
        name="News Daily",
        type=SourceType.SITEMAP,
        url="https://newsdaily.com/sitemap.xml",
    )

    assert source.url == "https://newsdaily.com/sitemap.xml"
```

- [ ] **Step 2 (RED): Run to confirm failure**

Run:

```bash
uv --no-config run --frozen pytest tests/test_source_model.py -q
```

Expected outcome (RED): collection errors / failures. Specifically `test_source_type_includes_html_and_sitemap_values` fails with `AttributeError: HTML is not a valid SourceType` (the `HTML`/`SITEMAP` members do not exist yet), and every other test fails the same way because `SourceType.HTML`/`SourceType.SITEMAP` cannot be resolved, or fails with `ValidationError` "Extra inputs are not permitted" for `seed_urls` once the enum exists. All seven tests must be failing.

- [ ] **Step 3 (GREEN): Add the enum members**

In `src/fashion_radar/models/source.py`, replace the `SourceType` block (lines 8-13):

```python
class SourceType(StrEnum):
    RSS = "rss"
    RSSHUB = "rsshub"
    GDELT = "gdelt"
    MANUAL_IMPORT = "manual_import"
```

with:

```python
class SourceType(StrEnum):
    RSS = "rss"
    RSSHUB = "rsshub"
    GDELT = "gdelt"
    HTML = "html"
    SITEMAP = "sitemap"
    MANUAL_IMPORT = "manual_import"
```

(`Field` is already imported on line 5 — no new import needed.)

- [ ] **Step 4 (GREEN): Add the seed_urls field**

In `src/fashion_radar/models/source.py`, the `SourceDefinition` field block currently has `url: str | None = None` on line 66. Replace:

```python
    name: str
    type: SourceType
    url: str | None = None
    query: str | None = None
```

with:

```python
    name: str
    type: SourceType
    url: str | None = None
    seed_urls: list[str] = Field(default_factory=list)
    query: str | None = None
```

- [ ] **Step 5 (GREEN): Extend the validator**

In `src/fashion_radar/models/source.py`, the `validate_source_target` validator (lines 83-91) currently ends:

```python
    @model_validator(mode="after")
    def validate_source_target(self) -> SourceDefinition:
        if self.type == SourceType.MANUAL_IMPORT:
            raise ValueError("manual_import is import-only; use fashion-radar import-signals")
        if self.type in {SourceType.RSS, SourceType.RSSHUB} and not self.url:
            raise ValueError(f"{self.type.value} source requires url")
        if self.type == SourceType.GDELT and not self.query:
            raise ValueError("gdelt source requires query")
        return self
```

Replace the `if self.type == SourceType.GDELT ...` and `return self` tail with:

```python
        if self.type == SourceType.GDELT and not self.query:
            raise ValueError("gdelt source requires query")
        if self.type == SourceType.HTML and not (self.url or self.seed_urls):
            raise ValueError("html source requires url or seed_urls")
        if self.type == SourceType.SITEMAP and not self.url:
            raise ValueError("sitemap source requires url (sitemap.xml or site root)")
        return self
```

- [ ] **Step 6 (GREEN): Run to confirm passing**

Run:

```bash
uv --no-config run --frozen pytest tests/test_source_model.py -q
```

Expected outcome (GREEN): all 7 tests pass. Then run the full config + collectors suites to confirm no regression:

```bash
uv --no-config run --frozen pytest tests/test_config.py tests/test_collectors_runner.py tests/test_collectors_base.py tests/test_collectors_rss.py tests/test_workflows.py -q
```

Expected: all pass (the new enum members and the optional `seed_urls` field are backward-compatible additions; existing RSS/GDELT/manual_import assertions are unaffected).

- [ ] **Step 7: Commit**

```bash
git add src/fashion_radar/models/source.py tests/test_source_model.py
git commit -m "Stage 212: add HTML/SITEMAP source types and seed_urls field"
```

## Task 2: HtmlCollector and SitemapCollector no-op stubs (RED → GREEN)

**Files:**

- Add: `tests/test_collectors_html.py`
- Add: `tests/test_collectors_sitemap.py`
- Add: `src/fashion_radar/collectors/html.py`
- Add: `src/fashion_radar/collectors/sitemap.py`

- [ ] **Step 1 (RED): Write the failing HtmlCollector test**

Create `tests/test_collectors_html.py` with this exact content:

```python
from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.collectors.base import CollectorRunStatus
from fashion_radar.collectors.html import HtmlCollector
from fashion_radar.models.source import SourceDefinition, SourceType


def test_html_collector_no_op_returns_success_with_no_items() -> None:
    source = SourceDefinition(
        name="Brand X Newsroom",
        type=SourceType.HTML,
        url="https://brandx.com/news",
    )
    collector = HtmlCollector()
    started_at = datetime(2026, 6, 11, 12, 0, tzinfo=UTC)

    result = collector.collect(source, started_at=started_at)

    assert result.status.status == CollectorRunStatus.SUCCESS
    assert result.status.source_name == "Brand X Newsroom"
    assert result.status.source_type == SourceType.HTML
    assert result.items == []
```

- [ ] **Step 2 (RED): Write the failing SitemapCollector test**

Create `tests/test_collectors_sitemap.py` with this exact content:

```python
from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.collectors.base import CollectorRunStatus
from fashion_radar.collectors.sitemap import SitemapCollector
from fashion_radar.models.source import SourceDefinition, SourceType


def test_sitemap_collector_no_op_returns_success_with_no_items() -> None:
    source = SourceDefinition(
        name="Fashion News Daily",
        type=SourceType.SITEMAP,
        url="https://fashionnewsdaily.com/sitemap.xml",
    )
    collector = SitemapCollector()
    started_at = datetime(2026, 6, 11, 12, 0, tzinfo=UTC)

    result = collector.collect(source, started_at=started_at)

    assert result.status.status == CollectorRunStatus.SUCCESS
    assert result.status.source_name == "Fashion News Daily"
    assert result.status.source_type == SourceType.SITEMAP
    assert result.items == []
```

- [ ] **Step 3 (RED): Run to confirm failure**

Run:

```bash
uv --no-config run --frozen pytest tests/test_collectors_html.py tests/test_collectors_sitemap.py -q
```

Expected outcome (RED): both tests error with `ModuleNotFoundError: No module named 'fashion_radar.collectors.html'` and `ModuleNotFoundError: No module named 'fashion_radar.collectors.sitemap'` respectively.

- [ ] **Step 4 (GREEN): Create the HtmlCollector stub**

Create `src/fashion_radar/collectors/html.py` with this exact content:

```python
from __future__ import annotations

from datetime import datetime

from fashion_radar.collectors.base import CollectorResult
from fashion_radar.models.source import SourceDefinition


class HtmlCollector:
    """Collector for ``html`` sources.

    Stage 212 is plumbing-only: ``collect`` is a no-op stub that returns a
    successful result with no items so the collector can be registered in the
    default collector map and exercised end-to-end by ``collect_sources``.
    Real seed-URL fetch + trafilatura extraction lands in Stage 213.
    """

    def collect(
        self,
        source: SourceDefinition,
        *,
        started_at: datetime | None = None,
    ) -> CollectorResult:
        return CollectorResult.success(source, items=[], started_at=started_at)
```

- [ ] **Step 5 (GREEN): Create the SitemapCollector stub**

Create `src/fashion_radar/collectors/sitemap.py` with this exact content:

```python
from __future__ import annotations

from datetime import datetime

from fashion_radar.collectors.base import CollectorResult
from fashion_radar.models.source import SourceDefinition


class SitemapCollector:
    """Collector for ``sitemap`` sources.

    Stage 212 is plumbing-only: ``collect`` is a no-op stub that returns a
    successful result with no items so the collector can be registered in the
    default collector map and exercised end-to-end by ``collect_sources``.
    Real sitemap discovery + trafilatura extraction lands in Stage 214.
    """

    def collect(
        self,
        source: SourceDefinition,
        *,
        started_at: datetime | None = None,
    ) -> CollectorResult:
        return CollectorResult.success(source, items=[], started_at=started_at)
```

- [ ] **Step 6 (GREEN): Run to confirm passing**

Run:

```bash
uv --no-config run --frozen pytest tests/test_collectors_html.py tests/test_collectors_sitemap.py -q
```

Expected outcome (GREEN): both tests pass.

- [ ] **Step 7: Commit**

```bash
git add src/fashion_radar/collectors/html.py src/fashion_radar/collectors/sitemap.py tests/test_collectors_html.py tests/test_collectors_sitemap.py
git commit -m "Stage 212: add no-op HtmlCollector and SitemapCollector stubs"
```

## Task 3: Register HtmlCollector and SitemapCollector in `_default_collectors()` (RED → GREEN)

**Files:**

- Modify: `tests/test_workflows.py`
- Modify: `src/fashion_radar/workflows.py`

- [ ] **Step 1 (RED): Add the registration test**

The existing `tests/test_workflows.py` already imports `_default_collectors` (line 14) and has `test_manual_import_is_not_a_default_collector` (line 112). Add these imports to the top-of-file import block. Replace:

```python
from fashion_radar.workflows import (
    _default_collectors,
    clean_old_data,
    collect_configured_sources,
    default_database_path,
    match_stored_items,
    write_daily_report_files,
)
```

with:

```python
from fashion_radar.collectors.gdelt import GdeltCollector
from fashion_radar.collectors.html import HtmlCollector
from fashion_radar.collectors.rss import RssCollector
from fashion_radar.collectors.sitemap import SitemapCollector
from fashion_radar.workflows import (
    _default_collectors,
    clean_old_data,
    collect_configured_sources,
    default_database_path,
    match_stored_items,
    write_daily_report_files,
)
```

Then append this new test function at the end of `tests/test_workflows.py`:

```python
def test_default_collectors_register_html_and_sitemap() -> None:
    collectors = _default_collectors()

    assert isinstance(collectors[SourceType.HTML], HtmlCollector)
    assert isinstance(collectors[SourceType.SITEMAP], SitemapCollector)
    assert isinstance(collectors[SourceType.RSS], RssCollector)
    assert isinstance(collectors[SourceType.RSSHUB], RssCollector)
    assert isinstance(collectors[SourceType.GDELT], GdeltCollector)
```

- [ ] **Step 2 (RED): Run to confirm failure**

Run:

```bash
uv --no-config run --frozen pytest tests/test_workflows.py::test_default_collectors_register_html_and_sitemap -q
```

Expected outcome (RED): `KeyError: <SourceType.HTML: 'html'>` (and/or `<SourceType.SITEMAP: 'sitemap'>`) — the default map does not yet contain those keys.

- [ ] **Step 3 (GREEN): Add imports to workflows.py**

In `src/fashion_radar/workflows.py`, replace the collector import block (lines 8-10):

```python
from fashion_radar.collectors.gdelt import GdeltCollector
from fashion_radar.collectors.rss import RssCollector
from fashion_radar.collectors.runner import collect_sources
```

with:

```python
from fashion_radar.collectors.gdelt import GdeltCollector
from fashion_radar.collectors.html import HtmlCollector
from fashion_radar.collectors.rss import RssCollector
from fashion_radar.collectors.runner import collect_sources
from fashion_radar.collectors.sitemap import SitemapCollector
```

- [ ] **Step 4 (GREEN): Register the collectors**

In `src/fashion_radar/workflows.py`, replace `_default_collectors()` (lines 116-121):

```python
def _default_collectors() -> dict[SourceType, object]:
    return {
        SourceType.RSS: RssCollector(),
        SourceType.RSSHUB: RssCollector(),
        SourceType.GDELT: GdeltCollector(),
    }
```

with:

```python
def _default_collectors() -> dict[SourceType, object]:
    return {
        SourceType.RSS: RssCollector(),
        SourceType.RSSHUB: RssCollector(),
        SourceType.GDELT: GdeltCollector(),
        SourceType.HTML: HtmlCollector(),
        SourceType.SITEMAP: SitemapCollector(),
    }
```

- [ ] **Step 5 (GREEN): Run to confirm passing**

Run:

```bash
uv --no-config run --frozen pytest tests/test_workflows.py -q
```

Expected outcome (GREEN): all tests in `tests/test_workflows.py` pass, including the new registration test and the existing `test_manual_import_is_not_a_default_collector`.

- [ ] **Step 6: Commit**

```bash
git add src/fashion_radar/workflows.py tests/test_workflows.py
git commit -m "Stage 212: register HtmlCollector and SitemapCollector as defaults"
```

## Task 4: Runner article-enrichment skip for HTML/SITEMAP (RED → GREEN)

**Files:**

- Modify: `tests/test_collectors_runner.py`
- Modify: `src/fashion_radar/collectors/runner.py`

- [ ] **Step 1 (RED): Add the enrichment-skip test**

Append this new test function to `tests/test_collectors_runner.py` (the file already imports `ArticleExtractionResult`, `CollectedItem`, `SourceDefinition`, `SourceType`, `collect_sources`, `create_sqlite_engine`, `initialize_schema`, `datetime`, `UTC`, and reuses the module-level `SuccessfulCollector` class which returns one item with `summary="Short attributed signal."`):

```python
def test_collect_sources_skips_article_enrichment_for_html_and_sitemap(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    html_source = SourceDefinition(
        name="HTML News",
        type=SourceType.HTML,
        url="https://example.com/news",
    )
    rss_source = SourceDefinition(
        name="RSS Feed",
        type=SourceType.RSS,
        url="https://example.com/feed.xml",
    )

    extractor_calls = {"count": 0}

    def article_extractor(
        source: SourceDefinition,
        item: CollectedItem,
    ) -> ArticleExtractionResult:
        extractor_calls["count"] += 1
        return ArticleExtractionResult(
            url=item.url,
            text=f"ENRICHED {source.name}",
            skipped=False,
        )

    results = collect_sources(
        [html_source, rss_source],
        engine=engine,
        collectors={
            "HTML News": SuccessfulCollector(),
            "RSS Feed": SuccessfulCollector(),
        },
        article_extractor=article_extractor,
        now=datetime(2026, 6, 11, 12, 0, tzinfo=UTC),
    )

    assert results[0].status.source_type == SourceType.HTML
    assert results[1].status.source_type == SourceType.RSS
    assert results[0].items[0].summary == "Short attributed signal."
    assert results[1].items[0].summary == "ENRICHED RSS Feed"
    assert extractor_calls["count"] == 1
```

Note: both sources default to `article.enabled=True` (the `ArticleSourceSettings` default), which is intentional — the test proves the skip is driven by `source.type`, not by `article.enabled`.

- [ ] **Step 2 (RED): Run to confirm failure**

Run:

```bash
uv --no-config run --frozen pytest tests/test_collectors_runner.py::test_collect_sources_skips_article_enrichment_for_html_and_sitemap -q
```

Expected outcome (RED): assertion failure. Without the guard, the runner enriches both the HTML and RSS items, so `results[0].items[0].summary` is `"ENRICHED HTML News"` (not `"Short attributed signal."`) and `extractor_calls["count"]` is `2` (not `1`).

- [ ] **Step 3 (GREEN): Add the runner enrichment-skip guard**

In `src/fashion_radar/collectors/runner.py`, the enrichment block (lines 91-104) currently reads:

```python
        items_stored = 0
        if result.status.status == CollectorRunStatus.SUCCESS:
            if source_article_extractor is not None:
                result = result.model_copy(
                    update={
                        "items": _enrich_items_with_article_snippets(
                            source,
                            result.items,
                            source_article_extractor,
                        )
                    }
                )
            if close_article_extractor is not None:
                close_article_extractor()
```

Replace the inner `if source_article_extractor is not None:` line with a guarded condition so HTML/SITEMAP sources skip enrichment. The block becomes:

```python
        items_stored = 0
        if result.status.status == CollectorRunStatus.SUCCESS:
            if source_article_extractor is not None and source.type not in {
                SourceType.HTML,
                SourceType.SITEMAP,
            }:
                result = result.model_copy(
                    update={
                        "items": _enrich_items_with_article_snippets(
                            source,
                            result.items,
                            source_article_extractor,
                        )
                    }
                )
            if close_article_extractor is not None:
                close_article_extractor()
```

`SourceType` is already imported in `src/fashion_radar/collectors/runner.py` on line 18 (`from fashion_radar.models.source import SourceDefinition, SourceType`). Confirm the import is present; no new import line is required.

- [ ] **Step 4 (GREEN): Run to confirm passing**

Run:

```bash
uv --no-config run --frozen pytest tests/test_collectors_runner.py -q
```

Expected outcome (GREEN): all tests in `tests/test_collectors_runner.py` pass, including the existing `test_collect_sources_enriches_items_with_article_snippet_before_upsert` (RSS enrichment still works) and the new `test_collect_sources_skips_article_enrichment_for_html_and_sitemap`.

- [ ] **Step 5: Commit**

```bash
git add src/fashion_radar/collectors/runner.py tests/test_collectors_runner.py
git commit -m "Stage 212: skip article enrichment for HTML and SITEMAP sources"
```

## Task 5: Claude Code code review + release verification + commit

**Files:**

- Add: `docs/reviews/claude-code-stage-212-code-review.md`
- Conditionally add: `docs/reviews/opencode-stage-212-code-review.md`

- [ ] **Step 1: Run the focused Stage 212 test set**

Run:

```bash
uv --no-config run --frozen pytest tests/test_source_model.py tests/test_collectors_html.py tests/test_collectors_sitemap.py tests/test_collectors_runner.py tests/test_collectors_base.py tests/test_collectors_rss.py tests/test_config.py tests/test_workflows.py -q
```

Expected: all pass.

- [ ] **Step 2: Run lint + format check**

Run:

```bash
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
```

Expected: no findings; no reformatting needed.

- [ ] **Step 3: Claude Code code review (project iron rule 2)**

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Review the Stage 212 code changes (git diff against the stage start) for Fashion Radar. Focus on: (1) src/fashion_radar/models/source.py — SourceType.HTML/SITEMAP additions, seed_urls field placement, validator branches; (2) src/fashion_radar/collectors/html.py and sitemap.py — no-op stubs correctly implementing the Collector protocol and reusing CollectorResult.success; (3) src/fashion_radar/workflows.py — default registration; (4) src/fashion_radar/collectors/runner.py — the single enrichment-skip guard on the article re-run path for HTML/SITEMAP. Confirm there is NO real extraction logic (plumbing only), no DB schema change, no dependency change, and that the new tests are RED-first and cover enum values, seed_urls default, all four validator branches, both no-op collectors, default registration, and the runner skip. Flag Critical/Important/Nice-to-have findings." > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-212-code-review.md
rm -f "$tmp_review"
```

Fix any Critical/Important findings, re-run the affected tests, and (if a second pass is warranted) capture an opencode revision under `docs/reviews/opencode-stage-212-code-review.md` using the standard `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar ...` form.

- [ ] **Step 4: Run full release verification**

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

Expected: full suite green; release hygiene clean; lockfile and `pyproject.toml` unchanged (no dependency change in this stage — `git diff --exit-code -- uv.lock pyproject.toml` exits 0); first-run smoke passes.

- [ ] **Step 5: Commit the review artifacts + any review-driven fixes**

Run:

```bash
git status --short --untracked-files=all
git add --ignore-missing docs/reviews/claude-code-stage-212-code-review.md docs/reviews/opencode-stage-212-code-review.md docs/superpowers/plans/2026-06-29-stage-212-source-model-plumbing-plan.md docs/reviews/claude-code-stage-212-plan-review.md docs/reviews/opencode-stage-212-plan-review.md
git commit -m "Stage 212: add HTML/SITEMAP source plumbing"
git status --short --branch --untracked-files=all
```

(The final commit message is exactly `Stage 212: add HTML/SITEMAP source plumbing`. Do not push unless the project owner asks.)

## Self-Review

- **Spec coverage:** Every Stage 212 item from the design spec section 9 (sub-stage 1b) is covered — `SourceType.HTML`/`SITEMAP` (spec 5.1), `seed_urls` field + validator (spec 5.2), `HtmlCollector`/`SitemapCollector` modules (spec 5.3), default-collector registration (spec 5.3), and the runner enrichment-skip guard (spec 5.4, "the plan pins the exact guard"). Spec section 8 test intentions (enum values, validator branches, no-op collectors, default registration, runner enrichment-skip) are all present as concrete TDD tests. No real extraction (spec 5.4 data flow) is implemented — that is explicitly deferred to 213/214.
- **Placeholder scan:** No TBD/TODO/fill-in/`...` placeholders remain in this plan. Every code step shows complete, copy-pasteable code.
- **Type consistency:** The new enum members are consistently named `HTML`/`SITEMAP` with values `"html"`/`"sitemap"` across the model, collectors, workflow registration, runner guard, and tests. The `seed_urls` field name is used consistently in the model, validator, and test. The collector class names `HtmlCollector`/`SitemapCollector` are used consistently in the new modules, the workflow imports/registration, and the tests.
- **Scope check:** This is a plumbing-only node. It deliberately avoids real HTML/sitemap extraction (213/214), RSSHub expansion (215), any DB schema change, any dependency/`pyproject.toml`/`uv.lock` change, and any change to matching, scoring, candidate discovery, reporting, dashboard, importer, source-liveness, community-handoff, imported, external-tool, social/platform connector, scraping, browser automation, account/cookie/token/session, proxy, demand proof, platform coverage verification, ranking, hot-list, or compliance-review behavior.
- **Changelog decision:** No `CHANGELOG.md` entry is added in this stage, by explicit decision (plumbing ships no user-facing capability; the user-facing entry belongs in Stage 213/214).

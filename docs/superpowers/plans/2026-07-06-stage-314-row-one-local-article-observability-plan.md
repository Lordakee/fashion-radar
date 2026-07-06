# Stage 314 ROW ONE Local Article Observability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> When spawning Codex subagents for this project, set `reasoning_effort` to `xhigh` as required by `AGENTS.md`.

**Goal:** Add ROW ONE generated-site local article metrics so build, preview, refresh, status, tests, and docs prove whether saved local article bodies are present in the generated website.

**Architecture:** Create a small `row_one.site_metrics` module that reads generated `data/articles/*.json` sidecars and returns internal metrics. Wire those metrics into CLI text/status JSON only, leaving `row-one-app/v7`, runtime, manifest, schemas, source collection, scoring, and generated JSON artifacts unchanged.

**Tech Stack:** Python 3.12, dataclasses, existing Pydantic `RowOneLocalArticle`, Typer CLI, pytest, ruff, frozen/no-config uv verification.

**Pipeline Gap Closed:** Stage 310-313 render and organize saved article bodies when sidecars exist. Stage 314 makes the generated artifact observable: operators can see whether the site actually contains saved local articles, and tests prove a deterministic enabled-source workflow creates sidecars, detail local article content, and homepage saved article modules.

---

## Non-Goals

- Do not add source collection behavior, scraping behavior, platform APIs, browser automation, login/cookie/proxy/CAPTCHA/paywall behavior, social/community connectors, connector defaults, adapter execution, external-tool imports, scoring, ranking, matching, sorting, scheduling, LLM calls, translation services, image generation, demand proof, platform coverage verification, or compliance-review product features.
- Do not change `row-one-app/v7`, `data/edition.json`, `row-one-manifest/v1`, `data/manifest.json`, `row-one-runtime/v1`, `data/runtime.json`, schemas, story IDs, detail routes, paragraph anchors, or generated detail-page routes.
- Do not write a new generated JSON artifact.
- Do not commit generated `reports/row-one/site/**`.
- Do not rewrite `uv.lock` to mirror URLs.

## Files

- Create: `src/fashion_radar/row_one/site_metrics.py`
  - Internal generated-site metrics for local article sidecars.
- Modify: `src/fashion_radar/cli.py`
  - Print local article metrics in build/preview/refresh/status output and include metrics in status JSON.
- Create: `tests/test_row_one_site_metrics.py`
  - Unit coverage for empty and populated generated-site metrics.
- Modify: `tests/test_row_one_cli.py`
  - Status output and status JSON assertions for local article metrics.
- Modify: `tests/test_workflows.py`
  - Artifact-level proof that enabled local article extraction writes sidecars and saved article homepage/detail modules.
- Modify: `tests/test_row_one_docs.py`
  - Docs boundary for Stage 314.
- Modify: `README.md`, `docs/row-one.md`
  - Explain local article observability and article extra/config requirements.
- Create review artifacts under `docs/reviews/`.

## Task 1: Add Local Article Site Metrics Tests

**Files:**
- Create: `tests/test_row_one_site_metrics.py`

- [ ] **Step 1: Add empty-site test**

Create `tests/test_row_one_site_metrics.py`:

```python
from __future__ import annotations

import json
from datetime import UTC, datetime

from fashion_radar.row_one.models import RowOneLocalArticle, RowOneLocalArticleContentSection, LocalizedText
from fashion_radar.row_one.site_metrics import (
    build_row_one_local_article_site_metrics,
    row_one_local_article_site_metrics_payload,
)

AS_OF = datetime(2026, 7, 6, 4, 0, tzinfo=UTC)


def test_local_article_site_metrics_are_zero_without_sidecars(tmp_path) -> None:
    metrics = build_row_one_local_article_site_metrics(tmp_path)

    assert metrics.article_count == 0
    assert metrics.paragraph_count == 0
    assert metrics.organized_section_count == 0
    assert metrics.source_count == 0
    assert row_one_local_article_site_metrics_payload(metrics) == {
        "article_count": 0,
        "paragraph_count": 0,
        "organized_section_count": 0,
        "source_count": 0,
    }
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_site_metrics.py::test_local_article_site_metrics_are_zero_without_sidecars -q
```

Expected: FAIL because `fashion_radar.row_one.site_metrics` does not exist.

- [ ] **Step 2: Add populated-site test**

Append:

```python
def _write_article(
    site_dir,
    story_id: str,
    *,
    source_name: str,
    paragraphs: list[str],
    organized_sections: int,
) -> None:
    articles_dir = site_dir / "data" / "articles"
    articles_dir.mkdir(parents=True, exist_ok=True)
    article = RowOneLocalArticle(
        story_id=story_id,
        title=f"{story_id} article",
        url=f"https://example.com/{story_id}",
        source_name=source_name,
        extracted_at=AS_OF,
        paragraphs=paragraphs,
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(zh="要点", en="Takeaways"),
                items=[],
            )
            for _ in range(organized_sections)
        ],
    )
    (articles_dir / f"{story_id}.json").write_text(
        json.dumps(article.model_dump(mode="json"), ensure_ascii=False),
        encoding="utf-8",
    )


def test_local_article_site_metrics_count_publishable_sidecars(tmp_path) -> None:
    _write_article(
        tmp_path,
        "the-row-a-1234567890",
        source_name="Vogue Business",
        paragraphs=["One paragraph.", "   ", "Second paragraph."],
        organized_sections=2,
    )
    _write_article(
        tmp_path,
        "coach-b-1234567890",
        source_name="Vogue Business",
        paragraphs=["Coach paragraph."],
        organized_sections=1,
    )
    _write_article(
        tmp_path,
        "purse-c-1234567890",
        source_name="PurseBlog",
        paragraphs=["Bag paragraph."],
        organized_sections=0,
    )

    metrics = build_row_one_local_article_site_metrics(tmp_path)

    assert metrics.article_count == 3
    assert metrics.paragraph_count == 4
    assert metrics.organized_section_count == 3
    assert metrics.source_count == 2
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_site_metrics.py -q
```

Expected: FAIL until the metrics module exists.

## Task 2: Implement Local Article Site Metrics

**Files:**
- Create: `src/fashion_radar/row_one/site_metrics.py`

- [ ] **Step 1: Add metrics module**

Create:

```python
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from fashion_radar.row_one.models import RowOneLocalArticle


@dataclass(frozen=True)
class RowOneLocalArticleSiteMetrics:
    article_count: int = 0
    paragraph_count: int = 0
    organized_section_count: int = 0
    source_count: int = 0


def build_row_one_local_article_site_metrics(site_dir: Path) -> RowOneLocalArticleSiteMetrics:
    articles_dir = site_dir / "data" / "articles"
    if not articles_dir.is_dir():
        return RowOneLocalArticleSiteMetrics()
    article_count = 0
    paragraph_count = 0
    organized_section_count = 0
    sources: set[str] = set()
    for article_path in sorted(articles_dir.glob("*.json")):
        article = _load_article(article_path)
        if article is None:
            continue
        article_count += 1
        paragraph_count += sum(1 for paragraph in article.paragraphs if paragraph.strip())
        organized_section_count += len(article.content_sections)
        source_name = article.source_name.strip()
        if source_name:
            sources.add(" ".join(source_name.split()).casefold())
    return RowOneLocalArticleSiteMetrics(
        article_count=article_count,
        paragraph_count=paragraph_count,
        organized_section_count=organized_section_count,
        source_count=len(sources),
    )


def row_one_local_article_site_metrics_payload(
    metrics: RowOneLocalArticleSiteMetrics,
) -> dict[str, int]:
    return {
        "article_count": metrics.article_count,
        "paragraph_count": metrics.paragraph_count,
        "organized_section_count": metrics.organized_section_count,
        "source_count": metrics.source_count,
    }


def _load_article(path: Path) -> RowOneLocalArticle | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return RowOneLocalArticle.model_validate(payload)
    except (OSError, json.JSONDecodeError, ValidationError):
        return None
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_site_metrics.py -q
```

Expected: PASS.

## Task 3: Add CLI/Status Metrics Tests

**Files:**
- Modify: `tests/test_row_one_cli.py`

- [ ] **Step 1: Add status text/json assertions**

Update `test_row_one_status_prints_runtime_readiness` or the closest existing
status success test to assert:

```python
assert "Saved local articles: 0" in result.output
assert "Saved local paragraphs: 0" in result.output
```

Add a dedicated JSON assertion near the status JSON test:

```python
def test_row_one_status_json_includes_local_article_metrics(tmp_path: Path) -> None:
    # Use the existing helper in tests/test_row_one_cli.py. It renders a valid
    # ROW ONE site with one current story and one matching local article sidecar.
    story = _render_status_site_with_local_article(tmp_path)

    result = CliRunner().invoke(
        app,
        ["row-one", "status", "--site-dir", str(tmp_path), "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["local_articles"] == {
        "article_count": 1,
        "paragraph_count": 2,
        "organized_section_count": 2,
        "source_count": 1,
    }
    assert payload["local_article_count"] == 1
    assert payload["local_article_paragraph_count"] == 2
    assert story["id"] in (tmp_path / "data" / "articles" / f"{story['id']}.json").read_text(
        encoding="utf-8"
    )
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py -q -k "row_one_status and local_article"
```

Expected: FAIL until CLI status includes metrics.

- [ ] **Step 2: Add build/preview/refresh count expectations where output is already stubbed**

For existing build/preview/refresh tests that assert output lines, add:

```python
assert "Saved local articles:" in result.output
assert "Saved local paragraphs:" in result.output
```

Run the touched tests.

Expected: FAIL until CLI commands print metrics.

## Task 4: Wire Metrics Into CLI

**Files:**
- Modify: `src/fashion_radar/cli.py`

- [ ] **Step 1: Import metrics helpers**

Add:

```python
from fashion_radar.row_one.site_metrics import (
    build_row_one_local_article_site_metrics,
    row_one_local_article_site_metrics_payload,
)
```

- [ ] **Step 2: Add local helper**

Add near `_build_row_one_status_payload`:

```python
def _row_one_local_article_metrics_payload(site_dir: Path) -> dict[str, int]:
    metrics = build_row_one_local_article_site_metrics(site_dir)
    return row_one_local_article_site_metrics_payload(metrics)


def _echo_row_one_local_article_metrics(site_dir: Path) -> None:
    metrics = _row_one_local_article_metrics_payload(site_dir)
    typer.echo(f"Saved local articles: {metrics['article_count']}")
    typer.echo(f"Saved local paragraphs: {metrics['paragraph_count']}")
```

- [ ] **Step 3: Add status JSON fields**

In `_build_row_one_status_payload`, compute:

```python
local_articles = _row_one_local_article_metrics_payload(site_dir)
```

Include in the returned payload:

```python
"local_articles": local_articles,
"local_article_count": local_articles["article_count"],
"local_article_paragraph_count": local_articles["paragraph_count"],
```

- [ ] **Step 4: Print metrics in text commands**

In `row_one_build`, after story count:

```python
_echo_row_one_local_article_metrics(result.output_dir)
```

In `row_one_preview`, after evidence links or before generated-at:

```python
_echo_row_one_local_article_metrics(result.output_dir)
```

In `row_one_refresh`, after evidence links:

```python
_echo_row_one_local_article_metrics(site_result.output_dir)
```

In `row_one_status`, after evidence links:

```python
local_articles = payload["local_articles"]
typer.echo(f"Saved local articles: {local_articles['article_count']}")
typer.echo(f"Saved local paragraphs: {local_articles['paragraph_count']}")
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py -q -k "row_one_status or row_one_build or row_one_preview or row_one_refresh"
```

Expected: PASS after updating assertions.

## Task 5: Add Workflow Artifact Proof

**Files:**
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Strengthen the existing local article workflow test**

In `test_write_row_one_site_files_writes_local_article_without_mutating_sqlite`
or the closest existing test, assert generated homepage/detail artifact proof:

```python
index_html = (output_dir / "index.html").read_text(encoding="utf-8")
detail_html = next((output_dir / "details").glob("*.html")).read_text(encoding="utf-8")
article_files = list((output_dir / "data" / "articles").glob("*.json"))

assert len(article_files) == 1
assert 'id="local-article"' in detail_html
assert "Local article paragraph for the ROW ONE detail page." in detail_html
assert (
    "daily-local-intelligence" in index_html
    or "saved-article-coverage" in index_html
    or "saved-article-briefs" in index_html
)
```

Run this test before deciding whether any render wiring needs to change:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite -q
```

Expected: PASS if the existing workflow path already creates homepage saved modules; otherwise implement only the smallest missing render wiring needed to satisfy the artifact proof without changing contracts.

## Task 6: Update Docs And Docs Tests

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Add docs test**

Add:

```python
def test_row_one_docs_describe_local_article_observability_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "row-one.md").read_text(encoding="utf-8")

    expected_phrases = [
        "local article observability",
        "saved local articles",
        "saved local paragraphs",
        "row-one status --json",
        "`row_one_article.enabled: true`",
        "optional article extraction dependency",
        "does not change `row-one-app/v7`",
        "does not write a new json artifact",
        "does not add source collection",
        "does not add scoring",
        "does not add llm calls",
    ]
    for phrase in expected_phrases:
        assert phrase in readme
        assert phrase in docs
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_local_article_observability_boundary -q
```

Expected: FAIL until docs are updated.

- [ ] **Step 2: Add docs wording**

Add a short paragraph near the Stage 313 paragraph in both `README.md` and
`docs/row-one.md`:

```markdown
Stage 314 adds local article observability for ROW ONE: build, preview,
refresh, and `row-one status --json` report saved local articles and saved local
paragraphs from generated `data/articles/<story-id>.json` sidecars. This proves
whether the generated website contains local saved article bodies; full article
body extraction requires sources with `row_one_article.enabled: true` and the
optional article extraction dependency. This does not change `row-one-app/v7`,
does not write a new json artifact, does not add source collection, does not add
scoring, and does not add llm calls. Use `--latest-only` when you want the
reported sidecar count to reflect only the current generated site.
```

Run the docs test.

Expected: PASS.

## Task 7: Verification, Review, Commit, Push

**Files:**
- Create: `docs/reviews/claude-code-stage-314-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-314-code-review.md`

- [ ] **Step 1: Run focused verification**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_site_metrics.py tests/test_row_one_cli.py tests/test_workflows.py tests/test_row_one_docs.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
```

- [ ] **Step 2: Run full verification**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one build --as-of 2026-07-06T04:00:00Z --output-dir reports/row-one/site --latest-only
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one status --site-dir reports/row-one/site --json
```

The status JSON may show zero local articles in the current local environment,
but it must include `local_articles`, `local_article_count`, and
`local_article_paragraph_count`.

- [ ] **Step 3: Request Claude Code review**

Use:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-314-code-review-prompt.md)"
```

Fix any Critical or Important findings and rereview.

- [ ] **Step 4: Commit and push**

```bash
git status --short --branch
git diff --check
git diff --cached --name-only -- uv.lock reports/row-one/site .codegraph
git diff --cached --check
git commit -m "Stage 314: add row one local article observability"
git push origin main
```

Do not stage `uv.lock`, generated site output, `.codegraph`, cookies, tokens, or local account data.

# Stage 315 ROW ONE Article Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a read-only ROW ONE article-readiness diagnostic so local operators and agents can see why saved local article sidecars are or are not generated.

**Architecture:** Add a pure analyzer module under `fashion_radar.row_one`, wire it into a new `row-one article-readiness` Typer subcommand, and document it as a preflight before relying on 04:00 daily refresh. The command reads source config and optional generated site files only; it does not collect, fetch, extract, score, mutate config, mutate SQLite, or change generated app contracts.

**Tech Stack:** Python dataclasses, Typer CLI, existing Pydantic config models, Stage 314 `RowOneLocalArticleSiteMetrics`, pytest, Ruff, existing docs/review workflow.

---

## Files

- Create: `src/fashion_radar/row_one/article_readiness.py`
- Create: `tests/test_row_one_article_readiness.py`
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_row_one_cli.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_config.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `docs/first-run.md`
- Modify: `tests/test_first_run_docs.py`
- Create: `docs/reviews/claude-code-stage-315-plan-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-315-plan-review.md`
- Later implementation review artifacts:
  - `docs/reviews/claude-code-stage-315-code-review-prompt.md`
  - `docs/reviews/claude-code-stage-315-code-review.md`

---

### Task 1: Read-Only Article Readiness Analyzer

**Files:**
- Create: `src/fashion_radar/row_one/article_readiness.py`
- Create: `tests/test_row_one_article_readiness.py`

- [ ] **Step 1: Add failing analyzer tests**

Create `tests/test_row_one_article_readiness.py` with these tests:

```python
from __future__ import annotations

from fashion_radar.models.source import SourceDefinition, SourceType
from fashion_radar.row_one.article_readiness import (
    build_row_one_article_readiness,
    row_one_article_readiness_payload,
)
from fashion_radar.row_one.site_metrics import RowOneLocalArticleSiteMetrics


def _rss_source(name: str, *, row_one_enabled: bool = False) -> SourceDefinition:
    slug = name.casefold().replace(" ", "-")
    return SourceDefinition(
        name=name,
        type=SourceType.RSS,
        url=f"https://{slug}.example/feed.xml",
        article={"enabled": False},
        row_one_article={"enabled": row_one_enabled, "max_chars": 2400},
    )


def _edition_payload(source_names: list[str]) -> dict[str, object]:
    return {
        "contract_version": "row-one-app/v7",
        "story_count": len(source_names),
        "stories": [
            {
                "id": f"story-{index}-1234567890",
                "source_name": source_name,
                "source_url": (
                    f"https://{source_name.casefold().replace(' ', '-')}.example/{index}"
                ),
            }
            for index, source_name in enumerate(source_names)
        ],
    }


def test_article_readiness_counts_article_enabled_sources_and_story_coverage() -> None:
    readiness = build_row_one_article_readiness(
        sources=[
            _rss_source("Fashionista", row_one_enabled=True),
            _rss_source("Legacy Fashion", row_one_enabled=False),
        ],
        edition_payload=_edition_payload(["Fashionista", "Legacy Fashion", "Unknown"]),
        local_article_metrics=RowOneLocalArticleSiteMetrics(
            article_count=1,
            paragraph_count=4,
            organized_section_count=2,
            source_count=1,
        ),
    )

    assert readiness.source_summary.total_sources == 2
    assert readiness.source_summary.enabled_sources == 2
    assert readiness.source_summary.article_enabled_sources == 1
    assert readiness.story_coverage.story_count == 3
    assert readiness.story_coverage.eligible_story_count == 1
    assert readiness.story_coverage.disabled_source_count == 1
    assert readiness.story_coverage.missing_source_count == 1
    assert not readiness.recommendations


def test_article_readiness_recommends_row_one_article_when_no_stories_are_eligible() -> None:
    readiness = build_row_one_article_readiness(
        sources=[_rss_source("Legacy Fashion", row_one_enabled=False)],
        edition_payload=_edition_payload(["Legacy Fashion"]),
        local_article_metrics=RowOneLocalArticleSiteMetrics(),
    )

    assert readiness.story_coverage.eligible_story_count == 0
    assert any("row_one_article.enabled: true" in item for item in readiness.recommendations)


def test_article_readiness_matches_enabled_source_by_story_url_host_when_name_differs() -> None:
    readiness = build_row_one_article_readiness(
        sources=[
            SourceDefinition(
                name="Fashionista",
                type=SourceType.RSS,
                url="https://shared.example/feed.xml",
                article={"enabled": False},
                row_one_article={"enabled": True, "max_chars": 2400},
            )
        ],
        edition_payload={
            "contract_version": "row-one-app/v7",
            "story_count": 1,
            "stories": [
                {
                    "id": "story-host-fallback-1234567890",
                    "source_name": "Historical Source",
                    "source_url": "https://shared.example/articles/the-row",
                }
            ],
        },
        local_article_metrics=RowOneLocalArticleSiteMetrics(),
    )

    assert readiness.story_coverage.story_count == 1
    assert readiness.story_coverage.eligible_story_count == 1
    assert readiness.story_coverage.disabled_source_count == 0
    assert readiness.story_coverage.missing_source_count == 0
    assert not readiness.recommendations


def test_article_readiness_payload_is_machine_readable() -> None:
    readiness = build_row_one_article_readiness(
        sources=[_rss_source("Fashionista", row_one_enabled=True)],
        edition_payload=None,
        local_article_metrics=RowOneLocalArticleSiteMetrics(),
    )

    assert row_one_article_readiness_payload(readiness) == {
        "source_summary": {
            "total_sources": 1,
            "enabled_sources": 1,
            "article_enabled_sources": 1,
        },
        "story_coverage": {
            "story_count": 0,
            "eligible_story_count": 0,
            "disabled_source_count": 0,
            "missing_source_count": 0,
        },
        "local_articles": {
            "article_count": 0,
            "paragraph_count": 0,
            "organized_section_count": 0,
            "source_count": 0,
        },
        "recommendations": [
            "Build or refresh ROW ONE before evaluating current story source coverage.",
        ],
    }
```

- [ ] **Step 2: Run analyzer tests and verify they fail**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_article_readiness.py -q
```

Expected: fail with `ModuleNotFoundError` for `fashion_radar.row_one.article_readiness`.

- [ ] **Step 3: Implement analyzer**

Create `src/fashion_radar/row_one/article_readiness.py`:

```python
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit

from fashion_radar.models.source import SourceDefinition
from fashion_radar.row_one.site_metrics import (
    RowOneLocalArticleSiteMetrics,
    row_one_local_article_site_metrics_payload,
)
from fashion_radar.row_one.utils import safe_external_url


@dataclass(frozen=True)
class RowOneArticleReadinessSourceSummary:
    total_sources: int = 0
    enabled_sources: int = 0
    article_enabled_sources: int = 0


@dataclass(frozen=True)
class RowOneArticleReadinessStoryCoverage:
    story_count: int = 0
    eligible_story_count: int = 0
    disabled_source_count: int = 0
    missing_source_count: int = 0


@dataclass(frozen=True)
class RowOneArticleReadiness:
    source_summary: RowOneArticleReadinessSourceSummary
    story_coverage: RowOneArticleReadinessStoryCoverage
    local_article_metrics: RowOneLocalArticleSiteMetrics
    recommendations: tuple[str, ...] = ()


def build_row_one_article_readiness(
    *,
    sources: Sequence[SourceDefinition],
    edition_payload: Mapping[str, Any] | None,
    local_article_metrics: RowOneLocalArticleSiteMetrics,
) -> RowOneArticleReadiness:
    source_summary = _source_summary(sources)
    story_coverage = _story_coverage(sources, edition_payload)
    return RowOneArticleReadiness(
        source_summary=source_summary,
        story_coverage=story_coverage,
        local_article_metrics=local_article_metrics,
        recommendations=_recommendations(source_summary, story_coverage),
    )


def row_one_article_readiness_payload(
    readiness: RowOneArticleReadiness,
) -> dict[str, object]:
    return {
        "source_summary": {
            "total_sources": readiness.source_summary.total_sources,
            "enabled_sources": readiness.source_summary.enabled_sources,
            "article_enabled_sources": readiness.source_summary.article_enabled_sources,
        },
        "story_coverage": {
            "story_count": readiness.story_coverage.story_count,
            "eligible_story_count": readiness.story_coverage.eligible_story_count,
            "disabled_source_count": readiness.story_coverage.disabled_source_count,
            "missing_source_count": readiness.story_coverage.missing_source_count,
        },
        "local_articles": row_one_local_article_site_metrics_payload(
            readiness.local_article_metrics
        ),
        "recommendations": list(readiness.recommendations),
    }


def _source_summary(
    sources: Sequence[SourceDefinition],
) -> RowOneArticleReadinessSourceSummary:
    enabled_sources = [source for source in sources if source.enabled]
    return RowOneArticleReadinessSourceSummary(
        total_sources=len(sources),
        enabled_sources=len(enabled_sources),
        article_enabled_sources=sum(
            1 for source in enabled_sources if source.row_one_article.enabled
        ),
    )


def _story_coverage(
    sources: Sequence[SourceDefinition],
    edition_payload: Mapping[str, Any] | None,
) -> RowOneArticleReadinessStoryCoverage:
    if edition_payload is None:
        return RowOneArticleReadinessStoryCoverage()
    raw_stories = edition_payload.get("stories")
    if not isinstance(raw_stories, list):
        return RowOneArticleReadinessStoryCoverage()
    source_by_name = {source.name: source for source in sources if source.enabled}
    eligible_story_count = 0
    disabled_source_count = 0
    missing_source_count = 0
    story_count = 0
    for story in raw_stories:
        if not isinstance(story, Mapping):
            continue
        story_count += 1
        source_name = story.get("source_name")
        if not isinstance(source_name, str) or not source_name.strip():
            missing_source_count += 1
            continue
        source = source_by_name.get(source_name)
        if source is None:
            source = _source_by_story_url_host(story, sources)
        if source is None:
            missing_source_count += 1
            continue
        if source.row_one_article.enabled:
            eligible_story_count += 1
        else:
            disabled_source_count += 1
    return RowOneArticleReadinessStoryCoverage(
        story_count=story_count,
        eligible_story_count=eligible_story_count,
        disabled_source_count=disabled_source_count,
        missing_source_count=missing_source_count,
    )


def _source_by_story_url_host(
    story: Mapping[str, Any],
    sources: Sequence[SourceDefinition],
) -> SourceDefinition | None:
    story_url = story.get("source_url")
    story_host = _hostname(safe_external_url(story_url if isinstance(story_url, str) else None))
    if story_host is None:
        return None
    for source in sources:
        if not source.enabled:
            continue
        source_hosts = {_hostname(url) for url in [source.url, *source.seed_urls] if url}
        if story_host in source_hosts:
            return source
    return None


def _hostname(url: str | None) -> str | None:
    if url is None:
        return None
    parsed = urlsplit(url)
    return parsed.hostname.casefold() if parsed.hostname else None


def _recommendations(
    source_summary: RowOneArticleReadinessSourceSummary,
    story_coverage: RowOneArticleReadinessStoryCoverage,
) -> tuple[str, ...]:
    recommendations: list[str] = []
    if story_coverage.story_count == 0:
        recommendations.append(
            "Build or refresh ROW ONE before evaluating current story source coverage."
        )
    if source_summary.article_enabled_sources == 0:
        recommendations.append(
            "Enable row_one_article.enabled: true on sources that should produce ROW ONE local article sidecars."
        )
    elif story_coverage.story_count > 0 and story_coverage.eligible_story_count == 0:
        recommendations.append(
            "Current ROW ONE stories come from sources without row_one_article.enabled: true."
        )
    return tuple(recommendations)
```

- [ ] **Step 4: Run analyzer tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_article_readiness.py -q
```

Expected: pass.

---

### Task 2: CLI Command

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_row_one_cli.py`

- [ ] **Step 1: Add failing CLI tests**

In `tests/test_row_one_cli.py`, add tests near existing ROW ONE status tests:

```python
def test_row_one_article_readiness_prints_config_and_site_counts(tmp_path: Path) -> None:
    config_dir = tmp_path / "configs"
    output_dir = tmp_path / "site"
    _write_minimal_config(config_dir)
    _render_status_site_with_local_article(output_dir)

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "article-readiness",
            "--config-dir",
            str(config_dir),
            "--site-dir",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "ROW ONE article readiness" in result.output
    assert f"Config: {config_dir}" in result.output
    assert f"Site: {output_dir}" in result.output
    assert "ROW ONE article-enabled sources: 0" in result.output
    assert "Saved local articles: 1" in result.output
    assert "Saved local paragraphs: 2" in result.output
    assert "Story source coverage: 0/1 eligible" in result.output
    assert "row_one_article.enabled: true" in result.output


def test_row_one_article_readiness_json_is_machine_readable(tmp_path: Path) -> None:
    config_dir = tmp_path / "configs"
    output_dir = tmp_path / "site"
    _write_minimal_config(config_dir)
    _render_status_site_with_local_article(output_dir)

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "article-readiness",
            "--config-dir",
            str(config_dir),
            "--site-dir",
            str(output_dir),
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["config_dir"] == str(config_dir)
    assert payload["site_dir"] == str(output_dir)
    assert payload["local_articles"]["article_count"] == 1
    assert payload["local_articles"]["paragraph_count"] == 2
    assert payload["story_coverage"]["story_count"] == 1
    assert payload["story_coverage"]["eligible_story_count"] == 0
    assert payload["recommendations"]
```

- [ ] **Step 2: Run CLI tests and verify they fail**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_cli.py::test_row_one_article_readiness_prints_config_and_site_counts \
  tests/test_row_one_cli.py::test_row_one_article_readiness_json_is_machine_readable -q
```

Expected: fail because `article-readiness` command is not registered.

- [ ] **Step 3: Implement CLI command**

In `src/fashion_radar/cli.py`, import:

```python
from fashion_radar.row_one.article_readiness import (
    build_row_one_article_readiness,
    row_one_article_readiness_payload,
)
```

Add helper near ROW ONE status helpers:

```python
def _load_row_one_edition_payload_if_present(site_dir: Path) -> dict[str, object] | None:
    edition_path = site_dir / "data" / "edition.json"
    if not edition_path.exists():
        return None
    try:
        payload = json.loads(edition_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None
```

Add command before `local-ops`:

```python
@row_one_app.command(name="article-readiness")
def row_one_article_readiness(
    config_dir: Path = CONFIG_DIR_OPTION,
    site_dir: Path = ROW_ONE_OUTPUT_DIR_OPTION,
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Print machine-readable JSON readiness payload.",
    ),
) -> None:
    """Inspect ROW ONE local article sidecar readiness without fetching anything."""
    try:
        source_config = load_source_config(config_dir / "sources.yaml")
        metrics = build_row_one_local_article_site_metrics(site_dir)
        readiness = build_row_one_article_readiness(
            sources=source_config.sources,
            edition_payload=_load_row_one_edition_payload_if_present(site_dir),
            local_article_metrics=metrics,
        )
    except ConfigError as exc:
        typer.echo(f"Invalid config: {exc}", err=True)
        raise typer.Exit(1) from exc
    except Exception as exc:
        typer.echo(f"ROW ONE article readiness failed: {exc}", err=True)
        raise typer.Exit(1) from exc

    payload = row_one_article_readiness_payload(readiness)
    payload["config_dir"] = str(config_dir)
    payload["site_dir"] = str(site_dir)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    source_summary = payload["source_summary"]
    story_coverage = payload["story_coverage"]
    local_articles = payload["local_articles"]
    typer.echo("ROW ONE article readiness")
    typer.echo(f"Config: {config_dir}")
    typer.echo(f"Site: {site_dir}")
    typer.echo(
        "Sources: "
        f"{source_summary['enabled_sources']}/{source_summary['total_sources']} enabled"
    )
    typer.echo(
        "ROW ONE article-enabled sources: "
        f"{source_summary['article_enabled_sources']}"
    )
    typer.echo(f"Saved local articles: {local_articles['article_count']}")
    typer.echo(f"Saved local paragraphs: {local_articles['paragraph_count']}")
    typer.echo(
        "Story source coverage: "
        f"{story_coverage['eligible_story_count']}/{story_coverage['story_count']} eligible"
    )
    for recommendation in payload["recommendations"]:
        typer.echo(f"Recommendation: {recommendation}")
```

- [ ] **Step 4: Run CLI tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_cli.py::test_row_one_article_readiness_prints_config_and_site_counts \
  tests/test_row_one_cli.py::test_row_one_article_readiness_json_is_machine_readable -q
```

Expected: pass.

---

### Task 3: Config and Docs Guards

**Files:**
- Modify: `tests/test_config.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `docs/first-run.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_first_run_docs.py`

- [ ] **Step 1: Add config guard tests**

In `tests/test_config.py`, add assertions to
`test_starter_source_config_covers_core_fashion_signals_without_article_fetching`:

```python
    assert any(source.row_one_article.enabled for source in enabled_sources)
    assert all(
        source.row_one_article.enabled
        for source in enabled_sources
        if source.type.value == "rss"
    )
```

Add a separate test:

```python
def test_packaged_starter_sources_match_repo_starter_sources() -> None:
    assert Path("configs/sources.example.yaml").read_text(
        encoding="utf-8"
    ) == Path("src/fashion_radar/templates/configs/sources.example.yaml").read_text(
        encoding="utf-8"
    )
```

- [ ] **Step 2: Update docs tests**

In `tests/test_row_one_docs.py`, update `test_row_one_docs_include_user_required_phrases` to require:

```python
"row-one article-readiness",
"article readiness",
"row_one_article.enabled: true",
"saved local articles",
"saved local paragraphs",
"older platformdirs config",
```

Also update `test_row_one_docs_describe_local_article_observability_boundary`
so the Stage 314 slice ends at the newly inserted Stage 315 paragraph:

```python
    readme_stage_314 = readme[
        readme.index("Stage 314 adds local article observability") : readme.index("Stage 315 adds")
    ]
    docs_stage_314 = docs[
        docs.index("Stage 314 adds local article observability") : docs.index("Stage 315 adds")
    ]
```

Then add this separate Stage 315 guard. The current README and row-one docs
order is Stage 314 followed by Stage 310, so Stage 315 must be inserted between
those two paragraphs and sliced from Stage 315 to Stage 310:

```python
def test_row_one_docs_describe_article_readiness_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "row-one.md").read_text(encoding="utf-8")
    readme_stage_315 = readme[
        readme.index("Stage 315 adds ROW ONE article readiness diagnostics") : readme.index("Stage 310 adds")
    ]
    docs_stage_315 = docs[
        docs.index("Stage 315 adds ROW ONE article readiness diagnostics") : docs.index("Stage 310 adds")
    ]
    readme_stage_315_normalized = _normalized(readme_stage_315)
    docs_stage_315_normalized = _normalized(docs_stage_315)

    expected_phrases = [
        "row one article readiness diagnostics",
        "`row-one article-readiness`",
        "selected `sources.yaml`",
        "saved local article sidecars",
        "saved local paragraphs",
        "current story source coverage",
        "older platformdirs config",
        "`row_one_article.enabled: true`",
        "does not change `row-one-app/v7`",
        "does not write a new generated json artifact",
        "does not add source collection",
        "does not fetch article pages",
        "does not add scoring",
        "does not add llm calls",
    ]
    for phrase in expected_phrases:
        assert phrase in readme_stage_315_normalized
        assert phrase in docs_stage_315_normalized

    forbidden_phrases = [
        "row-one-app/v8",
        "row-one-manifest/v2",
        "row-one-runtime/v2",
        "changes schemas",
        "changes detail routes",
        "adds source collection",
        "adds scoring",
        "adds llm calls",
        "adds social connectors",
        "adds community connectors",
        "adds compliance review",
        "adds compliance-review",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in readme_stage_315_normalized
        assert phrase not in docs_stage_315_normalized
```

In `tests/test_first_run_docs.py`, add a docs guard that requires:

```python
"row-one article-readiness",
"deterministic first-run smoke",
"does not require saved article sidecars",
"row_one_article.enabled: true",
"optional article extraction dependency",
```

- [ ] **Step 3: Update README, row-one docs, and first-run docs**

Add a Stage 315 paragraph after Stage 314 in both `README.md` and
`docs/row-one.md`:

```md
Stage 315 adds ROW ONE article readiness diagnostics: `row-one article-readiness`
checks the selected `sources.yaml`, the generated ROW ONE site, saved local
article sidecars, saved local paragraphs, and current story source coverage
without collecting sources, fetching article pages, mutating SQLite, changing
`row-one-app/v7`, or writing a new generated JSON artifact. It does not change
`row-one-app/v7`, does not write a new generated JSON artifact, does not add
source collection, does not fetch article pages, does not add scoring, and does
not add llm calls. Use it when `row-one build` reports zero saved local
articles; older platformdirs config directories may still contain source packs
without `row_one_article.enabled: true`, while the current starter config can
produce saved local article sidecars when matching stories exist.
```

In `docs/first-run.md`, add a short paragraph near the ROW ONE smoke guidance:

```md
The deterministic first-run smoke keeps live sources empty, so it does not
require saved article sidecars. For live daily ROW ONE use, run
`row-one article-readiness` against your real `--config-dir` and generated
`--site-dir`; source configs need `row_one_article.enabled: true`, and full
article body extraction uses the optional article extraction dependency.
```

- [ ] **Step 4: Run focused config/docs tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_config.py \
  tests/test_row_one_docs.py \
  tests/test_first_run_docs.py -q
```

Expected: pass.

---

### Task 4: Review, Full Verification, and Push

**Files:**
- Create: `docs/reviews/claude-code-stage-315-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-315-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_article_readiness.py \
  tests/test_row_one_cli.py \
  tests/test_row_one_docs.py \
  tests/test_first_run_docs.py \
  tests/test_config.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
```

Expected: pass.

- [ ] **Step 2: Run smoke commands**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one article-readiness \
  --config-dir configs \
  --site-dir reports/row-one/site

UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one article-readiness \
  --config-dir "$HOME/.config/fashion-radar" \
  --site-dir reports/row-one/site
```

Expected: first command reports article-enabled starter sources; second command may report zero article-enabled sources and should print a recommendation instead of failing.

- [ ] **Step 3: Request Claude Code review**

Create `docs/reviews/claude-code-stage-315-code-review-prompt.md` with the stage goal, files changed, verification commands, and explicit review questions:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-315-code-review-prompt.md)" \
  > docs/reviews/claude-code-stage-315-code-review.md
```

Fix any Critical or Important findings and rerun focused verification.

- [ ] **Step 4: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
```

Expected: pass.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short --branch
git diff --check
git add \
  src/fashion_radar/row_one/article_readiness.py \
  src/fashion_radar/cli.py \
  tests/test_row_one_article_readiness.py \
  tests/test_row_one_cli.py \
  tests/test_config.py \
  tests/test_row_one_docs.py \
  tests/test_first_run_docs.py \
  README.md \
  docs/row-one.md \
  docs/first-run.md \
  docs/reviews/claude-code-stage-315-code-review-prompt.md \
  docs/reviews/claude-code-stage-315-code-review.md
git diff --cached --name-only -- uv.lock reports/row-one/site .codegraph
git diff --cached --check
git commit -m "Stage 315: add row one article readiness diagnostics"
git push origin main
```

Expected: no `uv.lock`, generated site, `.codegraph`, cookies, or tokens staged.

---

## Plan Self-Review

- Spec coverage: covers analyzer, CLI, JSON, docs, config guard, review, and verification.
- Placeholder scan: no TBD/TODO/fill-in-later text remains.
- Type consistency: plan uses existing `SourceDefinition`, `RowOneLocalArticleSiteMetrics`, and `load_source_config`.
- Scope check: no config auto-migration, no new extraction logic, and no generated app contract changes.

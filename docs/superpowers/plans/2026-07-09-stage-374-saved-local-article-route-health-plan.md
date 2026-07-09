# Stage 374 Saved Local Article Route Health Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. REQUIRED PROJECT GATE: submit this plan for Claude Code review with `--effort max` before implementation; after Claude Code's plan review, run local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar`.

**Goal:** Add read-only Saved Local Article Route Health so ROW ONE detects when saved local article sidecars exist but `articles/index.html` or `articles/<story-id>.html` is missing or unlinked.

**Architecture:** Add one pure analyzer module that checks existing generated site files and returns a small dataclass/payload. Integrate it into strict `row-one status` validation by returning the validated route-health object from `validate_row_one_generated_site_integrity(...)`, and integrate the same analyzer into read-only `row-one ops-check` diagnostics without changing generated app/runtime/manifest JSON contracts or rendering new page sections.

**Tech Stack:** Python 3, dataclasses, pathlib, existing ROW ONE safety helper `safe_local_article_story_id`, Typer CLI, pytest, ruff, uv with `UV_NO_CONFIG=1 uv --no-config`.

---

## File Structure

- Create `src/fashion_radar/row_one/local_article_route_health.py`
  - Owns `RowOneLocalArticleRouteHealth`, analyzer, payload conversion, and strict validator.
- Create `tests/test_row_one_local_article_route_health.py`
  - Analyzer and validator tests.
- Modify `src/fashion_radar/row_one/status_integrity.py`
  - Calls the strict validator after current sidecars are already validated.
- Modify `src/fashion_radar/cli.py`
  - Adds CLI-only `local_article_routes` status payload and human output line.
  - Adds ops-check human output line.
- Modify `src/fashion_radar/row_one/ops_check.py`
  - Adds read-only route health payload, status influence, and refresh action.
- Modify `tests/test_row_one_cli.py`
  - Adds status JSON and strict-failure tests.
- Modify `tests/test_row_one_ops_check.py`
  - Adds ops-check JSON/status/action/human output coverage.
- Modify `README.md` and `docs/row-one.md`
  - Adds exact Stage 374 boundary paragraph before Stage 373.
- Modify `tests/test_row_one_docs.py`
  - Adds exact Stage 374 paragraph and stale phrase guard.
- Modify `tests/test_workflows.py`
  - Adds app-contract denylist, artifact denylist, and generated-site-only read-only guard.
- Add review artifacts under `docs/reviews/`
  - `claude-code-stage-374-plan-review.md`
  - `opencode-stage-374-plan-review.md`
  - `claude-code-stage-374-code-review.md`
  - `opencode-stage-374-code-review.md`

## Core Product Gap Closed

Earlier stages already organize saved local article content visually. Stage 374 closes a more basic access gap: it ensures already-saved local article bodies are actually reachable through generated same-site article routes before the site is reported healthy.

## Parallel Execution Shape After Plan Review

Use parallel workers only with disjoint write scopes:

- Worker A: `src/fashion_radar/row_one/local_article_route_health.py` and `tests/test_row_one_local_article_route_health.py`.
- Worker B: `src/fashion_radar/row_one/status_integrity.py`, `src/fashion_radar/cli.py`, `tests/test_row_one_cli.py`.
- Worker C: `src/fashion_radar/row_one/ops_check.py`, `tests/test_row_one_ops_check.py`.
- Worker D: `README.md`, `docs/row-one.md`, `tests/test_row_one_docs.py`, `tests/test_workflows.py`.

Workers are not alone in the codebase. They must not revert edits made by others, and they must adjust to existing changes when integrating.

---

### Task 1: Plan Review Gate

**Files:**
- Create: `docs/reviews/claude-code-stage-374-plan-review.md`
- Create: `docs/reviews/opencode-stage-374-plan-review.md`

- [ ] **Step 1: Request Claude Code plan review**

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Review Stage 374 Saved Local Article Route Health plan/spec in /home/ubuntu/fashion-radar. Read docs/superpowers/specs/2026-07-09-stage-374-saved-local-article-route-health-design.md and docs/superpowers/plans/2026-07-09-stage-374-saved-local-article-route-health-plan.md. Goal: detect generated ROW ONE sites where saved local article sidecars exist but articles/index.html, articles/<story-id>.html, or same-site links to them are missing. Technical stack: Python dataclasses, pathlib, existing ROW ONE safe story-id helper, Typer CLI, pytest, ruff, uv. Implementation method: pure read-only route health analyzer, strict status_integrity validation, CLI-only row-one status --json local_article_routes field, ops-check diagnostic field/action, no generated JSON artifacts or app/runtime/manifest contract changes. Check feasibility, route/link correctness, read-only behavior, generated-site-only boundaries, app-contract/artifact leakage risk, duplication with existing local article stages, and test plan. Return findings only, ordered by Critical, Important, Minor." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-374-plan-review.md
rm -f "$tmp_review"
```

Expected: review is saved and contains no live-capture/tool chatter.

- [ ] **Step 2: Request opencode plan review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Review Stage 374 Saved Local Article Route Health plan/spec in /home/ubuntu/fashion-radar. Read docs/superpowers/specs/2026-07-09-stage-374-saved-local-article-route-health-design.md and docs/superpowers/plans/2026-07-09-stage-374-saved-local-article-route-health-plan.md. Also read docs/reviews/claude-code-stage-374-plan-review.md if present and cross-check it. Goal: detect generated ROW ONE sites where saved local article sidecars exist but articles/index.html, articles/<story-id>.html, or same-site links to them are missing. Technical stack: Python dataclasses, pathlib, existing ROW ONE safe story-id helper, Typer CLI, pytest, ruff, uv. Implementation method: pure read-only route health analyzer, strict status_integrity validation, CLI-only row-one status --json local_article_routes field, ops-check diagnostic field/action, no generated JSON artifacts or app/runtime/manifest contract changes. Return findings only, ordered by Critical, Important, Minor." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-374-plan-review.md
rm -f "$tmp_review"
```

Expected: review is saved and contains no live-capture/tool chatter.

- [ ] **Step 3: Fix valid Critical and Important plan findings**

If either review raises Critical or Important issues, update the spec/plan before implementation and run a matching re-review. Do not edit production code until this gate passes.

### Task 2: Analyzer RED Tests

**Files:**
- Create: `tests/test_row_one_local_article_route_health.py`

- [ ] **Step 1: Write failing analyzer tests**

Create tests that import the not-yet-created module:

```python
from fashion_radar.row_one.local_article_route_health import (
    RowOneLocalArticleRouteHealth,
    build_row_one_local_article_route_health,
    row_one_local_article_route_health_payload,
    validate_row_one_local_article_route_health,
)
```

Use helpers:

```python
def _write_base_site(site_dir: Path) -> None:
    site_dir.mkdir(parents=True)
    (site_dir / "index.html").write_text(
        '<a href="articles/index.html">Saved article library</a>',
        encoding="utf-8",
    )


def _write_article_sidecar(site_dir: Path, story_id: str) -> None:
    articles_dir = site_dir / "data" / "articles"
    articles_dir.mkdir(parents=True, exist_ok=True)
    (articles_dir / f"{story_id}.json").write_text("{}", encoding="utf-8")


def _write_article_routes(site_dir: Path, story_id: str) -> None:
    articles_dir = site_dir / "articles"
    articles_dir.mkdir(parents=True, exist_ok=True)
    (articles_dir / "index.html").write_text(
        f'<a href="{story_id}.html">Read local article</a>',
        encoding="utf-8",
    )
    (articles_dir / f"{story_id}.html").write_text(
        "<!doctype html><title>ROW ONE article</title>",
        encoding="utf-8",
    )
```

Required test names:

- `test_route_health_is_not_applicable_without_saved_article_sidecars`
- `test_route_health_reports_ready_for_linked_library_and_article_pages`
- `test_route_health_reports_missing_library_route`
- `test_route_health_reports_missing_homepage_library_link`
- `test_route_health_reports_missing_article_pages_and_library_links_deterministically`
- `test_route_health_uses_supplied_story_ids_exactly`
- `test_route_health_payload_is_stable`
- `test_validate_route_health_raises_clear_errors`
- `test_route_health_discovery_ignores_unsafe_sidecar_stems`

Key expectations:

```python
health = build_row_one_local_article_route_health(site_dir)
assert health.status == "ready"
assert health.article_count == 1
assert health.library_path == "articles/index.html"
assert health.library_present is True
assert health.homepage_library_link_present is True
assert health.missing_article_pages == ()
assert health.missing_library_links == ()
```

Validator failure checks must assert all four clear error branches:

```python
with pytest.raises(ValueError, match="articles/index.html"):
    validate_row_one_local_article_route_health(missing_library_health)
with pytest.raises(ValueError, match="library link is missing from index.html"):
    validate_row_one_local_article_route_health(missing_homepage_link_health)
with pytest.raises(ValueError, match="local article route is missing: articles/"):
    validate_row_one_local_article_route_health(missing_article_page_health)
with pytest.raises(ValueError, match="library page is missing article link"):
    validate_row_one_local_article_route_health(missing_library_link_health)
```

- [ ] **Step 2: Run analyzer tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_local_article_route_health.py -q
```

Expected: fail with `ModuleNotFoundError: No module named 'fashion_radar.row_one.local_article_route_health'`.

### Task 3: Analyzer Implementation

**Files:**
- Create: `src/fashion_radar/row_one/local_article_route_health.py`
- Test: `tests/test_row_one_local_article_route_health.py`

- [ ] **Step 1: Implement dataclass, discovery, analyzer, payload, and validator**

Implement:

```python
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from fashion_radar.row_one.articles import safe_local_article_story_id

LOCAL_ARTICLE_LIBRARY_PATH = "articles/index.html"


@dataclass(frozen=True)
class RowOneLocalArticleRouteHealth:
    status: str
    article_count: int
    library_path: str
    library_present: bool
    homepage_library_link_present: bool
    missing_article_pages: tuple[str, ...]
    missing_library_links: tuple[str, ...]


def build_row_one_local_article_route_health(
    site_dir: Path,
    story_ids: Iterable[str] | None = None,
) -> RowOneLocalArticleRouteHealth:
    resolved_story_ids = _resolve_story_ids(site_dir, story_ids)
    if not resolved_story_ids:
        return RowOneLocalArticleRouteHealth(
            status="not_applicable",
            article_count=0,
            library_path=LOCAL_ARTICLE_LIBRARY_PATH,
            library_present=False,
            homepage_library_link_present=False,
            missing_article_pages=(),
            missing_library_links=(),
        )
    library_present = (site_dir / LOCAL_ARTICLE_LIBRARY_PATH).is_file()
    homepage_library_link_present = _html_contains_href(
        site_dir / "index.html",
        LOCAL_ARTICLE_LIBRARY_PATH,
    )
    missing_article_pages = tuple(
        f"articles/{story_id}.html"
        for story_id in resolved_story_ids
        if not (site_dir / "articles" / f"{story_id}.html").is_file()
    )
    missing_library_links = (
        tuple(
            f"{story_id}.html"
            for story_id in resolved_story_ids
            if not _html_contains_href(site_dir / LOCAL_ARTICLE_LIBRARY_PATH, f"{story_id}.html")
        )
        if library_present
        else ()
    )
    status = (
        "ready"
        if library_present
        and homepage_library_link_present
        and not missing_article_pages
        and not missing_library_links
        else "missing"
    )
    return RowOneLocalArticleRouteHealth(
        status=status,
        article_count=len(resolved_story_ids),
        library_path=LOCAL_ARTICLE_LIBRARY_PATH,
        library_present=library_present,
        homepage_library_link_present=homepage_library_link_present,
        missing_article_pages=missing_article_pages,
        missing_library_links=missing_library_links,
    )
```

Implement helpers:

```python
def _resolve_story_ids(site_dir: Path, story_ids: Iterable[str] | None) -> tuple[str, ...]:
    if story_ids is None:
        articles_dir = site_dir / "data" / "articles"
        if not articles_dir.is_dir():
            return ()
        return tuple(
            sorted(
                {
                    path.stem
                    for path in articles_dir.glob("*.json")
                    if safe_local_article_story_id(path.stem)
                }
            )
        )
    # Wrap a bare string so a single story-id is not iterated character by character.
    candidates = (story_ids,) if isinstance(story_ids, str) else story_ids
    # Strict callers pass story ids already validated from sidecars; this defensive
    # filter keeps the public analyzer safe for direct use.
    safe_ids = {
        story_id
        for story_id in candidates
        if safe_local_article_story_id(story_id)
    }
    return tuple(sorted(safe_ids))


def _html_contains_href(path: Path, href: str) -> bool:
    try:
        html = path.read_text(encoding="utf-8")
    except OSError:
        return False
    # Generated ROW ONE HTML uses double-quoted attributes; single quotes are a
    # defensive fallback for hand-edited generated sites.
    return f'href="{href}"' in html or f"href='{href}'" in html
```

Implement payload:

```python
def row_one_local_article_route_health_payload(
    health: RowOneLocalArticleRouteHealth,
) -> dict[str, object]:
    return {
        "status": health.status,
        "article_count": health.article_count,
        "library_path": health.library_path,
        "library_present": health.library_present,
        "homepage_library_link_present": health.homepage_library_link_present,
        "missing_article_pages": list(health.missing_article_pages),
        "missing_library_links": list(health.missing_library_links),
    }
```

Implement validator:

```python
def validate_row_one_local_article_route_health(
    health: RowOneLocalArticleRouteHealth,
) -> None:
    if health.status in {"ready", "not_applicable"}:
        return
    if not health.library_present:
        raise ValueError(f"row-one local article library route is missing: {health.library_path}")
    if not health.homepage_library_link_present:
        raise ValueError(
            "row-one local article library link is missing from index.html: "
            f"{health.library_path}"
        )
    if health.missing_article_pages:
        raise ValueError(
            "row-one local article route is missing: "
            f"{health.missing_article_pages[0]}"
        )
    if health.missing_library_links:
        raise ValueError(
            "row-one local article library page is missing article link: "
            f"{health.missing_library_links[0]}"
        )
    raise ValueError("row-one local article route health is missing")
```

- [ ] **Step 2: Run analyzer tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_local_article_route_health.py -q
```

Expected: all analyzer tests pass.

### Task 4: Status Integration With RED/GREEN Tests

**Files:**
- Modify: `src/fashion_radar/row_one/status_integrity.py`
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_row_one_cli.py`

- [ ] **Step 1: Add failing status tests**

In `tests/test_row_one_cli.py`, add tests near existing local article status tests:

```python
def test_row_one_status_json_includes_local_article_route_health(tmp_path: Path) -> None:
    story = _render_status_site_with_local_article(tmp_path)
    assert (tmp_path / "articles" / "index.html").is_file()
    assert (tmp_path / "articles" / f"{story['id']}.html").is_file()
    assert 'href="articles/index.html"' in (tmp_path / "index.html").read_text(
        encoding="utf-8"
    )
    assert f'href="{story["id"]}.html"' in (
        tmp_path / "articles" / "index.html"
    ).read_text(encoding="utf-8")

    result = CliRunner().invoke(
        app,
        ["row-one", "status", "--site-dir", str(tmp_path), "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["local_article_routes"] == {
        "status": "ready",
        "article_count": 1,
        "library_path": "articles/index.html",
        "library_present": True,
        "homepage_library_link_present": True,
        "missing_article_pages": [],
        "missing_library_links": [],
    }

def test_row_one_status_prints_local_article_route_health(tmp_path: Path) -> None:
    story = _render_status_site_with_local_article(tmp_path)
    assert (tmp_path / "articles" / "index.html").is_file()
    assert (tmp_path / "articles" / f"{story['id']}.html").is_file()

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert "Local article routes: ready (1 saved local article)" in result.output
```

Add strict failure tests:

```python
def test_row_one_status_rejects_missing_saved_article_library_route(tmp_path: Path) -> None:
    _render_status_site_with_local_article(tmp_path)
    (tmp_path / "articles" / "index.html").unlink()

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "articles/index.html" in result.output


def test_row_one_status_rejects_missing_saved_article_page_route(tmp_path: Path) -> None:
    story = _render_status_site_with_local_article(tmp_path)
    (tmp_path / "articles" / f"{story['id']}.html").unlink()

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert f"articles/{story['id']}.html" in result.output


def test_row_one_status_rejects_missing_homepage_saved_article_library_link(
    tmp_path: Path,
) -> None:
    _render_status_site_with_local_article(tmp_path)
    index_path = tmp_path / "index.html"
    index_path.write_text(
        index_path.read_text(encoding="utf-8").replace(
            'href="articles/index.html"',
            'href="details/index.html"',
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "library link is missing from index.html" in result.output


def test_row_one_status_rejects_missing_saved_article_library_page_link(
    tmp_path: Path,
) -> None:
    story = _render_status_site_with_local_article(tmp_path)
    library_path = tmp_path / "articles" / "index.html"
    library_path.write_text(
        library_path.read_text(encoding="utf-8").replace(
            f'href="{story["id"]}.html"',
            'href="missing.html"',
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert f"{story['id']}.html" in result.output
```

- [ ] **Step 2: Run status tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py -q -k "local_article_route or saved_article_library_route or saved_article_page_route or homepage_saved_article_library_link or saved_article_library_page_link"
```

Expected: new tests fail because `local_article_routes` is absent and strict route validation is not wired.

- [ ] **Step 3: Implement status integration**

In `status_integrity.py`, import:

```python
from fashion_radar.row_one.local_article_route_health import (
    RowOneLocalArticleRouteHealth,
    build_row_one_local_article_route_health,
    validate_row_one_local_article_route_health,
)
```

Update the function signature to return the validated route health:

```python
def validate_row_one_generated_site_integrity(
    *,
    site_dir: Path,
    edition: dict[str, object],
) -> RowOneLocalArticleRouteHealth:
```

After `_load_article_sidecars(...)`, build and validate route health, keep the existing `_validate_local_intelligence(...)` call, then return the same route-health object that strict validation used:

```python
    route_health = build_row_one_local_article_route_health(
        site_dir,
        story_ids=article_sidecars.keys(),
    )
    validate_row_one_local_article_route_health(route_health)
    _validate_local_intelligence(
        site_dir=site_dir,
        detail_to_story_id=detail_to_story_id,
        article_sidecars=article_sidecars,
    )
    return route_health
```

In `cli.py`, import:

```python
from fashion_radar.row_one.local_article_route_health import (
    RowOneLocalArticleRouteHealth,
    row_one_local_article_route_health_payload,
)
```

Add a keyword-only argument to `_build_row_one_status_payload(...)`:

```python
def _build_row_one_status_payload(
    *,
    site_dir: Path,
    host: str,
    port: int,
    manifest: dict[str, object],
    edition: dict[str, object],
    runtime: dict[str, object],
    local_article_route_health: RowOneLocalArticleRouteHealth,
) -> dict[str, object]:
```

Add to returned payload:

```python
        "local_article_routes": row_one_local_article_route_health_payload(
            local_article_route_health
        ),
```

In `row_one_status(...)`, store the strict validator return value:

```python
        local_article_route_health = validate_row_one_generated_site_integrity(
            site_dir=site_dir,
            edition=edition,
        )
```

Then pass it to the payload builder:

```python
    payload = _build_row_one_status_payload(
        site_dir=site_dir,
        host=host,
        port=port,
        manifest=manifest,
        edition=edition,
        runtime=runtime,
        local_article_route_health=local_article_route_health,
    )
```

In `row_one_status(...)` human output:

```python
    local_article_routes = payload["local_article_routes"]
    if isinstance(local_article_routes, dict):
        route_status = local_article_routes.get("status", "unknown")
        route_count = local_article_routes.get("article_count", 0)
        suffix = "saved local article" if route_count == 1 else "saved local articles"
        typer.echo(f"Local article routes: {route_status} ({route_count} {suffix})")
```

- [ ] **Step 4: Run status tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py -q -k "local_article_route or saved_article_library_route or saved_article_page_route or homepage_saved_article_library_link or saved_article_library_page_link"
```

Expected: selected status tests pass.

### Task 5: Ops-Check Integration With RED/GREEN Tests

**Files:**
- Modify: `src/fashion_radar/row_one/ops_check.py`
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_row_one_ops_check.py`
- Modify: `tests/test_row_one_cli.py`

- [ ] **Step 1: Add failing ops-check tests**

In `tests/test_row_one_ops_check.py`, add:

```python
def _write_saved_article_route_fixture(site_dir: Path, *, complete: bool = True) -> None:
    _write_site(site_dir, edition_date="2026-07-07T04:00:00Z")
    story_id = "the-row-route-1234567890"
    articles_data = site_dir / "data" / "articles"
    articles_data.mkdir(parents=True, exist_ok=True)
    (articles_data / f"{story_id}.json").write_text("{}", encoding="utf-8")
    if complete:
        (site_dir / "index.html").write_text(
            '<h1>ROW ONE</h1><a href="articles/index.html">Saved article library</a>',
            encoding="utf-8",
        )
        articles_dir = site_dir / "articles"
        articles_dir.mkdir(parents=True, exist_ok=True)
        (articles_dir / "index.html").write_text(
            f'<a href="{story_id}.html">Read local article</a>',
            encoding="utf-8",
        )
        (articles_dir / f"{story_id}.html").write_text(
            "<!doctype html><title>ROW ONE local article</title>",
            encoding="utf-8",
        )
```

Add:

```python
def test_ops_check_reports_local_article_route_health_ready(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    unit_dir = tmp_path / "units"
    _write_saved_article_route_fixture(site_dir, complete=True)
    unit_dir.mkdir()
    for unit in ROW_ONE_SYSTEMD_UNITS:
        (unit_dir / unit).write_text("[Unit]\n", encoding="utf-8")

    payload = build_row_one_ops_check_payload(
        site_dir=site_dir,
        host="127.0.0.1",
        port=8787,
        unit_dir=unit_dir,
        as_of=datetime(2026, 7, 7, 8, 0, tzinfo=UTC),
        server_probe=lambda host, port, timeout: _probe("serving_row_one"),
    )

    assert payload["status"] == "ready"
    assert payload["local_article_routes"]["status"] == "ready"
    assert payload["local_article_routes"]["article_count"] == 1
    assert payload["actions"] == []


def test_ops_check_reports_attention_for_missing_local_article_routes(
    tmp_path: Path,
) -> None:
    site_dir = tmp_path / "site"
    unit_dir = tmp_path / "units"
    _write_saved_article_route_fixture(site_dir, complete=False)
    unit_dir.mkdir()
    for unit in ROW_ONE_SYSTEMD_UNITS:
        (unit_dir / unit).write_text("[Unit]\n", encoding="utf-8")

    payload = build_row_one_ops_check_payload(
        site_dir=site_dir,
        host="127.0.0.1",
        port=8787,
        unit_dir=unit_dir,
        as_of=datetime(2026, 7, 7, 8, 0, tzinfo=UTC),
        server_probe=lambda host, port, timeout: _probe("serving_row_one"),
    )

    assert payload["status"] == "attention"
    assert payload["local_article_routes"]["status"] == "missing"
    assert any("row-one refresh" in action for action in payload["actions"])
```

In `tests/test_row_one_cli.py`, add an ops-check human output test using monkeypatch of `build_row_one_ops_check_payload`:

```python
def test_row_one_ops_check_human_output_includes_local_article_route_health(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    payload = {
        "ok": True,
        "status": "attention",
        "site_dir": str(tmp_path),
        "as_of": "2026-07-07T08:00:00Z",
        "access": {},
        "site": {"status": "present"},
        "freshness": {"status": "fresh"},
        "server": {"status": "serving_row_one"},
        "systemd": {"status": "present"},
        "local_article_routes": {"status": "missing", "article_count": 1},
        "actions": ["Run `fashion-radar row-one refresh --output-dir site`."],
    }

    monkeypatch.setattr(
        "fashion_radar.cli.build_row_one_ops_check_payload",
        lambda **_kwargs: payload,
    )

    result = CliRunner().invoke(app, ["row-one", "ops-check", "--site-dir", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert "Local article routes: missing" in result.output
```

- [ ] **Step 2: Run ops-check tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_ops_check.py tests/test_row_one_cli.py -q -k "local_article_route_health or local_article_routes"
```

Expected: tests fail because ops-check payload and human output lack route health.

- [ ] **Step 3: Implement ops-check integration**

In `ops_check.py`, import:

```python
from fashion_radar.row_one.local_article_route_health import (
    build_row_one_local_article_route_health,
    row_one_local_article_route_health_payload,
)
```

Inside `build_row_one_ops_check_payload(...)`:

```python
    local_article_routes = row_one_local_article_route_health_payload(
        build_row_one_local_article_route_health(site_dir)
    )
    actions = _actions(site, freshness, probe, systemd, local_article_routes, site_dir)
    status = _overall_status(site, freshness, probe, systemd, local_article_routes)
```

Add `"local_article_routes": local_article_routes` to the returned payload.

Update `_actions(...)` signature, keeping `site_dir` as the final positional argument:

```python
def _actions(
    site: dict[str, object],
    freshness: dict[str, object],
    server: RowOneServerProbeResult,
    systemd: dict[str, object],
    local_article_routes: dict[str, object],
    site_dir: Path,
) -> list[str]:
```

Then add:

```python
    if local_article_routes.get("status") == "missing":
        action = f"Run `fashion-radar row-one refresh --output-dir {site_dir}`."
        if action not in actions:
            actions.append(action)
```

Update `_overall_status(...)` with the full priority order:

```python
def _overall_status(
    site: dict[str, object],
    freshness: dict[str, object],
    server: RowOneServerProbeResult,
    systemd: dict[str, object],
    local_article_routes: dict[str, object],
) -> str:
    if site.get("status") != "present" or freshness.get("status") == "unknown":
        return "unknown"
    if (
        freshness.get("status") == "fresh"
        and server.status == "serving_row_one"
        and systemd.get("status") == "present"
        and local_article_routes.get("status") != "missing"
    ):
        return "ready"
    return "attention"
```

In `_render_row_one_ops_check_text(...)`, add:

```python
    local_article_routes = (
        payload.get("local_article_routes")
        if isinstance(payload.get("local_article_routes"), dict)
        else {}
    )
```

Add line:

```python
        f"Local article routes: {local_article_routes.get('status', 'unknown')}",
```

- [ ] **Step 4: Run ops-check tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_ops_check.py tests/test_row_one_cli.py -q -k "local_article_route_health or local_article_routes"
```

Expected: selected ops-check tests pass.

### Task 6: Docs And Workflow Guards With RED/GREEN Tests

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Add failing docs/workflow tests**

Add a docs test in `tests/test_row_one_docs.py` using this exact paragraph:

```python
paragraph = (
    "Stage 374 adds read-only generated-site Saved Local Article Route Health to "
    "`row-one status` and `row-one ops-check`; it reuses current generated "
    "`data/articles/*.json` saved local article sidecars, current validated story ids, "
    "existing `index.html`, existing `articles/index.html`, and existing "
    "`articles/<story-id>.html` routes to verify that already-saved local article bodies "
    "are reachable through same-site generated article pages without changing app-facing "
    "contracts; it adds CLI-only route-health status payload fields, but it does not "
    "create `data/local-article-route-health.json`, does not create "
    "`data/article-route-health.json`, does not create `data/route-health.json`, does not "
    "create `local-article-route-health.html`, does not create `article-route-health.html`, "
    "does not create `route-health.html`, does not create new article-source sidecars, "
    "does not create new route families, does not alter `index.html`, "
    "`articles/index.html`, `articles/<story-id>.html`, or detail page rendering, does "
    "not publish full articles outside existing local article pages, does not add outbound "
    "article URLs as primary navigation, and does not change row-one-app/v7, "
    "row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts, source "
    "collection, fetching, matching, extraction, scoring, ranking, LLM, connector, "
    "scheduling, deployment, market grouping, domestic/international classification, "
    "analytics, personalization, recommendation, or compliance-review behavior."
)
```

Assert the paragraph appears in both docs before `Stage 373 adds` and scan the Stage 374 slice for stale phrases:

```python
for stale_phrase in (
    "creates data/local-article-route-health.json",
    "writes data/local-article-route-health.json",
    "creates data/article-route-health.json",
    "writes data/article-route-health.json",
    "creates data/route-health.json",
    "writes data/route-health.json",
    "creates local-article-route-health.html",
    "writes local-article-route-health.html",
    "creates article-route-health.html",
    "writes article-route-health.html",
    "creates route-health.html",
    "writes route-health.html",
    "changes row-one-app/v7",
    "changes row-one-manifest/v1",
    "changes row-one-runtime/v1",
    "adds app contract",
    "changes app contract",
    "adds generated json artifact",
    "changes generated json artifacts",
    "creates new article-source sidecars",
    "creates new route families",
    "adds new routes",
    "alters index.html",
    "alters articles/index.html",
    "alters articles/<story-id>.html",
    "publishes full articles outside existing local article pages",
    "adds outbound article urls as primary navigation",
    "adds source collection",
    "adds fetching",
    "adds matching",
    "adds extraction",
    "adds scoring",
    "adds ranking",
    "adds llm",
    "adds connector",
    "adds scheduling",
    "adds deployment",
    "adds analytics",
    "adds personalization",
    "adds recommendation",
    "adds compliance review",
    "adds compliance-review",
    "adds compliance-review behavior",
):
    assert stale_phrase not in normalized
```

In `tests/test_workflows.py`, extend generated contract denylist with:

```python
assert "local_article_route_health" not in generated_contract_payload
assert "article_route_health" not in generated_contract_payload
assert "route_health" not in generated_contract_payload
assert "RowOneLocalArticleRouteHealth" not in generated_contract_payload
assert "RowOneArticleRouteHealth" not in generated_contract_payload
assert "Saved Local Article Route Health" not in generated_contract_payload
assert "Local Article Route Health" not in generated_contract_payload
assert "Article Route Health" not in generated_contract_payload
assert "local-article-route-health" not in generated_contract_payload
assert "article-route-health" not in generated_contract_payload
assert "route-health" not in generated_contract_payload
assert "本地文章路由健康检查" not in generated_contract_payload
```

Extend artifact stem denylist with hyphen and underscore variants:

```python
"local-article-route-health",
"article-route-health",
"route-health",
"saved-local-article-route-health",
"saved-article-route-health",
"local_article_route_health",
"article_route_health",
"route_health",
"saved_local_article_route_health",
"saved_article_route_health",
```

Add a generated-site-only guard:

```python
def test_stage_374_saved_local_article_route_health_stays_generated_site_only(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from fashion_radar.row_one import status_integrity

    monkeypatch.setattr(
        status_integrity,
        "build_row_one_local_article_route_health",
        lambda *_args, **_kwargs: None,
        raising=True,
    )
    monkeypatch.setattr(
        status_integrity,
        "validate_row_one_local_article_route_health",
        lambda _health: None,
        raising=True,
    )
    test_write_row_one_site_files_writes_local_article_without_mutating_sqlite(tmp_path)
```

- [ ] **Step 2: Run docs/workflow tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_workflows.py -q -k "stage_374 or route_health"
```

Expected: docs paragraph and guard tests fail before docs/guards are updated.

- [ ] **Step 3: Update docs and workflow guards**

Add the exact Stage 374 paragraph to `README.md` and `docs/row-one.md` before the Stage 373 paragraph.

Add the docs test, contract denylist entries, artifact denylist entries, and generated-site-only guard described above.

- [ ] **Step 4: Run docs/workflow tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_workflows.py -q -k "stage_374 or route_health"
```

Expected: selected docs/workflow tests pass.

### Task 7: Focused Verification, Code Reviews, Full Gates, Commit, Push

**Files:**
- Create: `docs/reviews/claude-code-stage-374-code-review.md`
- Create: `docs/reviews/opencode-stage-374-code-review.md`
- Create rereview artifacts only if Critical or Important review findings require fixes.

- [ ] **Step 1: Run focused test and style checks**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_local_article_route_health.py \
  tests/test_row_one_cli.py \
  tests/test_row_one_ops_check.py \
  tests/test_row_one_docs.py \
  tests/test_workflows.py \
  -q -k "route_health or local_article_routes or saved_article_library_route or saved_article_page_route or homepage_saved_article_library_link or saved_article_library_page_link or stage_374"
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check \
  src/fashion_radar/row_one/local_article_route_health.py \
  src/fashion_radar/row_one/status_integrity.py \
  src/fashion_radar/row_one/ops_check.py \
  src/fashion_radar/cli.py \
  tests/test_row_one_local_article_route_health.py \
  tests/test_row_one_cli.py \
  tests/test_row_one_ops_check.py \
  tests/test_row_one_docs.py \
  tests/test_workflows.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check \
  src/fashion_radar/row_one/local_article_route_health.py \
  src/fashion_radar/row_one/status_integrity.py \
  src/fashion_radar/row_one/ops_check.py \
  src/fashion_radar/cli.py \
  tests/test_row_one_local_article_route_health.py \
  tests/test_row_one_cli.py \
  tests/test_row_one_ops_check.py \
  tests/test_row_one_docs.py \
  tests/test_workflows.py
```

Expected: focused tests and style checks pass.

- [ ] **Step 2: Request Claude Code code review**

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Review Stage 374 Saved Local Article Route Health implementation in /home/ubuntu/fashion-radar. Compare current git diff to docs/superpowers/specs/2026-07-09-stage-374-saved-local-article-route-health-design.md and docs/superpowers/plans/2026-07-09-stage-374-saved-local-article-route-health-plan.md. Focus on correctness, route/link validation, read-only behavior, status/ops-check behavior, generated-site-only boundaries, app/runtime/manifest contract safety, docs/tests, and regressions. Return findings only, ordered by Critical, Important, Minor." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-374-code-review.md
rm -f "$tmp_review"
```

Expected: review is saved and contains no live-capture/tool chatter.

- [ ] **Step 3: Request opencode code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Review Stage 374 Saved Local Article Route Health implementation in /home/ubuntu/fashion-radar. Compare current git diff to docs/superpowers/specs/2026-07-09-stage-374-saved-local-article-route-health-design.md and docs/superpowers/plans/2026-07-09-stage-374-saved-local-article-route-health-plan.md. Also read docs/reviews/claude-code-stage-374-code-review.md if present and cross-check it. Focus on correctness, route/link validation, read-only behavior, status/ops-check behavior, generated-site-only boundaries, app/runtime/manifest contract safety, docs/tests, and regressions. Return findings only, ordered by Critical, Important, Minor." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-374-code-review.md
rm -f "$tmp_review"
```

Expected: review is saved and contains no live-capture/tool chatter.

- [ ] **Step 4: Fix valid Critical and Important code findings**

If review raises Critical or Important issues, fix them with tests and run Claude/opencode rereviews before full gates.

- [ ] **Step 5: Run full gates**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config lock --check --offline
git diff --check && git diff --cached --check
```

Expected: all gates pass.

- [ ] **Step 6: Commit and push**

Run:

```bash
git status --short
git add src/fashion_radar/row_one/local_article_route_health.py \
  src/fashion_radar/row_one/status_integrity.py \
  src/fashion_radar/row_one/ops_check.py \
  src/fashion_radar/cli.py \
  tests/test_row_one_local_article_route_health.py \
  tests/test_row_one_cli.py \
  tests/test_row_one_ops_check.py \
  tests/test_row_one_docs.py \
  tests/test_workflows.py \
  README.md docs/row-one.md \
  docs/superpowers/specs/2026-07-09-stage-374-saved-local-article-route-health-design.md \
  docs/superpowers/plans/2026-07-09-stage-374-saved-local-article-route-health-plan.md \
  docs/reviews/claude-code-stage-374-plan-review.md \
  docs/reviews/opencode-stage-374-plan-review.md \
  docs/reviews/claude-code-stage-374-code-review.md \
  docs/reviews/opencode-stage-374-code-review.md
git commit -m "Stage 374: add saved local article route health"
git push origin main
```

Expected: commit is created and pushed to GitHub.

# Stage 348 Saved Article Source Routes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add generated-site-only Source Routes that let the saved article daily summary jump directly to source groups and Source Briefs.

**Architecture:** Build source route view data inside `src/fashion_radar/row_one/templates.py` from the existing saved article library source groups. Render stable same-page anchors on source group sections and a capped Source Routes chip row inside the existing daily summary, without changing schemas, JSON artifacts, route families, collection, extraction, ranking, or app-facing contracts.

**Tech Stack:** Python 3.12, existing ROW ONE dataclasses, HTML string rendering in `templates.py`, pytest, ruff, uv.

---

## File Structure

- Modify `src/fashion_radar/row_one/templates.py`
  - Add `SAVED_ARTICLE_SOURCE_ROUTE_LIMIT = 4`.
  - Add CSS selectors for `.saved-article-source-routes`, route header/list/chip classes, and route metrics.
  - Add a small private `_SavedArticleSourceRoute` dataclass or tuple helper if useful.
  - Add helpers for safe source anchor creation, duplicate suffixing, route item building, and source route rendering.
  - Pass source route ids into `_render_saved_article_library_source(...)`.
  - Render Source Routes in `_render_saved_article_daily_summary(...)` after metrics and before broad links.
- Modify `tests/test_row_one_render.py`
  - Add daily summary route rendering and placement tests.
  - Add anchor generation, escaping, capping, duplicate slug, empty-shell, and homepage absence tests.
  - Add CSS selector coverage.
- Modify `tests/test_workflows.py`
  - Add generated-contract negative assertions and artifact absence checks for Stage 348.
- Modify `tests/test_row_one_docs.py`
  - Add Stage 348 boundary documentation guard.
- Modify `README.md` and `docs/row-one.md`
  - Add one concise Stage 348 boundary paragraph before Stage 347.
- Add `docs/reviews/claude-code-stage-348-plan-review-prompt.md`.
- Add `docs/reviews/opencode-stage-348-plan-review-prompt.md`.

## Task 1: Write Failing Tests

**Files:**
- Modify: `tests/test_row_one_render.py`
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Add a source-route placement test**

Add near saved article daily-summary tests:

```python
def test_render_saved_article_library_daily_summary_links_to_source_routes() -> None:
    html = render_saved_article_library_html(_edition(), _saved_article_library_fixture())
    summary_start = html.index('class="saved-article-daily-summary"')
    summary_html = html[summary_start : html.index("</section>", summary_start)]

    assert 'class="saved-article-source-routes"' in summary_html
    assert "Source Routes" in summary_html
    assert "来源导览" in summary_html
    assert 'href="#saved-article-source-vogue-business"' in summary_html
    assert "Vogue Business" in summary_html
    assert "1 article" in summary_html
    assert "1 saved paragraph" in summary_html
    assert summary_html.index('class="saved-article-daily-summary-metrics"') < summary_html.index(
        'class="saved-article-source-routes"'
    )
    assert summary_html.index('class="saved-article-source-routes"') < summary_html.index(
        'class="saved-article-daily-summary-links"'
    )
```

- [ ] **Step 2: Add a source section anchor test**

Add near Stage 347 source-brief tests:

```python
def test_render_saved_article_library_source_groups_have_route_anchors() -> None:
    html = render_saved_article_library_html(_edition(), _saved_article_library_fixture())
    source_html = _saved_article_library_first_source_html(html)

    assert '<section class="saved-article-library-source" id="saved-article-source-vogue-business">' in source_html
    assert 'href="#saved-article-source-vogue-business"' in html
    assert source_html.index('id="saved-article-source-vogue-business"') < source_html.index(
        'class="saved-article-source-brief"'
    )
```

- [ ] **Step 3: Add escaping, capping, and duplicate-slug tests**

Create a `RowOneSavedArticleLibrary` with five source groups:

- `Vogue Business`;
- `Vogue Business`;
- `WWD <script>`;
- `The Row / Signals`;
- `Overflow Source`.

Assert:

- route chips are capped at four;
- duplicate source anchors suffix deterministically, for example
  `saved-article-source-vogue-business` and
  `saved-article-source-vogue-business-2`;
- `<script>` is escaped in text and absent as raw HTML;
- hrefs remain same-page fragments;
- `Overflow Source` is omitted from the route row but its source group can still
  render in the grid.

- [ ] **Step 4: Add empty-shell test**

Create a library with a source group whose `entries=[]`.

Assert:

```python
assert 'class="saved-article-source-routes"' not in html
assert 'id="saved-article-source-' not in html
```

- [ ] **Step 5: Add generated contract and homepage absence assertions**

In the site-render test that reads `edition.json`, `manifest.json`, and
`runtime.json`, assert none of these strings appear:

```python
"saved_article_source_routes"
"source_routes"
"saved-article-source-routes"
"source-routes"
"Source Routes"
"来源导览"
```

Assert the homepage `index.html` does not contain
`saved-article-source-routes`.

- [ ] **Step 6: Add CSS selector coverage**

Extend `test_row_one_css_includes_saved_article_library_styles(...)` with:

```python
".saved-article-source-routes"
".saved-article-source-routes-header"
".saved-article-source-routes-list"
".saved-article-source-route"
".saved-article-source-route-name"
".saved-article-source-route-metrics"
```

- [ ] **Step 7: Add docs/workflow failing tests**

Add Stage 348 docs guard in `tests/test_row_one_docs.py`, mirroring Stage 347,
with expected text:

```text
Stage 348 adds generated-site only Saved Article Source Routes inside
`articles/index.html`; it reuses the existing saved article library source
groups, existing source group counts, existing Source Brief placement, and safe
same-page anchors to let the daily summary jump directly to each source group
without changing app-facing contracts; it does not create
`data/saved-article-source-routes.json`, does not create
`data/source-routes.json`, does not create new article-source sidecars, does not
create new route families, does not publish full articles on the library index,
does not add outbound article URLs as primary navigation, does not change
row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON
artifacts, source collection, fetching, matching, extraction, scoring, ranking,
LLM, connector, scheduling, deployment, market grouping,
domestic/international classification, analytics, personalization,
recommendation, or compliance-review behavior.
```

- [ ] **Step 8: Run tests and confirm they fail**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py -q -k "source_routes or stage_348"
```

Expected: fail because source route anchors and docs do not exist yet.

## Task 2: Implement Source Route Rendering

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Add cap and route helper structure**

Add near saved article constants:

```python
SAVED_ARTICLE_SOURCE_ROUTE_LIMIT = 4
```

Add a private frozen dataclass near the saved article library helpers:

```python
@dataclass(frozen=True)
class _SavedArticleSourceRoute:
    source_name: str
    anchor_id: str
    article_count: int
    saved_paragraph_count: int
```

- [ ] **Step 2: Build route anchors from source groups**

Add:

```python
def _saved_article_source_routes(
    groups: Sequence[RowOneSavedArticleLibrarySourceGroup],
) -> list[_SavedArticleSourceRoute]:
    routes: list[_SavedArticleSourceRoute] = []
    seen_slugs: dict[str, int] = {}
    for group in groups:
        if not group.entries:
            continue
        slug = _saved_article_source_route_slug(group.source_name)
        if slug is None:
            continue
        count = seen_slugs.get(slug, 0) + 1
        seen_slugs[slug] = count
        anchor_id = f"saved-article-source-{slug}" if count == 1 else f"saved-article-source-{slug}-{count}"
        routes.append(
            _SavedArticleSourceRoute(
                source_name=group.source_name.strip() or "Unknown source",
                anchor_id=anchor_id,
                article_count=group.article_count,
                saved_paragraph_count=group.saved_paragraph_count,
            )
        )
    return routes
```

Add:

```python
def _saved_article_source_route_slug(source_name: str) -> str | None:
    slug = re.sub(r"[^a-z0-9]+", "-", source_name.strip().casefold()).strip("-")
    if not slug:
        return None
    return slug[:64].strip("-") or None
```

Use existing `re` import if already present; otherwise add it at the top of
`templates.py`.

- [ ] **Step 3: Pass route anchors into source rendering**

In `render_saved_article_library_html(...)`:

```python
source_routes = _saved_article_source_routes(library.groups)
source_route_ids_by_index = {
    index: route.anchor_id for index, route in enumerate(source_routes)
}
```

Render groups with `enumerate(library.groups)` and pass:

```python
source_anchor_id=source_route_ids_by_index.get(index)
```

Update `_render_saved_article_library_source(...)` signature:

```python
source_anchor_id: str | None = None
```

Render:

```python
id_attr = f' id="{_esc(source_anchor_id)}"' if source_anchor_id else ""
return f"""    <section class="saved-article-library-source"{id_attr}>
...
"""
```

- [ ] **Step 4: Render routes in the daily summary**

Update `_render_saved_article_daily_summary(...)` signature:

```python
source_routes: Sequence[_SavedArticleSourceRoute] = (),
```

Add helper:

```python
def _render_saved_article_source_routes(
    source_routes: Sequence[_SavedArticleSourceRoute],
) -> str:
    chips = []
    seen_hrefs: set[str] = set()
    for route in source_routes[:SAVED_ARTICLE_SOURCE_ROUTE_LIMIT]:
        href = f"#{route.anchor_id}"
        if href in seen_hrefs:
            continue
        seen_hrefs.add(href)
        article_count = _count_label(route.article_count, "article", "articles")
        paragraph_count = _count_label(
            route.saved_paragraph_count,
            "saved paragraph",
            "saved paragraphs",
        )
        chips.append(
            f"""<a class="saved-article-source-route" href="{_esc(href)}">
      <span class="saved-article-source-route-name">{_esc(route.source_name)}</span>
      <span class="saved-article-source-route-metrics">
        <span data-lang="en">{_esc(article_count)}, {_esc(paragraph_count)}</span>
        <span data-lang="zh">{_esc(route.article_count)} 篇文章，{_esc(route.saved_paragraph_count)} 个保存段落</span>
      </span>
    </a>"""
        )
    if not chips:
        return ""
    return (
        '<div class="saved-article-source-routes" aria-label="Saved article source routes">'
        '<div class="saved-article-source-routes-header">'
        '<span data-lang="en">Source Routes</span>'
        '<span data-lang="zh">来源导览</span>'
        "</div>"
        '<div class="saved-article-source-routes-list">' + "".join(chips) + "</div></div>"
    )
```

In `_render_saved_article_daily_summary(...)`, compute:

```python
source_routes_html = _render_saved_article_source_routes(source_routes)
```

Insert between metrics and links:

```python
  {source_routes_html}
  <div class="saved-article-daily-summary-links">...
```

- [ ] **Step 5: Add CSS**

Add CSS near `.saved-article-daily-summary-*` and
`.saved-article-source-brief-*`:

```css
.saved-article-source-routes { ... }
.saved-article-source-routes-header { ... }
.saved-article-source-routes-list { ... }
.saved-article-source-route { ... }
.saved-article-source-route-name { ... }
.saved-article-source-route-metrics { ... }
```

Mirror existing understated library chip styling.

## Task 3: Add Documentation Boundary

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Add docs paragraph**

Insert the Stage 348 paragraph before Stage 347 in both `README.md` and
`docs/row-one.md`.

- [ ] **Step 2: Add workflow guard strings**

In `tests/test_workflows.py`, add forbidden contract strings:

```python
"saved_article_source_routes"
"source_routes"
"Saved Article Source Routes"
"saved-article-source-routes"
"source-routes"
"Source Routes"
"来源导览"
```

Add artifact absence checks:

```python
output_dir / "saved-article-source-routes.json"
output_dir / "articles" / "saved-article-source-routes.json"
output_dir / "data" / "saved-article-source-routes.json"
output_dir / "saved-article-source-routes.html"
output_dir / "articles" / "saved-article-source-routes.html"
output_dir / "data" / "saved-article-source-routes.html"
output_dir / "source-routes.json"
output_dir / "articles" / "source-routes.json"
output_dir / "data" / "source-routes.json"
output_dir / "source-routes.html"
output_dir / "articles" / "source-routes.html"
output_dir / "data" / "source-routes.html"
```

- [ ] **Step 3: Run docs/workflow tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_workflows.py -q -k "stage_348 or source_routes"
```

Expected: pass after docs and workflow guards are updated.

## Task 4: Verify, Review, Commit

**Files:**
- All modified files

- [ ] **Step 1: Run focused tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py -q -k "source_routes or stage_348"
```

- [ ] **Step 2: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv --no-config lock --check
git diff --check
```

- [ ] **Step 3: Request code review**

Use Claude Code when available:

```bash
printf '%s\n' 'Review the current uncommitted Stage 348 changes in /home/ubuntu/fashion-radar. Focus on correctness, generated-site-only boundaries, link safety, tests, and whether anything should block commit. Return concise findings by severity; do not edit files.' | claude -p --effort max --permission-mode dontAsk --add-dir /home/ubuntu/fashion-radar
```

If Claude Code times out, use subagent review and record the timeout in the
handoff.

- [ ] **Step 4: Run staged checks and commit**

Run:

```bash
git add README.md docs/row-one.md src/fashion_radar/row_one/templates.py tests/test_row_one_docs.py tests/test_row_one_render.py tests/test_workflows.py docs/reviews/claude-code-stage-348-plan-review-prompt.md docs/reviews/opencode-stage-348-plan-review-prompt.md docs/superpowers/plans/2026-07-08-stage-348-saved-article-source-routes-plan.md docs/superpowers/specs/2026-07-08-stage-348-saved-article-source-routes-design.md
git diff --cached --check
git diff --cached | grep -nE 'ghp_[A-Za-z0-9]+|sk-[A-Za-z0-9]{20,}|BEGIN (RSA|OPENSSH|PRIVATE) KEY|xox[baprs]-[A-Za-z0-9-]+' || true
git commit -m "Stage 348: add saved article source routes"
```

- [ ] **Step 5: Push and hand off**

Push to `origin/main` using the existing local token file and temporary
extraheader. Then report:

- repo status;
- verified commands;
- uncommitted files;
- next step.

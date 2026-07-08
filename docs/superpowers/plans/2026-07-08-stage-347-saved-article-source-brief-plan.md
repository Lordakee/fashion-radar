# Stage 347 Saved Article Source Brief Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add generated-site-only source-level briefs to saved article source groups and align saved article coverage inclusion with the library/page story-id guard.

**Architecture:** Render the source brief inside `src/fashion_radar/row_one/templates.py` using the existing saved article library source groups, safe article page allowlist, and content-organization body-guide cards already grouped by detail path. Add one small coverage-builder guard in `src/fashion_radar/row_one/saved_article_coverage.py` so homepage coverage skips mismatched local article sidecars like the library and local article page flow.

**Tech Stack:** Python 3.12, existing ROW ONE dataclasses, HTML string rendering in `templates.py`, pytest, ruff, uv.

---

## File Structure

- Modify `src/fashion_radar/row_one/templates.py`
  - Add `SAVED_ARTICLE_SOURCE_BRIEF_ITEMS_PER_SOURCE = 2`.
  - Add source-brief CSS selectors.
  - Pass existing `snippets_by_detail_path` and `local_article_page_hrefs_by_detail_path` into `_render_saved_article_library_source(...)`.
  - Add private helpers for source-brief rendering, source contribution items, safe entry hrefs, and bullet dedupe/capping.
  - Insert the brief after the source header and before `saved-article-library-source-grid`.
- Modify `src/fashion_radar/row_one/saved_article_coverage.py`
  - Skip articles when `article.story_id != story.id`.
- Modify `tests/test_row_one_render.py`
  - Add source-brief rendering, placement, escaping, cap/dedupe, safe href filtering, empty-shell omission, CSS selector, and contract non-leak tests.
- Modify saved article coverage tests
  - Add a builder-level test proving mismatched `article.story_id` is rejected.
- Modify `tests/test_workflows.py`
  - Add generated contract negative assertions and artifact absence checks for Stage 347.
- Modify `tests/test_row_one_docs.py`
  - Add Stage 347 boundary documentation guard.
- Modify `README.md` and `docs/row-one.md`
  - Add one concise Stage 347 boundary paragraph.
- Add `docs/reviews/claude-code-stage-347-plan-review-prompt.md`
- Add `docs/reviews/opencode-stage-347-plan-review-prompt.md`

## Task 1: Write Failing Tests

**Files:**
- Modify: `tests/test_row_one_render.py`
- Modify: saved article coverage test file or adjacent coverage tests in `tests/test_row_one_render.py`

- [ ] **Step 1: Add a site-render test for source brief placement**

Add near saved article library tests:

```python
def test_render_row_one_site_includes_saved_article_source_brief_in_library(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _theme_digest_local_article()},
    )

    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    source_html = _saved_article_library_first_source_html(library_html)
    edition_payload = json.loads((tmp_path / "data" / "edition.json").read_text())
    manifest_payload = json.loads((tmp_path / "data" / "manifest.json").read_text())
    runtime_payload = json.loads((tmp_path / "data" / "runtime.json").read_text())

    assert 'class="saved-article-source-brief"' in source_html
    assert "Source Brief" in source_html
    assert "来源简报" in source_html
    assert "Vogue Business" in source_html
    assert "1 saved article" in source_html
    assert "3 saved paragraphs" in source_html
    assert "Start with The Row retail signal." in source_html
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"'
        in source_html
    )
    assert source_html.index('class="saved-article-library-source-header"') < source_html.index(
        'class="saved-article-source-brief"'
    )
    assert source_html.index('class="saved-article-source-brief"') < source_html.index(
        'class="saved-article-library-source-grid"'
    )
    assert 'class="saved-article-source-brief"' not in (
        tmp_path / "index.html"
    ).read_text(encoding="utf-8")

    for contract_json in (
        json.dumps(edition_payload, ensure_ascii=False),
        json.dumps(manifest_payload, ensure_ascii=False),
        json.dumps(runtime_payload, ensure_ascii=False),
    ):
        assert "saved_article_source_brief" not in contract_json
        assert "source_brief" not in contract_json
        assert "saved-article-source-brief" not in contract_json
        assert "Source Brief" not in contract_json
    assert not (tmp_path / "data" / "saved-article-source-brief.json").exists()
```

- [ ] **Step 2: Add source slicing helper**

```python
def _saved_article_library_first_source_html(index_html: str) -> str:
    marker = '<section class="saved-article-library-source">'
    assert marker in index_html
    source_start = index_html.index(marker)
    next_source = index_html.find(marker, source_start + len(marker))
    section_end = index_html.find("</section>", source_start) + len("</section>")
    source_end = next_source if next_source >= 0 else section_end
    assert source_end > source_start
    return index_html[source_start:source_end]
```

- [ ] **Step 3: Add direct renderer test for escaping, cap, and dedupe**

Create a `RowOneSavedArticleLibrarySourceGroup` with three safe entries/snippet
cards, including duplicate lead text and unsafe HTML. Assert:

- brief item count is two;
- duplicate text appears once;
- `<script>` text is escaped;
- long text is truncated;
- no raw unsafe HTML appears.

- [ ] **Step 4: Add direct renderer test for unsafe links and empty shell**

Assert unsafe article-page hrefs and unsafe detail paths do not render in source
brief items, and a source group with no safe cards returns no
`saved-article-source-brief` shell.

- [ ] **Step 5: Add coverage builder parity test**

Add a test proving `build_row_one_saved_article_coverage()` returns `None` or
omits the item when the local article sidecar is keyed by `story.id` but
`article.story_id` differs.

- [ ] **Step 6: Run tests and confirm they fail**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "source_brief or saved_article_coverage"
```

Expected: fail because source brief rendering and coverage story-id guard are
not implemented yet.

## Task 2: Implement Source Brief Rendering

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Add source brief cap and CSS**

Add:

```python
SAVED_ARTICLE_SOURCE_BRIEF_ITEMS_PER_SOURCE = 2
```

Add CSS selectors:

```css
.saved-article-source-brief
.saved-article-source-brief-header
.saved-article-source-brief-metrics
.saved-article-source-brief-list
.saved-article-source-brief-item
.saved-article-source-brief-label
.saved-article-source-brief-body
.saved-article-source-brief-link
```

- [ ] **Step 2: Add source-brief renderer**

Add a helper that accepts the source group, the existing snippets lookup, and
article page allowlist:

```python
def _render_saved_article_source_brief(
    group: RowOneSavedArticleLibrarySourceGroup,
    *,
    snippets_by_detail_path: Mapping[str, Sequence[RowOneSavedArticleContentOrganizationCard]] | None,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str:
    items = _saved_article_source_brief_items(...)
    if not items:
        return ""
    ...
```

Use existing `_count_label(...)`, `_local_article_digest_excerpt(...)`,
`_saved_article_library_entry_detail_path(...)`,
`_saved_article_library_entry_snippets(...)`,
`_safe_saved_article_content_organization_href(...)`,
`_prefixed_saved_article_content_organization_href(...)`, and
`_saved_article_library_entry_article_page_href(...)`.

- [ ] **Step 3: Insert source brief in source renderer**

In `_render_saved_article_library_source(...)`, compute `source_brief` after
`paragraph_count_zh` and place it between source header and source grid:

```python
      </div>
      {source_brief}
      <div class="saved-article-library-source-grid">{cards}</div>
```

- [ ] **Step 4: Ensure safe fallback behavior**

Contribution items should prefer the first safe body-guide snippet for each
entry. If no snippet is available, use a safe entry title/section label and the
safe article page href or digest href. Deduplicate by normalized label/body/href
and stop after two safe items.

## Task 3: Implement Coverage Inclusion Guard

**Files:**
- Modify: `src/fashion_radar/row_one/saved_article_coverage.py`

- [ ] **Step 1: Add story-id mismatch guard**

In `build_row_one_saved_article_coverage(...)`, after the `article is None`
check:

```python
if article.story_id != story.id:
    continue
```

- [ ] **Step 2: Run coverage-focused tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "saved_article_coverage"
```

Expected: pass.

## Task 4: Add Contract Guards And Docs

**Files:**
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Add workflow negative assertions**

Add forbidden generated-contract strings:

```python
"saved_article_source_brief"
"source_brief"
"Saved Article Source Brief"
"saved-article-source-brief"
"source-brief"
```

Add artifact absence checks for:

```python
saved-article-source-brief.json/html
source-brief.json/html
```

- [ ] **Step 2: Add docs guard**

Add `test_row_one_docs_describe_stage_347_saved_article_source_brief_boundary`
before the Stage 346 docs guard.

- [ ] **Step 3: Add docs paragraphs**

Add this paragraph before Stage 346 in `README.md` and `docs/row-one.md`:

```markdown
Stage 347 adds a generated-site only Saved Article Source Brief inside
`articles/index.html`; it reuses existing saved article library source groups,
existing source-group counts, existing saved article card routes, existing safe
detail-path anchors, and existing saved article body-guide snippets to explain
what each source contributes before its card grid without changing app-facing
contracts; it does not create `data/saved-article-source-brief.json`, does not
create `data/source-brief.json`, does not create new article-source sidecars,
does not create new route families, does not publish full articles on the
library index, does not add outbound article URLs as primary navigation, does
not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas,
JSON artifacts, source collection, fetching, matching, extraction, scoring,
ranking, LLM, connector, scheduling, deployment, market grouping,
domestic/international classification, analytics, personalization,
recommendation, or compliance-review behavior.
```

## Task 5: Verify, Review, Commit, Push

**Files:**
- Verify all modified files.

- [ ] **Step 1: Run focused tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py -q \
  -k "source_brief or saved_article_coverage or row_one_docs_describe_stage_347 or local_article_without_mutating_sqlite"
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

Run local Claude Code review with max effort if reachable. If local Claude cannot
access the Linux repo path, record the failure and use the subagent code-review
fallback.

- [ ] **Step 4: Stage, scan, commit, push**

Run staged whitespace and secret scans, then commit:

```bash
git commit -m "Stage 347: add saved article source brief"
git -c http.version=HTTP/1.1 -c http.curloptResolve=github.com:443:140.82.113.4 push origin main
```

## Self-Review Checklist

- The source brief explains existing source-group contribution, not source
  quality or ranking.
- The feature is generated-site-only and stays out of app contracts and JSON
  artifacts.
- Links are internal and safe.
- Text is escaped, deduped, and capped.
- Empty source brief shells do not render.
- Coverage builder rejects mismatched story IDs.

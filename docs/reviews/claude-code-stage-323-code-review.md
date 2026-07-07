**Stage 323ROW ONE Local-First Reading — Code Review**

---

**No Critical or Important findings. Safe to push.**

---

### Correctness

`render.py` change is a single line — passes the existing `local_articles_by_story_id` map through to `render_index_html()`. No new data produced, no side effects.

`render_index_html()` defaults `local_articles_by_story_id or {}` immediately, so downstream calls never receive `None`. The map is threaded into `_render_lead_story()` and `_render_section()` without mutation.

Eligibility guard (`_usable_local_article_paragraph_count(article) > 0`) correctly counts only non-empty paragraphs via `normalize_row_one_paragraph`. No article → no local-first path rendered. Clean fallback to existing CTAs.

### href Safety

`_local_article_href()` validates the story's `detail_path` through `validated_row_one_detail_relative_path()` before constructing `detail_path#local-article`. The result is HTML-escaped at every point of use (`_esc(local_article_href)`).

`_safe_saved_article_content_organization_evidence_href()` applies layered guards:
- Re-validates the path portion through `validated_row_one_detail_relative_path()`
- Rejects `bool` masquerading as `int` (explicit `isinstance(paragraph_index, bool)` check)
- Rejects negative indices
- Constructs the fragment then validates it against `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE` (`local-article-paragraph-[1-9][0-9]*`)

`#` is not escaped by `html.escape`, so the fragment survives `_esc()` intact. No double-escape concern.

### No Nested Anchors

The old `<a class="saved-article-content-organization-card">` wrapper has been replaced by `<article>`. Ref chips are `<span>` elements (no anchors). The evidence links and card-link `<a>` are now direct children of `<article>` — valid HTML, no interactive content nesting.

The detail `local-read-path` is a `<p>` containing one `<a href="#local-article">`, placed at the top level of the detail body template, not inside any other anchor.

### JSON Contract / Schema Boundaries

No Pydantic models touched. No new fields in app, runtime, or manifest payloads. Workflow test explicitly asserts all seven forbidden field names are absent from the generated contract payload. Boundary intact.

### Evidence Link Cap and Dedup

`seen: set[int]` deduplicates by `paragraph_index` before the cap. Cap is `SAVED_ARTICLE_CONTENT_ORGANIZATION_EVIDENCE_LINK_LIMIT = 3`. Order follows `card.paragraph_indices` as declared. Correct.

### Test Coverage

Four new render tests cover: homepage local-first presence, homepage absence without article, detail ordering (local action before source action), and content-organization card→article migration + evidence links. Workflow test adds negative contract assertions. Coverage is adequate for the scope.

### Minor Observations (non-blocking)

- `_esc(story_action_class)` / `_esc(lead_action_class)` escapes string literals built from constants — harmless but unnecessary.
- Re-calling `validated_row_one_detail_relative_path(path)` inside evidence href after `_safe_saved_article_content_organization_href()` already validated it is redundant but defensive and not a bug.

---

**Verdict: No blockers. Implementation is correct, href-safe, nested-anchor-clean, and respects all hard boundaries.**

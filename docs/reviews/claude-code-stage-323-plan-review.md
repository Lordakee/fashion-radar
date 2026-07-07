## Stage323Plan Review — ROW ONE Local-First Reading

**No unresolved Critical or Important findings.**

---

### Prior-Review Fixes Verified

**`dataclasses.replace()` / frozen dataclass** — `RowOneSavedArticleContentOrganizationCard` is `@dataclass(frozen=True)`. `replace()` is the correct mutation mechanism. ✅

**Valid constructor fields in safety test** — card is constructed with `title`, `source_name`, `section_title`, `section_label`, `lead`, `detail_path`, `paragraph_indices`, `references`. These match the dataclass exactly. No phantom `story_id` or `section_key` fields used. ✅

**Bad-index card count assertion** — 5 total cards, 3 invalid-path cards filtered (JS, traversal, wrong-fragment) → safe_card + bad_index_card + duplicate_card = 3 rendered. `== 3` is correct. ✅

**`Read the brief` / `Read brief` CTA labels** — Step 1 test now uses *negative* assertions (`not in index_html`) for both labels. Positive assertion checks for `"Read saved article"` / `"阅读本地正文"`. ✅

**`#local-article` target** — used consistently in homepage href helpers, detail renderer, and all related test assertions. ✅

**Homepage `local-read-action` class** — Step 1 asserts `class="local-read-action"` present; Task 2 Step 4 uses `"lead-story-link local-read-action"` and `"story-detail-link local-read-action"` (both contain the asserted substring). ✅

---

### Other Checks

**Pre-existing helpers confirmed** — `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE` already defined in `templates.py`; `validated_row_one_detail_relative_path` already imported; `_safe_saved_article_content_organization_href` already exists. No new regex or validator needs to be introduced. ✅

**`bool` guard** — `isinstance(paragraph_index, bool)` correctly prevents `True` (a `bool` subclass of `int`) from producing a paragraph-2 link. ✅

**No nested anchors** — homepage `local-read-path` block is a plain `<p>` with no `<a>`; the CTA link is the card's existing headline/footer anchor. Detail `local-read-path` block contains one `<a>` inside a `<p>`, not inside another anchor. Evidence links are inside `<article>`, not inside `<a>`. ✅

**JSON contract boundary** — `local_articles_by_story_id` is passed only to `render_index_html()` (private render argument); Step 2 explicitly guards against adding it to `build_row_one_app_payload()`. Workflow negative assertions cover all five banned keys. ✅

**href safety** — evidence helper re-validates path from already-validated `safe_section_href` (redundant but harmless), then checks paragraph fragment against `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE`. Covers external URLs, traversal, wrong fragments, negative and zero indices. ✅

**Test coverage** — render, omission, detail ordering, evidence, safety, cap+dedupe, nested-anchor, CSS, workflow boundary, and docs boundary tests are all present. ✅

---

### Minor Notes (non-blocking)

- Double validation inside `_safe_saved_article_content_organization_evidence_href` (path validated once via `_safe_saved_article_content_organization_href`, then re-validated via `validated_row_one_detail_relative_path`) is redundant but adds no correctness risk.
- `duplicate_card` uses `paragraph_indices=(0, 0, 1)` — dedup by integer index before building hrefs is correct; the `seen` set operates on raw indices, not on computed fragment strings. Count assertion `== 2` for paragraph-1 (safe_card index 0 + duplicate_card index 0) is accurate.

**Plan is feasible and ready for implementation.**

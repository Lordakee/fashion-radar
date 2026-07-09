## Stage 377 Plan/Spec Review

### Critical

None.

Feasibility, integration points, and Pydantic fixtures verified sound against the codebase:
- `_local_article_page_hrefs_by_story_id` exists (`render.py:454`), `_write_local_article_pages` exists (`render.py:463`), `render_local_article_page_html` exists (`templates.py:829`), and `{local_article_section}` at `templates.py:936` sits inside `<div class="local-article-page-article">` (`:916`) before its closing `</div>` (`:937`) — so the after-body placement is achievable exactly as specified.
- `safe_local_article_story_id` (`articles.py:629`) and `local_article_paragraph_anchor` (`local_article_anchors.py:12`, returns `index + 1`) match the spec's href/anchor rules. Fixture story ids ending in `-2222222222` (10 hex digits) satisfy the id regex.
- The Task 2 Step 1 fixtures (`_story`, `_article`, `_edition`, `_content_section`, `_ref`) are Pydantic-valid against `models.py` (all required fields and `Literal` values present, `extra="forbid"` honored). The original I-1 is resolved.

---

### Important

**I-1: Unaddressed overlap with `saved_article_local_reading_companion` — the article page already has a "read next" module**

The saved local article page already renders `saved_article_local_reading_companion` (`render.py:492` → `templates.py:930`), whose `related_items` field (`saved_article_local_reading_companion.py:73`) is rendered as `saved-article-local-reading-companion-related` cards (`templates.py:9127`). Each card carries a title, source name, lead/excerpt, reference chips, and an `<a class="saved-article-local-reading-companion-action" href="...">Read next locally / 继续本地阅读</a>` link (`templates.py:9162`) to a sibling article page, gated by a renderer-side href validator.

Stage 377 adds a second cross-article card module with the same product shape (title, source, reason, excerpt, reference chips, sibling-page href). The differences are real but narrow:
- selection basis: companion uses content-organization **group** membership; Stage 377 uses **shared reference / section / source** signals across the whole edition;
- placement: companion renders **before** the body (`:930`), Stage 377 renders **after** (`:936`);
- gating: companion requires `saved_article_library` + `saved_article_content_organization` (returns `None` otherwise, `saved_article_local_reading_companion.py:92`); Stage 377 works from the edition alone.

Three concrete problems follow:
1. The spec's "Product Gap Closed" claim — *"They do not provide a professional 'read next' path at the end of each locally saved article page"* — is inaccurate; a read-next path already exists via the companion.
2. When library/organization are present, **both** card lists will render on the same page (a before-body group-based list and an after-body signal-based list), which is an unreviewed UX duplication the plan never acknowledges.
3. Nothing guarantees the two modules won't recommend the **same** sibling article twice.

**Required:** add an explicit non-duplication/co-existence section to the spec stating (a) the corrected gap rationale, (b) whether both modules co-render and why that is acceptable, and (c) whether the new builder should dedupe against the companion's `related_items` (e.g., by candidate story id). Without this, reviewers and implementers cannot judge whether Stage 377 is complementary or redundant.

---

### Minor

**M-1: `card_count` invariant is unenforced (carried forward from rereview, still open)**
`RowOneSavedArticleLocalRelatedReads.card_count: int` is a frozen-dataclass field with no check that it equals `len(cards)`; correctness depends on builder convention. Either derive it at render time, assert `card_count == len(cards)` in the builder/tests, or drop the field.

**M-2: `paragraphs_zh` aligned-excerpt case is not a named RED test**
The spec Test Plan lists "uses aligned `paragraphs_zh` ... falls back to English when absent or blank," but Task 2 Step 2's named RED tests omit it; it survives only as Task 3 Step 3 prose. Add a named failing test in Task 2 (e.g., `test_saved_article_local_related_reads_uses_aligned_paragraphs_zh_excerpt`) so RED verification actually covers the zh/fallback branch.

**M-3: Renderer-side fragment validator does not re-bind `N` to a real candidate paragraph**
The specified `_safe_saved_article_local_related_read_href(...)` correctly ties the base to `card.candidate_story_id` and validates `#local-article-paragraph-N` as a positive integer with no leading zeros — sound defense-in-depth. It does not, however, confirm `N` corresponds to an actual non-empty paragraph in the candidate article. Acceptable since the builder is the source of truth (`_valid_paragraph_index` + `local_article_paragraph_anchor`), but add a code comment and one render test asserting the renderer trusts `candidate_story_id` format only, so the division of responsibility is explicit.

**M-4: Make base-vs-fragment validation order explicit in the builder**
The builder validates the bare `{story_id}.html` from `local_article_page_hrefs_by_story_id` via `_safe_sibling_article_href` and only then appends the `#fragment`. State explicitly that a rejected base short-circuits the whole candidate (no fragment append), so a future edit cannot construct a href from an unvalidated base.

END_OF_REVIEW

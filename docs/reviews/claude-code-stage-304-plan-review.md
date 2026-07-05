## Stage 304 Plan Review

**Verdict: APPROVE**

---

### Critical Issues

None.

---

### Important Issues

None.

---

### Minor Notes

**1. `normalize_row_one_paragraph` called on already-normalized paragraphs**

In `_local_article_reference_excerpt`, the plan calls `normalize_row_one_paragraph(paragraphs[index])`, but paragraphs stored in `article.paragraphs` have already been through `text_to_local_article_paragraphs`, which normalizes them. The call is idempotent and harmless, but the plan would benefit from a one-line comment acknowledging this is intentional defensive re-normalization (in case the function is ever called with raw paragraph lists in the future).

**2. No zh≠ en excerpt test in the generator**

The new generator tests all end up with `body.zh == body.en` because the mock extractors return English-only text, which gets copied into `paragraphs_zh`. The render test in Task 2 does cover a genuinely different zh value (`"第一段本地正文，关于 The Row 需求。"`), so the zh path is exercised at the render layer. Acceptable scope for this stage.

**3. Helper parameter name vs. call-site variable name**

`_local_article_reference_excerpt` accepts a parameter named `paragraph_indices` (matching the project-wide naming convention), but at the call site the variable passed to it is named `excerpt_indices`. This is unambiguous and consistent with the existing pattern, but a reader of the helper signature in isolation may not immediately distinguish it from the badge-matching indices. A brief docstring or comment distinguishing "name-only, limit-1 indices used for excerpt body" from "name+label indices used for paragraph badges" would be useful.

**4. Docs drift phrase casing**

`test_row_one_docs_describe_daily_local_intelligence` uses `_normalized()` which lowercases and collapses whitespace before asserting. The plan's new assertion `assert "reference cards can include saved-source paragraph excerpts" in readme` operates on the already-normalized string, which matches the proposed README sentence "Detail-page reference cards can include saved-source paragraph excerpts…" correctly. Just confirming this is not a latent case-sensitivity trap.

---

### Assessment Against Each Review Objective

**Goal, architecture, tech stack, implementation method, staged plan** — all reasonable. The goal precisely matches the product gap described (metadata-only bodies → saved-source excerpts). Architecture correctly reuses the existing `body: LocalizedText | None` field. Tech stack and commands are accurate for this codebase. TDD order (failing tests → implementation → render evidence → docs guard → verify/review/commit) is the right sequence.

**Sound next step after Stage 303** — yes. Stage 303 built the `paragraph_indices` linkage from reference items to saved paragraphs; Stage 304 uses those same indices (via the name-only `excerpt_indices` subset) to populate the body text. The progression is incremental and reversible.

**Reusing `body` vs. new schema** — correct. `RowOneLocalArticleContentItem.body` is already used for takeaway items with full paragraph text; using it for excerpt text in reference items is consistent, requires no app-contract change, and templates already render it.

**Name-matched excerpts only; unmatched and generic-label-only refs fall back to `type / label`** — correctly specified. `excerpt_indices` is derived from `[ref.name]` only (no label), and `_local_article_reference_body` returns the `fallback` string when `_local_article_reference_excerpt` returns `None`. The fallback test and the generic-label guard test both prove this.

**Broad badge matching keeps name+label; excerpt body must not use generic labels** — confirmed. `paragraph_indices` (for badges) still uses `[ref.name, ref.label]`. `excerpt_indices` uses only `[ref.name]`. The generic-label guard test (`test_build_row_one_local_articles_reference_excerpt_requires_name_match`) verifies that a paragraph containing "bag" but not "Margaux" yields `margaux.paragraph_indices == [0]` (badge still links) while `margaux.body.en == "product / bag"` (no misleading excerpt).

**Stage 303 paragraph anchor semantics preserved** — yes. The `paragraph_indices` computation in the `for ref in refs` loop is unchanged; only `excerpt_indices` is added as a separate computation.

**Homepage Daily Local Intelligence behavior preserved** — yes. Daily Local Intelligence is a downstream projection of local article `content_sections`. Since `body` was already being populated (previously to `type / label`), the projection is unaffected; it now receives richer content, not a structural change.

**Out-of-scope items kept out** — confirmed. No new schema classes, no `row-one-app/v7` or `data/edition.json` contract change, no dependency additions, no scraping or social connectors, no scheduling or image generation, no demand proof or compliance-review features.

**Tests strong enough to catch metadata-only regression** — yes. The Step 1 assertions in `test_build_row_one_local_articles_adds_content_sections_from_story_refs_and_paragraphs` will fail immediately if any matched body reverts to `brand / tracked`, `celebrity / new`, `designer / founder`, or `product / bag`. The JSON dump test in Step 4 independently catches a serialization regression. The render test in Task 2 catches an HTML rendering regression. The docs drift guard in Task 3 catches documentation staleness.

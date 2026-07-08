Here is the review.

---

## 1. Product Fit

Strong fit. The user asked for a professional daily fashion news site that organizes article content locally rather than only linking out. Stages357–359 built signal, momentum, and heat layers on top of local article data; Stage 360 completes the arc by surfacing the actual article text as readable capsules. Compact cards with excerpt, source attribution, why-it-matters, references, and deep-link anchors directly satisfy "organizes article content locally."

The four-card cap and three-paragraph-per-card cap are correctly calibrated for a scan-first homepage. The feature does not try to replace the full article detail page, only to give enough of each piece to decide what to read next.

---

## 2. Homepage Placement

Technically sound. The insertion point in the template is between `{daily_local_heat_signals_section}` and `{saved_article_content_organization_section}`, which are adjacent string interpolations in the single `render_index_html` f-string body. Adding one more variable there is the same pattern already used for Stages 357, 358, and 359. The placement test asserts index ordering in the rendered HTML, which is the correct verification approach. No DOM restructuring is needed.

---

## 3. Data Sources and Contract Isolation

The plan reuses `edition.stories`, `local_articles_by_story_id`, and `local_article_page_hrefs_by_story_id`—all three are already computed in `render_row_one_site` before `render_index_html` is called. The new argument `daily_local_article_capsules_article_hrefs_by_story_id` is the same map already passed as `daily_local_heat_signals_article_hrefs_by_story_id`, just passed again under a new parameter name. That is correct: the two sections have independent safety logic and independent rendering.

No conflict with Stages 357–359 or Saved Article Content Organization. Each of those sections has its own CSS class family, rendering function, and data path. Stage 360 does not touch any of them.

One observation worth flagging: `render_index_html` in `templates.py` takes `local_articles_by_story_id` as `dict[str, RowOneLocalArticle] | None`, while `_render_daily_local_heat_signals` receives it as `Mapping[str, RowOneLocalArticle]`. The new `_render_daily_local_article_capsules` signature in the plan uses `Mapping[str, RowOneLocalArticle]` (correct, more general). Make sure the new parameter on `render_index_html` itself also uses `Mapping` or at minimum stays consistent with the existing parameter type annotation for `local_articles_by_story_id` already on that function.

---

## 4. Link Safety Rules

The plan copies and extends the existing `_safe_daily_local_heat_signals_page_href` pattern precisely. The checks are:

- `isinstance(href, str)` — handles non-string map values
- whitespace strip equality — catches leading/trailing whitespace
- `any(character.isspace() for character in href)` — catches embedded whitespace
- no leading `.`, `/`, `//` — blocks relative traversal and absolute paths
- `PurePosixPath.parts` length == 1 — blocks nested slashes
- `.html` suffix required — blocks extensionless or other-extension targets
- `safe_local_article_story_id(stem)` — validates the filename as a known safe story ID pattern
- stem == story_id equality — blocks map-swap attacks where a valid-looking href resolves to a different story

The digest anchor `#local-article-digest` and paragraph anchors `#local-article-paragraph-N` are constructed by the renderer from the validated story ID, not from any user-supplied string, so they are safe by construction.

These rules are sufficient for the defined threat model (same-site static site, no query strings or fragment user input).

---

## 5. MVP Completeness Without Overbuilding

The content set—headline, source name, body-source label, up to three paragraph excerpts, one why-it-matters line, up to six deduplicated reference chips, and same-site digest/paragraph links—is exactly right for an MVP. It matches what a reader needs to triage an article in a few seconds.

The `paragraphs_zh` alignment check (use only when `len(paragraphs_zh) == len(paragraphs)`) is a sensible guard. The 150-char excerpt constant keeps cards compact. Ordering by current edition story order rather than heat or score is correct for a read-path section: it maintains editorial coherence without introducing a ranking subsystem.

The reference dedup by normalized name/type/label is a small but important polish detail—without it, the same brand or product could appear twice when pulled from both `entity_refs`/`product_refs`/`designer_refs` and the local article's own references.

Nothing in the plan is overbuilt. There is no scoring, no ranking model, no LLM summarization, no personalization hook.

---

## 6. Generated-Site-Only Discipline

The plan is clean on this axis. The new parameter is optional with `None` default, so existing callers of `render_index_html` require no changes. The feature is activated only when `render_row_one_site` passes `local_article_page_hrefs_by_story_id` into the new slot—which is already available at that callsite.

The site test explicitly checks that `data/edition.json`, `data/manifest.json`, and `data/runtime.json` contain none of the capsule-related strings, and that no artifact with capsule-related stems exists. The workflow guard test monkeypatches out the renderer to confirm the pipeline remains inert at the contract layer.

The prohibited behavior list in the design's Non-Goals section is comprehensive and matches the project's established discipline.

---

## 7. Template Escaping and Tests

Escaping is addressed correctly. The test fixture deliberately injects `<script>` into headlines, `<Business>` into source names, and `<b>` into paragraph text and Chinese text. The assertion that none of those strings appear raw in the output is the right verification pattern.

All display text flows through `templates.py` helpers that apply escaping before interpolation into the HTML string. The plan does not propose any `Markup(...)` bypass or `| safe` pattern.

The test coverage is thorough:
- direct render: content, ordering, caps, escaping, links
- filtering: unsafe IDs, missing articles, empty paragraphs, traversal hrefs, mismatched hrefs
- placement: ordering relative to heat signals and saved article content organization
- site integration: homepage-only presence, absence from article pages, absence from contract JSON
- CSS: all selector names verified
- docs: boundary text presence and required phrases
- workflow: monkeypatched denylist guard

The one gap: the filtering test does not explicitly assert that `../secret.html` does not appear in rendered output as a literal string. Given the safety function returns `None` and the renderer skips the card entirely, this is implicitly covered, but an explicit `assert "../secret" not in html` line would make the test self-documenting.

---

## 8. Corrections Before Implementation

These are concrete items to fix, roughly in priority order:

**Required**

1. **Type annotation consistency.** `render_index_html`'s existing `local_articles_by_story_id` parameter is typed as `dict[str, RowOneLocalArticle] | None`. The new `daily_local_article_capsules_article_hrefs_by_story_id` parameter should use `Mapping[str, str] | None` (consistent with `daily_local_heat_signals_article_hrefs_by_story_id`). Confirm the plan matches this; it does in the helper signatures, but the plan's `render_index_html` snippet only names the parameter without a full annotation example. Write it out explicitly to avoid the implementer defaulting to `dict`.

2. **Paragraph anchor index base.** The plan links to `#local-article-paragraph-N` where N is the loop index. Confirm whether the existing local article page renders anchors as `local-article-paragraph-1` (1-based) or `local-article-paragraph-0` (0-based). The plan's test asserts `local-article-paragraph-1`, which implies1-based. The `_DailyLocalArticleCapsuleParagraph.index` field and the link construction must agree. Document this explicitly in the plan's Step 3safety rules rather than leaving it implicit.

3. **Missing `article_hrefs_by_story_id=None` guard in `_daily_local_article_capsule_href`.** The helper `_daily_local_article_capsule_href` must handle `article_hrefs_by_story_id is None` as a hard `None` return, not call `.get()` on `None`. The existing `_daily_local_heat_signal_story_href` does this correctly with an explicit early return. Make sure the plan's Step 3 pseudocode is unambiguous on this; currently it says "derived" without showing the None branch.

**Recommended**

4. **Explicit `assert "../secret" not in html`** in the filtering test (as noted in §7). Small addition, high signal value.

5. **`_DailyLocalArticleCapsule.title` type.** The design says the card uses the story's `headline` field (a `str`) but also the local article's `title` field. The dataclass names it `title: LocalizedText`. If the story headline is a plain `str` and the article title is also a `str`, wrapping it in `LocalizedText` for this internal dataclass is fine—just make sure the construction site is consistent and does not accidentally pass a raw story headline string where a `LocalizedText` is expected.

6. **CSS responsive breakpoints.** The plan defines only `grid-template-columns: 1fr` for both header and grid at all widths. Existing sections (e.g., heat signals) likely define a two- or three-column grid at wider breakpoints. Add at least one `@media (min-width: ...)` rule for the grid so the four cards lay out in a two-column grid on tablet/desktop, consistent with the rest of the homepage.

7. **No test for the `paragraphs_zh` alignment guard.** The design specifies "prefer aligned `paragraphs_zh` only when it has the same length as `paragraphs`". Add a small assertion that when `len(paragraphs_zh) != len(paragraphs)`, the English paragraph text is shown in both language spans, not a misaligned Chinese paragraph.

---

**Summary:** The design and plan are technically sound and well-scoped. The three required corrections (type annotation explicitness, paragraph anchor base, `None`-guard in the href helper) are small and all fixable within Task 2Step 3 before any tests are written. The recommended items improve robustness and consistency with existing sections but are not blockers. The plan is ready to implement after those corrections.

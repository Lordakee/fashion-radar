## Stage 377 Code Review — Saved Local Article Related Reads

### Critical

None.

The original Critical (entries-only candidates admitted via `score <= 0`) is resolved: `saved_article_local_related_reads.py:169` gates on `if not shared_keys and not same_section and not same_source: return None` before scoring, so a candidate with content sections but no relationship signal is rejected. The existing `test_saved_article_local_related_reads_filters_unrelated_and_current_article` now exercises exactly that path — the unrelated candidate *does* have content sections, differs in section and source, and the test asserts `is None`; removing the line-169 guard would let the entries bonus (+5) push it through and fail the test, so the guard is regression-protected.

### Important

None.

- **Entries bonus is now two-sided** (`saved_article_local_related_reads.py:176`): `if current_has_content_sections and entries:` requires both articles to have content sections, matching the spec. Resolved.
- **Companion exclusion no longer drops content-section fragments** (`render.py:493-497`): `_companion_related_story_id_from_href` accepts `local-article-digest`, `local-article-paragraph-N`, and `local-article-content-section-N`, so any sibling the companion links to is excluded. `test_companion_related_story_ids_accepts_only_safe_sibling_hrefs` (test_row_one_render.py:3664) covers digest/paragraph/content-section acceptance plus the unsafe-prefix/absolute/`../details/`/bad-id/fragment-0 rejection set. Resolved.
- **Renderer-side href binding** (`templates.py:9399-9417`): `_safe_saved_article_local_related_read_href` re-validates against `card.candidate_story_id`, requires `page_href == f"{story_id}.html"`, and allows only `local-article-digest` / `local-article-paragraph-[1-9][0-9]*` fragments — exactly the two shapes the builder emits (`saved_article_local_related_reads.py:184-188`). The deliberate asymmetry (companion extractor is a superset; renderer is the builder's output set) is correct defense-in-depth. A mismatched-story-id card is dropped at render time and verified by `test_render_local_article_page_drops_related_read_with_mismatched_story_id_href`.
- **Escaping**: all dynamic card text (title, source_name, reason, excerpt, references) and the `href` attribute route through `_esc` (`html.escape(..., quote=True)`), verified by `test_render_local_article_page_escapes_related_reads_content`.
- **Generated-site-only boundary**: `test_stage_377_saved_local_article_related_reads_stays_generated_site_only` monkeypatches the renderer to empty and re-runs the SQLite-stable site-generation test; contract-payload assertions (test_workflows.py:691-695) confirm no related-reads keys leak into the manifest.

### Minor

**1. Dead validation guards in `_safe_sibling_article_href`**
`saved_article_local_related_reads.py:220-229`

After `clean != expected` returns at line 218 (so `clean == f"{story_id}.html"`) and `safe_local_article_story_id` passes at line 221 (story id matches `^[a-z0-9][a-z0-9-]{0,63}-[0-9a-f]{10}$`), the trailing `endswith(".html")`, whitespace, `://`, starts-with, `/`, `\\`, and `..` checks are provably unreachable — a valid story id plus `.html` cannot contain any of those characters. Harmless, but noisy. (Carried forward from rereview.)

**2. Dead `score <= 0` guard**
`saved_article_local_related_reads.py:178-179`

The line-169 guard guarantees at least one of shared_keys / same_section / same_source, yielding a minimum score of 10 (same-source only). The trailing `if score <= 0: return None` is unreachable. (Carried forward from rereview.)

**3. Redundant `card_count` field**
`saved_article_local_related_reads.py:44, 134`

`card_count` is always `len(cards)` at the sole construction site; no invariant asserts equality. Render code uses `related_reads.cards` directly, so the field is unused beyond the model. Either derive it at render time or drop it. (Carried forward from rereview / plan review.)

**4. No explicit `../details/` companion-fallback rejection assertion**
`tests/test_row_one_render.py:3664`

The companion extractor rejection case set covers `articles/`, `https://`, `/`, `../details/`, bad-id, and fragment-0 — wait, re-checking: it actually does include `"../details/safe-row-1111111111.html#local-article-digest"` at line 3680 in the rejection tuple. So this gap is closed. The only residual observation is that the acceptance tuple does not include a standalone `../details/`-shaped fallback (the `_item_href` fallback form), which is already rejected by the traversal/separator checks; an explicit assertion would merely document that path. Very low priority. (Carried forward from opencode plan-rereview.)

**5. Empty reference label renders an empty span**
`templates.py:9388` filters reference chips on `reference.name.strip()` only. A reference with a non-empty name but blank label (possible via `_rendered_reference` when both `label` and `type` normalize to empty) renders `<span></span>` for the label. Cosmetic only; no correctness or safety impact.

---

**Summary:** No Critical or Important findings. The builder, companion exclusion, sibling-href safety, renderer-side `candidate_story_id` binding, escaping, and generated-site-only boundaries are correct and adequately tested. Remaining items are informational dead-code/redundancy cleanups and one cosmetic edge.

END_OF_REVIEW

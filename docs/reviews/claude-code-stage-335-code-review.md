**Verdict: Ready**

---

**Critical issues:** None.

The security model is correct: `_safe_content_section_href` validates that only `#local-article-content-section-N` fragments (N ≥ 1, no zero-padding) are accepted, then `_reading_path_step` cross-references the card's detail path against the library allowlist before emitting any step. Path traversal, XSS, wrong fragment types, and unrecognized articles are all rejected. Tests cover every rejection case.

---

**Important issues:**

1. **Step numbering gap if a step is filtered in the template.** In `_render_saved_article_reading_path`, `enumerate(path.steps, start=1)` produces 1-based indices over the original step list, but the rendered `steps` list is then filtered for empty strings. If a middle step fails `_safe_saved_article_content_organization_href` in the template, the displayed numbers would skip (e.g. "1, 3"). This can't happen in practice — `step.detail_path` entering the template is already a validated `#local-article-content-section-N` href from the builder — but it's a latent fragility if the builder contract ever changes. Low urgency, but worth a note.

---

**Minor issues:**

1. **"Start path" link uses `path.steps[0]` rather than the first *rendered* step.** If step 0's href somehow fails the template-side safe check, `start_href` is `None` and `start_link` is suppressed (no broken link emitted), so the failure mode is graceful. But it's a subtle inconsistency with the filtered `steps` list. In practice unreachable; no action required before commit.

2. **`render_index_html` correctly omits `saved_article_reading_paths`.** The wiring in `render.py` builds the paths and passes them to `_write_saved_article_library_page` → `render_saved_article_library_html` only. `render_index_html` never receives them. This is intentional per scope and is correct.

3. **CSS grid column strategy differs from other grids.** `.saved-article-reading-paths-grid` uses `repeat(auto-fill, minmax(280px, 1fr))` while most other grids in the file use a fixed column count. This is fine — arguably better for paths since the count varies (1–4) — not a bug.

---

**Required fixes before commit/push:** None. All issues are non-blocking.

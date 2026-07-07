**Verdict: Safe to implement**

---

**Critical issues**

None.

---

**Important issues**

1. **Claude Code Important #1 is resolved (false alarm).** I verified `_safe_saved_article_content_organization_href` at `templates.py:4796` uses `_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE = re.compile(r"local-article-content-section-[1-9][0-9]*$")` (`templates.py:67`). It already accepts `#local-article-content-section-N` for N≥1 and rejects `0`, `01`, padded, JS, traversal, paragraph, and missing-hash fragments exactly as the plan's tests require. No new helper needed.

2. **`path.step_count` used for the count label is stale after renderer-level filtering.** In `_render_saved_article_reading_path` the count label reads `path.step_count`, but the renderer independently re-filters steps via `_safe_saved_article_content_organization_href`. If any step is dropped at render time (defense-in-depth path, exercised by `test_render_saved_article_library_filters_unsafe_reading_path_view_model_steps`), the card will advertise e.g. "6 steps" while rendering 1. Use `len(steps)` after the filter list comprehension, not `path.step_count`. This is the only real correctness gap; it does not breach scope or contracts.

3. **Claude Code Important #3 stands.** `test_saved_article_reading_paths_accepts_any_safe_library_route` is misnamed: both parametrized cases include an unsafe `../outside.html` route among the three entry paths and verify partial-safe fallback. Rename to e.g. `..._accepts_step_when_any_one_library_route_is_safe` to avoid misleading future maintainers.

---

**Minor issues**

1. **Builder duplicates two template-private helpers.** `_safe_content_section_href` and `_detail_path_key` in the new module re-implement `_safe_saved_article_content_organization_href` (`templates.py:4796`) and `_saved_article_library_detail_path_key` (`templates.py:4127`). Importing them is blocked by a circular dep (templates.py will import the new module), so duplication is defensible, but note it. A future refactor could move the shared fragment regex into `detail_routes.py`. Not a Stage 335 blocker.

2. **Claude Code Minor #1 stands.** The `_render_saved_article_reading_path_step` list comprehension (plan line 927) is one very long line; Ruff will flag it. Plan says "PASS after small syntax/import adjustments" — fine, just pre-note it.

3. **Claude Code Minor #2 stands.** `.saved-article-reading-paths-grid` uses `repeat(2, minmax(0, 1fr))`; a single path renders half-width. Acceptable for the 2–4 path target, but consider `repeat(auto-fill, minmax(280px, 1fr))` or document the intent.

4. **Claude Code Minor #3 stands.** `test_render_saved_article_library_reading_path_hrefs_match_local_anchor_allowlist` regex requires exactly a 10-hex story-id suffix. Fixtures in this codebase use `*-1234567890` (10 digits, all hex-valid), so it passes here, but if any fixture diverges the test will fail unexpectedly.

5. **Claude Code Minor #4 resolved.** `_count_label` exists at `templates.py:4989`; `_local_article_digest_excerpt` exists at `templates.py:6149`. Both safe to reuse.

---

**Required plan changes**

1. In `_render_saved_article_reading_path`, replace `path.step_count` in the count-label spans with the post-filter `len(steps)` (Important #2).
2. Rename `test_saved_article_reading_paths_accepts_any_safe_library_route` to reflect partial-safe fallback semantics (Important #3).

No task reordering, no scope/contract changes, no architectural blockers. The remaining Important/Minor items are pre-implementation polish, not structural.

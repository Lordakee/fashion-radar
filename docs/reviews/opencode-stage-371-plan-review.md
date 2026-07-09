# Stage 371 Plan Review — Daily Local Saved Article Organizer

Reviewed spec (`docs/superpowers/specs/2026-07-09-stage-371-...-design.md`) and plan (`...-plan.md`) against the codebase. No files edited.

## Findings by Severity

### Critical
None.

### Important

1. **Mobile CSS has no `@media` wrapper in the plan (Task 4 Step 4).** The two "mobile rules" are shown bare:
   ```css
   .daily-local-saved-article-organizer-header { grid-template-columns: 1fr; }
   .daily-local-saved-article-organizer-grid { grid-template-columns: 1fr; }
   ```
   The codebase places all such rules inside one `@media` block (`templates.py:~6680-6711`). Added bare, they share specificity with the base `repeat(4, minmax(0,1fr))` rule but come later, so the grid becomes single-column on desktop too. The render test only asserts `1fr` appears (`re.search(...grid-template-columns:\s*1fr...)`), so it passes either way — the regression is uncaught. Fix: explicitly instruct placing them inside the existing `@media` block, and add an assertion that `repeat(4, minmax(0, 1fr))` also survives.

2. **`_read_first_card` brief path hardcodes `#local-article-paragraph-1` (plan line 632).** When a brief section supplies the excerpt, the href is `f"articles/{page_href}#local-article-paragraph-1"` regardless of whether paragraph 0 exists or is non-empty. If `paragraphs[0]` is empty/missing (the article page skips empties), the anchor is dead. The brief path returns before calling `_first_paragraph`. Fix: derive the paragraph index from `_first_paragraph` (as the fallback path does), or point to a brief-section anchor if one exists.

3. **Spec/plan mismatch on `paragraph_indices`.** The spec lists "existing item-level paragraph indices" as a data source and requires "validate paragraph indices before using them"; the spec test list says "invalid paragraph indices ... are filtered." The plan's builder never reads `item.paragraph_indices`, and no test covers index validation. Either drop the spec claim or implement+test it. As written, the spec promises a behavior the plan does not deliver.

4. **`source_context` lane is largely redundant with `read_first`.** When an article has no brief section, both `_read_first_card` and `_source_context_card` call `_first_paragraph` and emit the same excerpt text against the same `#local-article-paragraph-N` href. Per-lane dedup (`seen_hrefs[lane_key]`) does not catch cross-lane duplication, so the homepage shows two near-identical cards. This weakens the "content organization over links" goal. Consider making `source_context` surface `body_source`/`source_name` context instead of re-excerpting paragraph 0.

### Minor

5. `lane.total_count` is computed but never rendered in the template; dead field.
6. `_truncate` can split mid-word; cosmetic only.
7. Render-time href-filter test (Task 3) needs a fixture card with an intentionally unsafe href to prove `_safe_daily_local_saved_article_organizer_href` rejects it. The plan references the helper but doesn't show the unsafe-href fixture; frozen dataclasses still allow direct construction, so it's feasible — just make it explicit.
8. Task 7 Step 5 pushes to `origin main` without a branch/remote check.
9. Even when paragraph 0 exists, the brief-card href `#local-article-paragraph-1` doesn't correspond to the brief-section body the excerpt came from — minor anchor/content mismatch.

## Assessment of Requested Dimensions

- **Feasibility:** Good. `safe_local_article_story_id` (`articles.py:629`, regex `^[a-z0-9][a-z0-9-]{0,63}-[0-9a-f]{10}$`), `normalize_row_one_paragraph` (`text.py:148`), `local_article_page_hrefs_by_story_id` (`render.py:201/427`), all referenced models/Literals, and the Stage 370 insertion points (`templates.py:603-604`) all exist. The `_safe_article_page_href` is a faithful copy of the proven Stage 370 validator (`daily_local_article_intelligence_brief.py:251`). Test story IDs satisfy the regex.
- **Scope:** Clean. Generated-site-only, homepage-only, no new JSON/HTML artifacts, no article/detail page edits, no collection/fetch/LLM/connector/scheduling/compliance paths.
- **TDD coverage:** RED→GREEN→lint per task across builder, render, docs, workflow. Gaps: paragraph-index validation (see #3) and unsafe-href render fixture (see #7).
- **Generated-site-only boundary:** Well-guarded — contract payload denylist, artifact-stem denylist, homepage-only render assertions, and a wrapper guard that disables the renderer and re-runs the sqlite-mutation test. The wrapper reuses `test_write_row_one_site_files_writes_local_article_without_mutating_sqlite(tmp_path)` (signature-compatible, takes only `tmp_path`).
- **App contract/artifact safety:** Strong. Explicit denylist of Stage 371 names/stems; spec enumerates every artifact not created; docs boundary paragraph is exact-matched in tests.
- **Href safety:** Builder validates page hrefs (Stage 370 pattern); section/paragraph anchors are constructed from `enumerate(..., start=1)` so N≥1 always. Render-time validator is defense-in-depth. Main gap is the hardcoded `paragraph-1` in the brief path (#2).
- **Content organization vs. links:** Yes — advances content organization. Publishes ≤180-char excerpts grouped into 4 editorial lanes with reference chips and same-site deep anchors; explicitly does not republish full articles. The one weak spot is `source_context` redundancy (#4).

## Verdict

Approve with fixes. Address Important #1 (mobile `@media`), #2 (brief-path href), #3 (paragraph_indices spec/plan mismatch), and #4 (source_context redundancy) before implementation. None are blocking enough to abandon the stage; all are local fixes within the proposed file set.

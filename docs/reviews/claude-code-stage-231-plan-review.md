# Stage 231 Plan Review
**Verdict:** APPROVE_WITH_NITS

## Critical
None.

## Important
None.

## Nits

1. **test_workflows.py:230** — The test `test_default_collectors_register_html_sitemap_and_xiaohongshu()` enumerates all registered collectors explicitly. Adding `INSTAGRAM` will require adding a line `assert isinstance(collectors[SourceType.INSTAGRAM], InstagramCollector)` to prevent this test from breaking due to incomplete coverage (the test currently checks all 6 non-MANUAL_IMPORT types; with INSTAGRAM it would need to check 7).

## Summary

**Architecture consistency:** The plan correctly mirrors Stage 212 (HTML/SITEMAP) and Stage 222 Task 1 (XIAOHONGSHU) patterns.

**InstagramSourceSettings shape (Plan line 28-35):** Sound. `Literal` is already imported in source.py:6. Field bounds (`max_posts_per_run: int = Field(default=20, gt=0, le=200)`) mirror `XiaohongshuSourceSettings.max_notes_per_run` exactly. Placement after XiaohongshuSourceSettings is consistent.

**Validator branch (Plan line 39-41):** Correct. Placement after the XIAOHONGSHU branch (source.py:107-108) is consistent. Pattern matches existing query-requiring sources (GDELT, XIAOHONGSHU).

**SourceType member + SourceDefinition field:** Plan adds `SourceType.INSTAGRAM = "instagram"` after XIAOHONGSHU (consistent with chronological order) and `instagram: InstagramSourceSettings = Field(default_factory=InstagramSourceSettings)` in SourceDefinition (consistent with gdelt/xiaohongshu pattern).

**Runner dual-guard (Plan line 22):** Correct and consistent. The plan adds `INSTAGRAM` to BOTH:
- Line ~73 extractor-creation guard (currently `{HTML, SITEMAP, XIAOHONGSHU}`) — skips creating article extractor for sources that extract their own snippets
- Line ~97 enrichment-skip set (currently `{HTML, SITEMAP, XIAOHONGSHU}`) — skips article enrichment for items already carrying extracted content

This mirrors the HTML/SITEMAP pattern from Stage 212 (5dec36b) and the XIAOHONGSHU extension from Stage 222.

**Scope discipline:** Plumbing only (no live instaloader subprocess in Stage 231); no schema change; no dependency change (instaloader stays external). Consistent with stated scope.

**Tests requiring update:** `tests/test_workflows.py:230` explicitly checks all registered collectors. Adding `INSTAGRAM` to `_default_collectors()` without updating this test will leave it incomplete (though not broken). The plan's Task 1 includes "tests" so this should be caught during implementation.

**No enumeration guards found:** Searched tests/ for patterns that iterate or parametrize over all SourceType values — none found. No scripts/check_release_hygiene.py references to SourceType.

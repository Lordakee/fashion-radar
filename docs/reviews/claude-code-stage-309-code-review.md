## Verdict

**Approve with Important fixes**

---

## Critical Findings

None.

---

## Important Findings

**`_story_article_item` is dead code (local_intelligence.py:272–290)**

The function is fully replaced by `_story_article_aggregate_item` but remains defined. No caller references it in the codebase. It matters because: (1) future maintainers may believe there are two live item-creation paths or that the non-clustering path is still a fallback; (2) it creates a false impression that clustering is optional rather than unconditional for `strongest_reads` and `heat_movers`.

Fix: delete lines 272–290 (`def _story_article_item` through its `return` statement). No callers need updating.

---

## Minor Findings

**Cluster key omits headline — intentional deviation from plan, but undocumented**

The plan specified `headline | source | full_body` as the key; the implementation uses `source | full_body`. The deviation is correct — omitting the headline allows the same saved article body to cluster even when story headlines differ across duplicates, which is what `test_build_row_one_local_article_intelligence_clusters_same_text_with_different_headlines` explicitly exercises. No fix required, but the plan step2 in Task 2 should be noted as superseded to avoid confusing future plan readers.

**`_article_cluster_text` uses full joined body instead of plan's first-paragraph-only helper**

Plan spec had `_article_primary_cluster_text` returning only the first non-empty paragraph. The implementation joins all paragraphs (and all content-section bodies). This is strictly safer against false clustering from shared opening paragraphs, and `test_build_row_one_local_article_intelligence_keeps_same_lead_different_bodies_separate` covers exactly that case. No fix needed; the behavior is better than the plan's spec.

**CSS deviates from plan spec — uses design system variables**

Plan specified `border: 1px solid rgba(31, 31, 29, 0.16)` and `border-radius: 999px` (pill). Implementation uses `border: 1px solid var(--line)` and `border-radius: 4px`. This is the right call — it reuses the established `--line` token and matches the existing detail-map card radius rather than introducing hardcoded values. No fix needed.

**`_local_article_provenance_item` label spans lack `class="local-article-provenance-label"`**

The plan spec showed label spans with this class; the implementation omits it. No corresponding CSS is defined for that class in `row_one_css()` so there is no visual regression. If label-specific styling is ever needed, the class will have to be added retroactively. Cosmetic only; no fix required.

**`_local_article_saved_paragraph_count` counts non-empty paragraphs only**

Plan spec used `str(len(article.paragraphs))`. Implementation counts paragraphs where `paragraph.strip()` is truthy. The implementation is more precise (matches what the renderer actually surfaces) and is directly asserted by `test_render_row_one_detail_skips_invalid_local_article_paragraph_links`. No fix needed; the behavior is correct.

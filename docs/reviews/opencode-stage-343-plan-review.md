I'll review the Stage 343 plan. Let me start by reading the three primary documents in parallel.
Let me verify the plan's assumptions against the actual source code, since the plan references many existing helpers.
Let me read the key sections of the source to verify the plan's integration assumptions.
Let me verify the test helpers, `Sequence` import, and check for any existing CSS to avoid collisions.
The first grep returned cross-file results. Let me directly inspect the test file and the render entry point.
Let me read the relevant test file sections directly to confirm the test helpers exist.
Let me read the section extraction helper and confirm the render signature accepts the `saved_article_content_organization` keyword.
Let me verify the test file imports (`replace`, `RowOneReference`) needed by the plan's new tests.
Let me confirm `_count_label`'s signature and the `_edition()` helper used in the plan's tests.
Let me verify the Stage 342 anchor phrase exists in both docs (the new guard depends on it), and confirm the docs guard normalization convention matches prior stages.
Let me read the existing Stage 342 docs guard to confirm the plan follows the established convention exactly.
## opencode Stage 343 Plan Review Verdict

**Verdict: The plan is acceptable and ready for implementation.** No critical or important corrections are required before proceeding.

### Design ↔ Plan consistency (Q1)
Every design requirement maps to a plan step and is verified against the actual source:
- Safe-href filtering reuses `_safe_saved_article_content_organization_href` (templates.py:6259), matching the card renderer. ✓
- Distinct-article dedupe by validated detail path, distinct-source dedupe by normalized+casefolded name, evidence dedupe by `(detail_path, strict int paragraph_index)`, capped first-seen reference chips — all present and correct. ✓
- Strict paragraph-index counting excludes bools and negatives (plan Task 2 Step 2). ✓
- Summary inserts between group header and grid (templates.py:6137–6149 structure confirms a clean insertion point). ✓
- All referenced helpers exist and are already imported: `validated_row_one_detail_relative_path`, `normalize_row_one_paragraph`, `_esc`, `_count_label` (`f"{count} {singular if count==1 else plural}"`, confirmed at templates.py:6452), `Sequence` (templates.py:4). ✓

### Claude Code review fixes (Q2)
- **IMPORTANT (workflow assertion guard): ADDRESSED.** Plan Task 3 Step 3 uses the guarded form `if 'class="saved-article-content-organization-group"' in articles_html:` and explains the rationale. ✓
- **MINOR (same-article multi-section dedup test): ADDRESSED.** Plan Task 1 Step 2 adds exactly this case (two cards, same path, different `#local-article-content-section-N` → "1 saved article", "2 evidence paragraphs"). ✓
- **MINOR (first-seen vs "recurring"):** The design actually says "first-seen" (lines 49, 60), not "recurring" — the plan is consistent with the design. The finding rested on a misread; no change needed.
- **MINOR (helper duplication):** The new `_saved_article_content_organization_detail_path_key` overlaps `_saved_article_library_detail_path_key` (templates.py:4982) but is safe in context (callers only pass hrefs already validated by the `#`-requiring safe-href filter). Claude Code left this as implementer's call. Non-blocking; optional to reuse the existing helper.

### Risk surface (Q3)
Safe href filtering, strict index counting, evidence dedupe by path+index, reference dedupe/cap/escaping, and content-organization section ordering (summary before grid; Stage 343 doc paragraph before Stage 342) are all sound. The new docs guard (Task 3 Step 2) mirrors the proven Stage 342 guard convention exactly (test_row_one_docs.py:1243–1281); the Stage 342 anchor phrase exists verbatim in both README.md:256 and docs/row-one.md:473, and `_normalized` whitespace+casefold collapsing means no stale-phrase false positive (paragraph uses "create", guard checks "creates"). Test-file imports needed by the new tests (`replace`, `RowOneReference`, organization dataclasses, `LocalizedText`, `row_one_css`) are already present (test_row_one_render.py:5,25,41–44). No existing CSS collision for the new selectors.

### Scope leakage (Q4)
None. The change stays renderer-only in `templates.py` + tests + docs. No new JSON artifacts, no app-contract keys (workflow test already guards `saved_article_content_organization` and the plan adds explicit Stage-343 negative assertions and artifact-path absences). Reference selection is first-seen, **not** frequency ranking — so no ranking behavior is introduced. No source collection, scraping, browser automation, platform APIs, analytics, recommendation, scheduling, deployment, or compliance-review behavior is added, consistent with AGENTS.md boundaries.

The plan may proceed to implementation as written.

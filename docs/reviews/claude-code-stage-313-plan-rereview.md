## Critical

No Critical findings.

## Important

**1. `safe_local_article_story_id` path never directly tested for in-edition bad IDs (plan:283–312)**

The filter-cap test puts `"bad id"` into `local_articles_by_story_id` but not into the edition, so the builder never reaches `safe_local_article_story_id(story.id)` for it. The `safe_local_article_story_id` guard at `saved_article_briefs.py` (plan:520–521) is only exercised indirectly by the `bad_path_story`, which fails the earlier `is_safe_row_one_detail_path` check before reaching the ID check. A story *in* the edition with a bad ID has no direct test coverage. Add a story with `id="bad id"` or similar to `_edition(…)` in Task 1 Step 3 so the ID guard is exercised explicitly.

**2. `RowOneSavedArticleBriefItem.people_brands` / `.products` are mutable `list` inside a `frozen=True` dataclass (plan:488–502)**

`frozen=True` prevents attribute reassignment but does not prevent `item.people_brands.append(…)`. If the existing codebase uses `tuple` for frozen-dataclass sequences (check `saved_article_coverage.py`), switching to `tuple[RowOneReference, ...]` would be consistent and makes the immutability claim true. If the existing convention already uses `list` in frozen dataclasses, this is acceptable.

## Minor

**3. `if lead is None: continue` is logically dead after the `_has_nonblank_paragraph` guard (plan:526–528)**

`_has_nonblank_paragraph` returning `True` guarantees `_first_paragraph_text` returns a value, so `_lead_text` cannot return `None` at that point. The guard is harmless defensive code but adds noise; a short comment would clarify intent.

**4. `article_count` field is stored but never consumed (plan:499–501, task 5templates)**

`RowOneSavedArticleBriefs.article_count` counts all publishable articles (including the capped-out ones) but no template renders it and no test verifies its display. This is fine if it is reserved for a future "N sources" label, but it should either be used or documented with a `# reserved` comment to avoid confusion.

**5. CSS test retrieves CSS path via `render_row_one_site(…).index_path` with no saved articles (plan:782–784)**

The CSS file is written unconditionally regardless of content, so this works correctly. However, the comment in the plan ("Expected: FAIL until render wiring exists") is slightly misleading — the test would fail because the CSS selectors are absent, not because `render_row_one_site` raises. A clearer expected-failure note would help the implementer.

**6. Minor: section title repeated in `<p class="story-section">` and `<h2>` (plan:959–966)**

Both elements render the same "Saved Article Briefs / 保存正文简报" text. This mirrors the pattern already used in adjacent sections (e.g. Saved Article Coverage), so it is likely intentional for the bilingual display pattern — acceptable if consistent with surrounding sections.

## Verdict

No Critical or Important blockers. The plan is correctly scoped: it stays within the generated-site layer, does not touch `row-one-app/v7`, `data/edition.json`, manifest/runtime contracts, schemas, detail routes, or paragraph anchors, and does not write a new JSON artifact. The two Important findings are addressable before implementation begins — add one extra fixture story to cover the ID-guard branch, and audit the `list`-vs-`tuple` convention for frozen dataclasses. The remaining items are minor polish.

## Critical
- No Critical findings.

## Important
- No Important findings remain.

**Finding 1 — bad story-id guard (resolved):** Task 1 Step 3 now creates `bad_id_story = _story("bad id", "Bad ID")` with a valid `detail_path` and passes it into `_edition(*stories, bad_path_story, bad_id_story)` *and* into `local_articles_by_story_id`. The story is in the edition, has a valid detail path, and has a matching article, so the builder reaches `safe_local_article_story_id(story.id)` and the guard is exercised directly. The `article_count == 6` / `len(items) == 4` assertion confirms it is excluded from `publishable_count`.

**Finding 2 — mutable `list` in frozen dataclass (resolved):** `RowOneSavedArticleBriefItem.people_brands` and `.products` are now typed as `tuple[RowOneReference, ...]`. The builder's `_references()` helper already returns `tuple(refs)`, so both declaration and construction are consistent and immutable.

## Minor
- The previous review's Minor items (dead `lead is None` guard, `article_count` unreferenced in templates, CSS test comment wording, bilingual header duplication) carry forward as-is — none were regressions introduced by the fixes, and none block implementation.

## Verdict
Both Important findings from the rereview are fixed. The plan and design are clear to implement.

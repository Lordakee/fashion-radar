## Verification Against Requirements

**1. Local article/content sections generated site-only** ✓
- `render.py:140-161` `_write_local_article_files` writes only to `data/articles/`; `templates.py:1896-1919` `_render_local_article` renders only into the detail HTML.
- `workflows.py:74-118` `write_daily_report_files` never calls `build_row_one_local_articles`.

**2. Not SQLite / daily report JSON / data/edition.json** ✓
- `build_row_one_local_articles` (articles.py:43-79) takes no engine and cannot write SQLite.
- `build_row_one_app_payload` (render.py:164-192) never includes local-article paragraphs; test `test_render_row_one_detail_includes_local_article_content` asserts paragraphs are absent from `edition.json` (test_row_one_render.py:330).
- `test_write_row_one_site_files_writes_local_article_without_mutating_sqlite` confirms the stored summary is unchanged (test_workflows.py:325).

**3. `row_one_article` default off** ✓
- `source.py:56` `enabled: bool = False`. The workflow-level `local_articles_enabled=True` cannot override a disabled source (`_source_for_story` returns `None`).

**4. Source matching deterministic** ✓
- articles.py:189-207: exact `source.name == story.source_name` first; hostname fallback iterates `sources` in declared order, first enabled host match wins (verified by `test_build_row_one_local_articles_uses_first_enabled_hostname_match`).

**5. Extraction/fallback nonblocking** ✓
- articles.py:133-143 wraps the extractor in `try/except Exception` and falls back to the stored summary; skipped/empty results also fall back (verified by `test_build_row_one_local_articles_falls_back_to_stored_summary_on_failure`).

**6. `data/articles` only for current stories** ✓
- render.py:145-152 filters on `current_story_ids = {story.id for story in edition.stories}` plus `safe_local_article_story_id` and non-empty `paragraphs`.

**7. Safe filenames** ✓
- `LOCAL_ARTICLE_STORY_ID_RE = ^[a-z0-9][a-z0-9-]{0,63}-[0-9a-f]{10}$` (articles.py:18) forbids separators/dots/traversal; filename is `{story_id}.json` only after `safe_local_article_story_id` passes.

## Additional Checks
- XSS: `_render_local_article` escapes paragraphs, title, and source_name; test_row_one_render.py:345-372 confirms script/img/onerror are neutralized.
- Env kill switch (`ROW_ONE_LOCAL_ARTICLES`) only disables and cannot enable against a disabled source (articles.py:32-40).
- HTTP client/robots checker cached per source and closed in `finally` (articles.py:61-79).
- `_write_local_article_files` sorts by `story_id` for deterministic output order.

## Documentation Note (Minor, not reported as Important)
docs/row-one.md:295-296 states `data/articles/<story-id>.json` is written "when ... extraction succeeds", but the code also writes when the summary fallback succeeds. Behavior is safe, tested, and intentional; the bullet is slightly narrower than reality. Flagging as Minor only.

## Conclusion

**No Critical or Important findings.**

## Post-review fix

The minor documentation note about `data/articles/<story-id>.json` wording was
addressed in `docs/row-one.md` by documenting both article extraction and
stored-summary fallback.

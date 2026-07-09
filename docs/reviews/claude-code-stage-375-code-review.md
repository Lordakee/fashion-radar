## Important

**1. `_resolve_articles` silently filters the supplied mapping, violating the spec's "uses that exact validated set" guarantee.**

`local_article_content_health.py:153–158` applies `safe_local_article_story_id(story_id) and article.story_id == story_id` as a filter even when `articles` is supplied. For the strict path, `_load_article_sidecars` already enforces both invariants and raises on any violation, so no entry should ever be dropped. But the silent drop means content health could silently under-count articles if a future caller passes an un-validated mapping, and no test covers the case where a supplied article fails either filter condition. The spec says "uses that exact validated set"; a silent filter is not exact. The discovery path (no `articles` supplied) legitimately needs both checks; the supplied path should trust the already-validated mapping and should not filter.

**2. The named test `test_ops_check_text_includes_local_article_content_health` required by plan Task 6, Step 1 is not present in `test_row_one_ops_check.py`.**

Coverage for the ops-check human text line exists in `test_row_one_cli.py` via the augmented `test_row_one_ops_check_human_output_is_read_only` fixture, but that is a different module and a different test name than the plan requires. The plan's Task 6 ops-check test list is therefore incomplete as written. This is testable coverage, not a gap in behavior, but it means the plan's task checklist cannot be signed off as complete.

**3. The `_IdCollectingHTMLParser` case-normalization change silently alters existing `status_integrity.py` local-intelligence anchor validation, not only new content-health code.**

The old `_IdCollectingHTMLParser` in `status_integrity.py` used `name == "id"` (exact case). The new shared parser in `local_article_anchors.py:41` uses `name.lower() == "id"`. `_require_html_anchor` in `status_integrity.py` now uses `parse_html_ids` from the shared module and therefore now accepts `ID="..."`, `Id="..."` etc. in existing detail-page fragment validation for local-intelligence items. This is strictly more correct per the HTML spec, but it is an implicit behavioral expansion to code that predates Stage 375 and is not called out in the spec or plan as a migration. Any existing detail pages that relied on the old exact-case behavior now behave differently.

---

## Minor

**4. `article_count` in the content-health human output is labelled "saved local articles" but counts only renderable sidecars (those with non-empty paragraphs), not total sidecars.**

The site-metrics line just above the content-health line prints the total count from `local_article_site_metrics`. If a site has 3 sidecars but 1 is skipped (empty paragraphs), the output reads `Saved local articles: 3` then `Local article content: ready (2 saved local articles, 4 paragraph anchors)`. The3→2 divergence is spec-correct but has no label to distinguish "renderable" from "total". A user would reasonably expect the same count in both lines.

**5. In `test_stage_375_local_article_content_health_stays_generated_site_only`, the monkeypatch lambdas return `None` rather than raising, making the "should not be called" intent implicit.**

`lambda *_args, **_kwargs: None` succeeds silently. If `build_row_one_local_article_content_health` were inadvertently called during site generation, the test would not fail at the call site — it would fail downstream when `RowOneGeneratedSiteHealth(local_article_content=None)` propagates a `None` through `row_one_local_article_content_health_payload`. Sibling tests for earlier stages (e.g., Stage 374 equivalent) presumably use the same pattern, so this is consistent, but the intent is "assert not called" and a more direct approach (e.g., `lambda *a, **k: (_ for _ in ()).throw(AssertionError(...))`) or `pytest.fail` inside the lambda would document this better.

**6. In `test_content_health_discovery_ignores_unsafe_sidecar_stems`, writing `"unsafe.html"` to the articles directory is unreachable by the `glob("*.json")` pattern and tests nothing.**

`articles_dir.glob("*.json")` never matches `"unsafe.html"`. Only `"unsafe story.json"` (the entry with a space in the stem) exercises the `safe_local_article_story_id` guard. The `.html` write is dead test code.

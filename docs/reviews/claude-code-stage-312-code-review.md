Now I have a complete picture of all changed files. Here is the full review.

---

## Stage 312 Code Review

### No Critical Findings

The implementation is contract-clean. No schema changes, no new JSON artifacts, no detail-route or paragraph-anchor changes, no `row-one-app/v7` mutations. `safe_local_article_story_id` is correctly called, corpus metrics use the full article set, and the read queue cap is applied only to `items`. All href rendering goes through `_safe_saved_article_coverage_href`, which validates both the base path via `_validated_detail_relative_path` and requires the fragment to be exactly `"local-article-digest"`. No XSS risk found.

---

### Important

**I1 — Builder silently produces un-renderable items when `story.detail_path` is malformed; path not tested**

`saved_article_coverage.py:68`:

```python
detail_path=f"{story.detail_path}#local-article-digest",
```

`story.detail_path` is appended to without first calling `_validated_detail_relative_path`. In `render_row_one_site`, this is benign because `_validate_unique_story_routes` raises an exception before this line is ever reached. But `build_row_one_saved_article_coverage` is called directly in tests and could be called from outside the render pipeline with an edition whose stories have bad `detail_path` values. In that situation, `_safe_saved_article_coverage_href` silently returns `None`, and `_render_saved_article_coverage_card` returns `""`. The card vanishes from the grid with no error. The `coverage.items` list claims N cards, the HTML renders fewer.

The review prompt says tests cover "bad coverage href filtering", but `test_row_one_saved_article_coverage.py` only exercises the builder, not this silent-drop path. `test_row_one_render.py` likely covers it at the template level, but the gap is the builder itself: an item whose `detail_path` is bad is included in `coverage.items` with a fragment-appended path that will silently disappear when rendered.

**Fix options (pick one):**
- Validate `story.detail_path` inside `build_row_one_saved_article_coverage` and skip items that fail, so `coverage.items` and the rendered cards remain in agreement.
- Add a unit test to `test_row_one_saved_article_coverage.py` asserting that a story with a bad `detail_path` is excluded from `coverage.items` entirely (making the silent-drop explicit and expected), while also covering the template-level rendering omission in `test_row_one_render.py`.

The second option is lower-churn and consistent with the rest of the codebase's render-time filtering pattern, but the behaviour should be visible in the test suite.

---

### Minor

**M1 — Card headline renders English-only, breaking the `data-lang` span pattern**

`templates.py:2151`:

```python
<strong>{_esc(item.title.en)}</strong>
```

Every other bilingual string in this template is wrapped in `data-lang` spans. Both `item.title.zh` and `item.title.en` are set to `story.headline` (the same value per `saved_article_coverage.py:65`), so there is no functional regression today. But the inconsistency is a pattern break: if zh headlines were ever differentiated (or if this is copied as a template for future sections), the silently-English-only render will not be obvious. The idiomatic form is:

```python
<strong>
  <span data-lang="en">{_esc(item.title.en)}</span>
  <span data-lang="zh">{_esc(item.title.zh)}</span>
</strong>
```

**M2 — `coverage.article_count == 0` guard in `_render_saved_article_coverage` is unreachable**

`templates.py:2045`:

```python
if coverage is None or coverage.article_count == 0:
```

`build_row_one_saved_article_coverage` returns `None` whenever there are no publishable articles — it never returns a `RowOneSavedArticleCoverage` with `article_count == 0`. The second condition is dead code. Not harmful, but it implies a construction path that doesn't exist and slightly obscures the function's actual invariant. A comment would clarify, or the guard can simply be `if coverage is None:`.

---

### Summary

| Severity | Count | Notes |
|---|---|---|
| Critical | 0 | |
| Important | 1 | Builder includes un-renderable items; no test asserts the silent-drop path |
| Minor | 2 | Bilingual pattern break on card headline; unreachable `article_count == 0` guard |

**Residual risk/test gaps:** The builder-level test suite covers the primary filter conditions (not-in-edition, unsafe ID, blank paragraphs) and the 4-item cap well. The one gap worth addressing before commit is I1: either pre-validate `story.detail_path` in `build_row_one_saved_article_coverage` to keep `coverage.items` consistent with what the template will actually render, or add a test that explicitly asserts the bad-href-silent-omission contract so it becomes a documented and tested behavior rather than an undocumented one.

## Stage 331 Re-Review

All 338 focused tests passed (6.69s). Here is the verdict on each finding.

---

### Prior Important Findings

**Finding 1 — Missing suppression render test**
✅ **CLOSED.**
`test_render_row_one_detail_suppresses_skipped_local_article` is present at `tests/test_row_one_render.py` (appended after line 1278in the diff). The test:
- Constructs a `RowOneLocalArticle` with `body_source="skipped"`, `skipped=True`, `reason="no_publishable_paragraphs"`, and no `paragraphs` argument (empty list by default).
- Renders via `render_row_one_site`.
- Asserts `'id="local-article"' not in detail_html` and `"no_publishable_paragraphs" not in detail_html`.

The suppression path is correct: `_render_local_article_paragraphs` returns `[]` for empty `paragraphs`, causing `_render_local_article` to return `""` at `templates.py:5458-5459`, which propagates to a missing section in the rendered HTML.

**Finding 2 — `uv.lock` should be excluded**
✅ **CLOSED.**
The plan's final `git add` command (confirmed in plan file) lists the Stage 331
files and does **not** include `uv.lock`. Final release verification restored
`uv.lock` to the committed public-PyPI form, so it is not modified in the final
worktree.

**Additional fixes reported as applied**
- "no publishable saved body" wording:✅ `docs/row-one.md` says"`skipped` marks no publishable saved body"; `README.md` says "`skipped` means no publishable saved body was written".
- Plan `git add` list includes `tests/test_row_one_cli.py`: ✅ confirmed.
- Plan `git add` list omits `docs/first-run.md` and `tests/test_cli_docs.py`: ✅ confirmed; neither file appears in the git status as modified.

---

### New Findings

**Critical:** none.

**Important:** none.

**Minor — stale return annotation on `_fallback_story_summary_article` (`articles.py`)**

The only `return None` in `_fallback_story_summary_article` was replaced with `return _skipped_story_local_article(...)`, so the function now always returns a `RowOneLocalArticle`. The annotation still reads `-> RowOneLocalArticle | None`. This is harmless at runtime (Pydantic validates the model; the sole caller `_build_story_local_article` passes the return straight through its own `-> RowOneLocalArticle | None` signature), but the annotation is stale and could mislead a future reader into thinking `None` is possible. Updating the annotation to `-> RowOneLocalArticle` is low-risk and non-urgent.

**Minor — suppression relies on implicit invariant, not an explicit gate**

`id="local-article"` is suppressed for `body_source="skipped"` articles because `_render_local_article` short-circuits on empty paragraphs (`templates.py:5458-5459`), not because it checks `article.body_source == "skipped"`. This is currently safe: `_skipped_story_local_article` never sets `paragraphs`, so the invariant holds. But there is no render-layer guard that would prevent a future code path from accidentally writing a skipped article with non-empty paragraphs and inadvertently rendering a `local-article` section. The existing test directly covers the current behaviour; this is an observation for future maintainers, not a defect today.

---

### Summary

No Critical or Important findings remain or were introduced. The two prior Important findings are fully closed. The commit list is correct; `uv.lock` is excluded. The change is ready to proceed.

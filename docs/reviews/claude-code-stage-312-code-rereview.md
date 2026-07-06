## Stage 312 Code Re-Review Findings

---

### Finding 1 (Important — Original)✅ Fixed

**Claim:** `build_row_one_saved_article_coverage()` included items whose `story.detail_path` would be rejected by the template href sanitizer, causing `coverage.items` and rendered cards to diverge.

**Verdict: Fixed and correctly implemented.**

`saved_article_coverage.py:52–53` adds an early builder-level guard:

```python
if not _safe_detail_path(story.detail_path):
    continue
```

The `_safe_detail_path()` implementation (`saved_article_coverage.py:105–114`) is logically equivalent to `_validated_detail_relative_path()` in `templates.py:3893–3905`. Both check the same five conditions (not absolute, exactly 2 parts, first part `"details"`, no `..` traversal, filename matches `_DETAIL_FILENAME_RE`). The test at `test_row_one_saved_article_coverage.py:146–162` confirms the path `"../private.html"` is excluded from `coverage.items` and the count, which is the precise divergence scenario from the original finding.

---

### Finding 2 (Minor — Original) ✅ Fixed

**Claim:** Saved article coverage card headline used English-only text instead of the bilingual `data-lang` span pattern.

**Verdict: Fixed.**

`templates.py:2150–2154` now renders the card headline as:

```html
<strong>
  <span data-lang="en">{title.en}</span>
  <span data-lang="zh">{title.zh}</span>
</strong>
```

The builder sets `title=LocalizedText(zh=story.headline, en=story.headline)` — both sides carry the same string since `headline` is a single-language field. This matches the treatment of other non-bilingual content elsewhere (e.g. signal `name`). The rendering pattern is correct.

---

### Finding 3 (Minor — Original) ✅ Fixed

**Claim:** `_render_saved_article_coverage()` had an unreachable `coverage.article_count == 0` guard.

**Verdict: Fixed.**

`templates.py:2044–2070` now has only:

```python
def _render_saved_article_coverage(coverage: RowOneSavedArticleCoverage | None) -> str:
    if coverage is None:
        return ""
```

No `article_count == 0` guard. Since the builder already returns `None` when no publishable articles exist, this is the correct single check.

---

### No Critical or Important Findings Remain

All three original findings are resolved. Two low-severity residual notes:

**Residual Minor1 — `_DETAIL_FILENAME_RE` defined twice.**
The regex `r"^[a-z0-9][a-z0-9-]{0,63}-[0-9a-f]{10}\.html$"` is copy-defined at the module level in both `saved_article_coverage.py:12` and `templates.py:39`. The values are currently identical and the render integration tests would catch a divergence, but a future edit to one without the other is a silent maintenance trap. Not a blocking issue; worth a follow-up extraction to a shared constant (e.g. in `utils.py` or a dedicated `paths.py`).

**Residual Minor 2 — Bilingual span structure not assertion-tested in render tests.**
`test_render_row_one_site_includes_saved_article_coverage` (line 1731) checks that the escaped headline string appears somewhere inside `coverage_html`, but does not explicitly assert the `<span data-lang="en">` / `<span data-lang="zh">` wrapping. The template code guarantees correctness by construction, so this is low risk, but a targeted assertion would lock in the fix against future regressions.

Neither residual is blocking for shipping Stage 312.

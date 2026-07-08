---

## Stage 342Plan Review

**Verdict: Two critical bugs in the proposed implementation code require fixing before the TDD green phase. Plan is otherwise approved.**

---

### Finding 1 — CRITICAL: Off-by-one in content section enumeration

**Location:** Plan Task 2, Step 3 — `_local_article_paragraph_contexts` helper

The proposed helper uses:
```python
for section_position, section in enumerate(article.content_sections):section_anchor = _local_article_content_section_anchor(section_position)
```

Every existing callsite that maps sections to anchor IDs uses `start=1`:
- `templates.py:7376` — `enumerate(article.content_sections[:...], start=1)`
- `templates.py:7946` — `enumerate(article.content_sections, start=1)`
- `templates.py:7999` — `enumerate(article.content_sections, start=1)`
- `templates.py:8188` — `enumerate(article.content_sections, start=1)` (evidence entries, canonical parallel)

`_local_article_content_section_anchor(position)` returns `f"local-article-content-section-{position}"` verbatim. Zero-based enumeration produces `#local-article-content-section-0` for the first section, but the section element rendered on the page carries `id="local-article-content-section-1"`. Every context cue link would point to a non-existent anchor. The test in Task 1 Step 4 also asserts `href="#local-article-content-section-1"`, so it would catch this — but only after a confusing red failure.

**Fix:** `enumerate(article.content_sections, start=1)`.

---

### Finding 2 — CRITICAL: Wrong first argument to `_strict_valid_local_article_paragraph_indices`

**Location:** Plan Task 2, Step 3 — `_local_article_paragraph_contexts` helper, first statement in body

The proposed helper opens with:
```python
valid_indices = _strict_valid_local_article_paragraph_indices(
    article.paragraphs,
    rendered_indices=rendered_indices,
)
```

`article.paragraphs` is `list[str]` — paragraph text, not index values. `_strict_valid_local_article_paragraph_indices` (`templates.py:8164`) checks `isinstance(index, int) or isinstance(index, bool)` for every element it iterates over. All strings fail that check, so the function returns `[]`. The subsequent per-item loop then checks `paragraph_index not in valid_indices`, which is always `True`, so no context cue is ever added. The helper would silently return an empty dict for every article.

The canonical pattern is in the evidence function (`templates.py:8190`):
```python
valid_indices = _strict_valid_local_article_paragraph_indices(
    item.paragraph_indices,   # ← the item's indices, not the paragraphs list
    rendered_indices,
)
```

The simplest correct approach is to compute the valid rendered set once before the section loop (which the helper already receives as `rendered_indices`) and do the per-item strict-bool/negative/range check inside the loop using `item.paragraph_indices`:

```python
for section_position, section in enumerate(article.content_sections, start=1):
    section_anchor = _local_article_content_section_anchor(section_position)
    ...
    for item in section.items:
        for paragraph_index in _strict_valid_local_article_paragraph_indices(
            item.paragraph_indices, rendered_indices
        ):
            ...
```

This matches the evidence function pattern exactly and eliminates the stale `valid_indices` variable at the top.

---

### Finding 3 — IMPORTANT: `rendered_indices=None` default is latently unsafe

**Location:** Plan Task 2, Step 3 — helper signature

```python
def _local_article_paragraph_contexts(
    article:RowOneLocalArticle,
    *,
    rendered_indices: set[int] | None = None,
) -> dict[int, list[_LocalArticleParagraphContextCue]]:
```

If Finding 2 is fixed as described above, a caller passing `rendered_indices=None` would invoke `_strict_valid_local_article_paragraph_indices(item.paragraph_indices, None)`, which crashes with `TypeError: argument of type 'NoneType' is not iterable` when it hits `if index not in rendered_indices`. The renderer always provides the set, but the `None` default makes the API a footgun.

**Fix (two options):** Remove the default and make `rendered_indices` required, or call `_local_article_rendered_paragraph_indices(article)` inside the helper as the fallback:
```python
if rendered_indices is None:
    rendered_indices = _local_article_rendered_paragraph_indices(article)
```

Either matches the existing style; the internal fallback is slightly more ergonomic for tests that don't need to pre-compute the set.

---

### Finding 4 — MINOR: Test count assertion in Task 1 Step 4 needs verification

**Location:** Plan Task 1, Step 4

```python
assert html.count('href="#local-article-content-section-1"') == 2
```

The test collapses `content_sections` to a single section and sets `paragraph_indices=[True, 0, 0, -1, 99, 1]`. After filtering, valid indices are 0 and 1. With Fix 1applied (1-based), that section maps to `#local-article-content-section-1`. The content section navigation panel also contributes at least one `href="#local-article-content-section-1"` link. Depending on how many navigation links the information panel generates, the count may be 3, not 2. Verify with a real run during TDD Step 8; adjust the count or switch to `>=` if needed.

---

### Questions3–5: No further issues

**Paragraph indices, blank paragraphs, bilingual rendering, escaping, anchors:** Existing `_local_article_rendered_paragraph_indices` correctly excludes blank paragraphs (same guard used in `_render_local_article_paragraphs`). `_esc` is applied to both `entry.anchor` and `entry.label`. Existing bilingual span structure in `_render_local_article_paragraphs` is preserved; the plan inserts the context span before the text content, not inside either `data-lang` span. The `data-lang="en"` / `data-lang="zh"` prefix spans in `_render_local_article_paragraph_context` follow the same bilingual convention used across the file.

**Scope boundaries:** No new models, JSON artifacts, app contract keys, or data extraction paths. The workflow test guards in Task 3 Step 3 are comprehensive; the artifact absence list and contract-key negative assertions are sufficient.

**Tests:** The CSS selector test, invalid-index test, escaping/cap test, information panel test, and workflow HTML-only test are well-scoped. TDD ordering (fail first, then implement) is correct.

---

### Summary of required fixes

| # | Severity | Location | Fix |
|---|----------|----------|-----|
| 1 | Critical | Task 2 Step 3 — `enumerate(article.content_sections)` | Add `start=1` |
| 2 | Critical | Task 2 Step 3 — `_strict_valid_local_article_paragraph_indices(article.paragraphs, ...)` | Replace with per-item call over `item.paragraph_indices` |
| 3 | Important | Task 2 Step 3 — `rendered_indices: set[int] \| None = None` | Require the param or add an internal `_local_article_rendered_paragraph_indices` fallback |
| 4 | Minor | Task 1 Step 4 — `html.count(...) == 2` | Verify count during TDD; adjust if 3 |

Once fixes1–3 are applied to the implementation code, the plan is approved for implementation.

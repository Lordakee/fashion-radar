---

## Stage 325 Code Review

### Files reviewed
- `src/fashion_radar/row_one/templates.py` (diff only)
- `tests/test_row_one_render.py` (diff only)

---

### Critical findings

None.

---

### Important findings

None.

---

### Minor suggestions

**1. `body.zh.strip()` silently assumes `zh` is a non-None `str`**

```python
zh = _local_article_paragraph_evidence_body(body.zh) if body.zh.strip() else en
```

The old code passed `body.zh` directly to `_local_article_paragraph_evidence_body()`, so the non-None assumption is pre-existing and not a regression introduced here. Still worth noting: if `LocalizedText.zh` is ever widened to `Optional[str]`, this will raise an `AttributeError` rather than falling back gracefully. No action needed now, but it is a latent fragility.

**2. The empty-refs test does not assert the `</div>` closes cleanly**

The test checks `"<div></div>" not in evidence_html`, which is correct for the stated goal. It does not assert that the support `<div>` itself still closes (i.e., `</div>` is present). This is not a gap that would hide a real bug — the structural close is part of the f-string literal, not the conditional path — but a positive assertion like `'class="local-article-paragraph-evidence-support"' in evidence_html` is already there and that is sufficient.

**3. Map-slice assertion uses `.index()` twice on the same string**

```python
map_html = detail_html[
    detail_html.index('class="local-article-map"') : detail_html.index(
        'id="local-article-paragraph-evidence"'
    )
]
```

The two `.index()` calls are not guarded against the case where either marker appears more than once. Given these are unique IDs/classes in the detail page this is fine in practice, and the ordering assertion above it already guarantees both markers exist before this slice is taken. No change needed.

---

### Review of each Stage 324 polish item

**Item 1 — omit empty refs wrapper**

```python
refs = "".join(_render_local_article_paragraph_evidence_ref(ref) for ref in item.references)
refs_html = f"                <div>{refs}</div>\n" if refs else ""
```

Correct. `"".join(...)` over an empty list yields `""`, which is falsy, so the wrapper is suppressed. The indentation of `refs_html` is consistent with the surrounding `body` string (both use 16-space indent). The `<div></div>` test confirms this behaviour.

**Item 2 — Chinese body fallback**

```python
def _local_article_paragraph_evidence_body_text(body: LocalizedText) -> LocalizedText:
    en = _local_article_paragraph_evidence_body(body.en)
    zh = _local_article_paragraph_evidence_body(body.zh) if body.zh.strip() else en
    return LocalizedText(en=en, zh=zh)
```

Correct. Normalization and truncation are applied to `body.en` first; that processed value is reused as `zh` on blank input rather than re-processing `body.en` a second time — so both spans are byte-for-byte identical when the fallback fires. The test uses `zh="   "` (whitespace-only) and `<` in the English body, verifying both the fallback path and that `_esc()` is applied to the fallback result, not bypassed.

**Item 3 — map link assertion**

The slice approach is the right call here: it restricts the `href` search to the map element rather than anywhere in the page, making the assertion precise. Combined with the existing ordering assertions, the test now verifies structure, position, and linkage together.

---

### Scope boundary check

- No changes outside `templates.py` and `test_row_one_render.py` (plus doc artifacts).
- No Pydantic model, JSON contract, schema, or dependency changes.
- All2153 tests pass; linting and lock-file checks pass.

---

### Verdict

**Approved to commit.** The three polish items are implemented correctly and are fully covered by the new tests. No regressions introduced in existing ROW ONE render paths.

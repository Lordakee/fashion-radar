## Stage 301 Code Re-Review

**Focus**: I1 — `_safe_daily_local_intelligence_href` fragment-rejection test coverage

---

### What Was Read

- `tests/test_row_one_render.py` lines 826–845 (new parametrized test)
- `src/fashion_radar/row_one/templates.py` lines 1836–1844 (implementation)
- `docs/reviews/claude-code-stage-301-code-review.md` (prior review)

---

### Checklist Against Review Objective

The new test is `test_safe_daily_local_intelligence_href_accepts_only_safe_detail_links` at lines 826–845. Seven parametrized cases:

| Case | Input | Expected | Covers |
|------|-------|----------|--------|
| 1 | `"details/the-row-signal-1234567890.html"` | same string | ✅ accepted bare detail link |
| 2 | `"details/the-row-signal-1234567890.html#local-article"` | same string | ✅ accepted exact `#local-article` |
| 3 | `"details/the-row-signal-1234567890.html#summary"` | `None` | ✅ invalid fragment |
| 4 | `"details/the-row-signal-1234567890.html#local-article#extra"` | `None` | ✅ multiple fragments |
| 5 | `"../details/the-row-signal-1234567890.html#local-article"` | `None` | ✅ path traversal |
| 6 | `"javascript:alert(1)"` | `None` | ✅ unsafe scheme |
| 7 | `None` | `None` | ✅ non-string input |

All seven categories from the review objective are present.

---

### Is the Test Meaningful?

The implementation body is four branches:

```python
def _safe_daily_local_intelligence_href(href: object) -> str | None:
    if not isinstance(href, str):          # → case 7
        return None
    if "#" not in href:                    # → case 1(accept), implicitly cases 5/6 (reject via _validated_detail_relative_path)
        return href if _validated_detail_relative_path(href) is not None else None
    path, fragment = href.split("#", 1)
    if fragment != "local-article":        # → cases 3, 4 (reject)
        return None
    return href if _validated_detail_relative_path(path) is not None else None  # → case 2 (accept), case 5 rejection via base path
```

Every branch is exercised. Cases 3 and 4 prove the critical `fragment != "local-article"` guard. Case 4 specifically proves that `split("#", 1)` causes `fragment = "local-article#extra"`, which correctly fails the equality check — the exact nuance that was identified as the regression risk in I1. The test is meaningful, not just a smoke test.

---

### Import and Style Check

- `_safe_daily_local_intelligence_href` is added to the existing import from `fashion_radar.row_one.templates` (line 32–34). No new import block; no disruption.
- `@pytest.mark.parametrize` with `("href", "expected")` tuple and type annotation `href: object, expected: str | None` matches the file's existing parametrized test style (see `test_render_row_one_site_rejects_malformed_detail_paths` at line 1714).
- No `tmp_path`, no disk I/O, no mock — the test is a fast, pure unit test. No fragility concerns.

---

### New Critical Issues

None.

---

### New Important Issues

None.

---

### Minor Notes

**n1. No case for a non-`details/`-prefixed bare path.**
An input like `"other/foo.html"` (no fragment, fails `_validated_detail_relative_path`) is not parametrized. That rejection path is covered indirectly by cases 5 and 6, which both go through `_validated_detail_relative_path` and return `None`. The gap is cosmetic — not a correctness risk.

**n2. Empty string not tested.**  
`""` is a valid `str`, has no `#`, and `_validated_detail_relative_path("")` returns `None`, so `_safe_daily_local_intelligence_href("")` returns `None`. Not tested, but the behavior is correct and the case is low risk.

---

### Verdict

**APPROVE**

I1 is resolved. The parametrized test covers all seven cases from the review objective, exercises every branch of the implementation including the multi-fragment edge case, introduces no import or style issues, and is not fragile. The prior minor notes (n1–n6from the original review) are unchanged in status — none were blocking and none are affected by this change. Safe to merge.

I have all the diffs and design documents needed. Here is the review.

---

## Stage 358 Code Review

### Critical Issues — None

No correctness bugs, data leaks into contracts, or unsafe rendering paths found.

---

### Important Issues

**1. `_write_local_article_pages()` parameter coupling is asymmetric**
`render.py:392–414`

The function accepts `local_article_page_hrefs_by_detail_path` independently from `local_article_page_specs`. If someone passes only `hrefs_by_detail_path=<non-None>` without `local_article_page_specs`, the function computes specs itself and overwrites `hrefs_by_detail_path` with the passed value — which may be derived from a *different* spec run. In `render_row_one_site()` both are always passed together, so this can't actually bite in production, but the signature allows the mismatch. This isn't a bug today, but it's a latent inconsistency worth a short comment or assertion (e.g. "both or neither").

**2. CSS test misses `.daily-local-signal-momentum-counts`**
`tests/test_row_one_render.py:11463`

`test_row_one_css_includes_daily_local_signal_momentum_styles` asserts 9 selectors but the CSS adds10. `.daily-local-signal-momentum-counts` is defined in the stylesheet and emitted in the template's counts `<div>`, but it's not in the test tuple. The class is present and correct in the CSS; only the coverage assertion is missing. Should be added before commit.

---

### Minor Issues

**3. Redundant checks in `_safe_daily_local_signal_momentum_page_href()`**
`templates.py` (new function)

`path.is_absolute()` cannot be true after `href.startswith((".", "/", "//"))` already rejects absolute paths. Likewise `".." in path.parts` is unreachable when `len(path.parts) != 1`. Belt-and-suspenders is fine for security-sensitive validation — just noting the redundancy so future maintainers don't add more layers needlessly.

**4. Unnecessary `list()` / `dict()` defensive copies in `_write_local_article_pages()`**
`render.py:392–414`

```python
page_specs = list(local_article_page_specs) if local_article_page_specs is not None else ...
hrefs_by_detail_path = dict(local_article_page_hrefs_by_detail_path) if ... else ...
```

The function only reads both values; it never mutates them. The copies are harmless but add noise. Fine to leave for later.

**5. Gratuitous outer parens in one integration-test assertion**
`tests/test_row_one_render.py:4004`

```python
assert 'href="articles/..."' in (section_html)
```

The parentheses around `section_html` do nothing. Trivial nit.

**6. Pre-existing style carry-over in old `hrefs_by_detail_path` comprehension**
`render.py` (old code, now removed) used `story` (non-underscore) for an unused binding in the dict comprehension. The new `_local_article_page_hrefs_by_detail_path()` helper correctly uses `_story`. No new issue introduced; the cleanup was done correctly.

---

### Checklist Against Requirements

| Requirement | Status |
|---|---|
| Section renders only on `index.html` | ✅ Verified by integration test and monkeypatch wrapper |
| Placement: after `.daily-local-key-signals-digest`, before `.saved-article-content-organization` | ✅ Verified by ordering test |
| Reuses Stage 350 dataclasses/builder without mutation | ✅ Builder not changed; data passed by reference |
| Prefers `articles/<id>.html#local-article-digest` when safe | ✅ `_daily_local_signal_momentum_support_href()` first tries mapped href |
| Falls back to `details/<safe>.html#local-article-digest` | ✅ `_safe_daily_local_signal_momentum_detail_href()` delegates to existing `safe_row_one_detail_fragment_href` |
| Filters unsafe links, traversal, external schemes, wrong fragments | ✅ Covered in both unit and integration test; unsafe supports assert-absent |
| Mapping values validated (traversal, nesting, non-`.html`) | ✅ `_safe_daily_local_signal_momentum_page_href()` is thorough |
| All display text escaped | ✅ Every user-facing string goes through `_esc()` |
| Mapping computed once in `render_row_one_site()` flow | ✅ Computed once, passed to `render_index_html` and `_write_local_article_pages` |
| No JSON artifacts, app contracts, schemas touched | ✅ Test suite guards (workflows + docs + render) all pass |
| Docs boundary statement present and ordered correctly | ✅ Stage 358 before Stage 357 in both README and docs |

---

### Ready to Commit?

**Yes, after fixing item 2** — the missing `.daily-local-signal-momentum-counts` assertion in `test_row_one_css_includes_daily_local_signal_momentum_styles`. Everything else is either verified correct or minor enough to defer. Once tests and the lint gate pass with that one assertion added, this is clean to commit.

---

## Follow-up

- Added `.daily-local-signal-momentum-counts` to the CSS selector coverage test.
- Added a regression test for orphaned `local_article_page_hrefs_by_detail_path`
  input and updated `_write_local_article_pages(...)` to reject a mapping passed
  without matching `local_article_page_specs`.
- Verified:
  - `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_write_local_article_pages_rejects_orphaned_href_mapping tests/test_row_one_render.py::test_row_one_css_includes_daily_local_signal_momentum_styles -q`
  - `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/render.py tests/test_row_one_render.py`
  - `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/render.py tests/test_row_one_render.py`

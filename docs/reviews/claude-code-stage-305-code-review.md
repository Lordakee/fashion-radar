## Stage 305 Code Review

**Base:** `e75254c` → working tree
**Files reviewed:** `templates.py`, `test_row_one_render.py`, `test_row_one_docs.py`, `docs/row-one.md`, `README.md`

---

### Verdict: APPROVE

---

### Critical Issues

None.

---

### Important Issues

None.

---

### Minor Notes

**1. `_render_local_article_map` — `#local-article-body` link always emitted when map renders**

For articles that have `content_sections` but zero `paragraphs`, the Full saved text link targets an empty `#local-article-body` div. The anchor exists, so it is not a dead link, and the requirements do not prohibit this. Worth a comment in the function body if the team wants to document the intentional behaviour.

**2. CSS — `.local-article-map a` has no explicit `display` value**

Inside the flex container `.local-article-map { display: flex; }`, `<a>` elements become flex items automatically; no explicit `display` is needed. Correct as written, but differs stylistically from the parallel `.local-article-content-paragraph-links a { display: inline-block; }` rule. No behaviour impact.

**3. No isolated test for content-sections-only (no brief) article map**

The matrix covers: structured (brief + content), brief-only, plain-paragraph-only. A content-sections-only case (no `brief_sections`, some `content_sections`) is not exercised as a dedicated test. The implementation path is simple and correct, and the existing structured test covers both brief and content links. Low risk, acceptable gap for this stage.

---

### Required Fixes Before Commit

None.

---

### Requirements Checklist

| Requirement | Status |
|---|---|
| Detail-page-only map inside `#local-article` for structured articles | ✅ `_render_local_article_map` called only from `_render_local_article`; homepage hrefs tested |
| Map links target `#local-article-brief`, `#local-article-content-section-N`, `#local-article-body` | ✅ All three anchor types generated and tested |
| Stage 303 paragraph anchors preserved exactly (`local-article-paragraph-{index+1}`) | ✅ `_local_article_paragraph_anchor` unchanged |
| Plain paragraph-only → `id="local-article-body"`, no map | ✅ Map gated on `brief_sections or content_sections`; body ID unconditional; tested |
| Brief-only → Brief + Full saved text links, no content-section links | ✅ `test_render_row_one_detail_map_handles_brief_only_local_article` covers and verifies |
| Homepage Daily Local Intelligence receives no detail-only fragments | ✅ Extended homepage href assertions cover `#local-article-content-section-*` and `#local-article-body` |
| All model-supplied text escaped in map links | ✅ `_esc()` on section title `.en` and `.zh`; escape test extended |
| Scope: template/CSS/docs/tests only | ✅ No schema, contract, or dependency changes in diff |

---

### Test Coverage Assessment

7 new or extended test cases match the 8 requirements cleanly. Ordering assertions (map before brief, link before anchor target) are a good addition. The escape coverage extension to `test_render_row_one_detail_escapes_local_article_content` correctly validates the new map surface. 93 total tests passing with no regressions confirms scope containment.

---

REVIEW_COMPLETE

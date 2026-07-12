## Re-Review: Stage 382 Local Article Synthesis Brief

### Prior Finding: FIXED ✅

`local_article_synthesis_brief.py:225` now reads:
```python
if len(anchors) >= LOCAL_ARTICLE_SYNTHESIS_BRIEF_MAX_ANCHORS - 1:
```
The hardcoded `2` is gone. Logic trace confirms correctness with `MAX=3`: sections slot fills to at most 2, paragraph branch fires when `len < 3`, final `[:MAX]` slice is defensive-only. The caps test (3 sections + 2 paragraphs → 3 anchors) exercises the full path cleanly.

---

### Critical

None.

---

### Important

None.

The reconciled-plan requirement — synthesis-specific href wrapper that delegates to `_safe_local_article_intelligence_href` for fragment shape, adds rendered-target existence checks, and does not duplicate the regex allow-list — is correctly implemented:

- `_safe_local_article_synthesis_href` (`templates.py:17709`) opens by calling `_safe_local_article_intelligence_href` as a gate; no regex literals are copied.
- After that gate, it adds paragraph-index and content-section position checks against the live `local_article` object.
- `_render_local_article_synthesis_anchor` calls only `_safe_local_article_synthesis_href`; all render-side escaping goes through `_esc()`.

---

### Minor

**1. Unreachable `return None` at the end of `_safe_local_article_synthesis_href` (`templates.py:17729`)**

`_safe_local_article_intelligence_href` only returns non-`None` when the fragment matches exactly one of the two regex patterns. Post-delegation, the fragment must therefore satisfy one of the two `fullmatch` branches, each of which returns before reaching the trailing `return None`. That final statement is dead code. No correctness risk, but it implies a missing pattern could silently produce `None` if the regex set ever widens — an explicit `raise AssertionError` or a comment would make the invariant explicit.

**2. Inline href construction in builder bypasses canonical helpers (`local_article_synthesis_brief.py:252`, `280`)**

`_section_anchor` constructs `f"#local-article-content-section-{section_position}"` and `_paragraph_anchor` constructs `f"#local-article-paragraph-{number}"` by hand rather than composing from `local_article_content_section_anchor()` / `local_article_paragraph_anchor()` in `local_article_anchors.py`. The fragment shape is validated at render time by `_safe_local_article_synthesis_href`, so there is no correctness risk today. The coupling gap would matter only if the anchor prefix constants changed and the builder were not updated — the render guard provides a safety net, but the single-definition principle is not honoured.

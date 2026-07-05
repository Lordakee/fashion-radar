Here is the Stage 303 plan review.

---

## Stage 303 Plan Review — Row One Local Article Paragraph Anchors

**Reviewer:** Claude (Opus4.81M)
**Date:** 2026-07-05
**Plan:** `docs/superpowers/plans/2026-07-05-stage-303-row-one-local-article-paragraph-anchors-plan.md`

---

### Verdict: APPROVE_WITH_NOTES

No critical blockers. The plan is technically sound, correctly scoped, and safe to implement after reviewing the notes below.

---

### Critical Issues

None.

---

### Important Issues

**1. `_safe_daily_local_intelligence_paragraph_href` relies on an implicit contract with the existing fragment guard**

The proposed helper calls `_safe_daily_local_intelligence_href(detail_path)` and then does `href.split("#", 1)[0]`. The current `_safe_daily_local_intelligence_href` (templates.py:1964) only accepts two forms of `detail_path`:

- A plain path with no `#` — passes `_validated_detail_relative_path` check, returned as-is.
- A path with `#local-article` exactly — fragment validated, returned as-is.

Any other fragment causes `None` to be returned, and the new helper correctly propagates `None`. This is safe. However, if production `detail_path` values can carry `#local-article` (they can, per the existing model), the helper's `split("#", 1)[0]` correctly strips that fragment before appending the new paragraph anchor. This contract should be explicitly called out in a brief comment on the helper, since a future maintainer might not realize why the old fragment is stripped — they could accidentally break the double-split if the guard logic changes.

**Action:** Add a one-line comment on `_safe_daily_local_intelligence_paragraph_href` explaining that it strips any existing `#local-article` fragment before appending the paragraph anchor, and that path safety is delegated to `_safe_daily_local_intelligence_href`.

---

**2. Task 3 Step 4 underspecifies the plain-paragraph anchor case**

The bilingual paragraph render path already uses an explicit loop (`for paragraph_en, paragraph_zh in zip(...)`), so inserting `rendered_index = len(rendered)` is straightforward there. But the plain fallback path at templates.py:2451 is currently a list comprehension:

```python
return [f"      <p>{_esc(paragraph)}</p>" for paragraph in source_paragraphs]
```

A list comprehension has no `rendered` accumulator to call `len()` on mid-iteration. The plan says "Keep source order and skip blank paragraphs while numbering based on rendered paragraph order" but gives no explicit code for this branch. The implementer needs to refactor the plain path to an explicit loop too — this is easy but the plan should make it explicit, not leave it as an inference.

**Action:** Add a code snippet in Task 3 Step 4 showing the refactored plain-paragraph loop (mirrors the bilingual pattern with `rendered: list[str] = []` and `rendered.append(...)`).

---

### Minor Notes

1. **CSS class `local-article-content-paragraph-links` has no corresponding rule in `row-one-app/v7`.** This is intentional and correct (v7 is out of scope for Stage 303), but the paragraph links will be unstyled until a future stage updates the CSS. No action needed; just worth recording in the Handoff Summary so the next stage knows.

2. **Anchor IDs are 1-based; `paragraph_indices` are 0-based.** The `+1` offset is handled centrally by `_local_article_paragraph_anchor(index)`, which is good. The test assertions in Task 2 correctly reflect this (index=1 → `local-article-paragraph-2`). No action needed, but worth a brief docstring on the helper.

3. **Blank-paragraph edge case is unspecified for `paragraph_count` semantics.** `paragraph_count = len(paragraphs)` uses the rendered count (non-blank), not `len(article.paragraphs)` (raw). This means `paragraph_indices` must be treated as rendered-order indices. If source data ever includes blank paragraphs mid-list, raw indices and rendered indices diverge. In practice this is unlikely since extraction normalises content, but the plan should document that `paragraph_indices` are indices into the rendered (non-blank) sequence. A comment in `_valid_local_article_paragraph_indices` is sufficient.

4. **Task 4 Step 2 unsafe-path test asserts `"Paragraph 1" in html`** (plain fallback label still appears even when no safe href exists). This is the right behaviour. Confirm the segment-meta render logic for the unsafe case renders the plain label, not an empty string — the test would catch a silent omission, but the plan step should explicitly say "fall back to plain label, not empty output."

5. **`_esc(anchor)` in href is redundant** since `local-article-paragraph-N` contains only ASCII alphanumerics and hyphens. It is harmless defensive coding and consistent with the rest of the template — no change needed.

---

### Boundary Confirmation

- ✅ No scraping, social connectors, source acquisition, demand proof, platform coverage verification, app UI work, paywall bypass, image generation, or compliance-review product features introduced.
- ✅ `data/edition.json` is not read or written by any new code path.
- ✅ `row-one-app/v7` is not modified.
- ✅ All generated hrefs and anchor IDs are constructed from validated integer indices and paths that pass `_validated_detail_relative_path`.
- ✅ All user-visible strings go through `_esc()`.
- ✅ Red-Green test discipline is properly sequenced across Tasks2–5.
- ✅ Full verification (pytest, ruff check, ruff format, hygiene script, lock check) is included in Task 6.

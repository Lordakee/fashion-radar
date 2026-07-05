## Stage 303 Code Review

---

### Verdict: APPROVE

The implementation is correct, complete, and all verification passes. No critical or important issues found.

---

### Critical Issues

None.

---

### Important Issues

None.

---

### Review Findings By Objective

**Paragraph anchor IDs on detail-page local article body**

`_render_local_article_paragraphs` (templates.py:2497–2523) correctly uses `enumerate(article.paragraphs)` on both the plain fallback path and the bilingual path. Blank paragraphs are skipped but the `index` from `enumerate` is preserved, so `id="local-article-paragraph-{index+1}"` is stable and based on original position. Both render paths are covered. ✅

**Zero-based original index semantics throughout**

`_local_article_rendered_paragraph_indices` (line 2439) builds a set of original indices of non-blank paragraphs via `enumerate(article.paragraphs)`. `_valid_local_article_paragraph_indices` (lines 2448–2460) checks membership against that set — not against a compacted rendered position. The comment "Both inputs use original zero-based RowOneLocalArticle.paragraphs positions" is correct and present. The `_local_article_paragraph_anchor` comment "paragraph_indices are zero-based; fragment IDs are one-based for readers" is also correct. ✅

**Invalid/blank/duplicate/out-of-range index safety**

`_valid_local_article_paragraph_indices` uses a `seen: set[int]` guard for duplicates and rejects any index not in `rendered_indices`. Negative indices (e.g. `-1`) are not in the non-negative rendered set and are silently dropped. The `test_render_row_one_detail_skips_invalid_local_article_paragraph_links` test exercises all four failure modes (`[-1, 0, 1, 2, 2, 99]` against `["rendered", "   ", "rendered"]`) with arithmetic-correct count assertions. ✅

**Homepage Daily Local Intelligence remains plain text, no nested anchors**

`_render_daily_local_intelligence_segment_meta` (lines 1876–1892) emits paragraph labels as plain `<span>` text:
```python
parts.append((f"Paragraph {paragraph_label}", f"段落 {paragraph_label}"))
```
No `<a>` tags. This is the correct choice given homepage cards can themselves be `<a class="daily-local-intelligence-card">` elements. The regression assertion in `test_render_row_one_site_writes_and_renders_daily_local_intelligence_segments` (line 924) checks all homepage hrefs, not just one path:
```python
assert "#local-article-paragraph-" not in "".join(re.findall(r'href="([^"]+)"', html))
```
This would catch nested anchors, wrong-article paragraph links, and stray paragraph fragments anywhere on the homepage. ✅

**`data/edition.json`, `data/local-intelligence.json`, and `row-one-app/v7` unchanged**

All Stage 303 changes are confined to the render layer (`templates.py`). The `data/local-intelligence.json` structure is confirmed unchanged — `paragraph_indices` is still plain integer data (test line 936). The edition JSON isolation test at line 535 still passes. ✅

**Anchor/href determinism and escaping**

`_local_article_paragraph_anchor(index)` produces only `local-article-paragraph-N` (ASCII alphanum + hyphens) — deterministic across re-renders. `_esc()` is applied defensively to the href and to anchor IDs, harmlessly. All user/source text — paragraphs, titles, source names, ref names — passes through `_esc()`. The escaping test at lines 776–795 covers XSS payloads (`<script>`, `<img onerror=>`, `&`) in all content positions including the new paragraph anchor and link paths. ✅

**Tests are meaningful and catch named regressions**

- Removing `id="local-article-paragraph-N"` from paragraph rendering would fail the plain and bilingual tests.
- Removing `href="#local-article-paragraph-N"` from content-section item rendering would fail the main content test and the zh-mismatch test.
- Reverting to compact rendered indices would cause the blank-paragraph-skip test (`paragraph-2` must be absent) to fail.
- Adding any `<a>` with `#local-article-paragraph-` to the homepage would fail the regex href inspection.
- The link-before-id ordering assertion (line 504–506) catches if content sections and the local article body swap render order. ✅

**Review artifacts**

All four review artifacts (`claude-code-stage-303-plan-review.md`, `claude-code-stage-303-plan-rereview.md`, `opencode-stage-303-plan-review.md`, `opencode-stage-303-plan-rereview.md`) are coherent, have clear verdicts, and are free of live-capture/tool-status noise. Both APPROVE_WITH_NOTES reviews had Important issues that were correctly resolved by plan revisions before implementation. ✅

---

### Minor Notes

1. **Rereview artifacts missing from commit list.** The plan's Task 4 Step 7 `git add` list omits `docs/reviews/claude-code-stage-303-plan-rereview-prompt.md`, `docs/reviews/claude-code-stage-303-plan-rereview.md`, `docs/reviews/opencode-stage-303-plan-rereview-prompt.md`, and `docs/reviews/opencode-stage-303-plan-rereview.md`. The git status confirms all four are currently untracked. Add them to the `git add` before committing.

2. **`local-article-content-paragraph-links` has no CSS rule in this stage.** Links are functional but unstyled. This is the known carry-forward from plan reviews (rereview Minor Note 1). Worth a one-sentence note in the Handoff Summary.

3. **`_valid_local_article_paragraph_indices` comment is accurate but could be sharper.** The comment states "Both inputs use original zero-based RowOneLocalArticle.paragraphs positions" which is correct. Adding "blank positions are absent from rendered_indices" would make it easier for future callers to understand why a valid-looking index can be rejected. No action needed before commit.

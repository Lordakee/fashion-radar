Having read the plan, both prior reviews, and the actual current test file, here is my rereview.

---

## Stage 303 Plan Rereview 2

**Reviewer:** Kiro (Claude Opus4.81M)
**Date:** 2026-07-05
**Files reviewed:**
- `docs/superpowers/plans/2026-07-05-stage-303-row-one-local-article-paragraph-anchors-plan.md`
- `docs/reviews/claude-code-stage-303-plan-rereview.md`
- `docs/reviews/opencode-stage-303-plan-rereview.md`
- `tests/test_row_one_render.py` (current state)

---

### Verdict: APPROVE

No Critical or Important issues. The plan is technically sound as written. All prior Important Issues are resolved, and the prior rereview Minor Note 2 that misdescribed index semantics is superseded by the current plan's explicit comment.

---

### 1. Original-index contract — CONFIRMED SOUND

The plan's contract is coherent end-to-end:

- `_local_article_rendered_paragraph_indices(article)` → `{index for index, paragraph in enumerate(article.paragraphs) if paragraph.strip()}` — produces **original zero-based positions** of non-blank paragraphs, not a compacted/renumbered sequence.
- `_valid_local_article_paragraph_indices(indices, rendered_indices)` — both arguments are original positions; the function checks membership, not sequence-order.
- `_local_article_paragraph_anchor(index)` → `local-article-paragraph-{index + 1}` — the `+1` is a reader-friendly offset, not a renumbering.
- Task 3 Step 1 comment: `# paragraph_indices and rendered_indices both use original zero-based RowOneLocalArticle.paragraphs positions; blank source paragraphs are absent.` — precise and correct.

The prior rereview Minor Note 2 described `rendered_indices` as if it were a renumbered compact sequence. That was wrong. The current plan's description is correct. Treating it as superseded is the right call.

Validation against the test file (lines 613–661): `paragraphs=["First rendered paragraph.", "   ", "Third rendered paragraph."]`, `paragraph_indices=[-1, 0, 1, 2, 2, 99]` — the expected results are:
- `id="local-article-paragraph-1"` present (index 0, non-blank) ✅
- `id="local-article-paragraph-2"` absent (index 1, blank → not in `rendered_indices`) ✅
- `id="local-article-paragraph-3"` present (index 2, non-blank) ✅
- `href="#local-article-paragraph-0"` absent (index -1 not in `rendered_indices`) ✅
- `href="#local-article-paragraph-2"` absent (index 1 blank) ✅
- `href="#local-article-paragraph-100"` absent (index 99 out of range) ✅
- count of `href="#local-article-paragraph-3"` == 2 (one en span, one zh span; duplicate index 2 deduplicated) ✅

All arithmetic is correct. The contract is sound.

---

### 2. Homepage deferral regression — CONFIRMED BROAD ENOUGH

Test already in file at lines 924–926:

```python
assert '#local-article-paragraph-' not in "".join(re.findall(r'href="([^"]+)"', html))
assert "Paragraph 1" in html
assert "段落 1" in html
```

`re.findall(r'href="([^"]+)"', html)` extracts every double-quoted href value from the entire homepage HTML. Joining them and checking for the fragment prefix:

- Catches paragraph fragment links anywhere on the homepage regardless of which story they target — covers wrong-article aggregate links.
- Catches links nested inside card `<a>` elements — covers the nested-anchor HTML invalidity risk.
- Is not limited to one specific story path or one specific fragment number.

The render layer uses double-quoted attributes consistently (all plan code snippets use `href="..."` and `id="..."`), so single-quote variants are not a concern.

The positive assertions confirm plain-text paragraph metadata (`paragraph_indices=[0]` rendering as "Paragraph 1" / "段落 1") survives unchanged on the homepage. This is correct given Stage 302's existing homepage render behavior.

The regression is broad enough.✅

---

### 3. Nested homepage anchors and wrong-article aggregate links — CONFIRMED SAFE

Two layers of protection:

**Architecture:** The homepage render path is not modified at all in Stage 303. `paragraph_indices` metadata continues to render as plain text in homepage Daily Local Intelligence segments. No code path adds `<a href="#local-article-paragraph-...">` to homepage HTML.

**Test guard (Task 2 Step 5):** The href-join scan catches any accidental regression — including nested anchors inside card `<a>` elements, links to the wrong article's paragraphs, and broken fragment fragments from any cause.

Both layers are in place. ✅

---

### Critical Issues

None.

---

### Important Issues

None.

---

### Minor Notes

**1. Prior rereview Minor Note 2 is resolved**
The comment `# paragraph_indices and rendered_indices both use original zero-based RowOneLocalArticle.paragraphs positions; blank source paragraphs are absent.` in Task 3 Step 1 closes the prior observation. No further action needed.

**2. `local-article-content-paragraph-links` unstyled in v7 — still applies, still Minor**
Task 4 Step 8 now includes the handoff note. Functional links, no visual polish yet. No action needed before implementation.

**3. Tests are already GREEN-staged in the working tree**
`tests/test_row_one_render.py` shows as modified (`M`) in git status. The RED test assertions from Task 2 are already written into the file. The plan's Task 2 Step 6 verification step is still the correct next checkpoint — confirm they fail before implementing Task 3, not after.

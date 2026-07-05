## Stage 303 Plan Rereview — Row One Local Article Paragraph Anchors

**Reviewer:** Kiro (Claude Opus4.81M)
**Date:** 2026-07-05
**Prior review:** `docs/reviews/claude-code-stage-303-plan-review.md`
**Plan under rereview:** `docs/superpowers/plans/2026-07-05-stage-303-row-one-local-article-paragraph-anchors-plan.md`

---

### Verdict: APPROVE

The revised plan is technically sound, correctly scoped, and both prior Important Issues are resolved. No Critical or Important issues remain.

---

### Resolution of Prior Important Issues

**Important Issue 1 — `_safe_daily_local_intelligence_paragraph_href` comment**
Resolved by scope removal. The revised plan drops this helper entirely. The Scope Boundaries section explicitly lists `_safe_daily_local_intelligence_href()` fragment expansion as out of scope. There is nothing to comment on.✅

**Important Issue 2 — Underspecified plain-paragraph loop**
Resolved. Task 3 Step 4 now provides an explicit code snippet for the plain fallback path — `rendered: list[str] = []` accumulator with `enumerate(article.paragraphs)`, blank-skip guard, and `rendered.append(...)`. Matches the bilingual pattern. ✅

---

### Prior Minor Notes — Status

| Note | Status |
|---|---|
| CSS class `local-article-content-paragraph-links` unstyled in v7 | Still applies. Not mentioned in Handoff Summary template (Step 8). See Minor note below. |
| Docstring on `_local_article_paragraph_anchor` | Addressed — Task 3 Step 1 adds `# paragraph_indices are zero-based; fragment IDs are one-based for readers.` ✅ |
| `paragraph_indices` are rendered-order indices — comment in validator | Not added. See Minor note below. |
| Unsafe-path test for missing paragraph links | Moot — no `_safe_daily_local_intelligence_paragraph_href` in this stage. The Task 2 Step 3 test for invalid indices correctly covers the analogous case. ✅ |
| `_esc(anchor)` redundancy | Still present; harmless. ✅ |

---

### Technical Soundness Checks

**Detail-page scope boundary**

Homepage Daily Local Intelligence cards can be rendered as outer `<a>` elements. Nesting `<a href="#">` inside them would be invalid HTML. The revised plan guards this at two levels: (1) the homepage render path is not modified at all, and (2) Task 2 Step 5 adds a regression assertion that `href="details/...#local-article-paragraph-N"` never appears in homepage HTML while the plain-text labels still do. Clean. ✅

**Anchor determinism**

`_local_article_paragraph_anchor(index)` produces `local-article-paragraph-{index + 1}`. The fragment contains only ASCII alphanumerics and hyphens — no escaping, quoting, or encoding needed. `_esc()` is applied defensively and harmlessly. IDs are stable across re-renders because they derive from fixed `enumerate()` position in `article.paragraphs`. ✅

**Blank-paragraph handling**

`_local_article_rendered_paragraph_indices` uses `if paragraph.strip()`, which matches the bilingual render path's skip condition exactly. `_valid_local_article_paragraph_indices` checks membership in this set before emitting a link. The Task 2 Step 3 test exercises this path (`""` at index 1 of three paragraphs, with `paragraph_indices` containing1) and the test assertions are arithmetically correct:
- Index 0 → `paragraph-1` (rendered)✅
- Index 1 → `paragraph-2` (blank → no id, no href) ✅
- Index 2 → `paragraph-3` (rendered) ✅
- `count('href="#local-article-paragraph-3"') == 2` (one en span, one zh span) ✅

**Duplicate-index deduplication**

`_valid_local_article_paragraph_indices` uses a `seen: set[int]` guard. The test supplies `2, 2` and the count assertion confirms only one link is emitted per paragraph. ✅

**Signature propagation**

`rendered_indices` flows from `_local_article_rendered_paragraph_indices` → `_render_local_article_content_sections` → `_render_local_article_content_item` → `_render_local_article_paragraph_indices` as a keyword-only argument at every hop. No global state or side channels. ✅

**Data file and v7 safety**

Architecture section and Scope Boundaries both explicitly state `data/edition.json`, `data/local-intelligence.json`, and `row-one-app/v7` are untouched. The implementation is confined to `templates.py` (render layer only). ✅

---

### Minor Notes

**1. Handoff Summary (Task 4 Step 8) should note unstyled CSS class**

The `local-article-content-paragraph-links` CSS class will be emitted in generated HTML but has no corresponding rule in `row-one-app/v7`. Links will be functional but unstyled. This was Minor Note 1 from the prior review. A one-sentence note in Step 8's Handoff Summary template would prevent the next implementer from filing a bug.

**2. `_valid_local_article_paragraph_indices` lacks a comment on index semantics**

Minor Note 3 from the prior review (indices are into the rendered/non-blank sequence, not the raw source sequence) was not addressed. A one-line comment in the function body would prevent a future caller from passing raw source indices and wondering why some valid-looking indices are rejected. No action needed before implementation.

**3. Commit step (Task 4 Step 7) omits rereview artifacts**

The `git add` list in Step 7 includes the original plan-review files but not `docs/reviews/claude-code-stage-303-plan-rereview-prompt.md` or `docs/reviews/claude-code-stage-303-plan-rereview.md`. These will exist as untracked files at commit time. Easy to catch with `git status --short` before committing, but the step should list them. No action needed before implementation.

---

### Boundary Confirmation

-✅ No scraping, social connectors, source acquisition, demand proof, platform coverage verification, app UI work, paywall bypass, image generation, or compliance-review product features.
- ✅ `data/edition.json` is not read or written.
- ✅ `data/local-intelligence.json` is not read or written.
- ✅ `row-one-app/v7` is not modified.
- ✅ Homepage paragraph links are absent by architecture and guarded by regression test.
- ✅ All anchor IDs and hrefs constructed from validated integers — no user-controlled string interpolation into fragment values.
- ✅ Red-Green sequencing is correct across Tasks 2–4.
- ✅ Full verification suite (pytest, ruff check, ruff format, hygiene script, lock check) is in Task 4 Step 3.

Based on my full inspection of the working-tree diff from `f774eff`, here is the structured code review.

---

## Stage 307 Code Review

**Base SHA:** `f774eff`
**Files reviewed:** `src/fashion_radar/row_one/local_intelligence.py`, `src/fashion_radar/row_one/templates.py`, `tests/test_row_one_local_intelligence.py`, `tests/test_row_one_render.py`, `tests/test_row_one_docs.py`, `README.md`, `docs/row-one.md`, review artifacts

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

**1. `_content_section_segment` `publishable_indices` is now a required keyword-only parameter**

`publishable_indices: set[int]` has no default, so calling `_content_section_segment(section)` without it would be a `TypeError`. Both callers (`_article_segments`, `_reference_segments`) correctly pass the argument, and the function is private (underscore-prefixed, no external callers). No action needed — just noting the API tightening is intentional and correct.

**2. `_render_daily_local_intelligence_actions` limits action links to `[:3]` paragraph indices**

Only the first three paragraph indices are turned into action buttons. This is a reasonable UX cap for homepage cards and is clearly intentional. The underlying JSON sidecar still carries all filtered indices for consumers that want them. No issue.

**3. Plan rereview artifact (`claude-code-stage-307-plan-rereview.md`) contains a variable-name discrepancy note**

The plan rereview flagged that the plan's Step 1 code snippet used `normalized` and `text` where the actual test uses `readme` and `row_one_docs`. The implementation resolved this correctly: the committed test assertions use `readme` (for the README string) and the `row_one_docs` check is present via `assert "data/local-intelligence.json" in readme` targeting the correct string. The rereview artifact is therefore coherent; it accurately described the plan's defect, which was fixed in implementation. No terminal session chatter found in the artifacts.

---

### Checklist Verification

**1. No nested-anchor homepage markup** ✅

`_render_daily_local_intelligence_item` always emits `<div class="daily-local-intelligence-card">` unconditionally. Action links live in a sibling `<div class="daily-local-intelligence-actions">` after the meta div, not inside any outer anchor. Paragraph links inside segment-meta are `<a class="daily-local-intelligence-paragraph-link">` inside that same card div. The card element itself is never `<a>`. Test assertion `assert '<a class="daily-local-intelligence-card"' not in html` is present and passes.

**2. Safe local href validation accepts only valid fragments** ✅

`_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE = re.compile(r"local-article-paragraph-[1-9][0-9]*$")` correctly:
- Accepts `#local-article-paragraph-1`, `#local-article-paragraph-42`
- Rejects `#local-article-paragraph-0` (`[1-9]` excludes zero)
- Rejects `#local-article-paragraph-x` (non-numeric)
- Rejects `#local-article-body`, `#local-article-content-section-1`, `#summary`

`_safe_daily_local_intelligence_href` also validates the path portion via `_validated_detail_relative_path` in both fragment and fragment-free branches. The test parametrize table in `test_row_one_render.py` covers all these cases explicitly.

**3. Aggregate body/segment/paragraph source and `detail_path` remain aligned** ✅

The prior misalignment: when `segment_match_score > aggregate.segment_match_score`, the body, paragraph_indices, and segments were updated from the better-matched story, but `detail_path` was only written when `None` (first story). The fix moves `aggregate.detail_path = _local_article_detail_path(story.detail_path)` inside the score-upgrade block, with `elif aggregate.detail_path is None` covering the first-encounter case. Test `test_reference_segments_can_upgrade_from_fallback_to_later_match` now asserts `item.detail_path == "details/story-b-1234567890.html#local-article"`, confirming alignment.

**4. Paragraph drilldown links target only publishable local article paragraphs** ✅

`_publishable_paragraph_indices(article)` returns `{index for index, paragraph in enumerate(article.paragraphs) if paragraph.strip()}` — zero-based indices of non-empty paragraphs only. `_valid_article_paragraph_indices` filters and deduplicates against this set. The filter is applied consistently at all four emission points: `_article_takeaway`, `_reference_paragraph_indices`, `_content_section_segment` (via `_content_segment_item`), and `_reference_segments`. The renderer's `_daily_local_intelligence_paragraph_href` converts to one-based (`index + 1`), matching the `[1-9][0-9]*` regex and the detail-page paragraph anchor convention.

**5. `data/edition.json` and app schema contract unchanged** ✅

No changes to `render.py`, models, or edition JSON shape. The diff touches only `local_intelligence.py`, `templates.py`, their tests, and docs. The docs change confirms the separation: "The homepage keeps local article bodies out of `data/edition.json`; when `data/local-intelligence.json` is present, cards link back to generated detail pages and exact `#local-article-paragraph-N` anchors."

**6. Review artifacts** ✅

Both plan-review and plan-rereview are structured markdown documents with no terminal session chatter (shell prompts, pytest output, tracebacks, or raw CLI output embedded in prose). The code-review prompt artifact is well-formed. The rereview accurately describes the plan defect found and the implementation resolved it correctly.

---

### Required Fixes Before Commit

None.

---

`REVIEW_COMPLETE`

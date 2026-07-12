Here is the re-review against the seven prior findings.

---

## Stage 383 Plan Re-Review —2026-07-12

---

### Prior Critical

**C1 — Href validation inverted (builder always returns None)**
✅ **Resolved.** Line 129 now explicitly requires a bare filename at the builder input layer and calls out `articles/<story-id>.html` as invalid there. Line 135 documents that `RowOneDailyLocalSynthesisBriefCard.href` stores the bare filename. Lines 212–216 document the render-layer validator that accepts `articles/<safe-story-id>.html` after the template prepends `articles/`. Line 216 explicitly separates the two layers so neither validates the wrong form.

---

### Prior Important

**I1 — Fragment policy for card hrefs unspecified**
✅ **Resolved.** Fragments in builder-layer input are now in the unsafe fixture list (line 246: `<story-id>.html#local-article-paragraph-1`). The render-layer validator (line 213) accepts `articles/<safe-story-id>.html` with no fragment requirement. The render test (lines 275–277) explicitly asserts that a fragmentless safe href renders. The two-layer split makes it impossible for the builder to accidentally inherit the fragment-required `_safe_daily_local_article_intelligence_href` validator.

**I2 — Source-ID dedupe unjustified and collapses same-source editions**
✅ **Resolved.** Line 156: "Do not dedupe by source name: multiple current-edition stories from the same source are valid." The dedupe rule is now `(title, href)` and `read` only. The test at lines 248–251 explicitly asserts same-source-but-distinct articles are kept.

**I3 — Test fixtures encode the wrong href shape**
✅ **Resolved.** The unsafe fixture list (lines 246–247) now uses bare-filename inputs: `index.html`, `../unsafe.html`, `<story-id>.html?x=1`, `<story-id>.html#local-article-paragraph-1`, `articles/<story-id>.html` (correctly invalid at the builder layer because it has two path parts), `<other-story-id>.html`, a whitespace href, plus one safe bare `<story-id>.html`. The fixtures are now consistent with the corrected builder-layer validation.

**I4 — Opening-read title truncation underspecified**
❌ **Still open.** Lines 143–147 now say "Cap to 180 characters" and "Use ASCII apostrophe" — the apostrophe issue is fixed — but the truncation order when the assembled string exceeds 180 characters remains unspecified. The plan does not say whether each title is pre-truncated to a per-title constant before assembly, whether a word-boundary or character boundary is used, or what fallback applies when the cap would eat into the second title. The `test_build_daily_local_synthesis_brief_caps_text_and_cards` test (line 257) says "Provide long text" but does not pin a two-120-character-title scenario and does not assert that mid-title truncation is prevented. An implementer following only the plan text today could produce `Today's local read connects Brand X with Wholesa` on the homepage.

**Required fix:** Specify the truncation order explicitly — e.g., pre-truncate each title to a named per-title constant (e.g. `_OPENING_READ_TITLE_MAX = 60`) before assembling the template string, then apply the 180-character final cap as a safety net only. Add a test case to `test_build_daily_local_synthesis_brief_caps_text_and_cards` (or a dedicated test) that provides two titles each exceeding the per-title constant and asserts the assembled `opening_read` does not contain a partial word and does not exceed 180 characters.

---

### Prior Minor — status

| Prior | Verdict |
|---|---|
| M1 (`why_it_matters` dead clause) | ✅ Resolved — line 152 now says "Do not read `RowOneStory.why_it_matters` directly." |
| M2 (`href` field shape not pinned) | ✅ Resolved — line 135 documents bare filename in the card. |
| M3 (docs ordering assertion missing) | ✅ Resolved — line 313: `text.index(paragraph) < text.index("Stage 382 adds")`. |
| M4 (no test for all-synthesis-None) | ✅ Resolved — test added at lines 254–256. |
| M5 (`article_count` rename to `eligible_article_count`) | Still named `article_count` but line 159 now says "post-dedupe, pre-cap," which closes the ambiguity. Renaming remains optional. |
| M6 (apostrophe file-inspection check) | ✅ Resolved — line 147: "Use ASCII apostrophe: `Today's`." |

**New minor:** `source_count` (line 160) is defined as "the number of distinct normalized source names among eligible candidates" without specifying whether "eligible candidates" means pre-dedupe or post-dedupe. `article_count` was tightened to say "post-dedupe" explicitly — `source_count` should have the same clarification (post-dedupe, pre-cap normalized source names) to keep the two count definitions parallel and prevent a subtle off-by-one when the same source appears under two slightly different names.

---

### Summary

**No Critical findings remain.**

**One Important finding remains (I4):** Opening-read title truncation is still underspecified. The plan needs a named per-title constant, a truncation-order rule, and a test case for two long titles before implementation proceeds.

**Two minor notes:** M5 (`article_count` rename) is optional; `source_count` definition needs the same "post-dedupe, pre-cap" precision as `article_count`.

All other prior Critical, Important, and Minor findings are resolved.

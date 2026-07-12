## Stage 383 Plan Re-review — Second Fix Pass (opencode, GLM 5.2 max)

### Verification of the four prior findings

**1. Opening-read title truncation — RESOLVED.** Plan lines 141–151 now cover every axis:
- Named per-title constant: `DAILY_LOCAL_SYNTHESIS_BRIEF_OPENING_TITLE_CHARS = 56` (line 147), anchored by the test at line 265.
- Truncation order: per-title cap *before* assembly (line 147); 180-char final cap *after* assembly as a safety net only (line 149).
- Word-boundary behavior: "on a word boundary for English when possible, with `...` appended only when text is shortened"; Chinese character-capped (line 148).
- Final-cap behavior: stated as safety-net only, "so the sentence does not cut through the second title" (line 149).
- Two-long-title regression test: lines 150 & 265 — asserts `opening_read.en` ≤ 180, includes both shortened titles, ends cleanly with punctuation, no mid-word second-title fragment.

**2. Dedupe semantics — RESOLVED.** Lines 131 and 161 are now consistent: both use composite `(title, href)` plus normalized `read`; line 161 explicitly says "Do not dedupe by source name." Same-title/different-href kept when reads differ (line 131 + test 256); same-source distinct articles kept (test 257). The prior independent-axis vs. composite-key conflict is gone. (Note: because `read` is a dedupe key and the 2-card minimum holds, any two kept cards always have distinct normalized reads, so the combined-branch condition is effectively "≥2 cards," which is coherent.)

**3. source_count post-dedupe, pre-cap — RESOLVED.** Lines 164–165 are now parallel: both say "post-dedupe eligible article-level synthesis candidates before the three-card cap is applied."

**4. opencode rereview artifact complete — RESOLVED.** `docs/reviews/opencode-stage-383-plan-rereview.md` is now a complete 18-line structured review (Critical / Important / Minor + summary), not a stub.

Codebase grounding also re-confirmed: `build_row_one_local_article_synthesis_brief(*, story=, local_article=)` signature and the `lead`/`thesis`/`article_adds`/`source_name` fields match `local_article_synthesis_brief.py:33-98`; the builder-layer bare-filename rule mirrors the sibling `_safe_article_page_href` at `daily_local_article_intelligence_brief.py:251-270`; the insertion point is feasible — `{daily_local_article_intelligence_brief_section}` (templates.py:651) and `{daily_local_saved_article_organizer_section}` (templates.py:652) are consecutive.

### Critical
None.

### Important
None remain. All four prior findings are resolved and no new Important issues were found on fresh scan.

### Minor (non-blocking)
- **M1** — Card `read` cap (150, line 136) and `adds` cap (140, line 137) are stated as inline magic numbers, which sits awkwardly next to line 161's directive ("Use named constants for all card/text/reference limits; do not scatter magic numbers"). The opening-title cap is named; these two should be too (e.g. `..._CARD_READ_CHARS`, `..._CARD_ADDS_CHARS`). Cosmetic consistency.
- **M2** — "first non-duplicate article-level `thesis`" (lines 154–155) does not specify the duplicate set (against card reads? against prior theses only?). A one-clause clarification would prevent an implementer choosing a thesis identical to a card `read`.
- **M3** — The task-level summary of `test_build_daily_local_synthesis_brief_caps_text_and_cards` (lines 264–266) omits "includes both shortened titles" / "no mid-word second-title fragment" that the spec section (lines 149–150) requires. Spec takes precedence, but the task checklist should echo the key assertions so a test author reading only Tasks doesn't write a weaker test. (Echoed from the prior Claude rereview; still open as minor.)
- **M4 (process, not plan content)** — `docs/reviews/opencode-stage-383-plan-rereview-2.md` is currently a 1-line live-capture stub. It is the capture slot for *this* review, so it is not a defect in the plan; it must be replaced with this completed review output before commit per AGENTS.md / `docs/REVIEW_PROTOCOL.md:124-139` hygiene.

**Summary:** No Critical findings. No Important findings remain — the plan is implementable as written. Four Minor non-blocking observations are noted above.

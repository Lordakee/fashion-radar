**Stage 383Plan Re-review — Second Fix Pass**

Checking each of the four prior remaining findings against the current plan text and the opencode rereview artifact.

---

**Prior Finding 1 — Opening-read title truncation underspecified**

Status: **Resolved.**

Plan lines 141, 147–151 now cover every axis the prior review flagged:
- Named per-title constant: "a named constant such as `DAILY_LOCAL_SYNTHESIS_BRIEF_OPENING_TITLE_CHARS = 56`"
- Truncation order: per-title cap applied before assembly;180-char final cap applied as safety net after assembly, not as primary truncation
- Word-boundary behavior for English: "on a word boundary for English when possible, with `...` appended only when text is shortened"; Chinese character-capped with same `...` convention
- "first title"/"second title" defined at line 141: "the first two post-dedupe eligible cards in current edition order"
- Two-long-title regression test at lines 149–151 and 265–266: asserts `opening_read.en`≤ 180 chars, includes both shortened titles, ends cleanly with punctuation, no mid-word second-title fragment

One marginal note: the plan writes "such as `DAILY_LOCAL_SYNTHESIS_BRIEF_OPENING_TITLE_CHARS = 56`" (the phrase "such as" makes the name illustrative, not prescriptive), but the test at line 265 references "titles longer than the per-title cap," which anchors the constant's existence in the test contract. The softness is cosmetic; an implementer will define the constant.

---

**Prior Finding 2 — Dedupe semantics conflict between line 131 and line 156**

Status: **Resolved.**

Both occurrences are now consistent:
- Line 131: "Skip only duplicate normalized `(title, href)` pairs and duplicate normalized `read` text. Same-title/different-href articles remain eligible if their `read` text is distinct; same-source articles remain eligible."
- Line 161: "Dedupe by normalized `(title, href)` and normalized `read`. Do not dedupe by source name."

The prior conflict (independent `href` + `title` axes on one line, composite key on the other) is gone. The dedupe test at lines 253–257 now explicitly asserts same-title/different-href kept when reads differ, and same-source-but-distinct kept.

---

**Prior Finding 3 — source_count not specified as post-dedupe pre-cap**

Status: **Resolved.**

Lines 164–165 are now parallel:
> `article_count` is the number of post-dedupe eligible article-level synthesis candidates before the three-card cap is applied.
> `source_count` is the number of distinct normalized source names among post-dedupe eligible article-level synthesis candidates before the three-card cap is applied.

Both fields use the same phrase. The drift risk is closed.

---

**Prior Finding 4 — opencode rereview artifact was a live-capture stub**

Status: **Resolved.**

`docs/reviews/opencode-stage-383-plan-rereview.md` is now a complete structured review (Critical / Important / Minor sections,3 Important findings with reasoning, 3 Minor findings, summary sentence). It is not a stub.

---

## No Critical findings.

## No Important findings remain.

---

**Minor observations (not blockers):**

- The task-level description for `test_build_daily_local_synthesis_brief_caps_text_and_cards` (line 265–266) omits "includes both shortened titles" and "does not contain a mid-word second-title fragment." These assertions appear in the opening-read spec section (lines 149–151) but not in the task checklist. An implementer reading only the task section could write a weaker test. The spec section takes precedence, but the task description should ideally echo the key assertions.

- The Review Requirements section (line 534) says "Create rereview artifacts when Critical or Important findings are fixed" but does not carry the "Remove any opencode process chatter before the first review heading" instruction from Task 7. That instruction applies to code reviews; plan rerreviews have no equivalent cleanup directive in the plan. Low risk given the artifact is already clean, but a process consistency gap.

Neither observation is a plan correctness issue. The plan is implementable as written.

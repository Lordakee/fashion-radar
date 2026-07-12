### Critical
None remain from the original href-shape list. The builder/render href split is now correct and matches the real data shape.

### Important

**I1 — Opening-read title truncation still underspecified (carried forward).** Plan lines 142-147 cap the *combined* string to 180 chars but never specify: (a) whether each `{first title}`/`{second title}` is pre-truncated to a named per-title constant before assembly, (b) character- vs word-boundary truncation, (c) fallback when the cap eats into the second title, or (d) that "first/second title" means the first two post-dedupe cards in edition order. `test_build_daily_local_synthesis_brief_caps_text_and_cards` (line 257) only says "Provide long text" and does not pin a two-long-title scenario. An implementer following only the plan text could ship `Today's local read connects Brand X with Wholesa` (mid-word/mid-title). Fix: name a per-title constant (e.g. `_OPENING_READ_TITLE_MAX`), state truncation order explicitly, and add a two-long-title assertion.

**I2 (new) — Dedupe semantics conflict between line 131 and line 156.** Line 131 says "Skip duplicate hrefs and duplicate normalized article titles" — two *independent* axes, so a same-title/different-href article is dropped at eligibility. Line 156 says "Dedupe by normalized `(title, href)` and normalized `read`" — a *composite* key, so the same article is kept. These produce different card sets. The dedupe test (lines 248-250) does not disambiguate the same-title/different-href case. Pick one rule, align both lines, and add a test row for it.

**I3 (process gate) — `docs/reviews/opencode-stage-383-plan-rereview.md` is a live-capture stub.** It contains only 6 lines of "I'll review… / Let me explore…" chatter and zero review output, directly violating the AGENTS.md rule against live-capture stubs/tool-status messages/empty output. The opencode side of the rereview gate is therefore unmet; regenerate it with completed findings before proceeding.

### Minor

- **M1** — `source_count` (line 160) says "among eligible candidates" without "post-dedupe, pre-cap," unlike the parallel `article_count` (line 159). Tighten to match or the two counts can drift on same-source/slightly-different-name editions.
- **M2** — "first title"/"second title" (lines 144-145) and the cap for the single-read fallback branch (when fewer than two distinct reads) are implicit; state both.
- **M3 (optional)** — `article_count` still reads like a total count in the dataclass; rename to `eligible_article_count` remains optional now that line 159 documents "post-dedupe, pre-cap."

**Summary:** No Critical findings. Three Important findings remain (I1 truncation, I2 dedupe conflict, I3 stub artifact), so the plan is not yet implementable as-written.

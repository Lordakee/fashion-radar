## Stage 372 Plan/Spec Review — Daily Local Reading Itinerary

**Critical:** None.

**Important:** None.

All seven prior-concern fixes are correctly incorporated in both documents (signatures, counts, source-context semantics, evidence-label priority, dedupe key, dek, review commands). `body_source` confirmed real at `models.py:147` (a `RowOneLocalArticleBodySource` Literal). Stage 371 precedent (`source_count = len(emitted_sources)` at `daily_local_saved_article_organizer.py:218`, fed by `source_name.casefold()` at line 233) is the correct reference pattern.

**Minor findings, ordered by severity:**

**Minor 1 — `source_count` computation unspecified (spec silent).**
Confirmed. Spec line 92 defines `selected_count` but never `source_count`; the dataclass (plan:173) declares it and the builder test asserts `== 1` (plan:89). With a single-article fixture, unique-sources / unique-stories / unique-articles all yield 1, so the test cannot distinguish a wrong implementation. Add to the spec builder contract: *"compute `source_count` as the number of unique source names represented across rendered `Start Here` and `Skim Next` cards"* (matching Stage 371's casefolded-source set). Highest-impact minor since a wrong value would pass silently.

**Minor 2 — Paragraph-index fallback card anchor not stated in spec.**
Confirmed. Spec line 84 lists the three Skim-Next inputs but omits which href the paragraph-fallback case emits. The test (plan:114) pins it to the **content-section** anchor (not the paragraph anchor) while sourcing excerpt text from the valid paragraph index. Add to the spec: *"paragraph-index fallback cards link to the content-section anchor for the containing section, not the paragraph anchor."* The plan test catches a wrong guess, but the spec gap could cause a false RED.

**Minor 3 — Builder test has no dek assertion.**
Confirmed. `test_..._sequences_saved_content` (plan:76–110) asserts title, counts, start_here, skim_next, evidence_trail, and `Margaux bag`, but not `itinerary.dek.en`. The dek is defined (plan:187) and the render test checks the escaped value (plan:241), but a wrong dek string would only surface at render-test time, not at the unit level. Add `assert itinerary.dek.en == "A short path through today's saved local articles."` to the builder test block.

**Minor 4 — `evidence_count` definition implicit.**
Confirmed. Dataclass declares it (plan:174); render test asserts `3 evidence links`; builder test asserts `>= 2` (plan:90). `evidence_count = len(evidence_trail)` is unambiguous but, unlike `selected_count`/`source_count`, has no explicit computation rule — a consistency gap. Low impact; one clarifying line resolves it.

**Additional process note (Minor, not a spec/plan defect):** `docs/reviews/opencode-stage-372-plan-review.md:1–8` currently contains live-capture narration ("I'll review...", "Let me explore...") before the review body, which violates `REVIEW_PROTOCOL.md` "Review Capture Hygiene" and `AGENTS.md`'s "no live-capture stubs / tool-status messages" rule. Since Task 6 Step 4 `git add`s and commits this artifact, strip the narration lines (1–8) to a single coherent review body before commit.

**Verdict:** Approve for implementation. Minors 1–4 are spec/test-clarity gaps — recommended but non-blocking; none change architecture, boundaries, href safety, or the generated-site-only contract.

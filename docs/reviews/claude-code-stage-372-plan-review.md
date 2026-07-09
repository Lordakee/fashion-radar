**All7 prior review concerns are resolved.** All prior concern fixes are present and correctly incorporated:

- `_first_paragraph_anchor(article, page_href) -> str | None` — correctly defined in spec (line 81) and plan (line 188) with matching signatures.
- `selected_count` — defined as unique story ids across rendered Start Here and Skim Next (spec line 92, plan line 200); asserted in builder test (plan line 88) and render test (`1 selected read`).
- Source context semantics — emits one card per article regardless of Brand/Product; uses `body_source` + paragraph-count metadata not raw paragraph text (spec lines 87–88, plan lines 193–194).
- Evidence label priority — reference name → item label → section title → article title → paragraph label (spec line 119, plan lines 196–197).
- Dedupe key — `(href, normalized reason label)` tuple across Start Here and Skim Next, with explicit test assertion (plan lines 117–118).
- Dek — defined in builder (plan lines 186–187), escaped value asserted in render test (plan line 241).
- Review commands — `--permission-mode plan` for Claude Code (plan line 432), `zhipuai-coding-plan/glm-5.2--variant max` for opencode (plan line 437).

`body_source` is a confirmed real field on `RowOneLocalArticle` (models.py:147). Not an issue.

---

**No Critical findings.**

**No Important findings.**

---

**Minor findings, ordered by severity:**

**Minor1 — `source_count` computation not specified.**
Both documents declare `source_count: int` in the dataclass and assert `itinerary.source_count == 1` in the builder test, but neither the spec nor the plan defines how it is computed. The codebase pattern from Stage 371 (`len(emitted_sources)` at `daily_local_saved_article_organizer.py:218`) strongly implies unique source names from rendered cards, but the spec is silent on it. Because the test uses a single article, every plausible definition — unique sources from rendered cards, unique stories, unique articles — yields1, so the tests cannot distinguish a wrong implementation. Recommend adding one line to the spec builder contract: "compute `source_count` as the number of unique source names represented across rendered `Start Here` and `Skim Next` cards."

**Minor 2 — Builder test has no dek assertion.**
Prior concern fix required "Render and test the itinerary dek." The render test satisfies the render half (plan line 241: escaped dek string). `test_build_daily_local_reading_itinerary_sequences_saved_content` lists assertions for title, selected_count, source_count, evidence_count, start_here, skim_next, and evidence_trail, but has no `assert itinerary.dek.en == "A short path through today's saved local articles."` line. A wrong dek value would only be caught at render test time, not at the unit level. Recommend adding the dek assertion to the builder test block (plan line 79–109).

**Minor 3 — `evidence_count` field definition implicit.**
The dataclass declares `evidence_count: int`, the render test asserts `3 evidence links`, but neither document states `evidence_count = len(evidence_trail)`. The value is unambiguously implied, but since `selected_count` and `source_count` have their own explicit computation rules, the absence of an explicit rule for `evidence_count` is inconsistent.

**Minor 4 — Paragraph-index fallback card anchor type not stated in spec.**
Spec builder rule (line 84) says "build `Skim Next` cards from content-section items with item body, valid indexed paragraph fallback, or section body" without specifying which href the fallback case produces. The test (plan line 114) makes clear the card uses the content-section anchor — not the paragraph anchor — even when the excerpt comes from a paragraph-index fallback. The spec does not state this rule. Recommend adding "paragraph-index fallback cards link to the content-section anchor for the containing section, not to the paragraph anchor" to the spec builder contract.

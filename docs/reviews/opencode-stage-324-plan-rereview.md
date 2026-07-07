# opencode Stage 324 Plan Rereview

Fallback reviewer: local opencode  
Model: `zhipuai-coding-plan/glm-5.2`  
Variant: `max`  
Mode: read-only plan rereview

## Scope

Rereview of the Stage 324 plan after the C-1 fix from the initial
`opencode-stage-324-plan-review.md`. Files in scope:

- `docs/superpowers/specs/2026-07-07-stage-324-row-one-paragraph-evidence-index-design.md`
- `docs/superpowers/plans/2026-07-07-stage-324-row-one-paragraph-evidence-index-plan.md`
- `docs/reviews/opencode-stage-324-plan-review.md`

## C-1 Verification (Fixed)

**Status: RESOLVED.**

The previous Critical finding was that the docs test phrases in
`tests/test_row_one_docs.py` (Task 4 Step 1) did not match the proposed
README/docs paragraph wording (Task 4 Step 2/3), so the docs test would fail.

The fix rewrote the proposed Stage 324 README/docs paragraph to use the
established project convention of repeated `does not change ...` and
`does not add ...` clauses, matching the existing Stage 321/322/323 docs
paragraphs.

Verification method: programmatically normalized the proposed paragraph with
the same `_normalized()` logic used by the test (`" ".join(text.split()).casefold()`)
and checked all 17 docs test phrases.

Results — all 17 phrases FOUND in the normalized proposed paragraph:

1. `paragraph evidence index` — FOUND
2. `saved paragraph evidence` — FOUND
3. `` `rowonelocalarticle.content_sections` `` — FOUND
4. `` `paragraph_indices` `` — FOUND
5. `` `references` `` — FOUND
6. `` `#local-article-paragraph-n` `` — FOUND
7. `` `#local-article-content-section-n` `` — FOUND
8. `generated-site only` — FOUND
9. `does not change `row-one-app/v7`` — FOUND
10. `does not change `data/edition.json`` — FOUND
11. `does not change `row-one-manifest/v1`` — FOUND
12. `does not change `row-one-runtime/v1`` — FOUND
13. `does not add source collection` — FOUND
14. `does not add scoring` — FOUND
15. `does not add connectors` — FOUND
16. `does not add llm calls` — FOUND
17. `does not add compliance-review product features` — FOUND

The docs test slice anchors are also sound:
- Start anchor `stage 324 adds paragraph evidence index` is the normalized form
  of the paragraph's opening line and is unique in the file.
- End anchor `stage 323 adds local-first reading` is the normalized form of the
  existing Stage 323 paragraph opening, which remains immediately below the
  inserted Stage 324 paragraph.

The plan's Files section (lines 30, 32) and the design doc body text
(lines 15, 16, 151) now use `generated-site only` (space), matching the docs
test phrase and the existing docs convention. The previous M-3 minor is
resolved.

## Cross-Check: Existing Docs Tests Not Broken

Inserting the Stage 324 paragraph above Stage 323 does not break adjacent
docs tests:

- `test_row_one_docs_describe_local_first_reading_boundary` slices raw README
  content from `Stage 323 adds Local-First Reading` to `Stage 322 adds`.
  Inserting Stage 324 above Stage 323 does not enter this slice.
- `test_row_one_docs_describe_homepage_daily_edit_boundary` slices from
  `Stage 320 adds homepage Daily Edit` to `Stage 321 adds`, which spans across
  the 323 and 322 paragraphs. Its forbidden phrases (`adds source collection`,
  `adds scoring`, `adds llm calls`, `adds connectors`, `adds compliance review`)
  do not match the Stage 324 paragraph because `does not add X` does not
  contain `adds X` as a substring (`add ` vs `adds `).

## Critical Findings

None.

## Important Findings

None.

## Minor Suggestions

Carried over from the initial review (non-blocking):

- M-1: `_strict_valid_local_article_paragraph_indices` duplicates
  `_valid_local_article_paragraph_indices` with a bool guard. Acceptable for
  Stage 324; a future refactor could fold the bool guard into the shared
  helper.
- M-2: The Stage 324 docs test slices normalized content, while existing
  Stage 321/322/323 tests slice raw content then normalize the slice. Both
  approaches work; raw slicing would be more consistent with neighbors.
- M-4: Place the new JSON-absence assertions in `tests/test_workflows.py`
  near the existing `generated_contract_payload` boundary checks.
- M-5: The omission render test could also assert no
  `local-article-paragraph-evidence-row` class leaks.

New minor observations (non-blocking):

- M-6: The Stage 324 docs test omits the `forbidden_phrases` block that
  existing Stage 315-323 docs tests include. This is a style gap, not a bug:
  the proposed paragraph's `does not add X` wording means forbidden phrases
  like `adds X` would never match anyway. Adding the forbidden block would
  improve consistency with neighboring tests.
- M-7: The design doc Testing Requirements line 137 retains
  `generated-site-only` (hyphen) in the high-level description. This matches
  the existing Stage 323 design doc line 150 convention and is not a testable
  phrase (the docs test checks README and `docs/row-one.md`, not the design
  doc). No action required.

## Scope-Boundary Check

The plan correctly stays inside the generated-site boundary:

- No `row-one-app/v7`, `row-one-manifest/v1`, `row-one-runtime/v1`, schema,
  Pydantic model, or JSON-artifact changes.
- No source acquisition, fetching, extraction, scoring, ranking, LLM,
  translation, image-generation, connector, scheduling, deployment, or
  compliance-review behavior.
- No new dependencies.
- Anchors are derived from validated numeric positions via existing helpers.
- Display text passes through `_esc()`.
- Caps are explicit (8 rows, 4 items, 4 refs; 8 x 4 x 4 = 128 ref chips).
- No conflicts with `AGENTS.md` or `docs/REVIEW_PROTOCOL.md`.

## Verdict

**Approved.**

C-1 is fixed. The docs test and the proposed README/docs paragraph are
internally consistent. No new Critical or Important issues were introduced by
the fix. The remaining Minor suggestions are non-blocking style/consistency
items. The plan is technically sound, properly scoped, and consistent with the
current `templates.py` architecture and existing Stage 315-323 test patterns.

# opencode Stage 324 Plan Review

Fallback reviewer: local opencode  
Model: `zhipuai-coding-plan/glm-5.2`  
Variant: `max`  
Mode: read-only plan review

## Critical Findings

### C-1: Docs test assertions contradict the proposed README/docs paragraph wording

Location: `docs/superpowers/plans/2026-07-07-stage-324-row-one-paragraph-evidence-index-plan.md`, Task 4 Step 1 docs test vs Task 4 Step 2 README/docs paragraph.

The docs test asserts exact normalized phrases such as:

- `does not change `row-one-app/v7``
- `does not change `data/edition.json``
- `does not change `row-one-manifest/v1``
- `does not change `row-one-runtime/v1``
- `does not add source collection`
- `does not add scoring`
- `does not add connectors`
- `does not add llm calls`
- `does not add compliance-review product features`

The proposed README/docs paragraph instead uses one comma-separated `without changing ...` clause, so those `does not change ...` and `does not add ...` substrings will not appear after the docs test normalizes whitespace and casing. Existing Stage 322 and Stage 323 docs paragraphs use the project convention of repeated `does not change ...` / `does not add ...` wording.

Impact: `pytest tests/test_row_one_docs.py` will fail.

Recommended fix: rewrite the proposed Stage 324 README and `docs/row-one.md` paragraph in the plan to use the established docs convention, for example:

> Stage 324 adds Paragraph Evidence Index to generated ROW ONE detail pages. It is generated-site only and turns existing `RowOneLocalArticle.content_sections` items with existing `paragraph_indices`, existing `references`, existing `#local-article-paragraph-N` anchors, and existing `#local-article-content-section-N` anchors into a compact saved paragraph evidence index with safe internal links. It does not change `row-one-app/v7`, does not change `data/edition.json`, does not change `row-one-manifest/v1`, does not change `row-one-runtime/v1`, does not add `local_article_paragraph_evidence`, does not add `paragraph_evidence_index`, does not change schemas, does not write a new json artifact, does not add source collection, does not fetch article pages, does not add scoring, does not add llm calls, does not add connectors, and is not a compliance review feature.

## Important Findings

None.

The reviewer checked and considered the following sound:

- The workflow fixture should produce a local article with a valid `paragraph_indices=[0]` mapping, so Stage 324 workflow HTML marker assertions are feasible.
- Cap-test arithmetic is correct: 8 rows x 4 support items x 4 reference chips = 128 reference chips.
- The strict helper bool rejection design is correct when tested directly.
- Escaping expectations are consistent because `normalize_row_one_paragraph` is whitespace-only and `_esc()` performs HTML escaping.
- `Sequence` and `dataclass` are already imported in `templates.py`.
- Existing anchor helpers make the planned paragraph/content-section link math correct.

## Minor Suggestions

- M-1: `_strict_valid_local_article_paragraph_indices` duplicates `_valid_local_article_paragraph_indices` with a bool guard. This is acceptable for Stage 324; a future refactor could fold the bool guard into the existing helper.
- M-2: The proposed Stage 324 docs test slices normalized content, while existing Stage 322/323 tests slice raw content. Both work; raw slicing would be more consistent.
- M-3: The plan uses `generated-site-only`; existing docs prefer `generated-site only`.
- M-4: Add the new JSON absence assertions in `tests/test_workflows.py` near the existing `generated_contract_payload` boundary checks.
- M-5: The omission render test could also assert no `local-article-paragraph-evidence-row` class leaks.

## Scope-Boundary Check

The plan correctly stays inside the generated-site boundary:

- No `row-one-app/v7`, `row-one-manifest/v1`, `row-one-runtime/v1`, schema, Pydantic model, or JSON-artifact changes.
- No source acquisition, fetching, extraction, scoring, ranking, LLM, translation, image-generation, connector, scheduling, deployment, or compliance-review behavior.
- No new dependencies.
- Anchors are derived from validated numeric positions via existing helpers.
- Display text passes through `_esc()`.
- Caps are explicit.

No conflicts with `AGENTS.md` or `docs/REVIEW_PROTOCOL.md` were found.

## Verdict

Not approved until C-1 is fixed.

After C-1 is resolved, the plan is technically sound, properly scoped, and consistent with the current `templates.py` architecture and existing test patterns. Minor suggestions are non-blocking.

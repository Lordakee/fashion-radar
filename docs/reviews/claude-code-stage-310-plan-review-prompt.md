Review Stage 310 plan only. Do not modify files.

Repo: `/home/ubuntu/fashion-radar`
Design: `docs/superpowers/specs/2026-07-06-stage-310-row-one-saved-article-reader-design.md`
Plan: `docs/superpowers/plans/2026-07-06-stage-310-row-one-saved-article-reader-plan.md`

Goal: add a generated-site detail-page saved text reader for existing local article sidecars.

Check for Critical/Important issues only:
- internal contradictions between design and plan;
- missing TDD steps or affected existing tests;
- unsafe wording that implies full external article republication;
- accidental changes to source collection, scoring, schemas, `data/edition.json`, detail routes, paragraph anchors, `row-one-app/v7`, `row-one-manifest/v1`, or `row-one-runtime/v1`;
- docs-test phrases that do not match planned README/docs text;
- commands that violate the project frozen/no-config uv workflow;
- review artifact naming that violates `AGENTS.md`.

Known edge cases to verify:
- `RowOneLocalArticle.paragraphs` can be extracted source text, fallback summary, or appended ROW ONE context.
- New reader links add one more valid `href="#local-article-paragraph-3"` in an existing render test.
- `_meta_description()` uses Unicode ellipsis `…`.

Return:

## Verdict
Approve, Approve with Important fixes, or Reject.

## Critical Findings
- ...

## Important Findings
- ...

## Minor Findings
- ...

Keep the response concise, but every bullet must be a complete sentence. If a
section has no findings, write `None.`. Do not leave an unfinished sentence.

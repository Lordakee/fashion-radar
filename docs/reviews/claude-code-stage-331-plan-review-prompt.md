# Claude Code Stage 331 Plan Review Prompt

You are reviewing the Stage 331 plan in `/home/ubuntu/fashion-radar`.

Model/effort requirement from the user: use max reasoning effort.

## Goal

Stage 331 should add ROW ONE local article body provenance so generated saved
article content distinguishes:

- extracted article page text
- ROW ONE summary/editorial fallback text
- skipped/unusable extraction

The feature must improve information organization for the daily ROW ONE website
without adding compliance-review product behavior.

## Files To Review

- `docs/superpowers/specs/2026-07-07-stage-331-row-one-local-article-provenance-design.md`
- `docs/superpowers/plans/2026-07-07-stage-331-row-one-local-article-provenance-plan.md`
- Existing implementation context:
  - `src/fashion_radar/row_one/models.py`
  - `src/fashion_radar/row_one/articles.py`
  - `src/fashion_radar/row_one/site_metrics.py`
  - `src/fashion_radar/row_one/templates.py`
  - `src/fashion_radar/cli.py`
  - relevant tests under `tests/test_row_one_*.py`

## Review Focus

Findings first, ordered by severity.

Look for:

1. Any Critical/Important gap that would make the plan fail implementation.
2. Wrong function names, test helper names, or signatures in planned snippets.
3. Contract drift risk: `row-one-app/v7`, `data/edition.json`,
   `row-one-manifest/v1`, `row-one-runtime/v1`, detail routes, paragraph
   anchors, schemas.
4. Backward compatibility risk for existing sidecars without `body_source`.
5. Whether `skipped` sidecars should actually be generated in Stage 331 or only
   accepted by model/metrics.
6. Whether CLI/article-readiness payload additions require schema/docs/test
   updates not listed.
7. Whether the final commit allowlist includes every file the plan may modify.
8. Whether review/release verification is complete enough.

Do not propose adding compliance review functionality.

## Output Format

- Critical
- Important
- Medium
- Minor
- Verdict

Include file/line references where possible.

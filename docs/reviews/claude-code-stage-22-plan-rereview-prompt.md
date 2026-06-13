# Claude Code Stage 22 Plan Rereview Prompt

You are rereviewing the Stage 22 plan for `/home/ubuntu/fashion-radar` in
read-only mode. Do not edit files. Use maximum reasoning.

## Context

The first Stage 22 plan review is recorded in:

- `docs/reviews/claude-code-stage-22-plan-review.md`

It approved implementation but raised Important planning issues that should be
resolved before implementation:

1. JSON output included a `database` path while the design said no file paths.
2. Docs boundary scan was too broad to be actionable.
3. Commit/push step unconditionally pushed to `origin main`.
4. Source-name sorting needed clearer exact stored-label/collation behavior.
5. No-mutation testing could be stronger.

## Updated Plan

The Stage 22 plan now proposes:

- command: `fashion-radar imported-signals-summary`;
- no `--as-of`, lookback, or limit;
- current retained local `manual_import` rows only;
- exact stored `source_name` grouping and SQLite stored-text ascending order;
- top-level `database` path is explicitly allowed as an existing-style local
  database pointer, while imported source file paths remain excluded;
- docs scan uses `git diff -U0 -- README.md docs CHANGELOG.md | rg ...`;
- no-mutation test also checks `schema_metadata.version` and table set;
- commit/push step checks the current branch is `main` before pushing to
  `origin main` and instructs stopping/adapting if not.

## Documents To Rereview

- `docs/superpowers/specs/2026-06-13-stage-22-imported-source-summary-design.md`
- `docs/superpowers/plans/2026-06-13-stage-22-imported-source-summary-plan.md`
- `docs/reviews/claude-code-stage-22-plan-review-prompt.md`

## Review Request

Please verify whether all previous Critical/Important planning issues are
resolved and whether the plan is ready for implementation.

Focus on:

1. Is the `database` path vs imported source file path boundary now coherent?
2. Is the docs wording scan actionable as a diff scan?
3. Is the commit/push guidance safe enough for this direct-main workflow?
4. Is source-name sorting clear as exact stored text with no normalization,
   ranking, or source quality implication?
5. Are no-mutation tests strong enough for a read-only command?
6. Did the revisions accidentally add scope drift or new contradictions?

Return findings by severity:

- Critical: must fix before implementation.
- Important: should fix before implementation.
- Minor: optional polish.

Please end with one of:

- `Approved for Stage 22 implementation`
- `Not approved`

Do not modify files.

# Claude Code Stage 263 Plan Review Prompt

You are the primary plan reviewer for Fashion Radar Stage 263.

Review these files in `/home/ubuntu/fashion-radar`:

- `docs/superpowers/specs/2026-07-02-stage-263-row-one-app-contract-design.md`
- `docs/superpowers/plans/2026-07-02-stage-263-row-one-app-contract-plan.md`
- Current ROW ONE implementation under `src/fashion_radar/row_one/`
- Current ROW ONE tests under `tests/test_row_one_*.py`
- `docs/row-one.md`
- `docs/REVIEW_PROTOCOL.md`
- `AGENTS.md`

## Objective

Stage 263 should formalize ROW ONE `data/edition.json` as a stable app-facing
JSON contract for a separate ROW ONE app.

## Architecture / Tech Stack

- Keep `RowOneEdition` as the internal presentation model.
- Add a deterministic app payload builder for `data/edition.json`.
- Add `contract_version: "row-one-app/v1"`.
- Add client-ready section/story fields derived from existing data.
- Add `schemas/row-one-app.schema.json` and tests.
- Do not alter collection, matching, ranking, scoring, story IDs, HTML output,
  cleanup, server behavior, schedule behavior, deployment, LLMs, translation,
  platform APIs, demand proof, platform coverage verification, or compliance
  product behavior.

## Implementation Method

Follow TDD:

1. Add failing payload and schema tests.
2. Implement the app payload builder in `render.py`.
3. Add JSON Schema.
4. Update CLI smoke tests and docs.
5. Run focused verification.
6. Run code review, full gate, release review, commit, and push.

## Review Focus

Please check:

- whether Stage 263 is the right next increment after Stage 262;
- whether changing `data/edition.json` to a versioned app contract is acceptable
  or if the plan should preserve a raw payload separately;
- whether the schema and payload fields are concrete enough;
- whether tests avoid overfitting while locking the public contract;
- whether the design preserves ROW ONE boundaries and the collect -> match ->
  report path;
- whether review artifacts and verification gates satisfy project protocol.

## Output Format

Return one coherent review body only:

- Verdict: accept / accept with fixes / reject
- Critical findings
- Important findings
- Minor findings
- Required plan/spec fixes before coding
- Optional follow-ups

Do not modify files.

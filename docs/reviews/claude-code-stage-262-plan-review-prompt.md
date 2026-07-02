# Claude Code Stage 262 Plan Review Prompt

You are the primary plan reviewer for Fashion Radar Stage 262.

Review these files in `/home/ubuntu/fashion-radar`:

- `docs/superpowers/specs/2026-07-02-stage-262-row-one-reader-orientation-design.md`
- `docs/superpowers/plans/2026-07-02-stage-262-row-one-reader-orientation-plan.md`
- Current ROW ONE implementation under `src/fashion_radar/row_one/`
- Current ROW ONE tests under `tests/test_row_one_*.py`
- `docs/REVIEW_PROTOCOL.md`
- `AGENTS.md`

## Objective

Stage 262 should add a deterministic reader-orientation layer to ROW ONE:

- homepage edition contents;
- section jump links;
- current story counts;
- story-card metadata;
- detail-page back-to-section links.

## Architecture / Tech Stack

- Keep implementation in `src/fashion_radar/row_one/templates.py`.
- Use existing `RowOneEdition`, `RowOneSection`, and `RowOneStory` data only.
- Use static HTML/CSS/JS template strings, pytest, and Ruff.
- Do not alter collection, matching, ranking, scoring, story IDs, JSON payload
  shape, server behavior, cleanup behavior, deployment, LLMs, translation,
  platform APIs, demand proof, platform coverage verification, or compliance
  product behavior.

## Implementation Method

Follow TDD:

1. Add failing render tests for homepage contents and section counts.
2. Implement `_render_edition_nav()` and styles.
3. Add failing render/CLI tests for story-card metadata and detail back links.
4. Implement story orientation metadata and detail return link.
5. Add docs boundary tests and documentation.
6. Run focused verification, full gate, code review, release review, commit, and
   push.

## Review Focus

Please check:

- whether the scope is the right next increment after Stage 261;
- whether the plan is concrete enough for implementation;
- whether test expectations are specific and not brittle;
- whether the design preserves ROW ONE boundaries;
- whether any task risks touching frozen `external-tool-*`, `community-*`, or
  `imported-*` behavior;
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

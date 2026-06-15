## Stage 51 Plan Review

### Critical findings

None.

### Important findings

1. **Matched imported-signal validators are wired before matching runs.**

   In the current smoke flow, `imported-signals-summary` and `imported-signals` run before `match`:

   - `scripts/check_first_run_smoke.py`: import dry-run/import → `imported-signals-summary` → `imported-signals` → `match` → `report`

   The Stage 51 plan proposes validators that require:

   - `imported-signals-summary.matched_count == 2`
   - `imported-signals.matched_count == 2`
   - item-level matches for `The Row`, `The Row Margaux`, and `Ballet Flats`

   Those expectations should only be true after the `match` command has populated `item_entities`. As written, the real smoke would likely fail, while the updated command-sequence test stubs would mask the ordering problem by returning matched fake payloads too early.

   **Required fix before implementation:** either:

   - move `match` before the imported summary/review commands, then validate matched imported rows; or
   - keep the pre-match imported review as an import-only check, then rerun `imported-signals-summary` / `imported-signals` after `match` for matched-count and match-detail validation.

2. **The plan requires push/GitHub Actions/external service steps despite the stage boundary.**

   The Stage 51 context says this stage must remain local-first/free-first and must not require external services. The implementation plan’s Task 4 includes:

   - reading a GitHub token from `/home/ubuntu/.config/fashion-radar/github-token`
   - pushing directly to `origin main`
   - checking GitHub Actions via the GitHub API

   That conflicts with the stated stage boundary and with `docs/github-upload-checklist.md`, which says the user controls remote creation, pushing to GitHub, publishing, and uploads.

   **Required fix before implementation:** remove commit/push/GitHub Actions confirmation from the required Stage 51 implementation plan, or clearly move them to an optional, user-explicit post-stage release step. Local verification, release hygiene, package build, installed-wheel smoke, and local Claude Code release review are sufficient for this stage.

### Minor findings

1. **The plan should explicitly account for recording the plan review.**

   `docs/REVIEW_PROTOCOL.md` requires pre-coding plan review records under `docs/reviews/`. The plan includes release-review records after implementation, but it does not explicitly mention recording this Stage 51 plan review before coding.

   This is process-related rather than a design blocker, but adding a plan-review record step would better satisfy the staged workflow.

2. **`docs/cli-reference.md` drift protection is weaker than the other doc updates.**

   The plan modifies `docs/cli-reference.md`, but the proposed `tests/test_cli_docs.py` additions mostly pin README / first-run / upload-checklist wording. If the CLI reference wording matters, add a small assertion that the CLI reference mentions the deterministic sample-output gate, not just command execution.

3. **Some validators intentionally pin exact strings; keep them focused.**

   The exact stdout checks are reasonable for a release smoke, but they should remain limited to stable user-facing lines. Avoid asserting full stdout or incidental path formatting. The proposed checks mostly do this well.

### Review focus answers

1. **Staged workflow and boundaries**

   Mostly yes, but not fully. The local implementation, tests, docs, and review-gated approach fit the staged workflow. However, the required push/GitHub Actions steps violate the local-first/no-external-services boundary for this stage and should be removed or made optional/user-triggered. Also add/record the plan review artifact if not already handled outside the plan.

2. **Changing the two-row CSV to match starter entities**

   Yes. This is a sound approach. The proposed rows use existing starter aliases and required context terms:

   - `The Row Margaux` row includes `The Row Margaux`, `handbag`, and `tote`, which supports both `The Row` and `The Row Margaux` without broadening aliases.
   - `Ballet flats` row includes `ballet flats`, `shoes`, and `footwear`, satisfying the configured category context.

   This makes first-run output useful without weakening matching rules.

3. **Smoke validators**

   The proposed validators are meaningful and mostly appropriately scoped: row counts, exact sample URLs/titles, matched starter entities, report presence, trend deltas, empty candidates, and directory handoff counts are good semantic gates.

   The main validator issue is ordering: matched imported-summary/imported-signals checks must run after `match`.

4. **Tests and docs**

   The test plan is broadly sufficient: unit tests for validator pass/fail behavior, command-sequence stubs, CSV contract tests, docs drift tests, source smoke, installed-wheel smoke, and full verification should prevent drift.

   Improvements:

   - make the command-sequence test reflect the real match-before-matched-review order;
   - add a docs assertion for the CLI reference if that wording is changed;
   - ensure the real smoke, not only stubs, is part of verification after the ordering fix.

5. **Blockers before implementation**

   There are **Important** blockers:

   - fix the validator/match ordering;
   - remove or optionalize required push/GitHub Actions/external-service steps.

Implementation should **not** proceed until those Important issues are fixed.

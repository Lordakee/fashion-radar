## Critical

No Critical blockers found in the proposed Stage 22 design or implementation plan.

## Important

1. **JSON output contradicts the “no file paths” boundary**
   - The design says the command “does not expose … file paths,” but the JSON contract includes:
     ```json
     "database": "data/fashion-radar.sqlite"
     ```
   - The tests also assert the database path is present.
   - If “file paths” means only imported source file paths, say that explicitly. Otherwise remove `database` from the public output contract or replace it with a non-path indicator.
   - This should be resolved before implementation because it affects the output schema and tests.

2. **Docs boundary scan is too broad to be actionable as written**
   - The proposed `rg` command searches all `README.md docs CHANGELOG.md` for terms such as `source quality`, `source health`, and `source coverage`.
   - Existing files like `docs/community-signal-quality.md` and `docs/source-boundaries.md` are likely to contain those terms legitimately.
   - The plan says “Expected: no new problematic wording,” but the command itself cannot distinguish existing allowed guardrail language from newly introduced problematic wording.
   - Recommend changing verification to one of:
     - scan only `git diff`;
     - run the broad scan but require manual review of hits;
     - use `git diff -U0 -- README.md docs CHANGELOG.md | rg ...`.

3. **Commit/push step should not unconditionally push to `origin main`**
   - The plan ends with:
     ```bash
     git push origin main
     ```
   - That is operationally risky unless the project intentionally works directly on `main`.
   - Recommend adding explicit branch/status checks and making push target conditional on the current workflow, e.g. “push the current Stage 22 branch” or “only push main if the user/project explicitly requires direct-main updates.”

4. **Clarify that `source_name` is an exact stored label, including case/collation behavior**
   - The design says sorting is by stored `source_name` ascending and grouping is exact, which is good.
   - SQLite default text ordering can be case-sensitive and locale-light. That is acceptable, but the docs/tests should not imply human-friendly alphabetical normalization.
   - A brief note like “ordered by SQLite’s stored text value; no normalization or ranking is applied” would make the deterministic/non-ranking intent clearer.

5. **No-mutation testing could be slightly stronger**
   - Current no-mutation test checks `items` and `item_entities` row counts before/after.
   - That is useful, but a read-only command should also avoid creating side artifacts and avoid touching schema metadata.
   - Consider also checking:
     - no config/report/data artifacts are created for missing DB;
     - schema version/table counts remain unchanged for existing DB;
     - optionally file modification time is unchanged if stable enough for the test environment.
   - Not a blocker because the read-only engine test is the stronger protection.

## Minor

1. **CLI name is acceptable**
   - `imported-signals-summary` is clear and remains inside the imported-signals review boundary.
   - It distinguishes the command from `imported-signals` by making it aggregate/source-label oriented rather than row-review oriented.
   - It does not inherently imply source health, quality, coverage, or ranking.

2. **Command is sufficiently distinct from `imported-signals`**
   - `imported-signals` reviews individual retained rows with time/window/filter behavior.
   - `imported-signals-summary` aggregates all retained `manual_import` rows by stored source-name label.
   - The proposed output avoids row-level titles, URLs, summaries, match reasons, and internal match details.

3. **Summarizing all retained local `manual_import` rows without `--as-of`, lookback, or limit is appropriate**
   - The command is a current-state inventory summary, not a review window.
   - Omitting ranking/limit/lookback helps avoid source-ranking or source-performance implications.
   - The wording “currently retained local rows” is the right boundary.

4. **Counts are well-defined**
   - `row_count`: retained local `items` rows where `source_type == "manual_import"`.
   - Grouping: exact stored `source_name`.
   - `matched_count`: item-level existence of at least one `item_entities` row.
   - `unmatched_count`: `row_count - matched_count`.

5. **Match-count inflation is addressed**
   - The proposed query uses item-level `EXISTS`, so one item with multiple entity matches counts once.
   - The planned test with two matches for a single item directly covers this.

6. **Ascending source-name sort avoids ranking implications**
   - Sorting by label rather than count, match count, latest timestamp, or “top” language is appropriate.
   - The docs should continue to avoid “top sources,” “best sources,” “coverage,” or “quality” wording.

7. **Read-only behavior is preserved**
   - Missing DB returns an empty summary before creating an engine.
   - Existing DB uses `create_readonly_sqlite_engine`.
   - The command does not initialize schema, migrate, import, match, score, report, or write dashboard artifacts.

8. **The implementation plan stays within scope**
   - No migrations, collectors, schedulers, watch folders, source acquisition, matching/scoring changes, dashboard writes, reports, platform APIs, or scraping behavior are proposed.
   - The docs updates need careful wording, especially in `docs/community-signal-quality.md`, but the plan’s intended wording is bounded.

9. **Test coverage is broadly sufficient**
   - Covered: missing DB, invalid format, manual-only filtering, grouping, match-count inflation, sorting, invalid schema, table/JSON output, no mutation, special-character paths, docs boundary scan.
   - Suggested additions are refinements, not blockers.

10. **Verification commands are mostly adequate**
   - Focused pytest, full pytest, ruff, format check, `git diff --check`, lock check, frozen sync check, build, installed-wheel smoke, and hygiene scans are appropriate.
   - Improve the docs scan and commit/push instructions as noted above.

## Overall readiness

The plan is close and technically sound. The main item to fix before implementation is the output-contract contradiction around exposing a database file path while claiming no file paths are exposed. After that clarification, the remaining issues are verification/process polish.

Approved for Stage 22 implementation

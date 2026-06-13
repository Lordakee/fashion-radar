## Critical

No Critical blockers found.

## Important

No Important blockers found. The previous Important planning issues appear resolved sufficiently for implementation.

## Minor

1. **Commit/push guard is directionally safe, but the shell block could be made more fail-closed**
   - The plan now checks:
     ```bash
     current_branch="$(git branch --show-current)"
     test "$current_branch" = "main"
     ```
     and explicitly says to stop/adapt if not on `main`.
   - This resolves the prior “unconditional push to `origin main`” issue at the plan level.
   - Optional polish: make the command block itself fail-closed with an explicit `if`/`exit 1`, since `test ...` only stops the sequence automatically if executed under `set -e` or as part of a chained command:
     ```bash
     if [ "$current_branch" != "main" ]; then
       echo "Not on main; stop and adapt push target."
       exit 1
     fi
     ```
   - Not a blocker because the prose instruction is clear and the direct-main workflow is explicit.

2. **Docs diff scan is actionable, but expected wording could be slightly clearer**
   - The updated scan:
     ```bash
     git diff -U0 -- README.md docs CHANGELOG.md | rg ...
     ```
     fixes the prior problem of scanning all historical docs and surfacing unrelated existing guardrail language.
   - The plan also states that existing negative scope guards may appear only as guardrails.
   - Minor wording issue: because Stage 22 may add new negative guardrail language in docs/review artifacts, “existing negative scope guards” could be broadened to “negative scope guard wording may appear only as guardrails.”
   - Not a blocker; the scan is now usable as a diff review.

3. **Sorting behavior is clear; optional edge-case test could strengthen it**
   - The design now says source summaries are ordered by the exact stored `source_name` text value in SQLite ascending order, with no normalization, merging, locale-aware collation, or ranking.
   - This resolves the prior ambiguity.
   - Optional polish: add a test with mixed-case or punctuation labels if the project wants to lock down SQLite default collation behavior visibly.

## Previous Issue Resolution Check

1. **`database` path vs imported source file path boundary** — Resolved.
   The design now explicitly allows the top-level local SQLite `database` path as an existing-style database pointer while continuing to exclude imported source file paths, row URLs, titles, summaries, raw import rows, and internal match details. This boundary is coherent.

2. **Docs wording scan actionable as diff scan** — Resolved.
   The scan now runs against `git diff -U0 -- README.md docs CHANGELOG.md`, making it focused on Stage 22 changes rather than all historical documentation. The plan also allows guardrail hits with manual review.

3. **Commit/push guidance safe enough for direct-main workflow** — Resolved with minor polish noted.
   The plan now checks the current branch is `main`, shows branch/status, and instructs stopping/adapting if not on `main`. For this repository’s direct-main workflow, that is sufficient planning guidance.

4. **Source-name sorting exact stored text / no ranking implication** — Resolved.
   The design explicitly says exact stored `source_name`, SQLite ascending order, no normalization, no merging, no locale-aware collation, and no ranking. That is clear and bounded.

5. **No-mutation tests strong enough** — Resolved.
   The updated plan checks:
   - missing DB creates no config/data/report artifacts;
   - invalid format avoids query/database access and creates no `--data-dir`;
   - existing DB preserves `items` count;
   - preserves `item_entities` count;
   - preserves `schema_metadata.version`;
   - preserves table set;
   - query uses read-only engine.

   This is strong enough for a read-only command.

6. **Scope drift or new contradictions** — None found.
   The plan remains local-first and read-only. It does not introduce collectors, migrations, matching/scoring changes, reports, dashboards, watch folders, schedulers, platform/API integrations, source acquisition, source quality, source health, source coverage, or ranking behavior.

Approved for Stage 22 implementation

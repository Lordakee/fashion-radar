## Critical

1. **Output privacy boundary conflict blocks implementation.**
   The design states the command must not output “source files” or “import paths,” but the planned output model includes top-level `path`, and the planned table renderer prints:

   ```text
   File: <path>
   ```

   This directly conflicts with the stated safety boundary and the user’s instruction that output must not include source files or import paths. Fix before coding by either:
   - removing `path` from JSON and table output, or
   - explicitly revising the design to allow a sanitized display name only.

   Given the user’s current constraints, the safer fix is: **do not output the supplied path at all**.

## Important

1. **The plan is too broad for one implementation node.**
   The core feature is scoped well enough: one new module, one CLI command, focused tests. But the plan also includes broad docs updates, review-doc generation, full release verification, build/wheel smoke tests, lock checks, commit, and push. That is more than one focused implementation node.

   Recommended split:
   - Node 1: implementation + focused tests.
   - Node 2: docs updates.
   - Node 3: final verification/review/commit/push, only if explicitly requested.

2. **Output-safety tests are too shallow.**
   The planned privacy test checks only forbidden top-level keys and candidate keys:

   ```python
   assert forbidden.isdisjoint(payload)
   assert forbidden.isdisjoint(payload["candidates"][0])
   ```

   This would not catch private values leaking inside serialized JSON/table output, such as row URLs, titles, summaries, raw text, normalized keys, contexts, representative item details, source file paths, import paths, or account/private fields.

   Add recursive/string-level assertions against:
   - JSON serialized output
   - table output
   - nested candidate values

3. **Required test cases are incomplete despite the design listing them.**
   The plan should add explicit tests for:

   - review thresholds filtering candidates;
   - single-token thresholds;
   - per-row duplicate candidate mention suppression;
   - `candidate_discovery.enabled: false`;
   - invalid `--format` before file loading;
   - negative `--limit` before file loading;
   - invalid config clean error;
   - no SQLite/data/report/dashboard artifacts created;
   - CLI help listing `community-candidates`;
   - newline sanitization, not only pipe sanitization;
   - recursive privacy checks for URLs, titles, summaries, raw text, contexts, normalized keys, source paths, and representative item fields.

4. **Validation-order requirements need stronger test coverage.**
   The design is clear that invalid `--as-of` must fail before reading the input file. The plan partially covers this by parsing `--as-of` before calling `preview_community_candidates`.

   However, the broader CLI-error requirements are not fully tested. The plan should prove file loading does not happen for:
   - invalid `--as-of`;
   - invalid `--format`;
   - negative `--limit`.

   It should also clearly state whether config loading may occur before invalid input-file errors. The current design says invalid config exits before extraction, but the ordering relative to file access should be made explicit.

5. **Documentation scope needs guardrails.**
   The implementation avoids source collection, scheduling, dashboard, report generation, SQLite writes, and entity config generation. But the docs task touches several broad docs files. The plan should explicitly constrain docs updates to describing the new local pre-import preview only, and should not change semantics around:
   - source collection;
   - scheduling;
   - dashboard/report behavior;
   - stored database state;
   - entity YAML generation;
   - source health/quality/ranking.

6. **Candidate duplicate handling may fail the design without a targeted test.**
   The design says each row contributes at most one mention per candidate normalized key. The implementation plan loops over `phrases` returned by `extract_candidate_phrases()`. That helper currently deduplicates by key internally, so this may work, but the plan should still include a test proving repeated mentions in the same row count once.

7. **`path` in module model also conflicts with CLI/table privacy.**
   This is not only a renderer issue. The planned `CommunityCandidatePreview` model itself includes:

   ```python
   path: str
   ```

   If retained, JSON output will leak source/import path by design. Remove it from the model or make it non-serialized/internal-only.

## Minor

1. **Scoring and label behavior is coherent for a local pre-import preview.**
   The plan correctly avoids SQLite stored matches and uses `configured_entity_keys()` only. The local labels `new`, `rising`, and `observed` are reasonable for pre-import preview.

2. **Known-entity suppression caveat is acceptable but should be explicit.**
   Because SQLite stored matches are intentionally not consulted, entities known only through stored DB matches may still appear. This matches the design, but the docs or plan should mention this is a pre-import/config-only suppression model.

3. **`candidate_count` before `limit` is coherent.**
   The design expects `limit=0` to show no candidates while preserving aggregate row count and candidate count before limit. The implementation plan does this, but it should call out that `candidate_count` means “pre-limit candidate count.”

4. **Fallback source-name behavior is coherent.**
   Blank `--source-name` normalization to `Community Tool Export` and row-level fallback through `load_manual_signal_rows()` are aligned with existing patterns.

5. **Avoid commit/push in the implementation plan unless explicitly requested.**
   The plan’s final commit/push instructions are operationally useful, but should be separated from implementation. Also keep the explicit `uv.lock` exclusion.

## Verdict

Blocking findings remain. Do **not** begin implementation yet.

The main required fixes are:

1. Remove or redesign `path`/`File:` output to satisfy the privacy boundary.
2. Strengthen recursive JSON/table privacy tests.
3. Add the missing required tests.
4. Narrow or split the plan into implementation/test, docs, and finalization phases.
5. Clarify validation ordering for invalid `--format`, negative `--limit`, invalid config, and file reading.

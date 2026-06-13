You are re-reviewing the revised Stage 27A plan before implementation.

Repository: `/home/ubuntu/fashion-radar`

Previous review:

- `docs/reviews/claude-code-stage-27-plan-review.md`

The previous review blocked implementation because:

1. the plan exposed the supplied input path in JSON/table output;
2. the implementation node was too broad;
3. output-safety tests were too shallow;
4. several required tests were missing;
5. validation ordering needed stronger coverage.

Revised design and plan:

- `docs/superpowers/specs/2026-06-13-stage-27-community-candidate-preview-design.md`
- `docs/superpowers/plans/2026-06-13-stage-27-community-candidate-preview-plan.md`

Goal:

Add `fashion-radar community-candidates`, a local read-only command that
previews aggregate candidate phrases from one user-supplied community signal
CSV/JSON file before import.

Important context:

- This is Stage 27A: implementation plus focused tests only. Broad docs updates,
  final release verification, Claude Code code review, commit, and push are now
  explicitly out of scope for this node.
- The current worktree may still have a pre-existing `uv.lock` mirror URL diff.
  Stage 27A must not modify, stage, or commit `uv.lock`.
- Stage 27A should read one local file and local config only. It must not add
  live collection, platform APIs, account automation, directory watching,
  recursive file discovery, SQLite reads/writes, config writes, report/dashboard
  writes, candidate approval state, or entity YAML draft generation.
- The command may output aggregate candidate phrases and counts. It must not
  output local file paths, row URLs, row titles, summaries, raw text, normalized
  keys, candidate contexts, source files, import paths, account/private fields,
  or representative item details.
- The implementation should use existing parser/extraction/config patterns:
  `load_manual_signal_rows()`, `extract_candidate_phrases()`,
  `configured_entity_keys()`, `ScoringSettings`, and
  `CandidateDiscoverySettings`.

Review focus:

1. Are all previous Critical and Important findings resolved?
2. Is the Stage 27A node scoped tightly enough for implementation plus focused
   tests?
3. Does the plan avoid outputting the supplied file path in JSON, table output,
   and CLI file-error output?
4. Does the plan avoid changing source collection, scheduling, dashboard, report
   generation, stored database state, and entity config generation?
5. Are validation-order requirements clear and tested for invalid `--as-of`,
   invalid `--input-format`, negative `--limit`, invalid config, and file
   reading?
6. Are recursive output-safety tests strong enough for JSON and table output?
7. Are tests sufficient for current/baseline windows, fallback source names,
   known entity suppression, thresholds, per-row duplicate suppression,
   disabled candidate discovery, `limit=0`, table sanitization, CLI help, clean
   errors, and artifact absence?
8. Is the planned scoring/label behavior coherent enough for a pre-import local
   preview without depending on SQLite stored matches?

Output format:

- List findings by severity: Critical, Important, Minor.
- Critical and Important findings block implementation and must be fixed before
  coding.
- If no blocking findings remain, include the exact phrase:
  `APPROVED FOR IMPLEMENTATION`.

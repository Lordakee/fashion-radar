You are reviewing the revised Stage 27A plan before implementation.

Repository: `/home/ubuntu/fashion-radar`

Goal:

Add `fashion-radar community-candidates`, a local read-only command that
previews aggregate candidate phrases from one user-supplied community signal
CSV/JSON file before import.

Design and plan:

- `docs/superpowers/specs/2026-06-13-stage-27-community-candidate-preview-design.md`
- `docs/superpowers/plans/2026-06-13-stage-27-community-candidate-preview-plan.md`

Important context:

- This is Stage 27A: implementation plus focused tests only. Broad docs updates,
  final release verification, commit, and push are intentionally out of scope
  for this node.
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

1. Is the Stage 27A node now scoped tightly enough for implementation plus
   focused tests?
2. Does the plan avoid outputting the supplied file path in JSON, table output,
   and CLI file-error output?
3. Does the plan avoid changing source collection, scheduling, dashboard, report
   generation, stored database state, and entity config generation?
4. Are validation-order requirements clear and tested for invalid `--as-of`,
   invalid `--input-format`, negative `--limit`, invalid config, and file
   reading?
5. Are recursive output-safety tests strong enough for JSON and table output?
6. Are tests sufficient for current/baseline windows, fallback source names,
   known entity suppression, thresholds, per-row duplicate suppression,
   disabled candidate discovery, `limit=0`, table sanitization, CLI help, clean
   errors, and artifact absence?
7. Is the planned scoring/label behavior coherent enough for a pre-import local
   preview without depending on SQLite stored matches?

Output format:

- List findings by severity: Critical, Important, Minor.
- Critical and Important findings block implementation and must be fixed before
  coding.
- If no blocking findings remain, include the exact phrase:
  `APPROVED FOR IMPLEMENTATION`.

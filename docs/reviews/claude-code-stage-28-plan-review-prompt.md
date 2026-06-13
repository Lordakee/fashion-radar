You are reviewing the Stage 28 plan before implementation.

Repository: `/home/ubuntu/fashion-radar`

Goal:

Add `fashion-radar community-candidates-dir`, a local read-only command that
previews aggregate candidate phrases from a non-recursive directory of
user-supplied community signal CSV/JSON handoff files before import.

Design and plan:

- `docs/superpowers/specs/2026-06-13-stage-28-community-candidates-dir-design.md`
- `docs/superpowers/plans/2026-06-13-stage-28-community-candidates-dir-plan.md`

Important context:

- This is Stage 28: implementation plus focused tests only. Broad docs updates,
  final release verification, commit, and push are intentionally out of scope
  for this node.
- The current worktree may still have a pre-existing `uv.lock` mirror URL diff.
  Stage 28 must not modify, stage, or commit `uv.lock`.
- Stage 28 should read local files directly under one supplied local directory
  and local config only. It must not add live collection, platform APIs, account
  automation, browser automation, directory watching, recursive file discovery,
  schedulers, SQLite reads/writes, config writes, report/dashboard writes,
  candidate approval state, or entity YAML draft generation.
- The command may output aggregate candidate phrases and counts. It must not
  output local directory paths, file paths, file names, row URLs, row titles,
  summaries, raw text, normalized keys, candidate contexts, source files, import
  paths, raw validation findings, account/private fields, or representative
  item details.
- Directory/file/row errors must be generic and must not echo supplied paths,
  filenames, row values, raw loader findings, validation details, or traceback.
- The implementation should use existing parser/extraction/config patterns:
  `load_manual_signal_directory_rows()`, `extract_candidate_phrases()`,
  `configured_entity_keys()`, `ScoringSettings`, and
  `CandidateDiscoverySettings`.

Review focus:

1. Is the Stage 28 node scoped tightly enough for implementation plus focused
   tests?
2. Does the plan avoid outputting the supplied directory path, matched file
   paths, matched file names, pattern, raw findings, or row-level values in JSON,
   table output, and CLI error output?
3. Does the plan avoid changing source collection, scheduling, dashboard, report
   generation, stored database state, and entity config generation?
4. Are validation-order requirements clear and tested for invalid `--as-of`,
   invalid `--input-format`, negative `--limit`, invalid config, and directory
   reading?
5. Are recursive output-safety tests strong enough for JSON and table output?
6. Are tests sufficient for multi-file aggregation, non-recursive direct-child
   matching, pattern filtering, fallback source names, known entity suppression,
   thresholds, per-row duplicate suppression, disabled candidate discovery,
   `limit=0`, CLI help, clean generic errors, and artifact absence?
7. Is the planned scoring/label behavior coherent enough for a pre-import local
   directory preview without depending on SQLite stored matches?

Output format:

- List findings by severity: Critical, Important, Minor.
- Critical and Important findings block implementation and must be fixed before
  coding.
- If no blocking findings remain, include the exact phrase:
  `APPROVED FOR IMPLEMENTATION`.

You are re-reviewing the Stage 28 plan before implementation.

Repository: `/home/ubuntu/fashion-radar`

Previous review:

- `docs/reviews/claude-code-stage-28-plan-review.md`

Updated design and plan:

- `docs/superpowers/specs/2026-06-13-stage-28-community-candidates-dir-design.md`
- `docs/superpowers/plans/2026-06-13-stage-28-community-candidates-dir-plan.md`

Goal:

Add `fashion-radar community-candidates-dir`, a local read-only command that
previews aggregate candidate phrases from a non-recursive directory of
user-supplied community signal CSV/JSON handoff files before import.

Changes made after your previous review:

- Removed Stage 28 code-review prompt creation/submission from the implementation
  plan. Claude Code code review, release verification, commit, and push are now
  explicitly follow-up node work, not Stage 28 implementation work.
- Added CLI JSON recursive forbidden-value scans over actual stdout.
- Added validation-order requirements proving invalid `--as-of`, invalid
  `--input-format`, and negative `--limit` fail before config load and before
  directory preview/read; invalid config must prevent directory preview/read.
- Added custom pattern and regular-file behavior tests, including matching
  directories ignored and no recursive traversal for nested files.
- Added score/label/parity/tie-break assertions after factoring shared scoring.
- Broadened unexpected-exception handling to use a generic directory-preview
  error instead of printing raw exception text.

Important context:

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

Review focus:

1. Are all Critical and Important findings from the previous review resolved?
2. Is the Stage 28 node scoped tightly enough for implementation plus focused
   tests?
3. Does the updated plan avoid outputting supplied directory paths, matched file
   paths, matched file names, pattern, raw findings, or row-level values in JSON,
   table output, and CLI error output?
4. Are validation-order requirements now clear and tested for config loading
   and directory reading?
5. Are tests now sufficient for multi-file aggregation, non-recursive
   direct-child matching, custom pattern filtering, regular-file-only behavior,
   fallback source names, known entity suppression, thresholds, per-row duplicate
   suppression, disabled candidate discovery, `limit=0`, score/label/tie-break
   behavior, CLI help, clean generic errors, and artifact absence?

Output format:

- List findings by severity: Critical, Important, Minor.
- Critical and Important findings block implementation and must be fixed before
  coding.
- If no blocking findings remain, include the exact phrase:
  `APPROVED FOR IMPLEMENTATION`.

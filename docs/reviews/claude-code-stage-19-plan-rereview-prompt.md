# Claude Code Stage 19 Plan Rereview Prompt

You are rereviewing the Stage 19 plan for `/home/ubuntu/fashion-radar` in
read-only mode. Do not edit files. Use maximum reasoning.

Initial review approved the stage but raised Important plan clarifications. The
plan and design have been revised.

## Files To Review

- `docs/superpowers/specs/2026-06-12-stage-19-import-signals-directory-execution-design.md`
- `docs/superpowers/plans/2026-06-12-stage-19-import-signals-directory-execution-plan.md`
- Initial review result:
  `docs/reviews/claude-code-stage-19-plan-review.md`

## Important Findings To Verify

Please verify that the revised plan now covers:

1. `--imported-at` behavior during `--dry-run`: if supplied, it is validated
   before directory reads or artifact creation, even though it is unused during
   dry-run.
2. Explicit no-artifact coverage for invalid directory and unreadable directory
   in the actual import path.
3. Explicit preservation of the Stage 18 dry-run JSON shape:
   `ManualSignalDirectoryDryRunResult` fields unchanged, no `rows` field leaks
   into dry-run output, and the CLI still serializes the dry-run result model.
4. Atomic validation-before-import coverage using a valid first sorted matched
   file and invalid later sorted matched file, proving no partial import.
5. Docs and GitHub upload checklist coverage includes manual import docs,
   community signal docs, community signal quality docs, architecture, source
   boundaries, README, changelog, and installed-wheel smoke tests.

The Stage 19 scope remains local user-provided files only. It must not add or
document scraping, crawling, platform APIs, account automation, source export
acquisition, watch folders, schedulers, recursive scanning, collectors,
authorization verification, or approval/audit/policy workflow product features.

Return findings by severity:

- Critical: must fix before implementation.
- Important: should fix before implementation.
- Minor: optional polish.

Please end with one of:

- `Approved for Stage 19 implementation`
- `Not approved`

Do not modify files.

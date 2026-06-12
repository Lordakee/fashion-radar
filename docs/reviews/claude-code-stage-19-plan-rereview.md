## Critical

No Critical findings.

## Important

No Important findings. The revised Stage 19 design and implementation plan address the prior Important clarifications:

1. **`--imported-at` during `--dry-run`** — Covered.
   The design explicitly states that `--imported-at` is validated even during `--dry-run`, before file reads or `--data-dir` creation, and that the parsed timestamp is unused during dry-run. The plan also adds CLI tests for invalid `--dry-run --imported-at`.

2. **No-artifact coverage for invalid and unreadable directories** — Covered.
   The plan now explicitly lists invalid directory and unreadable directory cases in Task 2 Step 3, requiring non-zero exit, Stage 18 diagnostics, and no database/artifact creation.

3. **Stage 18 dry-run JSON shape preservation** — Covered.
   The design and plan both explicitly require `ManualSignalDirectoryDryRunResult` fields to remain unchanged, no `rows` field to leak into dry-run JSON, existing `files[*]` / `findings[*]` nesting to remain unchanged, and CLI dry-run JSON to continue serializing `ManualSignalDirectoryDryRunResult.model_dump_json(indent=2)`.

4. **Atomic validation-before-import coverage** — Covered.
   The design and plan now require a validation failure test where the first sorted matched file is valid and a later sorted matched file is invalid, proving the CLI does not import incrementally and opens no SQLite database on batch validation failure.

5. **Docs and GitHub upload checklist coverage** — Covered.
   The plan’s documentation task includes updates to:
   - `README.md`
   - `docs/manual-signal-import.md`
   - `docs/community-signal-import.md`
   - `docs/community-signal-quality.md`
   - `docs/architecture.md`
   - `docs/source-boundaries.md`
   - `docs/github-upload-checklist.md`
   - `CHANGELOG.md`

   It also requires installed-wheel smoke checks for `import-signals-dir --help`, dry-run, and a tiny local directory import into a temporary `--data-dir`.

The local-only Stage 19 boundary is also preserved. The design and plan continue to exclude scraping, crawling, platform APIs, account automation, source export acquisition, watch folders, schedulers, recursive scanning, collectors, authorization verification, and approval/audit/policy workflow product features.

## Minor

1. **Release-check smoke-test snippet could mirror the docs checklist more explicitly.**
   Task 3 Step 1 says the installed-wheel smoke checks should include help, dry-run, and tiny local import. Task 4 Step 2 only shows the tiny local import command inline. This is not a blocker because the docs checklist requirement is explicit, but implementation would be slightly clearer if Task 4 also listed the help and dry-run smoke commands.

Approved for Stage 19 implementation

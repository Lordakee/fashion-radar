# Claude Code Stage 17 Plan Rereview Prompt

You are rereviewing the Stage 17 plan for Fashion Radar after the first Claude
Code plan review returned `Not approved`. Run this as a read-only planning
review. Do not edit files, do not commit, do not call the network, do not run
collectors, do not create directories, do not open SQLite, and do not execute
platform/social/community tooling.

Project: `/home/ubuntu/fashion-radar`

Use maximum reasoning effort. The invoking command should be:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-17-plan-rereview-prompt.md
```

## Prior Review Result

The first review asked for these fixes before implementation:

1. Replace `Path.glob(pattern)` with direct-child enumeration using
   `directory.iterdir()` plus `fnmatch.fnmatch(path.name, pattern)`, so patterns
   such as `**/*.csv` cannot recurse.
2. Handle unreadable directories and directory enumeration `OSError` as stable
   `invalid_directory` findings.
3. Make directory JSON severity counts (`error_count`, `warning_count`,
   `info_count`) serialized fields rather than non-serialized properties, and
   update JSON shape tests.
4. Add explicit invalid-directory module/CLI tests, including missing path or a
   file path used as a directory, and unreadable-directory module coverage where
   feasible.
5. Make aggregate count ordering deterministic with
   `dict(sorted(counter.items()))`.
6. Make no-artifact CLI tests explicit with env/default config/data/reports,
   SQLite, report, digest, latest/index/workflow artifact assertions.
7. Specify deterministic directory-level finding sorting.

## Plan And Design To Rereview

Please rereview:

- `docs/superpowers/specs/2026-06-12-stage-17-community-signal-directory-lint-design.md`
- `docs/superpowers/plans/2026-06-12-stage-17-community-signal-directory-lint-plan.md`

## Goal

Stage 17 should add a local, read-only directory-level community signal
diagnostics command:

```bash
fashion-radar community-signal-lint-dir ./exports --input-format csv --pattern "*.csv"
fashion-radar community-signal-lint-dir ./exports --input-format json --pattern "*.json"
fashion-radar community-signal-lint-dir ./exports --input-format csv --pattern "*.csv" --format json
fashion-radar community-signal-lint-dir ./exports --input-format json --pattern "*.json" --strict
```

The command should help external tools controlled by the user write multiple
sanitized local handoff files into a local directory and preflight them before
any single-file `import-signals --dry-run` or import step.

This is not a product-facing compliance review, audit workflow, safety workflow,
policy checklist, approval UI, authorization verifier, platform connector,
scraper, crawler, browser automation flow, social monitoring system, source
acquisition tool, multi-file import, multi-file dry-run, watch folder, or
current-hotness ranking.

## Rereview Questions

Please focus on whether the revised plan fully resolves the prior Important
findings:

1. Direct-child non-recursive matching is technically guaranteed.
2. Invalid or unreadable directories produce stable `invalid_directory`
   findings.
3. Directory JSON output includes serialized severity counts.
4. Invalid-directory and no-artifact tests are concrete enough.
5. Aggregate counts and directory findings are deterministic.
6. Docs and scope still avoid platform/source acquisition instructions,
   platform claims, and policy/compliance/audit product features.

Also flag any remaining plan issue that should block implementation.

## Response Format

Start with one of:

- `Approved for Stage 17 implementation`
- `Not approved`

Then list findings in this format:

- `Critical:` issues that must be fixed before implementation.
- `Important:` issues that should be fixed before implementation.
- `Minor:` optional improvements.

If approved, still list any Minor improvements. If not approved, be specific
about the exact file/section and the change needed.

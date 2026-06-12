# Claude Code Stage 12 Plan Rereview 2 Prompt

You are rereviewing the Stage 12 plan for Fashion Radar after the second Claude
Code plan review still found Important read-only boundary issues in the
implementation plan. Run this as a read-only planning review. Do not edit
files, do not commit, do not call the network, do not run collectors, do not
create directories, do not open SQLite, and do not execute platform/social
tooling.

Project: `/home/ubuntu/fashion-radar`

Use maximum reasoning effort. The invoking command should be:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-12-plan-rereview-2-prompt.md
```

## Files To Review

- `docs/superpowers/specs/2026-06-12-stage-12-source-pack-quality-design.md`
- `docs/superpowers/plans/2026-06-12-stage-12-source-pack-quality-plan.md`
- `docs/reviews/claude-code-stage-12-plan-review.md`
- `docs/reviews/claude-code-stage-12-plan-rereview.md`

## Second Review Findings To Verify

Please verify that the remaining Important read-only boundary findings have
been fixed in `docs/superpowers/plans/2026-06-12-stage-12-source-pack-quality-plan.md`:

1. Task 3 should now name CLI tests proving that `source-pack-lint` does not
   create default or explicit config/data/report directories, `fashion-radar.sqlite`,
   `*.sqlite*`, collector artifacts, report artifacts, digest artifacts, or
   workflow artifacts.

2. Task 6 installed-wheel smoke should now:
   - copy the source pack to a temporary path;
   - run `source-pack-lint` from an isolated working directory;
   - set explicit `FASHION_RADAR_CONFIG_DIR`, `FASHION_RADAR_DATA_DIR`, and
     `FASHION_RADAR_REPORTS_DIR` paths;
   - assert the isolated working directory does not contain default
     config/data/report directories;
   - assert the explicit config/data/report directories were not created;
   - assert no `fashion-radar.sqlite`, `*.sqlite*`, collector artifacts, report
     artifacts, digest artifacts, or workflow artifacts were created.

3. Acceptance Criteria should now explicitly say no default or explicit
   config/data/report directories, no `fashion-radar.sqlite`, no `*.sqlite*`,
   no collector artifacts, no report artifacts, no digest artifacts, and no
   workflow artifacts.

## Stage 12 Goal

Stage 12 should improve daily fashion information quality by adding local
source-pack diagnostics and expanding the public RSS/GDELT starter pack with
bounded GDELT coverage lanes. It must not add collection behavior, social
platform extraction, network fetches, DB schema changes, source-health changes,
dashboard changes, or a product-facing compliance/audit workflow.

## Response Format

Start with one of:

- `Approved for Stage 12 implementation`
- `Not approved`

Then list findings in this format:

- `Critical:` issues that must be fixed before implementation.
- `Important:` issues that should be fixed before implementation.
- `Minor:` optional improvements.

If approved, still list any Minor improvements. If not approved, be specific
about the exact file/section and the change needed.

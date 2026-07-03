# Stage 271 Focused Plan Re-review Request

Review only these two files:

- `docs/superpowers/specs/2026-07-03-stage-271-row-one-app-content-organization-design.md`
- `docs/superpowers/plans/2026-07-03-stage-271-row-one-app-content-organization-plan.md`

This is a focused re-review after a prior NOT APPROVED result. Do not perform a
full project review. Do not inspect implementation files unless a cited line in
the plan makes the answer impossible.

Return exactly one of:

- `APPROVED`
- `NOT APPROVED`

Then list concise blockers only.

## Prior Blockers To Verify

1. C1 Manifest schema update:
   - The manifest contract must remain `row-one-manifest/v1`.
   - The plan/spec must require `schemas/row-one-manifest.schema.json` to update
     nested `app_contract.version.const` from `row-one-app/v1` to
     `row-one-app/v2`.
   - The plan/spec must not add `runtime_path` or content arrays to manifest
     `site`.

2. C2 Active `row-one-app/v1` inventory:
   - The plan must explicitly include a search step:
     `rg -n "row-one-app/v1" src tests schemas docs README.md scripts`.
   - The plan must include active pin updates for at least:
     `schemas/row-one-manifest.schema.json`,
     `tests/test_row_one_app_contract.py`,
     `tests/test_row_one_render.py`,
     `tests/test_row_one_cli.py`,
     `tests/test_first_run_smoke.py`,
     `tests/test_row_one_docs.py`,
     current docs/README if applicable.
   - The plan must say historical stage/review docs may retain old version
     strings.
   - The schema drift test that used to reject `row-one-app/v2` must now reject
     `row-one-app/v3`.

3. I1 `editorial_takeaway` in detail organization:
   - The spec and plan must include `editorial_takeaway` in story
     `detail_sections`.
   - The plan's test snippets must assert the section key and body mirror the
     story field.
   - The HTML alignment task must include Editorial Takeaway / `编辑整理`.

Do not raise optional product-scope expansions as blockers. Stage 271 is limited
to app-facing content organization and HTML alignment.

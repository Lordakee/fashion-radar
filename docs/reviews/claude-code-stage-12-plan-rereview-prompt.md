# Claude Code Stage 12 Plan Rereview Prompt

You are rereviewing the Stage 12 plan for Fashion Radar after the first Claude
Code plan review returned `Not approved` with no Critical findings and two
Important findings. Run this as a read-only planning review. Do not edit files,
do not commit, do not call the network, do not run collectors, do not create
directories, do not open SQLite, and do not execute platform/social tooling.

Project: `/home/ubuntu/fashion-radar`

Use maximum reasoning effort. The invoking command should be:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-12-plan-rereview-prompt.md
```

## Files To Review

- `docs/superpowers/specs/2026-06-12-stage-12-source-pack-quality-design.md`
- `docs/superpowers/plans/2026-06-12-stage-12-source-pack-quality-plan.md`
- `docs/reviews/claude-code-stage-12-plan-review.md`

## First Review Findings To Verify

Please verify that these two Important findings have been fixed:

1. Strengthen the read-only boundary tests for `source-pack-lint`.
   The plan should now explicitly test that the command does not create default
   or explicit config/data/report directories, `fashion-radar.sqlite`,
   `*.sqlite*`, collector artifacts, report artifacts, digest artifacts, or
   workflow artifacts. The installed-wheel smoke should also check those paths.

2. Mirror the full explicit out-of-scope list in the design Non-Goals and plan
   Scope Guard.
   The design and plan should now explicitly exclude official or unofficial
   social platform APIs, platform search/export instructions, raw comments,
   full post bodies, DMs, account IDs, follower lists, images, videos,
   downloads, reposting, LLM scoring, embeddings, vector databases, image
   recognition, and paid-service requirements.

## Additional Minor Notes Incorporated

- The plan now asks for a short implementation comment explaining why raw YAML
  is read before typed validation.
- Duplicate name, URL, and query findings should report every source in each
  collision group.
- URL normalization tests should cover lowercased scheme/host, stripped
  fragments, and trailing slash trimming while preserving query strings.
- `article_extraction_enabled` remains informational and is framed as a
  local-pack quality reminder, not a compliance or policy check.

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

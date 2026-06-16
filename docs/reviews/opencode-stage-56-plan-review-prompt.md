# Opencode Stage 56 Plan Review Prompt

You are reviewing the Stage 56 implementation design and plan for the
`fashion-radar` repository before implementation begins.

Required review mode:

- Review model: GLM 5.2 via local opencode
  (`zhipuai-coding-plan/glm-5.2`).
- This is a plan review only.
- Do not edit files.
- Do not narrate tool usage or file-reading steps.
- Keep the response concise.
- Treat Critical and Important findings as blocking.

## Goal

Add a local-only `community-handoff-check-dir` command that aggregates existing
directory lint, candidate preview, and import dry-run checks into one handoff
readiness report for user-controlled community signal directories.

## Files To Review

- `docs/superpowers/specs/2026-06-17-stage-56-community-handoff-check-design.md`
- `docs/superpowers/plans/2026-06-17-stage-56-community-handoff-check-plan.md`
- Current related files:
  - `src/fashion_radar/cli.py`
  - `src/fashion_radar/community_signals.py`
  - `src/fashion_radar/community_candidates.py`
  - `src/fashion_radar/importers/manual_signals.py`
  - `src/fashion_radar/community_handoff_workflow.py`
  - `src/fashion_radar/community_handoff_manifest.py`
  - `src/fashion_radar/community_signal_profile.py`
  - `tests/test_cli.py`
  - `tests/test_cli_docs.py`
  - `tests/test_community_handoff_workflow.py`
  - `tests/test_community_handoff_manifest.py`
  - `tests/test_community_signal_profile.py`
  - `docs/cli-reference.md`
  - `docs/community-signal-import.md`
  - `docs/github-upload-checklist.md`

## Required Boundaries

The plan must not add:

- source acquisition;
- platform collection;
- scraping/crawling;
- browser automation;
- platform API clients;
- account login/cookies/sessions/tokens;
- monitoring, scheduling, or watching;
- media download;
- demand proof;
- source ranking;
- platform/community coverage verification;
- entity generation;
- SQLite writes;
- report/dashboard/digest generation;
- profile, workflow, or manifest ordering changes;
- compliance-review, legal-review, approval UI, authorization verifier, safety
  review, or policy workflow features;
- dependency or lockfile changes.

## Review Questions

1. Is a standalone `community-handoff-check-dir` command the right next step
   after Stage 55 directory examples?
2. Does the plan reuse existing lint, candidate preview, and import dry-run
   functions instead of duplicating parsing/import logic?
3. Are the result model fields, exit semantics, and source-name/default handling
   coherent?
4. Does the plan keep invalid `--as-of` and invalid config behavior clean and
   side-effect-free?
5. Are tests and docs scoped enough to catch public command drift without
   changing producer profile/workflow/manifest contracts?
6. Is the verification/upload plan sufficient and mirror-safe?

## Required Output

Respond with:

- `## Critical Findings`
- `## Important Findings`
- `## Minor Findings`
- `## Verdict`

If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 56 COMMUNITY HANDOFF CHECK
```

# Stage 178 Plan Review Prompt

Review the Stage 178 plan for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
This is a read-only review: do not edit files, do not run `git stash`, and do
not mutate the working tree.
Start the response exactly with:

# Stage 178 Plan Review

Objective:

Add focused regression guards for community handoff directory check renderer
count labels and unavailable candidate preview output.

Files to review:

- `docs/superpowers/specs/2026-06-24-stage-178-community-handoff-renderer-guard-design.md`
- `docs/superpowers/plans/2026-06-24-stage-178-community-handoff-renderer-guard-plan.md`
- `docs/reviews/opencode-stage-178-plan-review-prompt.md`
- Existing context:
  - `tests/test_community_handoff_check.py`
  - `src/fashion_radar/community_handoff_check.py`
  - `docs/reviews/opencode-stage-171-code-review.md`

Scope boundaries:

- Test-only hardening unless a new test reveals an actual renderer defect.
- No planned runtime behavior changes.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, monitoring, scheduling, demand proof, ranking, coverage verification
  features, compliance-review product features, dependency changes, or
  `uv.lock` changes.

Review questions:

1. Does the plan directly address the Stage 171 follow-up notes for plural
   renderer output and unavailable candidate preview rendering?
2. Are the proposed tests deterministic and scoped to renderer behavior rather
   than candidate scoring internals?
3. Is the singular test rename safe and useful?
4. Are the verification, review, release, commit, and push steps sufficient for
   a small test-only stage?
5. Are there any critical or important issues to fix before implementation?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Guidance
- Verdict

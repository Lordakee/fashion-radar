# Stage 180 Plan Review Prompt

Review the Stage 180 plan for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
This is a read-only review: do not edit files, do not run `git stash`, and do
not mutate the working tree.
Start the response exactly with:

# Stage 180 Plan Review

Objective:

Add a regression test proving the package archive checker reports both invalid
UTF-8 errors when a wheel contains invalid bytes in both `METADATA` and
`entry_points.txt`.

Files to review:

- `docs/superpowers/specs/2026-06-24-stage-180-package-archive-dual-invalid-utf8-design.md`
- `docs/superpowers/plans/2026-06-24-stage-180-package-archive-dual-invalid-utf8-plan.md`
- `docs/reviews/opencode-stage-180-plan-review-prompt.md`
- Existing context:
  - `tests/test_package_archives.py`
  - `scripts/check_package_archives.py`
  - `docs/reviews/opencode-stage-163-release-review.md`

Scope boundaries:

- Test-only hardening unless the new test exposes a real aggregation defect.
- No planned package archive checker runtime changes.
- No planned archive metadata, required-member, forbidden-member, sdist,
  dependency, or `uv.lock` changes.
- No source acquisition, scraping, platform APIs, monitoring, scheduling, demand
  proof, ranking, coverage verification features, or compliance-review product
  features.

Review questions:

1. Does the plan directly address the Stage 163 follow-up note about combined
   invalid UTF-8 coverage?
2. Is the proposed test deterministic and scoped to aggregation behavior?
3. Is the placement next to existing invalid UTF-8 tests appropriate?
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

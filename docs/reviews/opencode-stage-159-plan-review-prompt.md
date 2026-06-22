# Stage 159 Plan Review Prompt

Review the Stage 159 design and implementation plan for Fashion Radar.

Files to review:

- `docs/superpowers/specs/2026-06-23-stage-159-review-artifact-hygiene-gate-design.md`
- `docs/superpowers/plans/2026-06-23-stage-159-review-artifact-hygiene-gate-plan.md`
- Existing implementation context:
  - `scripts/check_release_hygiene.py`
  - `tests/test_release_hygiene.py`
  - `AGENTS.md`
  - `docs/REVIEW_PROTOCOL.md`
  - `docs/github-upload-checklist.md`

Objective:

Add an automated release-hygiene guard that rejects malformed Stage 159+ local
review capture artifacts before commit or GitHub upload.

Proposed implementation:

- Add review-artifact path matching for completed opencode review output files
  under `docs/reviews/`.
- Enforce only Stage 159 and newer artifacts so historical review records remain
  untouched.
- Ignore review prompt files.
- Check both tracked and untracked files.
- Reject empty output, ANSI escape output, tool-status lines, opencode UI
  marker lines that start with status glyphs or `build middle-dot`, and
  first-line process chatter.
- Allow ordinary review prose such as `pytest -q -> passed`.
- Keep this as a release/process hygiene gate only, with no product/runtime
  feature changes.

Review questions:

1. Is Stage 159+ review artifact hygiene a safe and useful next narrow stage?
2. Is the Stage 159 enforcement floor the right way to avoid historical review
   churn?
3. Are the proposed markers narrow enough to catch capture mistakes without
   likely false positives in legitimate review analysis?
4. Do the RED tests prove tracked/untracked coverage and prompt/legacy
   exclusions?
5. Does the plan preserve the product scope boundaries: no social connectors,
   scraping, browser automation, platform APIs, login/session/cookie behavior,
   monitoring, scheduling, source acquisition, demand proof, ranking, coverage
   verification, or compliance-review product features?
6. Are any release-gate or review-gate steps missing?

Return critical, important, and minor findings. If there are no blocking
findings, say so explicitly.

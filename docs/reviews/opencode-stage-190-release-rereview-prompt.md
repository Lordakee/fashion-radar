# Stage 190 Release Rereview Prompt

You are rereviewing Stage 190 after the release review found one Important
process issue: the plan's final `git add` manifest omitted
`docs/github-upload-checklist.md`, plan rereview #3 artifacts, and code
rereview artifacts.

Please inspect:

- `docs/superpowers/plans/2026-06-24-stage-190-source-liveness-diagnostics-plan.md`
- `docs/reviews/opencode-stage-190-release-review.md`
- current `git status --short`

Confirm:

1. The plan's file list and final `git add` block now include
   `docs/github-upload-checklist.md`.
2. The plan includes plan rereview #3, code rereview, release review, and release
   rereview artifacts.
3. No Critical or Important release-blocking issue remains before commit/push.

Return Markdown starting with exactly:

`# Stage 190 Release Rereview`

Use sections: Critical, Important, Minor, Verdict.

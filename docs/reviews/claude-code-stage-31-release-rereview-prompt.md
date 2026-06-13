# Claude Code Stage 31 Release Rereview Prompt

You are rereviewing Stage 31 after the first release review found a process
blocker:

- `docs/reviews/claude-code-stage-31-release-review-prompt.md` and
  `docs/reviews/claude-code-stage-31-release-review.md` were not listed in the
  first review prompt's changed/new files.
- The release-review result artifact was being written during that review and
  was reported as empty/incomplete.

Resolution:

- Both release-review files are now intentionally part of the Stage 31 commit
  scope.
- `docs/reviews/claude-code-stage-31-release-review.md` now contains the first
  release review findings.
- `docs/release-gate-stage31.md` now lists the release-review prompt/result in
  the review artifacts section.

Please review the full current Stage 31 commit scope:

- `docs/release-gate-stage31.md`
- `docs/github-upload-checklist.md`
- `docs/superpowers/specs/2026-06-13-stage-31-release-gate-design.md`
- `docs/superpowers/plans/2026-06-13-stage-31-release-gate-plan.md`
- `docs/reviews/claude-code-stage-31-*.md`

Check:

1. The first release review blocker is resolved.
2. No Stage 31 review artifact is empty or outside the intended commit scope.
3. The docs/review artifacts remain accurate and ready to commit.
4. No runtime feature creep, prohibited platform/source-acquisition claims,
   secrets, generated artifacts, staged `uv.lock`, or push-hygiene issues are
   introduced.

If and only if this is ready to commit and push, include this exact phrase:

```text
APPROVED FOR STAGE 31 COMMIT AND PUSH
```

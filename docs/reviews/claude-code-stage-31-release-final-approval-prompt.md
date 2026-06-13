# Claude Code Stage 31 Release Final Approval Prompt

You are doing a final approval check after the previous release rereview found
only a self-referential artifact race: the rereview result file was empty while
Claude was writing to it.

Resolution:

- `docs/reviews/claude-code-stage-31-release-rereview.md` is now populated with
  the previous rereview result.
- Future Claude output for this final approval is being written outside the
  repo first, then copied into the repo after completion, so it will not appear
  as an empty file during your review.

Please review the current intended Stage 31 commit scope:

- `docs/release-gate-stage31.md`
- `docs/github-upload-checklist.md`
- `docs/superpowers/specs/2026-06-13-stage-31-release-gate-design.md`
- `docs/superpowers/plans/2026-06-13-stage-31-release-gate-plan.md`
- `docs/reviews/claude-code-stage-31-*.md`

Check:

1. No existing Stage 31 review artifact is empty.
2. The first release-review blocker and rereview artifact race are resolved.
3. The docs/review artifacts are ready to commit.
4. No staged/dirty `uv.lock`, secrets, generated artifacts, runtime feature
   creep, prohibited platform/source-acquisition claims, or push-hygiene issues
   remain.

If and only if this is ready to commit and push, include this exact phrase:

```text
APPROVED FOR STAGE 31 COMMIT AND PUSH
```

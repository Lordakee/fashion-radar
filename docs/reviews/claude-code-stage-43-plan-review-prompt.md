# Claude Code Stage 43 Plan Review Prompt

You are reviewing the Stage 43 Claude review protocol restore plan for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.

## User Rule Change

The user canceled the temporary local opencode/GLM 5.2 review rule and asked to
return review work to local Claude Code.

## Goal

Restore Claude Code with `--effort max` as the active plan and code/release
review authority, while preserving historical opencode records as audit history.

## Proposed Technical Approach

- Update `AGENTS.md` active review gate instructions from local opencode/GLM 5.2
  to local Claude Code with `--effort max`.
- Update `docs/REVIEW_PROTOCOL.md` active review process, command examples, and
  review record naming from `opencode-stage-N-*` to `claude-code-stage-N-*`.
- Keep `docs/github-upload-checklist.md` unchanged unless a real inconsistency
  is found; it already points to Claude Code in Final Review.
- Add `tests/test_review_protocol_docs.py` to assert active workflow docs do not
  contain active opencode authority terms such as `local opencode`,
  `opencode run`, `zhipuai-coding-plan/glm-5.2`, `GLM 5.2`, or
  `docs/reviews/opencode-stage-N`, and do contain the expected Claude Code
  command/naming terms.
- Allow the narrow historical note that older `opencode-*` review records under
  `docs/reviews/` are audit records and do not need rewriting.
- Scope the guard to active workflow docs only:
  - `AGENTS.md`
  - `docs/REVIEW_PROTOCOL.md`
  - `docs/github-upload-checklist.md`
- Do not rewrite historical review artifacts, prior stage specs/plans, runtime
  behavior, package metadata, lockfiles, CI, databases, dashboards, scraping,
  crawling, platform automation, source acquisition, schedulers, watchers,
  monitors, or external services.

## Files To Review

- `docs/superpowers/specs/2026-06-15-stage-43-claude-review-protocol-restore-design.md`
- `docs/superpowers/plans/2026-06-15-stage-43-claude-review-protocol-restore-plan.md`

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 43 CLAUDE REVIEW PROTOCOL RESTORE
```

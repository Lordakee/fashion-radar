# Claude Code Stage 31 Plan Review Prompt

You are reviewing the Stage 31 release-gate plan for the `fashion-radar`
repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Verify that Stage 31 will produce a reproducible GitHub release-readiness gate
for the current public command surface after Stage 30.

## Proposed Technical Approach

- Tech stack: Python package managed by `uv`, pytest, ruff, git, Markdown
  process docs, installed-wheel CLI smoke checks.
- Stage 31 is a verification/documentation node, not a runtime feature node.
- It must not add source connectors, scraping, crawling, platform automation,
  login/browser automation, watchers, schedulers, source acquisition, source
  ranking, demand proof, or platform coverage verification.
- It should run dependency checks with a mirror through
  `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple` where practical,
  but must not persist mirror URLs in `uv.lock`.
- It should restore the locally mirror-rewritten `uv.lock` before claiming
  release readiness.
- It should build wheel/sdist, install the wheel into a temp venv, smoke the
  public CLI command surface, and specifically verify the Stage 30
  `community-handoff-workflow` command remains print-only and does not create
  supplied missing directories.
- It should run boundary scans, secret scans, artifact scans, package content
  checks, and public examples smoke checks.
- It should add concise release-gate evidence docs and review artifacts, then
  commit/push only Stage 31 files with no staged `uv.lock`.

## Files To Review

- `docs/superpowers/specs/2026-06-13-stage-31-release-gate-design.md`
- `docs/superpowers/plans/2026-06-13-stage-31-release-gate-plan.md`

## Specific Questions

1. Does the design/plan satisfy the user-required workflow: plan first, Claude
   Code plan review before execution, Claude Code release review before commit
   and push?
2. Is the strict `uv.lock` cleanup requirement clear enough, including no dirty
   lockfile and no persisted mirror URLs?
3. Is the installed-wheel public command help loop broad enough for the current
   CLI surface, including `community-handoff-workflow`?
4. Is the `community-handoff-workflow` behavior smoke adequate for Stage 30's
   print-only/no-directory-creation contract?
5. Are package content checks, public example smokes, boundary scans, and
   secret/artifact scans sufficient for a GitHub release gate?
6. Does the plan avoid implying or implementing scraping, crawling, platform
   automation, source acquisition, or platform connector functionality?
7. Are there any commands that are destructive, likely to dirty tracked files
   unexpectedly, or likely to leave generated artifacts in the repo?

## Output Required

Respond with:

- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A concise verdict.

If and only if the plan is acceptable to execute, include this exact approval
phrase:

```text
APPROVED FOR STAGE 31 RELEASE GATE
```

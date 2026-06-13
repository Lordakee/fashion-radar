# Claude Code Stage 32 Plan Review Prompt

You are reviewing the Stage 32 CI release hygiene plan for the `fashion-radar`
repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Stage 32 should align GitHub CI, contributor docs, PR/issue templates, and upload
smoke commands with the Stage 31 release-gate findings.

## Proposed Technical Approach

- CI should run `UV_NO_CONFIG=1 uv lock --check` and
  `UV_NO_CONFIG=1 uv sync --locked --dev --check` before the normal install.
- CI should reject mirror/index URL markers in `uv.lock`.
- CI build smoke should build to a temp directory and install the wheel from
  that temp directory, not from repository `dist/`.
- Contributor docs/templates should use `UV_NO_CONFIG=1` for public lockfile
  checks and keep `UV_DEFAULT_INDEX=... uv sync --frozen ...` for mirror-backed
  local installs.
- Upload package smoke docs should avoid a bare `python` command and use
  `uv run python` or a temp venv interpreter.
- Stage 32 must not add runtime features, platform connectors, scraping,
  crawling, browser automation, source acquisition, watchers, schedulers,
  source ranking, demand proof, or platform coverage claims.

## Files To Review

- `docs/superpowers/specs/2026-06-14-stage-32-ci-release-hygiene-design.md`
- `docs/superpowers/plans/2026-06-14-stage-32-ci-release-hygiene-plan.md`

## Specific Questions

1. Is this the right next node after Stage 31 for GitHub readiness?
2. Are the proposed CI changes technically sound, including the `tmp_build`
   handoff between build smoke and dashboard extra smoke?
3. Are the docs/template command changes complete enough for public lockfile
   hygiene after the user-level uv mirror finding?
4. Does the plan avoid runtime feature creep and prohibited
   platform/source-acquisition functionality?
5. Are the verification and release-review gates sufficient before commit/push?

## Required Output

Respond with:

- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A concise verdict.

If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 32 CI RELEASE HYGIENE
```

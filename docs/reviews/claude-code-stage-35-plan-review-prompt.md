# Claude Code Stage 35 Plan Review Prompt

You are reviewing the Stage 35 public launch contact plan for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Make the repository's public security and conduct reporting paths actionable
before public GitHub launch, without changing runtime behavior.

## Proposed Technical Approach

- Because the repository may still be private, defer GitHub private
  vulnerability reporting enablement until after the private-repo commit is
  pushed and CI succeeds. Then switch the repository public, immediately enable
  PVR with the dedicated GitHub REST endpoint, and verify `{"enabled": true}`.
- Update `SECURITY.md` to point sensitive reports to the repository Security tab
  private vulnerability reporting path.
- Update `CODE_OF_CONDUCT.md` to point conduct reports to a dedicated GitHub
  conduct/moderation issue template.
- Add `.github/ISSUE_TEMPLATE/conduct_report.yml` with redaction warnings and
  no request for secrets, private security details, local databases, generated
  reports, or doxxing material.
- Add a complete wheel archive content assertion to CI after `uv build --out-dir
  "$tmp_build"` so CI verifies all required packaged templates/configs and
  matches `docs/github-upload-checklist.md`.
- Run pre-public diff and history secret scans before the visibility switch.
- If public visibility or PVR enablement fails after the visibility switch,
  immediately attempt to restore private visibility and block the stage.
- Keep Stage 35 docs/CI/settings-only: no runtime code, dependencies, `uv.lock`,
  source connectors, scraping/crawling/platform automation, watchers,
  schedulers, source acquisition, ranking, demand proof, platform coverage, or
  social-platform functionality.

## Files To Review

- `docs/superpowers/specs/2026-06-14-stage-35-public-launch-contact-design.md`
- `docs/superpowers/plans/2026-06-14-stage-35-public-launch-contact-plan.md`

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 35 PUBLIC LAUNCH CONTACT
```

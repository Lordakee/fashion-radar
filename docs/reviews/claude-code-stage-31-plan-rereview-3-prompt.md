# Claude Code Stage 31 Plan Rereview 3 Prompt

Review the final Stage 31 release-gate design/plan after incorporating
additional read-only audit findings.

Files:

- `docs/superpowers/specs/2026-06-13-stage-31-release-gate-design.md`
- `docs/superpowers/plans/2026-06-13-stage-31-release-gate-plan.md`

Changes since the prior approval:

- Added `/tmp` snapshot evidence for the pre-restore `uv.lock` diff.
- Kept the `.venv/bin/python` mirror-only `uv.lock` diff guard before
  `git restore uv.lock`.
- Expanded installed-wheel `community-handoff-workflow` smoke to assert emitted
  command strings and `--dry-run` placement, plus table output saying commands
  were not executed.
- Expanded public examples smoke to cover CSV and JSON lint/preview plus
  dry-run imports with no temp data files created.
- Added diff-scoped boundary scans.
- Expanded secret/artifact scans and added a staged-file allowlist check.
- Clarified that push is allowed in this current run because the user explicitly
  authorized it, and that future reuse still requires explicit push approval.

Please check:

1. No new Critical or Important issues.
2. The strengthened checks are executable and appropriate for this repo.
3. The plan still avoids runtime feature changes and any scraping/crawling/
   platform automation/source acquisition implications.
4. The push step is acceptable given current-thread explicit authorization and
   one-shot auth hygiene.

If acceptable, include exactly:

```text
APPROVED FOR STAGE 31 RELEASE GATE
```

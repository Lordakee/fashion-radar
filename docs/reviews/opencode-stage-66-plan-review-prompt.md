Review the Stage 66 external-tool-readiness spec and implementation plan in
/home/ubuntu/fashion-radar.

Focus on:
- whether `external-tool-readiness` should be `local_read_only` rather than
  `print_only` given that it checks `shutil.which`;
- whether the scope stays local-only and free-first;
- whether the plan conflicts with the existing external-tool adapter/template/
  workflow trio or the community-handoff-check-dir command;
- whether the planned tests and docs updates are sufficient and not overbroad;
- whether any missing boundary text or smoke assumptions would cause CI drift.

Files to review:
- `docs/superpowers/specs/2026-06-17-stage-66-external-tool-readiness-design.md`
- `docs/superpowers/plans/2026-06-17-stage-66-external-tool-readiness-plan.md`

Return only concrete Critical or Important findings, plus any test gaps that
would block execution.

Review the Stage 329 plan for /home/ubuntu/fashion-radar.

Files to review:
- docs/superpowers/specs/2026-07-07-stage-329-row-one-local-ops-check-design.md
- docs/superpowers/plans/2026-07-07-stage-329-row-one-local-ops-check-plan.md

Stage 329 objective:
- Add `row-one ops-check` as a read-only local ROW ONE ops diagnostic.
- Report site freshness, server/port readiness, access URLs, and user systemd unit-file presence.
- Keep `status`, `serve`, `install-local`, `local-ops`, generated site contracts, and schemas unchanged.

Hard boundaries:
- Do not start servers.
- Do not install, enable, reload, start, stop, restart, or kill systemd units.
- Do not call `systemctl`.
- Do not kill or alter any process occupying a port.
- Do not rebuild or refresh the ROW ONE site.
- Do not write files, generated artifacts, reports, service files, unit files, caches, lockfiles, or SQLite data.
- Do not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, generated site routes, source collection, fetching, extraction, scoring, ranking, LLM, connectors, deployment automation, market grouping, domestic/international classification, or compliance-review behavior.

Please verify Claude Code plan findings are addressed if this is used as a rereview, or provide initial plan findings if Claude Code is unavailable.

Return concise complete sections: Critical, Important, Medium, Minor, Verdict.
If there are no findings for a severity, write `None`.
Do not edit files.

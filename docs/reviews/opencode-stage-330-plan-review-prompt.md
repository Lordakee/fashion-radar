Review the Stage 330 plan for /home/ubuntu/fashion-radar.

Files to review:
- docs/superpowers/specs/2026-07-07-stage-330-row-one-refresh-data-retention-design.md
- docs/superpowers/plans/2026-07-07-stage-330-row-one-refresh-data-retention-plan.md

Objective:
- Add default 1-day SQLite data retention to `row-one refresh`.
- Reuse `clean_old_data()`.
- Add `--retention-days` and `--skip-data-retention`.
- Keep standalone `clean-old-data` unchanged and preserve ROW ONE contracts.

If used as fallback/rereview, verify Claude Code findings are addressed.
Otherwise provide initial plan findings.

Return concise complete sections: Critical, Important, Medium, Minor, Verdict.
If there are no findings for a severity, write `None`.
Do not edit files.

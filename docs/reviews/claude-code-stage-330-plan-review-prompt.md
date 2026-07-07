Review the Stage 330 plan for /home/ubuntu/fashion-radar.

Files to review:
- docs/superpowers/specs/2026-07-07-stage-330-row-one-refresh-data-retention-design.md
- docs/superpowers/plans/2026-07-07-stage-330-row-one-refresh-data-retention-plan.md
- src/fashion_radar/cli.py
- src/fashion_radar/workflows.py
- tests/test_row_one_cli.py
- tests/test_workflows.py
- docs/row-one.md
- docs/data-retention.md
- docs/first-run.md
- README.md

Stage 330 objective:
- Add default 1-day SQLite data retention to `row-one refresh` after successful ROW ONE site/report generation.
- Reuse existing `clean_old_data()`.
- Add `--retention-days` and `--skip-data-retention`.
- Keep standalone `clean-old-data` unchanged.

Hard boundaries:
- Do not change scoring, matching, source collection, extraction, generated site routes, app/runtime/manifest contracts, schemas, LLM, connectors, systemd enablement, local server behavior, or compliance-review behavior.
- Do not prune collector_runs, source_health, entity_first_seen, config files, generated site files, or non-SQLite data.
- Do not add dependencies.

Please review feasibility, default retention choice, command option design, sequencing after site generation, tests, docs, and risk to ROW ONE scoring/history.

Return concise complete sections: Critical, Important, Medium, Minor, Verdict.
If there are no findings for a severity, write `None`.
Do not edit files.

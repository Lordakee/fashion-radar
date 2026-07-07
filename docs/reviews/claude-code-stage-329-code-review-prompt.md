Review Stage 329 implementation for /home/ubuntu/fashion-radar.

Objective:
- Add `fashion-radar row-one ops-check` as a read-only local ROW ONE ops diagnostic.
- Report generated-site presence, runtime freshness, server/port readiness, access URLs, and user systemd unit-file presence.
- Keep ROW ONE generated contracts unchanged: row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1.

Plan/design:
- docs/superpowers/specs/2026-07-07-stage-329-row-one-local-ops-check-design.md
- docs/superpowers/plans/2026-07-07-stage-329-row-one-local-ops-check-plan.md
- docs/reviews/claude-code-stage-329-plan-review.md
- docs/reviews/claude-code-stage-329-plan-rereview.md

Implementation files:
- src/fashion_radar/row_one/ops_check.py
- src/fashion_radar/cli.py
- tests/test_row_one_ops_check.py
- tests/test_row_one_cli.py
- tests/test_row_one_docs.py
- tests/test_workflows.py
- README.md
- docs/row-one.md
- docs/cli-reference.md

Hard boundaries to verify:
- Does not start servers.
- Does not install, enable, reload, start, stop, restart, or kill systemd units.
- Does not call `systemctl`.
- Does not kill or alter any process occupying a port.
- Does not rebuild or refresh the ROW ONE site.
- Does not write files, generated artifacts, reports, service files, unit files, caches, lockfiles, or SQLite data.
- Does not change schemas, generated site routes, source collection, fetching, extraction, scoring, ranking, LLM, connectors, deployment automation, market grouping, domestic/international classification, or compliance-review behavior.
- Bind probing must not use `SO_REUSEADDR`; socket errors must not crash the diagnostic.
- Missing unit directories must be reported as missing without creating them.
- `--as-of` parsing must reject malformed input without running the diagnostic.

Targeted verification already run by Codex:
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_ops_check.py tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_workflows.py -q` -> 141 passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/ops_check.py src/fashion_radar/cli.py tests/test_row_one_ops_check.py tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_workflows.py` -> passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/ops_check.py src/fashion_radar/cli.py tests/test_row_one_ops_check.py tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_workflows.py` -> passed
- `git diff --check` -> passed

Please review the actual diff and code for correctness, plan compliance, safety, test quality, docs accuracy, and integration risk.

Return concise complete sections: Critical, Important, Medium, Minor, Verdict.
If there are no findings for a severity, write `None`.
Do not edit files.

You are reviewing Stage 308 code for the `fashion-radar` repo.

Repo: `/home/ubuntu/fashion-radar`
Plan: `docs/superpowers/plans/2026-07-05-stage-308-row-one-site-integrity-plan.md`
Plan review: `docs/reviews/claude-code-stage-308-plan-review.md`

Changed files to review:
- `src/fashion_radar/row_one/status_integrity.py` (new)
- `src/fashion_radar/cli.py`
- `tests/test_row_one_cli.py`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `README.md`
- `docs/row-one.md`
- `docs/cli-reference.md`
- `tests/test_row_one_docs.py`
- `reports/row-one/site/**` regenerated snapshot
- `docs/superpowers/plans/2026-07-05-stage-308-row-one-site-integrity-plan.md`
- `docs/reviews/claude-code-stage-308-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-308-plan-review.md`

Requirements:
- `row-one status` stays read-only. It may read generated files but must not rebuild, refresh, collect, write, deploy, or start a server.
- No schema/app contract change. `row-one-app/v7`, `row-one-manifest/v1`, and `row-one-runtime/v1` remain unchanged.
- No compliance-review product feature.
- The new integrity checks should catch generated file drift, missing current detail files, missing local assets, stale/mismatched article sidecars, unsafe local-intelligence links, missing local article anchors, noncanonical paragraph fragments, and route drift.
- The first-run smoke should exercise the documented `row-one status --json` script-facing preflight and then real local HTTP serving without flaky fixed ports or indefinite subprocess hangs.
- The regenerated ROW ONE site should be current enough for the new status preflight.

Verification already run successfully:
```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py tests/test_first_run_smoke.py tests/test_row_one_docs.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one status --site-dir reports/row-one/site --json
```

Please review for:
1. Correctness bugs or false positives/false negatives in `status_integrity.py`.
2. Flaky or hanging behavior in the first-run smoke changes.
3. Test coverage gaps for the requirements above.
4. Any accidental schema, generated contract, ranking/scoring, or compliance-feature drift.
5. Generated site snapshot consistency risks.

Return findings in this format:

## Verdict
Approve, Approve with Important fixes, or Reject.

## Critical Findings
- File/line reference, issue, why it matters, concrete fix.

## Important Findings
- File/line reference, issue, why it matters, concrete fix.

## Minor Findings
- File/line reference, issue, why it matters, concrete fix.

Do not modify files.

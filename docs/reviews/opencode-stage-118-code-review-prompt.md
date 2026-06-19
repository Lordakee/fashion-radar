Review the Stage 118 implementation in `/home/ubuntu/fashion-radar`.

Focus only on the current docs/test changes for agent UV run hygiene:

- `AGENTS.md`
- `README.md`
- `docs/dependency-mirrors.md`
- `docs/github-upload-checklist.md`
- `tests/test_cli_docs.py`

Also check the stage artifacts if useful:
- `docs/superpowers/specs/2026-06-20-stage-118-agent-uv-run-hygiene-design.md`
- `docs/superpowers/plans/2026-06-20-stage-118-agent-uv-run-hygiene-plan.md`
- `docs/reviews/opencode-stage-118-plan-review.md`
- `docs/reviews/opencode-stage-118-plan-rereview.md`

What to verify:
1. The docs clearly separate mirror-backed frozen local installs from
   no-config frozen agent-run verification.
2. All four scoped docs sections contain `uv --no-config run --frozen`,
   `agent-run verification`, `mirror-backed`, `uv.lock`, and
   `frozen mirror install`.
3. The new test in `tests/test_cli_docs.py` is section-scoped and uses existing
   path/helper conventions.
4. No `uv.lock`, `pyproject.toml`, runtime code, CI, dependency, connector,
   scraping, scheduling, monitoring, source acquisition, ranking, coverage
   verification, or compliance/audit product behavior changed.

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final statement on whether Stage 118 is ready to ship.

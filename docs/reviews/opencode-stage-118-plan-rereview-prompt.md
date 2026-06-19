Review the updated Stage 118 plan after the initial Important finding.

Repository: `/home/ubuntu/fashion-radar`

Files to review:
- `docs/superpowers/specs/2026-06-20-stage-118-agent-uv-run-hygiene-design.md`
- `docs/superpowers/plans/2026-06-20-stage-118-agent-uv-run-hygiene-plan.md`
- `docs/reviews/opencode-stage-118-plan-review.md`
- Current targets:
  - `AGENTS.md`
  - `README.md`
  - `docs/dependency-mirrors.md`
  - `docs/github-upload-checklist.md`
  - `tests/test_cli_docs.py`

Focus only on whether the updated plan resolves the prior Important finding:

- the planned test requires all four scoped sections to contain
  `uv --no-config run --frozen`, `agent-run verification`, `mirror-backed`,
  `uv.lock`, and `frozen mirror install`;
- the planned doc edits must explicitly add or preserve those strings in
  `AGENTS.md`, `README.md`, `docs/dependency-mirrors.md`, and
  `docs/github-upload-checklist.md`;
- the planned test should use existing constants where appropriate, including
  `AGENTS_DOC`.

Also verify that the stage remains docs/tests-only and does not introduce
runtime behavior, dependency or lockfile changes, CI changes, connectors,
scraping, scheduling, monitoring, source acquisition, ranking, coverage
verification, or compliance/audit product behavior.

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether any Critical or Important blockers remain
  before implementation.

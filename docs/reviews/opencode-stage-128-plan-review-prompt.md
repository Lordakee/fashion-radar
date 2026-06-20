Review the Stage 128 design and implementation plan before any code changes.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Align `docs/cli-reference.md` support sentences for
  `external-tool-workflow` and `external-tool-readiness` with actual command
  help.
- Keep the change docs/test-only.

Design:
- `docs/superpowers/specs/2026-06-20-stage-128-external-tool-cli-reference-option-parity-design.md`

Plan:
- `docs/superpowers/plans/2026-06-20-stage-128-external-tool-cli-reference-option-parity-plan.md`

Proposed implementation scope:
- `docs/cli-reference.md`
- `tests/test_cli_docs.py`
- Stage 128 review artifacts only

Review focus:
1. Does the design address the CLI reference option drift without changing
   runtime CLI behavior?
2. Is the planned RED test specific enough to parse only the relevant command
   bullets and avoid whole-file false positives?
3. Does the plan keep readiness wording accurate as local read-only and avoid
   implying directory inspection or file validation?
4. Does the scope avoid runtime CLI behavior, dependencies, lockfile,
   connectors, scraping, browser automation, platform API, monitoring,
   scheduling, source acquisition, demand proof, ranking, coverage
   verification, and compliance/audit product behavior?
5. Are the verification commands sufficient?

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before implementation.

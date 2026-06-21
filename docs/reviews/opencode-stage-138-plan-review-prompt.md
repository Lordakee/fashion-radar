Review the Stage 138 design and implementation plan before code changes.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Harden `external-tool-readiness` first-run smoke payload validation by
  exact-checking every readiness step command that is not currently covered.
- Reuse existing `shlex.split()` exact argv comparison.
- Keep this validation-only with no CLI runtime behavior changes.

Design:
- `docs/superpowers/specs/2026-06-21-stage-138-external-tool-readiness-step-argv-design.md`

Plan:
- `docs/superpowers/plans/2026-06-21-stage-138-external-tool-readiness-step-argv-plan.md`

Proposed implementation scope:
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- Stage 138 review artifacts only

Review focus:
1. Does the design correctly identify the five `external-tool-readiness`
   payload step commands that are currently not exact argv-checked?
2. Are the planned RED tests specific enough to prove the previous validator
   accepted command drift while names/effects and payload fields stayed valid?
3. Does the implementation plan reuse `validate_expected_external_tool_command`
   and its `shlex.split()` exact argv comparison rather than adding a second
   parser or substring checks?
4. Are expected argv values derived from `validate_external_tool_readiness()`
   payload fields (`adapter_id`, `directory`, `config_dir`, `data_dir`,
   `as_of`, `input_format`, `pattern`, `source_name`) instead of hardcoded
   first-run paths?
5. Does the plan preserve existing workflow and dry-run exact checks plus
   step-count, step-name, step-effect, checks, boundary, install-hint, and
   forbidden-scope validation?
6. Does the plan avoid CLI runtime behavior changes, generated command
   execution, PATH lookup changes, directory inspection, handoff file reads,
   import behavior changes, SQLite behavior changes, artifact creation,
   dependency changes, `uv.lock`, connectors, scraping, browser automation,
   platform APIs, account/session/cookie/token behavior, media downloads,
   monitoring, scheduling, source acquisition, demand proof, ranking, coverage
   verification, and compliance/audit product behavior?
7. Are the verification commands sufficient?

Return:
Start with `# Stage 138 Plan Review`, then include:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before implementation.

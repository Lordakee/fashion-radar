# Stage 193 Plan Review

Review target:

- `docs/superpowers/specs/2026-06-24-stage-193-trend-heat-explanation-sidecar-design.md`
- `docs/superpowers/plans/2026-06-24-stage-193-trend-heat-explanation-sidecar-plan.md`

Reviewer command:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "<review prompt>"
```

## Verdict

Not approved.

The plan's sidecar architecture is contract-safe and aligns with the existing
`heat-movers` precedent, but two Important issues must be fixed before
implementation.

## Critical

None.

## Important

1. The planned table GREEN test asserted a contiguous
   `no platform coverage verification` substring, but the planned renderer only
   emitted `no demand proof or platform coverage verification`. This would make
   the mandated GREEN gate fail even after implementation. The plan should add a
   dedicated `No platform coverage verification is performed.` table line and
   assert that exact line.

2. The planned rising/cooling explanation clauses said score and mention
   movement both increased or both decreased. Existing trend status logic allows
   rising/cooling when one dimension is flat and the other moves. The planned
   prose should use `score and/or mention movement` wording so the explanation
   matches the actual classifier.

## Minor

- The file manifest should list `tests/test_trend_explanations.py` as an added
  file, not a modified file.
- The new CLI command should avoid applying `limit` both inside
  `build_trend_comparison(...)` and inside `build_trend_explanations(...)`.
  The sidecar should own explanation truncation.
- A dedicated `TREND_EXPLANATION_FORMAT_OPTION` would better match the existing
  per-command option style.
- A parse-time test for negative `--limit` would cover the Typer guard.
- The docs test can require `needs review` in the user-facing narrative docs
  while keeping the boundary terms required across the full documentation set.

## Follow-Up

Fix the two Important findings and rerun a plan review before implementation.

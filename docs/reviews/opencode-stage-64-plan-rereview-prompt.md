Review only these two files in /home/ubuntu/fashion-radar:
- docs/superpowers/specs/2026-06-17-stage-64-external-tool-workflow-design.md
- docs/superpowers/plans/2026-06-17-stage-64-external-tool-workflow-plan.md

Context:
- This is Stage 64 for `fashion-radar`.
- The planned command is `fashion-radar external-tool-workflow`.
- It must be local, stdout-only, print-only workflow metadata.
- JSON output is workflow metadata, not importable handoff row JSON.
- It must not add connectors, scraping, browser automation, platform APIs,
  monitoring, scheduling, source acquisition, demand proof, ranking, coverage
  verification, SQLite access, generated command execution, directory reads, or
  a compliance-review product feature.
- `external-tool-template` remains responsible for importable CSV/JSON example
  handoff rows.

Check only for Critical or Important issues before coding:
1. Objective/scope mismatch.
2. A test or implementation instruction that is clearly impossible against the
   existing repo patterns.
3. Missing boundary coverage that could allow platform collection or side
   effects.
4. A JSON contract ambiguity that would likely break implementation or docs.

Return exactly:
- Verdict: APPROVED FOR STAGE 64 IMPLEMENTATION or CHANGES REQUIRED
- Critical:
- Important:
- Minor:
- Rationale:

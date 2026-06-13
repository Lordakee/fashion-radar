You are reviewing the Stage 27B docs plan before implementation.

Repository: `/home/ubuntu/fashion-radar`

Context:

- Stage 27A implemented `fashion-radar community-candidates` and Claude Code
  approved Stage 27A completion in
  `docs/reviews/claude-code-stage-27a-code-review.md`.
- Stage 27B is documentation only. It must not modify production code, tests,
  configs, dependencies, generated artifacts, or `uv.lock`.

Design and plan:

- `docs/superpowers/specs/2026-06-13-stage-27b-community-candidate-docs-design.md`
- `docs/superpowers/plans/2026-06-13-stage-27b-community-candidate-docs-plan.md`

Review focus:

1. Is the docs-only scope clear and tight enough?
2. Do the planned docs accurately describe `community-candidates` as one-file,
   local, read-only, pre-import, aggregate-only preview?
3. Do the planned docs avoid implying platform coverage, proof of demand,
   source quality/ranking, scraping, monitoring, acquisition, scheduling,
   dashboard updates, report generation, database import, or entity YAML
   generation?
4. Do the planned docs state that output does not include local file paths, row
   URLs, row titles, summaries, raw text, normalized keys, candidate contexts,
   or representative item details?
5. Are verification steps sufficient for a docs-only node?

Output format:

- List findings by severity: Critical, Important, Minor.
- Critical and Important findings block implementation and must be fixed before
  editing docs.
- If no blocking findings remain, include the exact phrase:
  `APPROVED FOR STAGE 27B DOCS`.

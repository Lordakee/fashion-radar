You are reviewing the Stage 29 docs-only plan before implementation.

Repository: `/home/ubuntu/fashion-radar`

Context:

- Stage 28 implemented and pushed `fashion-radar community-candidates-dir`.
- Stage 29 is documentation only. It must not modify production code, tests,
  configs, dependencies, generated artifacts, or `uv.lock`.

Design and plan:

- `docs/superpowers/specs/2026-06-13-stage-29-community-candidates-dir-docs-design.md`
- `docs/superpowers/plans/2026-06-13-stage-29-community-candidates-dir-docs-plan.md`

Review focus:

1. Is the docs-only scope clear and tight enough?
2. Do the planned docs accurately describe `community-candidates-dir` as local,
   read-only, non-recursive, pre-import, and aggregate-only?
3. Do the planned docs avoid implying platform coverage, proof of demand, source
   ranking, scraping, monitoring, source acquisition, scheduling, dashboard
   updates, report generation, database import, or entity YAML generation?
4. Do the planned docs state that output does not include supplied directory
   path, matched file paths, matched file names, row URLs, row titles, summaries,
   raw text, normalized keys, candidate contexts, raw validation findings, or
   representative item details?
5. Are verification steps sufficient for a docs-only node?

Output format:

- List findings by severity: Critical, Important, Minor.
- Critical and Important findings block implementation and must be fixed before
  editing docs.
- If no blocking findings remain, include the exact phrase:
  `APPROVED FOR STAGE 29 DOCS`.

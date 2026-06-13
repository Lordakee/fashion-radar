Rereview Stage 29 docs-only changes before commit and push.

Repository: `/home/ubuntu/fashion-radar`

Previous review:

`docs/reviews/claude-code-stage-29-docs-review.md` found one Important blocker:
the `community-candidates-dir` output-exclusion wording omitted
`account/private fields`.

Fix applied:

Added explicit `account/private fields` or equivalent `account/private field`
wording to the Stage 29 `community-candidates-dir` docs/checklists/design where
the output-exclusion lists appear:

- `README.md`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `docs/candidate-discovery.md`
- `docs/source-boundaries.md`
- `docs/github-upload-checklist.md`
- `docs/superpowers/specs/2026-06-13-stage-29-community-candidates-dir-docs-design.md`

Please rereview all Stage 29 docs-only changes, with focus on:

1. Confirm the previous Important blocker is resolved.
2. Confirm documentation still describes `community-candidates-dir` as local,
   read-only, non-recursive, pre-import, and aggregate-only.
3. Confirm documentation does not imply platform coverage, proof of demand,
   source ranking, source acquisition, acquisition workflows, source collection,
   source connectors, scraping, monitoring, watching, scheduling, database
   import, database writes/state, report writing/generation, dashboard
   updates/generation, or entity YAML/entity file generation.
4. Confirm output exclusions are explicit: no supplied directory path, matched
   file paths, matched file names, row URLs, row titles, summaries, raw text,
   normalized keys, candidate contexts, raw validation findings,
   account/private fields, or representative item details.
5. Confirm no code/test/config/dependency/`uv.lock` changes should be included
   in this Stage 29 docs-only commit.

Output format:

- List findings by severity: Critical, Important, Minor.
- Critical and Important findings block commit and push.
- If no blocking findings remain, include the exact phrase:
  `APPROVED FOR STAGE 29 DOCS COMMIT AND PUSH`.

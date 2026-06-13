Rereview Stage 29 docs-only staged commit before push.

Repository: `/home/ubuntu/fashion-radar`

Context:

- `docs/reviews/claude-code-stage-29-docs-review.md` found one Important
  blocker: `community-candidates-dir` output-exclusion wording omitted
  `account/private fields`.
- That wording was fixed in the primary Stage 29 docs/design/checklists.
- `docs/reviews/claude-code-stage-29-docs-rereview.md` then found:
  - Important: `uv.lock` is modified in the working tree.
  - Minor: the Stage 29 implementation plan snippets omitted
    `account/private fields`.
- `uv.lock` has a known pre-existing unstaged mirror diff and must remain
  excluded from the Stage 29 commit. Please review the staged diff, not the
  entire dirty working tree, for commit eligibility.
- The Stage 29 implementation plan snippets have now been updated to include
  `account/private fields` in the embedded exclusion lists.

Please review:

1. `git diff --cached --name-only` should show only Stage 29 docs/review files
   and must not include `uv.lock`, source files, tests, configs, or dependency
   files.
2. `git diff --cached -- uv.lock` should be empty.
3. The staged Stage 29 docs still describe `community-candidates-dir` as local,
   read-only, non-recursive, pre-import, and aggregate-only.
4. The staged Stage 29 docs do not imply platform coverage, proof of demand,
   source ranking, source acquisition, acquisition workflows, source collection,
   source connectors, scraping, monitoring, watching, scheduling, database
   import, database writes/state, report writing/generation, dashboard
   updates/generation, or entity YAML/entity file generation.
5. The staged Stage 29 docs preserve explicit output exclusions: no supplied
   directory path, matched file paths, matched file names, row URLs, row titles,
   summaries, raw text, normalized keys, candidate contexts, raw validation
   findings, account/private fields, or representative item details.

Output format:

- List findings by severity: Critical, Important, Minor.
- Critical and Important findings block commit and push.
- If no blocking findings remain, include the exact phrase:
  `APPROVED FOR STAGE 29 DOCS COMMIT AND PUSH`.

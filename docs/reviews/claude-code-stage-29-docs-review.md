## Critical

None.

## Important

1. **`community-candidates-dir` output-exclusion wording omits account/private fields.**

   The review request explicitly requires documentation to preserve this output exclusion list, including “account/private fields.” The new `community-candidates-dir` documentation consistently excludes:

   - supplied directory path
   - matched file paths
   - matched file names
   - row URLs
   - row titles
   - summaries
   - raw text
   - normalized keys
   - candidate contexts
   - raw validation findings
   - representative item details

   However, the new `community-candidates-dir` boundary text does **not** explicitly say the command output excludes account/private fields or account/private material.

   Examples checked:

   - `README.md:138-145`
   - `docs/community-signal-import.md:95-100`
   - `docs/community-signal-quality.md:97-102`
   - `docs/source-boundaries.md:72-78`
   - `docs/github-upload-checklist.md:48-52`
   - `docs/superpowers/specs/2026-06-13-stage-29-community-candidates-dir-docs-design.md:43-54`

   Existing docs do contain general community-import/private-data boundary language elsewhere, but the Stage 29 `community-candidates-dir` output-exclusion language itself does not explicitly preserve this required exclusion.

   **Blocker:** Add “account/private fields” or equivalent explicit wording to the `community-candidates-dir` output-exclusion prose/checklist/design where the rest of the exclusions are listed.

## Minor

1. **`uv.lock` is modified in the working tree but not staged.**

   Verification output showed:

   ```text
    M uv.lock
   ```

   `git diff --cached -- uv.lock` produced no output, so it does not appear staged. Source/test diffs also produced no output for the reviewed source/test paths.

   This does not appear to be part of the Stage 29 docs commit yet, but it should remain unstaged and excluded from any Stage 29 commit/push.

2. **Docs otherwise look aligned with the main command boundaries.**

   The reviewed Stage 29 docs describe `community-candidates-dir` as local, read-only, non-recursive, pre-import, and aggregate-only. They avoid implying platform coverage, proof of demand, source ranking, source acquisition, source connectors, scraping, monitoring, watching, scheduling, database import/write behavior, report/dashboard generation, or entity file generation, except as negative boundary language.

Because one Important blocker remains, I cannot approve the Stage 29 docs commit and push yet.

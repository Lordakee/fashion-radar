# Stage 168 Release Rereview Prompt

Review the Stage 168 release-readiness follow-up for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
Start the response exactly with:

# Stage 168 Release Rereview

Context:

- `docs/reviews/opencode-stage-168-release-review.md` found one Important
  issue: the release review artifact itself contained process chatter, causing
  `scripts/check_release_hygiene.py` to fail.
- The artifact has now been replaced with a clean review body that starts with
  `# Stage 168 Release Review`.
- The release review file permission has been normalized to 0644.
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
  now passes.

Stage objective:

Synchronize `docs/source-packs.md` with the checked-in public starter source
pack so the documentation names the actual 10 GDELT lanes and shows current
source-pack lint count output.

Changed files:

- `docs/source-packs.md`
- `tests/test_source_packs_docs.py`
- Stage 168 spec, plan, plan review, code review, release review, rereview
  prompt, and release review prompt artifacts.

Scope boundaries:

- Documentation and documentation-test drift guard only.
- No changes to `configs/source-packs/fashion-public.example.yaml`.
- No source-pack linter behavior changes.
- No CLI changes.
- No collector changes.
- No network availability probing.
- No Google News RSS, Google Trends, source acquisition expansion, scraping,
  browser automation, platform APIs, login, cookies, monitoring, scheduling,
  demand proof, ranking, coverage verification, or compliance-review product
  features.

Latest verification evidence:

- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
  - Result: Release hygiene checks passed.
- Prior release gate evidence from the cleaned release review:
  - full pytest: 1366 passed.
  - focused docs test: 3 passed.
  - first-run smoke passed.
  - ruff check and format passed.
  - `UV_NO_CONFIG=1 uv lock --check` passed.
  - `git diff --check` passed.
  - no `ghp_` token matches and no GitHub extraheader.

Rereview questions:

1. Is the prior Important finding fixed?
2. Are the release/review artifacts now clean enough to commit?
3. Does Stage 168 remain in scope and ready to commit and push?
4. Are there any remaining critical or important findings?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict

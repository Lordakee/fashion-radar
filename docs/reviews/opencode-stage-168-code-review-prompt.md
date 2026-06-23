# Stage 168 Code Review Prompt

Review the Stage 168 implementation for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
Start the response exactly with:

# Stage 168 Code Review

Objective:

Synchronize `docs/source-packs.md` with the checked-in public starter source
pack so the documentation names the actual 10 GDELT lanes and shows current
source-pack lint count output.

Changed files:

- `docs/source-packs.md`
  - Expands the example JSON `tag_counts` object to match current
    `source-pack-lint` output.
  - Replaces the stale four-theme GDELT list with all 10 exact current GDELT
    source names in YAML order and concise lane descriptions.
- `tests/test_source_packs_docs.py`
  - Reads `configs/source-packs/fashion-public.example.yaml`.
  - Verifies the docs GDELT section contains exactly the current backticked
    GDELT source names in pack order.
  - Parses the docs JSON example and compares stable count fields to
    `lint_source_pack(...)`.
- Stage 168 spec, plan, plan-review prompt, and plan-review artifacts.

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

Plan review history:

- `docs/reviews/opencode-stage-168-plan-review.md`
  - No critical findings.
  - No important findings.
  - Recommended two minor improvements: exact/no-extra GDELT lane guard and
    explicit `result.findings == []`; both were adopted.

RED/GREEN evidence:

- RED:
  - Temporarily stashed only `docs/source-packs.md` to run the new tests
    against the previous docs while keeping the new tests.
  - `uv --no-config run --frozen pytest tests/test_source_packs_docs.py -q`
  - Result: 2 failed, 1 passed. Failures were:
    - old GDELT bullets were not backticked current lane names;
    - old example `tag_counts` had only `industry_news` and `gdelt`, missing
      the full current public-pack tag count set.
- GREEN:
  - Same focused command after restoring the docs update.
  - Result: 3 passed.
- `uv --no-config run --frozen ruff check tests/test_source_packs_docs.py`
  - Result: All checks passed.
- `uv --no-config run --frozen ruff format --check tests/test_source_packs_docs.py`
  - Result: 1 file already formatted.
- `git diff --check`
  - Result: no output, exit 0.

Review questions:

1. Does the implementation meet the Stage 168 objective?
2. Are the tests strong enough to prevent the documented drift without being
   brittle?
3. Is the decision to compare stable linter fields and exclude absolute linter
   `path` output technically sound?
4. Did any runtime behavior, config, linter, collector, CLI, source acquisition,
   coverage verification, or social/platform behavior slip in?
5. Are there any critical or important findings before release verification?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict

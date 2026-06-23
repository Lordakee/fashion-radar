# Stage 175 Code Review Prompt

Review the Stage 175 implementation for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
This is a read-only review: do not edit files, do not run `git stash`, and do
not mutate the working tree. If you run verification, limit it to the focused
commands listed below and return one final review body.
Start the response exactly with:

# Stage 175 Code Review

Objective:

Keep `docs/entity-pack-quality.md` synchronized with the current
`entity-pack-lint` output for the checked-in starter watchlist pack, without
changing runtime lint behavior.

Changed files:

- `tests/test_entity_pack_quality_docs.py`
  - Adds fenced-block extraction helpers.
  - Adds a table sample parity test using the relative starter pack path.
  - Adds a JSON sample parity test that compares all stable count fields and a
    representative first finding to the current lint output.
- `docs/entity-pack-quality.md`
  - Marks the JSON example as an abbreviated representative excerpt.
  - Expands `tag_counts` and `category_tag_counts` to current lint output.
  - Replaces the sample finding with the current first lint finding.
- Stage 175 spec, plan, plan-review prompt, plan-review artifact, plan-rereview
  prompt, and plan-rereview artifact.

Scope boundaries:

- Docs/test-only.
- No changes to `src/fashion_radar/entity_packs.py`.
- No changes to `src/fashion_radar/cli.py`.
- No changes to entity pack YAML config.
- No changes to matcher behavior, scoring behavior, runtime lint payload shape,
  renderer behavior, CLI exit behavior, install hints, mirror hints, dependency
  manifests, or `uv.lock`.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, monitoring, scheduling, demand proof, ranking, coverage verification, or
  compliance-review product feature.

Review history:

- `docs/reviews/opencode-stage-175-plan-review.md`
  - One important finding: the initial table parity test used an absolute path,
    which would have made the rendered first line disagree with the documented
    relative-path sample.
  - Two minor findings: helper signature alignment and RED-step clarity.
- `docs/reviews/opencode-stage-175-plan-rereview.md`
  - No critical or important findings remain.
  - The absolute-path issue and minor alignment issues were fixed.

Verification evidence:

- RED:
  - `uv --no-config run --frozen pytest tests/test_entity_pack_quality_docs.py::test_entity_pack_quality_json_sample_matches_watchlist_lint_counts -q`
  - Result before docs updates: failed on abbreviated `tag_counts`.
- RED:
  - `uv --no-config run --frozen pytest tests/test_entity_pack_quality_docs.py -q`
  - Result before docs updates: 3 passed, 1 failed on the JSON parity test.
- GREEN:
  - `uv --no-config run --frozen pytest tests/test_entity_pack_quality_docs.py::test_entity_pack_quality_json_sample_matches_watchlist_lint_counts -q`
  - Result after docs updates: 1 passed.
- GREEN:
  - `uv --no-config run --frozen pytest tests/test_entity_pack_quality_docs.py -q`
  - Result after docs updates: 4 passed.
- GREEN:
  - `uv --no-config run --frozen pytest tests/test_entity_pack_lint.py tests/test_entity_pack_quality_docs.py -q`
  - Result: 28 passed.
- GREEN:
  - `uv --no-config run --frozen ruff check tests/test_entity_pack_quality_docs.py`
  - Result: All checks passed.
- GREEN:
  - `uv --no-config run --frozen ruff format --check tests/test_entity_pack_quality_docs.py`
  - Result: 1 file already formatted.

Review questions:

1. Does the implementation meet the Stage 175 objective?
2. Does the table parity test correctly use the relative starter pack path and
   stay aligned with the documented CLI example?
3. Does the JSON sample guard pin the right stable fields without overfitting to
   a full findings dump?
4. Did any out-of-scope runtime, matcher, scoring, CLI, payload, install-hint,
   mirror-hint, dependency, or lockfile behavior slip in?
5. Are there any critical or important findings before release verification?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict

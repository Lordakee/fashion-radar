# Stage 175 Release Review Prompt

Review the Stage 175 release readiness for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
This is a read-only review: do not edit files, do not run `git stash`, and do
not mutate the working tree. If you run verification, limit it to confirming the
evidence below and return one final review body.
Start the response exactly with:

# Stage 175 Release Review

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
  prompt, plan-rereview artifact, code review prompt, and code review artifact.

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
- `docs/reviews/opencode-stage-175-code-review.md`
  - No critical or important findings.
  - Minor notes only: exact marker coupling, `Any` annotation, and table prefix
    comparison are all intentional.

Focused verification evidence:

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
  - `env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q`
  - Result: 1372 passed.
- GREEN:
  - `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
  - Result: First-run sample smoke passed.
- GREEN:
  - `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
  - Result: Release hygiene checks passed.
- GREEN:
  - `uv --no-config run --frozen ruff check tests/test_entity_pack_quality_docs.py`
  - Result: All checks passed.
- GREEN:
  - `uv --no-config run --frozen ruff format --check tests/test_entity_pack_quality_docs.py`
  - Result: 1 file already formatted.
- GREEN:
  - `uv --no-config run --frozen ruff check .`
  - Result: All checks passed.
- GREEN:
  - `uv --no-config run --frozen ruff format --check .`
  - Result: 144 files already formatted.
- GREEN:
  - `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check`
  - Result: Resolved 84 packages.
- GREEN:
  - `git diff --check`
  - Result: no output, exit 0.
- GREEN:
  - `rg -n 'ghp_[A-Za-z0-9]+' .`
  - Result: no matches, exit 1.
- GREEN:
  - `git config --get-all http.https://github.com/.extraheader`
  - Result: no configured GitHub extraheader, exit 1.

Release review questions:

1. Is Stage 175 in scope and ready to commit?
2. Are the plan/code review artifacts clean and consistent with
   `docs/REVIEW_PROTOCOL.md`?
3. Is the release verification evidence sufficient for this docs/test-only
   stage?
4. Did any out-of-scope runtime, matcher, scoring, CLI, payload, install-hint,
   mirror-hint, dependency, or lockfile behavior slip in?
5. Are there any critical or important findings before commit and push?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict

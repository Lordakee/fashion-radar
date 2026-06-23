# Stage 176 Release Review Prompt

Review the Stage 176 release readiness for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
This is a read-only review: do not edit files, do not run `git stash`, and do
not mutate the working tree. If you run verification, limit it to confirming the
evidence below and return one final review body.
Start the response exactly with:

# Stage 176 Release Review

Objective:

Keep `docs/source-pack-quality.md` synchronized with the current
`source-pack-lint` output for the checked-in public source pack, without
changing runtime lint behavior.

Changed files:

- `tests/test_source_pack_quality_docs.py`
  - Adds fenced-block extraction helpers.
  - Adds a table sample parity test using the relative public pack path.
  - Adds a JSON sample parity test that compares the stable count fields and
    empty findings list to current lint output.
- `docs/source-pack-quality.md`
  - Expands `tag_counts` to current lint output.
  - Replaces the synthetic warning finding with `findings: []`.
- Stage 176 spec, plan, plan-review prompt, plan-review artifact, code review
  prompt, and code review artifact.

Scope boundaries:

- Docs/test-only.
- No changes to `src/fashion_radar/source_packs.py`.
- No changes to `src/fashion_radar/cli.py`.
- No changes to source pack YAML config.
- No changes to collector behavior, runtime lint payload shape, renderer
  behavior, CLI exit behavior, install hints, mirror hints, dependency
  manifests, or `uv.lock`.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, monitoring, scheduling, demand proof, ranking, coverage verification, or
  compliance-review product feature.

Review history:

- `docs/reviews/opencode-stage-176-plan-review.md`
  - No critical or important findings.
  - Minor notes only: task title wording, hard-coded markers, and preserving the
    illustrative finding row.
- `docs/reviews/opencode-stage-176-code-review.md`
  - No critical or important findings.
  - Minor notes only: relative-path handling and stable-field tradeoffs.

Focused verification evidence:

- RED:
  - `uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py::test_source_pack_quality_json_sample_matches_public_pack_lint_output -q`
  - Result before docs updates: failed on abbreviated `tag_counts`.
- RED:
  - `uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py -q`
  - Result before docs updates: 4 passed, 1 failed on the JSON parity test.
- GREEN:
  - `uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py::test_source_pack_quality_json_sample_matches_public_pack_lint_output -q`
  - Result after docs updates: 1 passed.
- GREEN:
  - `uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py -q`
  - Result after docs updates: 5 passed.
- GREEN:
  - `uv --no-config run --frozen pytest tests/test_source_packs.py tests/test_source_pack_quality_docs.py -q`
  - Result: 19 passed.
- GREEN:
  - `env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q`
  - Result: 1374 passed.
- GREEN:
  - `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
  - Result: First-run sample smoke passed.
- GREEN:
  - `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
  - Result: Release hygiene checks passed.
- GREEN:
  - `uv --no-config run --frozen ruff check tests/test_source_pack_quality_docs.py`
  - Result: All checks passed.
- GREEN:
  - `uv --no-config run --frozen ruff format --check tests/test_source_pack_quality_docs.py`
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

1. Is Stage 176 in scope and ready to commit?
2. Are the plan/code review artifacts clean and consistent with
   `docs/REVIEW_PROTOCOL.md`?
3. Is the release verification evidence sufficient for this docs/test-only
   stage?
4. Did any out-of-scope runtime, collector, scoring, CLI, payload, install-hint,
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

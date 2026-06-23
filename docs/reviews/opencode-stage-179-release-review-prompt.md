# Stage 179 Release Review Prompt

Review the Stage 179 release readiness for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
This is a read-only review: do not edit files, do not run `git stash`, and do
not mutate the working tree. If you run verification, limit it to confirming the
evidence below and return one final review body.
Start the response exactly with:

# Stage 179 Release Review

Objective:

Add a focused regression guard that ensures the documented source-pack quality
JSON sample exposes the same top-level keys as the runtime
`SourcePackLintResult` payload.

Changed files:

- `tests/test_source_pack_quality_docs.py`
  - Adds `runtime_payload = result.model_dump(mode="json")`.
  - Adds `assert set(payload) == set(runtime_payload)` before the existing
    value-level assertions.
- Stage 179 spec, plan, plan-review prompt, plan-review artifact, code-review
  prompt, and code-review artifact.

Scope boundaries:

- Test-only hardening.
- No runtime behavior changes.
- No docs content changes.
- No source acquisition, collector/source config changes, availability checks,
  demand proof, ranking, coverage verification features, compliance-review
  product features, dependency changes, or `uv.lock` changes.

Review history:

- `docs/reviews/opencode-stage-179-plan-review.md`
  - No critical or important findings.
  - Minor notes only: key-set assertion placement is acceptable, `mode="json"`
    is semantically faithful even though top-level keys match plain
    `model_dump()`, and `extra="forbid"` makes the runtime key set stable.
- `docs/reviews/opencode-stage-179-code-review.md`
  - No critical or important findings.
  - Minor notes only: ordering before value assertions is fine, and
    `mode="json"` is harmless for top-level key comparison.

Focused verification evidence:

- Baseline GREEN:
  - `uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py::test_source_pack_quality_json_sample_matches_public_pack_lint_output -q`
  - Result before adding guard: 1 passed.
- GREEN:
  - `uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py::test_source_pack_quality_json_sample_matches_public_pack_lint_output -q`
  - Result after adding guard: 1 passed.
- GREEN:
  - `uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py -q`
  - Result: 5 passed.
- GREEN:
  - `uv --no-config run --frozen ruff check tests/test_source_pack_quality_docs.py`
  - Result: All checks passed.
- GREEN:
  - `uv --no-config run --frozen ruff format --check tests/test_source_pack_quality_docs.py`
  - Result: 1 file already formatted.

Release gate evidence:

- `env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q`
  - Result: 1376 passed.
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
  - Result: First-run sample smoke passed.
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
  - Result: Release hygiene checks passed.
- `uv --no-config run --frozen ruff check .`
  - Result: All checks passed.
- `uv --no-config run --frozen ruff format --check .`
  - Result: 144 files already formatted.
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check`
  - Result: Resolved 84 packages.
- `git diff --check`
  - Result: no output, exit 0.
- `rg -n 'ghp_[A-Za-z0-9]+' .`
  - Result: no matches, exit 1.
- `git config --get-all http.https://github.com/.extraheader`
  - Result: no configured GitHub extraheader, exit 1.
- Review artifact hygiene with the project helper script:
  - Result: no process output, ANSI escapes, capture markers, or tool messages
    in Stage 179 review artifacts.

Release review questions:

1. Is Stage 179 in scope and ready to commit?
2. Are the plan/code review artifacts clean and consistent with
   `docs/REVIEW_PROTOCOL.md`?
3. Is the release verification evidence sufficient for this test-only stage?
4. Did any out-of-scope runtime, docs, source acquisition, source config,
   availability, demand proof, ranking, coverage-verification feature,
   compliance-review product feature, dependency, or lockfile behavior slip in?
5. Are there any critical or important findings before commit and push?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict

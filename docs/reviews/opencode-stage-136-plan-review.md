# Stage 136 Plan Review

I have read the design, plan, existing checker, and existing tests. Below are my findings against the seven review focuses.

## Critical Findings

None.

## Important Findings

None. The design and plan correctly address all seven review focuses:

1. **Outer filename parity + sdist root masking gap, no wheel tag parsing.** The design derives `<normalized-name>-<version>-py3-none-any.whl`, `<normalized-name>-<version>.tar.gz`, and `<normalized-name>-<version>` sdist root from `ExpectedProjectMetadata`. Scope explicitly excludes wheel tag parsing and platform wheels. The `py3-none-any` pin matches the project's current pure-Python wheel output.
2. **RED tests are specific enough.** `test_rejects_package_archives_with_mismatched_filenames` covers wheel-name drift (`wrong_name-0.1.0-...`), wheel-version drift (`fashion_radar-9.9.9-...`), sdist-name drift, and sdist-version drift (4 cases). `test_rejects_sdist_with_mismatched_root_directory` covers root-name and root-version drift. All fixtures reuse the default valid `WHEEL_FILES`/`SDIST_FILES`, so contents are otherwise valid. I verified the current checker accepts all six cases, so they are genuinely RED.
3. **Derivation from `ExpectedProjectMetadata` + existing helper.** `expected_archive_base_name()` reuses `normalize_distribution_name()` from Stage 134 and `expected_metadata.name`/`.version`; the other three helpers compose from it. The refactor of `expected_wheel_dist_info_dir()` to reuse the same base is output-preserving.
4. **Missing/multiple archive behavior preserved.** Task 2 Step 4 places `filename_errors` strictly after the `wheel_path is None or sdist_path is None` guard and after `select_single_archive` errors short-circuit. Existing `missing wheel archive (*.whl)` / `expected exactly one ...` messages are unchanged.
5. **Root validation before normalization.** Task 2 Step 5 calls `validate_sdist_root_dir(raw_paths, expected_metadata)` inside the `tarfile.open` block before `normalize_sdist_paths(raw_paths)`, operating on raw member names. I traced the `wrong_name-0.1.0` root case: root validation emits the mismatch and `normalize_sdist_paths` then strips the wrong root, so required-file checks pass and the test's `assert "sdist archive missing required file" not in result.stderr` holds.
6. **Scope boundaries respected.** No wheel tag parsing, no `.dist-info` path/required-file changes, no license/forbidden-member changes, no `pyproject.toml`/`uv.lock`/CI/dependency changes, no runtime product behavior, and no connector/scrape/platform-API/monitoring/scheduling/source-acquisition/demand-proof/ranking/coverage/compliance behavior. Also consistent with the AGENTS.md external-tool / community-handoff boundaries (none touched).
7. **Verification sufficient.** Focused `-k "filename or sdist_root or dist_info"` pytest, full `test_package_archives.py` + `test_package_metadata.py` pytest, ruff check + format, live `uv build` + checker run, `git diff --check`, plus the full release gate including `UV_NO_CONFIG=1 uv lock --check`, `git diff --exit-code -- uv.lock`, and the GitHub token / auth-header leakage guards.

## Minor Findings

1. **No RED test for the multi-root case.** `validate_sdist_root_dir` has two branches (wrong single root vs `len(roots) != 1`), but the plan only parametrizes the single-wrong-root branch. Consider adding one fixture where sdist members are split across two roots (e.g. half under `fashion_radar-0.1.0/`, half under `other-0.1.0/`) to prove the "found X, Y" / `or "none"` branch is exercised. Non-blocking; the single-root cases are the primary threat model.
2. **Stray top-level member edge case.** `roots = {path.split("/", 1)[0] for path in cleaned_paths if "/" in path}` ignores members with no `/`. If an sdist mixed root-prefixed files with a top-level stray file, root validation would pass and `normalize_sdist_paths` would fall back to unstripped paths, causing a downstream "missing required file" error rather than a root error. This still rejects the archive (just with a noisier message) and is outside the Stage 134/136 threat model (wrong root/name), so non-blocking. Worth a one-line note in the design's Risks section if you want to be explicit.
3. **Refactor note for `expected_wheel_dist_info_dir`.** The plan shows rewriting it to delegate to `expected_archive_base_name`. Behavior is identical, but because the existing `test_rejects_wheel_with_mismatched_dist_info_directory` test only checks the error string (not the helper directly), this is safe. No action needed; flagging only so the implementer knows the refactor is intentional and covered.

## Final Statement

There are **no Critical or Important blockers** before implementation. The plan may proceed. The minor findings are optional hardening/coverage notes and do not block the stage.

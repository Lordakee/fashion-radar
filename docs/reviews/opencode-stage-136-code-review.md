# Stage 136 Code Review

I read the Stage 136 design, plan, plan review, the diffed implementation in `scripts/check_package_archives.py`, the test changes in `tests/test_package_archives.py`, and confirmed the verification commands. I also stashed the checker change to confirm the new tests are genuinely RED against the prior (HEAD) checker, then restored and re-ran the full suite.

## Critical Findings

None.

## Important Findings

None. All six review focuses are satisfied:

1. **Implementation matches design and plan.** All promised helpers exist and compose as designed: `expected_archive_base_name()` (`scripts/check_package_archives.py:297`), `expected_wheel_archive_name()` (`:302`), `expected_sdist_archive_name()` (`:306`), `expected_sdist_root_dir()` (`:310`), `validate_archive_filename()` (`:318`), `validate_sdist_root_dir()` (`:416`). `validate_build_dir()` threads `filename_errors` (`:196`) and `validate_sdist()` takes `expected_metadata` and computes `root_errors` before `normalize_sdist_paths()` (`:398-399`). The refactor of `expected_wheel_dist_info_dir()` to delegate to `expected_archive_base_name()` (`:314`) is output-preserving — the existing `test_rejects_wheel_with_mismatched_dist_info_directory` still passes.

2. **RED tests are genuinely RED.** I stashed only `scripts/check_package_archives.py` and ran both new tests against the HEAD checker: all 6 cases failed with `returncode == 0`, i.e., the prior checker accepted every wrong wheel filename, wrong sdist filename, and wrong sdist root when contents were otherwise valid. After restoring, all 6 pass. The fixtures reuse the default `WHEEL_FILES`/`SDIST_FILES`, so archive contents are otherwise valid.

3. **Derivation is correct.** All four expected names (`expected_wheel_archive_name`, `expected_sdist_archive_name`, `expected_sdist_root_dir`, `expected_wheel_dist_info_dir`) compose from `expected_archive_base_name()`, which calls `normalize_distribution_name(expected_metadata.name)` and combines with `expected_metadata.version` (`:297-315`).

4. **Missing/multiple archive short-circuit preserved.** `validate_build_dir()` runs `select_single_archive()` first and returns on errors before reaching the `wheel_path is None or sdist_path is None` guard (`:187-194`), which itself runs before `validate_archive_filename()` (`:196`). `select_single_archive()` and its `missing {label} archive ({pattern})` / `expected exactly one ...` messages are unchanged. `test_rejects_build_directory_without_wheel` and `test_rejects_build_directory_without_sdist` still pass.

5. **Sdist root validation is raw and pre-normalization.** `validate_sdist()` passes `raw_paths` to `validate_sdist_root_dir()` before calling `normalize_sdist_paths()` (`:398-399`). For the single-wrong-root threat model, I verified directly that root validation emits exactly one mismatch and `normalize_sdist_paths()` then strips the wrong root, so `missing_required_paths` returns `[]` — the test's `assert "sdist archive missing required file" not in result.stderr` holds cleanly.

6. **Scope boundaries respected.** Diff is limited to `scripts/check_package_archives.py` + `tests/test_package_archives.py` plus Stage 136 docs/review artifacts. `pyproject.toml` and `uv.lock` are untouched (`git diff --exit-code` clean). No wheel-tag parsing (filename is pinned to `py3-none-any`), no `.dist-info`/required-member/license/forbidden-member/build-backend/dependency/runtime/connector/scrape/platform-API/monitoring/scheduling/source-acquisition/demand-proof/ranking/coverage/compliance behavior changes. AGENTS.md external-tool / community-handoff / heat-movers boundaries untouched.

## Minor Findings

1. **Root validation emits a spurious line for the existing unsafe-member-path tests.** `validate_sdist_root_dir()` operates on every cleaned member including unsafe strays. When the existing `test_rejects_sdist_with_unsafe_archive_member_path` fixtures run (correct root plus a stray like `/absolute.txt` or `../outside.txt`), the stray's first segment (`""` or `..`) differs from the expected root, so the checker now emits an extra `sdist archive root directory mismatch: expected fashion_radar-0.1.0, found , fashion_radar-0.1.0` line alongside the unsafe-member error. I verified this directly. The existing tests still pass (they use `in` assertions) and the archive is still rejected, so this is an error-clarity regression rather than a correctness issue. Note: the plan's pseudocode filter `if "/" in path` would not have avoided this, since paths like `/absolute.txt` and `../outside.txt` still contain `/`. A cleaner fix would be to skip root validation when `unsafe_errors` is non-empty, or to compute roots only from safe paths. Non-blocking.

2. **Implementation deviates from plan pseudocode.** `validate_sdist_root_dir()` drops the `if "/" in path` filter from the `roots` comprehension and adds an `if not cleaned_paths: return []` short-circuit (`:422-425`). The behavior change is conservative (a top-level stray file now contributes its own name as a root, making multi-root detection stricter), and both formulations still satisfy the design intent. Worth flagging only so the deviation is intentional. Non-blocking.

3. **Carry-forward from plan review: no RED test for the multi-root branch.** The `len(roots) != 1` branch (`:426`) is not exercised by an explicit RED test. I verified a multi-root sdist produces both the root-mismatch line and a long list of `sdist archive missing required file: ...` noise (because `normalize_sdist_paths()` falls back to unstripped paths). This is a pre-existing characteristic acknowledged in the plan review and outside the Stage 136 single-wrong-root threat model, but a one-line note in the design's Risks section would make the noise trade-off explicit. Non-blocking.

## Verification

I re-ran the focused and full suites and they agree with the reported results:
- `pytest tests/test_package_archives.py::test_rejects_package_archives_with_mismatched_filenames tests/test_package_archives.py::test_rejects_sdist_with_mismatched_root_directory -q` → 6 passed (and 6 failed when run against the stashed HEAD checker, proving RED).
- `pytest tests/test_package_archives.py tests/test_package_metadata.py -q` → 72 passed.
- `ruff check` and `ruff format --check` on the two files → clean.
- Live `uv build` + `python scripts/check_package_archives.py "$tmp_build"` → exit 0, `Package archives contain required files.`
- `git diff --check` → clean.
- `git diff --exit-code -- pyproject.toml uv.lock` → clean.

## Final Statement

There are **no Critical or Important blockers** before release. The minor findings are error-message clarity and coverage notes that do not affect correctness, scope, or the stage's threat model.

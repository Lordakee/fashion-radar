# Stage 180 Release Review

## Summary

Stage 180 is a strictly test-only hardening stage that closes the Stage 163
combined-coverage follow-up by adding a single regression test proving the
package archive checker reports both `METADATA is not valid UTF-8` and
`entry_points.txt is not valid UTF-8` when one wheel carries invalid bytes in
both `.dist-info` text members. The diff is confined to
`tests/test_package_archives.py` (+22 lines, appended as the final test),
`scripts/check_package_archives.py` is untouched, and no other tracked source,
metadata, lockfile, sdist, required-member, or forbidden-member behavior
changed. The test passes deterministically against the current runtime because
`validate_wheel(...)` calls `validate_wheel_metadata(...)` and
`validate_wheel_entry_points(...)` independently when both members are present
(`scripts/check_package_archives.py:267-274`), each catches
`UnicodeDecodeError` and returns its single stable message
(`:362-365` and `:381-384`), and both lists extend one shared `errors` list
printed line-by-line via `main(...)` (`:175-176`). All focused and release-gate
verification evidence reproduces fresh. No critical or important findings.

## Findings

### Critical

None.

### Important

None.

### Minor

1. The new test uses exact-line stderr membership
   (`stderr_lines = result.stderr.splitlines()` then
   `assert "..." in stderr_lines`), which is slightly inconsistent with the
   two sibling tests at `tests/test_package_archives.py:1057` and `:1161`,
   which use substring membership (`assert "..." in result.stderr`). The
   exact-line form is valid here and is arguably stricter: each error is
   emitted via `print(error, file=sys.stderr)`
   (`scripts/check_package_archives.py:175-176`), so each stable message is
   guaranteed to be a whole stderr line. This was already raised and accepted
   as optional in both the Stage 180 plan and code reviews; no change
   required.

2. The test does not assert the relative order of the two error lines. Order is
   deterministic (METADATA errors append before entry_points errors in
   `validate_wheel(...)`, `:267-274`), but order-agnostic assertions match the
   stated objective, which is aggregation presence, not ordering. Reasonable
   design choice; no change required.

3. Fixture bytes `b"\xff\xfe\xfa"` are genuinely invalid UTF-8 (`\xff` is never
   a valid lead byte), so `read_zip_text(...)` reliably raises
   `UnicodeDecodeError` and the decode is genuinely reached (both members are
   present, only their contents are swapped, so the presence guards at `:267`
   and `:271` pass). The `\xff\xfe`-prefixed bytes resemble a UTF-16-LE BOM, a
   sensible adversarial choice. Observation only; the fixture is correct.

## Verification Assessment

1. Is Stage 180 in scope and ready to commit? Yes. The only modified tracked
   file is `tests/test_package_archives.py` (+22 lines, verified via
   `git diff --stat`); all other Stage 180 entries are new untracked
   spec/plan/review artifacts. `scripts/check_package_archives.py` is
   unchanged, `uv.lock` is unchanged (not in the modified set), and the change
   is purely additive at the end of the test module.

2. Are the plan/code review artifacts clean and consistent with
   `docs/REVIEW_PROTOCOL.md`? Yes. Both
   `docs/reviews/opencode-stage-180-plan-review.md` and
   `docs/reviews/opencode-stage-180-code-review.md` follow the required
   structure (Summary, Findings with Critical/Important/Minor, Verification,
   Verdict), each carries exactly one verdict, and the hygiene scan found no
   write-status lines, no ANSI escapes, no capture markers, no code
   fences, no truncation, and no duplicate drafts. The prompts
   (`opencode-stage-180-plan-review-prompt.md`,
   `opencode-stage-180-code-review-prompt.md`,
   `opencode-stage-180-release-review-prompt.md`) and the spec/plan under
   `docs/superpowers/` are all present.

3. Is the release verification evidence sufficient for this test-only stage?
   Yes. All evidence reproduced fresh in this review:
   - New test alone: 1 passed.
   - Three invalid-UTF-8 tests together: `3 passed`.
   - Full module: `75 passed`.
   - `ruff check tests/test_package_archives.py`: `All checks passed!`.
   - `ruff format --check tests/test_package_archives.py`:
     `1 file already formatted`.
   - Release gate: `1377 passed`.
   - `check_first_run_smoke.py`: `First-run sample smoke passed.`.
   - `check_release_hygiene.py`: `Release hygiene checks passed.`.
   - `ruff check .`: `All checks passed!`; `ruff format --check .`:
     `144 files already formatted`.
   - `UV_NO_CONFIG=1 uv lock --check`: `Resolved 84 packages` (unchanged).
   - `git diff --check`: clean, exit 0.
   - Secret scan `rg -n 'ghp_[A-Za-z0-9]+' .`: no matches, exit 1.
   - `git config --get-all http.https://github.com/.extraheader`: none
     configured, exit 1.

4. Did any out-of-scope runtime, archive metadata, required-member,
   forbidden-member, sdist, dependency, lockfile, source-acquisition, ranking,
   coverage-verification, or compliance-review product behavior slip in? No.
   The runtime checker is byte-for-byte unchanged; the test only constructs
   fixtures and asserts on aggregated stderr. No connector, scraping, browser
   automation, platform API, login/cookie/token, monitoring, scheduling,
   demand-proof, ranking, coverage-verification, or compliance-review product
   behavior was introduced. The `heat-movers` and community-handoff
   boundaries are untouched.

5. Are there any critical or important findings before commit and push? No.

## Verdict

Approve. Stage 180 matches the approved plan verbatim, the new test
deterministically proves both invalid UTF-8 validators run and their friendly
errors aggregate into one stderr stream without a traceback, the change is
strictly additive and confined to `tests/test_package_archives.py`, the
plan/code review artifacts are clean and follow `docs/REVIEW_PROTOCOL.md`, all
focused and release-gate evidence reproduces fresh (1377 passed, hygiene and
smoke clean, lockfile unchanged, no secrets), and every scope boundary is
respected. No critical or important findings; the three minor notes are
observational and do not block release. Proceed to commit and push.

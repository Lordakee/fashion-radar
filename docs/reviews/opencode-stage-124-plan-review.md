# Stage 124 Plan Review

## Critical findings
None.

## Important findings
None.

## Minor findings

1. **Noisy sdist RED/GREEN output (cosmetic, not a correctness issue).**
   `write_sdist_with_raw_member` writes the unsafe member *without* the `fashion_radar-0.1.0/` root, so for 5 of 7 sdist cases (`../outside.txt`, `/absolute.txt`, `C:/outside.txt`, `C:outside.txt`, `//server/share/outside.txt`) `normalize_sdist_paths` sees multiple roots and returns the un-stripped set, which additionally triggers `sdist archive missing required file: ...` lines. The tests still go RED (the `unsafe archive member path` substring is absent today) and still go GREEN after implementation (asserts use `in`, and the design explicitly accepts multiple errors at `design.md:92-94`). Purely cosmetic; the two `..` cases that keep the root prefix are clean.

2. **`unsafe_archive_member_errors` does not deduplicate.**
   It iterates the raw list (before `clean_archive_paths` turns it into a set), so a repeated unsafe member yields repeated error lines. This matches the "report all problems" style and is harmless for a release gate, but is slightly inconsistent with the set-based dedup used elsewhere. No test exercises duplicates.

3. **No explicit task step creates the plan-review artifacts.**
   The Files section (`plan.md:22-23`) and Task 4 Step 3 `git add` reference `opencode-stage-124-plan-review-prompt.md` / `opencode-stage-124-plan-review.md`, but no Task creates them. This is expected — per `REVIEW_PROTOCOL.md:6-12` the plan review is produced at the pre-coding gate, outside the plan itself — but a one-line note pointing to that gate would make the artifact provenance explicit.

4. **Helper ordering.**
   The plan places `unsafe_archive_member_errors` / `is_unsafe_archive_path` *before* `clean_archive_paths` (`plan.md:210`), even though the former calls `clean_archive_path`. Functionally fine (module-level resolution at call time) and `re` is already imported (`check_package_archives.py:5`); only a readability nit.

## Review-focus answers

1. **Addresses blind spot without runtime change?** Yes — only `scripts/check_package_archives.py` (a release-gate checker) and its tests change; scope explicitly excludes runtime/CLI/dependency/lockfile behavior (`design.md:39-49`).
2. **RED tests specific enough?** Yes. I verified every parametrized wheel and sdist case (`..`, absolute, `C:/`, `C:`-relative, UNC, backslash) escapes the current `is_forbidden_release_member` and required-file logic, so each returns 0 (wheel) or 1-without-the-unsafe-message (sdist) today and fails the new assertions.
3. **Rejects before sdist root-prefix stripping?** Yes. `validate_sdist` computes `unsafe_errors = unsafe_archive_member_errors(raw_paths, ...)` on raw names *before* `paths = normalize_sdist_paths(raw_paths)` (`plan.md:190-194`), and the `fashion_radar-0.1.0/../outside.txt` case directly exercises the masking path.
4. **Preserves existing checks?** Yes. `paths = clean_archive_paths(raw_paths)` is unchanged in value, and required-file, forbidden-member, dist-info, METADATA, and entry-point validations continue in the same order (`plan.md:171-176`). I confirmed no existing WHEEL_FILES/SDIST_FILES/forbidden-test fixture contains a path the new guard would flag.
5. **Scope hygiene?** Yes — no dependency, lockfile, connector, scraping, browser automation, platform API, monitoring, scheduling, source acquisition, demand-proof, ranking, coverage-verification, or compliance/audit behavior.
6. **Verification sufficient?** Yes — focused pytest + ruff check/format, plus full release gate (`check_release_hygiene.py`, full pytest, ruff, `UV_NO_CONFIG=1 uv lock --check` with mirror envs unset, `git diff --exit-code -- uv.lock`, `git diff --check`), matching `AGENTS.md`.

## Final statement

**There are no Critical or Important blockers.** The plan is approved to proceed to implementation. The four Minor items are cosmetic and may be addressed at the implementer's discretion.

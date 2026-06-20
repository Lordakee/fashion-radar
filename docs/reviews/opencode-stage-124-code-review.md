# Stage 124 Code Review

## Critical findings
None.

## Important findings
None.

## Minor findings

1. **Sdist test fixtures emit collateral "missing required file" noise for 5 of 7 cases (by-design, pre-acknowledged at plan review).** `write_sdist_with_raw_member` writes the unsafe member without the `fashion_radar-0.1.0/` root, so for the non-`..` sdist cases (`../outside.txt`, `/absolute.txt`, `C:/outside.txt`, `C:outside.txt`, `//server/share/outside.txt`) `normalize_sdist_paths` sees >1 root and returns the un-stripped set, additionally producing `sdist archive missing required file: ...` lines. Tests still pass via `in` assertions, and the design explicitly accepts multiple errors per malformed archive (`design.md:92-94`). The two `fashion_radar-0.1.0/..`/backslash cases are clean. Non-blocking; carried forward from the plan review.

2. **`unsafe_archive_member_errors` does not deduplicate (pre-acknowledged at plan review).** It iterates the raw list before `clean_archive_paths` turns it into a set, so a repeated unsafe member would yield repeated error lines. Consistent with the "report all problems" style; no test exercises duplicates. Harmless for a release gate.

3. **`clean_archive_path` runs twice per sdist member** (once inside `unsafe_archive_member_errors`, once inside `normalize_sdist_paths`). Idempotent and purely a minor redundancy — not worth changing.

4. **A member that normalizes to empty (e.g. `/`, `./`) is skipped rather than flagged.** These are inert directory/root entries and not a realistic extraction escape vector for real wheel/sdist output, so this is acceptable within the stage's stated scope (reject clearly unsafe *shapes*), not a gap.

## Review-focus answers

1. **Matches design/plan?** Yes. `unsafe_archive_member_errors` (`scripts/check_package_archives.py:281`) and `is_unsafe_archive_path` (`:290`) match the plan code verbatim and are placed before `clean_archive_paths` as specified. `validate_wheel` (`:191-201`) and `validate_sdist` (`:266-272`) match the planned restructuring, including prepending `unsafe_errors` to the sdist error list. `re` (line 5) and `Iterable` (line 9) are already imported.

2. **Rejected before sdist root-prefix stripping?** Yes. In `validate_sdist`, `unsafe_archive_member_errors(raw_paths, ...)` runs on raw member names at `:267` before `normalize_sdist_paths(raw_paths)` at `:268`. The sdist case `fashion_radar-0.1.0/../outside.txt` whose expected error preserves the root prefix confirms the check sees the un-stripped name.

3. **Case coverage (`..`, absolute, drive, UNC, backslash)?** Yes, for both wheel and sdist. All 14 parametrized cases pass: parent traversal (`../`, `fashion_radar/../`, `fashion_radar-0.1.0/../`), POSIX absolute (`/absolute.txt`), Windows drive (`C:/x`, `C:x`), UNC (`//server/share/x` — caught by the leading-slash rule, backslash form also normalizes into it), and backslash normalization (`\..\` → `/../`). `is_unsafe_archive_path` lower/uppercase drive letters are both matched by `[A-Za-z]:`.

4. **Preserves existing checks?** Yes. Full suite: 53 passed. Required-file, forbidden-member, dist-info selection, METADATA Name/Version, and entry-point validations are unchanged and execute in the same order; no existing fixture path triggers the new guard.

5. **Avoids runtime/CLI/dependency/connector/scraping/etc.?** Yes. The diff touches only the release-gate checker and its tests — no runtime product code, CLI, dependency, `uv.lock`, connector, scraping, browser automation, platform API, monitoring, scheduling, source acquisition, demand proof, ranking, coverage verification, or compliance/audit behavior.

## Verification performed
- `uv --no-config run --frozen pytest tests/test_package_archives.py -q -k "unsafe_archive_member"` → 14 passed.
- `uv --no-config run --frozen pytest tests/test_package_archives.py -q` → 53 passed.
- `ruff check` + `ruff format --check` on both files → clean.

## Final statement

**There are no Critical or Important blockers before release.** The four Minor items are cosmetic/by-design (three were already accepted at plan review) and do not block the release gate.

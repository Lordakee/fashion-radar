Review the Stage 127 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Make `scripts/check_package_archives.py` reject unexpected direct children in
  the build output directory beyond the selected wheel, selected sdist, and
  uv's generated `.gitignore` marker.
- Preserve existing missing/duplicate wheel and sdist errors and
  archive-internal validation behavior.

Design, plan, and plan reviews:
- `docs/superpowers/specs/2026-06-20-stage-127-build-dir-direct-child-hygiene-design.md`
- `docs/superpowers/plans/2026-06-20-stage-127-build-dir-direct-child-hygiene-plan.md`
- `docs/reviews/opencode-stage-127-plan-review.md`
- `docs/reviews/opencode-stage-127-plan-rereview.md`
- `docs/reviews/opencode-stage-127-plan-rereview-2.md`

Files changed:
- `scripts/check_package_archives.py`
- `tests/test_package_archives.py`
- Stage 127 design/plan/review artifacts

Review focus:
1. Does the implementation match the revised Stage 127 design and plan?
2. Does the checker reject extra direct files and directories while still
   accepting exactly one valid wheel, one valid sdist, and uv's `.gitignore`
   marker?
3. Does the `.gitignore` allowance avoid hiding other unexpected direct
   children?
4. Does it preserve existing missing/duplicate archive selection messages and
   archive-internal validation behavior?
5. Does the stage avoid runtime product behavior, dependencies, lockfile,
   connectors, scraping, browser automation, platform API, monitoring,
   scheduling, source acquisition, demand proof, ranking, coverage
   verification, and compliance/audit product behavior?

Verified locally before review:
- `uv --no-config run --frozen pytest tests/test_package_archives.py -k "unexpected_direct or build_directory or gitignore" -q`
- `uv --no-config run --frozen pytest tests/test_package_archives.py -q`
- `uv --no-config run --frozen ruff check scripts/check_package_archives.py tests/test_package_archives.py`
- `uv --no-config run --frozen ruff format --check scripts/check_package_archives.py tests/test_package_archives.py`
- `tmp_build="$(mktemp -d)"; uv --no-config build --out-dir "$tmp_build"; uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"; rm -rf "$tmp_build"`
- `git diff --check`

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.

Review the Stage 134 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Reject wheels whose single top-level `.dist-info` directory does not match
  the expected project distribution name and version derived from
  `pyproject.toml`.
- Preserve existing exact-one-top-level `.dist-info`, missing dist-info file,
  metadata, entry point, and forbidden-member behavior.
- Keep this release-hygiene-only with no runtime product behavior changes.

Files changed:
- `scripts/check_package_archives.py`
- `tests/test_package_archives.py`
- Stage 134 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 134 design and plan?
2. Does the RED test prove that valid `METADATA` is not enough when the wheel
   `.dist-info` directory name or version is wrong?
3. Does the helper normalize `fashion-radar` to `fashion_radar` without adding
   dependencies?
4. Does the mismatch check run only after exactly one top-level `.dist-info`
   directory is selected, preserving nested/multiple/split layout behavior?
5. Does the stage avoid package filename validation, sdist root validation,
   dependency changes, `pyproject.toml`, `uv.lock`, CI changes, runtime product
   behavior changes, connectors, scraping, browser automation, platform API,
   monitoring, scheduling, source acquisition, demand proof, ranking, coverage
   verification, and compliance/audit product behavior?

Verification already run:
- `uv --no-config run --frozen pytest tests/test_package_archives.py::test_rejects_wheel_with_mismatched_dist_info_directory -q`
- `uv --no-config run --frozen pytest tests/test_package_archives.py -q -k "dist_info"`
- `uv --no-config run --frozen pytest tests/test_package_archives.py tests/test_package_metadata.py -q`
- `uv --no-config run --frozen ruff check scripts/check_package_archives.py tests/test_package_archives.py`
- `uv --no-config run --frozen ruff format --check scripts/check_package_archives.py tests/test_package_archives.py`
- `tmp_build="$(mktemp -d)"; uv --no-config build --out-dir "$tmp_build" && uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"; status=$?; rm -rf "$tmp_build"; exit $status`
- `git diff --check`

Return:
Start with `# Stage 134 Code Review`, then include:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.

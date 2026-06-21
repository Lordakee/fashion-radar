Review the Stage 136 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Reject wheel/sdist archive files whose outer filenames do not match the
  project name and version derived from `pyproject.toml`.
- Reject sdist archives whose raw top-level root directory does not match the
  same derived name/version before existing sdist path normalization can mask
  the mismatch.
- Preserve existing missing/multiple archive behavior and existing archive
  content checks.

Files changed:
- `scripts/check_package_archives.py`
- `tests/test_package_archives.py`
- Stage 136 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 136 design and plan?
2. Do the tests prove the previous checker accepted wrong wheel filenames,
   wrong sdist filenames, and wrong sdist roots when archive contents were
   otherwise valid?
3. Are expected wheel filename, sdist filename, sdist root directory, and wheel
   `.dist-info` directory derived from `ExpectedProjectMetadata` and the
   existing normalized distribution-name helper?
4. Does `validate_build_dir()` preserve missing/multiple archive short-circuit
   behavior before exact filename mismatch checks?
5. Does sdist root validation operate on raw tar member names before
   `normalize_sdist_paths()` strips a common root, and does it reject wrong
   single roots without adding noisy missing-required-file errors?
6. Does the implementation avoid wheel tag parsing, platform wheel support,
   wheel/sdist required-member changes, license-path validation changes,
   forbidden-member validation changes, build backend changes, dependency or
   lockfile changes, runtime product behavior changes, connectors, scraping,
   browser automation, platform APIs, monitoring, scheduling, source
   acquisition, demand proof, ranking, coverage verification, or
   compliance/audit product behavior?

Verification already run:
- `uv --no-config run --frozen pytest tests/test_package_archives.py::test_rejects_package_archives_with_mismatched_filenames tests/test_package_archives.py::test_rejects_sdist_with_mismatched_root_directory -q`
- `uv --no-config run --frozen pytest tests/test_package_archives.py -q`
- `uv --no-config run --frozen pytest tests/test_package_archives.py -q -k "filename or sdist_root or dist_info"`
- `uv --no-config run --frozen pytest tests/test_package_archives.py tests/test_package_metadata.py -q`
- `uv --no-config run --frozen ruff check scripts/check_package_archives.py tests/test_package_archives.py`
- `uv --no-config run --frozen ruff format --check scripts/check_package_archives.py tests/test_package_archives.py`
- `tmp_build="$(mktemp -d)"; uv --no-config build --out-dir "$tmp_build"; uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"; rm -rf "$tmp_build"`
- `git diff --check`

Return:
Start with `# Stage 136 Code Review`, then include:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.

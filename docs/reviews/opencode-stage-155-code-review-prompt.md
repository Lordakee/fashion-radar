# Stage 155 Code Review Prompt

You are reviewing the Stage 155 implementation for `/home/ubuntu/fashion-radar`.

Goal: Derive `tests/test_package_archives.py` package archive fixture names,
wheel `dist-info` paths, sdist root paths, and positive expected metadata strings
from `scripts/check_package_archives.py` helper functions instead of duplicating
`fashion_radar-0.1.0`.

Relevant files:
- `docs/reviews/opencode-stage-155-plan-review.md`
- `docs/reviews/opencode-stage-155-plan-rereview.md`
- `docs/superpowers/specs/2026-06-22-stage-155-package-archive-fixture-metadata-parity-design.md`
- `docs/superpowers/plans/2026-06-22-stage-155-package-archive-fixture-metadata-parity-plan.md`
- `tests/test_package_archives.py`
- `scripts/check_package_archives.py`

Review only the intended Stage 155 changes.

Please review:
- Whether positive wheel fixture `dist-info` paths and metadata content now use
  derived checker metadata.
- Whether archive writer defaults and sdist root/raw-member helpers use derived
  expected names.
- Whether `wheel_files_with_dist_info_dir()` and the three positive wheel
  override keys use `EXPECTED_WHEEL_DIST_INFO_DIR`.
- Whether expected error strings for expected archive filename, sdist root,
  wheel dist-info directory, missing `Name`, missing `Version`, and missing
  console script now derive from expected metadata.
- Whether intentionally wrong negative fixture names and unsafe traversal inputs
  remain explicit.
- Whether meaningful public package metadata pinning still exists and tests are
  not weakened.
- Whether runtime checker behavior remains unchanged.

Return findings first with severity and file/line references. If there are no
blocking issues, say that explicitly.

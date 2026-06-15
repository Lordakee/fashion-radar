# Claude Code Stage 45 Release Rereview Prompt

You are rereviewing Stage 45 after the initial release review found one
Important blocker.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a focused code, test, and release-readiness rereview.
- Do not edit files.
- Treat Critical and Important findings as blockers.

## Original Blocker

The initial release review in
`docs/reviews/claude-code-stage-45-release-review.md` found:

- Missing wheel `METADATA` or `entry_points.txt` could crash
  `scripts/check_package_archives.py` with a traceback instead of producing a
  controlled validation error.

## Fix Implemented

- Added regression tests:
  - `tests/test_package_archives.py::test_rejects_wheel_without_metadata_file_without_traceback`
  - `tests/test_package_archives.py::test_rejects_wheel_without_entry_points_file_without_traceback`
- Verified RED before the fix: both tests failed because stderr contained a
  traceback and did not contain the expected controlled missing-file message.
- Updated `scripts/check_package_archives.py` so content validation for
  `METADATA` and `entry_points.txt` runs only when those files exist; missing
  files are reported by `validate_wheel_dist_info_files()` as controlled
  validation errors.
- Also retained earlier tightened `.dist-info` validation:
  - exactly one top-level `.dist-info` directory;
  - all required dist-info files under that directory;
  - `RECORD` required;
  - nested, multiple, or split `.dist-info` layouts rejected.

## Additional Cleanup Since Initial Release Review

- `tests/test_package_archives.py` now includes missing single wheel-file and
  missing public sdist-doc regression tests, addressing the spec reviewer minor
  coverage note.
- CI/checklist/package-smoke tests require `UV_NO_CONFIG=1 uv build --out-dir
  "$tmp_build"` and `UV_NO_CONFIG=1 uv run python
  scripts/check_package_archives.py "$tmp_build"`.

## Files To Inspect

- `scripts/check_package_archives.py`
- `tests/test_package_archives.py`
- `tests/test_cli_docs.py`
- `.github/workflows/ci.yml`
- `docs/github-upload-checklist.md`
- `docs/reviews/claude-code-stage-45-release-review.md`
- `docs/reviews/claude-code-stage-45-release-review-prompt.md`
- `docs/reviews/claude-code-stage-45-release-rereview-prompt.md`

## Verification After Fix

Blocker regression tests:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_package_archives.py::test_rejects_wheel_without_metadata_file_without_traceback tests/test_package_archives.py::test_rejects_wheel_without_entry_points_file_without_traceback -q
```

Result after fix: `2 passed`.

Archive tests:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_package_archives.py -q
```

Result: `15 passed`.

Real archive smoke:

```bash
tmp_build="$(mktemp -d)"
UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
```

Result: build succeeded and archive script printed
`Package archives contain required files.`

Installed-wheel smoke:

```bash
tmp_build="$(mktemp -d)"
UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/fashion-radar" --help
"$tmp_env/venv/bin/python" -m fashion_radar --help
```

Result: both help commands exited 0.

Full verification:

```bash
UV_NO_CONFIG=1 uv run pytest -q
UV_NO_CONFIG=1 uv run ruff check .
UV_NO_CONFIG=1 uv run ruff format --check .
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```

Result: all passed; full test suite reported `655 passed`.

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the changes are acceptable to commit and push, include this exact
phrase:

```text
APPROVED FOR STAGE 45 COMMIT AND PUSH
```

# Stage 269 Code Rereview

The Important finding is fixed.

**Verification:**
- `_SAFE_ASSET_PATH_RE` (display.py:25-27) and schema `imageSrc` pattern (schema:317) now use the identical charset `[A-Za-z0-9._~-]` and identical overall regex.
- `_safe_asset_path` enforces it via `_SAFE_ASSET_PATH_RE.fullmatch(value) is None` (display.py:82), so `assets/foo bar.png`, `assets/foo+bar.png`, and `assets/foo%20bar.png` all return `None` → `image: null`.
- `test_row_one_app_payload_rejects_schema_invalid_display_asset_paths` (test:325-358) covers all three schema-invalid cases (space, plus, percent-encoded space) and asserts `image: None` + schema-valid payload.
- `test_row_one_app_payload_includes_story_display_metadata` (test:260-297) covers the safe path `assets/images/the-row.png` → serializes and schema-validates.
- All 33 contract tests pass.

**Accepted.**

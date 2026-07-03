Brief rereview only.

Previous code review:
- docs/reviews/opencode-stage-269-code-review.md

Review only whether the Important finding about schema/sanitizer mismatch is fixed.

Files to inspect:
- src/fashion_radar/row_one/display.py
- schemas/row-one-app.schema.json
- tests/test_row_one_app_contract.py

Expected fix:
- `safe_story_image_src` / `_safe_asset_path` must no longer accept `assets/...` paths that the schema `imageSrc` rejects.
- Tests should cover schema-invalid asset paths such as spaces, plus signs, or percent-encoded spaces becoming `image: null`.
- Safe `assets/images/the-row.png` should still serialize and schema-validate.

Return Critical/Important blockers only. If fixed, say Accepted.

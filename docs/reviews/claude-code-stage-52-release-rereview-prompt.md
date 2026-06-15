Please re-review the Stage 52 release after the first release review.

Original release review:
- `docs/reviews/claude-code-stage-52-release-review.md`

Files changed since that review:
- `docs/community-signal-import.md`
- `tests/test_cli_docs.py`

Fix applied:
- The Directory Manifest JSON example now uses the exact sorted
  `prohibited_fields` emitted by `build_community_signal_profile()`:
  `account_id`, `author_handle`, `cookie`, `direct_message`,
  `follower_count`, `full_post_body`, `image_url`, `profile_url`,
  `raw_comment`, `session`, `token`, `video_url`.
- `tests/test_cli_docs.py` now asserts those singular/current fields are in
  the Directory Manifest section and that quoted plural `cookies`, `sessions`,
  and `tokens` are not in that section.

Verification after the fix:
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q`
  -> `22 passed`
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check tests/test_cli_docs.py`
  -> `All checks passed!`
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check tests/test_cli_docs.py`
  -> `1 file already formatted`

Please check whether the prior Important finding is resolved and whether the
fix introduced any new Critical/Important issues.

You are re-reviewing Stage 28 before release commit and push.

Repository: `/home/ubuntu/fashion-radar`

Previous code review:

- `docs/reviews/claude-code-stage-28-code-review.md`

Blocking finding from previous review:

- `community-candidates` single-file mode printed arbitrary unexpected
  exception text unless it contained the input path/name. This could leak private
  row values or internals. Directory mode already used a generic unexpected
  exception message.

Fix made:

- `src/fashion_radar/cli.py`: single-file `community_candidates_command` now
  emits the same generic message for unexpected exceptions:
  `Could not preview community candidates: input file could not be read or validated`
- `tests/test_cli.py`: added
  `test_community_candidates_unexpected_error_has_clean_error_without_raw_message`
  to assert unexpected errors do not leak the input path, filename, private URL,
  private title text, or traceback.

Verification after fix:

- `.venv/bin/python -m pytest tests/test_cli.py -q` -> `184 passed`
- `.venv/bin/python -m ruff check src/fashion_radar/cli.py tests/test_cli.py`
- `.venv/bin/python -m ruff format --check src/fashion_radar/cli.py tests/test_cli.py`

Please verify:

1. The previous Important finding is fully resolved.
2. The fix does not weaken the Stage 28 directory command behavior.
3. No new Critical or Important findings block release.

Output format:

- List findings by severity: Critical, Important, Minor.
- Critical and Important findings block commit and push.
- If no blocking findings remain, include the exact phrase:
  `APPROVED FOR STAGE 28 RELEASE COMMIT AND PUSH`.

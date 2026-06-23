# Stage 160 Code Review Prompt

Review the Stage 160 implementation for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, or command logs. Start the response exactly with:

```text
# Stage 160 Code Review
```

Use repository files and the verification evidence below. Avoid running long
commands; if you run any commands, summarize the result in prose instead of
including logs.

Changed files:

- `scripts/check_package_archives.py`
- `tests/test_package_archives.py`
- `docs/superpowers/specs/2026-06-23-stage-160-wheel-entry-points-console-scripts-design.md`
- `docs/superpowers/plans/2026-06-23-stage-160-wheel-entry-points-console-scripts-plan.md`
- `docs/reviews/opencode-stage-160-plan-review-prompt.md`
- `docs/reviews/opencode-stage-160-plan-review.md`
- `docs/reviews/opencode-stage-160-code-review-prompt.md`

Objective:

Make the package archive checker require expected wheel entry points under the
`[console_scripts]` group.

Implementation summary:

- Added RED tests proving the old checker accepted expected scripts outside
  `[console_scripts]`, did not distinguish wrong targets, and accepted
  malformed no-header `entry_points.txt`.
- Replaced line-membership validation with
  `configparser.ConfigParser(interpolation=None)`.
- Set `parser.optionxform = str` before parsing to preserve script-name case.
- Added deterministic errors for missing console-script entries, wrong targets,
  and malformed `entry_points.txt`.

Verification already run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q -k "entry_points"
uv --no-config run --frozen pytest tests/test_package_archives.py -q
uv --no-config run --frozen ruff check scripts/check_package_archives.py tests/test_package_archives.py
uv --no-config run --frozen ruff format --check scripts/check_package_archives.py tests/test_package_archives.py
tmp_build=$(mktemp -d)
uv --no-config build --out-dir "$tmp_build"
uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"
rm -rf "$tmp_build"
```

Review questions:

1. Does the implementation reject expected scripts under the wrong entry-point
   group?
2. Does it preserve case-sensitive script names by setting `optionxform = str`?
3. Does it fail malformed `entry_points.txt` without a traceback?
4. Are tests sufficient and scoped to package archive validation?
5. Are there any critical or important findings before release verification?

Return critical, important, and minor findings. If there are no blocking
findings, say so explicitly.

# Claude Code Stage 330 Code Re-Review Prompt

You are re-reviewing `/home/ubuntu/fashion-radar` after Stage 330 post-review
fixes.

Model/effort requirement from the user: use max reasoning effort.

## Context

Base commit is `56047ec06ed83ee73e69472104a7dcce4792db80` (`origin/main`).
Review the current uncommitted working tree diff against that base.

Initial Stage 330 implementation adds default SQLite item retention to
`fashion-radar row-one refresh`, documents it, and updates first-run smoke and
scheduling docs.

After the first code review:

- Claude Code code review found no Critical/Important issues.
- A parallel release-risk audit found process issues:
  - Stage 330 plan commit allowlist omitted first-run/scheduling files.
  - Plan review-capture command did not use temp-file capture.
  - Plan final verification omitted first-run/package/installed-wheel release
    gates.
  - Release hygiene did not enforce Claude Code review artifact capture quality.

Those post-review fixes are now in the working tree:

- `docs/superpowers/plans/2026-07-07-stage-330-row-one-refresh-data-retention-plan.md`
  now includes temp-file Claude review capture, first-run/package/installed-wheel
  final verification, and the complete commit allowlist.
- `scripts/check_release_hygiene.py` now checks Stage 330+ Claude Code review
  artifacts in addition to opencode artifacts.
- `tests/test_release_hygiene.py` adds focused Claude Code review-artifact
  hygiene tests.
- `docs/reviews/claude-code-stage-330-plan-rereview.md` was cleaned to remove
  process chatter at the start.

## Re-Review Focus

Findings first, ordered by severity. Look for Critical/Important issues only in
the post-review changes and their integration with Stage 330:

1. Does the release-hygiene regex correctly include Claude Code review outputs
   while excluding prompt files?
2. Is Stage 330 enforcement starting at the right point without retroactively
   failing older Claude review artifacts?
3. Do the release-hygiene tests prove empty output, tool-status chatter, prompt
   exclusion, and legacy Stage 329 behavior?
4. Is the updated Stage 330 plan commit allowlist complete for the current
   changed files?
5. Is the updated final verification checklist aligned with the release gates?
6. Did any post-review change introduce product/runtime drift?

Do not propose compliance review product functionality.

## Fresh Verification Run After Post-Review Fixes

- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q`
  -> `2219 passed`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .`
  -> passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .`
  -> passed
- `UV_NO_CONFIG=1 uv lock --check`
  -> passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py`
  -> passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
  -> passed
- `git diff --check`
  -> passed
- tracked secret scan with `git grep -n -E 'ghp_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}' -- . ':!docs/reviews/*'`
  -> passed
- Package verification:
  - `UV_NO_CONFIG=1 uv --no-config build --out-dir "$tmp_build"`
  - `UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"`
  - install built wheel into a temporary venv
  - built-wheel `fashion-radar --help`
  - built-wheel `python -m fashion_radar --help`
  - built-wheel installed first-run smoke
  -> all passed

## Output Format

- Findings first.
- If no Critical/Important findings, say that clearly.
- Include file/line references for any issue.
- Include residual release risks, if any.

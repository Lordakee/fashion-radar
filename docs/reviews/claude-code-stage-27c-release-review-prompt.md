You are performing the final Stage 27 release review before commit and push.

Repository: `/home/ubuntu/fashion-radar`

Relevant approvals and plans:

- Stage 27A code approval:
  `docs/reviews/claude-code-stage-27a-code-review.md`
- Stage 27B docs approval:
  `docs/reviews/claude-code-stage-27b-docs-review.md`
- Stage 27C plan approval:
  `docs/reviews/claude-code-stage-27c-plan-review.md`
- Stage 27C continuation approval:
  `docs/reviews/claude-code-stage-27c-plan-rereview.md`
- Stage 27C design:
  `docs/superpowers/specs/2026-06-13-stage-27c-release-verification-design.md`
- Stage 27C plan:
  `docs/superpowers/plans/2026-06-13-stage-27c-release-verification-plan.md`

The previous final review blocked commit/push because malformed
`community-candidates` input could echo raw row values through validation error
messages. That has been fixed in `src/fashion_radar/cli.py` by returning the
generic message `input file could not be read or validated` for
`ManualSignalImportError`. A regression test was added in `tests/test_cli.py`
to assert malformed private row data does not leak path, filename, URL, title,
summary, invalid date, or invalid source-weight value.

A subsequent final-review attempt also exposed a process issue: writing review
output directly to `docs/reviews/claude-code-stage-27c-release-review.md` with
`tee` can make that file appear blank while Claude Code is reviewing the
worktree. The Stage 27C plan now writes final review output to a temporary file,
checks that the temporary file is non-empty and contains the approval phrase on
its own line, then moves it into
`docs/reviews/claude-code-stage-27c-release-review.md`.

Stage 27 changes to review:

- `src/fashion_radar/community_candidates.py`
- `src/fashion_radar/cli.py`
- `tests/test_community_candidates.py`
- `tests/test_cli.py`
- `README.md`
- `CHANGELOG.md`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `docs/candidate-discovery.md`
- `docs/architecture.md`
- `docs/source-boundaries.md`
- `docs/github-upload-checklist.md`
- Stage 27 plan/spec/review docs under `docs/superpowers/...` and
  `docs/reviews/claude-code-stage-27*.md`

Known worktree boundary:

- `uv.lock` has a pre-existing mirror-backed local diff.
- Stage 27 must not stage or commit `uv.lock`.
- Stage 27 does not modify `pyproject.toml`.
- Lock validation was performed against a clean `git archive HEAD` checkout
  with default PyPI, while the active worktree `uv.lock` diff remained
  unstaged.

Verification run after the validation-error fix:

```text
.venv/bin/python -m pytest -q
Result: 542 passed in 13.21s

.venv/bin/python -m pytest tests/test_cli.py::test_community_candidates_validation_error_has_clean_error_without_row_values tests/test_cli.py::test_community_candidates_invalid_file_has_clean_error_without_path_echo tests/test_cli.py::test_community_candidates_command_prints_json_without_paths_or_raw_values -q
Result: 3 passed

.venv/bin/python -m pytest tests/test_community_candidates.py tests/test_cli.py -q -k "community_candidates"
Result: 21 passed, 160 deselected

.venv/bin/python -m ruff check .
Result: All checks passed.

.venv/bin/python -m ruff format --check .
Result: 90 files already formatted.

git diff --check
Result: exit 0

UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
Result: checked 36 packages, would make no changes.

git diff --quiet -- pyproject.toml
Result: exit 0

git archive HEAD | tar -x -C "$tmp_lock_check"
uv lock --check --default-index https://pypi.org/simple --project "$tmp_lock_check"
Result: resolved 84 packages, exit 0.

Stage 27B required negative boundary phrase checks
Result: exit 0

Stage 27B unsafe-positive boundary classifier
Result: exit 0

Stage 27B output-exclusion documentation checker
Result: exit 0

UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv build --out-dir /tmp/fashion-radar-dist-stage27
Result: built sdist and wheel successfully.

Installed-wheel smoke:
- installed `/tmp/fashion-radar-dist-stage27/fashion_radar-0.1.0-py3-none-any.whl`
- ran `fashion-radar --help`
- ran `fashion-radar community-candidates --help`
- ran `fashion-radar community-candidates ... --format json`
- ran malformed `fashion-radar community-candidates ...` and asserted it failed
  with the generic validation message
- recursively rejected forbidden success-output keys:
  `path`, `url`, `title`, `summary`, `raw_text`, `normalized_key`,
  `normalized_phrase`, `candidate_context`, `candidate_contexts`,
  `representative_item`, `representative_items`
- recursively rejected forbidden success-output values:
  temp input path, temp CSV path, row URL, row title, row summary
- rejected forbidden error-output values:
  temp bad CSV path, private row URL, private row title, private row summary,
  invalid date, invalid source-weight value
- asserted the smoke temp root contained exactly:
  `config/`, `config/scoring.yaml`, `community-signals.csv`,
  `bad-community-signals.csv`, `community-candidates-smoke.json`,
  `bad.stdout`, `bad.stderr`
Result: exit 0

Pre-final-review secret scan over tracked + untracked files, excluding `uv.lock`
Result: exit 0, no findings

Pre-final-review generated artifact scans over tracked + untracked files
Result: exit 0, no findings outside allowed `.codegraph/.gitignore` and
`reports/README.md`

Pre-final-review staged `uv.lock` check
Result: exit 0, `uv.lock` is not staged
```

Review focus:

1. Is the previous blocking validation-error leak fixed?
2. Are the Stage 27A code changes ready to commit?
3. Are the Stage 27B docs ready to commit?
4. Does `community-candidates` remain local, one-file, read-only, pre-import,
   and aggregate-only?
5. Do code, tests, and installed-wheel smoke evidence show success and error
   output exclude supplied input paths, row URLs, row titles, summaries, raw
   text, normalized keys, candidate contexts, and representative item details?
6. Do the docs avoid unsafe positive claims about platform coverage, proof of
   demand, source quality/ranking, source acquisition, scraping,
   monitoring/watchers, scheduling, report/dashboard generation, database
   import/SQLite writes, entity YAML/config generation, and source connectors?
7. Is `uv.lock` correctly excluded from staging/commit despite the known local
   mirror diff?
8. Are the planned explicit staging allowlist and post-review scans adequate?
9. Is the planned push method non-persistent and token-safe if the real token is
   supplied only in the in-memory shell environment for the push command?
10. Are there any Critical or Important issues that should block commit/push?

Output format:

- List findings by severity: Critical, Important, Minor.
- Critical and Important findings block commit/push.
- If no blocking findings remain, put this exact approval phrase alone on its
  own line:
  `APPROVED FOR STAGE 27 RELEASE COMMIT AND PUSH`

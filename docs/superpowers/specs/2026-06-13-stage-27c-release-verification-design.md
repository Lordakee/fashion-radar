# Stage 27C Release Verification Design

## Goal

Complete Stage 27 by verifying the approved Stage 27A code and Stage 27B docs,
requesting final Claude Code review, committing the Stage 27 files, and pushing
to the existing GitHub remote.

## Scope

Stage 27C may create or update review/plan docs needed for final review, then
stage, commit, and push the already approved Stage 27A/27B work.

Files eligible for staging:

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
- `docs/superpowers/specs/2026-06-13-stage-27*.md`
- `docs/superpowers/plans/2026-06-13-stage-27*.md`
- `docs/reviews/claude-code-stage-27*.md`

Out of scope:

- `uv.lock` changes. The active worktree has a known pre-existing mirror-backed
  `uv.lock` diff. It must remain unstaged and uncommitted.
- Any production code changes beyond the already reviewed Stage 27A files.
- Any dependency, generated artifact, local database, report, browser state,
  token, or build artifact commits.

## Verification

Run full local verification before commit:

- `pytest`
- `ruff check`
- `ruff format --check`
- `git diff --check`
- `uv sync --frozen --dev --check` with the Tsinghua PyPI mirror
- `uv lock --check` against the default PyPI registry
- `uv build` into `/tmp`
- installed-wheel smoke including `community-candidates --help`, a local CSV
  preview run, recursive output-exclusion assertions, and a no-generated-output
  check in the smoke temp directory
- Stage 27B boundary and output-exclusion documentation verification
- secret scans for common token patterns before and after final review files are
  created
- artifact scans for generated databases, reports, build outputs, caches,
  CodeGraph runtime files, tracked files, and untracked pending files
- final Claude Code review with `--effort max`

## GitHub Push Boundary

The remote must remain token-free. Use the user-provided GitHub token only for a
single push command through an ephemeral Git HTTP header or equivalent
non-persistent mechanism. Do not write it to files, git config, shell history,
review docs, logs, or committed artifacts.

After pushing, verify that:

- `origin/main` contains the new commit;
- the remote URL does not include a token;
- local git config does not contain a persisted GitHub `extraheader` or token;
- `uv.lock` remains unstaged and uncommitted;
- no unexpected generated or secret-bearing files are tracked.

Review the Stage 132 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Extend `scripts/check_release_hygiene.py` so unignored untracked files are
  scanned for secret content, not only forbidden paths.
- Preserve symlink skip behavior for newly scanned untracked paths, so an
  untracked symlink is not followed to an ignored token-bearing target.
- Keep existing secret patterns, redaction, path policy, and runtime/product
  behavior unchanged.

Files changed:
- `scripts/check_release_hygiene.py`
- `tests/test_release_hygiene.py`
- Stage 132 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 132 design and plan?
2. Does `collect_findings()` now scan `untracked_paths` with
   `find_secret_findings(..., "untracked")`?
3. Does the regression test prove a publishable-looking untracked file with a
   valid GitHub token is rejected, redacted, and line-numbered?
4. Does `find_secret_findings()` skip original untracked symlink paths before
   `safe_repo_path()` can resolve their targets, does the symlink regression
   test prove this, and is tracked-path behavior preserved?
5. Does the stage avoid secret pattern changes, forbidden path policy changes,
   docs verification-surface changes, dependency/lockfile changes, package
   archive checker changes, runtime product behavior changes, connectors,
   scraping, browser automation, platform APIs, monitoring, scheduling, source
   acquisition, demand proof, ranking, coverage verification, and
   compliance/audit product behavior?

Use the current git diff and files for review. Do not run commands or repeat
verification; the focused verification already completed:
- `pytest tests/test_release_hygiene.py::test_untracked_symlink_target_is_not_scanned_for_secret -q` failed before the symlink-safe path fix and passed after it.
- `pytest tests/test_release_hygiene.py -k "untracked_file_with_valid_github_token or tracked_file_with_valid_github_token or untracked_symlink_target"` passed.
- `pytest tests/test_release_hygiene.py` passed.
- `ruff check scripts/check_release_hygiene.py tests/test_release_hygiene.py` passed.
- `ruff format --check scripts/check_release_hygiene.py tests/test_release_hygiene.py` passed.
- `python scripts/check_release_hygiene.py --repo-root .` passed.
- one-shot tracked symlink behavior check passed: a tracked symlink to an
  ignored token-bearing target still reports a tracked secret finding.
- `git diff --check` passed.

Return:
Start with `# Stage 132 Code Review`, then include:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.

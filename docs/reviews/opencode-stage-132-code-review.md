# Stage 132 Code Review

## Critical findings
None. The change is minimal, surgical, and well-scoped: it adds exactly one new scan call in `collect_findings()` and one guarded early-skip in `find_secret_findings()`. Tracked-file behavior is untouched (guarded by `path_status == "untracked"`), `safe_repo_path()` is unchanged, and all secret patterns, redaction, forbidden-path policy, and downstream checks remain as-is. No new file reads can escape the repo because `safe_repo_path()` still enforces resolved-path containment, and the new pre-check only makes untracked scanning *more* conservative (skipping symlinks).

## Important findings
None. The implementation correctly satisfies the stated goal:
- Untracked, unignored files are now scanned for secret content (`collect_findings` extension at scripts/check_release_hygiene.py:152).
- The new `(repo_root / normalized).is_symlink()` skip at scripts/check_release_hygiene.py:262–263 is genuinely necessary (not redundant): `safe_repo_path()` returns the *resolved* path, so the existing post-resolution `file_path.is_symlink()` guard would be `False` for an in-repo symlink target and the target would otherwise be followed. This is exactly what the RED→GREEN verification of `test_untracked_symlink_target_is_not_scanned_for_secret` proves.
- The skip is correctly placed after `if not normalized` and before `safe_repo_path()`, avoiding both containment bypass and unnecessary resolution.
- `Path.is_symlink()` cannot raise on missing/broken links, so no new exception surface is introduced; broken symlinks and symlinked directories are safely skipped.
- Secret-bypass analysis holds: an untracked symlink to an unignored untracked target still leaks via the target being scanned directly; only the intentionally-ignored-target case is suppressed, which is consistent with the pre-existing `.gitignore` policy.

## Minor findings
1. **Tracked/untracked symlink asymmetry is by design but non-obvious.** Tracked symlinks are followed (target scanned, per the manual verification), while untracked symlinks are skipped. This matches the goal ("preserve symlink skip behavior for newly scanned untracked paths") and preserves existing tracked behavior, so it is correct — but a one-line doc note in `find_secret_findings()` would help future maintainers understand why the `path_status == "untracked"` guard exists. Not a blocker.
2. **Coverage relies on manual verification for three edges.** Untracked-binary skip, out-of-repo untracked symlink containment, and the tracked-symlink-still-reports behavior are only verified manually per the prompt. Adding automated tests for these would harden the suite against future regressions, but the manual verification recorded is sufficient for release.
3. **Wording reuse of "forbidden"** in `forbidden secret in untracked file: ...` mirrors the tracked message format, which is consistent; only flagging since "forbidden" elsewhere refers to path policy. Cosmetic only.

## Final statement
There are **no Critical or Important blockers** before release. The diff matches the stated goal, the two new tests are correct and sufficient to lock in the intended behavior (with RED confirmed for both before the fix), the full 70-test suite, ruff check, ruff format --check, and the end-to-end `--repo-root .` run all pass, and the manual edge-case verifications (artifact scan, out-of-repo symlink containment, untracked binary skip, tracked-symlink reporting) cover the residual surface. The implementation is safe to release.

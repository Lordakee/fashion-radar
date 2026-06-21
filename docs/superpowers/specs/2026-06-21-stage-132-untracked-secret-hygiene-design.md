# Stage 132 Untracked Secret Hygiene Design

## Objective

Make the release hygiene checker scan unignored untracked files for secret
content, not only their paths.

## Problem

`scripts/check_release_hygiene.py` currently collects both tracked files and
unignored untracked files. It checks forbidden paths for both groups, but secret
content scanning only receives `tracked_paths`.

That leaves a narrow gap: an untracked publishable-looking file such as
`notes.md` can contain a valid GitHub token or PEM private key and still pass
the release hygiene gate as long as its path is not otherwise forbidden.

## Scope

In scope:

- Extend `collect_findings()` so `find_secret_findings()` also scans
  `untracked_paths` with the status label `untracked`.
- Add a regression test proving an untracked file with a valid GitHub token is
  rejected, redacted, and line-numbered.
- Preserve symlink skip behavior for the newly scanned untracked paths so an
  untracked symlink does not cause an ignored target to be scanned.
- Reuse existing secret pattern, redaction, binary skip, symlink skip, and safe
  path behavior.

Out of scope:

- No secret pattern changes.
- No forbidden path policy changes.
- No docs verification-surface changes.
- No dependency or lockfile changes.
- No package archive checker changes.
- No runtime product behavior changes.
- No connector, scraping, browser automation, platform API, monitoring,
  scheduling, source acquisition, demand proof, ranking, coverage verification,
  or compliance/audit product behavior.

## Architecture

The release hygiene flow already has the needed primitive:

```python
find_secret_findings(repo_root, paths, path_status)
```

Stage 132 only adds:

```python
findings.extend(find_secret_findings(repo_root, untracked_paths, "untracked"))
```

after the existing tracked secret scan. This keeps tracked and untracked
findings independently labeled and preserves all existing redaction behavior.
Because this makes untracked symlinks newly reachable by the secret scan,
`find_secret_findings()` checks the original repo-relative path for a symlink
before calling `safe_repo_path()` when the path status is `untracked`. That
preserves the existing resolved-path containment guard and tracked-path behavior
while preventing untracked symlink targets from being followed.

## Expected Behavior

After implementation:

- A clean repository still prints `Release hygiene checks passed.`
- A tracked file containing a valid GitHub token still fails with a redacted
  `tracked file` finding.
- An unignored untracked file containing a valid GitHub token now fails with a
  redacted `untracked file` finding.
- An untracked symlink is skipped rather than followed to an ignored target.
- Ignored local artifacts remain excluded by `git ls-files --others
  --exclude-standard`.

## Risks

- Unignored scratch files with realistic token-shaped fixture data will now fail
  the release hygiene gate. This is intentional for release hygiene.
- Unignored large text files will now be scanned. Ignored artifacts remain
  excluded, and binary files are still skipped by the existing helper.
- A forbidden untracked path containing a secret can produce both a path finding
  and a redacted secret finding. This mirrors the strict release-gate style and
  keeps sensitive values out of stderr.
- Existing untracked path regression fixtures use non-matching placeholder
  content, so they should continue to report path findings without new secret
  findings.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_release_hygiene.py -k "untracked_file_with_valid_github_token or tracked_file_with_valid_github_token"
uv --no-config run --frozen pytest tests/test_release_hygiene.py::test_untracked_symlink_target_is_not_scanned_for_secret -q
uv --no-config run --frozen pytest tests/test_release_hygiene.py
uv --no-config run --frozen ruff check scripts/check_release_hygiene.py tests/test_release_hygiene.py
uv --no-config run --frozen ruff format --check scripts/check_release_hygiene.py tests/test_release_hygiene.py
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --check
```

Release gate:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --exit-code -- uv.lock
git diff --check
if rg -n 'ghp_[A-Za-z0-9]+' .; then echo 'GitHub token pattern found in worktree' >&2; exit 1; fi
if [ -n "$(git config --get-all http.https://github.com/.extraheader || true)" ]; then echo 'Persistent GitHub auth header found' >&2; exit 1; fi
```

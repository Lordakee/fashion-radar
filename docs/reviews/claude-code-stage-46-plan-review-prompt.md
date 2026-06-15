# Claude Code Stage 46 Plan Review Prompt

You are reviewing the Stage 46 repo release hygiene gate plan for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Add a local, dependency-free release hygiene gate that catches accidental
publication of local runtime files, secrets, generated data, generated configs,
and private exports before the repository is pushed or packaged for GitHub.

## Proposed Technical Approach

- Create `scripts/check_release_hygiene.py` as a no-network standard-library
  script that checks:
  - forbidden tracked repository paths via `git ls-files`;
  - selected high-risk unignored local paths via
    `git ls-files --others --exclude-standard`;
  - persistent token-like git remotes and `http.*.extraheader` config;
  - high-confidence tracked content leaks such as GitHub personal access tokens
    and PEM private key blocks, with values redacted.
- Extend `scripts/check_package_archives.py` with a shared forbidden-member
  classifier used for both wheels and sdists.
- Keep content scanning intentionally narrow. Do not add broad keyword scanning
  for words such as token, secret, cookie, or session because docs and tests
  intentionally use those words.
- Update `.gitignore`, CI, `docs/github-upload-checklist.md`, and
  `tests/test_cli_docs.py` so local release hygiene, package archive smoke, and
  human upload steps stay aligned.
- Update GitHub Actions checkout to use `persist-credentials: false`, avoiding
  a false failure from runner-injected `http.*.extraheader` config.
- Add pytest coverage for release hygiene behavior, package archive denylist
  behavior, and docs/CI drift.
- Use length-aware valid-looking GitHub token regexes, not prefix-only
  detection, so docs/tests containing examples such as `ghp_` do not self-fail.
- Consistently deny local credential config filenames such as `.pypirc`,
  `pip.conf`, `pip.ini`, `uv.toml`, `.netrc`, and `.npmrc` across tracked path,
  high-risk untracked path, and package archive policies.
- Preserve current project boundaries: no scraping, crawling, platform
  automation, source acquisition, account/cookie/session tooling, external
  services, dependency changes, lockfile changes, runtime behavior changes, or
  product compliance-review functionality.
- Treat commit/push/CI confirmation as a separate node completion process that
  is user-authorized in this thread and must use a non-persistent git auth
  header, not as tool functionality.

## Files To Review

- `docs/superpowers/specs/2026-06-15-stage-46-repo-release-hygiene-gate-design.md`
- `docs/superpowers/plans/2026-06-15-stage-46-repo-release-hygiene-gate-plan.md`
- Current context files likely affected by the plan:
  - `.gitignore`
  - `.github/workflows/ci.yml`
  - `docs/github-upload-checklist.md`
  - `scripts/check_package_archives.py`
  - `tests/test_package_archives.py`
  - `tests/test_cli_docs.py`

## Specific Questions

1. Is Stage 46 the right next node after Stage 45 package archive readiness?
2. Is the release hygiene script scoped tightly enough to avoid false positives
   in documentation-heavy files while still catching high-confidence leaks?
3. Are the forbidden tracked, untracked, and archive-member policies complete
   enough for GitHub upload readiness?
4. Is the TDD sequence credible, especially the RED tests for the new script
   and archive denylist?
5. Does the plan avoid product compliance-review functionality and avoid any
   scraping/crawling/social platform automation or account/cookie/session
   tooling?
6. Are there any Critical or Important issues that must be fixed before
   implementation?

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 46 REPO RELEASE HYGIENE GATE
```

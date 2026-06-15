# Claude Code Stage 46 Release Review Prompt

You are reviewing the Stage 46 repo release hygiene gate diff for the
`fashion-radar` repository before commit and push.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a release/code/docs review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Add local release hygiene checks that prevent repository and package archives
from publishing secrets, generated local artifacts, private exports, runtime
state, or persistent git credentials.

## Approved Plan And Review Artifacts

- `docs/superpowers/specs/2026-06-15-stage-46-repo-release-hygiene-gate-design.md`
- `docs/superpowers/plans/2026-06-15-stage-46-repo-release-hygiene-gate-plan.md`
- `docs/reviews/claude-code-stage-46-plan-review.md`
- `docs/reviews/claude-code-stage-46-plan-rereview.md`

## Files Changed

- `.gitignore`
- `.github/workflows/ci.yml`
- `docs/github-upload-checklist.md`
- `docs/reviews/claude-code-stage-46-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-46-plan-review.md`
- `docs/reviews/claude-code-stage-46-plan-rereview-prompt.md`
- `docs/reviews/claude-code-stage-46-plan-rereview.md`
- `docs/reviews/claude-code-stage-46-release-review-prompt.md`
- `docs/superpowers/specs/2026-06-15-stage-46-repo-release-hygiene-gate-design.md`
- `docs/superpowers/plans/2026-06-15-stage-46-repo-release-hygiene-gate-plan.md`
- `scripts/check_package_archives.py`
- `scripts/check_release_hygiene.py`
- `tests/test_package_archives.py`
- `tests/test_release_hygiene.py`
- `tests/test_cli_docs.py`

## Implementation Summary

- Added `scripts/check_release_hygiene.py`, a dependency-free checker that:
  - runs only local git commands in the target repository;
  - rejects forbidden tracked paths;
  - rejects selected high-risk unignored untracked paths;
  - detects persistent token-like git remote URLs and
    `http.*.extraheader` authorization config without printing secret values;
  - scans tracked text files for length-aware GitHub token patterns and PEM
    private key blocks, redacting findings;
  - fails cleanly outside a git repository.
- Extended `scripts/check_package_archives.py` so wheels and sdists reject
  forbidden release members including env files, caches, bytecode, build/dist
  output, CodeGraph runtime files, generated data/reports/configs, SQLite/db
  files and sidecars, cookie/session/browser state, private exports, local
  credential configs, and key material.
- Updated `.gitignore` with narrow local artifact and credential patterns.
- Updated CI to use `actions/checkout@v4` with `persist-credentials: false`
  and run the release hygiene gate before lint/test/build.
- Updated `docs/github-upload-checklist.md` and docs drift tests so the human
  upload checklist and CI keep the same release hygiene/package smoke commands.
- Preserved project boundaries: no scraping, crawling, platform automation,
  source acquisition, account/cookie/session tooling, external service
  integrations, dependency changes, lockfile changes, runtime feature changes,
  or product compliance-review functionality.

## Verification Evidence To Check

The following commands were run locally after the implementation and reviewer
fixes:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_release_hygiene.py tests/test_package_archives.py tests/test_cli_docs.py -q
UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
```

Before this prompt was written, the focused results were:

- `105 passed` for the focused pytest command.
- `Release hygiene checks passed.` for the script self-check.

The full verification commands should be rerun after this prompt is created
and the result file is produced.

## Specific Questions

1. Does the diff implement the approved Stage 46 plan?
2. Are release hygiene tracked, untracked, remote/config, and tracked-content
   checks sufficiently complete and not overly broad?
3. Are package archive forbidden-member checks aligned with the repo hygiene
   policy and approved denylist?
4. Is CI wired correctly, especially `persist-credentials: false` before
   running the release hygiene gate?
5. Do docs and tests keep CI/checklist release commands aligned?
6. Does the implementation avoid product compliance-review functionality and
   avoid scraping/crawling/platform automation or account/cookie/session
   tooling?
7. Are there any Critical or Important issues that must be fixed before commit
   and push?

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the diff is acceptable to commit and push, include this exact
phrase:

```text
APPROVED FOR STAGE 46 COMMIT AND PUSH
```


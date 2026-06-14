# Claude Code Stage 35 Release Review Prompt

You are reviewing the completed Stage 35 public launch contact changes for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a release review only; do not edit files.
- Treat Critical and Important findings as blockers.
- Review both tracked diffs and untracked Stage 35 files.

## Goal

Make public security/conduct reporting paths actionable, align CI wheel package
smoke with the release checklist's required template/config paths, and prepare a
safe private-to-public repository visibility switch followed immediately by
GitHub private vulnerability reporting enablement.

## Changed Files To Review

- `SECURITY.md`
- `CODE_OF_CONDUCT.md`
- `CHANGELOG.md`
- `.github/workflows/ci.yml`
- `.github/ISSUE_TEMPLATE/conduct_report.yml`
- `docs/superpowers/specs/2026-06-14-stage-35-public-launch-contact-design.md`
- `docs/superpowers/plans/2026-06-14-stage-35-public-launch-contact-plan.md`
- `docs/reviews/claude-code-stage-35-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-35-plan-review.md`
- `docs/reviews/claude-code-stage-35-release-review-prompt.md`

## Scope Boundaries

Stage 35 must remain docs/CI/repository-settings only:

- No runtime code changes.
- No dependency or `uv.lock` changes.
- No source connectors, scraping, crawling, platform automation, browser
  automation, login/cookie flows, watchers, schedulers, source acquisition,
  source ranking, demand proof, platform coverage verification, or
  social-platform functionality.
- No PyPI publishing or artifact upload.

## GitHub Setting Evidence

Current pre-public repository check returned:

```json
{"full_name": "Lordakee/fashion-radar", "private": true, "permissions": {"admin": true, "maintain": true, "push": true, "triage": true, "pull": true}}
```

Earlier direct PVR `GET`/`PUT` calls returned `404` while the repository was
private, so the approved plan now defers PVR enablement until after the
private-repo commit is pushed and CI passes. The final release operation is:

1. Keep repo private through local verification, commit, push, and GitHub
   Actions confirmation.
2. Re-run final clean worktree and history secret scans.
3. Switch `Lordakee/fashion-radar` public via GitHub REST API.
4. Immediately enable PVR with
   `PUT /repos/Lordakee/fashion-radar/private-vulnerability-reporting`.
5. Verify `GET /repos/Lordakee/fashion-radar/private-vulnerability-reporting`
   returns `{"enabled": true}`.
6. If PVR enablement or verification fails after public visibility, immediately
   attempt to restore private visibility and stop Stage 35.

## Verification Evidence

Fresh commands already run successfully:

```text
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
UV_NO_CONFIG=1 CI=true GITHUB_ACTIONS=true _TYPER_FORCE_DISABLE_TERMINAL=1 uv run pytest -q
UV_NO_CONFIG=1 uv run ruff check .
UV_NO_CONFIG=1 uv run ruff format --check .
tmp_build="$(mktemp -d)"; UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"; UV_NO_CONFIG=1 uv run python - "$tmp_build"/*.whl ...
rg -n 'uv build --out-dir|Wheel template files present|fashion_radar/templates' .github/workflows/ci.yml
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
Stage 35 file secret scan with refined PAT/key patterns
tracked history secret scan with refined PAT/key patterns
LC_ALL=C rg -n '[^\x00-\x7F]' over Stage 35 files
```

Observed key results:

```text
572 passed in 14.28s
All checks passed!
92 files already formatted
Wheel template files present: fashion_radar/templates/configs/entities.example.yaml, fashion_radar/templates/configs/scoring.example.yaml, fashion_radar/templates/configs/sources.example.yaml, fashion_radar/templates/daily_report.md
No `uv.lock` diff.
No Stage 35 file or tracked-history secret matches with refined patterns.
No non-ASCII characters in Stage 35 files.
```

## Review Focus

Please review:

- Whether the docs make security and conduct reporting actionable after public
  visibility and PVR enablement.
- Whether the conduct issue form is safe for public issues and avoids requesting
  secrets, private source exports, local databases, generated reports, private
  security details, or doxxing material.
- Whether the CI here-doc wheel assertion is valid in GitHub Actions YAML and
  proves all required template/config files exist in the wheel.
- Whether the visibility/PVR sequence and rollback assertions in the plan are
  safe enough for public launch under the user's standing authorization.
- Whether the Stage 35 diff stays inside docs/CI/repository-settings scope.
- Whether any Critical or Important issue should block commit, push, public
  visibility, or PVR enablement.

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the changes are acceptable to commit, push, switch public, and
enable/verify PVR, include this exact phrase:

```text
APPROVED FOR STAGE 35 COMMIT, PUSH, PUBLIC VISIBILITY, AND PVR
```

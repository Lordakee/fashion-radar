# Claude Code Stage 11 Code Review Prompt

Please review the current Stage 11 code and docs before GitHub push. Do not
edit files, do not commit, do not call the network, do not run collectors, and
do not execute platform/social tooling.

Project: `/home/ubuntu/fashion-radar`

Use maximum reasoning effort. The invoking command should be:

```bash
claude -p --effort max --allowedTools=Read,Grep,Glob < docs/reviews/claude-code-stage-11-code-review-prompt.md
```

## Stage 11 Objective

Add optional local digest packaging for already-generated Fashion Radar daily
Markdown/JSON reports. The goal is to make scheduled daily output easier to
find and hand off locally, without adding delivery services, platform
collection, account automation, or network sending.

## Plan Gate

Plan/design files:

- `docs/superpowers/specs/2026-06-12-stage-11-local-digest-design.md`
- `docs/superpowers/plans/2026-06-12-stage-11-local-digest-plan.md`
- `docs/reviews/claude-code-stage-11-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-11-plan-review.md`

Plan review result:

- Claude Code returned `Approved for Stage 11 implementation`.
- Critical findings: none.
- Important findings: none.
- Minor notes were incorporated before implementation:
  - explicit `.eml` no `To`/`Cc`/`Bcc`,
  - report-index JSON shape,
  - real ISO date validation,
  - symlink replacement behavior,
  - explicit default no-op CLI tests,
  - digest module dependency boundary.

## Changed/New Files To Review

- `.gitignore`
- `CHANGELOG.md`
- `README.md`
- `docs/architecture.md`
- `docs/daily-digest.md`
- `docs/scheduling.md`
- `reports/README.md`
- `src/fashion_radar/digests.py`
- `src/fashion_radar/cli.py`
- `src/fashion_radar/dashboard/app.py`
- `tests/test_digests.py`
- `tests/test_cli.py`
- `tests/test_dashboard.py`

## Implemented Behavior Summary

- Added `fashion_radar.digests`, a stdlib-only local packaging module.
- Added `DigestLatestMode`, `DigestOptions`, and `DigestResult`.
- Added `package_daily_digest()` for optional local artifacts.
- Added `--digest-latest none|copy|symlink`, `--digest-index`,
  `--digest-eml`, and `--digest-summary` to both `fashion-radar report` and
  `fashion-radar run`.
- Default `report` and `run` behavior remains no-op for digest packaging and
  preserves existing output.
- `--digest-latest copy` writes local `latest.md` and `latest.json` copies.
- `--digest-latest symlink` writes local relative symlinks.
- `--digest-index` writes `report-index.json` with a stable top-level
  `entries` array containing `report_date`, `markdown_path`, and `json_path`.
- Index generation scans only strict `fashion-radar-YYYY-MM-DD.{md,json}` pairs
  with real ISO calendar dates and ignores helper/malformed files.
- `--digest-eml` writes a local `.eml` file with subject/body plus Markdown and
  JSON attachments. It sets no `To`, `Cc`, or `Bcc` headers and does not send.
- `--digest-summary` prints local observed configured-source-set wording.
- Packaging failures print `Could not package digest: <error>` and exit
  non-zero after the date-stamped report files have already been written.
- Updated dashboard trend caption wording to avoid broad coverage phrasing.
- Updated docs and `.gitignore` for local digest artifacts.

## Explicit Out Of Scope

Stage 11 must not add or document:

- SMTP sending, Sendmail sending, webhooks, push services, desktop
  notifications, browser opening, or background daemons
- platform search or automated social collection
- crawlers, scrapers, browser automation, Playwright, Selenium, MCP platform
  scraping servers, or account automation
- login cookies, account/session files, browser profiles, tokens, credentials,
  proxy pools, fingerprint evasion, CAPTCHA bypass, rate-limit bypass,
  access-control bypass, or paywall bypass
- official or unofficial social platform APIs
- instructions for obtaining exports from Instagram, TikTok, X/Twitter,
  Xiaohongshu, or similar platforms
- raw comments, full post bodies, DMs, private data, account IDs, follower
  lists, profile internals, images, videos, media downloading, or reposting
- claims of complete source coverage, verified demand outside the configured
  source set, or real-time social monitoring
- LLM scoring, embeddings, vector databases, image recognition, or paid service
  requirements
- database schema changes, new delivery tables, dashboard writes, or default
  source collection behavior changes

## Verification Already Run

- `.venv/bin/python -m pytest tests/test_digests.py -q`
  - `9 passed`
- `.venv/bin/python -m pytest tests/test_digests.py tests/test_cli.py -k "digest or report_command or run_command" -q`
  - `18 passed, 38 deselected`
- `.venv/bin/python -m pytest tests/test_digests.py tests/test_cli.py tests/test_dashboard.py -k "digest or report_command or run_command or trend_caption" -q`
  - `19 passed, 60 deselected`
- `.venv/bin/python -m pytest -q`
  - `261 passed`
- `.venv/bin/python -m ruff check .`
  - passed
- `.venv/bin/python -m ruff format --check .`
  - `70 files already formatted`
- `git diff --check`
  - passed
- `uv lock --check --default-index https://pypi.org/simple`
  - passed; `uv.lock` unchanged
- `uv sync --locked --dev --check --default-index https://pypi.org/simple`
  - passed; would make no changes
- `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check`
  - passed; mirror install check would make no changes
- `uv build --out-dir /tmp/fashion-radar-dist-stage11`
  - built wheel and sdist successfully
- Installed-wheel smoke:
  - created `/tmp/fashion-radar-stage11-smoke`
  - installed the built wheel using `--index-url https://pypi.tuna.tsinghua.edu.cn/simple`
  - `fashion-radar report --help` listed all digest options
- CodeGraph status:
  - healthy; 83 files indexed; new digest module visible
- Secret scan note:
  - GitHub token patterns were checked earlier with no matches.
  - A broad `session|cookie` scan currently matches only policy/review docs that
    explicitly forbid committing such artifacts, not newly generated secret
    material.

## Review Questions

Please focus on:

1. Whether `src/fashion_radar/digests.py` stays within local file packaging and
   avoids imports from database, collector, dashboard, source, scoring, and
   workflow modules.
2. Whether copy/symlink/latest/index/EML behavior is deterministic and safe.
3. Whether symlink replacement avoids following an existing outside target.
4. Whether report-index generation ignores malformed files and invalid dates.
5. Whether `.eml` generation remains a local file handoff and does not imply
   sending.
6. Whether CLI default behavior is preserved without digest flags.
7. Whether CLI error handling is appropriate when digest packaging fails after
   report generation.
8. Whether tests cover the important behavior and safety boundaries.
9. Whether docs and stdout copy use local observed configured-source-set wording
   without broad source coverage claims.
10. Whether `.gitignore` prevents committing generated digest artifacts.

## Next-Stage Plan If This Review Passes

1. Run a final git status/diff sanity check and ensure no generated data,
   reports, `.eml` files, secrets, venv files, build artifacts, or CodeGraph DB
   files are staged.
2. Stage only intended Stage 11 files.
3. Commit Stage 11 with a concise message such as
   `Add local digest packaging for reports`.
4. Push `main` to the configured GitHub remote. If direct `github.com` routing
   is unstable again, use a temporary `http.curloptResolve` override as in the
   previous successful push.
5. Report commit hash, push result, Claude review result, and verification
   summary.
6. Prepare Stage 12 plan for a compliant public-source-pack expansion and
   source-health review workflow. Stage 12 should improve daily fashion source
   coverage using allowed RSS/RSSHub/GDELT/public-page configuration and
   diagnostics only; it should not add social scraping, account automation, or
   platform extraction.

## Response Format

Please return one of:

- `APPROVED: no blocking issues; may commit/push.`
- `BLOCKED: list Critical/Important findings with file paths and suggested fixes.`

Also include any minor non-blocking notes separately.

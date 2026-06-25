# Stage 199 Release Review Prompt

Review the Stage 199 release candidate in `/home/ubuntu/fashion-radar`.

Stage goal: add aggregate match-evidence summaries to daily entity reports,
using existing accepted deterministic matcher rows while keeping aliases,
context terms, item ids, normalized URLs, raw reasons, and per-row matcher
explanations internal.

Changed scope:

- `src/fashion_radar/models/report.py`
- `src/fashion_radar/reports.py`
- `tests/test_reports.py`
- `tests/test_cli.py`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `docs/scoring.md`
- `CHANGELOG.md`
- Stage 199 plan/review artifacts under `docs/reviews/` and
  `docs/superpowers/plans/`

Release verification already run locally:

- `git diff --check`
- `UV_NO_CONFIG=1 uv lock --check`
- `git diff --exit-code -- uv.lock pyproject.toml`
- `rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock`
- `UV_NO_CONFIG=1 uv sync --locked --dev`
- `UV_NO_CONFIG=1 uv sync --locked --dev --check`
- `uv --no-config run --frozen ruff check .`
- `uv --no-config run --frozen ruff format --check .`
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
- `uv --no-config build --out-dir "$tmp_build"`
- `uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"`
- `uv --no-config run --frozen pytest tests/ -q --tb=short`
- token scan:
  `rg -n "ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+" --glob '!uv.lock' --glob '!dist/**' --glob '!build/**' .`
- review artifact hygiene scan for interactive chatter, ANSI sequences, shell
  transcripts, write-status lines, and failed-tool markers under
  `docs/reviews/*stage-199*.md`

Please check:

1. The final diff is scoped to Stage 199 and does not modify source packs,
   scraping/social connectors, imported/community/external-tool command
   behavior, scoring formulas, candidate discovery, trends, or heat movers.
2. The release verification set is sufficient and the recorded command results
   are plausible for the current diff.
3. Review artifacts are coherent and do not contain live tool chatter, partial
   stubs, ANSI control characters, duplicated verdicts, or hidden command logs.
4. `uv.lock` and `pyproject.toml` are unchanged and the lockfile is mirror-free.
5. The implementation and docs keep match evidence aggregate-only and do not
   imply demand proof, popularity ranking, source ranking, source-set
   completeness, platform coverage verification, scraping/crawling/browser
   automation, login/cookie/token handling, or compliance-review product
   features.
6. The first-run smoke and CLI contract checks are release-appropriate.
7. No secrets, local reports/databases, SQLite sidecars, build archives, temp
   build directories, or CodeGraph DB files are staged or likely to be committed.

Return findings as:

- Critical: must fix before commit/push.
- Important: should fix before commit/push.
- Minor: optional follow-up.

If there are no Critical or Important findings, say that clearly.

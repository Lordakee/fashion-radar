# Claude Code Stage 12 Code Review Prompt

Please review the current Stage 12 code, tests, configs, and docs before GitHub
push. Do not edit files, do not commit, do not call the network, do not run
collectors, do not create config/data/report directories, do not open SQLite,
and do not execute platform/social tooling.

Project: `/home/ubuntu/fashion-radar`

Use maximum reasoning effort. The invoking command should be:

```bash
claude -p --effort max --allowedTools=Read,Grep,Glob < docs/reviews/claude-code-stage-12-code-review-prompt.md
```

## Stage 12 Objective

Improve daily fashion information quality by adding local source-pack
diagnostics and expanding the public RSS/GDELT starter pack with bounded GDELT
coverage lanes. The feature should help users catch weak local source-pack
configuration before collection.

Stage 12 is not a product-facing compliance review, audit workflow, safety
workflow, or approval UI.

## Plan Gate

Plan/design files:

- `docs/superpowers/specs/2026-06-12-stage-12-source-pack-quality-design.md`
- `docs/superpowers/plans/2026-06-12-stage-12-source-pack-quality-plan.md`
- `docs/reviews/claude-code-stage-12-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-12-plan-review.md`
- `docs/reviews/claude-code-stage-12-plan-rereview-prompt.md`
- `docs/reviews/claude-code-stage-12-plan-rereview.md`
- `docs/reviews/claude-code-stage-12-plan-rereview-2-prompt.md`
- `docs/reviews/claude-code-stage-12-plan-rereview-2.md`

Plan review result:

- First Claude Code plan review: `Not approved`; Critical none; Important
  findings required stronger read-only boundary tests and a fuller explicit
  out-of-scope list.
- Second Claude Code plan review: `Not approved`; Critical none; remaining
  Important findings required installed-wheel smoke to run from an isolated
  working directory and verify explicit/default config/data/report paths plus
  SQLite, collector, report, digest, and workflow artifacts were not created.
- Third Claude Code plan review: `Approved for Stage 12 implementation`;
  Critical none; Important none.

## Changed/New Files To Review

- `CHANGELOG.md`
- `README.md`
- `configs/source-packs/fashion-public.example.yaml`
- `docs/architecture.md`
- `docs/source-pack-quality.md`
- `docs/source-packs.md`
- `docs/superpowers/specs/2026-06-12-stage-12-source-pack-quality-design.md`
- `docs/superpowers/plans/2026-06-12-stage-12-source-pack-quality-plan.md`
- `docs/reviews/claude-code-stage-12-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-12-plan-review.md`
- `docs/reviews/claude-code-stage-12-plan-rereview-prompt.md`
- `docs/reviews/claude-code-stage-12-plan-rereview.md`
- `docs/reviews/claude-code-stage-12-plan-rereview-2-prompt.md`
- `docs/reviews/claude-code-stage-12-plan-rereview-2.md`
- `docs/reviews/claude-code-stage-12-code-review-prompt.md`
- `src/fashion_radar/source_packs.py`
- `src/fashion_radar/cli.py`
- `tests/test_source_packs.py`
- `tests/test_config.py`
- `tests/test_cli.py`

## Implemented Behavior Summary

- Added `fashion_radar.source_packs`, a pure local source-pack lint module.
- Added `SourcePackFindingSeverity`, `SourcePackFinding`, and
  `SourcePackLintResult` typed models.
- Added `lint_source_pack(path)`:
  - reads raw YAML before typed validation so omitted fields such as `weight`
    can be diagnosed;
  - validates with the existing `load_source_config()` path;
  - returns structured findings instead of raising for invalid config;
  - computes source, enabled, disabled, type, and tag counts;
  - does not fetch sources, call collectors, open SQLite, or create files.
- Added normalization helpers for source names, RSS/RSSHub targets, and GDELT
  queries.
- Added findings:
  - `invalid_config`
  - `duplicate_source_name`
  - `empty_enabled_pack`
  - `duplicate_source_target`
  - `duplicate_gdelt_query`
  - `missing_tags`
  - `disabled_source`
  - `implicit_weight`
  - `article_extraction_enabled`
- Duplicate source-name, URL, and query findings report every member of a
  collision group.
- Added deterministic table output via `render_source_pack_lint_table()`.
- Added `fashion-radar source-pack-lint PATH [--format table|json] [--strict]`.
  Default behavior exits non-zero on errors only; `--strict` also exits non-zero
  on warnings.
- Added CLI tests proving the command does not create default or explicit
  config/data/report directories, `fashion-radar.sqlite`, `*.sqlite*`,
  collector artifacts, report artifacts, digest artifacts, or workflow
  artifacts.
- Expanded `configs/source-packs/fashion-public.example.yaml` from 10 to 16
  sources:
  - 6 RSS sources unchanged;
  - 10 bounded GDELT lanes;
  - new GDELT lanes for runway/fashion week, designer-brand momentum,
    retail/resale, footwear/sneakers, creative-director moves, and
    beauty/fashion crossover;
  - public-pack RSS article extraction remains disabled.
- Added `docs/source-pack-quality.md` and updated README/source-pack/architecture
  docs and changelog.

## Explicit Out Of Scope

Stage 12 must not add or document:

- Instagram, TikTok, X/Twitter, Xiaohongshu/RedNote, Reddit, Pinterest, or
  other platform connectors
- web scraping, crawler development, browser automation, Playwright, Selenium,
  MCP platform scraping servers, account automation, or platform search
- login cookies, account/session files, browser profiles, tokens, credentials,
  proxies, proxy pools, fingerprint evasion, CAPTCHA bypass, rate-limit bypass,
  access-control bypass, or paywall bypass
- official or unofficial social platform APIs
- instructions for obtaining platform exports from social platforms
- raw comments, full post bodies, DMs, private data, account IDs, follower
  lists, images, videos, media downloading, or reposting
- Google News RSS or any new source type
- complete source coverage, platform-wide coverage, market-wide trend proof,
  verified demand outside the configured source set, real-time social
  monitoring, or top social trends
- LLM scoring, embeddings, vector databases, image recognition, or paid service
  requirements
- DB migrations, source-health schema changes, collector changes, dashboard
  changes, report semantics changes, or network calls
- a product-facing compliance review, audit workflow, safety workflow, approval
  UI, or policy checklist

## Verification Already Run

- `.venv/bin/python -m pytest tests/test_source_packs.py -q`
  - `10 passed`
- `.venv/bin/python -m pytest tests/test_cli.py -k "source_pack_lint" -q`
  - `7 passed, 47 deselected`
- `.venv/bin/python -m pytest tests/test_config.py::test_public_fashion_source_pack_loads tests/test_source_packs.py::test_lint_repository_public_pack_has_no_errors -q`
  - `2 passed`
- `.venv/bin/python -m pytest tests/test_source_packs.py tests/test_config.py tests/test_cli.py -k "source_pack or public_fashion_source_pack" -q`
  - `18 passed, 63 deselected`
- `.venv/bin/python -m pytest -q`
  - `278 passed`
- `.venv/bin/python -m ruff check .`
  - passed
- `.venv/bin/python -m ruff format --check .`
  - `72 files already formatted`
- `git diff --check`
  - passed
- `uv lock --check --default-index https://pypi.org/simple`
  - passed; `uv.lock` unchanged
- `uv sync --locked --dev --check --default-index https://pypi.org/simple`
  - passed; would make no changes
- `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check`
  - passed; mirror install check would make no changes
- `uv build --out-dir /tmp/fashion-radar-dist-stage12`
  - built wheel and sdist successfully
- Installed-wheel smoke:
  - created a temporary venv;
  - installed the built wheel with
    `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple`;
  - ran `fashion-radar source-pack-lint --help`;
  - ran `fashion-radar source-pack-lint <tmp source pack> --format json` from
    an isolated working directory with explicit
    `FASHION_RADAR_CONFIG_DIR`, `FASHION_RADAR_DATA_DIR`, and
    `FASHION_RADAR_REPORTS_DIR`;
  - verified no default `config`, `data`, or `reports` directories were created;
  - verified no explicit config/data/report directories were created;
  - verified no `fashion-radar.sqlite`, `*.sqlite*`, collector artifacts, report
    artifacts, digest artifacts, or workflow artifacts were created;
  - verified JSON had `source_count == 16`, `type_counts == {"gdelt": 10, "rss": 6}`,
    and no findings.
- `codegraph status`
  - healthy; 85 files indexed; index up to date
- Wording guard:
  - `rg -n "complete social listening|platform-wide|market-wide|verified demand|top social trend|real-time social monitoring|scraper|crawler|cookie|CAPTCHA|fingerprint|proxy pool|login session" README.md docs/source-pack-quality.md docs/source-packs.md docs/architecture.md CHANGELOG.md`
  - no matches
- Secret/generated-file sanity:
  - token/private-key pattern scan found no token or private-key material in
    changed files
  - session/cookie scan matches only existing boundary/review documentation
    language
  - ignored local `.codegraph` and `dist/` artifacts exist but are not staged

## Review Questions

Please focus on:

1. Whether `source_packs.py` stays pure/local and does not reach into database,
   collector, dashboard, report, or network code.
2. Whether the lint result model and JSON shape are stable and useful.
3. Whether invalid configs returning `invalid_config` findings instead of
   raising is appropriate for CLI behavior.
4. Whether duplicate source names as errors, duplicate targets/queries as
   warnings, and missing tags as warnings are appropriate.
5. Whether URL/query/name normalization is deterministic and not likely to
   cause surprising false positives.
6. Whether `source-pack-lint` default/strict exit behavior is correct.
7. Whether tests sufficiently prove the command is read-only and does not
   create workflow artifacts.
8. Whether public pack expansion remains bounded to existing RSS/GDELT source
   types and keeps RSS article extraction disabled.
9. Whether docs avoid social/platform-wide/market-wide claims and do not frame
   this as a product-facing compliance/audit feature.
10. Whether any generated files, local data, secrets, cookies, or build artifacts
    are at risk of being committed.

## Next-Stage Plan If This Review Passes

1. Fix any Critical or Important Stage 12 review findings and re-review if
   needed.
2. Run a final `git status --short`, `git diff --check`, focused source-pack
   tests, full tests, ruff, and source-pack CLI smoke if any fixes were made.
3. Stage only intended Stage 12 files, excluding `.venv`, `.codegraph`, `dist`,
   build outputs, generated reports, SQLite files, cookies, tokens, and local
   account/session artifacts.
4. Commit Stage 12 with a concise message such as
   `Add source-pack quality diagnostics`.
5. Push `main` to the configured GitHub remote using a temporary askpass token
   injection and token-free remote URL. If direct GitHub routing is unstable,
   use the previously successful temporary `http.curloptResolve` override.
6. Report commit hash, push result, Claude review result, and verification
   summary.
7. Prepare a future Stage 13 plan for allowed, free-first source quality
   improvements only. Recommended Stage 13 direction: source-pack templates for
   user-curated local imports and official/public source lists, plus docs for
   manually adding social observations through local CSV/JSON imports. Do not
   add social scraping, account automation, browser automation, platform export
   acquisition instructions, unofficial social APIs, or network bypass logic.

## Response Format

Please return one of:

- `APPROVED: no blocking issues; may commit/push.`
- `BLOCKED: list Critical/Important findings with file paths and suggested fixes.`

Also include any minor non-blocking notes separately.

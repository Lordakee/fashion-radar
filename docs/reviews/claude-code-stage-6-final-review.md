# Claude Code Stage 6 Final Review

Base: `3d97313 feat: add stage 5 cli and dashboard workflow` plus uncommitted
Stage 6 working tree.

## Verification

Claude Code independently reran and verified:

- `pytest`: 115 passed.
- `ruff check`: clean.
- `ruff format --check`: 56 files formatted.
- YAML parse: CI, issue templates, and all root/packaged config examples parse.
- Root `configs/*.example.yaml` files are byte-identical to packaged
  `src/fashion_radar/templates/configs/*`.
- `git diff --check`: clean.
- `uv.lock` mirror URL scan: no matches.
- Tracked files under `reports/` and `data/` are README-only.
- `.codegraph/*.db*`, `.venv`, caches, pid/sock/log files are ignored; only
  `.codegraph/.gitignore` is tracked.
- `.mcp.json` uses relative `"."`; `.claude/settings.json` is a permission
  allowlist only; no secrets or `/home/ubuntu` absolute paths were found in
  tracked tooling/docs.

## Cross-Checks

- **Scoring:** `docs/scoring.md` matches `scoring.py`, including distinct
  `(entity_name, entity_type, item_id)` mentions, highest-confidence per item,
  `source_weight * confidence`, window bounds, score components, label
  precedence, stable first-seen, omitted zero-current entities, and duplicate
  `stable` fallback.
- **Retention:** `docs/data-retention.md` matches pruning behavior: cutoff is
  `as_of - retention_days`, `items` are pruned by `collected_at`,
  `item_entities` rows are deleted explicitly first, and
  `collector_runs`/`source_health`/`entity_first_seen`/reports are not pruned.
- **Dashboard:** docs match implementation: SELECT-only query helpers,
  `127.0.0.1:8501` default, no auth, no import/refresh collection or network
  work, and mention-count tabs rather than heat ranking.
- **Scope:** README, `source-boundaries.md`, `architecture.md`,
  `CONTRIBUTING.md`, config headers, and issue templates consistently limit
  v0.1.0 to RSS/RSSHub/GDELT and exclude scraping, cookies, proxy pools,
  CAPTCHA/paywall bypass, and private data.
- **CI/templates/checklist:** required GitHub-readiness surface is covered.

## Critical

None.

## Important

None.

## Minor

1. `CHANGELOG.md` keeps everything under `[Unreleased]` while `pyproject.toml`
   already has `version = "0.1.0"`. This is valid before tagging, but readers
   may expect a `[0.1.0]` heading after release.
2. `.github/ISSUE_TEMPLATE/` has no `config.yml`, so blank issues remain
   enabled and can bypass structured templates.
3. `SECURITY.md` and `CODE_OF_CONDUCT.md` defer actual contact/moderation path
   to before public launch. This is honest and acceptable for local prep, but
   should be resolved before the repo is public.

## Verdict

**Approved for Stage 6 commit and GitHub upload preparation.**

The Minor items are optional and do not block committing Stage 6.

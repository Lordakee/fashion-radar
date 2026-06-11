# Claude Code Stage 6 Final Review Prompt

You are Claude Code reviewing Fashion Radar after Stage 6 GitHub-readiness
implementation and before committing/publishing preparation.

Repository: `/home/ubuntu/fashion-radar`

Base commit:

- `3d97313 feat: add stage 5 cli and dashboard workflow`

Reviewed range:

- uncommitted Stage 6 working tree after `3d97313`

Stage 6 goal:

- Make the repository understandable and safe to publish to GitHub.
- Stay scoped to docs, CI/package smoke, repository hygiene, GitHub community
  files, and upload checklist.
- Do not implement social-platform scraping/connectors.
- User controls remote creation, pushing, PyPI publishing, and artifact uploads.

New or updated Stage 6 files include:

- `README.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `CODE_OF_CONDUCT.md`
- `CHANGELOG.md`
- `.github/workflows/ci.yml`
- `.github/ISSUE_TEMPLATE/bug_report.yml`
- `.github/ISSUE_TEMPLATE/feature_request.yml`
- `.github/pull_request_template.md`
- `.env.example`
- `configs/sources.example.yaml`
- `configs/entities.example.yaml`
- `configs/scoring.example.yaml`
- `src/fashion_radar/templates/configs/sources.example.yaml`
- `src/fashion_radar/templates/configs/entities.example.yaml`
- `src/fashion_radar/templates/configs/scoring.example.yaml`
- `data/README.md`
- `reports/README.md`
- `docs/architecture.md`
- `docs/scoring.md`
- `docs/data-retention.md`
- `docs/dashboard.md`
- `docs/github-upload-checklist.md`
- `docs/source-boundaries.md`
- `docs/dependency-mirrors.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/superpowers/plans/2026-06-11-fashion-radar-implementation-plan.md`
- `docs/superpowers/specs/2026-06-11-fashion-radar-design.md`
- Stage 6 plan review records under `docs/reviews/`

Stage 6 requirements to verify:

1. README has public quickstart, install, mirror-safe commands, init/doctor,
   collect/match/report/run/dashboard workflow, and dashboard extra note.
2. Docs are honest that v0.1.0 core sources are RSS/RSSHub-compatible public
   feeds and GDELT only. Instagram/TikTok/X/Xiaohongshu scraping, login cookies,
   proxy/account pools, CAPTCHA bypass, paywall bypass, private data
   collection, and full-platform coverage are out of scope.
3. Scoring docs match implementation: distinct `(entity_name, entity_type,
   item_id)` mentions, highest confidence per item, `source_weight *
   confidence`, current/baseline windows by `items.collected_at`, components,
   labels, stable first-seen, omitted zero-current entities, and known limits.
4. Data-retention docs match implementation: `clean-old-data` prunes by
   `items.collected_at`, deletes `item_entities` explicitly, does not prune
   `collector_runs`, `source_health`, `entity_first_seen`, or report files, and
   documents `last_seen_at` may refer to pruned history.
5. Dashboard docs match implementation: read-only, local-only default,
   `127.0.0.1:8501`, no auth if host changed, no collect/match/report/network
   work on refresh/import, mention-count tabs not heat ranking.
6. Config examples and packaged templates stay synchronized and parse as valid
   YAML.
7. CI covers locked install, ruff, format, tests, wheel build, installed CLI
   smoke, installed `daily_report.md` resource smoke, and dashboard extra import
   smoke.
8. GitHub issue/PR templates ask for useful diagnostics and prevent secrets,
   cookies, session files, private data, local DBs, generated reports, and
   excluded scraping requests.
9. Repository hygiene docs/checklist cover `.venv`, caches, generated reports,
   SQLite DBs/sidecars, `dist`, `build`, `.codegraph` DB files, cookies,
   browser profiles, account/session files, and mirror URLs in `uv.lock`.
10. No generated runtime data, build artifacts, secrets, cookies, local DBs, or
    `.codegraph` database files are staged/tracked.

Fresh local verification already run:

```text
.venv/bin/python -m pytest -q
115 passed in 3.42s

.venv/bin/python -m ruff check .
All checks passed!

.venv/bin/python -m ruff format --check .
56 files already formatted

uv lock --check
Resolved 84 packages

uv sync --locked --dev --check
Would make no changes

UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
Would make no changes

uv build --out-dir /tmp/fashion-radar-dist-stage6
wheel contains:
- fashion_radar/templates/daily_report.md
- fashion_radar/templates/configs/sources.example.yaml
- fashion_radar/templates/configs/entities.example.yaml
- fashion_radar/templates/configs/scoring.example.yaml

Installed wheel via Tsinghua mirror:
- fashion-radar --help works
- importlib.resources loads daily_report.md

Dashboard extra smoke via uv pip and Tsinghua mirror:
- installs wheel[dashboard] in a temp venv
- imports fashion_radar.dashboard.app and fashion_radar.dashboard.queries
```

Additional checks already run:

```text
YAML parse check for CI, issue templates, root configs, and packaged configs: ok
uv.lock mirror URL search: no matches
git diff --check: no output
CodeGraph sync/status: index up to date
```

Please review:

- Are there Critical, Important, or Minor issues to fix before committing Stage
  6?
- Is the repo GitHub-ready except for user-controlled remote creation/push?
- Did Stage 6 stay inside docs/CI/GitHub-readiness scope?

Return findings ordered by severity:

- Critical
- Important
- Minor

End with one of:

- Approved for Stage 6 commit and GitHub upload preparation
- Approved after fixes
- Do not proceed

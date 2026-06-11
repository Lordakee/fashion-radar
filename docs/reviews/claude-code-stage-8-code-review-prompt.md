# Claude Code Stage 8 Code Review Prompt

Review the Stage 8 implementation for Fashion Radar.

Repo: `/home/ubuntu/fashion-radar`
Base SHA: `346ab9118cd55218a42c5c849f4b15f745278826`
Head SHA: `ef67a2b91527a2bd3b375e836b22b4732c5ea142`

User rules:

- This review must use `--effort max`.
- This is a code review. Do not edit files, run collectors, access social
  platforms, scrape/crawl websites, mutate user configs, or perform network
  source collection. Return review findings only.
- Fix Critical and Important findings before GitHub sync.
- Core workflow must remain free/local-first.
- Dependencies/install checks may use mirrors locally but must not write mirror
  URLs into `uv.lock`.

Stage 8 goal:

Add deterministic "Untracked Candidate Signals" so users can review observed
phrases that may warrant human review for brands, designers, products, bags,
shoes, and style terms already present in locally collected RSS/GDELT items,
without adding new source collection.

Implemented files:

- `src/fashion_radar/settings.py`
- `configs/scoring.example.yaml`
- `src/fashion_radar/templates/configs/scoring.example.yaml`
- `configs/sources.example.yaml`
- `src/fashion_radar/templates/configs/sources.example.yaml`
- `src/fashion_radar/discovery/__init__.py`
- `src/fashion_radar/discovery/candidates.py`
- `src/fashion_radar/models/report.py`
- `src/fashion_radar/models/__init__.py`
- `src/fashion_radar/reports.py`
- `src/fashion_radar/templates/daily_report.md`
- `src/fashion_radar/workflows.py`
- `src/fashion_radar/cli.py`
- `src/fashion_radar/dashboard/queries.py`
- `src/fashion_radar/dashboard/app.py`
- `tests/test_candidate_extraction.py`
- `tests/test_candidate_scoring.py`
- `tests/test_config.py`
- `tests/test_reports.py`
- `tests/test_cli.py`
- `tests/test_dashboard.py`
- `docs/candidate-discovery.md`
- `README.md`
- `docs/architecture.md`
- `docs/scoring.md`
- `docs/dashboard.md`
- `docs/source-boundaries.md`
- `CHANGELOG.md`
- `docs/superpowers/plans/2026-06-11-fashion-radar-implementation-plan.md`

Implementation summary:

- Added optional `candidate_discovery` settings under `scoring.yaml`.
- Added deterministic candidate extraction and scoring in
  `fashion_radar.discovery.candidates`.
- Candidate discovery reads only existing local SQLite `items` and
  `item_entities` rows.
- Stored known-entity filtering uses
  `item_entities.confidence >= scoring.min_match_confidence` and does not
  require `reason == "accepted"`.
- Candidate labels are `new_candidate`, `rising_candidate`, and `review`.
- Reports now include a public-safe `candidates` field and Markdown
  `Untracked Candidate Signals` section.
- `fashion-radar run` and `fashion-radar report` pass loaded `entities.yaml`
  into candidate discovery.
- Added a read-only `fashion-radar candidates` command with table and JSON
  output. It checks DB existence before engine creation, uses read-only SQLite
  URI for existing DBs, and does not call `initialize_schema()`.
- Dashboard adds a `Candidate Signals` tab that reads latest report JSON only.
  It does not recompute candidates or touch SQLite for candidate rows.
- Docs describe candidate signals as observed phrases from configured sources
  that need review.

Source/safety boundaries:

- No new source type or collector.
- No social-platform access.
- No browser automation.
- No account/session/cookie handling.
- No proxy/account pools.
- No CAPTCHA/access-control bypass.
- No paid API requirement.
- No LLM, embedding, vector database, or image recognition dependency.
- No automatic mutation of `entities.yaml`.
- Candidate outputs avoid claims that phrases are externally ranked or
  validated entities.

Verification already run:

```text
.venv/bin/python -m pytest -q
161 passed in 4.56s

.venv/bin/python -m ruff check .
All checks passed!

.venv/bin/python -m ruff format --check .
62 files already formatted

uv lock --check
Resolved 84 packages in 52ms

uv sync --locked --dev --check
Checked 36 packages; would make no changes

UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
Checked 36 packages; would make no changes

uv build --out-dir /tmp/fashion-radar-dist-stage8
Successfully built sdist and wheel.

Installed wheel smoke:
fashion-radar candidates --help printed command help.

Resource smoke:
installed-resource-ok

Dashboard helper smoke:
parse_args latest_candidate_rows

Template sync:
configs/scoring.example.yaml matches packaged scoring template.
configs/sources.example.yaml matches packaged sources template.

Claim-language grep:
No user-facing matches for viral/global/market-wide/confirmed-brand/product
claims. Test matches are only negative assertions.

CodeGraph:
75 files indexed, 871 nodes, 2296 edges.
```

Please review:

1. Does implementation match the approved Stage 8 design and plan?
2. Are candidate extraction, filtering, scoring, and label thresholds
   deterministic and coherent?
3. Does `run`/`report` correctly pass `EntityConfig` into candidate discovery?
4. Is `fashion-radar candidates` genuinely read-only for missing and existing
   databases?
5. Are candidate JSON/Markdown/dashboard outputs public-safe and free of
   internal DB/matcher/extraction fields?
6. Does dashboard candidate behavior remain read-only and usable when DB is
   absent but reports exist?
7. Are docs and language boundaries safe for GitHub publication?
8. Are there missing tests, regressions, or data integrity risks?

Return findings by severity:

- Critical
- Important
- Minor

End with exactly one of:

- Approved for Stage 8 commit and GitHub sync
- Approved after fixes
- Do not proceed

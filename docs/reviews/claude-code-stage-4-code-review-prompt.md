# Claude Code Stage 4 Code Review And Stage 5 Plan Review Prompt

You are Claude Code reviewing Fashion Radar after Stage 4 implementation and
before Stage 5 implementation.

Repository: `/home/ubuntu/fashion-radar`

Base commit under review:

- `59785d5 docs: record stage 4 plan gate`

Reviewed range:

- uncommitted working tree after `59785d5`

Stage 4 requirements:

- Compute deterministic entity heat metrics from stored Stage 3 data.
- Generate Markdown and JSON reports from a vetted Pydantic report model.
- Bump SQLite schema version from `2` to `3`.
- Add `items.source_weight` and `items.collected_at`.
- Migrate v1/v2 databases to v3 without dropping existing items.
- Store source weight snapshots during collection/upsert.
- Preserve first-seen `collected_at` on duplicate normalized URL re-upsert.
- Use explicit `as_of` in scoring/reporting tests and functions.
- Use `items.collected_at` for current/baseline windows, not `published_at`.
- Count mentions as distinct `(entity_name, item_id)` pairs.
- Filter matches by `min_match_confidence`.
- Weighted contribution is `items.source_weight * max(confidence)`.
- Compute heat score exactly from configured weighted mention coefficient,
  scaled growth bonus, source-diversity bonus, and flat high-weight-source
  bonus.
- Apply deterministic labels in the approved order: new, hot, rising, cooling,
  stable.
- Sort deterministically by heat score desc, current mentions desc, distinct
  sources desc, entity name asc.
- Report representative items with source name, source URL, publication time,
  title, and short summary only.
- Report source health and recent failed/skipped collector runs.
- Do not leak `content_hash`, normalized URL, full article text, or raw matcher
  rows into Markdown or JSON.
- Use a packaged Markdown template at
  `src/fashion_radar/templates/daily_report.md`.
- Do not add Jinja2 in Stage 4.

Implementation summary:

- `src/fashion_radar/db/schema.py`
  - `SCHEMA_VERSION = 3`.
  - `items` now has `source_weight` and `collected_at`.
  - migration chain handles v1 -> v2 -> v3 and v2 -> v3.
- `src/fashion_radar/db/repositories.py`
  - `ItemRepository.upsert_item()` accepts `source_weight` and `collected_at`.
  - insert stores both; update preserves `collected_at`.
- `src/fashion_radar/collectors/runner.py`
  - `collect_sources()` passes `source.weight` and the runner `started_at` into
    item upsert.
- `src/fashion_radar/settings.py`
  - `ScoringSettings` now includes explicit Stage 4 window, threshold, label,
    and confidence settings.
- `configs/scoring.example.yaml` and packaged scoring template are synchronized.
- `src/fashion_radar/scoring.py`
  - new deterministic scoring API: `score_entities(engine, scoring, as_of)`.
- `src/fashion_radar/models/report.py`
  - new vetted Pydantic report models.
- `src/fashion_radar/reports.py`
  - new daily report builder and Markdown/JSON renderers.
- `src/fashion_radar/templates/daily_report.md`
  - packaged Markdown report template.
- Tests added/updated:
  - `tests/test_db.py`
  - `tests/test_collectors_runner.py`
  - `tests/test_config.py`
  - `tests/test_scoring.py`
  - `tests/test_reports.py`

Fresh local verification already run:

```text
.venv/bin/python -m pytest -q
96 passed in 2.21s

.venv/bin/python -m ruff check .
All checks passed!

.venv/bin/python -m ruff format --check .
50 files already formatted

uv lock --check
Resolved 84 packages

uv sync --locked --dev --check
Would make no changes

UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
Would make no changes

uv build --out-dir /tmp/fashion-radar-dist-stage4
Successfully built /tmp/fashion-radar-dist-stage4/fashion_radar-0.1.0.tar.gz
Successfully built /tmp/fashion-radar-dist-stage4/fashion_radar-0.1.0-py3-none-any.whl

Clean temporary venv wheel install via Tsinghua mirror:
fashion-radar --help displayed init and doctor commands
importlib.resources loaded fashion_radar.templates/daily_report.md successfully
```

CodeGraph status after sync:

```text
Files indexed: 59
Total nodes: 599
Total edges: 1501
```

Stage 5 plan to review:

- See `docs/superpowers/plans/2026-06-11-fashion-radar-implementation-plan.md`
  section `## Stage 5: CLI And Dashboard`.
- The plan was just updated to specify CLI workflow contracts, optional
  dashboard dependency handling, read-only localhost dashboard behavior,
  `clean-old-data`, and TDD tasks.

Please review:

1. Does Stage 4 implementation satisfy the approved Stage 4 plan?
2. Are there correctness bugs in scoring windows, mention counting, confidence
   filtering, formula components, labels, or deterministic ranking?
3. Are there migration/data-integrity risks in v1/v2 -> v3 schema handling?
4. Is the `source_weight`/`collected_at` upsert behavior correct for historical
   determinism?
5. Are report serialization boundaries strict enough to prevent internal fields
   or full content leakage?
6. Are tests meaningful and sufficient for this stage?
7. Is the updated Stage 5 plan concrete, safe, and sufficient to begin Stage 5?
8. Are there issues to fix before committing Stage 4 or starting Stage 5?

Return findings ordered by severity:

- Critical
- Important
- Minor

End with one of:

- Approved for Stage 4 commit and Stage 5 implementation
- Approved after fixes
- Do not proceed

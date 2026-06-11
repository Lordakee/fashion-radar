# Claude Code Stage 5 Code Review And Stage 6 Plan Review Prompt

You are Claude Code reviewing Fashion Radar after Stage 5 implementation and
before Stage 6 documentation/packaging work.

Repository: `/home/ubuntu/fashion-radar`

Base commit under review:

- `103ed10 feat: add stage 4 scoring and reports`

Reviewed range:

- uncommitted working tree after `103ed10`

Stage 5 requirements:

- Provide usable local CLI workflow commands:
  - `collect`
  - `match`
  - `report`
  - `run`
  - `dashboard`
  - `clean-old-data`
- Keep core CLI commands usable without installing the optional dashboard extra.
- Keep dashboard dependencies (`streamlit`, `pandas`) optional under the
  `dashboard` extra.
- Dashboard command must lazy-check Streamlit and provide a clear install hint
  when missing.
- Dashboard must bind to `127.0.0.1` by default.
- Dashboard import/refresh must not trigger collection, matching, or network
  access.
- Stage 5 must resolve Stage 4 review findings:
  - Do not rely on SQLite FK cascade for pruning matcher rows.
  - Persist stable entity first-seen independent of retained item history.
- Bump lightweight schema version from `3` to `4`.
- Add `entity_first_seen(entity_name, entity_type, first_seen_at, last_seen_at)`.
- `match_stored_items()` must persist stable first/last seen from accepted
  matches using the item's `collected_at`.
- `score_entities()` must prefer stable first-seen for `new` label decisions,
  falling back to retained item history only when absent.
- `clean-old-data` must prune by `items.collected_at`, explicitly delete
  `item_entities` rows before deleting items, support dry-run behavior, and not
  delete collector run/source health history.
- `run` must execute `collect -> match -> report` serially without parallel DB
  writers.

Implementation summary:

- `src/fashion_radar/db/schema.py`
  - `SCHEMA_VERSION = 4`.
  - added `entity_first_seen`.
  - migration chain now handles v1 -> v2 -> v3 -> v4.
- `src/fashion_radar/db/repositories.py`
  - `replace_item_matches()` updates stable first/last seen.
  - added `get_entity_first_seen()`.
  - added `prune_items_older_than()` with explicit matcher-row deletion and
    dry-run counts.
  - added `list_items_for_matching()`.
- `src/fashion_radar/scoring.py`
  - scoring loads stable first-seen and uses `(entity_name, entity_type, item_id)`
    for distinct mention keys.
- `src/fashion_radar/workflows.py`
  - new workflow helpers for default DB path, collection, matching, report file
    writing, and cleanup.
- `src/fashion_radar/cli.py`
  - new commands: `collect`, `match`, `report`, `run`, `dashboard`,
    `clean-old-data`.
- `src/fashion_radar/dashboard/`
  - new read-only dashboard package with lazy Streamlit app and SQLite query
    helpers.
- Tests added/updated:
  - `tests/test_db.py`
  - `tests/test_scoring.py`
  - `tests/test_workflows.py`
  - `tests/test_cli.py`
  - `tests/test_dashboard.py`

Untracked new files in this review:

- `src/fashion_radar/workflows.py`
- `src/fashion_radar/dashboard/__init__.py`
- `src/fashion_radar/dashboard/app.py`
- `src/fashion_radar/dashboard/queries.py`
- `tests/test_workflows.py`
- `tests/test_dashboard.py`

Fresh local verification already run:

```text
.venv/bin/python -m pytest -q
115 passed in 3.61s

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

uv build --out-dir /tmp/fashion-radar-dist-stage5
Successfully built /tmp/fashion-radar-dist-stage5/fashion_radar-0.1.0.tar.gz
Successfully built /tmp/fashion-radar-dist-stage5/fashion_radar-0.1.0-py3-none-any.whl

Clean temporary venv wheel install via Tsinghua mirror:
fashion-radar --help worked
importlib.resources loaded fashion_radar.templates/daily_report.md
import fashion_radar.dashboard.queries worked without installing Streamlit
```

CodeGraph status after sync:

```text
Files indexed: 65
Total nodes: 719
Total edges: 1828
```

Stage 6 plan to review:

- See `docs/superpowers/plans/2026-06-11-fashion-radar-implementation-plan.md`
  section `## Stage 6: GitHub Packaging`.
- The plan now includes explicit GitHub publishing boundaries, mirror-friendly
  install docs without committing mirror URLs into `uv.lock`, source/platform
  boundary docs, repository hygiene checks, CI/package smoke checks, and final
  Claude Code review before upload.

Please review:

1. Does Stage 5 implementation satisfy the approved Stage 5 plan?
2. Are there correctness bugs in schema v4 migration, stable first-seen,
   pruning, matching, scoring, or report workflow integration?
3. Are CLI commands safe, deterministic, and tested enough for local MVP use?
4. Does dashboard remain read-only and local-only by default, with optional
   dependencies handled correctly?
5. Are source/compliance boundaries preserved, with no social scraping or
   account/cookie automation introduced?
6. Are tests meaningful and sufficient for this stage?
7. Is the updated Stage 6 plan concrete, safe, and sufficient to begin GitHub
   packaging docs?
8. Are there issues to fix before committing Stage 5 or starting Stage 6?

Return findings ordered by severity:

- Critical
- Important
- Minor

End with one of:

- Approved for Stage 5 commit and Stage 6 implementation
- Approved after fixes
- Do not proceed

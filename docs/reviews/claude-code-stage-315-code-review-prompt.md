Review the uncommitted Stage 315 implementation in `/home/ubuntu/fashion-radar`.

Stage goal:
- Add a read-only `fashion-radar row-one article-readiness` diagnostic command.
- It should explain whether the selected `sources.yaml`, generated ROW ONE site, saved local article sidecars, and current story source coverage are ready to produce local article bodies.
- It must not collect sources, fetch article pages, mutate SQLite, auto-edit config, change extractor internals, activate social/community connectors, add compliance-review features, change scoring, or change generated app/manifest/runtime JSON contracts.

Changed implementation files:
- `src/fashion_radar/row_one/article_readiness.py`
- `src/fashion_radar/cli.py`

Changed tests:
- `tests/test_row_one_article_readiness.py`
- `tests/test_row_one_cli.py`
- `tests/test_config.py`
- `tests/test_row_one_docs.py`
- `tests/test_first_run_docs.py`

Changed docs/planning/review artifacts:
- `README.md`
- `docs/row-one.md`
- `docs/first-run.md`
- `docs/superpowers/specs/2026-07-06-stage-315-row-one-article-readiness-design.md`
- `docs/superpowers/plans/2026-07-06-stage-315-row-one-article-readiness-plan.md`
- `docs/reviews/claude-code-stage-315-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-315-plan-review.md`
- `docs/reviews/claude-code-stage-315-plan-rereview-prompt.md`
- `docs/reviews/claude-code-stage-315-plan-rereview.md`
- `docs/reviews/claude-code-stage-315-plan-rereview-2-prompt.md`
- `docs/reviews/claude-code-stage-315-plan-rereview-2.md`
- `docs/reviews/claude-code-stage-315-code-review-prompt.md`

Verification already run locally:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_article_readiness.py \
  tests/test_row_one_cli.py \
  tests/test_row_one_docs.py \
  tests/test_first_run_docs.py \
  tests/test_config.py -q
```

Result: `136 passed`.

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
```

Result: both passed.

Smoke commands already run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one article-readiness \
  --config-dir configs \
  --site-dir reports/row-one/site
```

Result included:
- `Sources: 14/14 enabled`
- `ROW ONE article-enabled sources: 10`
- `Saved local articles: 17`
- `Saved local paragraphs: 136`
- `Story source coverage: 17/17 eligible`

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one article-readiness \
  --config-dir "$HOME/.config/fashion-radar" \
  --site-dir reports/row-one/site
```

Result included:
- `ROW ONE article-enabled sources: 0`
- `Story source coverage: 0/17 eligible`
- recommendation to enable `row_one_article.enabled: true in sources.yaml`

Specific review questions:
1. Does `article_readiness.py` correctly mirror the local-article source eligibility boundary, including exact `source_name` match first and non-network hostname fallback from story `source_url` to enabled source `url` / `seed_urls`?
2. Is the Typer command wiring correct, especially `--config-dir`, `--site-dir`, and `--json`?
3. Is the command truly read-only and free of network/source collection/extraction/SQLite mutation?
4. Is the JSON payload stable enough for automation while avoiding generated app contract changes?
5. Do the docs/tests accurately explain the old platformdirs config mismatch without implying config auto-migration, connector activation, or compliance-review functionality?
6. Are there missing tests or edge cases that create a real risk before this is committed?

Return findings first, ordered by severity. Mark any Critical or Important items that must be fixed before commit. If no Critical/Important findings exist, say that explicitly and list Minor/Nit findings separately.

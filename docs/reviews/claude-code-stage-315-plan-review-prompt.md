Review the Stage 315 design and implementation plan in `/home/ubuntu/fashion-radar`.

Files to review:
- `docs/superpowers/specs/2026-07-06-stage-315-row-one-article-readiness-design.md`
- `docs/superpowers/plans/2026-07-06-stage-315-row-one-article-readiness-plan.md`

Project goal:
- ROW ONE should become a useful daily fashion-news website that stores and presents organized article content locally.
- Stage 314 made saved local article sidecars observable.
- Local evidence shows `row-one build --config-dir configs ...` can produce nonzero sidecars, while the default platformdirs user config on this machine is an older source pack without `row_one_article.enabled`, so default `row-one build` can still report zero.

Stage 315 proposed goal:
- Add a read-only `row-one article-readiness` diagnostic command.
- It should explain whether selected `sources.yaml`, current generated site, and saved sidecars are ready to produce local article bodies.
- It should not auto-migrate or overwrite user config.
- It should not collect sources, fetch article pages, change extraction internals, change scoring, activate social/community connectors, add compliance-review features, or change generated app/manifest/runtime JSON contracts.

Technology and approach:
- Python dataclasses in `src/fashion_radar/row_one/article_readiness.py`.
- Typer command in `src/fashion_radar/cli.py`.
- Reuse Stage 314 `RowOneLocalArticleSiteMetrics`.
- Tests in `tests/test_row_one_article_readiness.py`, `tests/test_row_one_cli.py`, `tests/test_config.py`, `tests/test_row_one_docs.py`, and `tests/test_first_run_docs.py`.
- Docs in `README.md`, `docs/row-one.md`, and `docs/first-run.md`.

Please evaluate:
1. Is the Stage 315 scope technically sound and aligned with moving from “links only” toward locally organized article content?
2. Does the plan correctly address the observed default-config mismatch without unsafe config overwrites?
3. Are the proposed analyzer semantics sufficient and deterministic?
4. Are there missing tests or docs updates that would cause implementation failures?
5. Does the plan accidentally change generated ROW ONE app contracts or activate out-of-scope connectors?
6. Are there any blocking issues in the concrete code snippets, Typer option wiring, JSON payload shape, or test expectations?

Return findings first, ordered by severity. Mark any Critical or Important items that must be fixed before implementation. If no Critical/Important findings exist, say that explicitly and list Minor/Nit findings separately.

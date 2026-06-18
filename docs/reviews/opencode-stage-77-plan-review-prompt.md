# Stage 77 Plan Review Prompt

Review the Stage 77 design and implementation plan in
`/home/ubuntu/fashion-radar`:

- `docs/superpowers/specs/2026-06-18-stage-77-watchlist-local-sample-design.md`
- `docs/superpowers/plans/2026-06-18-stage-77-watchlist-local-sample-plan.md`

## Objective

Stage 77 adds an optional expanded local community-signal sample that exercises
the existing `configs/entity-packs/fashion-watchlist.example.yaml` pack across
designer brands, named products, categories, designers, celebrity style, and
trend terms.

Current user instruction for this node temporarily assigns review work to local
opencode with model `zhipuai-coding-plan/glm-5.2` and max variant. Treat that as
the active stage-local review rule; do not require this plan to switch back to
Claude Code or permanently rewrite `docs/REVIEW_PROTOCOL.md`.

## Architecture And Tech Stack

- Static CSV sample under `examples/`.
- Existing local-only CLI commands: `community-signal-lint`,
  `entity-pack-lint`, `import-signals`, `match`, `report`, and `trends`.
- pytest tests using temporary config/data/report directories and Typer
  `CliRunner`.
- Docs updates in README, first-run guide, entity-pack guide, and GitHub upload
  checklist.
- sdist package archive path guard.
- Python 3.11, uv, ruff, Markdown, YAML, CSV.

## Review Questions

1. Does the plan add useful local starter coverage for the original Fashion
   Radar goal without changing runtime behavior or default first-run smoke
   expectations?
2. Are the tests strong enough to prove the sample lints, loads, matches
   existing watchlist entities, imports into a temp DB, reports, and trends
   deterministically?
3. Are package archive/docs drift checks adequate if the new example is added?
4. Does the plan keep the boundary clear: no scraping, browser automation,
   platform APIs, account/session/cookie/token/proxy/CAPTCHA behavior, media
   downloads, monitoring, scheduling, source acquisition, demand proof,
   ranking, coverage verification, or compliance-review product feature?
5. Does the plan correctly avoid committing the pre-existing `uv.lock` mirror
   rewrite, given `AGENTS.md` says public `uv.lock` must remain free of
   mirror-bound URLs?
6. Does the plan correctly keep the optional sample out of the canonical
   `community-signal-profile` producer contract and existing two-row repository
   example assumptions?

Return findings grouped as Critical, Important, Minor, and Notes. Critical and
Important findings must be fixed before implementation.

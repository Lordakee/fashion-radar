# Stage 206 Release Review Prompt

Review the current Stage 206 working tree in `/home/ubuntu/fashion-radar` for
release readiness before commit and push.

Objective: confirm that Stage 206 is safe to upload to GitHub. The stage adds a
backward-compatible alias-level `requires_context` gate to deterministic entity
matching and applies it only to high-risk optional watchlist category aliases.

Baseline:

- `HEAD` / `origin/main`: `4af8179501e9992b4f780e5c5dc688988be39675`
- Planned commit message: `Stage 206: add explicit alias context gates`

Stage 206 implementation summary:

- `AliasDefinition` adds `requires_context: bool = False`.
- Runtime matcher requires entity `context_terms` for non-product aliases with
  `requires_context: true`.
- Products with `parent_brand` keep the existing parent-brand-or-context branch
  even if an alias also sets `requires_context: true`.
- Entity config validation rejects `requires_context: true` aliases when the
  entity has no `context_terms`.
- Entity-pack lint counts explicit context aliases as
  `context_gated_aliases`.
- Optional `configs/entity-packs/fashion-watchlist.example.yaml` now gates only:
  `Mary Jane Shoes`, `East-West Bags`, `Boat Shoes`, and `Suede Sneakers`.
- Docs/changelog/tests were updated; default starter config, source packs,
  collectors, scoring, reports, dashboard, DB schema, social/platform
  connectors, scraping, demand proof, platform coverage verification,
  dependency files, and compliance-review behavior should be unchanged.

Review artifacts already present:

- `docs/superpowers/plans/2026-06-25-stage-206-explicit-alias-context-gates-plan.md`
- `docs/reviews/opencode-stage-206-plan-review-prompt.md`
- `docs/reviews/opencode-stage-206-plan-review.md`
- `docs/reviews/opencode-stage-206-plan-rereview-prompt.md`
- `docs/reviews/opencode-stage-206-plan-rereview.md`
- `docs/reviews/opencode-stage-206-code-review-prompt.md`
- `docs/reviews/opencode-stage-206-code-review.md`

Code review result:

- OpenCode code review found no Critical or Important findings.
- Minor documentation clarity issues were handled after code review by adding
  product-with-`parent_brand` exception wording and clearer context-term wording.

Please review:

1. Are all changed files appropriate for Stage 206?
2. Are there any release blockers, missing verification gates, stale docs sample
   outputs, or review artifact hygiene problems?
3. Is there any secret, token, cookie, local SQLite DB, generated report,
   build artifact, CodeGraph DB, or local-only mirror/index material staged or
   likely to be committed?
4. Is the public `uv.lock` / `pyproject.toml` unchanged?
5. Is the scope still limited to deterministic matching quality and optional
   watchlist precision?
6. Are the code-review minor follow-ups handled sufficiently?

Expected final release verification commands before commit:

```bash
uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
git diff --exit-code -- uv.lock pyproject.toml
git diff --check
```

Return findings as Critical, Important, and Minor. If there are no Critical or
Important findings, say that clearly.

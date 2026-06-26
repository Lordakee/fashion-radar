# Stage 208 Release Review Prompt

Review the current working tree in `/home/ubuntu/fashion-radar` for Stage 208
release readiness.

Goal: release the Stage 208 message-only entity-pack lint improvement. The
existing advisory `contained_context_term_for_gated_alias` warning now names the
offending context term and gated alias in the free-text message.

Baseline:

- `HEAD` / `origin/main`: `219bf870ec5f4360e7e0fe7c9d707d92a5f407db`
- Stage 208 plan:
  `docs/superpowers/plans/2026-06-26-stage-208-context-term-warning-detail-plan.md`

Review artifacts:

- `docs/reviews/opencode-stage-208-plan-review.md`
- `docs/reviews/opencode-stage-208-plan-rereview.md`
- `docs/reviews/opencode-stage-208-plan-rerereview.md`
- `docs/reviews/opencode-stage-208-code-review.md`
- `docs/reviews/opencode-stage-208-code-rereview.md`

Changed implementation/docs files:

- `src/fashion_radar/entity_packs.py`
- `tests/test_entity_pack_lint.py`
- `docs/entity-pack-quality.md`
- `CHANGELOG.md`

Scope assertions:

- No matcher behavior changes.
- No `EntityPackFinding` / `EntityPackLintResult` schema changes.
- No config validation, source acquisition, scoring, reports, dashboard,
  connectors, scraping, demand proof, platform coverage verification,
  dependency files, lockfile, or compliance-review behavior changes.
- Review artifacts were cleaned so release hygiene does not include process
  chatter or partial capture stubs.

Full release verification already run successfully:

```text
uv --no-config run --frozen pytest
# 1515 passed

uv --no-config run --frozen ruff check .
# All checks passed

uv --no-config run --frozen ruff format --check .
# 148 files already formatted

uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
# Release hygiene checks passed

env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
# Resolved 85 packages

UV_NO_CONFIG=1 uv sync --locked --dev --check
# Would make no changes

uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
# First-run sample smoke passed

git diff --exit-code -- uv.lock pyproject.toml
git diff --check
# clean
```

Please review:

1. Is the stage safe to commit and push?
2. Are review artifacts coherent and release-hygiene friendly?
3. Did the implementation stay within the stated message-only lint scope?
4. Are tests/docs/changelog sufficient for the changed behavior?
5. Are there any unaddressed Critical or Important release blockers?

Return findings as Critical, Important, and Minor. If there are no Critical or
Important findings, say that clearly and state whether this is safe to commit
and push as `Stage 208: name contained context terms`.

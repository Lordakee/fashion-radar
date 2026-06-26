# Stage 207 Release Review Prompt

Review the current Stage 207 working tree in `/home/ubuntu/fashion-radar` for
release readiness before commit and push.

Objective: add advisory entity-pack lint coverage for context terms contained
in gated aliases, without changing matcher behavior or current watchlist sample
lint output.

Baseline:

- `HEAD` / `origin/main`: `ceb812221afce9263336a63011f5c3e81362241d`
- Planned commit message: `Stage 207: flag contained context terms`

Stage 207 implementation summary:

- `src/fashion_radar/entity_packs.py`
  - emits `contained_context_term_for_gated_alias` for
    `AliasGateKind.CONTEXT_REQUIRED` aliases when a context term is a proper
    normalized contiguous token subset of the alias key
  - keeps `self_context_term` exact-equality behavior intact
  - excludes exact equality, equal-length reordered phrases, unrelated context,
    and product parent-brand aliases
- `tests/test_entity_pack_lint.py`
  - covers single-token containment, multi-token containment, surrounding
    context negative case, equal-length reorder negative case, and exact
    equality non-double-warning
- `docs/entity-pack-quality.md`
  - documents the new finding as an advisory token-containment heuristic
- `CHANGELOG.md`
  - records the Stage 207 scope

Review artifacts already present:

- `docs/reviews/opencode-stage-207-plan-review-prompt.md`
- `docs/reviews/opencode-stage-207-plan-review.md`
- `docs/reviews/opencode-stage-207-plan-rereview-prompt.md`
- `docs/reviews/opencode-stage-207-plan-rereview.md`
- `docs/reviews/opencode-stage-207-code-review-prompt.md`
- `docs/reviews/opencode-stage-207-code-review.md`

OpenCode code review result:

- No Critical findings.
- No Important findings.
- One benign minor about mixed exact/subset warnings; no code change required.

Fresh verification already run before this release review:

```text
uv --no-config run --frozen pytest
# 1514 passed

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

Please verify:

1. The final diff is appropriate for Stage 207 and release-ready.
2. There are no stale docs sample counts or parity-test gaps.
3. There are no secrets, tokens, generated reports, SQLite DBs, build artifacts,
   local mirror/index material, or dependency/lockfile changes.
4. The scope remains linter-only and does not change matcher behavior, entity
   schema, config validation, source acquisition, scoring, reports, dashboard,
   social/platform connectors, scraping, demand proof, platform coverage
   verification, dependency files, or compliance-review behavior.
5. Review artifacts are coherent and complete.

Return Critical, Important, and Minor findings. If there are no Critical or
Important findings, say that clearly.

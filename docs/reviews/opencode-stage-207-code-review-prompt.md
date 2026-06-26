# Stage 207 Code Review Prompt

Review the current working tree in `/home/ubuntu/fashion-radar` for Stage 207.

Goal: add an advisory entity-pack lint warning for context terms that are
contained in a gated alias, without changing matcher behavior or the checked-in
watchlist lint sample output.

Baseline:

- `HEAD` / `origin/main`: `ceb812221afce9263336a63011f5c3e81362241d`
- Stage 207 plan:
  `docs/superpowers/plans/2026-06-26-stage-207-context-term-containment-lint-plan.md`
- Stage 207 plan rereview says I1 is resolved and no Critical or Important
  blockers remain.

Files changed in this stage:

- `src/fashion_radar/entity_packs.py`
- `tests/test_entity_pack_lint.py`
- `docs/entity-pack-quality.md`
- `CHANGELOG.md`
- `docs/reviews/opencode-stage-207-code-review-prompt.md`

Review focus:

1. Linter-only scope: no matcher, schema, config validation, source, scoring,
   report, dashboard, connector, scraping, demand proof, platform coverage,
   dependency, lockfile, or compliance-review behavior changes.
2. Correct warning semantics:
   - emit `contained_context_term_for_gated_alias` only for
     `AliasGateKind.CONTEXT_REQUIRED` aliases
   - detect proper normalized token containment such as `shoes` or `mary jane`
     inside `mary jane shoes`
   - do not warn for exact equality, equal-length reorder, unrelated
     surrounding context, or product parent-brand aliases
3. Determinism: context keys are sorted before warning emission.
4. Existing `self_context_term` exact-equality warning remains intact and does
   not double-warn for exact equality.
5. Watchlist lint sample output stays unchanged:
   `0 errors, 2 warnings, 71 info`, `accepted_without_context_aliases=12`,
   `context_gated_aliases=14`.
6. Tests prove RED/GREEN behavior for single-token containment, multi-token
   containment, surrounding context negative case, equal-length reorder
   negative case, and exact equality.
7. Docs/changelog accurately describe the new finding as an advisory
   token-containment heuristic, not a matcher simulation.

Focused verification already run successfully:

```text
uv --no-config run --frozen pytest tests/test_entity_pack_lint.py tests/test_entity_packs.py tests/test_entity_pack_quality_docs.py -q
# 49 passed

uv --no-config run --frozen ruff check src/fashion_radar/entity_packs.py tests/test_entity_pack_lint.py docs/entity-pack-quality.md CHANGELOG.md
# All checks passed

uv --no-config run --frozen ruff format --check src/fashion_radar/entity_packs.py tests/test_entity_pack_lint.py
# 2 files already formatted

uv --no-config run --frozen fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml --format json
# live sample counts unchanged
```

Return findings as Critical, Important, and Minor. If there are no Critical or
Important findings, say that clearly.

# Stage 208 Code Review Prompt

Review the current working tree in `/home/ubuntu/fashion-radar` for Stage 208.

Goal: make the existing advisory `contained_context_term_for_gated_alias`
entity-pack lint warning name the offending context term and gated alias in the
free-text message, without changing matcher behavior or lint schemas.

Baseline:

- `HEAD` / `origin/main`: `219bf870ec5f4360e7e0fe7c9d707d92a5f407db`
- Stage 208 plan:
  `docs/superpowers/plans/2026-06-26-stage-208-context-term-warning-detail-plan.md`
- Stage 208 second plan rereview says I-2 is resolved and no Critical or
  Important planning blockers remain.

Files changed in this stage:

- `src/fashion_radar/entity_packs.py`
- `tests/test_entity_pack_lint.py`
- `docs/entity-pack-quality.md`
- `CHANGELOG.md`
- Stage 208 plan and OpenCode review artifacts under `docs/reviews/`

Review focus:

1. Linter-message-only scope:
   - no matcher behavior changes
   - no `EntityPackFinding` or `EntityPackLintResult` schema changes
   - no config validation, source acquisition, scoring, reports, dashboard,
     connector, scraping, demand proof, platform coverage, dependency,
     lockfile, or compliance-review behavior changes
2. Correct message semantics:
   - warning code remains `contained_context_term_for_gated_alias`
   - emits at most one containment warning per alias
   - message names the selected display context term and `alias.value`
   - exact equality remains covered by `self_context_term`
3. Determinism:
   - selected context key still comes from `sorted(context_keys)`
   - duplicate normalized context keys preserve the first configured display
     value
   - helper produces the same normalized key set as the Stage 207 set
     comprehension
4. Tests:
   - RED was observed for the three target message tests before production code
   - GREEN was observed after the implementation
   - focused linter/docs tests pass
5. Docs/changelog accurately describe a message-only explainability improvement.

Focused verification already run successfully:

```text
uv --no-config run --frozen pytest \
  tests/test_entity_pack_lint.py::test_contained_context_term_warns_for_explicit_gated_alias \
  tests/test_entity_pack_lint.py::test_multi_token_context_term_contained_in_gated_alias_warns \
  tests/test_entity_pack_lint.py::test_contained_context_term_message_uses_first_sorted_context_key \
  -q
# RED before production change: 3 failed on missing message terms
# GREEN after production change: 3 passed

uv --no-config run --frozen pytest tests/test_entity_pack_lint.py tests/test_entity_pack_quality_docs.py -q
# 36 passed

uv --no-config run --frozen ruff check src/fashion_radar/entity_packs.py tests/test_entity_pack_lint.py docs/entity-pack-quality.md CHANGELOG.md
# All checks passed

uv --no-config run --frozen ruff format --check src/fashion_radar/entity_packs.py tests/test_entity_pack_lint.py
# 2 files already formatted
```

Return findings as Critical, Important, and Minor. If there are no Critical or
Important findings, say that clearly.

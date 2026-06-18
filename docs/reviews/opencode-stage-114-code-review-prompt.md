# Stage 114 Code Review Prompt

Review the Stage 114 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 114 adds three optional watchlist sample rows for Tory Burch Pierced Mule,
East-West Bags, and Office Siren. It updates the tests that pin sample row count
and expected watchlist matches. It does not change entity YAML or runtime code.

## Files To Review

- `examples/community-signals.watchlist.example.csv`
- `tests/test_community_signal_lint.py`
- `tests/test_community_signal_import_contract.py`
- `tests/test_entity_packs.py`
- `tests/test_watchlist_sample_workflow.py`
- `docs/superpowers/specs/2026-06-19-stage-114-watchlist-sample-parity-design.md`
- `docs/superpowers/plans/2026-06-19-stage-114-watchlist-sample-parity-plan.md`
- `docs/reviews/opencode-stage-114-plan-review.md`
- `docs/reviews/opencode-stage-114-code-review-prompt.md`

## Review Focus

1. Are the added rows safe synthetic local-sample rows?
2. Do they exercise existing entities without YAML/runtime changes?
3. Are all row-count and expected-match tests updated consistently?
4. Does Boho Revival remain the final row?
5. Are there any release-blocking regressions or missing tests?

## Verification Already Run

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest tests/test_community_signal_lint.py tests/test_community_signal_import_contract.py tests/test_entity_packs.py tests/test_watchlist_sample_workflow.py -q
uv --no-config run --frozen fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml --format json
uv --no-config run --frozen fashion-radar community-signal-lint examples/community-signals.watchlist.example.csv --input-format csv --source-name "Community Watchlist Sample" --format json
uv --no-config run --frozen ruff check tests/test_community_signal_lint.py tests/test_community_signal_import_contract.py tests/test_entity_packs.py tests/test_watchlist_sample_workflow.py
uv --no-config run --frozen ruff format --check tests/test_community_signal_lint.py tests/test_community_signal_import_contract.py tests/test_entity_packs.py tests/test_watchlist_sample_workflow.py
git diff --check
```

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.

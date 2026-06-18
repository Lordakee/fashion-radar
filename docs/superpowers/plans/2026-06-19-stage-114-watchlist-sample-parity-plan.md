# Stage 114 Watchlist Sample Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the optional watchlist community-signal sample so it exercises
more existing watchlist entities: Tory Burch, Tory Burch Pierced Mule,
East-West Bags, and Office Siren.

**Architecture:** Add three local synthetic rows to the checked-in watchlist CSV
before the final Boho Revival row, then update the row-count and matched-entity
tests that intentionally pin that sample. Do not change entity YAML, importer,
matcher, report, trend, dashboard, CLI, dependency, lockfile, or docs behavior.

**Tech Stack:** CSV fixture data, Python 3.11, pytest, Typer CLI tests, uv, ruff.

---

## File Map

- Create:
  `docs/superpowers/specs/2026-06-19-stage-114-watchlist-sample-parity-design.md`
  records the Stage 114 design and scope.
- Create:
  `docs/superpowers/plans/2026-06-19-stage-114-watchlist-sample-parity-plan.md`
  records this implementation plan.
- Create: `docs/reviews/opencode-stage-114-plan-review-prompt.md` requests the
  local plan review.
- Create: `docs/reviews/opencode-stage-114-plan-review.md` records the local
  plan review.
- Modify: `examples/community-signals.watchlist.example.csv` adds three sample
  rows before `Boho Revival`.
- Modify: `tests/test_community_signal_lint.py` updates
  `WATCHLIST_EXPECTED_ROWS`.
- Modify: `tests/test_community_signal_import_contract.py` updates
  `WATCHLIST_EXPECTED_ROWS` and the explicit `len(rows)` assertion.
- Modify: `tests/test_entity_packs.py` extends expected matched names.
- Modify: `tests/test_watchlist_sample_workflow.py` extends expected report
  entities and output row-count strings.
- Create: `docs/reviews/opencode-stage-114-code-review-prompt.md` requests the
  local code review.
- Create: `docs/reviews/opencode-stage-114-code-review.md` records the local
  code review.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-114-plan-review-prompt.md` with this
      review request:

```markdown
# Stage 114 Plan Review Prompt

Review the Stage 114 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Expand the optional watchlist community-signal sample so it exercises existing
entity-pack entries for Tory Burch, Tory Burch Pierced Mule, East-West Bags, and
Office Siren.

## Files To Review

- `docs/superpowers/specs/2026-06-19-stage-114-watchlist-sample-parity-design.md`
- `docs/superpowers/plans/2026-06-19-stage-114-watchlist-sample-parity-plan.md`
- `examples/community-signals.watchlist.example.csv`
- `configs/entity-packs/fashion-watchlist.example.yaml`
- `tests/test_community_signal_lint.py`
- `tests/test_community_signal_import_contract.py`
- `tests/test_entity_packs.py`
- `tests/test_watchlist_sample_workflow.py`
- `docs/entity-packs.md`
- `docs/first-run.md`

## Planned Change

Add these three rows before the final `Boho Revival` row:

```csv
https://example.com/community-watchlist/tory-burch-pierced-mule,Tory Burch Pierced Mule footwear watchlist note,2026-06-12T14:15:00Z,Sanitized local note about Tory Burch Pierced Mule shoe styling and Tory Burch footwear interest,Community Watchlist Sample,community,1.1,2026-06-12T14:35:00Z
https://example.com/community-watchlist/east-west-bags,East-West Bags local watchlist note,2026-06-12T14:30:00Z,Sanitized local note about east-west bags and east west tote handbag styling,Community Watchlist Sample,community,1.0,2026-06-12T14:50:00Z
https://example.com/community-watchlist/office-siren,Office Siren styling watchlist note,2026-06-12T14:45:00Z,Sanitized local note about office siren styling signals and fashion aesthetics,Community Watchlist Sample,community,1.0,2026-06-12T14:55:00Z
```

Update row-count tests from 8 to 11 and extend expected matched/report/trend
entities with:

- `Tory Burch`
- `Tory Burch Pierced Mule`
- `East-West Bags`
- `Office Siren`

## Scope Constraints

Allowed changes:

- `examples/community-signals.watchlist.example.csv`
- `tests/test_community_signal_lint.py`
- `tests/test_community_signal_import_contract.py`
- `tests/test_entity_packs.py`
- `tests/test_watchlist_sample_workflow.py`
- Stage 114 review artifacts

Disallowed changes:

- `configs/entity-packs/fashion-watchlist.example.yaml`
- docs unless review identifies a concrete failing docs contract
- runtime importer, matcher, report, trend, dashboard, CLI, schema, source, or
  scheduling behavior
- source packs, external-tool adapters, connectors, scraping, platform search,
  browser automation, account/session/cookie/proxy behavior
- compliance/audit/legal review product features
- dependency manifests, `uv.lock`, package metadata, CI workflows, or default
  packaged config

## Review Questions

1. Do the planned rows exercise existing entities without requiring alias/YAML
   changes?
2. Is inserting before the final `Boho Revival` row sufficient to preserve
   existing first/last-row assertions?
3. Are row-count and expected-entity test updates complete?
4. Can docs safely remain unchanged because their match examples are
   non-exhaustive?
5. Are the focused verification commands sufficient?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
```

- [ ] Run the local plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-114-plan-review-prompt.md)" > docs/reviews/opencode-stage-114-plan-review.md
```

- [ ] Read `docs/reviews/opencode-stage-114-plan-review.md`.
- [ ] Fix any Critical or Important findings before Task 2.

## Task 2: Write The Failing Test Updates

- [ ] Update row-count constants before editing the CSV:

```python
# tests/test_community_signal_lint.py
WATCHLIST_EXPECTED_ROWS = 11

# tests/test_community_signal_import_contract.py
WATCHLIST_EXPECTED_ROWS = 11
```

- [ ] Update the explicit import-contract row assertion:

```python
assert len(rows) == 11
```

- [ ] Extend `tests/test_entity_packs.py` expected matched names:

```python
        "Tory Burch",
        "Tory Burch Pierced Mule",
        "East-West Bags",
        "Office Siren",
```

- [ ] Extend `tests/test_watchlist_sample_workflow.py`:

```python
EXPECTED_REPORT_ENTITIES = {
    ...
    "Tory Burch",
    "Tory Burch Pierced Mule",
    "East-West Bags",
    "Office Siren",
}
```

- [ ] Update workflow assertions:

```python
assert lint_payload["valid_row_count"] == 11
assert "Validated 11 manual signal rows" in dry_run_output
assert "Imported 11 manual signal rows" in import_output
assert "Processed 11 items" in match_output
```

- [ ] Run the focused tests and confirm they fail because the CSV still has 8
      rows and does not match the new expected entities:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest \
  tests/test_community_signal_lint.py::test_watchlist_community_signal_example_lints_cleanly \
  tests/test_community_signal_import_contract.py::test_watchlist_community_signal_csv_example_loads_expected_rows \
  tests/test_entity_packs.py::test_fashion_watchlist_sample_matches_expected_entities_and_types \
  tests/test_watchlist_sample_workflow.py::test_optional_watchlist_sample_runs_local_import_match_report_and_trends -q
```

Expected: fail before the CSV rows are added.

## Task 3: Add The Sample Rows

- [ ] Insert these rows in
      `examples/community-signals.watchlist.example.csv` after the existing
      `Mary Jane Shoes` row and before the final `Boho Revival` row:

```csv
https://example.com/community-watchlist/tory-burch-pierced-mule,Tory Burch Pierced Mule footwear watchlist note,2026-06-12T14:15:00Z,Sanitized local note about Tory Burch Pierced Mule shoe styling and Tory Burch footwear interest,Community Watchlist Sample,community,1.1,2026-06-12T14:35:00Z
https://example.com/community-watchlist/east-west-bags,East-West Bags local watchlist note,2026-06-12T14:30:00Z,Sanitized local note about east-west bags and east west tote handbag styling,Community Watchlist Sample,community,1.0,2026-06-12T14:50:00Z
https://example.com/community-watchlist/office-siren,Office Siren styling watchlist note,2026-06-12T14:45:00Z,Sanitized local note about office siren styling signals and fashion aesthetics,Community Watchlist Sample,community,1.0,2026-06-12T14:55:00Z
```

- [ ] Run the focused tests again:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest \
  tests/test_community_signal_lint.py::test_watchlist_community_signal_example_lints_cleanly \
  tests/test_community_signal_import_contract.py::test_watchlist_community_signal_csv_example_loads_expected_rows \
  tests/test_entity_packs.py::test_fashion_watchlist_sample_matches_expected_entities_and_types \
  tests/test_watchlist_sample_workflow.py::test_optional_watchlist_sample_runs_local_import_match_report_and_trends -q
```

Expected: pass.

## Task 4: Local Contract Checks

- [ ] Run CLI contract checks:

```bash
uv --no-config run --frozen fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml --format json
uv --no-config run --frozen fashion-radar community-signal-lint examples/community-signals.watchlist.example.csv --input-format csv --source-name "Community Watchlist Sample" --format json
```

- [ ] Run style and diff checks:

```bash
uv --no-config run --frozen ruff check tests/test_community_signal_lint.py tests/test_community_signal_import_contract.py tests/test_entity_packs.py tests/test_watchlist_sample_workflow.py
uv --no-config run --frozen ruff format --check tests/test_community_signal_lint.py tests/test_community_signal_import_contract.py tests/test_entity_packs.py tests/test_watchlist_sample_workflow.py
git diff --check
```

## Task 5: Code Review

- [ ] Create `docs/reviews/opencode-stage-114-code-review-prompt.md` with this
      review request:

```markdown
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

## Review Focus

1. Are the added rows safe synthetic local-sample rows?
2. Do they exercise existing entities without YAML/runtime changes?
3. Are all row-count and expected-match tests updated consistently?
4. Does Boho Revival remain the final row?
5. Are there any release-blocking regressions or missing tests?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
```

- [ ] Run the local code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-114-code-review-prompt.md)" > docs/reviews/opencode-stage-114-code-review.md
```

- [ ] Fix any Critical or Important findings before Task 6.

## Task 6: Full Release Gate And Commit

- [ ] Run the release gate:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then exit 1; fi
git diff --exit-code -- uv.lock pyproject.toml
git diff --check
```

- [ ] Stage only intended files and run staged checks:

```bash
git add -- \
  examples/community-signals.watchlist.example.csv \
  tests/test_community_signal_lint.py \
  tests/test_community_signal_import_contract.py \
  tests/test_entity_packs.py \
  tests/test_watchlist_sample_workflow.py \
  docs/superpowers/specs/2026-06-19-stage-114-watchlist-sample-parity-design.md \
  docs/superpowers/plans/2026-06-19-stage-114-watchlist-sample-parity-plan.md \
  docs/reviews/opencode-stage-114-plan-review-prompt.md \
  docs/reviews/opencode-stage-114-plan-review.md \
  docs/reviews/opencode-stage-114-code-review-prompt.md \
  docs/reviews/opencode-stage-114-code-review.md
git diff --cached --check
if git diff --cached --name-only | rg -x 'uv.lock'; then exit 1; fi
git grep --cached -n -E 'gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{82,255}|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' -- . ':!uv.lock' && exit 1 || true
```

- [ ] Commit:

```bash
git commit -m "Expand watchlist sample coverage"
```
```

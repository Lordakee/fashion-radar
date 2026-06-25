# Stage 199 Aggregate Match Evidence Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add aggregate deterministic match-evidence summaries to daily entity reports so users can see why tracked entity matches are credible without exposing raw matcher internals.

**Architecture:** Extend the report model with an additive `match_evidence` object on each `EntityReport`. Populate it from existing accepted `item_entities` rows joined to `items`, using the same current-window and `min_match_confidence` boundaries as entity scoring and representative items. Render a concise Markdown evidence line while keeping evidence aggregate-only and report-safe.

**Tech Stack:** Python 3.11+, Pydantic report models, SQLAlchemy Core selects over existing SQLite schema, existing report renderer, pytest, ruff, uv, local OpenCode review with `zhipuai-coding-plan/glm-5.2 --variant max`, no new dependencies.

---

## Scope Boundary

This stage closes a deterministic matching quality gap in the `collect -> match
-> score -> report` path. Stage 198 broadened optional watchlist matching
coverage; Stage 199 makes the daily report explain accepted tracked-entity
matches in aggregate.

Do not change:

- entity matching behavior or alias/context evaluation
- scoring formulas, heat-score sorting, candidate discovery, trend comparisons,
  or heat-movers contracts
- SQLite schema or migrations
- collectors, source packs, default source configs, source-liveness, RSS/GDELT
  behavior, article extraction, external tool/community/imported command
  surfaces
- social/Xiaohongshu/Instagram/TikTok/X connectors, scraping/crawling/browser
  automation, login/cookie/session/token handling, proxy behavior, source
  ranking, brand ranking, demand proof, platform coverage verification, or
  compliance-review/audit/legal-review product features

Report evidence must remain aggregate-only. Do not expose raw aliases, raw
context terms, item ids, normalized URLs, internal match rows, or per-row
matcher explanations in Markdown or JSON reports.

## Files And Responsibilities

- Modify `src/fashion_radar/models/report.py`: add `EntityMatchEvidence` and a
  `match_evidence` field on `EntityReport`.
- Modify `src/fashion_radar/reports.py`: load aggregate match evidence for each
  entity from existing stored matches, render a concise Markdown line, and keep
  raw matcher fields internal.
- Modify `tests/test_reports.py`: add direct JSON/Markdown coverage for
  aggregate evidence, duplicate-row deduplication, unknown reason bucketing,
  and no raw matcher leakage.
- Modify `tests/test_cli.py`: update the report CLI smoke to assert the new JSON
  field and Markdown evidence line.
- Modify `scripts/check_first_run_smoke.py`: validate that generated sample
  reports include the aggregate evidence contract without broadening live
  collection or external-tool behavior.
- Modify `tests/test_first_run_smoke.py`: update focused smoke validator tests
  for the new report evidence contract.
- Modify `docs/scoring.md`: add one short section explaining aggregate match
  evidence as local report-derived evidence, not demand proof or platform
  coverage verification.
- Modify `CHANGELOG.md`: add a Stage 199 entry under `[Unreleased]`.
- Create review artifacts:
  - `docs/reviews/opencode-stage-199-plan-review-prompt.md`
  - `docs/reviews/opencode-stage-199-plan-review.md`
  - `docs/reviews/opencode-stage-199-code-review-prompt.md`
  - `docs/reviews/opencode-stage-199-code-review.md`
  - `docs/reviews/opencode-stage-199-release-review-prompt.md`
  - `docs/reviews/opencode-stage-199-release-review.md`

Do not modify:

- `configs/source-packs/*`
- `configs/sources.example.yaml`
- `configs/entities.example.yaml`
- `src/fashion_radar/templates/configs/entities.example.yaml`
- `src/fashion_radar/extract/entities.py`
- `src/fashion_radar/scoring.py`
- `src/fashion_radar/discovery/candidates.py`
- `src/fashion_radar/trends.py`
- `src/fashion_radar/heat_movers.py`
- external/community/imported command modules

## Evidence Model

Add this model before `EntityReport` in `src/fashion_radar/models/report.py`:

```python
class EntityMatchEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    matched_items: int = 0
    accepted_without_context_items: int = 0
    context_supported_items: int = 0
    parent_brand_supported_items: int = 0
    safe_alias_supported_items: int = 0
    other_supported_items: int = 0
    min_confidence: float | None = None
    avg_confidence: float | None = None
    max_confidence: float | None = None
```

Add this field to `EntityReport` after `representative_items`:

```python
match_evidence: EntityMatchEvidence = Field(default_factory=EntityMatchEvidence)
```

Stable JSON key order is important. Do not use a plain `dict` for the evidence
payload.

## Reason Classification

Stored matcher reasons are strings. Classify only known support reasons and
bucket every other accepted row under `other_supported_items`:

| Stored reason | Evidence bucket |
| --- | --- |
| `accepted` | `accepted_without_context_items` |
| `context` | `context_supported_items` |
| `parent_brand` | `parent_brand_supported_items` |
| `safe_alias` | `safe_alias_supported_items` |
| anything else | `other_supported_items` |

Evidence is scoped to one report entity, so the SQL must filter by both
`entity_name` and `entity_type`. If duplicate accepted rows exist for the same
`(entity_name, entity_type, item_id)`, choose the row with the highest
confidence. If confidence ties, use the lexicographically smallest reason
string so output is deterministic. This mirrors scoring's per-entity/item
deduplication while making reason selection stable.

Use the same evidence window as current scoring:

```python
current_start = as_of - timedelta(days=scoring.current_window_days)
current_start < collected_at <= as_of
confidence >= scoring.min_match_confidence
```

Round confidence values to four decimal places in JSON. Render confidence in
Markdown with two decimals. When `min_confidence == max_confidence`, keep the
same range form (`confidence 1.00-1.00 avg 1.00`) so the Markdown sentence has
one stable shape.

## Markdown Rendering

Add one line in each entity section after `Distinct sources`:

```markdown
- Match evidence: 2 matched items; 1 accepted without context, 1 parent-brand supported; confidence 0.88-1.00 avg 0.94
```

Rules:

- Use `matched item` singular for one item and `matched items` otherwise.
- Omit zero support buckets from the Markdown line.
- If `matched_items == 0`, render:

```markdown
- Match evidence: no current-window accepted matches above the report confidence threshold.
```

- Do not include aliases, raw context terms, item ids, normalized URLs, or raw
  reason strings in Markdown.

## Task 0: Create Plan Review Artifacts

**Files:**
- Create: `docs/reviews/opencode-stage-199-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-199-plan-review.md`

- [ ] **Step 1: Write the plan review prompt**

Create `docs/reviews/opencode-stage-199-plan-review-prompt.md` asking local
OpenCode to review:

- whether the stage is the right deterministic matching-quality node after
  Stage 198
- whether the evidence model is aggregate-only and report-safe
- whether the reason classification and duplicate-row deduplication are
  technically sound
- whether the current-window and confidence filters align with scoring
- whether the plan avoids collection/source/social/ranking/compliance scope
  expansion
- whether the verification plan is sufficient

- [ ] **Step 2: Run plan review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-199-plan-review-prompt.md)" > "$tmp_review"
sed -n '1,400p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-199-plan-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important blockers. If OpenCode finds Critical or
Important issues, update this plan, rerun the plan review, and save a
`plan-rereview` artifact before implementation.

## Task 1: Add Report Model Contract

**Files:**
- Modify: `src/fashion_radar/models/report.py`
- Modify: `tests/test_reports.py`

- [ ] **Step 1: Add failing model/default JSON test**

In `tests/test_reports.py`, import `EntityMatchEvidence` from
`fashion_radar.models.report` and add this test near the existing report-model
tests:

```python
def test_entity_report_match_evidence_default_json_shape() -> None:
    report = EntityReport(
        entity_name="The Row",
        entity_type="brand",
        label="new",
        heat_score=1.0,
        current_mentions=1,
        baseline_mentions=0,
        distinct_sources=1,
    )
    payload = report.model_dump(mode="json")

    assert isinstance(report.match_evidence, EntityMatchEvidence)
    assert list(payload["match_evidence"]) == [
        "matched_items",
        "accepted_without_context_items",
        "context_supported_items",
        "parent_brand_supported_items",
        "safe_alias_supported_items",
        "other_supported_items",
        "min_confidence",
        "avg_confidence",
        "max_confidence",
    ]
    assert payload["match_evidence"] == {
        "matched_items": 0,
        "accepted_without_context_items": 0,
        "context_supported_items": 0,
        "parent_brand_supported_items": 0,
        "safe_alias_supported_items": 0,
        "other_supported_items": 0,
        "min_confidence": None,
        "avg_confidence": None,
        "max_confidence": None,
    }
```

- [ ] **Step 2: Run RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_reports.py::test_entity_report_match_evidence_default_json_shape -q
```

Expected: fail because `EntityReport` has no `match_evidence` field.

- [ ] **Step 3: Add model**

In `src/fashion_radar/models/report.py`, add `EntityMatchEvidence` exactly as
specified in the Evidence Model section. Add
`match_evidence: EntityMatchEvidence = Field(default_factory=EntityMatchEvidence)`
to `EntityReport` after `representative_items`.

- [ ] **Step 4: Run GREEN test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_reports.py::test_entity_report_match_evidence_default_json_shape -q
```

Expected: pass.

## Task 2: Populate Aggregate Evidence

**Files:**
- Modify: `src/fashion_radar/reports.py`
- Modify: `tests/test_reports.py`

- [ ] **Step 1: Add failing report build test**

Add a helper in `tests/test_reports.py` near `_store_item`:

```python
def _store_item_with_matches(
    engine,
    *,
    url: str,
    entity_name: str,
    matches: list[dict[str, object]],
    source_name: str = "Vogue Business",
    source_weight: float = 1.0,
    collected_at: datetime,
    published_at: datetime | None = None,
    summary: str = "Short attributed summary.",
) -> int:
    repository = ItemRepository(engine)
    item_id = repository.upsert_item(
        CollectedItem(
            source_name=source_name,
            source_type=SourceType.RSS,
            url=url,
            title=f"{entity_name} fashion signal",
            published_at=published_at or collected_at,
            summary=summary,
        ),
        source_weight=source_weight,
        collected_at=collected_at,
    )
    repository.replace_item_matches(item_id, matches)
    return item_id
```

Then update `_store_item(...)` to call `_store_item_with_matches(...)` with its
current single raw-internal match. This keeps existing tests unchanged.

Add this test:

```python
def test_daily_report_includes_aggregate_entity_match_evidence(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    _store_item_with_matches(
        engine,
        url="https://example.com/the-row-context",
        entity_name="The Row",
        collected_at=AS_OF - timedelta(hours=1),
        matches=[
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "raw alias must stay internal",
                "confidence": 0.8,
                "reason": "context",
                "context_terms": ["raw context must stay internal"],
            },
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "raw alias duplicate must stay internal",
                "confidence": 0.95,
                "reason": "parent_brand",
                "context_terms": ["raw duplicate context must stay internal"],
            },
        ],
    )
    _store_item_with_matches(
        engine,
        url="https://example.com/the-row-safe",
        entity_name="The Row",
        collected_at=AS_OF - timedelta(hours=2),
        matches=[
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "raw safe alias must stay internal",
                "confidence": 0.9,
                "reason": "safe_alias",
                "context_terms": ["raw safe context must stay internal"],
            }
        ],
    )
    _store_item_with_matches(
        engine,
        url="https://example.com/the-row-tie",
        entity_name="The Row",
        collected_at=AS_OF - timedelta(hours=3),
        matches=[
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "raw tie safe alias must stay internal",
                "confidence": 0.7,
                "reason": "safe_alias",
                "context_terms": ["raw tie safe context must stay internal"],
            },
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "raw tie parent alias must stay internal",
                "confidence": 0.7,
                "reason": "parent_brand",
                "context_terms": ["raw tie parent context must stay internal"],
            },
        ],
    )
    _store_item_with_matches(
        engine,
        url="https://example.com/the-row-low-confidence",
        entity_name="The Row",
        collected_at=AS_OF - timedelta(hours=4),
        matches=[
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "low confidence alias must stay internal",
                "confidence": 0.3,
                "reason": "accepted",
                "context_terms": [],
            }
        ],
    )
    _store_item_with_matches(
        engine,
        url="https://example.com/the-row-old",
        entity_name="The Row",
        collected_at=AS_OF - timedelta(days=8),
        matches=[
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "old alias must stay internal",
                "confidence": 1.0,
                "reason": "accepted",
                "context_terms": [],
            }
        ],
    )

    report = build_daily_report(
        engine,
        scoring=ScoringSettings(current_window_days=7, min_match_confidence=0.5),
        as_of=AS_OF,
        generated_at=AS_OF,
    )
    evidence = report.entities[0].match_evidence

    assert evidence.matched_items == 3
    assert evidence.accepted_without_context_items == 0
    assert evidence.context_supported_items == 0
    assert evidence.parent_brand_supported_items == 2
    assert evidence.safe_alias_supported_items == 1
    assert evidence.other_supported_items == 0
    assert evidence.min_confidence == 0.7
    assert evidence.avg_confidence == 0.85
    assert evidence.max_confidence == 0.95
```

This verifies current-window filtering, sub-threshold confidence exclusion,
duplicate item/entity deduplication by highest confidence, lexicographic reason
tie-break (`parent_brand` wins over `safe_alias` at confidence `0.7`), and
support reason counting.

- [ ] **Step 2: Run RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_reports.py::test_daily_report_includes_aggregate_entity_match_evidence -q
```

Expected: fail because evidence is still empty.

- [ ] **Step 3: Implement evidence loading**

In `src/fashion_radar/reports.py`:

1. Import `EntityMatchEvidence`.
2. Add `match_evidence=_match_evidence(...)` in `_entity_report(...)`, passing
   `entity_name=metric.entity_name`, `entity_type=metric.entity_type`, and the
   same `min_match_confidence`, `current_start`, and `as_of` values used by
   `_representative_items(...)`.
3. Add a helper near `_representative_items(...)`:

```python
def _match_evidence(
    engine: Engine,
    *,
    entity_name: str,
    entity_type: str,
    min_match_confidence: float,
    current_start: datetime,
    as_of: datetime,
) -> EntityMatchEvidence:
    ...
```

The helper should:

- select `items.id`, `items.collected_at`, `item_entities.entity_type`,
  `item_entities.confidence`, and `item_entities.reason`
- filter by `item_entities.entity_name == entity_name`,
  `item_entities.entity_type == entity_type`, and confidence threshold
- parse `collected_at` with `parse_datetime_utc`
- keep rows with `current_start < collected_at <= as_of`
- deduplicate by `(entity_name, entity_type, item_id)` using highest confidence;
  when confidence ties, choose the lexicographically smallest reason
- count the selected reason buckets from the Reason Classification table
- compute `min_confidence`, `avg_confidence`, and `max_confidence` from selected
  row confidence values, rounded to four decimal places in the helper before
  constructing `EntityMatchEvidence`
- return the default `EntityMatchEvidence()` when no rows survive

- [ ] **Step 4: Run GREEN report tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_reports.py::test_entity_report_match_evidence_default_json_shape tests/test_reports.py::test_daily_report_includes_aggregate_entity_match_evidence -q
```

Expected: pass.

## Task 3: Render Evidence And Guard Raw Fields

**Files:**
- Modify: `src/fashion_radar/reports.py`
- Modify: `tests/test_reports.py`

- [ ] **Step 1: Add Markdown and raw-field assertions**

Extend `test_json_report_excludes_internal_database_and_matcher_fields` to
assert:

```python
entity = parsed["entities"][0]
assert entity["match_evidence"]["matched_items"] == 1
assert entity["match_evidence"]["other_supported_items"] == 1
```

Extend the forbidden string tuple with:

```python
"raw duplicate context must stay internal",
"raw safe alias must stay internal",
```

Add this Markdown assertion to
`test_daily_report_includes_aggregate_entity_match_evidence`:

```python
markdown = render_markdown_report(report)
assert (
    "- Match evidence: 3 matched items; 2 parent-brand supported, "
    "1 safe-alias supported; confidence 0.70-0.95 avg 0.85"
) in markdown
```

Add a separate empty-evidence rendering test:

```python
def test_rendered_entity_sections_show_empty_match_evidence_message() -> None:
    report = DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF, item_count=1),
        entities=[
            EntityReport(
                entity_name="No Evidence Brand",
                entity_type="brand",
                label="new",
                heat_score=1.0,
                current_mentions=1,
                baseline_mentions=0,
                distinct_sources=1,
            )
        ],
    )

    markdown = render_markdown_report(report)

    assert (
        "- Match evidence: no current-window accepted matches above the report "
        "confidence threshold."
    ) in markdown
```

- [ ] **Step 2: Run RED rendering tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_reports.py -q -k "match_evidence or internal_database_and_matcher_fields"
```

Expected: fail until Markdown rendering is implemented.

- [ ] **Step 3: Implement Markdown rendering helpers**

In `src/fashion_radar/reports.py`, add:

```python
def _render_match_evidence(evidence: EntityMatchEvidence) -> str:
    ...
```

Use these labels:

- `accepted without context`
- `context supported`
- `parent-brand supported`
- `safe-alias supported`
- `other supported`

Use `_count_label(...)` for matched item grammar. Include only non-zero support
buckets. If `matched_items == 0`, return the empty-evidence sentence above.
When confidence min/max are equal, use the same range form as other evidence
lines, for example `confidence 1.00-1.00 avg 1.00`.

In `_render_entity_sections(...)`, insert:

```python
f"- Match evidence: {_render_match_evidence(entity.match_evidence)}",
```

immediately after `Distinct sources`.

- [ ] **Step 4: Run GREEN rendering tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_reports.py -q -k "match_evidence or internal_database_and_matcher_fields"
```

Expected: pass.

## Task 4: CLI, First-Run Smoke, Docs, And Changelog

**Files:**
- Modify: `tests/test_cli.py`
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_first_run_smoke.py`
- Modify: `docs/scoring.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update CLI report smoke**

In `tests/test_cli.py::test_report_command_writes_markdown_and_json`, after
`assert json_payload["entities"][0]["entity_name"] == "The Row"`, add:

```python
    assert "- Match evidence:" in markdown_text
    assert json_payload["entities"][0]["match_evidence"] == {
        "matched_items": 1,
        "accepted_without_context_items": 1,
        "context_supported_items": 0,
        "parent_brand_supported_items": 0,
        "safe_alias_supported_items": 0,
        "other_supported_items": 0,
        "min_confidence": 1.0,
        "avg_confidence": 1.0,
        "max_confidence": 1.0,
    }
```

- [ ] **Step 2: Update first-run smoke validator**

Find `validate_report_outputs(...)` in `scripts/check_first_run_smoke.py`. Add
checks that every entity object contains a full `match_evidence` object with
exactly these 9 keys:

```python
expected_evidence_keys = {
    "matched_items",
    "accepted_without_context_items",
    "context_supported_items",
    "parent_brand_supported_items",
    "safe_alias_supported_items",
    "other_supported_items",
    "min_confidence",
    "avg_confidence",
    "max_confidence",
}
```

Validate that `matched_items` is a non-negative integer for every expected
entity. Assert `matched_items >= 1` only for `The Row`, because the smoke sample
always has a direct `The Row` match and this keeps the validator useful without
overfitting exact product/category evidence counts. Also assert no evidence
object contains forbidden raw/internal keys:

```python
for forbidden_key in ("alias", "context_terms", "item_id", "normalized_url", "reason"):
    if forbidden_key in evidence:
        raise SmokeError(...)
```

Keep this validation read-only over generated local sample reports. Do not add
collection, external tools, source-liveness, or dashboard behavior.

- [ ] **Step 3: Update first-run smoke tests**

In `tests/test_first_run_smoke.py`, update `report_payload()` at the entity
dicts around the three sample entities to include this full 9-key
`match_evidence` object:

```python
"match_evidence": {
    "matched_items": 1,
    "accepted_without_context_items": 1,
    "context_supported_items": 0,
    "parent_brand_supported_items": 0,
    "safe_alias_supported_items": 0,
    "other_supported_items": 0,
    "min_confidence": 1.0,
    "avg_confidence": 1.0,
    "max_confidence": 1.0,
},
```

Use that fixture for `The Row`, `The Row Margaux`, and `Ballet Flats` unless
implementation output proves a different support bucket is more accurate for a
fixture. Add one negative case in
`test_validate_report_requires_expected_first_run_entity_sections` where the
first entity lacks `match_evidence` and `validate_report_outputs(...)` raises
`SmokeError` with a message containing `match_evidence`. Add one negative case
where `matched_items` is `-1` and the validator raises a message containing
`matched_items`.

- [ ] **Step 4: Update docs**

In `docs/scoring.md`, add a short `## Match Evidence` section after
`## Formula` and before `## Labels` so the existing `## Limits` docs parser is
unaffected:

```markdown
## Match Evidence

Daily reports include aggregate match evidence for each tracked entity. The
evidence is derived from accepted local matches in the current report window and
shows matched item count, support-bucket counts, and confidence range/average.

This evidence is local and report-derived. It does not expose raw aliases,
context terms, item ids, normalized URLs, or matcher internals. It is not demand
proof, brand ranking, source ranking, or platform coverage verification.
```

Add or update docs tests only if an existing docs test requires the new section.
Do not add broad boundary repetition elsewhere.

- [ ] **Step 5: Update changelog**

Under `[Unreleased]` / `### Added`, add:

```markdown
- Stage 199 adds aggregate match-evidence summaries to daily entity reports,
  showing matched item counts, support buckets, and confidence statistics from
  existing accepted local matches without exposing raw matcher internals or
  changing matching, scoring, collection, source packs, social connectors,
  demand proof, ranking, platform coverage verification, or compliance-review
  product behavior.
```

- [ ] **Step 6: Run focused CLI/smoke/docs tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_cli.py::test_report_command_writes_markdown_and_json \
  tests/test_first_run_smoke.py::test_validate_report_requires_expected_first_run_entity_sections \
  tests/test_reports.py -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

Expected: pass.

## Task 5: Focused Regression And Code Review

**Files:**
- Create: `docs/reviews/opencode-stage-199-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-199-code-review.md`

- [ ] **Step 1: Run focused regression suite**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_reports.py \
  tests/test_cli.py::test_report_command_writes_markdown_and_json \
  tests/test_first_run_smoke.py::test_validate_report_requires_expected_first_run_entity_sections \
  tests/test_matcher.py tests/test_entity_pack_lint.py tests/test_entity_packs.py \
  tests/test_scoring.py tests/test_candidate_scoring.py tests/test_trends.py \
  tests/test_trend_explanations.py -q
uv --no-config run --frozen ruff check \
  src/fashion_radar/models/report.py src/fashion_radar/reports.py \
  tests/test_reports.py tests/test_cli.py scripts/check_first_run_smoke.py \
  tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check \
  src/fashion_radar/models/report.py src/fashion_radar/reports.py \
  tests/test_reports.py tests/test_cli.py scripts/check_first_run_smoke.py \
  tests/test_first_run_smoke.py
git diff --check
```

Expected: all pass.

- [ ] **Step 2: Create code review prompt**

Create `docs/reviews/opencode-stage-199-code-review-prompt.md` covering:

- changed files and Stage 199 scope
- aggregate-only evidence requirements
- duplicate-row deduplication and reason classification
- current-window/confidence alignment with scoring
- raw matcher field non-leakage
- focused verification results
- prohibited scope boundaries

- [ ] **Step 3: Run local OpenCode code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-199-code-review-prompt.md)" > "$tmp_review"
sed -n '1,400p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-199-code-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important blockers. Fix any Critical/Important
findings and run a `code-rereview` before release review.

## Task 6: Release Verification, Release Review, Commit, And Push

**Files:**
- Create: `docs/reviews/opencode-stage-199-release-review-prompt.md`
- Create: `docs/reviews/opencode-stage-199-release-review.md`
- Modify: any file needed to fix Critical or Important release findings

- [ ] **Step 1: Run release verification**

Run:

```bash
git status --short --untracked-files=all
git diff --check
UV_NO_CONFIG=1 uv lock --check
git diff --exit-code -- uv.lock pyproject.toml
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then exit 1; fi
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
tmp_build="$(mktemp -d)"
uv --no-config build --out-dir "$tmp_build"
uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"
uv --no-config run --frozen pytest tests/ -q --tb=short
```

Expected: all pass. Remove temporary build directories after use.

- [ ] **Step 2: Run secret/local-artifact scans**

Run:

```bash
rg -n "ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+" --glob '!uv.lock' --glob '!dist/**' --glob '!build/**' . || true
git status --short --untracked-files=all
```

Expected: no secret hits and no accidental local artifacts.

- [ ] **Step 3: Create and run local OpenCode release review**

Create `docs/reviews/opencode-stage-199-release-review-prompt.md` covering:

- final diff and changed-file scope
- verification command results
- review artifact hygiene
- lockfile/mirror/secret checks
- package archive and installed-wheel smoke if run
- aggregate-only evidence and no raw matcher field leakage
- no prohibited source/social/connector/ranking/hotness/compliance feature
  expansion

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-199-release-review-prompt.md)" > "$tmp_review"
sed -n '1,400p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-199-release-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important blockers. Fix any Critical/Important
findings and run a `release-rereview` before commit.

- [ ] **Step 4: Check review artifact hygiene**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
rg -n "I'll|Let me|Now let me|→|✱|build ·|\\x1b|\\$ |Wrote|errored" docs/reviews/*stage-199*.md || true
```

Expected: release hygiene passes. Inspect any `rg` match before staging.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short --untracked-files=all
git add \
  CHANGELOG.md \
  docs/scoring.md \
  docs/reviews/opencode-stage-199-plan-review-prompt.md \
  docs/reviews/opencode-stage-199-plan-review.md \
  docs/reviews/opencode-stage-199-code-review-prompt.md \
  docs/reviews/opencode-stage-199-code-review.md \
  docs/reviews/opencode-stage-199-release-review-prompt.md \
  docs/reviews/opencode-stage-199-release-review.md \
  docs/superpowers/plans/2026-06-25-stage-199-aggregate-match-evidence-report-plan.md \
  scripts/check_first_run_smoke.py \
  src/fashion_radar/models/report.py \
  src/fashion_radar/reports.py \
  tests/test_cli.py \
  tests/test_first_run_smoke.py \
  tests/test_reports.py
git commit -m "Stage 199: add aggregate match evidence to reports"
git push origin main
```

Expected: push succeeds and `origin/main` points to the new commit.

## Handoff Summary Template

At node completion, report:

```markdown
Handoff Summary
- Repo status: branch, HEAD SHA, origin/main SHA, clean/dirty state.
- Verified commands: concise list with pass/fail status.
- Uncommitted files: exact `git status --short --untracked-files=all` result.
- Next step: the next recommended stage after Stage 199.
```

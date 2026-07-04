# Stage 289 ROW ONE Signal Story Refs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add app-ready supporting story references to each ROW ONE Signal Synthesis item so clients can explain why a brand, product, designer, or person signal appears without joining `signal_synthesis.story_ids` back to the full `stories[]` array.

**Architecture:** Keep this as a deterministic information-organization layer. `signal_synthesis` and `daily_digest.briefing_topics` are both derived from the same `briefing_topics_payload(stories)` topic-card source; Stage 289 copies a compact subset of each topic card into `signal_synthesis.groups[].signals[].story_refs`. It does not add collection, matching, scoring, ranking, compliance-review product features, network calls, or generated-report behavior.

**Tech Stack:** Python 3.12, JSON Schema 2020-12, existing ROW ONE renderer, pytest, ruff.

---

## File Structure

- Modify `src/fashion_radar/row_one/render.py`
  - Add `story_refs` to each signal payload using existing briefing topic `cards`.
  - Keep `story_ids`, lead story fields, summaries, and ordering unchanged.
- Modify `schemas/row-one-app.schema.json`
  - Add a `signalStoryRef` definition and require `story_refs` on each signal.
- Modify `tests/test_row_one_app_contract.py`
  - Verify `story_refs` order, fields, counts, and schema validation.
  - Update `_contract_drift_signal_group()` so existing drift tests keep targeting their intended malformed fields after `story_refs` becomes required.
  - Add schema drift rejection cases for missing/malformed `story_refs`.
- Modify `scripts/check_first_run_smoke.py`
  - Validate generated `story_refs` in the first-run smoke command path.
- Modify `tests/test_first_run_smoke.py`
  - Cover missing, mismatched, and field-drifted `story_refs` in smoke fixtures.
- Modify docs/tests:
  - `docs/row-one.md`
  - `README.md`
  - `tests/test_row_one_docs.py`
- Create review artifacts in `docs/reviews/`.

## Constraints

- Do not modify `uv.lock` or `pyproject.toml`.
- Do not commit generated `reports/row-one/` artifacts.
- Do not add compliance-review product features.
- Do not change collection, matching, scoring, ranking, sorting, scheduling, or story IDs.
- Do not add dependencies or network calls.
- Bump to `row-one-app/v7` because `story_refs` is a required signal-level app contract field and the schema uses `additionalProperties: false`; generated payloads, manifest schema, CLI/status validation, smoke validation, and docs move together.
- Use `UV_NO_CONFIG=1 uv --no-config run --frozen ...` for verification commands.

## Task 1: Add App Contract Tests for Signal Story Refs

**Files:**
- Modify: `tests/test_row_one_app_contract.py`

- [ ] **Step 1: Extend existing Signal Synthesis payload test**

In `test_row_one_app_payload_includes_signal_synthesis_for_clients`, extend the expected brand signal so it includes:

```python
"story_refs": [
    {
        "story_id": "the-row-signal-1234567890",
        "headline": "The Row signal",
        "section_key": "top_stories",
        "section_title": {"zh": "今日重点", "en": "Top Stories"},
        "detail_href": "details/the-row-signal-1234567890.html",
        "source_name": "Vogue Business",
        "published_date": "2026-07-02",
        "evidence_count": 1,
        "heat_delta": 4,
    },
    {
        "story_id": "brand-move-2222222222",
        "headline": "The Row Brand Move",
        "section_key": "brand_moves",
        "section_title": {"zh": "品牌动态", "en": "Brand Moves"},
        "detail_href": "details/brand-move-2222222222.html",
        "source_name": "Vogue Business",
        "published_date": "2026-07-02",
        "evidence_count": 1,
        "heat_delta": 2,
    },
],
```

Also assert:

```python
assert [story_ref["story_id"] for story_ref in brand["story_refs"]] == brand["story_ids"]
```

- [ ] **Step 2: Update schema drift helper and add schema drift cases**

Update `_contract_drift_signal_group()` so its synthetic signal remains otherwise valid after `story_refs` becomes required:

```python
story_ref = {
    "story_id": lead_story["id"],
    "headline": lead_story["headline"],
    "section_key": lead_story["section_key"],
    "section_title": lead_story["section"]["title"],
    "detail_href": lead_story["detail_href"],
    "source_name": lead_story["source_name"],
    "published_date": lead_story["published_date"],
    "evidence_count": lead_story["evidence_count"],
    "heat_delta": lead_story["heat_delta"],
}
```

Then add `"story_refs": [story_ref]` to the helper signal before applying `signal_overrides`.

Add drift cases that reject:

In `test_row_one_app_schema_rejects_contract_drift`, add cases that reject:

```python
lambda payload: payload["signal_synthesis"]["groups"][0]["signals"][0].pop("story_refs")
lambda payload: payload["signal_synthesis"]["groups"][0]["signals"][0]["story_refs"][0].__setitem__("extra", True)
lambda payload: payload["signal_synthesis"]["groups"][0]["signals"][0]["story_refs"][0].__setitem__("story_id", "bad id")
lambda payload: payload["signal_synthesis"]["groups"][0]["signals"][0]["story_refs"][0].__setitem__("detail_href", "../escape.html")
lambda payload: payload["signal_synthesis"]["groups"][0]["signals"][0]["story_refs"][0].__setitem__("evidence_count", -1)
```

Also add a positive schema validation assertion that `story_refs[0]["published_date"] = None` remains valid, matching existing `contentCard.published_date` behavior for undated ROW ONE stories.

- [ ] **Step 3: Verify red**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_app_contract.py::test_row_one_app_payload_includes_signal_synthesis_for_clients tests/test_row_one_app_contract.py::test_row_one_app_schema_rejects_contract_drift -q
```

Expected before implementation: fail because `story_refs` is missing.

## Task 2: Implement Story Refs in Payload and Schema

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `schemas/row-one-app.schema.json`

- [ ] **Step 1: Add story_refs helper**

Add a helper near `_signal_payload_from_topic()`:

```python
def _signal_story_refs_from_topic(topic: dict[str, object]) -> list[dict[str, object]]:
    cards = topic.get("cards")
    if not isinstance(cards, list):
        return []
    story_refs: list[dict[str, object]] = []
    for card in cards:
        if not isinstance(card, dict):
            continue
        section = card.get("section")
        if not isinstance(section, dict):
            continue
        story_refs.append(
            {
                "story_id": card["id"],
                "headline": card["headline"],
                "section_key": card["section_key"],
                "section_title": section["title"],
                "detail_href": card["detail_href"],
                "source_name": card["source_name"],
                "published_date": card["published_date"],
                "evidence_count": card["evidence_count"],
                "heat_delta": card["heat_delta"],
            }
        )
    return story_refs
```

Then include `"story_refs": _signal_story_refs_from_topic(topic)` in `_signal_payload_from_topic()`.

- [ ] **Step 2: Add schema definition**

In `schemas/row-one-app.schema.json`, add a `signalStoryRef` definition:

```json
"signalStoryRef": {
  "type": "object",
  "required": [
    "story_id",
    "headline",
    "section_key",
    "section_title",
    "detail_href",
    "source_name",
    "published_date",
    "evidence_count",
    "heat_delta"
  ],
  "additionalProperties": false,
  "properties": {
    "story_id": { "$ref": "#/$defs/storyId" },
    "headline": { "type": "string", "minLength": 1 },
    "section_key": { "$ref": "#/$defs/sectionKey" },
    "section_title": { "$ref": "#/$defs/localizedText" },
    "detail_href": { "$ref": "#/$defs/detailHref" },
    "source_name": { "type": "string", "minLength": 1 },
    "published_date": { "$ref": "#/$defs/nullablePublishedDate" },
    "evidence_count": { "type": "integer", "minimum": 0 },
    "heat_delta": {
      "anyOf": [
        { "type": "integer" },
        { "type": "null" }
      ]
    }
  }
}
```

Add `"story_refs"` to the signal item required list and properties:

```json
"story_refs": {
  "type": "array",
  "minItems": 1,
  "items": { "$ref": "#/$defs/signalStoryRef" }
}
```

- [ ] **Step 3: Verify payload and schema**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_app_contract.py::test_row_one_app_payload_includes_signal_synthesis_for_clients tests/test_row_one_app_contract.py::test_row_one_app_contract_orders_signal_synthesis_within_group tests/test_row_one_app_contract.py::test_row_one_app_schema_rejects_contract_drift -q
```

Expected: selected tests pass.

## Task 3: Docs and First-Run Smoke Coverage

**Files:**
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_first_run_smoke.py`
- Modify: `docs/row-one.md`
- Modify: `README.md`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Add smoke validation**

Update `validate_row_one_signal_synthesis()` to require each signal's `story_refs` as a non-empty list and assert:

- `story_refs[].story_id` values exactly match `story_ids`.
- Each story ref object has required keys: `story_id`, `headline`, `section_key`, `section_title`, `detail_href`, `source_name`, `published_date`, `evidence_count`, and `heat_delta`.
- `detail_href`, `source_name`, `evidence_count`, and `heat_delta` match the corresponding generated story in `edition_payload["stories"]`.
- `section_key` and `section_title` match the corresponding generated story section.

Add unit coverage in `tests/test_first_run_smoke.py`:

- Extend the smoke fixture used by the signal-synthesis validation tests, or create a minimal inline fixture in the new tests, so it includes one `groups[0].signals[0]` with valid `story_refs`.
- Pop `story_refs` from a sample signal and expect `SmokeError` matching `story_refs`.
- Reorder or replace `story_refs[].story_id` so it differs from `story_ids` and expect `SmokeError` matching `story_ids`.
- Change a field such as `detail_href` or `section_key` in `story_refs[0]` and expect `SmokeError` matching that field name.

- [ ] **Step 2: Add docs test**

Extend `test_row_one_docs_describe_stage_287_signal_synthesis()` or add a Stage 289 docs test asserting these phrases in both `docs/row-one.md` and `README.md` where appropriate:

- `story_refs`
- `supporting story references`
- `app clients`
- `supporting story cards inline`
- `derived from the same briefing topic source story data`
- `not a compliance review feature`
- `does not add collection`
- `does not change matching, ranking, scoring, sorting, or story ids`

- [ ] **Step 3: Update docs**

In `docs/row-one.md` and `README.md`, describe `signal_synthesis.groups[].signals[].story_refs` as an app-facing information-organization index derived from existing topic cards and stories.

- [ ] **Step 4: Verify smoke/docs**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_first_run_smoke.py tests/test_row_one_docs.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

Expected: selected tests pass.

## Task 4: Plan Review, Code Review, Full Verification, Commit, Push

**Files:**
- Create: `docs/reviews/claude-code-stage-289-plan-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-289-plan-review.md`
- Create: `docs/reviews/opencode-stage-289-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-289-plan-review.md`
- Create: `docs/reviews/claude-code-stage-289-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-289-code-review.md`
- Create: `docs/reviews/opencode-stage-289-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-289-code-review.md`

- [ ] **Step 1: Request plan review before implementation**

Try Claude Code first. If it fails with the known 401 disabled-key error, record the failure and use:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max < docs/reviews/opencode-stage-289-plan-review-prompt.md > docs/reviews/opencode-stage-289-plan-review.md
```

- [ ] **Step 2: Request code review after implementation**

Try Claude Code first, then opencode fallback if needed. Fix Critical and Important findings before full verification.

- [ ] **Step 3: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
git diff --check
git diff --exit-code -- uv.lock pyproject.toml
```

Expected: all commands exit `0`.

- [ ] **Step 4: Commit and push**

Run:

```bash
git add src/fashion_radar/row_one/render.py schemas/row-one-app.schema.json scripts/check_first_run_smoke.py tests/test_row_one_app_contract.py tests/test_first_run_smoke.py tests/test_row_one_docs.py docs/row-one.md README.md docs/superpowers/plans/2026-07-04-stage-289-row-one-signal-story-refs-plan.md docs/reviews/
git commit -m "Stage 289: add row one signal story refs"
git push origin main
```

- [ ] **Step 5: Handoff Summary**

Report:
- Repo status
- Verified commands
- Uncommitted files
- Next step

## Self-Review

- Spec coverage: Adds supporting story refs to Signal Synthesis and validates them through schema, smoke, docs, contract tests, and existing drift-helper compatibility.
- Scope control: Does not change collection, matching, scoring, ranking, sorting, schedule behavior, generated story IDs, or compliance-review features.
- App value: Lets app clients explain each signal's source stories without reconstructing joins from full payload arrays.
- Schema correctness: Reuses existing `storyId`, `sectionKey`, `detailHref`, and `nullablePublishedDate` definitions to avoid drift from the rest of the app contract.
- Smoke correctness: Runs both first-run smoke unit tests and the actual `scripts/check_first_run_smoke.py --repo-root .` command path.
- Placeholder scan: No TODO/TBD placeholders remain.

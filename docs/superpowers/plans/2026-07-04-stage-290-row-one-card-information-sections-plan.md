# Stage 290 ROW ONE Card Information Sections Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add app-ready `information_sections` to every ROW ONE app content card so clients can show organized story information directly from JSON, not just links or flat card text.

**Architecture:** Keep Stage 290 as a deterministic presentation-organization layer over existing ROW ONE story fields. Each `contentCard` already carries `summary`, `why_it_matters`, `editorial_takeaway`, `signal_context`, and `reader_path`; Stage 290 packages those same localized fields into ordered `information_sections` blocks that mirror the detail-page information-map concept. This does not add collection, scraping, matching, scoring, ranking, sorting, story-ID changes, network calls, LLMs, image generation, compliance-review product features, source acquisition, or generated-report behavior.

**Tech Stack:** Python 3.12, existing ROW ONE renderer, JSON Schema 2020-12, pytest, ruff.

---

## Product Gap Closed

ROW ONE already exposes story cards, signal synthesis, story refs, and route indexes for app clients. The remaining app-display gap is that clients must decide how to organize each card's explanatory text fields (`summary`, `why_it_matters`, `editorial_takeaway`, `signal_context`, `reader_path`) themselves. Stage 290 closes that gap by adding a stable, ordered information-section array to every app `contentCard`, so the app can render a professional story information panel without inventing labels, order, or field mapping.

## File Structure

- Modify `src/fashion_radar/row_one/render.py`
  - Bump `ROW_ONE_APP_CONTRACT_VERSION` from `row-one-app/v7` to `row-one-app/v8`.
  - Add a deterministic helper that returns five ordered information sections for one content-card story dict.
  - Add `information_sections` to `_content_card_payload()` only; full `stories[]` already has richer `detail_sections` and should not duplicate this new card-specific surface.
- Modify `schemas/row-one-app.schema.json`
  - Bump `contract_version.const` to `row-one-app/v8`.
  - Add a `contentCardInformationSection` definition and require `information_sections` on `contentCard`.
- Modify `schemas/row-one-manifest.schema.json`
  - Bump nested `app_contract.version.const` to `row-one-app/v8`.
- Modify `src/fashion_radar/cli.py`
  - Update status contract expectation to `row-one-app/v8`.
  - Add semantic validation that each card's `information_sections` has the expected keys/order/titles and mirrors the existing card fields.
- Modify `scripts/check_first_run_smoke.py`
  - Update app contract expectation to `row-one-app/v8`.
  - Add first-run smoke validation for content-card information sections.
- Modify tests:
  - `tests/test_row_one_app_contract.py`
  - `tests/test_row_one_cli.py`
  - `tests/test_first_run_smoke.py`
  - `tests/test_row_one_render.py`
    - Migrate existing app contract assertions from `row-one-app/v7` to `row-one-app/v8`; add UI rendering tests only if homepage rendering touches `information_sections` directly.
  - `tests/test_row_one_docs.py`
    - Migrate existing active app contract assertions from `row-one-app/v7` to `row-one-app/v8`, then add Stage 290 docs coverage.
- Modify docs:
  - `README.md`
  - `docs/row-one.md`
- Create review artifacts under `docs/reviews/`.

## Contract Decision

Bump `row-one-app/v7` to `row-one-app/v8`. The schema uses `additionalProperties: false`, and Stage 290 adds a required field to the shared `contentCard` contract used by `content_sections`, `daily_digest.blocks`, and `daily_digest.briefing_topics`. This is an app contract change even though it is additive in generated payloads.

Manifest and runtime contract versions remain unchanged unless their own top-level shapes change. Only the manifest's nested `app_contract.version` expectation changes to `row-one-app/v8`.

## New Payload Shape

Each app `contentCard` gains:

```json
"information_sections": [
  {
    "key": "summary",
    "title": {"zh": "摘要", "en": "Summary"},
    "body": {"zh": "...", "en": "..."}
  },
  {
    "key": "why_it_matters",
    "title": {"zh": "为什么重要", "en": "Why It Matters"},
    "body": {"zh": "...", "en": "..."}
  },
  {
    "key": "editorial_takeaway",
    "title": {"zh": "编辑整理", "en": "Editorial Takeaway"},
    "body": {"zh": "...", "en": "..."}
  },
  {
    "key": "signal_context",
    "title": {"zh": "信号背景", "en": "Signal Context"},
    "body": {"zh": "...", "en": "..."}
  },
  {
    "key": "reader_path",
    "title": {"zh": "阅读路径", "en": "Reader Path"},
    "body": {"zh": "...", "en": "..."}
  }
]
```

The values must be copied from the same card's existing localized fields. Do not generate new prose.

## Constraints

- Do not modify `uv.lock` or `pyproject.toml`.
- Do not commit generated `reports/row-one/` artifacts.
- Do not add dependencies.
- Do not add collection, scraping, platform APIs, connectors, paid APIs, login/cookie/proxy behavior, LLM calls, image generation, scheduling, deployment, ranking/scoring/sorting changes, story-ID changes, demand proof, platform coverage verification, or compliance-review product features.
- Keep the feature deterministic and derived only from existing ROW ONE local report/story fields.
- Use `UV_NO_CONFIG=1 uv --no-config run --frozen ...` for verification commands.

## Task 1: Add App Contract Tests for Card Information Sections

**Files:**
- Modify: `tests/test_row_one_app_contract.py`

- [ ] **Step 1: Extend content card assertions**

In `test_row_one_app_payload_includes_daily_digest_for_clients`, after reading `read_first_card`, assert the ordered information section keys and that each section body mirrors the existing card fields:

```python
assert [section["key"] for section in read_first_card["information_sections"]] == [
    "summary",
    "why_it_matters",
    "editorial_takeaway",
    "signal_context",
    "reader_path",
]
sections_by_key = {section["key"]: section for section in read_first_card["information_sections"]}
assert sections_by_key["summary"] == {
    "key": "summary",
    "title": {"zh": "摘要", "en": "Summary"},
    "body": read_first_card["summary"],
}
assert sections_by_key["why_it_matters"] == {
    "key": "why_it_matters",
    "title": {"zh": "为什么重要", "en": "Why It Matters"},
    "body": read_first_card["why_it_matters"],
}
assert sections_by_key["editorial_takeaway"] == {
    "key": "editorial_takeaway",
    "title": {"zh": "编辑整理", "en": "Editorial Takeaway"},
    "body": read_first_card["editorial_takeaway"],
}
assert sections_by_key["signal_context"] == {
    "key": "signal_context",
    "title": {"zh": "信号背景", "en": "Signal Context"},
    "body": read_first_card["signal_context"],
}
assert sections_by_key["reader_path"] == {
    "key": "reader_path",
    "title": {"zh": "阅读路径", "en": "Reader Path"},
    "body": read_first_card["reader_path"],
}
```

Also assert the same keys exist on the first `content_sections[0]["cards"][0]` and first `daily_digest["briefing_topics"][0]["cards"][0]` when those fixtures produce cards.

- [ ] **Step 2: Add empty-edition assertion**

In `test_row_one_app_payload_includes_empty_edition_brief_for_clients` or the nearest empty-payload test, assert empty editions still produce valid contract surfaces without requiring any cards:

```python
assert payload["content_sections"][0]["cards"] == []
assert payload["daily_digest"]["blocks"][0]["cards"] == []
assert payload["daily_digest"]["briefing_topics"] == []
_schema_validator().validate(payload)
```

- [ ] **Step 3: Add schema drift cases**

In `test_row_one_app_schema_rejects_contract_drift`, add cases for malformed `information_sections` on a `contentCard` fixture:

```python
lambda payload: payload["daily_digest"]["blocks"][0]["cards"][0].pop("information_sections")
lambda payload: payload["daily_digest"]["blocks"][0]["cards"][0]["information_sections"].append({"key": "extra", "title": {"zh": "x", "en": "x"}, "body": {"zh": "x", "en": "x"}})
lambda payload: payload["daily_digest"]["blocks"][0]["cards"][0]["information_sections"][0].__setitem__("key", "bad")
lambda payload: payload["daily_digest"]["blocks"][0]["cards"][0]["information_sections"][0].pop("body")
```

Use expected schema error patterns matching existing style: required property, too long/too short or enum failure, and additional/missing properties as appropriate.

- [ ] **Step 4: Verify red**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_app_contract.py::test_row_one_app_payload_includes_daily_digest_for_clients tests/test_row_one_app_contract.py::test_row_one_app_schema_rejects_contract_drift -q
```

Expected before implementation: fail because `information_sections` and `row-one-app/v8` are missing.

## Task 2: Implement Renderer and Schema Contract

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `schemas/row-one-app.schema.json`
- Modify: `schemas/row-one-manifest.schema.json`

- [ ] **Step 1: Bump app contract version**

In `src/fashion_radar/row_one/render.py`:

```python
ROW_ONE_APP_CONTRACT_VERSION = "row-one-app/v8"
```

In `schemas/row-one-app.schema.json`:

```json
"contract_version": {
  "const": "row-one-app/v8"
}
```

In `schemas/row-one-manifest.schema.json`, update nested app contract const to `row-one-app/v8`.

- [ ] **Step 2: Add information section helper**

In `src/fashion_radar/row_one/render.py`, near `_content_card_payload`, add:

```python
CONTENT_CARD_INFORMATION_SECTIONS = (
    ("summary", {"zh": "摘要", "en": "Summary"}),
    ("why_it_matters", {"zh": "为什么重要", "en": "Why It Matters"}),
    ("editorial_takeaway", {"zh": "编辑整理", "en": "Editorial Takeaway"}),
    ("signal_context", {"zh": "信号背景", "en": "Signal Context"}),
    ("reader_path", {"zh": "阅读路径", "en": "Reader Path"}),
)


def _content_card_information_sections(story: dict[str, object]) -> list[dict[str, object]]:
    return [
        {
            "key": key,
            "title": dict(title),
            "body": story[key],
        }
        for key, title in CONTENT_CARD_INFORMATION_SECTIONS
    ]
```

- [ ] **Step 3: Add field to content cards**

In `_content_card_payload`, add:

```python
"information_sections": _content_card_information_sections(story),
```

Do not remove existing top-level card fields.

- [ ] **Step 4: Add JSON Schema defs**

In `schemas/row-one-app.schema.json`, add `information_sections` to `contentCard.required` and `contentCard.properties`:

```json
"information_sections": {
  "type": "array",
  "minItems": 5,
  "maxItems": 5,
  "prefixItems": [
    { "$ref": "#/$defs/contentCardSummaryInformationSection" },
    { "$ref": "#/$defs/contentCardWhyItMattersInformationSection" },
    { "$ref": "#/$defs/contentCardEditorialTakeawayInformationSection" },
    { "$ref": "#/$defs/contentCardSignalContextInformationSection" },
    { "$ref": "#/$defs/contentCardReaderPathInformationSection" }
  ],
  "items": false
}
```

Add section definitions that constrain the keys and reuse `localizedText` for `title` and `body`. Pattern:

```json
"contentCardSummaryInformationSection": {
  "allOf": [
    { "$ref": "#/$defs/contentCardInformationSectionBase" },
    {
      "type": "object",
      "properties": {
        "key": { "const": "summary" },
        "title": { "const": { "zh": "摘要", "en": "Summary" } }
      }
    }
  ]
}
```

Use equivalent constants for the other four keys/titles. Add base definition:

```json
"contentCardInformationSectionBase": {
  "type": "object",
  "required": ["key", "title", "body"],
  "additionalProperties": false,
  "properties": {
    "key": { "type": "string" },
    "title": { "$ref": "#/$defs/localizedText" },
    "body": { "$ref": "#/$defs/localizedText" }
  }
}
```

If JSON Schema `allOf` plus `additionalProperties: false` proves awkward in this schema, use five fully expanded definitions instead of `allOf`. Prefer clarity over cleverness.

- [ ] **Step 5: Verify green**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_app_contract.py::test_row_one_app_payload_includes_daily_digest_for_clients tests/test_row_one_app_contract.py::test_row_one_app_schema_rejects_contract_drift -q
```

Expected: pass.

## Task 3: Add CLI and Smoke Semantic Validation

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_row_one_cli.py`
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Update app contract expectations**

In `src/fashion_radar/cli.py`, update the status validator expected app contract from `row-one-app/v7` to `row-one-app/v8`.

In `scripts/check_first_run_smoke.py`, update the app contract expectation from `row-one-app/v7` to `row-one-app/v8`.

Update every active contract-string assertion found by `rg -n "row-one-app/v7" README.md docs/row-one.md schemas scripts src tests`: `tests/test_row_one_cli.py` currently has 3 active test refs, `tests/test_row_one_render.py` has 2, `tests/test_row_one_app_contract.py` has 3, `tests/test_first_run_smoke.py` has 5, `tests/test_row_one_docs.py` has 5, `src/fashion_radar/cli.py` has 2, `scripts/check_first_run_smoke.py` has 2, the app schema has 1, the manifest schema has 1, README has 2, and `docs/row-one.md` has 8. Historical Stage 289 plan/review artifacts stay unchanged.

- [ ] **Step 2: Add semantic validator helper**

In `src/fashion_radar/cli.py`, add a helper near other ROW ONE validation helpers:

```python
_EXPECTED_ROW_ONE_CARD_INFORMATION_SECTIONS = (
    ("summary", {"zh": "摘要", "en": "Summary"}),
    ("why_it_matters", {"zh": "为什么重要", "en": "Why It Matters"}),
    ("editorial_takeaway", {"zh": "编辑整理", "en": "Editorial Takeaway"}),
    ("signal_context", {"zh": "信号背景", "en": "Signal Context"}),
    ("reader_path", {"zh": "阅读路径", "en": "Reader Path"}),
)


def _validate_row_one_content_card_information_sections(
    label: str,
    card: dict[str, object],
) -> None:
    sections = card.get("information_sections")
    if not isinstance(sections, list):
        raise ValueError(f"row-one {label}.information_sections must be a JSON array")
    _require_row_one_value(f"{label}.information_sections count", len(sections), 5)
    for index, (expected_key, expected_title) in enumerate(
        _EXPECTED_ROW_ONE_CARD_INFORMATION_SECTIONS
    ):
        section = sections[index]
        if not isinstance(section, dict):
            raise ValueError(f"row-one {label}.information_sections[{index}] must be an object")
        _require_row_one_value(
            f"{label}.information_sections[{index}].key",
            section.get("key"),
            expected_key,
        )
        _require_row_one_value(
            f"{label}.information_sections[{index}].title",
            section.get("title"),
            expected_title,
        )
        _require_row_one_value(
            f"{label}.information_sections[{index}].body",
            section.get("body"),
            card.get(expected_key),
        )
```

Call this helper for every card in `content_sections[].cards`, `daily_digest.blocks[].cards`, and `daily_digest.briefing_topics[].cards` from the existing status payload validation path. Do not add new CLI output fields.

- [ ] **Step 3: Add CLI drift test**

In `tests/test_row_one_cli.py`, add a status drift test that mutates a card's `information_sections[0]["body"]` to a schema-valid but semantically wrong localized text and expects status failure:

```python
payload["daily_digest"]["blocks"][0]["cards"][0]["information_sections"][0]["body"] = {
    "zh": "错误摘要",
    "en": "Wrong summary",
}
```

Expected output contains `information_sections[0].body`.

- [ ] **Step 4: Add first-run smoke validation**

Mirror the CLI validation helper in `scripts/check_first_run_smoke.py` with `SmokeError` messages. Add tests in `tests/test_first_run_smoke.py` for:

```python
missing_sections = copy.deepcopy(payload)
del missing_sections["daily_digest"]["blocks"][0]["cards"][0]["information_sections"]

wrong_body = copy.deepcopy(payload)
wrong_body["daily_digest"]["blocks"][0]["cards"][0]["information_sections"][0]["body"] = {"zh": "错误", "en": "Wrong"}
```

Expected errors mention `information_sections` and `information_sections[0].body`.

- [ ] **Step 5: Verify focused semantic checks**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py -q -k "row_one_status and information_sections"
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "information_sections or row_one_runtime"
```

Expected: pass.

## Task 4: Documentation and Review Artifacts

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`
- Create: `docs/reviews/claude-code-stage-290-plan-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-290-plan-review.md`
- Create: `docs/reviews/opencode-stage-290-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-290-plan-review.md`
- Later create code review artifacts after implementation.

- [ ] **Step 1: Migrate active docs and docs tests to v8**

Migrate active `row-one-app/v7` wording to `row-one-app/v8` in `README.md` and `docs/row-one.md`. Update the existing `tests/test_row_one_docs.py` assertions that currently expect `row-one-app/v7`, including `test_row_one_docs_describe_versioned_app_json_contract`, `test_row_one_docs_describe_stage_271_app_content_organization`, `test_row_one_docs_describe_stage_277_homepage_briefing_topics`, and `test_row_one_docs_describe_stage_272_editorial_web_experience`.

- [ ] **Step 2: Add Stage 290 docs wording**

In README and docs, describe:

```text
Stage 290 adds `information_sections` to app content cards as an app-facing information organization layer. It packages existing ROW ONE localized story fields into display-ready sections for app clients, without changing collection, matching, ranking, scoring, sorting, story IDs, source acquisition, platform coverage, demand proof, external enrichment, LLMs, image generation, deployment, or compliance-review behavior.
```

- [ ] **Step 3: Add Stage 290 docs test**

In `tests/test_row_one_docs.py`, add `test_row_one_docs_describe_stage_290_card_information_sections` asserting both README and docs mention:

```python
"information_sections"
"app-facing information organization layer"
"display-ready sections"
"existing row one localized story fields"
"does not change collection, matching, ranking, scoring, sorting, or story ids"
"not a compliance review feature"
```

- [ ] **Step 4: Create review prompts

Create Stage 290 plan review prompts that ask Claude Code first, then opencode fallback, to evaluate:

1. Whether `contentCard.information_sections` is the right next information-organization layer.
2. Whether bumping to `row-one-app/v8` is appropriate.
3. Whether tests cover schema, semantic status/smoke validation, empty payloads, and docs.
4. Whether the plan avoids collection/ranking/scoring/compliance/platform behavior.

- [ ] **Step 5: Run plan reviews before implementation**

Attempt Claude Code plan review with:

```bash
claude --effort max --permission-mode plan --no-session-persistence --tools Read,Grep,Glob,LS,Bash -p "$(cat docs/reviews/claude-code-stage-290-plan-review-prompt.md)"
```

If Claude Code times out or produces no review, record that honestly and use opencode fallback:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-290-plan-review-prompt.md)"
```

Inspect and clean review artifacts before committing them. Do not commit live-capture output.

## Task 5: Final Verification and Commit

**Files:**
- All Stage 290 files above.

- [ ] **Step 1: Run focused checks**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_app_contract.py tests/test_row_one_cli.py tests/test_row_one_render.py tests/test_first_run_smoke.py tests/test_row_one_docs.py -q -k "row_one"
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/render.py src/fashion_radar/cli.py scripts/check_first_run_smoke.py tests/test_row_one_app_contract.py tests/test_row_one_cli.py tests/test_row_one_render.py tests/test_first_run_smoke.py tests/test_row_one_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/render.py src/fashion_radar/cli.py scripts/check_first_run_smoke.py tests/test_row_one_app_contract.py tests/test_row_one_cli.py tests/test_row_one_render.py tests/test_first_run_smoke.py tests/test_row_one_docs.py
```

- [ ] **Step 2: Run full release gate**

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

- [ ] **Step 3: Request code review**

Follow `docs/REVIEW_PROTOCOL.md`: attempt Claude Code code review first, then opencode fallback if unavailable. Fix critical/important findings.

- [ ] **Step 4: Commit and push**

Use exact staging, then commit:

```bash
git add README.md docs/row-one.md schemas/row-one-app.schema.json schemas/row-one-manifest.schema.json scripts/check_first_run_smoke.py src/fashion_radar/cli.py src/fashion_radar/row_one/render.py tests/test_first_run_smoke.py tests/test_row_one_app_contract.py tests/test_row_one_cli.py tests/test_row_one_render.py tests/test_row_one_docs.py docs/superpowers/plans/2026-07-04-stage-290-row-one-card-information-sections-plan.md docs/reviews/claude-code-stage-290-plan-review-prompt.md docs/reviews/claude-code-stage-290-plan-review.md docs/reviews/opencode-stage-290-plan-review-prompt.md docs/reviews/opencode-stage-290-plan-review.md docs/reviews/opencode-stage-290-plan-rereview-prompt.md docs/reviews/opencode-stage-290-plan-rereview.md

git commit -m "Stage 290: add row one card information sections"
git push origin main
```

## Definition of Done

- Generated ROW ONE app payload validates as `row-one-app/v8`.
- Every app `contentCard` includes ordered `information_sections` with five display-ready sections.
- Each section body mirrors an existing localized card field exactly.
- Empty editions remain valid without cards.
- `row-one status` and first-run smoke reject schema-valid semantic drift in information sections.
- README and `docs/row-one.md` document the feature as app-facing information organization only.
- No dependency, lockfile, collection, ranking/scoring, compliance-review, network, generated report, or story-ID changes are introduced.
- Full release gate passes before commit.

## Stage 266 Plan Review

I verified the plan against the current codebase (`render.py`, `templates.py`, `models.py`, both schemas, the render/contract/docs/package tests, `pyproject.toml`, `ops.py`, and the docs being edited).

### Critical

**C1 — Task 3 render tests are pinned to the wrong `_edition()` fixture and cannot pass after a correct implementation.**
The tests are added to `tests/test_row_one_render.py`, whose `_edition()` uses HTML-special values (`headline='The Row <signals> "quiet" demand'`, `summary.en="Original source summary: The Row signal with <angle> detail."`, `editorial_takeaway.en="The Row is today's priority signal."` — see `tests/test_row_one_render.py:26,29,37`). But the new assertions match the *other* fixture in `tests/test_row_one_app_contract.py:55,56,58`:
- `test_render_row_one_site_includes_lead_story_block`: `assert "The Row signal"` and `assert "Editorial takeaway."` — neither substring is rendered (headline escapes to `The Row &lt;signals&gt;…`).
- `test_render_row_one_site_includes_index_and_detail_metadata`: `content="Source summary."`, `og:title content="The Row signal`, `twitter:title content="The Row signal">` — all three miss (detail description is the full escaped summary; titles are the escaped `<signals>` headline).

The TDD step says "Expected: PASS" — it will FAIL. Rewrite these assertions against the render fixture's actual escaped values.

### Important

**I1 — Manifest schema timestamp regex is over-escaped.** The plan's code block shows `"pattern": "^\\\\d{4}-…"` (four backslashes). Transcribed verbatim, JSON parses to regex `^\\d{4}` (literal backslash+d), which rejects `2026-07-02T04:00:00Z` and breaks `test_row_one_manifest_schema_validates_generated_payload` + the empty-edition test. Use two backslashes to match `schemas/row-one-app.schema.json:29` (`^\\d{4}-\\d{2}-\\d{2}T…`).

**I2 — Drift parametrize case `app_contract.path → "/abs/edition.json"` expects the wrong message.** `path` is a `const` (`schemas/…` plan §Task1 Step4), so jsonschema emits `"'data/edition.json' was expected"`, not `"does not match"`. The same parametrize list already uses `"was expected"` correctly for `contract_version`. Change this case's `match` to `"was expected"`.

**I3 — Docs test/checklist wording mismatch.** The test asserts `"do not upload generated ROW ONE site artifacts" in checklist.lower()`, but the plan's `github-upload-checklist.md` addition says "without uploading generated ROW ONE site artifacts." The pinned substring is absent → docs test fails. Align the wording.

### Minor

- **M1** — `build_row_one_manifest_payload` recomputes `build_row_one_app_payload(edition)` a second time (render already built it for `edition.json`), doubling story/evidence iteration and `safe_external_url` calls. Pass the already-built `app_payload` in instead; this also matches the design's "from the same `RowOneEdition` object" intent and removes any drift risk.
- **M2** — README step is underspecified ("add `docs/row-one.md` to the docs list and add a sentence"). The test pins the exact substring `"docs/row-one.md"`; provide the concrete line so the implementer doesn't miss it.
- **M3** — Lead story is intentionally also kept in the section grid (design acknowledges). Fine, but the top story now appears twice on the homepage — acceptable for v1, just noting.

### Verified correct (no blockers)
- `row-one-app/v1` stays **backwards compatible**: `edition.json` and its schema are untouched; only a sidecar `data/manifest.json` + HTML presentation are added.
- Manifest is **small, stable, schema-validated, non-duplicative** (counts/paths/readiness/capabilities only — no story/section arrays, no host/port/absolute URLs).
- **Boundaries correct**: generated `data/manifest.json` lives under runtime `reports/…/data/` (never committed; `data/` is already forbidden in release); shipped `schemas/row-one-manifest.schema.json` is auto-included in the sdist via hatchling VCS defaults — **no `pyproject.toml` change needed**.
- Lead story + SEO/social metadata are **presentation-only** (`templates.py`); no change to collection/matching/scoring/ranking/scheduling/server/cleanup/app-payload. `--latest-only` already wipes the whole `data/` dir, so the manifest is cleaned correctly.
- First-run doc command flags (`--config-dir/--data-dir/--reports-dir/--output-dir/--as-of/--latest-only/--dry-run-serve-url`) match the real `row-one build`/`preview` CLI (`ops.py:40-52`).
- **No** new collector, LLM call, image generation, paid API, deployment, system service, or compliance-review product feature is introduced.

### Verdict
**Revise before implementation.** Architecture, scope boundaries, and backwards-compatibility are sound, but C1 plus I1–I3 mean the plan cannot be executed verbatim to a green suite. Fix C1 and I1–I3 (and ideally M1–M2), then proceed.

# Stage 263 Plan Review (opencode fallback, GLM-5.2 max)

## Critical findings

**C1. `jsonschema` is not installed in the default dev/test environment, but the new test hard-imports it.**
`tests/test_row_one_app_contract.py` (Task 1, Step 3 / Task 3) does `from jsonschema import Draft202012Validator`. `jsonschema` is **not** declared in `pyproject.toml`. In `uv.lock` it is only reachable transitively via `altair` → `streamlit` → the **`dashboard`** extra. The dev group is `pytest, pytest-cov, ruff, fashion-radar[article]` (`pyproject.toml:70-76`), so `UV_NO_CONFIG=1 uv sync --locked --dev` (Task 6, Step 1) does **not** install it. Result: the release gate fails at collection with `ModuleNotFoundError: No module named 'jsonschema'`. The plan's Files/Artifacts list does not include `pyproject.toml` or `uv.lock`, and no task adds the dependency.
The Tech Stack hedge ("`jsonschema` already available … if present or schema structural tests otherwise") is factually wrong for the default env and the fallback branch is unimplemented.
**Fix (pick one):** (a) add `jsonschema` to `[dependency-groups].dev` **and** `[project.optional-dependencies].dev`, regenerate the frozen lock via the mirror-frozen install flow, and add a task plus `pyproject.toml`/`uv.lock` to the Files list; or (b) rewrite the schema test with stdlib structural checks (no `jsonschema`). Option (a) is recommended.

## Important findings

**I1. TDD ordering is muddled.** `tests/test_row_one_app_contract.py` is created in Task 1 but `schemas/row-one-app.schema.json` is not created until Task 3. At Task 1 Step 4 the test goes red via `FileNotFoundError` on `SCHEMA.read_text()`, not via a meaningful assertion. Move creation of the schema test into Task 3 (alongside the schema file) so red→green reflects validation logic.

**I2. Schema `format` keywords are not enforced by the planned test.** `Draft202012Validator(schema).validate(payload)` treats `format` (`uri`, `date-time`) as annotation-only unless `format_checker=...` is passed. So the spec/plan claim that the schema "validates … URL/date fields" is only type-level (`string|null`). Either enable `format_checker=draft202012_format_checker` in the test, or soften the docs/plan language. This directly affects review-focus #6.

**I3. Coverage regression in `test_render_row_one_site_writes_json_payload`.** Task 1 Step 1 replaces the test body and drops existing assertions for story-level `summary`, `editorial_takeaway`, `signal_context`, and `reader_path` localized text (the Stage 261/262 value the contract is meant to expose). Preserve those assertions alongside the new contract fields.

**I4. Strengthen `contract_version` in the schema.** Use `"const": "row-one-app/v1"` (or enum) rather than a free string so a wrong/unknown version fails validation explicitly.

## Minor findings

- **M1.** `_app_detail_href` returns `str | None`, but `_write_detail_pages` (render.py:78-87) already raises on any invalid `detail_path` before the JSON write, so `detail_href` is never `null` in emitted payloads. Make the schema require `detail_path`/`detail_href` as strings and either simplify the helper or document the branch as unreachable.
- **M2.** `_section_for_story` raises `ValueError` for a story whose `section_key` is absent from `edition.sections`. `build_row_one_edition` always emits all 5 sections (edition.py:30-65,118), so this won't trigger in practice, but for hand-built editions it's a new hard failure where the old dump rendered silently. Low risk.
- **M3.** `evidence_count` counts only safe URLs while `evidence[]` still emits unsafe entries with `url: null` (intentional, matches Stage 262). Ensure schema has `evidence_count: integer, minimum 0` and `evidence.url: ["string","null"]`.
- **M4.** `schemas/` ships in sdist but not the wheel (`packages = ["src/fashion_radar"]`). Acceptable for v0.1.0; revisit if app clients should discover the schema at runtime.
- **M5.** Review artifacts under `docs/reviews/**` and `docs/superpowers/**` are excluded from sdist (pyproject.toml:85-88). Per AGENTS.md, ensure each review record has complete content (no stubs/truncation) before commit.

## Scope-safety check (clean)

No internal reader of the old `edition.json` shape exists — only the writer at `render.py:44`. HTML rendering (`render_index_html`/`render_detail_html`), detail-page writes, `latest_only` cleanup, server dry-run, `schedule`, source collection, matching, ranking, story IDs, and social integrations are all untouched. Replacing the old sanitized dump is reasonable; the decision against shipping `edition.raw.json` now is sound (no committed external consumer; avoids dual surfaces drifting). Nullable URL fields (safe → string, unsafe → `null`) and nullable `published_at`/`published_date` are appropriate.

## Final verdict

**Proceed after fixes.** C1 (the `jsonschema` dependency/install gap) will break the Task 6 release gate and must be resolved before implementation — either declare `jsonschema` in dev deps and regenerate the frozen lock, or drop `jsonschema` for stdlib structural validation. Apply I1–I4 during implementation; M1–M5 can be handled inline.

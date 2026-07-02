# Stage 263 Release Review

**Scope verified:** full working tree (10 modified + 13 untracked files), schema/builder alignment, tests, docs, plan/spec, all three review artifacts, lockfile, and archive registration. Focused suite re-run green: `56 passed` (render + contract + docs + cli).

## Critical

None.

## Important

**I1. The plan's `git add` checklist omits 5 essential modified files — a literal run would ship a broken commit.**
`docs/superpowers/plans/2026-07-02-stage-263-row-one-app-contract-plan.md:410` lists the commit set, but excludes:
- `docs/architecture.md` — required by `tests/test_row_one_docs.py::test_row_one_docs_describe_versioned_app_json_contract` (asserts `"versioned app json"` in architecture).
- `pyproject.toml` + `uv.lock` — the `jsonschema>=4.26.0` dev dependency that resolved plan-review C1. Without both, a fresh-clone `uv sync --locked --dev` fails (lock/pyproject drift) and `tests/test_row_one_app_contract.py` raises `ModuleNotFoundError: jsonschema`.
- `scripts/check_package_archives.py` + `tests/test_package_archives.py` — the `schemas/row-one-app.schema.json` sdist registration; committing one without the other leaves the gate inconsistent.

**Action before commit:** stage all 10 modified tracked files, not just the plan's subset (e.g. `git add -A`, or append the five names). The working tree itself is correct and release-ready — only the commit step needs care.

## Minor

- **M1 (carried, N1).** Date `pattern`s enforce shape, not calendar ranges (`2026-13-99T...` still validates). Already documented in `opencode-stage-263-code-rereview.md:31`; non-blocking since `_isoformat_z` always emits valid RFC3339. Consider `rfc3339-validator` before exposing `row-one-app/v1` to an external client.
- **M2 (carried).** `localizedText` schema (`row-one-app.schema.json:66-73`) requires `minLength:1` but `LocalizedText` allows empty strings. Safe in production (`build_row_one_edition` always emits non-empty); only hand-built editions hit it.
- **M3 (carried).** `edition_date` is a full `date-time`, not a plain date (`render.py:99`, schema:31-34). Matches spec/design intent; name may mislead app authors vs. `published_date`.
- **M4 (doc lag, harmless).** Plan Task 2's `build_row_one_app_payload` sketch omits top-level `story_count`/`evidence_count`, but the implementation (`render.py:95-105`), schema, and design spec all include them. Implementation is the more complete source of truth; no code defect.

## Positive checks

- **Schema ↔ builder alignment is exact.** Top-level, section, story, story-section, evidence, and localized-text objects all match between `render.py` field sets and schema `required`/`properties` with `additionalProperties: false`. `const` version + closed objects applied.
- **No internal reader of the old `edition.json` shape** exists outside `render.py`; HTML rendering, collection, matching, ranking, detail pages, cleanup (`data` added to `GENERATED_CHILDREN`), server, and schedule are untouched. No social/platform behavior introduced — all deltas are render/docs/tests/schema/lockfile.
- **Dependency/lockfile clean:** `jsonschema` added to both `[project.optional-dependencies].dev` and `[dependency-groups].dev`; `uv.lock` delta is 4 lines, no mirror/private-index URLs.
- **Review artifacts are coherent, substantive bodies** (plan-review 34 lines, code-review 39 lines, code-rereview 37 lines); all prompt files non-empty (20–67 lines). Absent `claude-code-stage-263-*.md` review *outputs* are consistent with the documented Claude timeouts; opencode fallback reviews are captured per AGENTS.md.
- **No forbidden content:** no secrets/tokens, no DB/cache/dist/`__pycache__` artifacts, no mirror or private index URLs in any diff. New source files are not gitignored.

## Verdict

**Release approved with minor notes.** The working tree is coherent and release-ready; schema, tests, docs, plan/spec, reviews, archive registration, and lockfile are all consistent and the full gate is green. The single actionable item is **I1**: ensure the commit stages all 10 modified files (not just the plan's subset), or the pushed tree will fail the fresh-clone gate. M1–M4 are non-blocking follow-ups for when `row-one-app/v1` is exposed to an external client.

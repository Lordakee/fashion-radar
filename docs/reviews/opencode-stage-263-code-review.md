# Stage 263 Code Review (opencode fallback, GLM-5.2 max)

Scope verified read-only against the uncommitted tree. Focused suite re-run is green (150 passed), confirming the claimed verification. No scope violations: collection, matching, ranking, HTML rendering, detail pages, cleanup, server, and schedule paths are untouched.

## Critical

None.

## Important

**I1. Schema `format` assertions on date fields are not actually enforced (false assurance).**
`schemas/row-one-app.schema.json:26-33,201-222`, `tests/test_row_one_app_contract.py:81,89-92`. The schema declares `format: "date-time"` on `generated_at`/`edition_date`/`published_at` and `format: "date"` on `published_date`, and the test enables `FormatChecker()`. But `jsonschema`'s FormatChecker silently skips `date-time`/`date`/`uri` unless optional packages (`rfc3339-validator`/`strict_rfc3339`/`rfc3987`) are installed — none are present. Verified directly:
```
FormatChecker().iter_errors("not-a-date")   -> []
FormatChecker().iter_errors("2026-13-99")   -> []
```
URL fields are rescued by their `pattern` (`safeExternalUrl` lines 88-89), but the date fields have **no pattern fallback**, so their only real enforcement is "string|null". The plan-review I2 flagged format-as-annotation; the applied fix (adding `FormatChecker`) didn't go far enough because the checker package is absent. A `contract-drift` case for a malformed `generated_at` would currently pass. Recommend (for v1, dependency-free): add a `pattern` next to each date/date-time `format`, or add `rfc3339-validator` to the dev group. Not a runtime defect — the builder always emits valid RFC3339 via `_isoformat_z` — but the "validated contract" assurance is weaker than presented.

**I2. `evidence_count` can diverge from `len(evidence)` and the public doc doesn't say so.**
`src/fashion_radar/row_one/render.py:145-146,170-171`, `docs/row-one.md:73-76`. `evidence[]` keeps unsafe-URL entries as `url:null`/`href:null`, while `evidence_count` counts only safe URLs (e.g. in `test_render_row_one_site_writes_json_payload`, count=1 but `len(evidence)`=2). The design spec documents this intent (specs…design.md:113-114), but `docs/row-one.md` only says "evidence counts (`evidence_count`)" / "Unsafe external URLs are written as `null`" without stating the count excludes null-URL entries. For a stable app contract, add one line to the App JSON Contract section, or omit null-URL entries from `evidence[]` so count == len.

## Minor

- **M1. Schema stricter than the model for `localizedText`.** `schema:63-72` requires `minLength:1` on `zh`/`en`, but `LocalizedText` (`models.py:19-23`) allows empty strings. Production builder always emits non-empty (`edition.py:34-60`), so safe today; a hand-built edition with empty `dek` would fail validation. Consider `min_length=1` on the model or a doc note.
- **M2. Sparse-section HTML/JSON divergence.** `_section_for_story` (`render.py:149-157`) synthesizes a section so JSON includes the story, but HTML's `_render_section` (`templates.py:414-415`, `next(...)`) only renders sections in `edition.sections`. `build_row_one_edition` always emits all 5 sections (`edition.py:31-62`), so this only affects hand-built editions (covered by `test_row_one_app_payload_preserves_rendering_for_sparse_sections`). Intentional asymmetry; a one-line code/doc comment would help future maintainers.
- **M3. Duplicated section-key enum.** `sectionKey` enum (`schema:74-82`) is re-listed verbatim in the `href` patterns (`schema:115,136`). Adding a key needs two edits. Fine for v1.
- **M4. Redundant double UTC normalization.** `_story_payload` (`render.py:121,138`) runs `_utc_datetime` then `_isoformat_z`, which calls it again. Idempotent/harmless.
- **M5. `edition_date` is a full `date-time`, not a date** (`schema:30-33`, `render.py:99`). Matches `generated_at` and the spec; just flag that the name may mislead app authors vs. the plain-date `published_date`.

## Positive checks

- Dependency/lockfile: `jsonschema>=4.26.0` added to both `[project.optional-dependencies].dev` and `[dependency-groups].dev` (`pyproject.toml:65,73`) — resolves plan-review C1. `uv.lock` delta is minimal (4 lines). `schemas/row-one-app.schema.json` registered in sdist required paths (`scripts/check_package_archives.py:91`, `tests/test_package_archives.py`).
- Regression: `data` added to `GENERATED_CHILDREN` (`render.py:19`) and both `latest_only` cleanup tests updated to cover the `data/` child — stale `edition.json` is now removed. Stage 261/262 localized-text assertions preserved (plan-review I3 addressed). `const` version + closed objects applied (plan-review I4 addressed).
- Tests: good coverage of counts, undated stories, tz→UTC normalization, UTC `published_date`, sparse sections, href sync, URL sanitization, and contract-drift rejection (version/extra-prop/section-key/detail-href/zh-required); empty-payload case covered.
- Review hygiene: the one committed review body, `docs/reviews/opencode-stage-263-plan-review.md`, is complete and substantive (no stubs/chatter/truncation). No stale contract examples in `docs/row-one.md`. Note: `claude-code-stage-263-{plan,code}-review.md` bodies are absent — consistent with the stated Claude timeouts, but if either was actually produced it should be committed or the plan items updated.

## Verdict

**Approved with minor notes.** The contract, builder, schema, and tests are correct and internally consistent, and the dependency/install gap from the plan review is resolved. The one substantive item to address before locking `row-one-app/v1` for an external client is I1 (date `format` is non-enforced — add a `pattern` or `rfc3339-validator`); I2 is a one-line doc clarification. Everything else is minor.

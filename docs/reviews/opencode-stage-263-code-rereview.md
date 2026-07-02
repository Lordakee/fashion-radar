# Stage 263 Code Rereview (opencode, GLM-5.2 max)

Reread read-only against the uncommitted tree. Focused suite re-run is green (**132 passed**). Direct schema probes confirm the pattern enforcement behavior.

## Previous Important findings — resolution

**I1 (date `format` non-enforced) — Fixed, with one residual Minor (see N1).**
Patterns now sit beside every date/date-time `format`: `generated_at`/`edition_date` (`schemas/row-one-app.schema.json:29,34`), `published_at` (`:208`), `published_date` (`:220`). Negative drift cases added in `tests/test_row_one_app_contract.py:216-227` cover `generated_at="not-a-date"`, a space-separated `published_at`, and `published_date="2026-7-2"`. Verified directly that `"not-a-date"` and `"2026-07-02 04:00:00"` are now **rejected**, resolving the false-assurance concern.

**I2 (`evidence_count` divergence undocumented) — Fixed.**
`docs/row-one.md:73-76` now states verbatim that `evidence_count` counts only safe clickable evidence URLs and that unsafe/missing entries remain with `url: null` / `href: null`. Aligns with the builder at `render.py:145-146,170-171`.

**UTC date derivation — Fixed.**
`render.py:138` derives `published_date` from the UTC-normalized `published_at_utc` (computed at `:121`), not the source-tz date. Regression test `test_row_one_app_payload_published_date_uses_utc_date` (`tests/test_row_one_app_contract.py:141-156`) proves `2026-07-02 00:30 +08:00` → `published_at=2026-07-01T16:30:00Z`, `published_date=2026-07-01`. Correct.

**Review hygiene — Fixed.**
`docs/reviews/opencode-stage-263-code-review.md` is a single coherent 39-line body, no stubs/chatter/truncation.

## New regressions

None. Verified:
- Contract shape: required fields, `const` version (`:20`), `additionalProperties: false` on root and all sub-objects.
- URL/date nullability: `safeExternalUrl` (`:85-96`) and `published_at`/`published_date` (`:203-226`) correctly nullable.
- latest-only cleanup: `data` in `GENERATED_CHILDREN` (`render.py:19`); covered by existing cleanup tests (green).
- Package archive: `schemas/row-one-app.schema.json` registered in both `scripts/check_package_archives.py:91` and `tests/test_package_archives.py`.
- `uv.lock`: minimal 4-line delta, `jsonschema>=4.26.0` only, no mirror URLs, public-index clean.
- No social/platform behavior added — all deltas are render/docs/tests/schema/lockfile.

## Minor

- **N1 (residual of I1): pattern enforces shape, not calendar ranges.** Direct probe: `generated_at="2026-13-02T04:00:00Z"`, `"2026-07-99T..."`, `"2026-07-02T99:00:00Z"` are all still **accepted** because `\d{2}` doesn't bound ranges. This is inherent to the chosen pattern-over-`rfc3339-validator` path (which the original review offered as either/or). Not a runtime defect — `_isoformat_z` always emits valid RFC3339 — but app clients should not assume the schema alone rejects calendar-invalid dates. Consider a one-line note in `docs/row-one.md`, or add `rfc3339-validator` to the dev group, before exposing `row-one-app/v1` externally. Non-blocking.
- **M1 (carried forward).** `localizedText` schema (`:63-72`) requires `minLength:1` but `LocalizedText` model allows empty strings. Safe in production; only hand-built editions hit it.
- **M4 (carried forward, now intentional).** `_story_payload` pre-normalizes to `published_at_utc` to derive `published_date`, then `_isoformat_z` re-normalizes — idempotent and required for the UTC-date fix. Fine.

## Verdict

**Approved with minor notes.** All previous Important findings are fixed or acceptably documented, no new regressions, lockfile clean, no platform-integration drift. N1 is the only item worth a follow-up before locking the contract for an external client; it is non-blocking for the v0.1.0 free-first core.

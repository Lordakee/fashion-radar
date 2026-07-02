## opencode Stage 264 Post-Polish Review

Scope: only the two final polish changes (smoke-test mock alignment + ROW ONE docs en/zh note).

### Critical
None.

### Important
None.

### Minor
- **m1. Mock alignment is faithful; the smoke *validator* still uses label-only substrings.** `tests/test_first_run_smoke.py:4225-4249` now mirrors the real CLI (`cli.py:1456-1467`) exactly — English-only `Readiness: empty`, port `8787`, `Open: http://127.0.0.1:8787` (no `/index.html`), correct field order, and the empty-sections list matches `edition.py:33-59` (Top Stories → Brand Moves → Celebrity Style → Hot Products → Rising Radar). However, `assert_output_contains_text` (`check_first_run_smoke.py:2816-2822`) still matches only `"Stories:"`, `"Sections:"`, etc., so a future value divergence would still slip through. This is pre-existing, not introduced here — non-blocking.
- **m2. `Generated at:` mock value is a plausible stand-in, not the true source.** The mock emits `smoke.AS_OF` for `Generated at:`, whereas the real CLI prints `readiness.generated_at` derived from `report.metadata.generated_at`. Format (ISO-8601 `Z`) is consistent, and the validator only checks the substring — cosmetic.

### Checks performed
- Contract intact: `schemas/row-one-app.schema.json` untouched (no diff); `test_row_one_app_contract.py` 17 passed; `render.py` still emits `edition_date` via `isoformat_z`.
- Docs/test consistency: `test_row_one_docs.py:137-153` now requires `"compact english status labels"` + `"bilingual english/chinese labels"`, both present at `docs/row-one.md:103-104`. Doc claim matches code (CLI uses `.en`; homepage renders en/zh, confirmed by `test_row_one_render.py:214`).
- No stale references to the old mock (`可阅读` in preview, port `8000`, `/index.html` Open URL) remain; surviving `可阅读` hits are the legitimate homepage/readiness-`zh` paths.
- Tests: 289 passed across the six relevant files. Ruff clean on touched modules.

### Verdict
**Approved for release.** The two polish changes correctly resolve prior m1/m2 with no release blockers, no test/doc inconsistency, and no `row-one-app/v1` contract drift. The two minor notes are pre-existing/cosmetic and may be deferred.

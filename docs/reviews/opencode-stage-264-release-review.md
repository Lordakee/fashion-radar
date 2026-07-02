# opencode Stage 264 Release Review

## Critical
None.

## Important
None.

## Minor

- **m1. Smoke unit-test fixture misrepresents real `preview` output.** The `row-one preview` mock in `tests/test_first_run_smoke.py:4210` emits `Readiness: ready / 可阅读`, `Stories: 2`, `Empty sections: none`, and `Open: http://127.0.0.1:8000/index.html`. The real CLI prints English-only readiness (`Readiness: empty` / `ready`), default port `8787`, and `Open: http://127.0.0.1:8787` (no `/index.html`). Assertions only match substrings (`Readiness:`, `Stories:`, `Open:`) so tests pass, and the real `scripts/check_first_run_smoke.py` exercises true output — but the mock would silently miss a regression in the bilingual/port format and could mislead a maintainer who tightens it. Non-blocking.
- **m2. CLI `preview` stdout is English-only while the homepage strip is bilingual.** `cli.py:1455-1462` prints `Readiness: {readiness.readiness.en}` and `Empty sections: {readiness.empty_sections.en}` only. This matches the design's machine-readable example (design L107-118), so it is by-design — but the en/zh asymmetry versus the homepage is worth a one-line docs note. Cosmetic.

## Positive checks

- **No `row-one-app/v1` contract drift.** `schemas/row-one-app.schema.json` is unchanged (not in diff); `build_row_one_app_payload` (`render.py:94-106`) still emits `edition_date` as `isoformat_z(...)` (date-time). Confirmed on a real build: `"edition_date": "2026-07-02T04:00:00Z"` matches the schema pattern; `test_row_one_app_contract.py` passes. The readiness `edition_date` (date-only `2026-07-02`) lives only in the homepage strip / Python dataclass, never in the JSON — documented as intentional display copy (design L123-125).
- **Scope boundaries intact.** New `readiness.py`/`utils.py` use only stdlib `urlsplit` (scheme/netloc *validation*, not fetching) and `datetime`. No `requests`/`httpx`/`selenium`/`playwright`/`subprocess`/LLM/translate/login/cookie/token. No source collection, scoring, ranking, scheduling-semantic, scraping, connector, or compliance-review behavior added. Readiness is derived solely from the existing `RowOneEdition`. The `socket` hits are pre-existing Stage 260 local-server code, not new.
- **Schedule check is defense-in-depth, not a semantic change.** `validate_row_one_schedule_output` only *asserts* that printed schedule text keeps `fashion-radar run` before `fashion-radar row-one build --latest-only`; it does not alter scheduling.
- **Internal plumbing is safe.** `RowOneRenderResult.edition` is a private dataclass field populated at the single construction site (`render.py:51`); `write_row_one_site_files` (`workflows.py:141`) returns it with no signature change, so `preview` reads `result.edition` without touching the JSON path.
- **No circular imports.** Graph is `templates → readiness → {models, utils}` and `templates → utils`, `render → {templates, utils}` — no back-edge to `templates`. `workflows.py` was correctly left unmodified (plan-rereview already validated this).
- **Build/preview output collision is safe.** Both share `ROW_ONE_OUTPUT_DIR_OPTION` (`reports/row-one/site`); `--latest-only` cleanup is marker-gated (`.row-one-site` written before clean), confirmed by the real smoke run.
- **Package guardrails symmetric.** `SDIST_REQUIRED_PATHS` (checker) and `SDIST_FILES` (fixture) both gained `docs/row-one.md` + all eight `row_one/*.py` including `readiness.py` and `utils.py` (prior m1 resolved); new failure test `test_rejects_sdist_without_row_one_doc` covers the doc.
- **Render assertions tightened.** Prior "near-tautological" `assert "1" in index_html` is now anchored on `'<span data-lang="en">1</span>'` / `'<span data-lang="zh">1 条</span>'` (prior m3 resolved).

## Verdict

**Approved for release.** No Critical or Important issues; no `row-one-app/v1` contract drift and no boundary violations. m1/m2 are cosmetic mock/docs asymmetries that do not affect correctness or release safety and may be tidied in a later polish stage.

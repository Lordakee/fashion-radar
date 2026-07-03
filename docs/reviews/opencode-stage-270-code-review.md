## Stage 270 Code Review — APPROVED

Independently re-ran the focused gate (`508 passed`), `ruff check` (clean), `check_release_hygiene.py` (passed), and `check_first_run_smoke.py` (passed) — all claims in the prompt reproduced.

### Verification of review-focus criteria
1. **Runtime payload correctness** — `build_row_one_runtime_payload` (`src/fashion_radar/row_one/render.py:175-217`) is internally consistent: counts derive from the same `app_payload` as the manifest, readiness mirrors `build_row_one_readiness`, and the generated payload validates against `schemas/row-one-runtime.schema.json` with a full contract-drift suite (`tests/test_row_one_app_contract.py:129-192, 622-663`).
2. **`row-one status` correctness/maintainability** — `_validate_row_one_status_payloads` (`src/fashion_radar/cli.py:1607-1716`) does strong cross-file agreement checks (timestamps, counts, readiness status across runtime/manifest/edition) with clear labeled errors; JSON + text outputs both tested (`tests/test_row_one_cli.py:515-651`).
3. **Schema/tests/docs alignment** — schema is strict (`additionalProperties: false`, consts/enums); docs tests pin the contract phrases; smoke script mirrors the validator.
4. **Manifest stability** — confirmed unchanged: `schemas/row-one-manifest.schema.json` is unmodified, `build_row_one_manifest_payload` gained no `runtime_path`, and `tests/test_row_one_app_contract.py:153` explicitly asserts `runtime_path not in manifest["site"]`.
5. **Smoke/release coverage** — real subprocess serve smoke on an ephemeral port fetching 6 assets (`tests/test_row_one_cli.py:739-798`); runtime validation wired into `check_first_run_smoke.py:1169-1252, 2998-3042`; sdist requires the new schema with a dedicated test (`tests/test_package_archives.py:569-585`, `scripts/check_package_archives.py:94`).

### Required fixes before commit/push
None.

### Optional follow-ups (non-blocking)
- **Nit, test fidelity:** the first-run-smoke mock hard-codes `"zh": "empty"` for the empty readiness (`tests/test_first_run_smoke.py:4317, 4345`), whereas real generation produces `"暂无故事"` (`src/fashion_radar/row_one/readiness.py:44`). Harmless (schema only requires non-empty `zh`) but cosmetically inaccurate; consider matching the real value.
- **Validator parity:** `validate_row_one_runtime` (`scripts/check_first_run_smoke.py:1233-1236`) asserts `default_host`, `default_port`, `local_url` but omits `serve.lan_url_hint`, which the CLI validator does check (`src/fashion_radar/cli.py:1669-1673`). Consider adding it for full parity.
- **Status test coverage:** `row-one status` CLI tests cover only the empty-site case directly; the "ready" runtime contract is covered in `test_row_one_app_contract.py`, but an end-to-end `status` run on a populated site would close the loop. Optional.

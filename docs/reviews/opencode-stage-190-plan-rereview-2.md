# Stage 190 Plan Rereview 2

## Critical

None.

## Important

None. All four review questions resolve favorably against the current source.

1. **Skipped vs. invalid-config scoping is correct.** `load_source_config` → `SourceConfig.model_validate` validates the *entire* file atomically via `SourceDefinition.validate_source_target` (`models/source.py:83-90`). A disabled RSS source missing `url` (or disabled GDELT missing `query`) raises `ValidationError`, which `settings.py:178-179` wraps as `ConfigError`, so `build_source_liveness_report` returns a single `invalid_config` finding with empty `results` — no partial skipped row. The design states this precisely (spec lines 195-197), the implementation sketch builds skipped rows only *after* a successful load (plan line 485), and `test_invalid_disabled_source_returns_invalid_config_instead_of_skipped_row` (plan lines 233-261) plus `test_invalid_source_config_returns_error_report_without_network_call` lock it in.

2. **GDELT rate-limit wording is technically accurate.** `FashionHttpClient._last_request_by_domain` is per-instance (`utils/http.py:29,89-100`), and `GdeltCollector.collect` creates a fresh client per source (`gdelt.py:30-36`) using `gdelt_http_settings(source)` (`gdelt.py:55-61`). The plan mirrors this (`_probe_gdelt_source` passes `gdelt_http_settings(source)` to the factory), so no command-global domain timing is maintained across separate GDELT sources — exactly as the spec (lines 213-215) and plan (lines 847-849) disclose. The `test_gdelt_liveness_passes_gdelt_http_settings_to_client_factory` assertion (`per_domain_delay_seconds == 2.0` from `rate_limit_per_second: 0.5`) is only satisfiable via `gdelt_http_settings`, not raw `source.http`.

3. **TDD coverage is sufficient** for the three flagged edge cases: `test_liveness_probe_order_matches_config_and_failures_do_not_abort_later_sources` (plan lines 776-816) covers both probe order and continue-after-failure in one test (asserts `requested_sources == ["Broken Feed", "Live Feed"]` and that the second probe still runs and returns `LIVE` after the first `FAILED`).

## Minor

- **M1 — RSS settings path not explicit.** The plan explicitly says "For GDELT, pass `gdelt_http_settings(source)` to `client_factory(...)`" but never states the RSS/RSSHUB counterpart (pass `source.http`). With default settings the difference is unobservable (both yield `per_domain_delay_seconds=1.0`), so there is no test guarding an RSS source from accidentally receiving GDELT-derived settings. Suggest adding one line to Task 2 Step 3 and one assertion that an RSS probe receives plain `source.http` (e.g. set `http.per_domain_delay_seconds: 0.25` and assert the factory sees `0.25`, not the GDELT-floored `1.0`).

- **M2 — GDELT pacing inertness not noted.** The disclosure covers cross-source timing, but each liveness probe issues exactly one `get_json` per client, so `per_domain_delay_seconds` never triggers a sleep within a probe either (the `_last_request_by_domain` map starts empty and the client is closed after one call). "Reuses GDELT-aware settings" could read as if rate-limiting is partially enforced. A one-line clarification ("each probe issues a single request per client, so the per-domain delay is effectively inert; settings are reused only to mirror collector configuration") would prevent user overestimation. Not a correctness defect.

- **M3 — `_skipped_result` target derivation undocumented.** Skipped rows need `target_type`/`target`, and disabled sources may be RSS/RSSHUB (`url`) or GDELT (`query`). The helper is named but not specified. Trivial to implement correctly given all sources are schema-valid at that point, but spelling it out avoids an implementer guessing.

- **M4 — Date-format divergence.** JSON shape asserts `"checked_at": "...Z"` while the table asserts `"Checked at: ...+00:00"` (plan lines 158, 298). Both are correct for their consumers (`model_dump_json` vs. renderer formatting), but the implementer must not reuse one formatter for both. Worth a one-line note.

- **M5 — All-or-nothing file validation is intentional but unstated as UX.** One typo'd source suppresses all other rows (including 15 good ones) into a single `invalid_config` finding. This matches `source-pack-lint`/`collect_sources` behavior and the design's explicit ordering, so it is acceptable; a sentence in the design acknowledging the trade-off would help reviewers.

## Verdict

Approve for implementation. No Critical or Important blockers remain. The subagent edge cases are correctly resolved: skipped rows are provably scoped to schema-valid disabled sources (Q1), the GDELT rate-limit wording is technically accurate for the per-source `FashionHttpClient` design (Q2), and the TDD plan covers probe order, continue-after-failure, and `gdelt_http_settings(source)` injection (Q3). The five Minor items are clarity/robustness improvements (most notably M1's missing RSS-settings test and M2's pacing inertness note) that can be folded in during Task 2 without blocking the stage.

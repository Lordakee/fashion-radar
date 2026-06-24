# Stage 190 Plan Rereview 3

## Critical

None.

## Important

None. All five review questions resolve favorably against the current plan and spec.

1. **Release-gate token/header absence checks pass when absent.** The two guards in Task 5 Step 3 (plan:1443-1444) are explicit negated-existence checks:
   - `if rg -n 'ghp_[A-Za-z0-9]+' .; then exit 1; fi` — `rg` exits 0 only on a match, so the `then exit 1` fires solely when a token-like string is present; with no match `rg` exits 1, the branch is skipped, and the gate passes with no stdout (confirmed: `RG_EXIT=1` against the current tree, and `tests/test_release_hygiene.py:13` builds its fixture as `"ghp_" + ("a" * 36)`, so the literal never matches the regex).
   - `if git config --get-all http.https://github.com/.extraheader; then exit 1; fi` — `git config --get-all` exits 0 and prints only when the key is set, so the branch trips only on presence; unset → exit 1 → skipped → pass.
   The plan's own expected-output note (plan:1447-1448) states these print nothing and exit 0 on the clean case. Resolved.

2. **Probe-coverage test matrix is complete.** Task 2 Step 1 adds every named case:
   - RSSHub parity — `test_rsshub_liveness_is_probed_like_rss` (plan:827-850), asserting `source_type==RSSHUB`, `target_type=="url"`.
   - RSS/RSSHub `source.http` injection — `test_rss_liveness_passes_source_http_settings_to_client_factory` (plan:797-824), setting `http.per_domain_delay_seconds: 0.25` and asserting the factory observes `0.25` (this directly closes rereview-2 M1, with the implementation contract now stated at plan:1040).
   - GDELT `gdelt_http_settings(source)` — `test_gdelt_liveness_passes_gdelt_http_settings_to_client_factory` (plan:886-912), asserting `per_domain_delay_seconds==2.0` from `rate_limit_per_second: 0.5`, satisfiable only via `gdelt_http_settings` (plan:1041-1043).
   - Probe order + disabled-row position + continue-after-failure — `test_liveness_probe_order_matches_config_and_failures_do_not_abort_later_sources` (plan:957-1009) asserts `requested_sources == ["Broken Feed","Live Feed"]`, result order `["Broken Feed","Disabled Feed","Live Feed"]`, and statuses `FAILED/SKIPPED/LIVE` — so the disabled row stays in config position and the third source is still probed after the first threw. Resolved.

3. **Default-network/client guard is present.** `tests/test_source_liveness.py` carries an `autouse` fixture `forbid_default_network_client` (plan:103-116) that monkeypatches `source_liveness_module.FashionHttpClient` with an `AssertionError`-raising stand-in (`raising=False`, so it tolerates Task 1 before the symbol exists). The only network seam is the HTTP client (feedparser parses already-fetched text), so this guard fully prevents accidental real I/O. Resolved.

4. **CLI tests cover default table rendering and broad artifact non-creation.**
   - Default (no `--format`) table path — `test_source_liveness_default_table_uses_renderer_output` (plan:1106-1151) asserts the summary line `Sources: 1 total, 1 enabled, 0 disabled, 1 probed`, the row `Designer Feed`, `Boundaries:`, and the `Does not collect, store` boundary.
   - Read-only breadth — `test_source_liveness_does_not_create_config_data_report_or_workflow_artifacts` (plan:1231-1280) runs under `monkeypatch.chdir(workdir)` plus explicit `FASHION_RADAR_CONFIG_DIR/DATA_DIR/REPORTS_DIR`, then negates config/data/reports dirs, `fashion-radar.sqlite`, `*.sqlite*`, `collector-*`, `collector_runs*`, `fashion-radar-*.md/.json`, and `latest.md/latest.json/report-index.json`. Resolved.

5. **Docs tests include README and architecture coverage.** Task 4 Step 1 (plan:1359-1362) adds explicit README (`source-liveness` + the public pack path) and architecture (`Source Liveness`, `RSS/RSSHub`, `GDELT`) requirements. The natural and listed home is `tests/test_cli_docs.py`, which already reads both `README.md` (test_cli_docs.py:22) and `docs/architecture.md` (test_cli_docs.py:25); that file is in the RED run (plan:1369), the GREEN run (plan:1394), and the commit (plan:1474). Resolved.

## Minor

- **M1 — Target test file for README/architecture assertions is not named.** Task 4 Step 1 says "README docs test file *or an existing* README docs test" / "Architecture docs test file *or an existing* architecture docs test" without pinning `tests/test_cli_docs.py`. An implementer who reads this as "create a new file" would produce a test that is absent from the Files list (plan:24-26), the staged RED/GREEN commands, and the `git add` block — silently dropping out of the staged verification. One line naming `tests/test_cli_docs.py` as the target would remove the ambiguity.

- **M2 — Staged `-k` filter may skip README/architecture tests.** The Task 4 RED/GREEN commands use `-k "source_liveness or source_pack"` (plan:1369, 1394). A README/architecture test whose name contains neither token (e.g. `test_architecture_documents_liveness_diagnostics`) would not be selected in the staged check, though the full `pytest -q` in Task 5 Step 3 (plan:1436) would still catch it. Either name the new tests to include `source_liveness`, or drop/broaden the `-k` filter in Task 4 so README/architecture coverage is exercised during the staged GREEN, not only at the final gate.

- **M3 — `_skipped_result` target derivation still unspecified (carried from rereview-2 M3).** A skipped row needs `target_type`/`target` derived from type (`url` for rss/rsshub, `gdelt_query` for gdelt). Trivial because all sources are schema-valid at that point, but a one-line spec would prevent an implementer guessing. Not a blocker.

- **M4 — Token regex scope.** `ghp_[A-Za-z0-9]+` catches only classic PATs and not `github_pat_`/`gho_`/`ghs_`/`ghr_` prefixes. This is outside the literal question (the negated check correctly passes when nothing is present), but worth noting if broader secret coverage is ever desired.

## Verdict

Approve for implementation. No Critical or Important blockers remain. All five flagged issues are resolved: the release-gate guards are correct negated-existence checks that pass when no token/header is present (and produce no false positives against existing fixtures), the Task 2 test matrix covers RSSHub, RSS `source.http`, `gdelt_http_settings(source)`, probe order, disabled-row position, and continue-after-failure, the source-liveness suite carries an autouse default-client guard, the CLI tests pin the default table renderer and broad read-only artifact non-creation, and README/architecture docs coverage is wired through `tests/test_cli_docs.py`. The four Minor items are clarity/robustness refinements (most usefully M1–M2, naming the docs test file and aligning the staged `-k` filter) that can be folded in during Task 4 without blocking the stage.

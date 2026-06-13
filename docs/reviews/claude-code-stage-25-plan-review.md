Findings list:

## Important

### 1. `docs/superpowers/specs/...` Output Model; `docs/superpowers/plans/...` Task 2 implementation
**Issue:** The proposed output reuses `CandidateReport` including `representative_items.source_url`, `title`, and `summary`. For `manual_import` rows, those fields are user-supplied local import content and may contain private/account URLs, local/import paths, raw comments, or other sensitive/manual-review text. This conflicts with the stated boundary that the command must not leak import paths, account/private fields, raw comments, or internals.

**Concrete fix:** Do not reuse the full public `CandidateReport` shape for this command unless representative items are removed or narrowed. Define an imported-candidate-specific public model, for example:

- candidate aggregate fields: `phrase`, `candidate_type`, `label`, `score`, `current_mentions`, `baseline_mentions`, `distinct_sources`, `growth_ratio`, `first_seen_at`
- optional safe representative metadata only: `source_name`, `published_at` / `collected_at` if needed
- omit `source_url`, `title`, `summary`, candidate `contexts`, item IDs, match data, aliases, and import/raw fields

Update JSON/table tests to assert these fields are absent, especially `source_url`, `title`, and `summary`.

---

### 2. `docs/superpowers/plans/...` Task 2 read-only test
**Issue:** `test_query_imported_candidates_uses_readonly_engine()` only calls `imported_candidates_module.create_readonly_sqlite_engine(db_path)` directly and proves that helper rejects writes. It does not prove `query_imported_candidates()` uses the read-only engine. The implementation could accidentally use `create_sqlite_engine()` and this test would still pass.

**Concrete fix:** Mirror the existing `test_query_imported_signals_uses_readonly_engine` pattern:

- monkeypatch `imported_candidates_module.create_readonly_sqlite_engine`
- record calls
- invoke `query_imported_candidates(...)`
- assert the read-only factory was called with `db_path`

Optionally add an additional mutation guard by checking table names / schema before and after query, but the monkeypatch call assertion is the key regression test.

---

### 3. `docs/superpowers/plans/...` Tests / verification scope
**Issue:** The stated compatibility requirement is that default `discover_candidates()` behavior remains unchanged for reports, trends, dashboard, and the existing `candidates` command. The plan adds a direct default-behavior unit test and focused CLI/trends verification, but it does not explicitly cover all broad call sites affected by the signature/path change, especially report/dashboard paths that may indirectly rely on candidate discovery.

**Concrete fix:** Add or explicitly run focused regression coverage for each existing call site:

- `discover_candidates()` direct default behavior
- existing `fashion-radar candidates`
- `build_daily_report()` / report command path that includes candidates
- `build_trend_comparison()` / trends command path
- dashboard/report loading path if it surfaces candidate discovery output

At minimum, update focused verification to include the relevant existing tests, not only `candidates_command` and `trends_command`. Full pytest is good as a release gate, but the plan should include concrete call-site coverage for the promised “unchanged behavior” guarantee.

---

## Minor

### 4. `docs/superpowers/plans/...` Task 3 CLI invalid-format wording
**Issue:** The plan says invalid `--format` is rejected by Typer before query execution, but the proposed Typer option uses a `Literal["table", "json"]` alias with a plain string option. Depending on the project’s Typer version/patterns, this may work, but it is worth confirming against existing output-format command patterns.

**Concrete fix:** During implementation, follow the repository’s existing `ImportedSignalsOutputFormat` / `CANDIDATES_FORMAT_OPTION` pattern exactly and keep the monkeypatch test that proves `query_imported_candidates()` is not called for invalid formats.

---

### 5. `docs/superpowers/plans/...` Release checks
**Issue:** The mirror-safe release checks are mostly concrete and avoid committing mirror URLs, but the plan should explicitly include a final `git status --short` / `git diff -- uv.lock` check after mirror-backed commands and before staging.

**Concrete fix:** Add a release hygiene assertion such as:

```bash
git status --short
git diff -- uv.lock
```

Expected: no `uv.lock` changes from mirror/index commands, and `uv.lock` is not staged.

---

Because there are Important issues, this is **not approved for implementation yet**.

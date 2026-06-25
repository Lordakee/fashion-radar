# Stage 205 Code Review

## Verdict

No Critical findings. No Important findings. The stage is minimal,
contract-safe, and correctly scoped. Implementation matches the plan and the
previous plan-review's minor recommendations were addressed: the partial legacy
test was added, docs mention `growth_ratio` and `first_seen_at`,
`uv lock --check` is in the gate, and the changelog entry is under `### Added`.

## Critical

None.

## Important

None.

## Verification Re-Run

- Focused dashboard and dashboard-docs tests: 47 passed.
- Focused ruff check on changed implementation, test, docs, changelog, plan,
  and plan-review files: clean.
- Focused ruff format check on changed Python files: clean.
- Config-isolated `uv lock --check`: passed.
- `git diff --check`: clean.
- `git diff --exit-code -- uv.lock pyproject.toml`: exit 0.

## Minor

1. `test_latest_candidate_rows_reads_latest_report` uses
   `growth_component: 0.0` in the fixture. Because the legacy default is also
   `0.0`, this value cannot distinguish "field preserved" from "field dropped
   and defaulted". Full-dict equality still catches a missing key, so the test
   is not vacuous, but a non-zero value would also catch a regression that
   re-introduces a default. Optional polish.

2. `first_seen_at` is raw pass-through. The dashboard forwards the ISO 8601
   string straight into `st.dataframe`, which renders it verbatim. The plan
   review explicitly accepted this as future UI polish.

3. The five new keys are inserted between `score` and `current_mentions`, so
   existing dashboard viewers will see new columns appear mid-table rather than
   appended. This is semantically appropriate because transparency components
   belong next to the score, but it is a visible dashboard change.

4. The code-review and release-review prompt files are expected to be paired
   with their review bodies before commit.

## Question-By-Question Assessment

1. Field preservation with correct legacy defaults: yes.
   `latest_candidate_report()` preserves all five fields. Component defaults
   match the report model default of `0.0`; `growth_ratio` and `first_seen_at`
   default to `None` for legacy raw JSON compatibility.

2. Test sufficiency: yes. Three scenarios are covered: full-field preservation
   via dict equality, legacy-missing defaulting, and partial legacy metadata
   where `growth_ratio` and `first_seen_at` survive while components default.
   Existing tests already cover empty candidate lists, missing report
   directories, and malformed JSON.

3. Docs and changelog accuracy: yes. The dashboard docs describe report-backed
   transparency fields and preserve the staleness caveat. The docs and
   changelog do not imply demand proof or platform coverage verification.

4. Leaving representative items, entity evidence, and Streamlit layout changes
   out of this node: correct. Those are different display shapes and broader
   dashboard scope.

5. Out-of-scope behavior changes: none found. The modified file set is limited
   to the dashboard read path, tests, docs, changelog, plan, and review
   artifacts. No source acquisition, connectors, scrapers, scoring, ranking,
   report-generation, schema, dashboard writes, platform coverage verification,
   demand proof, dependency, or compliance-review behavior changes were found.

## Critical

No Critical findings.

## Important

No Important findings.

## Minor

1. **CLI special-character fixture wording could be slightly clearer.**
   The planned test calls `_prepare_imported_signals_cli_fixture(tmp_path / "data ? # & %")`, while the helper currently appends `/data` internally. That still exercises a `--data-dir` path whose full path contains URI-special characters, so it is useful and valid. If the intent is specifically for the final `--data-dir` directory name itself to be `data ? # & %`, the helper should either be adjusted or the test should create the fixture manually. This is optional; the current plan already covers the real URI/path escaping risk.

2. **Read-only write rejection can assert a narrower exception if desired.**
   The planned SQLite test uses `pytest.raises(Exception, match="readonly|read-only|attempt to write")`. That is acceptable for cross-version SQLite/SQLAlchemy message variation, but `sqlalchemy.exc.OperationalError` would be a slightly tighter assertion if stable in this project’s supported environment.

3. **Validation tests should keep checking behavior, not exact Typer phrasing.**
   The plan already says to adjust only assertions if Typer wording differs. That is the right approach. The important invariant is: non-zero exit, option name visible, no traceback, no `query_imported_signals` call, and no data directory creation.

## Review Against Requested Questions

1. **`Matches:` → `Matched rows:`**
   Yes. This is the right minimal production change. It clarifies that the counts are imported item rows with/without stored `item_entities`, not counts of individual entity matches.

2. **Preserving JSON field names**
   Yes. Keeping `matched_count` and `unmatched_count` avoids unnecessary machine-readable contract churn. The existing JSON key stability test is a good guard.

3. **CLI validation tests**
   Yes. Monkeypatching `cli_module.query_imported_signals` to raise, plus asserting the sentinel does not appear and the data directory is not created, is sufficient to prove Typer/CLI validation fails before query/database access for `--lookback-days 0`, `--limit -1`, and `--format xml`.

4. **Special-character `--data-dir` CLI test**
   Yes. It adds useful full-path coverage from CLI option parsing through `default_database_path()` and the imported-signals query path. It does not duplicate the lower-level query test too much because it validates the integration boundary users actually invoke.

5. **Direct read-only SQLite engine test**
   Yes. `tests/test_db.py` is the appropriate location for the lower-level engine behavior: special-character path resolution, read-only opening, and write rejection.

6. **Docs update scope**
   Yes. The plan correctly limits docs updates to user-facing examples, changelog, and Stage 21 artifacts, and explicitly says not to rewrite historical Stage 20 process docs just to change old examples.

7. **Docs wording safety**
   Yes. The design and plan remain bounded to retained local rows, imported local signals, and stored match presence. The boundary scan terms are appropriate. I did not see source-acquisition, platform-coverage, market-wide-ranking, verified-demand, or audit/policy workflow claims outside explicit scope guards/review prompts.

8. **No scope expansion**
   Yes. The plan avoids new dependencies, lockfile changes, migrations, matching/scoring changes, reports, dashboard writes, schedulers, watch folders, collectors, and platform/API integrations.

9. **Verification commands**
   Yes. The focused tests, full pytest run, ruff checks, `git diff --check`, lock/sync/build checks, installed-wheel smoke, hygiene scans, code review prompt, release checks, commit, and push steps are adequate. The plan is slightly more thorough than strictly necessary, but appropriate before release.

10. **Anything missing**
   Nothing blocking. The only optional polish is to make the CLI special-character fixture setup explicit if the reviewer wants the final `--data-dir` basename itself to contain `? # & %`, and to narrow the read-only exception type if stable.

Approved for Stage 21 implementation

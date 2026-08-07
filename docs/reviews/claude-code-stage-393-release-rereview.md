# Stage 393 Follow-up - Final Release Rereview

Scope: frozen snapshot in `/home/ubuntu/fashion-radar`, single worktree on
`main`, HEAD `3464a9b` == `origin/main`. 16 modified tracked files, 11
untracked plan/spec/review artifacts, nothing staged, no deletions, no stash
entries. Read against `AGENTS.md`, `docs/REVIEW_PROTOCOL.md`,
`docs/github-upload-checklist.md`, the strict-ops-check plan and design, the
follow-up plan, and all eight completed Stage 393 records. The prior
`claude-code-stage-393-release-review.md` is superseded because `CHANGELOG.md`
and `tests/test_row_one_docs.py` were modified after it was written, so all
evidence below was regenerated on the current tree. No file was edited,
staged, committed, or pushed during this review.

## Critical

None.

Every hard constraint holds in the live tree:

- **Strict exit is outside the generic handler.** In
  `src/fashion_radar/cli.py`, the strict `raise typer.Exit(1)` sits after the
  output branch and outside the generic `try/except Exception` block. Since
  `typer.Exit` derives from `Exception`, this keeps strict failure from being
  rewritten as `ROW ONE ops check failed:`; the CLI tests assert that string is
  absent from strict output.
- **Output precedes the exit decision, in both modes.** JSON or text is emitted
  before strict health is evaluated, so a failing automation step keeps its
  diagnostic.
- **Byte-identical payloads.** Both paths use the same
  `json.dumps(payload, ensure_ascii=False, indent=2)`; strict JSON tests assert
  that only the exit code differs.
- **One healthy-status source of truth.**
  `ROW_ONE_OPS_CHECK_HEALTHY_STATUS = "site_ready_scheduler_unverified"`
  backs both `_overall_status`'s healthy return and
  `is_row_one_ops_check_strictly_healthy`. The predicate rejects `attention`,
  `unknown`, `degraded`, `""`, `None`, `0`, `{}`, and a missing key.
- **Malformed local health is total and asserted at the top level.**
  `_is_healthy_local_article_status` is the sole raw allowlist entry point,
  both `_overall_status` call sites route through it, and no residual
  `!= "missing"` remains in the health path. The regression feeds `degraded`,
  `""`, `None`, `[]`, and `{}` to each field independently and asserts
  `_overall_status(...) == "attention"` without raising. `_actions` still uses
  `== "missing"`, which is correct and separate.
- **Override is smoke-only.** `--allow-unaccepted-content` appears once in
  `scripts/check_first_run_smoke.py`, on the single `row-one refresh` after the
  deliberate `version: 1\nsources: []\n` fixture, and zero times in
  `src/fashion_radar/scheduling.py`. Generated cron and systemd snippets
  contain neither that flag nor `row-one ops-check --strict`, and both renderer
  tests assert those exclusions directly.
- **No scope creep.** No connectors, scraping, browser automation, platform
  APIs, account/cookie behavior, scheduling policy, source acquisition, demand
  proof, ranking, coverage verification, compliance feature, payload-key
  change, default-exit change, or new dependency was added. `uv.lock` is
  unmodified and free of mirror-bound URLs.

## Important

None.

The two items that superseded the previous release review are resolved:

1. **CHANGELOG matches the plan's prescribed text.** The single `[Unreleased]`
   -> `### Added` Stage 393 item is normalized-identical to Task 3 Step 4,
   covering malformed local article health, strict read-only behavior,
   unchanged default permissive mode and payloads, the smoke-limited one-shot
   override, and unchanged cron/systemd snippets. `- Stage 393` occurs exactly
   once in the whole file.
2. **The changelog test is genuinely helper-scoped.**
   `test_stage_393_changelog_records_bounded_unreleased_added_item` reads
   `_unreleased_changelog` -> `_subsection(..., "Added")` ->
   `_changelog_list_item(added, "- Stage 393")` -> `_normalized`, so it
   inspects only the bounded item. The existing
   `test_changelog_list_item_stops_before_ordinary_next_bullet` is preserved.

Also satisfied: empty-string coverage, the typed helper as the sole health
entry point, and deliberate `ready`/`not_applicable` tightening hold in code.
Documentation assertions remain bounded to the relevant guidance sections;
review-artifact hygiene passes on all eight Stage 393 records with one verdict
each, no tool-status lines, no stubs, no truncation, and no duplicated approval.

## Minor

1. This body must be recorded as
   `docs/reviews/claude-code-stage-393-release-rereview.md`; the superseded
   `claude-code-stage-393-release-review.md` remains in place per protocol.
2. Four tautological assertions in `tests/test_first_run_smoke.py` inspect
   substrings of `refresh_stderr` defined two lines earlier in the fake handler.
   Real coverage comes from the handler raising `SmokeError` when the flag is
   absent, plus source and installed smokes exercising the real warning.
3. `tests/test_row_one_ops_check.py` imports private `_overall_status`, coupling
   the regression to an internal name. This is deliberate per plan.
4. The strict predicate matrix includes `degraded` and `None`, which
   `_overall_status` never emits. This is defensive coverage of a public
   predicate, not a defect.
5. Six reflowed documentation lines exceed 80 characters. This is cosmetic;
   there is no markdownlint configuration, CI markdown lint step, or test that
   asserts document line width.

None of these items blocks release.

## Verification

Fresh evidence on the current frozen snapshot:

| Check | Result |
| --- | --- |
| Full `pytest -q -p no:cacheprovider` | 3303 passed in 77.67s |
| `ruff check .` | All checks passed |
| `ruff format --check .` | 266 files already formatted |
| `UV_NO_CONFIG=1 uv lock --check` | Resolved 85 packages, valid |
| `UV_NO_CONFIG=1 uv sync --locked --dev --check` | Would make no changes |
| `check_release_hygiene.py --repo-root .` | Release hygiene checks passed |
| `git diff --check` | Clean |
| Focused Task 3/docs/helper tests | 10 passed |
| Source first-run smoke | `First-run sample smoke passed.` |
| Generated cron/systemd snippets | Zero forbidden strings; temp removed |
| `uv build` | Exactly 1 wheel and 1 sdist |
| `check_package_archives.py` | `Package archives contain required files.` |
| sdist contents | `CHANGELOG.md` and `docs/scheduling.md` present; review/plan artifacts absent |
| Installed wheel CLI | Help, module help, init, doctor passed |
| Installed help flags | `--strict` present; `--no-strict` absent |
| Installed first-run smoke | `First-run sample smoke passed.` |
| Import origin | Temporary venv, not checkout `src/` |
| Packaged template resource | Passed |
| Dashboard extra | `dashboard.app` and `dashboard.queries` imported |
| Cleanup | Temp root removed; no new repo `build/` or `dist/` artifact |

Candidate allowlist and exclusions:

- The deliberate candidate is exactly 16 modified tracked files plus 11
  untracked Stage 393 plan/spec/review artifacts. Nothing is staged and every
  untracked path matches `stage-393`.
- `configs/scoring.yaml`, `configs/sources.yaml`, `configs/entities.yaml`,
  `data/fashion-radar.sqlite`, `.codegraph` databases/WAL/SHM/log/PID,
  generated reports, `dist/`, `.venv/`, caches, and `__pycache__` files remain
  ignored and excluded. No credentials were found; `.env.example` contains
  placeholders only.
- `.codegraph/.gitignore` and `reports/README.md` are intentional tracked
  documentation files, not runtime artifacts. The pre-existing ignored `dist/`
  inventory was unchanged.
- One worktree and one local branch remain: `HEAD == origin/main == 3464a9b`.
  There are zero stash entries.

Systemd activation and any future scheduled run are outside what these checks
can establish; the documentation states that boundary and the status name
preserves it.

Changed files: the 16 tracked Stage 393 files plus the 11 untracked Stage 393
plan/spec/review artifacts. Unresolved items are Minor 1 through 5 above, none
blocking. Partial writes: none found; no truncated file, empty capture, or
incomplete review output was found.

## Verdict

**Approve for release.** No Critical or Important finding remains and no
release blocker is outstanding. The two changes that superseded the previous
review are correct and verified: the bounded `[Unreleased]`/`Added` item now
matches its prescribed text exactly and appears exactly once, and its test is
scoped through the changelog helpers to that item alone. The strict/permissive
split, exit placement, byte-identical payloads, single healthy-status constant,
malformed-health hardening through one typed helper, smoke-only override,
generated-snippet exclusions, exact candidate allowlist, ignored-artifact and
credential exclusions, main-only worktree/branch parity, and review hygiene
hold under the fresh full-suite, lint, format, lock, sync, hygiene, package,
archive, installed-wheel, resource, and dashboard evidence above.

Nothing was staged, committed, or pushed. Any commit, remote operation, or
tagging remains a separate action requiring explicit authorization; any further
diff to a reviewed file invalidates this snapshot and requires affected
verification plus another rereview.

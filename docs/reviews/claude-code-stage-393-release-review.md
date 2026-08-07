# Stage 393 Follow-up - Final Release Review

Scope: stable integrated snapshot on `main` in `/home/ubuntu/fashion-radar`,
HEAD `3464a9b` (`origin/main`), with 16 modified tracked files and 10
untracked plan/review/spec artifacts. Read against `AGENTS.md`,
`docs/REVIEW_PROTOCOL.md`, `docs/github-upload-checklist.md`, the supplemental
plan, and all seven completed Stage 393 plan/code review records. No files were
edited, staged, committed, or pushed during this review.

## Critical

None.

Every hard constraint holds in the live tree:

- **Strict exit placement is correct.** `typer.Exit(1)` is after the generic
  `try/except Exception` handler in `src/fashion_radar/cli.py`. The strict
  text and JSON tests confirm that the failure diagnostic is printed once and
  that strict failure does not turn into `ROW ONE ops check failed:` output.
- **Byte-identical payloads.** Permissive and strict JSON use the same
  `json.dumps(payload, ensure_ascii=False, indent=2)` output. The tests confirm
  that only the exit code differs.
- **Single healthy-status source of truth.**
  `ROW_ONE_OPS_CHECK_HEALTHY_STATUS = "site_ready_scheduler_unverified"`
  backs both `_overall_status` and the strict predicate. The predicate rejects
  `attention`, `unknown`, `degraded`, empty, null, non-string, and missing
  values.
- **Malformed-health hardening is total and top-level.**
  `_is_healthy_local_article_status` is the sole raw allowlist entry point and
  both local article fields route through it. Regression coverage includes
  `degraded`, empty strings, `None`, lists, and dictionaries and returns
  `attention` without raising.
- **Override is smoke-only.** `--allow-unaccepted-content` occurs in exactly
  one `row-one refresh` invocation in `scripts/check_first_run_smoke.py`, after
  the deliberate `version: 1\nsources: []\n` fixture. It is absent from normal
  scheduling code and generated cron/systemd snippets. The snippets also do
  not contain `row-one ops-check --strict`.
- **No scope creep.** The change adds no connectors, scraping, browser
  automation, platform APIs, scheduling policy, source acquisition, demand
  proof, ranking, coverage verification, compliance feature, payload-key
  change, default-exit change, or dependency.

## Important

None.

- The prior plan conditions for empty-string regression coverage and a typed
  helper as the sole health entry point are satisfied in the integrated code.
- The allowlist tightening from `!= "missing"` to
  `{ready, not_applicable}` is behavior-preserving for current producers,
  which emit those values and `missing`, and is documented as deliberate.
- Review-record hygiene passes: all seven `opencode-stage-393-*.md` records
  have complete bodies and one verdict, with no tool-status lines, stubs, or
  duplicated approvals. No `claude-code-stage-393-*` record existed before
  this capture; the earlier Claude timeout is disclosed honestly and the
  protocol fallback records are not treated as Claude approval.

## Minor

1. The CHANGELOG wording differs from the follow-up plan's literal prescribed
   text. The current bounded item is accurate and its helper-scoped test is
   honest, but the plan text emphasizes malformed local health, the smoke-only
   override, and unchanged cron/systemd snippets. This is non-blocking wording
   drift, but it should be deliberately accepted or aligned before commit.
2. `tests/test_row_one_ops_check.py` imports private `_overall_status` directly.
   This is focused regression coverage but couples the test to an internal name.
3. The strict predicate matrix includes unreachable `degraded` and `None`
   statuses. This is defensible defensive coverage, not a defect.
4. Some smoke success-path assertions over-specify reason substrings from the
   fake handler. Source and installed smokes still verify the real warning
   prefix end to end.

## Verification

Fresh coordinator-run results on the reviewed snapshot:

| Check | Result |
| --- | --- |
| Full `pytest` suite | 3303 passed in 85.62s |
| `ruff check .` | All checks passed |
| `ruff format --check .` | 266 files already formatted |
| `UV_NO_CONFIG=1 uv lock --check` | Resolved 85 packages, valid |
| `UV_NO_CONFIG=1 uv sync --locked --dev --check` | Would make no changes |
| Release hygiene | Passed |
| `git diff --check` | Clean |
| Source first-run smoke | `First-run sample smoke passed.` |
| `uv build` | One wheel and one sdist |
| Package archive check | `Package archives contain required files.` |
| Installed-wheel CLI/help/init/doctor | Passed; `--strict` exposed |
| Installed-wheel first-run smoke | `First-run sample smoke passed.` |
| Import-origin check | Temporary venv, not checkout `src/` |
| Packaged template resource | Passed |
| Dashboard extra imports | `dashboard.app` and `dashboard.queries` passed |

Additional release evidence:

- `uv.lock` has no mirror-bound URLs and was not modified.
- Ignored `configs/*.yaml`, `.codegraph` database/WAL/SHM files, SQLite data,
  generated reports, caches, `.venv`, and `dist` artifacts are excluded. No
  credential files were found; `.env.example` contains placeholders only.
- Nothing was staged. The deliberate candidate is the 16 modified tracked
  paths plus 10 untracked plan/review/spec paths, all accounted for by the
  Stage 393 plans; no unrelated path is included.
- The sdist includes `CHANGELOG.md` and `docs/scheduling.md` and excludes
  review/plan artifacts.
- Temporary package roots and build artifacts were removed.
- The repository has one worktree, `/home/ubuntu/fashion-radar`, on `main`;
  `HEAD == origin/main == 3464a9b`, with no extra branches or worktrees.
- Systemd activation and a future scheduled refresh are outside what a
  filename-only diagnostic can prove, and the documentation states that
  boundary.

## Verdict

**Approve for release.** No Critical or Important finding remains and no
release blocker is outstanding. The strict/permissive split, malformed-health
hardening, typed helper, smoke-only override placement, generated-snippet
exclusions, bounded CHANGELOG scope, main-only worktree/branch, ignored-file
exclusions, and review hygiene hold under the fresh release checks above.

The four Minor items are non-blocking and do not require a rereview. Item 1,
the CHANGELOG wording difference, should receive a deliberate accept-or-align
decision before commit; aligning it changes `CHANGELOG.md` and
`tests/test_row_one_docs.py` and requires rerunning the affected verification
and a release rereview.

Nothing was staged, committed, or pushed. Remote operations and tagging remain
separate actions after the release gate.

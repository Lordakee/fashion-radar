# Stage 393 Follow-up — Final Release Rereview

Scope: frozen snapshot in `/home/ubuntu/fashion-radar`, single worktree on `main`, HEAD `3464a9b` == `origin/main`. 16 modified tracked files, 11 untracked plan/spec/review artifacts, nothing staged, no deletions, no stash entries. Read against `AGENTS.md`, `docs/REVIEW_PROTOCOL.md`, `docs/github-upload-checklist.md`, the strict-ops-check plan and design, the follow-up plan, and all eight completed Stage 393 records. The prior `claude-code-stage-393-release-review.md` is treated as superseded: `CHANGELOG.md` (06:51) and `tests/test_row_one_docs.py` (06:52) were both modified after that record was written (06:48), so all evidence below was regenerated on the current tree. No file was edited, staged, committed, or pushed.

## Critical

None.

Every hard constraint holds in the live tree:

- **Strict exit is outside the generic handler.** In `src/fashion_radar/cli.py`, the `try/except Exception` around `build_row_one_ops_check_payload` closes with its own `typer.Exit(1)`; the strict `raise typer.Exit(1)` sits after the output branch, outside that block. Since `typer.Exit` derives from `Exception`, this placement is what keeps strict failure from being rewritten as `ROW ONE ops check failed:`, and the CLI tests assert that string is absent from strict output.
- **Output precedes the exit decision, in both modes.** The refactor emits JSON or text via `if/else` and only then evaluates strict health, so a failing automation step keeps its diagnostic.
- **Byte-identical payloads.** Both paths use the same `json.dumps(payload, ensure_ascii=False, indent=2)`; the strict JSON tests assert `strict.output == permissive.output` with only the exit code differing.
- **One healthy-status source of truth.** `ROW_ONE_OPS_CHECK_HEALTHY_STATUS = "site_ready_scheduler_unverified"` backs both `_overall_status`'s healthy return and `is_row_one_ops_check_strictly_healthy`. The predicate rejects `attention`, `unknown`, `degraded`, `""`, `None`, `0`, `{}`, and a missing key.
- **Malformed local health is total and asserted at the top level.** `_is_healthy_local_article_status` is the sole raw allowlist entry point (`rg` reports exactly one `in ROW_ONE_LOCAL_ARTICLE_HEALTHY_STATUSES` occurrence), both `_overall_status` call sites route through it, and no residual `!= "missing"` remains in the health path. The parametrized regression feeds `degraded`, `""`, `None`, `[]`, `{}` to each field independently and asserts `_overall_status(...) == "attention"` without raising. `_actions` still uses `== "missing"`, which is correct and separate.
- **Override is smoke-only.** `--allow-unaccepted-content` appears once in `scripts/check_first_run_smoke.py`, on the single `row-one refresh` after the deliberate `version: 1\nsources: []\n` fixture, and zero times in `src/fashion_radar/scheduling.py`. Freshly generated cron and systemd snippets contain neither `--allow-unaccepted-content` nor `row-one ops-check --strict`, and both renderer tests now assert those exclusions directly.
- **No scope creep.** No connectors, scraping, browser automation, platform APIs, account/cookie behavior, scheduling policy, source acquisition, demand proof, ranking, coverage verification, compliance feature, payload-key change, default-exit change, or new dependency. `uv.lock` is unmodified and free of mirror-bound URLs.

## Important

None.

The two items that made the previous release review superseded are both resolved:

1. **CHANGELOG matches the plan's prescribed text.** The single `[Unreleased]` → `### Added` Stage 393 item is now normalized-identical to the Task 3 Step 4 prescription, covering malformed local article health, strict read-only behavior, unchanged default permissive mode and payloads, the smoke-limited one-shot override, and unchanged cron/systemd snippets. `- Stage 393` occurs exactly once in the whole file. The prior review's Minor 1 wording drift is closed by alignment rather than by acceptance.
2. **The changelog test is genuinely helper-scoped.** `test_stage_393_changelog_records_bounded_unreleased_added_item` reads `_unreleased_changelog` → `_subsection(..., "Added")` → `_changelog_list_item(added, "- Stage 393")` → `_normalized`, so it inspects only the bounded item, never the whole file. I confirmed independently that the item is inside `[Unreleased]`/`Added` and appears nowhere else. `test_changelog_list_item_stops_before_ordinary_next_bullet` is preserved.

Also satisfied: the earlier plan-gate conditions (empty-string coverage, typed helper as sole entry point, deliberate `ready`/`not_applicable` tightening) hold in code, not just in the plan. Documentation assertions stay bounded to `_ops_check_guidance(path)` for `README.md`, `docs/row-one.md`, and `docs/cli-reference.md`; the Stage 393 prose is an indented continuation of the `row-one ops-check` item with no new top-level `- Stage 393` bullet; the scheduling assertion stays bounded to the `ROW ONE Daily Site` section and requires all three negative boundaries. Documentation tests remain pure content checks and never invoke the CLI. Review-artifact hygiene passes on all eight Stage 393 records: one H1 and exactly one verdict each, no `Wrote`/tool-status lines, no stubs, no truncation, no duplicated approval. The recorded Claude timeout is disclosed honestly and never presented as approval.

## Minor

1. No release rereview record exists yet. This body should be recorded as `docs/reviews/claude-code-stage-393-release-rereview.md`; the superseded `claude-code-stage-393-release-review.md` should stay in place per the protocol's keep-existing-records rule rather than being edited, even though its Minor 1 no longer describes the tree.
2. Four tautological assertions in `tests/test_first_run_smoke.py` check substrings of `refresh_stderr`, a literal defined two lines earlier in the same fake handler, so they cannot fail. Real coverage comes from the handler raising `SmokeError` when the flag is absent, plus the source and installed smokes exercising the genuine warning prefix.
3. `tests/test_row_one_ops_check.py` imports the private `_overall_status`, coupling the regression to an internal name. Deliberate per plan.
4. The strict predicate matrix includes `degraded` and `None`, which `_overall_status` never emits. Defensive coverage of a public predicate, not a defect.
5. Six reflowed documentation lines exceed 80 characters. Cosmetic only: there is no markdownlint config, no CI markdown lint step, and no test asserting doc line width.

None of these blocks release.

## Verification

Fresh evidence, all run by me on the current frozen snapshot:

| Check | Result |
| --- | --- |
| Full `pytest -q -p no:cacheprovider` | 3303 passed in 77.67s |
| `ruff check .` | All checks passed |
| `ruff format --check .` | 266 files already formatted |
| `UV_NO_CONFIG=1 uv lock --check` | Resolved 85 packages, valid |
| `UV_NO_CONFIG=1 uv sync --locked --dev --check` | Would make no changes |
| `check_release_hygiene.py --repo-root .` | Release hygiene checks passed |
| `git diff --check` | Clean |
| Focused Task 3 Step 4 + docs/helper tests | 10 passed |
| Source first-run smoke | `First-run sample smoke passed.` |
| Generated cron + systemd snippets | Zero forbidden strings; temp dir removed |
| `uv build` | Exactly 1 wheel, 1 sdist |
| `check_package_archives.py` | `Package archives contain required files.` |
| sdist contents | `CHANGELOG.md` 1, `docs/scheduling.md` 1, review/plan artifacts 0 |
| Installed wheel CLI | `--help`, `python -m fashion_radar --help`, `init`, `doctor` all passed |
| Installed help flags | `--strict` present, `--no-strict` absent |
| Installed first-run smoke | `First-run sample smoke passed.` |
| Import origin | Resolves into the temporary venv, not checkout `src/` |
| Packaged template resource | Passed |
| Dashboard extra | `dashboard.app` and `dashboard.queries` imported |
| Cleanup | Temp root removed, no repo `build/`, no new `dist/` artifact |

Candidate allowlist and exclusions:

- Deliberate candidate is exactly 16 modified tracked files plus 11 untracked Stage 393 plan/spec/review artifacts. Nothing staged. Every untracked path matches `stage-393`; no unrelated path is present.
- Against the follow-up plan's recorded dirty-tree baseline, the only additions are `CHANGELOG.md` and `tests/test_scheduling.py` — precisely two of Worker D's three-file coupled write set, which was dormant when that baseline was captured. `tests/test_row_one_docs.py` was already in the baseline. Nothing was dropped, so no unrelated user change was reverted.
- `configs/scoring.yaml` is untracked and ignored via `.gitignore:41`; `configs/sources.yaml` and `configs/entities.yaml` likewise. Also excluded: `data/fashion-radar.sqlite`, `.codegraph/codegraph.db` with its `-wal`/`-shm`, `.codegraph/daemon.log`, `.codegraph/daemon.pid`, generated `reports/` files, `reports/row-one/`, `dist/`, `.venv/`, `.pytest_cache/`, `.ruff_cache/`, and all `__pycache__/`.
- Two tracked files match artifact-ish patterns and are both intentionally publishable: `.codegraph/.gitignore` (explicitly listed under the checklist's Tooling Files, and it ignores all CodeGraph runtime files) and `reports/README.md` (directory documentation). The pre-existing `dist/` directory holds only ignored July artifacts, zero tracked.
- No credentials found. The two files whose names match a secret pattern are the Stage 132 hygiene plan and design docs, both already in HEAD. `.env.example` contains three empty path placeholders and no values.
- One worktree, one local branch, `HEAD == origin/main == 3464a9b`, zero stash entries.

Not verified, and outside what these checks can establish: systemd activation and any future scheduled run. The documentation states that boundary, and `scheduler_unverified` preserves it in the status name itself.

Changed files: `AGENTS.md`, `CHANGELOG.md`, `README.md`, `docs/cli-reference.md`, `docs/row-one.md`, `docs/scheduling.md`, `scripts/check_first_run_smoke.py`, `src/fashion_radar/cli.py`, `src/fashion_radar/row_one/ops_check.py`, `tests/test_agents_scope_docs.py`, `tests/test_first_run_smoke.py`, `tests/test_row_one_cli.py`, `tests/test_row_one_docs.py`, `tests/test_row_one_ops_check.py`, `tests/test_scheduling.py`, `tests/test_scheduling_docs.py`, plus the 11 untracked Stage 393 artifacts.

Unresolved items: Minor 1 through 5 above, none blocking. Partial writes: none found — no truncated file, no empty capture, and no output file that could be mistaken for an incomplete review record.

## Verdict

**Approve for release.** No Critical or Important finding remains and no release blocker is outstanding. The two changes that superseded the previous release review are correct and verified: the bounded `[Unreleased]`/`Added` item now matches its prescribed text exactly and appears exactly once, and its test is scoped through the changelog helpers to that item alone. The strict/permissive split, exit placement outside the generic handler, byte-identical payloads, single healthy-status constant, total malformed-health hardening through one typed helper, smoke-only override, generated-snippet exclusions, exact candidate allowlist, ignored-artifact and credential exclusions, main-only worktree and branch parity, and review-artifact hygiene all hold under the fresh full-suite, lint, format, lock, sync, hygiene, package, archive, installed-wheel, resource, and dashboard evidence above.

Remaining action before upload: record this body as `docs/reviews/claude-code-stage-393-release-rereview.md`. Nothing was staged, committed, or pushed; any commit, remote operation, or tagging remains a separate action requiring explicit authorization, and any further diff to a reviewed file would invalidate this snapshot and require the affected verification plus another rereview.

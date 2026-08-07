# Stage 393 Follow-up Diff — Code Review (OpenCode fallback after Claude timeout)

Scope: stable integrated dirty tree on `main` in `/home/ubuntu/fashion-radar`, read against `AGENTS.md`, `docs/REVIEW_PROTOCOL.md`, the supplemental plan (`docs/superpowers/plans/2026-08-07-stage-393-review-followups-plan.md`), the strict-ops-check plan/design specs, and all six completed Stage 393 plan/rereview records. No files were edited; no commit/push attempted; Claude's timeout is not treated as approval.

## Critical

None.

Hard constraints verified against the live tree:

- **Strict/permissive split is correct.** The deliberate `typer.Exit(1)` sits at `src/fashion_radar/cli.py:2500`, *after* the `try/except Exception` block that ends at `:2494`. Because `typer.Exit` resolves to a `RuntimeError` subclass (an `Exception`), placing it inside the handler would have printed `ROW ONE ops check failed:` and corrupted the strict contract; the placement and the test asserting `ROW ONE ops check failed:` is absent from strict output both hold.
- **Byte-identical JSON.** Both branches emit `json.dumps(payload, ensure_ascii=False, indent=2)`; `--strict --json` and plain `--json` differ only by exit code (`test_row_one_ops_check_strict_json_preserves_payload_and_fails_unhealthy_status` asserts `strict.output == permissive.output`).
- **Single healthy-status source of truth.** `ROW_ONE_OPS_CHECK_HEALTHY_STATUS` is the constant used by both `_overall_status`'s return and the CLI predicate; the predicate test matrix accepts only that exact string and rejects `"attention"`, `"unknown"`, `"degraded"`, `""`, `None`, `0`, `{}`.
- **Smoke-only override.** `--allow-unaccepted-content` appears in exactly one `row-one refresh` invocation (`scripts/check_first_run_smoke.py`, after the deliberate `version: 1\nsources: []\n` fixture) and nowhere in `src/fashion_radar/scheduling.py` or generated snippets.
- **No scope creep.** No connectors, scraping, platform APIs, scheduling policy, source acquisition, demand proof, ranking, coverage verification, compliance review, daemon, or new dependency.

## Important

None.

The two prior Important conditions from the plan rereviews are satisfied in the integrated code, not just the plan:

1. **Malformed-health regression is real and top-level.** `_overall_status` is fed `degraded`/`None`/`""`/`[]`/`{}` on each local-article field independently and returns exactly `"attention"` without raising (`test_ops_check_overall_status_rejects_unhealthy_local_article_health`). The positive path still returns `ROW_ONE_OPS_CHECK_HEALTHY_STATUS` for both `ready` and `not_applicable`.
2. **Typed helper is the sole entry point.** `rg` confirms `in ROW_ONE_LOCAL_ARTICLE_HEALTHY_STATUSES` occurs only inside `_is_healthy_local_article_status` (`ops_check.py:49`); both `_overall_status` call sites (`:305`, `:306`) route through it. No residual `!= "missing"` membership remains in the health path. (`_actions` still uses `== "missing"` for action suggestions, which is correct and separate.)

The allowlist tightening is behavior-preserving for current producers (which emit only `ready`/`not_applicable`/`missing`) and correctly documented as a deliberate tightening rather than a bare `TypeError` swallow.

## Minor

1. **CHANGELOG wording diverges from the plan's prescribed text.** Task 3 Step 4 prescribed an item emphasizing "malformed local article health values yield `attention`," the smoke-only override, and "normal cron/systemd snippets remain unchanged." The implemented item instead leads with the `--strict` gate contract. The helper-scoped test was updated in lockstep to validate the *actual* wording, the item is accurate and bounded to one `[Unreleased]`/`### Added` entry, and the user-facing framing is arguably cleaner. Flagging only for transparency against the plan's literal text.
2. **Private-symbol test coupling.** `tests/test_row_one_ops_check.py` imports the private `_overall_status` directly. This is a focused regression surface and the plan chose it deliberately, but it does couple the test to an internal function name.
3. **Predicate test includes unreachable statuses.** The strict predicate is parametrized with `"degraded"` and `None`, which `_overall_status` never produces (it only returns `unknown`/`site_ready_scheduler_unverified`/`attention`). This is defensible defensive coverage of the public predicate, not a defect.
4. **Smoke success-path assertions over-specify reasons substrings** (`insufficient successful collectors: found 0, minimum 1`, etc.). These assert against the fake handler's own stderr, not the real CLI, so the real run is unaffected; the source smoke confirms the real warning prefix is emitted end-to-end.

## Verification

Fresh coordinator run on the reconciled integrated tree (not worker-reported):

- `pytest tests/test_row_one_ops_check.py tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_scheduling.py tests/test_scheduling_docs.py tests/test_agents_scope_docs.py` → 318 passed.
- `pytest tests/test_first_run_smoke.py` → 184 passed.
- Full suite `pytest` → 3303 passed in 76.42s.
- `ruff check .` → All checks passed. `ruff format --check .` → 266 files already formatted.
- `uv lock --check` → resolved, valid. `check_release_hygiene.py` → Release hygiene checks passed (no secrets/cookies/tokens/SQLite/build artifacts).
- `scripts/check_first_run_smoke.py --repo-root .` → First-run sample smoke passed. (Confirms the real `row-one refresh --allow-unaccepted-content` on empty sources emits the bypass warning and exits 0.)
- Generated `cron`/`systemd` snippets written to a temp dir: `rg -- '--allow-unaccepted-content|row-one ops-check --strict'` → no matches (RC=1). `git diff --check` → clean.
- Review-capture hygiene: all six `docs/reviews/opencode-stage-393-*.md` records contain complete bodies, exactly one verdict each, no `Wrote`/tool-status lines, no stubs or duplicated verdicts. No `claude-code-stage-393-*` record exists; the timeout is recorded honestly and the fallback route is used per protocol.

## Verdict

**Approve.** The integrated Stage 393 follow-up diff is sound and release-ready at the code level. The strict/permissive split, malformed-health hardening, smoke-only override placement, generated-snippet exclusions, bounded changelog scope, main-worktree ownership rule, and review hygiene all hold under fresh verification. No Critical or Important finding remains. The Minor items (notably the CHANGELOG wording divergence from the plan's literal text) are non-blocking and do not require a rereview; they may be resolved during implementation cleanup or noted for the record. A subsequent diff to any reviewed file would require the affected verification and a rereview to be rerun.

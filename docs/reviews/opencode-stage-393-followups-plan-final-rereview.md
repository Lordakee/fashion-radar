# Stage 393 Review Follow-ups — Revised Plan Review

Scope: revised plan at `docs/superpowers/plans/2026-08-07-stage-393-review-followups-plan.md`, read against `AGENTS.md`, `docs/REVIEW_PROTOCOL.md`, the four completed Stage 393 review records, the live dirty tree, and the referenced source/test/doc files. No files were edited.

## Critical

None.

Hard constraints hold:
- The strict `typer.Exit(1)` is raised *after* the generic `try/except Exception` block (`src/fashion_radar/cli.py:2500`), satisfying the prior Stage 393 plan-rereview Important finding, so strict failure cannot be corrupted by the `ROW ONE ops check failed:` handler.
- Top-level status string is unchanged (`site_ready_scheduler_unverified`, now a constant), so strict and non-strict `--json` stdout remain byte-identical for the same payload.
- `--allow-unaccepted-content` is added to exactly one `row-one refresh` invocation, only after the deliberate `version: 1\nsources: []\n` fixture is written (`scripts/check_first_run_smoke.py`), and is absent from `src/fashion_radar/scheduling.py` and the documented snippets.
- No new connectors, scraping, platform APIs, scheduling, source acquisition, demand proof, ranking, coverage verification, or compliance behavior is introduced.
- No Git metadata, commit, push, branch, or extra worktree is touched; the plan-only worker's sole write claim is the plan file itself.

## Important

1. **Empty-string coverage is mandated by the plan but missing from the baseline candidate `_overall_status` regression test.** Task 1 Step 1 explicitly requires each of `"degraded"`, `None`, `""`, `[]`, `{}` to be fed to both `local_article_routes` and `local_article_content`. The live dirty-tree test `test_ops_check_overall_status_rejects_unhealthy_local_article_health` parametrizes only `"degraded"`, `None`, `[]`, `{}` — the `""` case is absent on both sides. The strict top-level predicate test *does* include `("", False)`, but that does not exercise the local-article path. Because the follow-up rereview made the helper contract explicit ("safely rejects null, empty, and unhashable values"), the implementer must add `pytest.param("", "ready", id="routes-empty")` and `pytest.param("ready", "", id="content-empty")` rather than treat the green candidate as already-satisfying. Add an explicit checklist note so the gap is not shipped silently.

2. **Task 1 is a deliberate allowlist tightening, not only a TypeError guard — say so.** The HEAD baseline was `status != "missing"` (permissive: `""`, `None`, `[]`, `{}`, `"degraded"` were all treated as healthy and did not raise). The revised code requires `status in {"ready", "not_applicable"}` via `_is_healthy_local_article_status`. That is behavior-preserving for current producers (which emit only `ready`/`not_applicable`/`missing`, per the Stage 393 plan-rereview), but it flips any future `degraded`/`unknown`/malformed producer from healthy to `attention` at the top level. The plan's framing ("malformed values yield `attention` instead of an exception") describes the intermediate raw-frozenset state, not HEAD. Add one sentence so implementers and code reviewers understand this is a stricter membership predicate and not merely an exception swallow.

## Minor

- **Worker D file-portion claim wording.** The ownership table lists Worker D's claim as "the Stage 393 changelog contract portion of `tests/test_row_one_docs.py`" under the "Exact writable globs" column. A file portion is not a glob; AGENTS.md defines exclusivity at the glob/file level. In practice there is no conflict because the coordinator performs only read-only verification on the strict-ops-check tests in that file and Worker D is the sole writer of the changelog test, but consider stating the claim as "`tests/test_row_one_docs.py` (changelog-helper additions only)" to match the exclusivity model.
- **Already-complete Worker B claim.** Both Worker B files are already fully modified on the dirty baseline (flag, warning prefix, `SmokeError` gate, empty-source config pin). The handoff should be a quick reconcile + fresh run, not fresh implementation. The plan handles this via its "already-dirty baseline" note, but a one-line "Worker B work appears pre-applied; reconcile only" would avoid confusion.
- **Smoke `--help` disambiguation.** The candidate refresh branch guard is `args[:2] == ("row-one", "refresh") and "--help" not in args`. This is a correct robustness addition (an earlier `row-one refresh --help` smoke call would otherwise enter the branch) but is not mentioned in Task 2 Step 1; note it so a reviewer does not flag it as drift.
- **Smoke success-path assertions slightly over-specify the reasons text** (`insufficient successful collectors: found 0, minimum 1` and `insufficient fresh items: found 0, minimum 1`). These are asserted against the fake handler's own stderr, not the real CLI, so the real run is unaffected; still, it is marginally more brittle than the plan's "stable substring" intent. Acceptable as-is.

## Verification

- **Dirty-tree baseline:** exact match. 14 modified + 7 untracked, identical set and spelling to the plan's "Current Dirty-Tree And Write-Claim Baseline" block.
- **Worker B / Feynman write claim:** `scripts/check_first_run_smoke.py` + `tests/test_first_run_smoke.py`, both modified; the flag is added only to the single empty-source refresh, the empty-source config is pinned, the bypass-warning prefix is asserted, and the fake raises `SmokeError` when the flag is absent. Matches Task 2.
- **Worker D / Halley write claim:** dormant, as stated. `tests/test_scheduling.py` and `CHANGELOG.md` are unmodified; `tests/test_row_one_docs.py` is modified only with the strict-ops-check contract tests (Task 3 Step 1 verification material), not the changelog helper test.
- **Three-file scheduling/changelog coupled write set:** correctly described as one unit; Worker D is barred from editing `src/fashion_radar/scheduling.py` (confirmed no leaks of `--allow-unaccepted-content` or `ops-check --strict`).
- **Direct cron/systemd negative assertions (Task 3 Step 3):** accurate. The cron test variable is `text` (`tests/test_scheduling.py:117`) and the systemd variable is `service` (`:415`), matching the plan's "`service` instead of `text`" guidance.
- **Stage 393 Unreleased Added item + helper-scoped test:** feasible. `## [Unreleased]` contains an existing `### Added` section (line 63), so the "existing `### Added`" precondition is true. Required helpers (`_unreleased_changelog`, `_subsection`, `_normalized`, `_changelog_list_item`) and the `CHANGELOG` path constant exist in `tests/test_row_one_docs.py`; `test_changelog_list_item_stops_before_ordinary_next_bullet` exists and is preserved.
- **Executable package commands (Task 5 Step 5):** valid. `fashion-radar = "fashion_radar.cli:app"` is declared; `dashboard` extra exists; `scripts/check_first_run_smoke.py` supports `--repo-root`, `--python`, and `--installed`; `check_release_hygiene.py` and `check_package_archives.py` exist.
- **Finding-fix -> fresh-verification -> rereview loop (Task 5 Step 3):** coherent and consistent with AGENTS.md ("a subsequent diff change requires the affected verification and review to be rerun"), including honest timeout handling and the rule that a rereview record, not a second verdict, is used when a fix touches a review record.
- **Plan gate honesty:** the revised plan correctly requires a completed primary Claude plan review before Worker D starts, treats a `124` timeout / nonzero exit / empty or tool-status capture as non-approval, and prescribes the independent OpenCode fallback only after an honest Claude failure. The prior Claude timeout is not treated as approval anywhere in the plan or the rereview record.

## Verdict

**Approve with conditions.** No Critical issue and no blocking scope/sequencing defect. The plan preserves ROW ONE daily content acceptance, keeps the override smoke-only, leaves scheduling snippets and payloads untouched, holds the main-only worktree line, and routes every finding through a fresh-verification rereview loop. Before implementation closes, satisfy the two Important items: (1) explicitly add the missing `""` cases to the `_overall_status` regression test rather than relying on the green candidate, and (2) state that Task 1 is a deliberate `ready`/`not_applicable` allowlist tightening, not merely a TypeError swallow. The Minor items are addressable during implementation without re-review.

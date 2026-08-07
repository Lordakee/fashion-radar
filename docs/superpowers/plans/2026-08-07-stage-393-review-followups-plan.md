# Stage 393 Review Follow-ups Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or `superpowers:executing-plans`
> task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the Stage 393 review findings without weakening ROW ONE daily
content acceptance, changing the default ops-check behavior, or adding runtime
side effects.

**Architecture:** Harden the existing local-article health allowlist so malformed
values are diagnostic `attention` rather than exceptions. At the aggregation
boundary this deliberately tightens the healthy allowlist to `ready` and
`not_applicable`, rather than merely swallowing a TypeError; current producers
already use those canonical healthy values. Keep the offline
first-run fixture deterministic and opt it into the existing one-shot content
acceptance override only for its deliberate empty-source refresh. Tighten strict
documentation tests to their own guidance boundary, verify generated scheduling
snippets remain free of the one-shot override, and record the required
parallel-agent policy as a tested repository instruction.

**Tech Stack:** Python 3.11+, Typer, pytest, Ruff, uv, existing ROW ONE CLI and
first-run smoke helpers.

**Implementation Method:** Preserve the existing main-worktree ownership
claims, complete disjoint work in parallel after the plan gate, reconcile every
handoff in the coordinator, run fresh verification on the integrated snapshot,
and repeat review after every finding fix or subsequent diff.

---

## Scope And Non-Goals

- Do not change `row-one refresh` acceptance defaults, thresholds, or its
  current-run-only definition of collector evidence.
- Do not put `--allow-unaccepted-content` in normal cron/systemd documentation
  or generated scheduling snippets. The flag remains limited to the single
  deterministic smoke refresh whose fixture deliberately contains
  `version: 1\nsources: []\n`.
- Do not change ops-check payload keys, payload field order, its default
  permissive exit behavior, the meaning of `ok`, systemd probing, server
  lifecycle, generated-site contracts, or dependencies.
- Keep strict ops-check read-only and diagnostic-only. It must not start a
  server, refresh the site, install systemd units, invoke `systemctl` or
  `loginctl`, or add runtime side effects.
- Do not add source acquisition, connectors, scraping, browser automation,
  account/session/cookie behavior, demand proof, ranking, coverage verification,
  deployment automation, or compliance-review behavior.
- Update only the bounded Stage 393 item under `[Unreleased]` -> `### Added`
  described in Task 3. Do not add unrelated release notes or claims about new
  collection, scheduling, demand proof, platform coverage, or deployment.
- Do not create another Git worktree or use another branch. All work remains in
  the existing `main` worktree on `main`.
- This plan revision does not stage, commit, push, reset, clean, or otherwise
  change Git metadata or remote state.

## Current Dirty-Tree And Write-Claim Baseline

Before this plan-only revision, the coordinator captured:

```text
git status --short --branch
## main...origin/main
 M AGENTS.md
 M README.md
 M docs/cli-reference.md
 M docs/row-one.md
 M docs/scheduling.md
 M scripts/check_first_run_smoke.py
 M src/fashion_radar/cli.py
 M src/fashion_radar/row_one/ops_check.py
 M tests/test_agents_scope_docs.py
 M tests/test_first_run_smoke.py
 M tests/test_row_one_cli.py
 M tests/test_row_one_docs.py
 M tests/test_row_one_ops_check.py
 M tests/test_scheduling_docs.py
?? docs/reviews/opencode-stage-393-followups-plan-rereview.md
?? docs/reviews/opencode-stage-393-followups-plan-review.md
?? docs/reviews/opencode-stage-393-plan-rereview.md
?? docs/reviews/opencode-stage-393-plan-review.md
?? docs/superpowers/plans/2026-08-07-stage-393-review-followups-plan.md
?? docs/superpowers/plans/2026-08-07-stage-393-row-one-strict-ops-check-plan.md
?? docs/superpowers/specs/2026-08-07-stage-393-row-one-strict-ops-check-design.md
```

This is an ownership baseline, not a claim that the planning worker created any
of those changes. Workers must not reset, checkout, clean, or overwrite a path
from that snapshot merely to obtain a clean tree. The planning worker's only
write claim for this task is the supplemental plan file itself:
`docs/superpowers/plans/2026-08-07-stage-393-review-followups-plan.md`.

## Parallel Assignment Table

The following table records the real current claims before any further
delegation. An exact writable glob is an exclusive claim. A coupled write set
must be treated as one ownership unit even when the files are disjoint. A
read-only worker has no write claim and may run concurrently with all rows.

| Owner | Exact writable globs | Coupled write set | Read-only prerequisites and dependencies | Expected completion state |
| --- | --- | --- | --- | --- |
| Worker B / Feynman | **ONLY** `scripts/check_first_run_smoke.py`, `tests/test_first_run_smoke.py` | `scripts/check_first_run_smoke.py` + `tests/test_first_run_smoke.py` | Read the current smoke harness, the exact `version: 1\nsources: []\n` fixture, current `src/fashion_radar/cli.py`, and scheduling documentation. Do not claim CLI, scheduling, or other test files. | Full passing focused smoke handoff, then reclaim. Handoff must include the changed-file list, focused test and source-smoke results, unresolved work, and partial writes. |
| Worker C / Dewey | **ONLY** `docs/superpowers/plans/2026-08-07-stage-393-review-followups-plan.md` | Exactly `docs/superpowers/plans/2026-08-07-stage-393-review-followups-plan.md` | Read `AGENTS.md`, `docs/REVIEW_PROTOCOL.md`, the completed Stage 393 plan review/rereview records, current tests, scheduling/release documentation, and package scripts. Do not write production code, tests, CHANGELOG, review records, Git metadata, branches, or worktrees. | Revised plan with review findings addressed, then handoff/reclaim. The handoff must report this changed path, plan checks, unresolved issues, and partial writes. |
| Worker D / Halley (successor implementation worker; audit complete) | **ONLY** `tests/test_scheduling.py`, `CHANGELOG.md`, and `tests/test_row_one_docs.py` (changelog-helper additions only) | Exactly `tests/test_scheduling.py` + `CHANGELOG.md` + `tests/test_row_one_docs.py` | Halley's read-only scheduling/changelog audit completed with no writes. The write claim is dormant until the revised plan gate and required plan review complete. Read `src/fashion_radar/scheduling.py`, the existing cron/systemd renderer tests, the `[Unreleased]` changelog structure, and the existing `_unreleased_changelog`, `_subsection`, `_normalized`, and `_changelog_list_item` helpers. Do not modify `src/fashion_radar/scheduling.py` or any other production scheduling file. | After the plan gate, add the direct renderer negative assertions, the Stage 393 `Unreleased` `Added` item, and the helper-scoped changelog test; run the focused checks, hand off the three-file result, then reclaim. |
| Coordinator | `src/fashion_radar/row_one/ops_check.py`; `tests/test_row_one_ops_check.py`; `docs/cli-reference.md`; `docs/row-one.md`; `docs/scheduling.md`; `tests/test_scheduling_docs.py`; `tests/test_agents_scope_docs.py`; `docs/reviews/claude-code-stage-393-*.md`; `docs/reviews/opencode-stage-393-*.md` | The coordinator-owned implementation/documentation paths are one integration set. Worker D's three files are excluded from this claim and remain one coupled successor write set. Review records are coupled to the exact stable integrated snapshot and must be regenerated after any diff change. | Consume Worker B's smoke handoff, Worker C's plan handoff, Worker D's three-file handoff, and the completed Halley audit result. Review records may be written only after fresh integrated verification and only with complete reviewer output. | Integrated verification complete, review and rereview records are coherent, and no Critical or Important finding remains. Reconcile and record every handoff before reclaiming a worker. |

No worker may begin a new write outside this table. If a fix needs another
path, stop, report the dependency, update the ownership claim through the
coordinator, and wait for a disjoint claim. An errored or incomplete task stays
owned until the coordinator marks it complete or transfers its remaining write
set to a named successor. After that handoff is recorded, immediately reclaim
the worker and use freed capacity only for a named successor or another bounded
task.

## Prerequisites And Dependency Order

1. The coordinator preserves the dirty-tree baseline and confirms that Worker B,
   Worker C, and the dormant Worker D / Halley successor claim have the exact
   scopes above. Halley's read-only scheduling/changelog audit is complete with
   no writes; its terminal findings are read-only input, not a review artifact
   or a new write claim.
2. The completed read-only follow-up review
   `docs/reviews/opencode-stage-393-followups-plan-review.md` recorded no
   Critical finding and required an explicit malformed-health regression test
   plus proof that the typed helper is the sole raw allowlist entry point. Its
   rereview `docs/reviews/opencode-stage-393-followups-plan-rereview.md` was
   approved after those conditions were represented. The older strict-plan
   fallback records are context only; a Claude timeout is never an approval.
3. The revised plan gate and its required primary/fallback plan review must be
   complete before any new implementation worker starts. Worker D / Halley
   must not start its three-file write set while the plan is awaiting review,
   while a review is timed out, or while a Critical or Important plan finding
   is unresolved. Worker B may finish an already-active smoke claim, but the
   coordinator must reconcile its handoff before integrating it with other
   changes.
4. Worker B depends on the existing smoke command harness and must keep the
   override local to its one empty-source refresh. Worker C depends on the
   review records and repository guidance but has no production or test write
   dependency. Worker D / Halley depends on the plan gate, the existing
   scheduling renderer APIs, and the existing changelog helper boundaries; it
   must not edit production scheduling code. The coordinator's Task 1, Task 3,
   and Task 4 write sets are disjoint from both worker write sets, but final
   verification is serialized after all claimed changes are reconciled.
5. Code or release review starts only from a stable integrated snapshot after
   the applicable fresh verification. Any subsequent diff invalidates the
   prior review and requires the affected verification and a rereview.

### Plan Gate Before Implementation Worker Start

- [ ] **Complete the revised-plan review before launching Worker D / Halley**

  The coordinator must run the primary Claude plan-review command against this
  revised plan, using the exact required read-only settings from the review
  protocol:

  ```bash
  tmp_plan_review="$(mktemp)"
  plan_review_rc=0
  timeout --foreground 900s claude --effort max --permission-mode plan --no-session-persistence \
    --tools Read,Grep,Glob,LS,Bash \
    -p "Review the revised Stage 393 follow-up implementation plan in /home/ubuntu/fashion-radar. Read AGENTS.md, docs/REVIEW_PROTOCOL.md, the supplemental plan, and the completed Stage 393 review records. Verify the dirty-tree baseline, exact Worker B/Feynman and Worker D/Halley write claims, the three-file scheduling/changelog coupled write set, empty-string local health coverage, direct cron/systemd negative assertions, the Stage 393 Unreleased Added changelog item and helper-scoped test, package commands, and the finding-fix verification rereview loop. Return one coherent plan review with Critical, Important, Minor, Verification, and Verdict sections. Do not edit files and do not treat timeout or tool-status output as approval." \
    > "$tmp_plan_review" || plan_review_rc="$?"
  ```

  Inspect the exit code and complete body. A `124` timeout, nonzero exit,
  empty capture, or incomplete/tool-status output does not satisfy the gate.
  Use the protocol's independent OpenCode fallback only after an honest Claude
  failure, capture one complete fallback body, and resolve every Critical or
  Important plan finding. Record the completed primary review or honest
  fallback review before launching Worker D / Halley. No implementation worker
  may begin its write claim until this gate is complete.

## Task 1: Make Local Article Health Allowlist Total

**Owner and files:** Coordinator; `tests/test_row_one_ops_check.py` and
`src/fashion_radar/row_one/ops_check.py`.

- [ ] **Step 1: Extend the exact overall-status regression tests first**

  Extend the existing test named
  `test_ops_check_overall_status_rejects_unhealthy_local_article_health` so
  each of `"degraded"`, `None`, `""`, `[]`, and `{}` is supplied to
  `local_article_routes` while `local_article_content` is `"ready"`, and the
  same five values are supplied to `local_article_content` while routes are
  `"ready"`. Assert the return value from `_overall_status(...)` is exactly
  `"attention"` and that the call does not raise. This is the top-level
  aggregation result consumed by the ops-check payload; do not assert only a
  helper boolean or only the absence of an exception.

  Keep the existing positive test named
  `test_ops_check_overall_status_accepts_known_healthy_local_article_health` and
  assert that both local fields set to `"ready"`, and both set to
  `"not_applicable"`, return `ROW_ONE_OPS_CHECK_HEALTHY_STATUS` while the
  site, freshness, server, and systemd inputs remain canonical. Preserve the
  existing output status value and ordering.

- [ ] **Step 2: Run the corrected focused test names**

  Run:

  ```bash
  UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
    tests/test_row_one_ops_check.py::test_ops_check_overall_status_rejects_unhealthy_local_article_health \
    tests/test_row_one_ops_check.py::test_ops_check_overall_status_accepts_known_healthy_local_article_health
  ```

  On a clean pre-fix snapshot, the malformed `[]` and `{}` cases must fail for
  the intended reason: the current raw frozenset membership path raises or
  incorrectly accepts a non-string. On this already-dirty baseline, record the
  observed result honestly; a pre-existing green candidate change is not a
  claimed red test. In either case, the integrated tree must get a fresh run
  after the implementation change.

- [ ] **Step 3: Route every local health membership check through one typed helper**

  Add this private helper in `src/fashion_radar/row_one/ops_check.py`:

  ```python
  def _is_healthy_local_article_status(status: object) -> bool:
      return isinstance(status, str) and status in ROW_ONE_LOCAL_ARTICLE_HEALTHY_STATUSES
  ```

  Use it for both local-article health checks inside `_overall_status`. The
  helper accepts `object`, returns `bool`, safely rejects `None`, the empty
  string, lists, and dictionaries, and accepts only string `ready` and
  `not_applicable`. Verify that this command reports exactly the helper's one
  membership expression and no residual raw call site:

  ```bash
  rg -n "in ROW_ONE_LOCAL_ARTICLE_HEALTHY_STATUSES" \
    src/fashion_radar/row_one/ops_check.py
  ```

  Do not alter any other status condition, payload key, payload field order,
  or strict/permissive CLI behavior.

- [ ] **Step 4: Re-run local ops-check and CLI coverage**

  ```bash
  UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
    tests/test_row_one_ops_check.py tests/test_row_one_cli.py
  ```

  The strict JSON tests must still demonstrate byte-identical payload output
  and the existing `ready`/`not_applicable` semantics; only the process exit
  status may differ for strict unhealthy output.

## Task 2: Restore Deterministic First-Run Publish Smoke

**Owner and files:** Worker B / Feynman; **ONLY**
`tests/test_first_run_smoke.py` and `scripts/check_first_run_smoke.py`.
The two files are one coupled write set.

- [ ] **Step 1: Extend the exact smoke command assertion before changing the script**

  In the existing test named
  `test_run_first_run_flow_uses_deterministic_local_command_sequence`, add
  `"--allow-unaccepted-content"` immediately after
  `"--skip-data-retention"` in the exact `row-one refresh` command tuple.
  Keep the assertion pinned to the smoke's exact `version: 1\nsources: []\n`
  setup. Make the fake command handler raise `SmokeError` when this flag is
  absent; returning a nonzero `CompletedProcess` is insufficient because the
  fake bypasses `run_cli`'s real return-code check.

- [ ] **Step 2: Run the corrected focused smoke test**

  ```bash
  UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
    tests/test_first_run_smoke.py::test_run_first_run_flow_uses_deterministic_local_command_sequence
  ```

  On a clean pre-fix snapshot, the expected failure is the missing override in
  the asserted command sequence. On the current dirty baseline, report a
  pre-existing pass as such and still perform the fresh integrated run.

- [ ] **Step 3: Pass the existing one-shot override only to the empty-source smoke refresh**

  In `scripts/check_first_run_smoke.py`, add:

  ```python
  "--allow-unaccepted-content",
  ```

  only to the one `row-one refresh` invocation after the smoke writes the
  deliberate empty-source fixture. Do not add the flag to shared/default command
  construction, normal CLI defaults, cron/systemd docs, or generated snippets.

- [ ] **Step 4: Assert the bypass warning and successful refresh**

  Capture that refresh's `CompletedProcess` and require `stderr` to contain this
  stable substring:

  ```text
  Warning: ROW ONE refresh content acceptance bypassed:
  ```

  The fake successful refresh result must include the same prefix in `stderr`.
  Keep the existing success-path stdout assertions and assert the refresh
  succeeds with the flag; do not match an entire warning sentence. Confirm the
  flag occurs only in this one smoke command by inspecting the script and test
  command construction.

- [ ] **Step 5: Run the focused handoff checks**

  ```bash
  UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
    tests/test_first_run_smoke.py
  UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
  UV_NO_CONFIG=1 uv --no-config run --frozen ruff check \
    scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
  UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check \
    scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
  ```

  Handoff success requires every command to exit `0`, the source smoke to
  print `First-run sample smoke passed.`, and the changed-file list to contain
  only the two claimed paths. The coordinator records verification results,
  unresolved work, and partial writes, then reclaims Worker B immediately.

## Task 3: Strict Guidance, Generated Snippets, And Changelog Contract

**Coordinator write set:** `docs/cli-reference.md`, `docs/row-one.md`,
`docs/scheduling.md`, and `tests/test_scheduling_docs.py`.

**Worker D / Halley write set:** **ONLY** `tests/test_scheduling.py`,
`CHANGELOG.md`, and the Stage 393 changelog contract portion of
`tests/test_row_one_docs.py`. These three files are exactly one coupled write
set. Worker D must not modify `src/fashion_radar/scheduling.py` or any other
production scheduling file.

- [ ] **Step 1: Keep strict documentation assertions bounded to their existing sections**

  The existing Stage 393 strict assertions in `tests/test_row_one_docs.py` are
  a read-only dependency for this task because the successor owns only that
  file's changelog contract portion. Verify that
  `test_row_one_docs_describe_stage_393_strict_ops_check_contract` normalizes
  `_ops_check_guidance(path)` for `README.md`, `docs/row-one.md`, and
  `docs/cli-reference.md`, rather than entire documents. It must assert all of
  the existing strict contract plus:

  ```text
  does not change the default permissive diagnostic mode
  ```

  Verify `test_row_one_docs_list_strict_ops_check_flag` and
  `test_cli_reference_indents_stage_393_as_ops_check_continuation` remain
  intact. The latter must require the Stage 393 prose to be an indented
  continuation of the `row-one ops-check` item and must reject a new top-level
  `- Stage 393` item.

  Verify `test_scheduling_docs_describe_stage_393_strict_ops_check_boundary`
  remains bounded to the `ROW ONE Daily Site` section and asserts all of:

  ```text
  strict mode remains read-only
  does not change the default permissive diagnostic mode
  the strict command is not included in normal scheduled refresh snippets
  ```

- [ ] **Step 2: Make scheduling prose preserve both negative boundaries**

  In the coordinator-owned documentation files, state that strict mode remains
  read-only, does not change the default permissive diagnostic mode, and is not
  included in normal scheduled refresh snippets. Preserve the existing
  statement that `--allow-unaccepted-content` is a one-shot manual override and
  must not be added to normal cron or systemd commands.

- [ ] **Step 3: Add direct negative assertions to both scheduling renderer tests**

  In Worker D's exact `tests/test_scheduling.py` claim, extend both
  `test_render_row_one_cron_uses_one_timestamp_shared_env_and_grouped_log` and
  `test_render_row_one_systemd_uses_one_timestamp_and_output_env` with these
  direct assertions against their renderer output:

  ```python
  assert "--allow-unaccepted-content" not in text
  assert "row-one ops-check --strict" not in text
  ```

  Use `service` instead of `text` in the systemd test. Keep all existing
  renderer assertions. Do not change `src/fashion_radar/scheduling.py`, CLI
  generation logic, or any production scheduling behavior.

- [ ] **Step 4: Add the Stage 393 Unreleased Added item and helper-scoped test**

  Under the existing `## [Unreleased]` / `### Added` section in `CHANGELOG.md`,
  add exactly one bounded Stage 393 item with this content:

  ```markdown
  - Stage 393 adds bounded ROW ONE diagnostic hardening and guidance: malformed
    local article health values yield `attention` instead of an exception;
    opt-in `row-one ops-check --strict` remains read-only and does not change
    the default permissive diagnostic mode or payloads; the one-shot
    `--allow-unaccepted-content` override is limited to the deterministic
    empty-source first-run smoke; normal cron/systemd snippets remain unchanged.
  ```

  In the Stage 393 changelog contract portion of `tests/test_row_one_docs.py`,
  add this helper-scoped test. It must inspect only the `[Unreleased]` `Added`
  subsection and the bounded Stage 393 list item, not assert against the whole
  changelog file:

  ```python
  def test_stage_393_changelog_records_bounded_unreleased_added_item() -> None:
      unreleased = _unreleased_changelog(_read(CHANGELOG))
      added = _subsection(unreleased, "Added")
      stage_393 = _normalized(_changelog_list_item(added, "- Stage 393"))

      for phrase in (
          "malformed local article health values yield `attention` instead of an exception",
          "opt-in `row-one ops-check --strict` remains read-only",
          "does not change the default permissive diagnostic mode or payloads",
          "the one-shot `--allow-unaccepted-content` override is limited to the deterministic empty-source first-run smoke",
          "normal cron/systemd snippets remain unchanged",
      ):
          assert phrase in stage_393
  ```

  Preserve the existing `test_changelog_list_item_stops_before_ordinary_next_bullet`
  helper-boundary coverage. Do not add any unrelated changelog item.

- [ ] **Step 5: Run the three-file successor checks and bounded documentation checks**

  After the plan gate is complete, Worker D / Halley runs:

  ```bash
  UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
    tests/test_scheduling.py::test_render_row_one_cron_uses_one_timestamp_shared_env_and_grouped_log \
    tests/test_scheduling.py::test_render_row_one_systemd_uses_one_timestamp_and_output_env \
    tests/test_row_one_docs.py::test_stage_393_changelog_records_bounded_unreleased_added_item \
    tests/test_row_one_docs.py::test_changelog_list_item_stops_before_ordinary_next_bullet \
    tests/test_row_one_docs.py::test_row_one_docs_describe_stage_393_strict_ops_check_contract \
    tests/test_scheduling_docs.py::test_scheduling_docs_describe_stage_392_content_acceptance_operations \
    tests/test_scheduling_docs.py::test_scheduling_docs_describe_stage_393_strict_ops_check_boundary
  UV_NO_CONFIG=1 uv --no-config run --frozen ruff check \
    tests/test_scheduling.py tests/test_row_one_docs.py
  UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check \
    tests/test_scheduling.py tests/test_row_one_docs.py
  git diff --check -- tests/test_scheduling.py CHANGELOG.md tests/test_row_one_docs.py
  ```

  Then inspect generated snippets without writing repository files:

  ```bash
  tmp_schedule="$(mktemp -d)"
  cleanup_schedule() { rm -rf "$tmp_schedule"; }
  trap cleanup_schedule EXIT
  UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one schedule \
    --mode cron --project-dir "$PWD" --config-dir "$PWD/configs" \
    --data-dir "$PWD/data" --reports-dir "$PWD/reports" \
    --output-dir "$PWD/reports/row-one/site" --time 04:00 \
    > "$tmp_schedule/cron.txt"
  UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one schedule \
    --mode systemd --project-dir "$PWD" --config-dir "$PWD/configs" \
    --data-dir "$PWD/data" --reports-dir "$PWD/reports" \
    --output-dir "$PWD/reports/row-one/site" --time 04:00 \
    --host 0.0.0.0 --port 8787 > "$tmp_schedule/systemd.txt"
  ! rg -n -- '--allow-unaccepted-content|row-one ops-check --strict' \
    "$tmp_schedule/cron.txt" "$tmp_schedule/systemd.txt"
  cleanup_schedule
  trap - EXIT
  test ! -e "$tmp_schedule"
  ```

  Success requires every focused check to exit `0`, both direct renderer tests
  to reject both forbidden strings, the helper-scoped test to find the Stage
  393 item only inside `[Unreleased]` / `Added`, both generated snippets to
  contain neither forbidden command, and the temporary directory to be
  removed. The successor handoff must list exactly the three coupled files,
  verification results, unresolved work, and partial writes, then the
  coordinator reclaims Worker D / Halley.

## Task 4: Lock The Parallel Execution Rule

**Owner and files:** Coordinator; `tests/test_agents_scope_docs.py` only.

- [ ] **Step 1: Keep the exact ownership-contract test aligned with AGENTS.md**

  Extend or preserve the existing test
  `test_agents_parallel_execution_contract_covers_scope_ownership_and_reuse`.
  Extract `## Parallel Agent Execution`, normalize it, and require stable
  clauses for all of:

  ```text
  parallel agent execution as a mandatory default
  run independent nodes in parallel
  exact writable files or globs
  coupled write set
  conflicting claim on that write set
  expected completion state
  changed-file list
  verification commands/results
  unresolved work
  partial writes
  transfers its remaining write set to a named successor
  immediately reclaim a completed, errored, or no-longer-needed agent
  existing `main` worktree on the `main` branch
  do not create, use, or switch to another git worktree or branch
  ```

  Keep the ownership-transfer phrase distinct from the freed-capacity phrase:
  only a named successor may receive an incomplete task's remaining write set;
  after that handoff, released capacity may be assigned to a named successor or
  another bounded task. Keep the ordering assertions that verify handoff before
  reclaim and reclaim before reuse.

- [ ] **Step 2: Run the exact repository-guidance test**

  ```bash
  UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
    tests/test_agents_scope_docs.py::test_agents_parallel_execution_contract_covers_scope_ownership_and_reuse
  ```

  If the baseline already contains the candidate AGENTS wording, record that
  as a baseline-green result and do not weaken the ownership prerequisite to
  force a red test. No additional AGENTS edit is part of this plan node.

## Task 5: Integrated Review And Release Gate

**Owner and files:** Coordinator; future review records may be created only
after the review command below returns complete output:

- `docs/reviews/claude-code-stage-393-code-review.md`
- `docs/reviews/opencode-stage-393-code-review.md` only as an honest fallback
- analogous `*-code-rereview.md` or `*-release-rereview.md` records only after
  a finding fix changes the stable snapshot

The planning worker does not create or modify any of these records in this
task.

- [ ] **Step 1: Reconcile handoffs and run integrated regression verification**

  Record Worker B's two-file handoff and the read-only scheduling/changelog
  audit before running the integrated command. Then run:

  ```bash
  UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
    tests/test_row_one_ops_check.py tests/test_row_one_cli.py \
    tests/test_row_one_docs.py tests/test_scheduling.py \
    tests/test_scheduling_docs.py tests/test_agents_scope_docs.py \
    tests/test_first_run_smoke.py tests/test_cli_docs.py
  ```

  Success requires exit `0` on the reconciled integrated tree. Worker-reported
  checks are preliminary; the coordinator must run this fresh command itself.

- [ ] **Step 2: Request the primary Claude Code review with honest capture and fallback**

  Start only from the stable tree after Step 1. Use a temporary file outside
  the repository and this primary command shape, including all required
  read-only settings:

  ```bash
  tmp_review="$(mktemp)"
  claude_rc=0
  timeout --foreground 900s claude --effort max --permission-mode plan --no-session-persistence \
    --tools Read,Grep,Glob,LS,Bash \
    -p "Review the stable integrated Stage 393 follow-up diff in /home/ubuntu/fashion-radar. Read AGENTS.md, docs/REVIEW_PROTOCOL.md, the current supplemental plan, the changed production/tests/docs files, and the relevant completed review records. Check scope preservation, malformed local health handling including empty strings and unhashable values, smoke-only acceptance bypass, generated scheduling snippets, CHANGELOG scope, ownership claims, fresh verification, and release hygiene. Return one coherent review body with Critical, Important, Minor, Verification, and Verdict sections. Do not edit files and do not present a timeout or tool-status message as a review or approval." \
    > "$tmp_review" || claude_rc="$?"
  ```

  Inspect `claude_rc`, file size, and the complete captured body. A `124`
  timeout, any other nonzero exit, empty output, or output containing only
  status/tool-capture text is not a review and must not be copied into
  `docs/reviews/`. Record that timeout/failure only in scratch output outside
  the repository, remove the scratch file, and use the independent fallback:

  ```bash
  rm -f "$tmp_review"
  tmp_review="$(mktemp)"
  opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
    --dir /home/ubuntu/fashion-radar \
    "Review the stable integrated Stage 393 follow-up diff in /home/ubuntu/fashion-radar after Claude Code was unavailable or timed out. Read AGENTS.md, docs/REVIEW_PROTOCOL.md, the supplemental plan, changed files, and completed review records. Check scope preservation, empty-string and unhashable local health values, smoke-only override placement, normal generated scheduling snippets, CHANGELOG scope, ownership claims, and fresh verification. Return one coherent review body with Critical, Important, Minor, Verification, and Verdict sections. Do not edit files and do not claim Claude approval." \
    > "$tmp_review"
  test -s "$tmp_review"
  sed -n '1,500p' "$tmp_review"
  ```

  Copy exactly one inspected, coherent body to the applicable review record;
  never copy a timeout stub, duplicated verdict, truncated output, `Wrote`
  status line, or empty output. Remove `tmp_review` after the record is safely
  captured. The command exits successfully only when the chosen record has a
  complete body and one verdict, and the timeout path has left no repository
  artifact.

- [ ] **Step 3: Use the finding-fix -> fresh-verification -> rereview loop**

  For every Critical or Important finding, apply this exact loop:

  1. Record the finding and assign its fix to the existing non-conflicting
     owner and exact write set. Do not silently expand a worker's claim.
  2. Apply the smallest in-scope fix. A diff change invalidates the previous
     stable snapshot, previous verification, and previous review verdict.
  3. Run fresh affected tests, lints, and source smoke checks. Capture their
     commands and exit results in the handoff; do not treat an earlier worker
     result as fresh coordinator verification.
  4. Reconcile the changed-file list and establish a new stable integrated
     snapshot. If the finding fix touched a review record, use a new
     rereview record rather than appending a second verdict to the old one.
  5. Rerun the same Claude primary command with the new stable snapshot. If it
     times out or has no coherent body, use the honest OpenCode fallback above
     and record the fallback as fallback review output.
  6. Repeat from step 1 until the rereview has no unresolved Critical or
     Important finding. Minor findings may be recorded with a concrete reason
     for deferral, but they may not conceal an unresolved Critical or Important
     issue.

- [ ] **Step 4: Run the complete release verification gate**

  ```bash
  UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider
  UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
  UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
  UV_NO_CONFIG=1 uv lock --check
  UV_NO_CONFIG=1 uv sync --locked --dev --check
  UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
  git diff --check
  ```

  Every command must exit `0`. `check_release_hygiene.py` must report no
  secrets, cookies, tokens, private data, generated reports, local SQLite
  files/sidecars, build artifacts, or CodeGraph databases. The coordinator must
  compare the final changed-file list with the preserved dirty-tree baseline
  and must not remove unrelated user changes.

- [ ] **Step 5: Run executable package, archive, installed-wheel, and optional dashboard smokes**

  Build only under a temporary root. The following block must be run as one
  shell session so its cleanup and success checks are meaningful:

  ```bash
  tmp_root="$(mktemp -d)"
  tmp_build="$tmp_root/build"
  tmp_env="$tmp_root/env"
  tmp_dash="$tmp_root/dashboard"
  tmp_run="$tmp_root/run"
  mkdir -p "$tmp_build"
  cleanup_package_smoke() { rm -rf "$tmp_root"; }
  trap cleanup_package_smoke EXIT

  UV_NO_CONFIG=1 uv --no-config build --out-dir "$tmp_build"
  test "$(find "$tmp_build" -maxdepth 1 -type f -name '*.whl' | wc -l)" -eq 1
  test "$(find "$tmp_build" -maxdepth 1 -type f -name '*.tar.gz' | wc -l)" -eq 1
  UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"

  UV_NO_CONFIG=1 uv venv "$tmp_env/venv"
  wheel_path="$(find "$tmp_build" -maxdepth 1 -type f -name '*.whl' -print -quit)"
  test -n "$wheel_path"
  UV_NO_CONFIG=1 uv pip install --python "$tmp_env/venv/bin/python" "$wheel_path"
  "$tmp_env/venv/bin/fashion-radar" --help
  "$tmp_env/venv/bin/python" -m fashion_radar --help
  "$tmp_env/venv/bin/fashion-radar" init \
    --config-dir "$tmp_run/config" --data-dir "$tmp_run/data" \
    --reports-dir "$tmp_run/reports"
  "$tmp_env/venv/bin/fashion-radar" doctor \
    --config-dir "$tmp_run/config" --data-dir "$tmp_run/data" \
    --reports-dir "$tmp_run/reports"
  "$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py \
    --repo-root . --python "$tmp_env/venv/bin/python" --installed
  "$tmp_env/venv/bin/python" -c "from importlib import resources; text = resources.files('fashion_radar.templates').joinpath('daily_report.md').read_text(encoding='utf-8'); assert 'Fashion Radar Daily Report' in text"

  UV_NO_CONFIG=1 uv venv "$tmp_dash/venv"
  UV_NO_CONFIG=1 uv pip install --python "$tmp_dash/venv/bin/python" "${wheel_path}[dashboard]"
  "$tmp_dash/venv/bin/python" -c "import fashion_radar.dashboard.app; import fashion_radar.dashboard.queries"

  cleanup_package_smoke
  trap - EXIT
  test ! -e "$tmp_root"
  test ! -d build
  test ! -d dist
  ```

  Success requires the build to exit `0`, exactly one wheel and one sdist to be
  present, `check_package_archives.py` to print
  `Package archives contain required files.`, all installed help/init/doctor
  checks to exit `0`, the installed smoke to print
  `First-run sample smoke passed.`, the import-origin check to resolve into the
  temporary venv, and the dashboard imports to exit `0` when the dashboard
  extra is in the release gate. The archive checker must confirm that the sdist
  includes `CHANGELOG.md` and `docs/scheduling.md` while excluding review and
  plan artifacts. The explicit temporary-root and repository `build`/`dist`
  checks are cleanup conditions; no archive or venv may remain in the worktree.

- [ ] **Step 6: Request final release rereview on the unchanged verified snapshot**

  Run the same Claude primary release-review command shape from Step 2, with a
  release prompt that reads the final diff, full verification output,
  `CHANGELOG.md` scope decision, package/archive results, and generated
  scheduling-snippet results. Use the same honest timeout fallback and create
  a release rereview record only after complete output. If any release review
  finding changes a file, return to Step 3 and rerun the affected verification
  before rereviewing.

  This plan stops after the verified handoff. Do not stage, commit, push, fetch,
  reset, or change remote parity in this task; any later GitHub upload decision
  requires separate explicit authorization.

## Handoff Record Requirements

Before reclaiming any completed, errored, or no-longer-needed worker, the
coordinator records a short handoff containing:

- the exact changed-file list and whether it stayed within the claimed glob;
- every verification command and its observed result;
- unresolved work, including deferred Minor findings and their reason;
- partial writes, including an incomplete file or an output file that must not
  be treated as a completed review record.

The coordinator then marks the task complete or transfers its remaining write
set to a named successor, immediately reclaims the worker, and only then uses
freed capacity for another bounded task. The final report for this plan-only
worker must separately state the changed path, summary, checks, unresolved
issues, and partial writes.

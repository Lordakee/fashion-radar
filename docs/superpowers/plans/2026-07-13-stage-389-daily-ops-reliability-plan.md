# Stage 389 Daily Operations Reliability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development or superpowers:executing-plans
> task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Make the local 04:00 ROW ONE workflow truthful to schedulers and
operators while aligning shipped documentation with the actual local scoring and
smoke behavior.

**Architecture:** Keep source scoring and collection unchanged. Treat failed
SQLite retention as a post-artifact command failure; centralize the existing
three-unit ROW ONE systemd payload; and retain ops-check as a filename-only
evidence probe whose healthiest state explicitly leaves scheduling unverified.
Package every newly changed public guide in the sdist.

**Tech Stack:** Python 3.11+, Typer, pytest, Ruff, existing scheduling renderers,
Markdown contract tests, uv, standard-library packaging checks, Git.

---

## File Map

- Modify: src/fashion_radar/scheduling.py - canonical ordered ROW ONE unit
  constants.
- Modify: src/fashion_radar/cli.py - retention exit, schedule preview reuse,
  and truthful ops-check text.
- Modify: src/fashion_radar/row_one/ops_check.py - shared tuple re-export,
  filename-only evidence enum, actions, and healthy top-level state.
- Modify: tests/test_row_one_cli.py, tests/test_row_one_ops_check.py, and
  tests/test_scheduling.py - behavior contracts.
- Modify: docs/PROJECT_BRIEF.md, docs/scoring.md, README.md, docs/row-one.md,
  docs/scheduling.md, docs/first-run.md, docs/cli-reference.md,
  docs/data-retention.md, and CHANGELOG.md - accurate public contracts.
- Modify: tests/test_project_brief_docs.py, tests/test_scoring_docs.py,
  tests/test_row_one_docs.py, tests/test_scheduling_docs.py,
  tests/test_first_run_docs.py, and tests/test_data_retention_docs.py - public
  document assertions.
- Modify: scripts/check_package_archives.py and tests/test_package_archives.py
  - sdist coverage for changed public guides.
- Create: docs/reviews/claude-code-stage-389-plan-review.md,
  docs/reviews/opencode-stage-389-plan-review.md,
  docs/reviews/claude-code-stage-389-plan-rereview.md,
  docs/reviews/claude-code-stage-389-plan-release-safety-rereview.md,
  docs/reviews/claude-code-stage-389-plan-test-contract-rereview.md,
  docs/reviews/claude-code-stage-389-code-review.md, and
  docs/reviews/claude-code-stage-389-release-review.md - concise,
  credential-free review records. Create matching Claude rereview or OpenCode
  fallback records only if a review-driven diff requires them.

## Parallel-Worker Ownership And Order

The coordinator owns Task 0, Task 7, integration, cross-cutting verification,
and conflict resolution. Workers own these disjoint write sets and completion
states:

- Worker A owns Task 1: docs/PROJECT_BRIEF.md, docs/scoring.md,
  tests/test_project_brief_docs.py, and tests/test_scoring_docs.py. Completion
  is the focused scoring-document suite GREEN.
- Worker B owns Task 2: src/fashion_radar/cli.py and
  tests/test_row_one_cli.py. Completion is the ROW ONE CLI suite GREEN.
- Worker C owns Task 3: src/fashion_radar/scheduling.py,
  src/fashion_radar/cli.py, tests/test_scheduling.py, and
  tests/test_row_one_cli.py. Completion is its scheduling and CLI suite GREEN.
- Worker D owns Task 4: src/fashion_radar/row_one/ops_check.py,
  src/fashion_radar/cli.py, tests/test_row_one_ops_check.py, and
  tests/test_row_one_cli.py. Completion is its ops-check and CLI suite GREEN.
- Worker E owns Task 5: README.md, docs/row-one.md, docs/scheduling.md,
  docs/first-run.md, docs/cli-reference.md, docs/data-retention.md, and their
  listed documentation tests. Completion is the focused documentation suite
  GREEN.
- Worker F owns Task 6: scripts/check_package_archives.py and
  tests/test_package_archives.py. Completion is the archive suite GREEN.

Tasks 2, 3, and 4 are a coupled sequential write set on
src/fashion_radar/cli.py and tests/test_row_one_cli.py. Task 2 must not overlap
Task 3 or Task 4. Task 4 must start only after Task 3 is integrated and GREEN,
because it imports ROW_ONE_SYSTEMD_UNITS from scheduling.py. Tasks 1, 5, and 6
may run in parallel with each other and with the coupled chain because their
write sets do not overlap.

## Task 0: Record And Accept The Plan Reviews

**Files:**
- Create: docs/reviews/claude-code-stage-389-plan-review.md
- Create: docs/reviews/opencode-stage-389-plan-review.md
- Create: docs/reviews/claude-code-stage-389-plan-rereview.md
- Modify: this plan and its Stage 389 design as needed to resolve findings

- [ ] **Step 1: Capture the primary plan review.**

Save one complete, coherent Claude Code plan-review body to
docs/reviews/claude-code-stage-389-plan-review.md. It must contain one verdict,
no live-capture stub, no tool-status line, no duplicated verdict, no truncation,
and no credential or token material.

- [ ] **Step 2: Record the required OpenCode plan revision.**

Run local OpenCode with model zhipuai-coding-plan/glm-5.2 and max variant after
the primary review. Save one coherent revision verdict and actionable findings
to docs/reviews/opencode-stage-389-plan-review.md using the same capture
hygiene.

- [ ] **Step 3: Resolve all critical and important plan findings.**

Update the design or plan, run whitespace and placeholder checks, and obtain a
fresh Claude Code plan rereview. Save its single coherent body to
docs/reviews/claude-code-stage-389-plan-rereview.md. Task 1 through Task 7 must
not start until the rereview has no critical or important finding.

## Task 1: Pin The Local Scoring Contract

**Files:**
- Modify: tests/test_project_brief_docs.py
- Modify: tests/test_scoring_docs.py
- Modify: docs/PROJECT_BRIEF.md
- Modify: docs/scoring.md

- [ ] **Step 1: Write the failing documentation contracts.**

Require this exact Product Brief sentence:

~~~
Score local heat changes using mention volume, recent growth, source weight,
and source diversity across configured sources and imported local signals.
~~~

Require cross-platform spread to be absent from Product Positioning. Require the
scoring Inputs section to retain distinct-source_name diversity and to include:

~~~
Imported item platform labels are retained as local provenance for review output.
They do not affect heat scores and do not establish platform coverage.
~~~

- [ ] **Step 2: Run the focused contracts and verify RED.**

~~~bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_project_brief_docs.py tests/test_scoring_docs.py -q
~~~

Expected: the Product Brief assertion fails because it still promises
cross-platform spread.

- [ ] **Step 3: Correct only the public wording.**

Replace the scoring workflow bullet in docs/PROJECT_BRIEF.md with the exact
sentence above. Add the two provenance sentences directly after the Inputs list
in docs/scoring.md. Do not modify scoring.py, configurations, schemas, or
report calculations.

- [ ] **Step 4: Run the focused contracts and verify GREEN.**

Run the Step 2 command. Expected: every selected test passes.

## Task 2: Make SQLite Retention Failure Observable

**Files:**
- Modify: tests/test_row_one_cli.py
- Modify: src/fashion_radar/cli.py

- [ ] **Step 1: Write the failing post-artifact failure test.**

Rename the existing retention-warning test to
test_row_one_refresh_fails_after_sqlite_retention_failure. Keep its mocked
clean_old_data error and require:

~~~python
assert result.exit_code == 1, result.output
assert "SQLite retention: failed: database locked" in result.output
assert "ROW ONE refresh failed" not in result.output
assert calls[-1] == "clean_old_data"
~~~

Use str.index assertions to prove Markdown, JSON, and HTML report lines appear
before the retention diagnostic; Site, edition JSON, manifest, and final access
output appear after it. Preserve successful and --skip-data-retention
exit-code-zero assertions.

- [ ] **Step 2: Run the focused test and verify RED.**

~~~bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py::test_row_one_refresh_fails_after_sqlite_retention_failure -q
~~~

Expected: it fails because the current command exits 0.

- [ ] **Step 3: Return nonzero after all ordinary output.**

In row_one_refresh, leave the retention exception handling and every normal
output line in place. Immediately after the final
format_row_one_site_access_message(host, port) output, add:

~~~python
if data_retention_error is not None:
    raise typer.Exit(1)
~~~

Do not send this condition through the pipeline-wide exception handler.

- [ ] **Step 4: Verify GREEN for all ROW ONE CLI tests.**

~~~bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py -q
~~~

Expected: all selected tests pass.

## Task 3: Use One Systemd Payload Set Everywhere

**Files:**
- Modify: tests/test_scheduling.py
- Modify: tests/test_row_one_cli.py
- Modify: src/fashion_radar/scheduling.py
- Modify: src/fashion_radar/cli.py

- [ ] **Step 1: Write failing canonical-preview tests.**

Add a scheduling test for the exact tuple:

~~~python
(
    "row-one-refresh.service",
    "row-one-refresh.timer",
    "row-one-serve.service",
)
~~~

Add a CLI test named
test_row_one_schedule_systemd_preview_matches_install_local_payloads. Invoke
both commands with --mode systemd --host 0.0.0.0 --port 9876 where applicable.
Require the three canonical headings in order, reject legacy headings
row-one.service and row-one.timer, and compare payload sections with
row-one install-local --dry-run. Assert the serve payload includes both
0.0.0.0 and 9876. Extend schedule help coverage to require --host and --port.

- [ ] **Step 2: Run the focused tests and verify RED.**

~~~bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_scheduling.py tests/test_row_one_cli.py -q
~~~

Expected: the CLI preview assertion fails because it has two legacy headings.
The new scheduling-constant test can fail at collection with ImportError until
ROW_ONE_SYSTEMD_UNITS is added to scheduling.py.

- [ ] **Step 3: Centralize names and reuse existing payload rendering.**

Define in scheduling.py:

~~~python
ROW_ONE_REFRESH_SERVICE = "row-one-refresh.service"
ROW_ONE_REFRESH_TIMER = "row-one-refresh.timer"
ROW_ONE_SERVE_SERVICE = "row-one-serve.service"
ROW_ONE_SYSTEMD_UNITS = (
    ROW_ONE_REFRESH_SERVICE,
    ROW_ONE_REFRESH_TIMER,
    ROW_ONE_SERVE_SERVICE,
)
~~~

Import these in the CLI. Key _row_one_systemd_unit_payloads from the constants
in their declared order. Add existing ROW ONE host/port option objects to
row_one_schedule; in its systemd branch iterate that helper and print the same
headings and values as install-local --dry-run. Do not invoke or enable systemd
and do not modify generic schedule-example --mode systemd behavior.

- [ ] **Step 4: Run the focused tests and verify GREEN.**

Run the Step 2 command. Expected: all selected tests pass.

## Task 4: Make Ops-Check Filename-Only And Explicitly Unverified

**Files:**
- Modify: tests/test_row_one_ops_check.py
- Modify: tests/test_row_one_cli.py
- Modify: src/fashion_radar/row_one/ops_check.py
- Modify: src/fashion_radar/cli.py

- [ ] **Step 1: Write failing filename-evidence tests.**

For a fresh site, responding local server, healthy local articles, and all three
canonical filenames, assert:

~~~python
assert payload["status"] == "site_ready_scheduler_unverified"
assert payload["systemd"]["status"] == "unit_files_present"
assert payload["systemd"]["verification"] == "filenames_only"
assert payload["actions"] == []
~~~

Keep simple [Unit] placeholder files, then add a focused case where all three
files contain unrelated or malformed text and require the exact same result.
This is an output regression test, not proof of the no-read boundary.

Add a separate all-empty-files case: create the three canonical paths with
zero-byte content and require top-level site_ready_scheduler_unverified,
systemd unit_files_present, filenames_only, the exact all-true units map, and
an empty actions list. This confirms output equivalence when file content is
empty; the direct monkeypatched helper test below enforces the no-read boundary.

Import and call _systemd_payload directly with all three canonical files present.
Monkeypatch Path.read_text, Path.read_bytes, and Path.open to raise
AssertionError whenever the target is a canonical unit path. Require the helper
to still return unit_files_present, filenames_only, and the expected boolean
units map. This direct helper test avoids conflating the unrelated runtime.json
read in build_row_one_ops_check_payload with systemd filename evidence.

Parameterize each single missing canonical filename and the all-missing case.
For every parameter, require:

~~~python
assert payload["status"] == "attention"
assert payload["systemd"]["status"] == "missing"
assert payload["systemd"]["verification"] == "filenames_only"
assert payload["systemd"]["units"] == expected_units
assert payload["actions"] == [
    "Run `fashion-radar row-one install-local --dry-run` to inspect user systemd units."
]
~~~

Set expected_units to the exact three-name boolean map for every single-missing
and all-missing case. Update healthy local article route/content tests only at
the top level; retain their nested ready states. Update stale, unreachable-server,
and missing-article tests to retain their current attention or unknown precedence
while reporting unit_files_present if all filenames exist.

Retain the existing invalid-runtime plus partial-units case and assert top-level
unknown, systemd missing, filenames_only, and the boolean units map. Add a second
invalid-runtime case with all three names present and assert top-level unknown,
not site_ready_scheduler_unverified, systemd unit_files_present, filenames_only,
and the exact all-true units map. These two cases pin the current
unknown-before-systemd-status precedence.

Update JSON-forwarding and human-output CLI fixtures to be coherent healthy
payloads. Require json.loads(result.output) in the JSON-forwarding test to
contain exactly:

~~~python
assert payload["status"] == "site_ready_scheduler_unverified"
assert payload["systemd"]["status"] == "unit_files_present"
assert payload["systemd"]["verification"] == "filenames_only"
assert payload["actions"] == []
~~~

Require these exact human renderer substrings:

~~~python
assert "Systemd verification: filenames_only" in result.output
assert "scheduler state is not verified" in result.output
~~~

- [ ] **Step 2: Run the focused ops tests and verify RED.**

~~~bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_ops_check.py tests/test_row_one_cli.py -q
~~~

Expected: the old healthy path returns top-level ready and systemd present.

- [ ] **Step 3: Implement only filename evidence.**

Import ROW_ONE_SYSTEMD_UNITS from scheduling.py in ops_check.py; this keeps
fashion_radar.row_one.ops_check.ROW_ONE_SYSTEMD_UNITS available to existing
imports. Keep _systemd_payload limited to Path.is_file for the three primary
names. Preserve the boolean units map and its missing-name details, change only
its positive status to unit_files_present, and add verification:
filenames_only on both positive and missing paths.

Do not read file contents, parse systemd directives, inspect drop-ins, import
or run systemctl/loginctl, add configured/invalid states, or add process probes
beyond the current server probe. Change _actions to suppress install-local
guidance only when the systemd status is unit_files_present. Change the sole
healthy _overall_status return to site_ready_scheduler_unverified; preserve
existing unknown and attention precedence. Make the text renderer emit
Systemd verification: filenames_only and scheduler state is not verified in its
human-readable output.

- [ ] **Step 4: Run the focused ops tests and verify GREEN.**

Run the Step 2 command. Expected: all selected tests pass.

## Task 5: Align Operations Documentation And Contracts

**Files:**
- Modify: README.md
- Modify: docs/row-one.md
- Modify: docs/scheduling.md
- Modify: docs/first-run.md
- Modify: docs/cli-reference.md
- Modify: docs/data-retention.md
- Modify: tests/test_row_one_docs.py
- Modify: tests/test_scheduling_docs.py
- Modify: tests/test_first_run_docs.py
- Modify: tests/test_data_retention_docs.py

- [ ] **Step 1: Write failing public-document contracts.**

Require the docs to say:

- non-skipped SQLite retention failure returns nonzero after reports and site
  output;
- row-one schedule --mode systemd and install-local use all three canonical unit
  names;
- Fashion Radar does not invoke systemctl or loginctl;
- unattended user-systemd operation requires manual
  loginctl show-user "$USER" -p Linger verification, and enabling lingering can
  require an authorized operator under host policy;
- filename-only ops-check reports site_ready_scheduler_unverified and
  unit_files_present only as filename evidence and does not prove contents,
  drop-ins, enablement, activity, or a successful future refresh;
- the first-run smoke checks dry-run URLs and starts, fetches through, and
  terminates a temporary local HTTP server.

Add scoped negative assertions across README.md, docs/row-one.md, and
docs/cli-reference.md that the obsolete exact ready-from-expected-unit-files
promise and Systemd units: present wording are absent. Do not globally ban
unrelated nested article uses of ready.

- [ ] **Step 2: Run focused documentation tests and verify RED.**

~~~bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_scheduling_docs.py tests/test_first_run_docs.py tests/test_data_retention_docs.py -q
~~~

Expected: existing wording fails at least filename-only, lingering, and smoke
contracts.

- [ ] **Step 3: Write consistent, manual operator guidance.**

Keep activation manual and local in the ROW ONE-specific sections:

~~~bash
loginctl show-user "$USER" -p Linger
loginctl enable-linger "$USER"
systemctl --user daemon-reload
systemctl --user enable --now row-one-refresh.timer
systemctl --user enable --now row-one-serve.service
systemctl --user status row-one-refresh.timer row-one-serve.service
~~~

Explain that an authorized operator may be needed for lingering. Add --host and
--port to the ROW ONE schedule reference. Preserve generic
schedule-example --mode systemd documentation, historical release-note scope,
and all claims that remain true for unrelated commands.

- [ ] **Step 4: Run focused documentation tests and verify GREEN.**

Run the Step 2 command. Expected: all selected tests pass.

## Task 6: Ship Every Changed Public Guide In The sdist

**Files:**
- Modify: tests/test_package_archives.py
- Modify: scripts/check_package_archives.py

- [ ] **Step 1: Write failing archive contract tests.**

Extend the SDIST_FILES fixture with exactly:

~~~text
docs/PROJECT_BRIEF.md
docs/scoring.md
docs/scheduling.md
docs/first-run.md
docs/data-retention.md
~~~

Add a parameterized test beside the existing missing-ROW-ONE-doc case. For each
path above, remove it from the synthetic sdist and require:

~~~text
sdist archive missing required file: <path>
~~~

- [ ] **Step 2: Run the archive tests and verify RED.**

~~~bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_package_archives.py -q
~~~

Expected: the checker currently accepts an sdist missing each newly required
public guide.

- [ ] **Step 3: Add exactly the five new public-guide requirements.**

Append the same five paths to SDIST_REQUIRED_PATHS. Do not add already required
README.md, CHANGELOG.md, docs/row-one.md, or docs/cli-reference.md. Do not add
Stage plans, specifications, or review records because the package deliberately
excludes docs/superpowers and docs/reviews.

- [ ] **Step 4: Run the archive tests and verify GREEN.**

Run the Step 2 command. Expected: all selected tests pass.

## Task 7: Review, Commit, Validate, And Publish

**Files:**
- Modify: CHANGELOG.md
- Create: docs/reviews/claude-code-stage-389-code-review.md
- Create if a review-driven diff occurs:
  docs/reviews/claude-code-stage-389-code-rereview.md
- Create: docs/reviews/claude-code-stage-389-release-review.md
- Create if a review-driven diff occurs:
  docs/reviews/claude-code-stage-389-release-rereview.md
- Create only if Claude Code is unavailable:
  docs/reviews/opencode-stage-389-code-review.md and
  docs/reviews/opencode-stage-389-release-review.md

- [ ] **Step 1: Add the accurate Unreleased entry.**

Describe local source-diversity wording, post-output nonzero retention failure,
canonical systemd preview payloads, filename-only scheduler-unverified ops
status, manual lingering guidance, and corrected temporary HTTP smoke wording.
Do not claim auto-enablement, static directive validation, platform scoring,
collectors, or deployment automation.

- [ ] **Step 2: Establish a freshly verified integrated snapshot.**

After Tasks 1 through 6 are integrated and before code review, run every focused
suite named in those tasks, then run:

~~~bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
~~~

Record the exact completed commands and outcomes for the reviewer. Any diff
after this point requires the affected checks to be rerun before the next
review.

- [ ] **Step 3: Obtain and, if needed, repeat the code review.**

Run Claude Code with max effort, plan permission mode, no persistent session,
and only Read, Grep, Glob, LS, and Bash. Give it the Stage 389 goal, this plan,
the changed-file list, the stable-snapshot verification outcomes, and the
explicit filename-only boundary. Save a concise verdict and findings only in
docs/reviews/claude-code-stage-389-code-review.md. If Claude Code is
unavailable, use OpenCode with zhipuai-coding-plan/glm-5.2 max and save the
fallback record under the matching opencode path.

Resolve every critical or important finding. For every review-driven diff,
rerun the affected tests and Ruff checks, then obtain the corresponding
claude-code-stage-389-code-rereview.md before staging. Every review record must
contain one coherent completed body with no raw tool output, live-capture stub,
empty result, duplicated verdict, timeout text, credential, token, or URL with
credentials.

- [ ] **Step 4: Stage and commit the reviewed implementation snapshot.**

Stage only intended source, tests, public docs, changelog, Stage 389 design and
plan, initial and rereview plan records, the OpenCode plan revision record, and
the applicable code-review record. Before commit run:

~~~bash
git diff --cached --check
git diff --cached --quiet -- uv.lock || { echo "Stage 389 must not modify uv.lock" >&2; exit 1; }
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL -u UV_PROJECT_ENVIRONMENT -u UV_INDEX -u UV_FIND_LINKS -u PIP_INDEX_URL -u PIP_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
~~~

Commit with Stage 389: strengthen daily operations reliability and capture the
exact committed SHA with git rev-parse HEAD. Do not push an uncommitted or
only-staged worktree.

- [ ] **Step 5: Run release validation from the committed snapshot.**

Define this shell helper in the protected release terminal so every dependency
operation ignores inherited private indexes and user uv configuration:

~~~bash
public_uv() {
  env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL -u UV_PROJECT_ENVIRONMENT -u UV_INDEX -u UV_FIND_LINKS -u PIP_INDEX_URL -u PIP_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv "$@"
}
~~~

Run:

~~~bash
public_uv lock --check
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then exit 1; fi
public_uv sync --locked --dev
public_uv sync --locked --dev --check
public_uv --no-config run --frozen pytest -q
public_uv --no-config run --frozen ruff check .
public_uv --no-config run --frozen ruff format --check .
public_uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
public_uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
git diff --check
~~~

Build exactly one temporary archive pair, validate it, then use isolated wheel
environments rather than checkout imports:

~~~bash
tmp_build="$(mktemp -d)"
public_uv --no-config build --out-dir "$tmp_build"
public_uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"
wheel="$(find "$tmp_build" -maxdepth 1 -name '*.whl' -print -quit)"
tmp_env="$(mktemp -d)"
public_uv venv "$tmp_env/venv"
public_uv pip install --python "$tmp_env/venv/bin/python" "$wheel"
tmp_run="$(mktemp -d)"
env -u PYTHONPATH "$tmp_env/venv/bin/fashion-radar" --help
env -u PYTHONPATH "$tmp_env/venv/bin/python" -m fashion_radar --help
env -u PYTHONPATH "$tmp_env/venv/bin/fashion-radar" init --config-dir "$tmp_run/config" --data-dir "$tmp_run/data" --reports-dir "$tmp_run/reports"
env -u PYTHONPATH "$tmp_env/venv/bin/fashion-radar" doctor --config-dir "$tmp_run/config" --data-dir "$tmp_run/data" --reports-dir "$tmp_run/reports"
env -u PYTHONPATH "$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
env -u PYTHONPATH "$tmp_env/venv/bin/python" -c "from importlib import resources; text = resources.files('fashion_radar.templates').joinpath('daily_report.md').read_text(encoding='utf-8'); assert 'Fashion Radar Daily Report' in text"
tmp_dash="$(mktemp -d)"
public_uv venv "$tmp_dash/venv"
public_uv pip install --python "$tmp_dash/venv/bin/python" "$wheel[dashboard]"
env -u PYTHONPATH "$tmp_dash/venv/bin/python" -c "import fashion_radar.dashboard.app; import fashion_radar.dashboard.queries"
~~~

- [ ] **Step 6: Obtain, record, and verify the release review.**

Ask Claude Code for a release review using the same max-effort, read-only
command contract. Give it the committed SHA, complete Step 5 validation
outcomes, archive checks, and exact scope. If Claude Code is unavailable, use
OpenCode with zhipuai-coding-plan/glm-5.2 max and save the matching fallback
record. Save the concise credential-free result to the applicable release-review
path with one coherent body and no raw tool output, live-capture stub, empty
result, duplicated verdict, timeout text, credential, token, or URL with
credentials.

Resolve every critical or important finding. If the review causes any diff,
rerun the full Step 5 suite from the changed stable snapshot, then obtain and
record the corresponding release rereview before continuing. When the release
review is clean, stage its record and rerun git diff --cached --check, release
hygiene, the staged `uv.lock` no-drift guard from Step 4, and the full Step 5
verification suite on that exact staged snapshot.
Commit the record as Stage 389: record release review and capture the final
HEAD SHA.

- [ ] **Step 7: Revalidate the final committed snapshot.**

Repeat the complete Step 5 public lock scan, sync checks, test suite, Ruff,
release hygiene, first-run smoke, archive, installed-wheel CLI init/doctor,
installed first-run, package-resource, and dashboard-extra checks from the
final committed HEAD. This second pass covers the release-review record and
proves the exact SHA selected for publication.

- [ ] **Step 8: Verify the authorized remote and publish one committed SHA.**

The user has given an ongoing instruction to publish completed stages to the
already selected origin. Before publication, prove the final worktree has no
staged, unstaged, or untracked content and inspect ignored paths for only
expected local tooling such as the ignored CodeGraph index. Then compare the
origin URL in a shell variable against only the user-authorized
Lordakee/fashion-radar HTTPS or SSH target. Do not echo the URL, print
credentials, use embedded credentials, alter persistent Git auth, or use shell
tracing. Abort if any condition does not match:

~~~bash
origin_url="$(git remote get-url origin)"
git status --short
git status --ignored --short
test -z "$(git status --porcelain=v1)"
case "$origin_url" in
  https://github.com/Lordakee/fashion-radar.git|git@github.com:Lordakee/fashion-radar.git) ;;
  *) echo "origin is not the authorized Fashion Radar remote" >&2; exit 1 ;;
esac
unset origin_url
release_head="$(git rev-parse HEAD)"
remote_before="$(git ls-remote --exit-code origin refs/heads/main | awk '{print $1}')"
git merge-base --is-ancestor "$remote_before" "$release_head"
git push origin "$release_head:refs/heads/main"
remote_after="$(git ls-remote --exit-code origin refs/heads/main | awk '{print $1}')"
test "$remote_after" = "$release_head"
~~~

Do not publish packages or uploads beyond the authorized GitHub branch push.

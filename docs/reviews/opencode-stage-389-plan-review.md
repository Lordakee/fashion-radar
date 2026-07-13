# OpenCode Stage 389 Plan Revision Review

## Verdict

CHANGES REQUIRED

## Confirmed Architecture

The selected architecture matches the current codebase: retention failure is
currently swallowed after artifact output; the installer already has the
canonical three payloads; the schedule preview is legacy; and ops-check only
tests file existence today. The revised plan must preserve the strict
filename-only boundary: unit_files_present plus filenames_only, with
site_ready_scheduler_unverified as the sole healthy top-level result. It must
not parse directives, add configured or invalid states, inspect drop-ins, or
call systemctl/loginctl.

## Required Plan Revisions

1. Declare Tasks 2, 3, and 4 a coupled sequential write set because all touch
   cli.py and test_row_one_cli.py. Task 4 must follow Task 3 GREEN because it
   imports ROW_ONE_SYSTEMD_UNITS from scheduling.py.
2. Add Task 0: preserve the primary Claude plan review, this OpenCode revision,
   and an accepted Claude plan rereview before implementation begins.
3. Strengthen filename-only tests with a direct _systemd_payload call whose
   content-read APIs fail, exact per-file missing units maps and remediation
   action, and both unknown-over-missing and unknown-with-all-present cases.
4. Pin human renderer substrings for filenames_only and scheduler state is not
   verified. Explain that the Task 3 scheduling import test can initially fail
   at collection before the new constant exists.
5. Stage every plan-review artifact. Keep code and release reviews tied to fresh
   verification, require rereviews after review-driven diffs, and apply the same
   single-body capture hygiene to all records.
6. Include CI-equivalent public-lock scanning, installed wheel init, doctor,
   packaged-resource, and dashboard-extra checks. Verify a clean final worktree
   before the guarded non-forced push.

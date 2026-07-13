# Claude Code Stage 389 Plan Review

## Verdict

CHANGES REQUIRED

## Scope Confirmed

The reviewed design and plan keep ops-check filename-only: they do not parse
systemd directives, claim a configured state, or call systemctl/loginctl. The
planned retention exit, canonical three-unit preview, archive coverage, and
committed-SHA push verification are technically sound.

## Required Changes

1. Record Task 3 and Task 4 as a coupled sequential write set. Both modify
   src/fashion_radar/cli.py and tests/test_row_one_cli.py, and Task 4 imports
   ROW_ONE_SYSTEMD_UNITS created by Task 3. Task 4 must start only after Task 3
   is integrated and its focused tests pass.
2. Add an explicit pre-implementation review-record task. It must save this
   primary review, the OpenCode plan revision, and the accepted Claude rereview
   with one coherent body each before any runtime work starts.

## Incorporated Strengthening

The plan revision will also pin exact human renderer substrings, explain the
possible ImportError in Task 3 RED, require the full release suite again after
the staged release-review record, directly prove the filename-only helper does
not read unit-file content, preserve unknown-over-missing precedence, and
assert each single-missing and all-missing units map plus its exact remediation
action.

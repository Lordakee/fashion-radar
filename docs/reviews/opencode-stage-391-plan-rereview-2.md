# Stage 391 Readiness Plan Revision

OpenCode reviewed the Claude Code Stage 391 plan rereview and applied its one
Important clarification and three Nits to the approved plan and design.

## Changes

- The `_cleanup_after_handled_failure` pseudocode now explains that its first
  canonical-journal read is only a missing-journal guard; the complete preflight
  deliberately performs a second read and equality check.
- Task 3 now cross-references the early mutation-free canonical-journal RED
  tests with the Step 4 extraction that turns them green.
- The design states in both prose and the staged-render sequence that live-root
  metadata application is a no-op for first publish.
- Valid owner-present/no-backup recovery is explicitly accepted regardless of
  how the state arose when the complete live site and remaining ownership state
  validate.
- The fixed helper table now places `_is_owned_live` in Task 3 Step 4, where the
  commit and rollback helpers first require it.

## Independent Check

The mutation-free canonical preflight boundary, live owner binding, six-part
capability detector, metadata timing, and published/no-backup recovery matrix
remain consistent. No production code, test, dependency, schema, source, or
public behavior was changed by this revision.

## Verdict

APPROVED

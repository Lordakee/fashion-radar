# OpenCode Stage 390 Plan Rereview 3

## Verdict

APPROVED - the amendments add fail-closed staged-snapshot guards and a
mirror-scan diagnostic that close the release-safety gap without changing
product scope, fixed interfaces, or classification behavior.

## Findings

### Critical

No findings.

### Important

No findings.

### Minor

No findings.

## Assessment

Before the implementation commit, the plan now requires no unstaged changes or
nonignored untracked paths, then checks the cached diff, `uv.lock`, and release
hygiene. This ensures the immutable implementation SHA contains the complete
reviewed snapshot and no incidental artifact.

The mirror scan continues to treat exit status one as the expected no-match
case. Any other status now emits a diagnostic and aborts the fail-fast release
subshell, distinguishing an unreadable scan from a clean public lockfile.

Before the release-record commit, the same worktree and untracked-path guards
run before cached-diff and lockfile checks. This complements the existing final
path allowlist and prevents unreviewed implementation changes from entering the
record-only commit. All inserted shell blocks pass `bash -n`; no product code,
runtime interface, probe, GDELT, network, dependency, or lockfile content
changes are involved.

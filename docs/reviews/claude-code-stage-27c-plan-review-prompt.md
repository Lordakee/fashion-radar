You are reviewing the Stage 27C release-verification plan before implementation.

Repository: `/home/ubuntu/fashion-radar`

Plan and design:

- `docs/superpowers/specs/2026-06-13-stage-27c-release-verification-design.md`
- `docs/superpowers/plans/2026-06-13-stage-27c-release-verification-plan.md`

Context:

- Stage 27A implemented `fashion-radar community-candidates` and was approved in
  `docs/reviews/claude-code-stage-27a-code-review.md`.
- Stage 27B documented `community-candidates` and was approved in
  `docs/reviews/claude-code-stage-27b-docs-review.md`.
- The active worktree has a known pre-existing `uv.lock` mirror diff. Stage 27C
  must not stage or commit it.
- The existing remote is `https://github.com/Lordakee/fashion-radar.git` and
  must remain token-free.
- A GitHub token may be used only ephemerally for push. It must not be written
  to files, git config, remote URLs, docs, logs, or committed artifacts.

Review focus:

1. Does the plan include adequate full verification before commit?
2. Does it use the Tsinghua PyPI mirror for install/build operations where
   practical while keeping `uv.lock` checked against default PyPI?
3. Does it verify Stage 27B boundary language and output-exclusion docs?
4. Does it include installed-wheel smoke for `community-candidates`, including
   recursive output-exclusion assertions and a no-generated-artifacts check?
5. Does it include secret/artifact scans before final review and again after
   final review files exist but before staging?
6. Does it require final Claude Code review before commit/push?
7. Does explicit staging include all intended Stage 27 code, tests, docs, plan,
   and review files?
8. Does explicit staging exclude `uv.lock` and generated artifacts?
9. Does the push strategy give a concrete non-persistent command and verify no
   token-bearing remote URL or persisted GitHub extraheader remains afterward?
10. Does post-push verification re-scan the committed tree for tracked secrets
    and generated artifacts?
11. Are there any Critical or Important gaps that should block implementation?

Output format:

- List findings by severity: Critical, Important, Minor.
- Critical and Important findings block implementation and must be fixed before
  release verification.
- If no blocking findings remain, include the exact phrase:
  `APPROVED FOR STAGE 27C RELEASE VERIFICATION`.

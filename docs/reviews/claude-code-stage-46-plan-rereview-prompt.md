# Claude Code Stage 46 Plan Rereview Prompt

You are rereviewing the revised Stage 46 repo release hygiene gate plan for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Previous Important Findings To Verify

The first review identified these blockers:

1. CI would likely fail because `actions/checkout` persisted a GitHub auth
   extraheader by default.
2. The implementation plan included push/GitHub Actions polling without making
   clear that this is a user-authorized node completion process, not product
   functionality.
3. Token scanning needed length-aware, high-confidence regexes so prefix
   examples like `ghp_` in docs/tests do not self-fail.
4. Local credential/config filenames were not consistently covered across
   tracked-path, high-risk untracked-path, and archive policies.

## Revised Files To Review

- `docs/superpowers/specs/2026-06-15-stage-46-repo-release-hygiene-gate-design.md`
- `docs/superpowers/plans/2026-06-15-stage-46-repo-release-hygiene-gate-plan.md`
- `docs/reviews/claude-code-stage-46-plan-review-prompt.md`

## Specific Questions

1. Do the revised spec and plan resolve all previous Important blockers?
2. Is the CI checkout credential behavior now addressed with
   `persist-credentials: false`?
3. Is the commit/push/CI confirmation step now clearly a user-authorized node
   completion step rather than release hygiene functionality?
4. Is token scanning now specified as length-aware and high-confidence enough
   to avoid self-failing on docs/tests?
5. Are `.pypirc`, `pip.conf`, `pip.ini`, `uv.toml`, `.netrc`, and `.npmrc`
   covered consistently enough for implementation?
6. Are there any remaining Critical or Important issues that must be fixed
   before implementation?

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the revised plan is acceptable to execute, include this exact
phrase:

```text
APPROVED FOR STAGE 46 REPO RELEASE HYGIENE GATE
```


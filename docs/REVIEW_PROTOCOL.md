# Review Protocol

This project follows a review-gated workflow.

## Before Coding

1. Write the objective, architecture, technical stack, implementation method, and staged plan.
2. Ask local Claude Code with `--effort max` to review the plan.
3. Record the review in `docs/reviews/`.
4. Fix critical and important planning issues.
5. Start implementation only after the plan is acceptable.

Use this command form for plan reviews:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "review prompt..."
```

## During Development

Each implementation stage must end with:

1. Fresh tests and lint checks.
2. Local Claude Code review of newly added code.
3. Fixes for critical and important findings.
4. Local Claude Code review of the next-stage plan.

## Before GitHub Upload

Before pushing to GitHub:

1. Run the full test suite.
2. Run linting.
3. Run lockfile, package build, installed-wheel, packaged-resource, and optional
   dashboard extra smoke checks.
4. Check for secrets, cookies, tokens, private data, generated reports, local
   SQLite databases, SQLite sidecars, build artifacts, and CodeGraph DB files.
5. Ask local Claude Code with `--effort max` for final code and documentation review.
6. Fix critical and important findings.
7. Let the user create or choose the GitHub remote.

Use the same local Claude Code command form for release reviews:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "review prompt..."
```

## Review Record Naming

Use this convention:

```text
docs/reviews/claude-code-stage-N-plan-review.md
docs/reviews/claude-code-stage-N-release-review.md
```

For follow-up reviews after fixes:

```text
docs/reviews/claude-code-stage-N-plan-rereview.md
docs/reviews/claude-code-stage-N-release-rereview.md
```

Older `opencode-*` records under `docs/reviews/` are historical audit records
and do not need rewriting.

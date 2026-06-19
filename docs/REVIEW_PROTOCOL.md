# Review Protocol

This project follows a review-gated workflow. The active local review engine is
opencode with `zhipuai-coding-plan/glm-5.2 --variant max`.

## Before Coding

1. Write the objective, architecture, technical stack, implementation method, and staged plan.
2. Ask local opencode with `zhipuai-coding-plan/glm-5.2 --variant max` to review the plan.
3. Record the review in `docs/reviews/`.
4. Fix critical and important planning issues.
5. Start implementation only after the plan is acceptable.

Use this command form for plan reviews:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-N-plan-review-prompt.md)" > docs/reviews/opencode-stage-N-plan-review.md
```

## During Development

Each implementation stage must end with:

1. Fresh tests and lint checks.
2. Local opencode review of newly added code
   (`docs/reviews/opencode-stage-N-code-review.md`).
3. Fixes for critical and important findings.
4. Local opencode review of the next-stage plan.

## Before GitHub Upload

Before pushing to GitHub:

1. Run the full test suite.
2. Run linting.
3. Run lockfile, package build, installed-wheel, packaged-resource, and optional
   dashboard extra smoke checks.
4. Check for secrets, cookies, tokens, private data, generated reports, local
   SQLite databases, SQLite sidecars, build artifacts, and CodeGraph DB files.
5. Ask local opencode with `zhipuai-coding-plan/glm-5.2 --variant max` for final
   code and documentation review.
6. Fix critical and important findings.
7. Let the user create or choose the GitHub remote.

Use the same local opencode command form for release reviews:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-N-release-review-prompt.md)" > docs/reviews/opencode-stage-N-release-review.md
```

## Review Record Naming

Use this convention for active local opencode reviews:

```text
docs/reviews/opencode-stage-N-plan-review.md
docs/reviews/opencode-stage-N-code-review.md
docs/reviews/opencode-stage-N-release-review.md
```

For follow-up reviews after fixes:

```text
docs/reviews/opencode-stage-N-plan-rereview.md
docs/reviews/opencode-stage-N-code-rereview.md
docs/reviews/opencode-stage-N-release-rereview.md
```

Keep existing review records in place; do not rename old artifacts just because
the active review engine changes.

## Optional Alternate Route

Claude Code is an optional alternate route only when a stage explicitly requests
it. In that case, use `--effort max`, read-only plan mode, no session
persistence, and the `claude-code-stage-N-...` review artifact prefix.

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "review prompt..."
```

Use this convention for optional Claude Code reviews:

```text
docs/reviews/claude-code-stage-N-plan-review.md
docs/reviews/claude-code-stage-N-code-review.md
docs/reviews/claude-code-stage-N-release-review.md
docs/reviews/claude-code-stage-N-plan-rereview.md
docs/reviews/claude-code-stage-N-code-rereview.md
docs/reviews/claude-code-stage-N-release-rereview.md
```

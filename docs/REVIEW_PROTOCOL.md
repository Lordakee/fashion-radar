# Review Protocol

This project follows a review-gated workflow.

## Before Coding

1. Write the objective, architecture, technical stack, implementation method, and staged plan.
2. Ask local opencode with GLM 5.2 to review the plan.
3. Record the review in `docs/reviews/`.
4. Fix critical and important planning issues.
5. Start implementation only after the plan is acceptable.

Use this command form for plan reviews:

```bash
opencode run -m zhipuai-coding-plan/glm-5.2 "review prompt..."
```

`zhipuai-coding-plan/glm-5.2` is the local opencode model ID for GLM 5.2.

## During Development

Each implementation stage must end with:

1. Fresh tests and lint checks.
2. Local opencode review of newly added code.
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
5. Ask local opencode with GLM 5.2 for final code and documentation review.
6. Fix critical and important findings.
7. Let the user create or choose the GitHub remote.

Use the same local opencode command form for release reviews:

```bash
opencode run -m zhipuai-coding-plan/glm-5.2 "review prompt..."
```

## Review Record Naming

Use this convention:

```text
docs/reviews/opencode-stage-N-plan-review.md
docs/reviews/opencode-stage-N-release-review.md
```

For follow-up reviews after fixes:

```text
docs/reviews/opencode-stage-N-plan-rereview.md
docs/reviews/opencode-stage-N-release-rereview.md
```

Older `claude-code-*` records under `docs/reviews/` are historical audit records
and do not need rewriting.

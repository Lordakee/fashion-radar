# Review Protocol

This project follows a review-gated workflow.

## Before Coding

1. Write the objective, architecture, technical stack, implementation method, and staged plan.
2. Ask Claude Code to review the plan.
3. Record the review in `docs/reviews/`.
4. Fix critical and important planning issues.
5. Start implementation only after the plan is acceptable.

## During Development

Each implementation stage must end with:

1. Fresh tests and lint checks.
2. Claude Code review of newly added code.
3. Fixes for critical and important findings.
4. Claude Code review of the next-stage plan.

## Before GitHub Upload

Before pushing to GitHub:

1. Run the full test suite.
2. Run linting.
3. Check for secrets, cookies, tokens, private data, and large generated files.
4. Ask Claude Code for final code and documentation review.
5. Fix critical and important findings.
6. Let the user create or choose the GitHub remote.

## Review Record Naming

Use this convention:

```text
docs/reviews/YYYY-MM-DD-stage-N-claude-code-review.md
```

For the initial plan review:

```text
docs/reviews/claude-code-plan-review.md
```


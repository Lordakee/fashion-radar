# Review Protocol

This project follows a review-gated workflow. The active local review engine is
opencode with `zhipuai-coding-plan/glm-5.2 --variant max`.

## Before Coding

1. Write the objective, architecture, technical stack, implementation method, and staged plan.
2. Ask local opencode with `zhipuai-coding-plan/glm-5.2 --variant max` to review the plan.
3. Record the review in `docs/reviews/`.
4. Fix critical and important planning issues.
5. Start implementation only after the plan is acceptable.

Each new stage plan should state which core product gap it closes in the
collect -> match -> report pipeline.

Use this command form for plan reviews:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-N-plan-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-N-plan-review.md
rm -f "$tmp_review"
```

## During Development

Each implementation stage must end with:

1. Fresh tests and lint checks.
2. Local opencode review of newly added code
   (`docs/reviews/opencode-stage-N-code-review.md`).
3. Fixes for critical and important findings.
4. Local opencode review of the next-stage plan.

For the current v0.1.x release track, stage proposals should prioritize source
coverage/health, matching quality, and optional summary work over new
external/community handoff surface area. Changes to `external-tool-*`,
`community-handoff-*`, or `imported-*` commands should be treated as frozen
unless they fix a release-blocking defect or a correctness issue in existing
behavior.

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
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-N-release-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-N-release-review.md
rm -f "$tmp_review"
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

## Review Capture Hygiene

This review capture hygiene rule applies to
`docs/reviews/opencode-stage-N-plan-review.md`,
`docs/reviews/opencode-stage-N-code-review.md`, and
`docs/reviews/opencode-stage-N-release-review.md`, as well as non-stage local
opencode review records under `docs/reviews/` such as full-project reviews.
Capture the completed reviewer output to a temporary file first, inspect it, and
then copy only one coherent review body directly into the target review record.

Do not commit live-capture stubs, duplicated or truncated text, empty output,
multiple top-level review drafts, or more than one verdict. Do not commit tool
status lines such as `Wrote`, and do not duplicate approval phrases. If the
review times out, record the timeout honestly in a separate scratch location and
retry with a narrower prompt; committed review artifacts must not be timeout
stubs or partial output presented as approval.

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

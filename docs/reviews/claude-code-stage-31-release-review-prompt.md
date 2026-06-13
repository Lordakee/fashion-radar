# Claude Code Stage 31 Release Review Prompt

You are reviewing the completed Stage 31 release-gate node for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- Do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Decide whether the Stage 31 documentation/process changes and verification
evidence are ready to commit and push.

## Changed / New Files To Review

- `docs/release-gate-stage31.md`
- `docs/github-upload-checklist.md`
- `docs/superpowers/specs/2026-06-13-stage-31-release-gate-design.md`
- `docs/superpowers/plans/2026-06-13-stage-31-release-gate-plan.md`
- `docs/reviews/claude-code-stage-31-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-31-plan-review.md`
- `docs/reviews/claude-code-stage-31-plan-rereview.md`
- `docs/reviews/claude-code-stage-31-plan-rereview-2-prompt.md`
- `docs/reviews/claude-code-stage-31-plan-rereview-2.md`
- `docs/reviews/claude-code-stage-31-plan-rereview-3-prompt.md`
- `docs/reviews/claude-code-stage-31-plan-rereview-3.md`
- `docs/reviews/claude-code-stage-31-plan-rereview-4-prompt.md`
- `docs/reviews/claude-code-stage-31-plan-rereview-4.md`
- `docs/reviews/claude-code-stage-31-plan-rereview-5-prompt.md`
- `docs/reviews/claude-code-stage-31-plan-rereview-5.md`
- `docs/reviews/claude-code-stage-31-plan-rereview-6-prompt.md`
- `docs/reviews/claude-code-stage-31-plan-rereview-6.md`
- `docs/reviews/claude-code-stage-31-plan-rereview-7-prompt.md`
- `docs/reviews/claude-code-stage-31-plan-rereview-7.md`
- `docs/reviews/claude-code-stage-31-plan-rereview-8-prompt.md`
- `docs/reviews/claude-code-stage-31-plan-rereview-8.md`

## Verification Evidence

Passed:

- `git status --short --branch` and
  `git status --short --branch --untracked-files=all`
- `git log --oneline -5`
- `git status --short -- uv.lock`
- `git diff -- uv.lock`
- `git diff --numstat -- uv.lock`
- `git diff -- uv.lock > /tmp/fashion-radar-stage31-uv-lock-before.diff`
- `.venv/bin/python` `uv.lock` mirror-rewrite guard
- `git restore uv.lock`
- `git diff --cached -- uv.lock`
- mirror URL scan of `uv.lock`
- `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check`
- `UV_NO_CONFIG=1 uv lock --check`
- `UV_NO_CONFIG=1 uv sync --locked --dev --check`
- `.venv/bin/python -m pytest -q` with `572 passed`
- `.venv/bin/python -m ruff check .`
- `.venv/bin/python -m ruff format --check .`
- `git diff --check`
- `git diff --cached --check`
- `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv build --out-dir /tmp/fashion-radar-dist-stage31`
- installed-wheel top-level help and all public command `--help` smokes
- installed-wheel `community-handoff-workflow` JSON smoke, including
  step names/effects, command prefixes, `--dry-run` placement, and no supplied
  missing/config/data directory creation
- installed-wheel `community-handoff-workflow` table smoke with
  `Commands were not executed.`
- wheel/sdist package content assertions
- source/entity pack lint smokes
- CSV and JSON community signal lint/candidate-preview/directory-preview smokes
  using temp config copied from `configs/scoring.example.yaml`
- CSV and JSON `import-signals --dry-run` smokes with no temp data files
  created
- boundary scans: broad historical scan saved under `/tmp`, public-surface scan
  saved under `/tmp`, unstaged/cached diff-scoped boundary scans had zero
  matches
- secret/artifact scan: token-free remote URL, no persistent extraheader,
  clean unstaged/staged `uv.lock`, no actual secret-looking values, no tracked
  generated artifacts beyond allowed `data/README.md` and `reports/README.md`,
  and only `.codegraph/.gitignore` tracked under `.codegraph`
- `git diff --check -- docs/release-gate-stage31.md docs/github-upload-checklist.md docs/superpowers/specs/2026-06-13-stage-31-release-gate-design.md docs/superpowers/plans/2026-06-13-stage-31-release-gate-plan.md docs/reviews/claude-code-stage-31-*.md`

Execution-time findings were handled and rereviewed:

- User-level uv config sets the Tsinghua mirror as default. The release gate now
  uses `UV_NO_CONFIG=1` for public lockfile checks and keeps mirror-backed sync
  checks separate.
- Public example candidate preview requires a runtime `scoring.yaml`; the smoke
  now copies `configs/scoring.example.yaml` to `/tmp/.../scoring.yaml`.
- Single-file `import-signals` uses `--format`, not `--input-format`.
- Secret scan was narrowed to actual secret-looking values instead of bare
  variable names/placeholders.
- Artifact scan allows only `data/README.md` and `reports/README.md` under
  those directories.

## Review Questions

1. Do the Stage 31 docs and review artifacts accurately reflect the performed
   release gate?
2. Are the verification commands and execution-time corrections technically
   sound?
3. Is `uv.lock` protected from mirror persistence and excluded from staging?
4. Do the changes avoid runtime feature creep and avoid positive claims about
   scraping, crawling, platform automation, source acquisition, source ranking,
   demand proof, watchers, schedulers, or platform connectors?
5. Are secret/artifact checks and push hygiene sufficient for commit and push?
6. Is it acceptable to commit and push these Stage 31 files using one-shot git
   auth, given the user explicitly authorized pushing in this thread?

## Required Output

Respond with:

- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A concise verdict.

If and only if this is ready to commit and push, include this exact phrase:

```text
APPROVED FOR STAGE 31 COMMIT AND PUSH
```

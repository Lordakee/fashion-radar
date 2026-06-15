# Claude Code Stage 41 Release Review Prompt

You are reviewing the Stage 41 CLI docs readiness implementation for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a release review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Stage 41 refreshes public documentation so current CLI commands, path flags, and
release smoke checks are consistent, easy to audit, and ready for GitHub users.

## Implementation Summary

- Added `docs/cli-reference.md` as a compact map of the current public
  `fashion-radar` command surface and shared path options.
- Linked `docs/cli-reference.md` from README and removed the README current-docs
  link to historical `docs/release-gate-stage31.md`.
- Updated README, manual import, community import, community signal quality,
  architecture, source-pack, trend, dashboard, and data-retention examples so
  repo-local flows consistently carry `--config-dir`, `--data-dir`, and
  `--reports-dir` where relevant.
- Added current `--imported-at`, `--host`, `--port`, `--strict`, and
  `clean-old-data --data-dir` examples where the Stage 41 plan required them.
- Updated `docs/github-upload-checklist.md` so installed-wheel smoke includes a
  full help loop for the current 27 public commands.
- Extended the same path-consistency cleanup to candidate discovery, daily
  digest, scheduling, and entity-pack examples found during pre-release audit.
- Updated final review docs back to Claude Code with `--effort max` after the
  user's temporary opencode rule was canceled.
- Deleted superseded untracked `opencode-stage-41-*` attempt artifacts from the
  working tree; Claude Code plan review/rereview artifacts are the authoritative
  Stage 41 review records.

## Files To Review

- `README.md`
- `docs/cli-reference.md`
- `docs/manual-signal-import.md`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `docs/architecture.md`
- `docs/source-packs.md`
- `docs/trend-deltas.md`
- `docs/dashboard.md`
- `docs/data-retention.md`
- `docs/candidate-discovery.md`
- `docs/daily-digest.md`
- `docs/scheduling.md`
- `docs/entity-packs.md`
- `docs/github-upload-checklist.md`
- `docs/superpowers/specs/2026-06-15-stage-41-cli-docs-readiness-design.md`
- `docs/superpowers/plans/2026-06-15-stage-41-cli-docs-readiness-plan.md`
- `docs/reviews/claude-code-stage-41-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-41-plan-review.md`
- `docs/reviews/claude-code-stage-41-plan-rereview-prompt.md`
- `docs/reviews/claude-code-stage-41-plan-rereview.md`
- `docs/reviews/claude-code-stage-41-plan-rereview-2-prompt.md`
- `docs/reviews/claude-code-stage-41-plan-rereview-2.md`

## Verification Already Run

Documentation checks:

```bash
rg -n "docs/cli-reference.md|CLI Reference|Command Reference" README.md docs/cli-reference.md
rg -n "import-signals .*--data-dir|import-signals-dir .*--data-dir|--imported-at" README.md docs/manual-signal-import.md docs/community-signal-import.md docs/community-signal-quality.md docs/architecture.md
rg -n "trends .*--data-dir|match .*--data-dir" docs/trend-deltas.md README.md docs/architecture.md docs/manual-signal-import.md docs/community-signal-import.md docs/community-signal-quality.md
rg -n "dashboard .*--host|dashboard .*--port|clean-old-data .*--data-dir|source-pack-lint .*--strict" README.md docs/dashboard.md docs/data-retention.md docs/source-packs.md
if rg -qn "release-gate-stage31" README.md; then exit 1; fi
if rg -n "fashion-radar (match|report|candidates|trends) " docs/manual-signal-import.md docs/community-signal-import.md docs/community-signal-quality.md docs/architecture.md | rg -v -- "--data-dir"; then exit 1; fi
if rg -n "fashion-radar (match|report|candidates|trends) " docs/manual-signal-import.md docs/community-signal-import.md docs/community-signal-quality.md docs/architecture.md | rg -v -- "--config-dir"; then exit 1; fi
if rg -n "fashion-radar (match|report|candidates|trends) " README.md | rg -v -- "--help" | rg -v -- "--data-dir"; then exit 1; fi
if rg -n "fashion-radar (match|report|candidates|trends) " README.md | rg -v -- "--help" | rg -v -- "--config-dir"; then exit 1; fi
scoped_docs=(README.md docs/cli-reference.md docs/manual-signal-import.md docs/community-signal-import.md docs/community-signal-quality.md docs/architecture.md docs/source-packs.md docs/trend-deltas.md docs/dashboard.md docs/data-retention.md docs/candidate-discovery.md docs/daily-digest.md docs/scheduling.md docs/entity-packs.md docs/github-upload-checklist.md)
if rg -n "fashion-radar (report|candidates|trends|run) [^\\\\]*$" "${scoped_docs[@]}" | rg -v -- "--as-of|--help"; then exit 1; fi
rg -n -C 3 "fashion-radar (report|candidates|trends|run)( |$| \\\\)" "${scoped_docs[@]}"
rg -n "claude-code-stage-41" docs/reviews/claude-code-stage-41-*.md
git diff --check
```

CLI and dependency checks:

```bash
UV_NO_CONFIG=1 _TYPER_FORCE_DISABLE_TERMINAL=1 uv run fashion-radar --help
for cmd in init migrate-db doctor source-pack-lint entity-pack-lint community-signal-lint community-signal-lint-dir community-candidates community-candidates-dir community-handoff-workflow import-signals import-signals-dir imported-signals imported-signals-summary imported-entity-deltas imported-candidates imported-candidate-evidence imported-review-workflow collect match report candidates trends schedule-example dashboard clean-old-data run; do
  UV_NO_CONFIG=1 _TYPER_FORCE_DISABLE_TERMINAL=1 uv run fashion-radar "$cmd" --help
done
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
git diff --cached --check
git diff --quiet -- uv.lock
```

All commands above exited successfully.

## Review Questions

1. Does this implementation satisfy the approved Stage 41 plan?
2. Is `docs/cli-reference.md` accurate enough for the current Typer CLI command
   surface without copying full help pages?
3. Are repo-local examples path-consistent enough that imports into `$PWD/data`
   are reviewed, matched, reported, trended, and cleaned from the same local
   workspace?
4. Does the GitHub upload checklist now cover the current public command help
   surface while preserving existing runtime smoke checks?
5. Did this stage remain documentation-only, without source code, tests,
   dependencies, `uv.lock`, CI, schema, scraping/crawling/platform automation,
   source acquisition, schedulers, watchers, monitors, or external services?

## Required Output

Respond with:

- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A concise verdict.

If and only if this implementation is acceptable to commit and push, include
this exact phrase:

```text
APPROVED FOR STAGE 41 COMMIT AND PUSH
```

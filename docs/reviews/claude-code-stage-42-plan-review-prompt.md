# Claude Code Stage 42 Plan Review Prompt

You are reviewing the Stage 42 CLI docs drift guards plan for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Add pytest guards that keep Stage 41 CLI docs and upload checklist coverage in
sync with the actual public Typer command surface.

## Proposed Technical Approach

- Create `tests/test_cli_docs.py`.
- Derive public CLI command names dynamically from `typer.main.get_command(app)`.
- Assert `docs/cli-reference.md` lists every public command.
- Assert the installed-wheel help loop in `docs/github-upload-checklist.md`
  covers exactly the current public commands.
- Assert README links `docs/cli-reference.md` and does not present historical
  `docs/release-gate-stage31.md` as current docs.
- Parse selected Markdown bash blocks and assert repo-local operational command
  examples keep `--config-dir`, `--data-dir`, `--reports-dir`, and `--as-of`
  flags together where needed.
- Keep this test-focused node out of runtime behavior, source acquisition,
  scraping/crawling/platform automation, schedulers, watchers, monitors,
  external services, package metadata, lockfiles, and CI workflow behavior.

## Files To Review

- `docs/superpowers/specs/2026-06-15-stage-42-cli-docs-drift-guards-design.md`
- `docs/superpowers/plans/2026-06-15-stage-42-cli-docs-drift-guards-plan.md`

## Required Output

Respond with:

- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A concise verdict.

If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 42 CLI DOCS DRIFT GUARDS
```

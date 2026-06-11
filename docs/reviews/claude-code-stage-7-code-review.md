# Claude Code Stage 7 Code Review

Command:

```bash
claude -p --effort max --permission-mode bypassPermissions < docs/reviews/claude-code-stage-7-code-review-prompt-short.md
```

Result:

```text
Approved after fixes
```

## Critical

None.

## Important

1. `$HOME` in the cron `PATH` line is not expanded by cron.

The generated cron snippet used:

```text
PATH=/usr/local/bin:/usr/bin:/bin:$HOME/.local/bin:$HOME/.cargo/bin
```

In crontab environment assignments, `$HOME` remains literal. If `uv` is only in
the user's local path, cron may fail to find it.

Recommended fix:

- Keep the crontab-level `PATH` to system locations, or remove misleading
  `$HOME` entries.
- Prepend user-local paths inside the command where bash expands `$HOME`, for
  example:

```bash
PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH" uv run fashion-radar run
```

## Minor

- `--time` semantics differ by scheduler mode: cron/systemd use local time,
  GitHub Actions uses UTC. This was already documented.
- GitHub Actions snippets require real config files rather than only
  `*.example.yaml`; this was already documented.
- Unquoted cron paths can break if paths contain spaces.
- `validate_hhmm` validation is redundant but harmless.

## Follow-Up

The cron `PATH` issue was fixed by moving user-local path expansion into the
runtime command. Cron path quoting was also tightened, and systemd environment
assignments were updated after an additional subagent review found that
space-containing paths could otherwise be split in `Environment=`.

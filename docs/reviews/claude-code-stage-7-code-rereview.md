# Claude Code Stage 7 Code Rereview

Command:

```bash
claude -p --effort max --permission-mode bypassPermissions < docs/reviews/claude-code-stage-7-code-rereview-prompt-short.md
```

## Stage 7 Code Re-review

Base `eb52d36`, uncommitted working tree, effort max.

### What Claude Code Verified Independently

- **Cron `PATH` blocker resolved.** The crontab-level line is now static system
  paths only (`PATH=/usr/local/bin:/usr/bin:/bin`), and user-local paths are
  prepended at shell runtime via
  `PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH" uv run ...`. Claude Code
  reproduced the minimal-shell lookup behavior and confirmed bash applies the
  assignment before command lookup.
- **systemd with spaces.** Claude Code rendered the service and timer with
  `/opt/Fashion Radar/...` and ran `systemd-analyze verify`; it exited 0, with
  only an unrelated pre-existing system unit warning.
- **`%` escaping per context** is correct: `\%` for cron, `%%` for systemd, raw
  `%` for GitHub Actions.
- **Cron path quoting and systemd environment quoting** are correct for the
  generated snippets.
- **Source pack scope** loads through `load_source_config`: 10 sources, type set
  exactly `{rss, gdelt}`, and all RSS entries have `article.enabled: false`.
- **Focused tests and lint** passed for the scheduling and CLI files.

## Critical

None.

## Important

None. The prior cron `$HOME`-in-`PATH` issue is correctly fixed and empirically
confirmed.

## Minor

1. uv discovery is asymmetric: cron explicitly prepends user-local bins, systemd
   relies on `bash -lc` sourcing the profile. A user whose profile does not add
   `~/.local/bin` could see systemd fail where cron would not. Worth a one-line
   note in `docs/scheduling.md`.
2. No log-rotation guidance for the cron log path.
3. `_systemd_path` escapes only `%`, not `"`, an extreme edge case outside
   documented usage.

Follow-up: items 1 and 2 were addressed in `docs/scheduling.md` after this
review by documenting systemd `uv` path requirements and cron log rotation or
cleanup guidance.

## Answers

1. **Satisfies plan?** Yes: print-only scheduling, public RSS/GDELT pack, no new
   collectors.
2. **Examples correct/safe?** Yes: verified via cron lookup behavior and
   `systemd-analyze verify`; GitHub workflow has no secrets and nothing
   auto-installs.
3. **Scope preserved?** Yes: `rss`/`gdelt` only, article extraction off, no
   forbidden source types.
4. **Tests/docs sufficient?** Yes.
5. **Blockers?** None.

```text
Approved for Stage 7 commit and next-stage planning
```

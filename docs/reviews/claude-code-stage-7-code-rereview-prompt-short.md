# Claude Code Stage 7 Code Rereview Prompt Short

Review `/home/ubuntu/fashion-radar` Stage 7 before commit.

Use `--effort max`.

Base: `eb52d36`
Range: uncommitted working tree.

Approved Stage 7 scope:

- Print-only daily scheduling examples.
- Public RSS/GDELT source pack.
- No new collectors and no social/platform scraping.

Previous code review:

- `docs/reviews/claude-code-stage-7-code-review.md`
- Result was `Approved after fixes`.
- Important issue was cron `$HOME` inside crontab-level `PATH`.

Fixes now applied:

- `src/fashion_radar/scheduling.py`
  - Cron crontab-level path is now only:
    `PATH=/usr/local/bin:/usr/bin:/bin`
  - Cron command now prepends user-local uv paths at shell runtime:
    `PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH" uv run ...`
  - Cron paths are shell-quoted.
  - systemd `Environment=` values quote the whole assignment so paths with
    spaces are not split.
  - systemd `WorkingDirectory=` remains unquoted because
    `systemd-analyze verify` rejects double-quoted path values there.
- `tests/test_scheduling.py`
  - Covers cron `%` escaping, exact crontab `PATH` line, cron path quoting,
    systemd timer, systemd env quoting with spaces, GitHub Actions raw `%`.
- `tests/test_cli.py`
  - Covers cron, systemd, GitHub Actions, and invalid time CLI branches.
- `docs/scheduling.md`
  - Documents scheduler timezones, `%` escaping, cron PATH behavior, and
    systemd `Environment=` quoting.

Public source pack:

- `configs/source-packs/fashion-public.example.yaml`
- Uses only `rss` and `gdelt`.
- RSS article extraction defaults disabled.

Out of scope still excluded:

- No Google News RSS, Google Trends, Reddit, static webpage monitoring,
  Playwright, login cookies, account/session files, browser profiles, proxy
  pools, CAPTCHA bypass, paywall bypass, fingerprint evasion, private data, or
  social scraping.

Fresh verification:

```text
Focused schedule/CLI tests: 27 passed
pytest: 132 passed
ruff check: clean
ruff format --check: 58 files already formatted
uv lock --check: OK
uv sync --locked --dev --check: no changes
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check: no changes
uv build: wheel/sdist OK
installed wheel schedule-example smoke: OK
daily_report.md resource smoke: OK
dashboard import smoke: OK
source pack YAML parse: 10 sources, ['gdelt', 'rss']
root packaged sources template sync: OK
systemd-analyze verify generated service/timer with spaces: OK
git diff --check: clean
uv.lock mirror URL scan: clean
CodeGraph status: indexed and available
```

Please inspect the diff and answer:

1. Does Stage 7 satisfy the approved plan?
2. Are the scheduler examples correct and safe enough?
3. Is source-boundary scope preserved?
4. Are tests/docs sufficient?
5. Any blockers before commit?

Return findings by severity:

- Critical
- Important
- Minor

End with exactly one of:

- Approved for Stage 7 commit and next-stage planning
- Approved after fixes
- Do not proceed

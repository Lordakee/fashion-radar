# Claude Code Stage 7 Code Rereview Prompt

Review Fashion Radar Stage 7 after fixes.

Repo: `/home/ubuntu/fashion-radar`
Base: `eb52d36`
Range: uncommitted working tree.

User rules:

- This review must use `--effort max`.
- Stage 7 plan was approved in
  `docs/reviews/claude-code-stage-7-plan-rereview.md`.
- Previous Stage 7 code review result was recorded in
  `docs/reviews/claude-code-stage-7-code-review.md` as `Approved after fixes`.

Stage 7 approved scope:

- Add print-only scheduling examples.
- Add public RSS/GDELT source pack.
- No new collectors or social/platform scraping.

Key files:

- `src/fashion_radar/scheduling.py`
- `src/fashion_radar/cli.py`
- `tests/test_scheduling.py`
- `tests/test_cli.py`
- `tests/test_config.py`
- `configs/source-packs/fashion-public.example.yaml`
- `configs/sources.example.yaml`
- `src/fashion_radar/templates/configs/sources.example.yaml`
- `docs/scheduling.md`
- `docs/source-packs.md`
- `README.md`
- `docs/source-boundaries.md`

Implemented:

- `fashion-radar schedule-example --mode cron|systemd|github-actions`
- Print-only snippets; no scheduler mutation.
- Scheduler timestamp helpers:
  - raw `%` for GitHub Actions
  - `\%` for cron
  - `%%` for systemd
- Cron output keeps the crontab-level `PATH` to system paths only:
  `PATH=/usr/local/bin:/usr/bin:/bin`
- Cron command prepends user-local `uv` paths at runtime:
  `PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH" uv run ...`
- Cron paths are shell-quoted where needed.
- systemd `Environment=` assignments quote the whole assignment so values with
  spaces are not split.
- systemd `WorkingDirectory=` remains a scalar path value; local
  `systemd-analyze verify` rejected double-quoted `WorkingDirectory` paths but
  accepted the current form.
- Docs/snippets state cron/systemd local timezone and GitHub Actions UTC.
- Source pack uses only `rss` and `gdelt`, with RSS article extraction disabled.
- Default starter source changed from dead Vogue Business URL to Fashionista RSS.

Out of scope preserved:

- No new source type or collector.
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
mirror frozen sync check: no changes
wheel/sdist build: OK
installed wheel schedule-example smoke: OK
daily_report.md resource smoke: OK
dashboard extra import smoke: OK
source pack YAML parse: 10 sources, ['gdelt', 'rss']
root packaged sources template sync: OK
systemd-analyze verify on generated service/timer with spaces: OK
git diff --check: clean
uv.lock mirror URL scan: clean
CodeGraph status: indexed and available
```

Questions:

1. Does the implementation satisfy the approved Stage 7 plan?
2. Are scheduler snippets correct and safe after the cron PATH and systemd fixes?
3. Is source-boundary scope preserved?
4. Are tests/docs sufficient?
5. Any blockers before commit?

Return findings by severity:

- Critical
- Important
- Minor

End with one of:

- Approved for Stage 7 commit and next-stage planning
- Approved after fixes
- Do not proceed

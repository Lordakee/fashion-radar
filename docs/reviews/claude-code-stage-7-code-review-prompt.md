# Claude Code Stage 7 Code Review Prompt

You are Claude Code reviewing Fashion Radar after Stage 7 implementation and
before commit.

Repository: `/home/ubuntu/fashion-radar`

Base:

- `eb52d36 docs: record agent reasoning settings`

Reviewed range:

- Uncommitted Stage 7 working tree.

User/project rules:

- Codex subagents use reasoning effort `xhigh`.
- Claude Code reviews use `--effort max`.
- Stage plan was reviewed and approved in:
  - `docs/reviews/claude-code-stage-7-plan-review.md`
  - `docs/reviews/claude-code-stage-7-plan-rereview.md`

Stage 7 goal:

- Add safe daily scheduling examples and a public fashion RSS/GDELT source pack.
- Do not add new collectors or risky scraping.

Implemented files:

- `src/fashion_radar/scheduling.py`
- `src/fashion_radar/cli.py`
- `tests/test_scheduling.py`
- `tests/test_cli.py`
- `tests/test_config.py`
- `tests/test_stage1_hardening.py`
- `configs/source-packs/fashion-public.example.yaml`
- `configs/sources.example.yaml`
- `src/fashion_radar/templates/configs/sources.example.yaml`
- `docs/scheduling.md`
- `docs/source-packs.md`
- `README.md`
- `docs/source-boundaries.md`
- `CHANGELOG.md`
- Stage 7 design/plan/review docs under `docs/superpowers/` and `docs/reviews/`

Implementation summary:

- Added pure scheduling renderer helpers:
  - `raw_as_of_shell()`
  - `cron_as_of_shell()`
  - `systemd_as_of_shell()`
  - `render_cron_example()`
  - `render_systemd_service()`
  - `render_systemd_timer()`
  - `render_github_actions_workflow()`
- Added `fashion-radar schedule-example` with modes:
  - `cron`
  - `systemd`
  - `github-actions`
- The command prints snippets only. It does not modify crontab, systemd,
  launchd, Windows Task Scheduler, GitHub settings, or secrets.
- Fixed scheduler `%` escaping:
  - cron uses `\%`
  - systemd uses `%%`
  - GitHub Actions uses raw `%`
- Cron snippet includes a conservative `PATH`.
- Snippets/docs state timezone semantics:
  - cron/systemd use local machine time
  - GitHub Actions schedule uses UTC
- Added `configs/source-packs/fashion-public.example.yaml` with six RSS sources
  and four GDELT queries. RSS article extraction is disabled by default.
- Changed the default starter RSS source from the dead
  `https://www.voguebusiness.com/feed` URL to
  `https://fashionista.com/.rss/excerpt`.
- Root and packaged starter source templates remain synchronized.

Explicit out of scope:

- No new source type.
- No new collector.
- No Google News RSS.
- No Google Trends.
- No Reddit.
- No static webpage monitoring.
- No Playwright/browser automation.
- No Instagram/TikTok/X/Xiaohongshu/RedNote scraping.
- No login cookies, account/session files, browser profiles, proxy pools,
  CAPTCHA bypass, paywall bypass, fingerprint evasion, private data collection,
  or high-frequency crawling.
- No daemon, Celery/Redis worker, background service, or parallel collector
  runner.

Fresh verification:

```text
.venv/bin/python -m pytest -q
130 passed in 3.68s

.venv/bin/python -m ruff check .
All checks passed!

.venv/bin/python -m ruff format --check .
58 files already formatted

uv lock --check
Resolved 84 packages

uv sync --locked --dev --check
Would make no changes

UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
Would make no changes

uv build --out-dir /tmp/fashion-radar-dist-stage7
Successfully built wheel and sdist

Installed wheel via Tsinghua mirror:
fashion-radar schedule-example --mode cron --project-dir /tmp/fashion-radar worked
importlib.resources loaded daily_report.md

Dashboard extra smoke via Tsinghua mirror:
import fashion_radar.dashboard.app and fashion_radar.dashboard.queries worked

YAML/source template sync:
configs/source-packs/fashion-public.example.yaml parses
configs/sources.example.yaml == src/fashion_radar/templates/configs/sources.example.yaml

CodeGraph:
sync complete and index up to date
```

Subagent read-only review:

- No Critical or Important findings.
- Minor systemd CLI branch coverage gap was fixed by adding
  `test_schedule_example_prints_systemd_snippet`.

Please review:

1. Does Stage 7 implementation satisfy the approved plan?
2. Are scheduler snippets correct and safe, especially cron/systemd `%`
   escaping, PATH, timezone comments, and print-only behavior?
3. Is the source pack safe and honest, using only existing `rss`/`gdelt` source
   types and no live-network tests?
4. Are source boundaries preserved?
5. Are tests and docs sufficient?
6. Are there issues to fix before commit?

Return findings ordered by severity:

- Critical
- Important
- Minor

End with one of:

- Approved for Stage 7 commit and next-stage planning
- Approved after fixes
- Do not proceed

# Claude Code Stage 7 Plan Review Prompt

You are Claude Code reviewing Fashion Radar before Stage 7 implementation.

Repository: `/home/ubuntu/fashion-radar`

Current local head:

- `eb52d36 docs: record agent reasoning settings`

Remote note:

- Git smart HTTP was hanging from this environment.
- `AGENTS.md` was updated on GitHub via the Contents API and verified remotely.
- Local working tree now has only Stage 7 planning docs and the Stage 7 re-scope
  in the main implementation plan.

User workflow rules:

- Plan before implementation.
- Submit goal, scheme, tech stack, implementation method, and plan to Claude
  Code before coding.
- After each development node, submit new code and the next-stage plan to
  Claude Code before continuing.
- Codex subagents must use reasoning effort `xhigh`.
- Claude Code reviews must use `--effort max`.

Stage 7 goal:

- Make Fashion Radar practical for daily unattended use.
- Add safe scheduling examples and a public fashion source starter pack.
- Do not add new collectors or risky scraping.

Active design and implementation plan:

- `docs/superpowers/specs/2026-06-12-stage-7-daily-operations-design.md`
- `docs/superpowers/plans/2026-06-12-stage-7-daily-operations-plan.md`

Recommended architecture:

- Add pure Python scheduling renderers in `src/fashion_radar/scheduling.py`.
- Add a Typer CLI command:
  - `fashion-radar schedule-example --mode cron`
  - `fashion-radar schedule-example --mode systemd`
  - `fashion-radar schedule-example --mode github-actions`
- The command prints snippets only. It must not edit crontab, systemd, launchd,
  Windows Task Scheduler, GitHub settings, or repository secrets.
- Add `configs/source-packs/fashion-public.example.yaml` using only existing
  source types: `rss`, `rsshub`, and `gdelt`.
- Update default `sources.example.yaml` away from the currently dead
  `https://www.voguebusiness.com/feed` URL.
- Add docs:
  - `docs/scheduling.md`
  - `docs/source-packs.md`
- Update README, source-boundary docs, and CHANGELOG.

Tech stack:

- Python 3.11+
- Typer
- Pydantic config validation
- PyYAML
- pytest
- ruff
- uv
- Existing SQLite/RSS/GDELT/report/dashboard stack

Implementation method:

- TDD.
- No live-network CI tests.
- Source-pack YAML must validate through existing `load_source_config()`.
- Root and packaged starter config templates must remain synchronized.
- Full verification before code review:
  - `pytest`
  - `ruff check`
  - `ruff format --check`
  - `uv lock --check`
  - locked sync check
  - mirror frozen sync check
  - wheel/package smoke
  - dashboard extra smoke
  - CodeGraph sync/status

Explicit out of scope:

- No Instagram/TikTok/X/Xiaohongshu/RedNote scraping.
- No Google News RSS.
- No Google Trends.
- No Reddit.
- No static webpage collector.
- No Playwright/browser automation.
- No login cookies, account/session files, browser profiles, proxy pools,
  CAPTCHA bypass, paywall bypass, fingerprint evasion, private data collection,
  or high-frequency crawling.
- No daemon, Celery/Redis worker, background service, or parallel collector
  runner.

Please review:

1. Is the Stage 7 goal safe and useful?
2. Is the proposed architecture compatible with the existing CLI/config/test
   patterns?
3. Is the schedule-example command appropriately scoped to print-only snippets?
4. Is the public-source pack safe, honest, and testable without live-network
   CI?
5. Are source boundaries preserved?
6. Are the tests and verification plan sufficient?
7. Are there issues to fix before implementation?

Return findings ordered by severity:

- Critical
- Important
- Minor

End with one of:

- Approved for Stage 7 implementation
- Approved after fixes
- Do not proceed

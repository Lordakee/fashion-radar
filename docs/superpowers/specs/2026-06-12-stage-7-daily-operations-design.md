# Stage 7 Daily Operations Design

## Goal

Make Fashion Radar practical for daily use by adding scheduling guidance, a
safe schedule-snippet CLI, and a richer public-source starter pack.

## Problem

The v0.1.0 MVP can collect, match, score, report, and show a local dashboard,
but a new user still has to answer two operational questions:

1. How do I run this every day?
2. Which free public fashion sources should I start with?

The next stage should solve those questions without introducing a long-running
daemon, cloud service, social scraping, login cookies, proxy pools, CAPTCHA
bypass, paywall bypass, or private data collection.

## Recommended Approach

Add a small pure-rendering scheduling module and CLI command that prints safe
examples instead of mutating the user's crontab or systemd configuration.

Add a repository source pack with validated public RSS endpoints and GDELT
queries. Keep the source pack as an example config file, not an automatic source
subscription. Users still choose what to enable and remain responsible for
source terms.

## Scope

Included:

- `fashion-radar schedule-example` command.
- Pure functions that render cron, systemd user timer/service, and GitHub
  Actions snippets.
- `docs/scheduling.md` with daily operating guidance.
- `configs/source-packs/fashion-public.example.yaml`.
- `docs/source-packs.md` explaining the source pack and verification.
- Update default `configs/sources.example.yaml` and packaged starter template
  away from the dead Vogue Business URL.
- Tests for schedule rendering, CLI output, source-pack YAML parsing, and root
  vs packaged starter config synchronization.

Excluded:

- No background scheduler daemon.
- No mutation of crontab, systemd, launchd, Windows Task Scheduler, or GitHub
  repository settings.
- No notifications.
- No Google News RSS.
- No Google Trends, Reddit, Instagram, TikTok, X/Twitter, Xiaohongshu/RedNote,
  Pinterest, Playwright, login-cookie flows, account/session files, proxy pools,
  CAPTCHA bypass, paywall bypass, or high-frequency crawling.

## Source Pack

Candidate RSS sources verified by direct HTTP checks on 2026-06-12:

- `https://fashionista.com/.rss/excerpt`
- `https://fashionweekdaily.com/feed`
- `https://fashionunited.info/rss-news`
- `https://www.theindustry.fashion/feed`
- `https://www.highsnobiety.com/feed/`
- `https://wwd.com/feed/rss`

Observed but not used as the default starter URL:

- `https://www.voguebusiness.com/feed` returned 404 during the Stage 7 planning
  check and should be removed from the default starter config unless a working
  official feed URL is found later.

The pack should also include GDELT queries for:

- luxury/designer fashion
- celebrity style/red carpet
- bags/shoes/products
- emerging designers

Article extraction should be disabled by default in the source pack to avoid
unnecessary page fetching. Users can opt into article extraction per source.

## Architecture

### Scheduling

Create `src/fashion_radar/scheduling.py` with pure render functions:

- `validate_hhmm(value: str) -> str`
- `raw_as_of_shell() -> str`
- `cron_as_of_shell() -> str`
- `systemd_as_of_shell() -> str`
- `render_cron_example(...) -> str`
- `render_systemd_service(...) -> str`
- `render_systemd_timer(...) -> str`
- `render_github_actions_workflow(...) -> str`

The functions return strings only. They do not read or write user scheduler
state.

Timestamp escaping is mode-specific:

- cron command fields require `%` as `\%`
- systemd unit files require `%` as `%%`
- GitHub Actions shell commands can use raw `%`

The cron snippet should include a conservative `PATH` line because cron often
runs with a minimal environment where `uv` is not found.

Add CLI command:

```text
fashion-radar schedule-example --mode cron
fashion-radar schedule-example --mode systemd
fashion-radar schedule-example --mode github-actions
```

Options:

- `--mode`: `cron`, `systemd`, or `github-actions`
- `--project-dir`: working directory for the scheduled command
- `--config-dir`
- `--data-dir`
- `--reports-dir`
- `--time`: `HH:MM`, default `08:00`

The command prints instructions and snippets. It does not install them.

Docs and snippets must state that cron/systemd times are interpreted in the
machine's local timezone, while GitHub Actions scheduled workflows use UTC.
The generated `--as-of` timestamp is evaluated at run time in UTC and is used as
both the collection timestamp and report window timestamp.

### Source Packs

Create:

```text
configs/source-packs/fashion-public.example.yaml
docs/source-packs.md
```

The source-pack YAML must validate with the existing `SourceConfig` model.

Update:

```text
configs/sources.example.yaml
src/fashion_radar/templates/configs/sources.example.yaml
```

The root starter config and packaged starter template must remain byte-identical.

## Testing

- Unit tests for schedule renderers.
- CLI tests for `schedule-example` mode output and invalid `--time`.
- Config tests that load the source pack through `load_source_config()`.
- Config tests that root and packaged starter source templates are identical.
- Full existing test suite, ruff, format, lock checks, mirror sync check, build,
  installed resource smoke, and dashboard extra smoke.

## Documentation

Update:

- `README.md`: link scheduling/source-pack docs and show the schedule command.
- `docs/source-boundaries.md`: clarify source packs are examples, not
  endorsements or automatic subscriptions.
- `CHANGELOG.md`: add Stage 7 entries.

Add:

- `docs/scheduling.md`
- `docs/source-packs.md`

## Review Gates

1. Submit this design and the Stage 7 implementation plan to Claude Code with
   `--effort max`.
2. Fix Critical and Important plan findings before implementation.
3. After implementation, run fresh verification.
4. Submit Stage 7 code/docs to Claude Code with `--effort max`.
5. Fix Critical and Important code findings.
6. Commit and sync to GitHub.

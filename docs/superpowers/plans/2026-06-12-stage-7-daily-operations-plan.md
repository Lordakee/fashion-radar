# Stage 7 Daily Operations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Add safe daily scheduling examples and a richer public fashion source starter pack without adding risky connectors.

**Architecture:** Use a pure Python scheduling renderer module plus a Typer CLI command that prints snippets but never mutates user scheduler state. Add source-pack YAML examples that validate with existing config models and keep the default packaged starter config synchronized with the root starter config.

**Tech Stack:** Python 3.11+, Typer, Pydantic config validation, PyYAML, pytest, ruff, uv, SQLite workflow already implemented in earlier stages.

---

## Scope Guard

Stage 7 must not implement or document operational recipes for Instagram,
TikTok, X/Twitter, Xiaohongshu/RedNote, Google News RSS, Google Trends, Reddit,
Pinterest, Playwright scraping, login cookies, account/session files, proxy
pools, CAPTCHA bypass, paywall bypass, or private data collection.

The scheduling command must print examples only. It must not edit crontabs,
systemd units, launchd plists, Windows Task Scheduler entries, GitHub Actions
settings, or repository secrets.

## Files

- Create: `src/fashion_radar/scheduling.py`
- Modify: `src/fashion_radar/cli.py`
- Create: `tests/test_scheduling.py`
- Modify: `tests/test_cli.py`
- Modify: `tests/test_config.py`
- Modify: `tests/test_stage1_hardening.py`
- Create: `configs/source-packs/fashion-public.example.yaml`
- Modify: `configs/sources.example.yaml`
- Modify: `src/fashion_radar/templates/configs/sources.example.yaml`
- Create: `docs/scheduling.md`
- Create: `docs/source-packs.md`
- Modify: `README.md`
- Modify: `docs/source-boundaries.md`
- Modify: `CHANGELOG.md`
- Create: `docs/reviews/claude-code-stage-7-plan-review-prompt.md`
- Create after review: `docs/reviews/claude-code-stage-7-plan-review.md`
- Create after implementation: `docs/reviews/claude-code-stage-7-code-review-prompt.md`
- Create after implementation review: `docs/reviews/claude-code-stage-7-code-review.md`

## Task 1: Claude Code Plan Gate

- [x] Create `docs/reviews/claude-code-stage-7-plan-review-prompt.md` with the Stage 7 goal, architecture, tech stack, implementation method, source pack list, scheduling CLI behavior, tests, and explicit out-of-scope boundaries.
- [x] Run:

```bash
claude -p --effort max --permission-mode bypassPermissions < docs/reviews/claude-code-stage-7-plan-review-prompt.md
```

- [x] Save the review to `docs/reviews/claude-code-stage-7-plan-review.md`.
- [x] Fix any Critical or Important findings before Task 2.

## Task 2: Scheduling Renderer Tests

- [x] Add `tests/test_scheduling.py` with these tests:

```python
import pytest

from fashion_radar.scheduling import (
    cron_as_of_shell,
    render_cron_example,
    render_github_actions_workflow,
    render_systemd_service,
    render_systemd_timer,
    raw_as_of_shell,
    systemd_as_of_shell,
    validate_hhmm,
)


def test_validate_hhmm_accepts_24_hour_time() -> None:
    assert validate_hhmm("08:30") == "08:30"
    assert validate_hhmm("23:59") == "23:59"


@pytest.mark.parametrize("value", ["8:30", "24:00", "12:60", "aa:bb"])
def test_validate_hhmm_rejects_invalid_time(value: str) -> None:
    with pytest.raises(ValueError, match="HH:MM"):
        validate_hhmm(value)


def test_as_of_shell_is_escaped_per_scheduler_context() -> None:
    assert raw_as_of_shell() == '$(date -u +%Y-%m-%dT%H:%M:%SZ)'
    assert cron_as_of_shell() == '$(date -u +\\%Y-\\%m-\\%dT\\%H:\\%M:\\%SZ)'
    assert systemd_as_of_shell() == '$(date -u +%%Y-%%m-%%dT%%H:%%M:%%SZ)'


def test_render_cron_example_contains_run_command_and_paths() -> None:
    text = render_cron_example(
        project_dir="/opt/fashion-radar",
        config_dir="/opt/fashion-radar/configs",
        data_dir="/opt/fashion-radar/data",
        reports_dir="/opt/fashion-radar/reports",
        time="08:30",
    )
    assert "30 8 * * *" in text
    assert "PATH=" in text
    assert "uv run fashion-radar run" in text
    assert "FASHION_RADAR_CONFIG_DIR=/opt/fashion-radar/configs" in text
    assert "$(date -u +\\%Y-\\%m-\\%dT\\%H:\\%M:\\%SZ)" in text


def test_render_systemd_timer_contains_on_calendar() -> None:
    timer = render_systemd_timer(time="08:30")
    assert "OnCalendar=*-*-* 08:30:00" in timer
    assert "Persistent=true" in timer


def test_render_systemd_service_contains_environment_and_run_command() -> None:
    service = render_systemd_service(
        project_dir="/opt/fashion-radar",
        config_dir="/opt/fashion-radar/configs",
        data_dir="/opt/fashion-radar/data",
        reports_dir="/opt/fashion-radar/reports",
    )
    assert "WorkingDirectory=/opt/fashion-radar" in service
    assert "Environment=FASHION_RADAR_DATA_DIR=/opt/fashion-radar/data" in service
    assert "ExecStart=/usr/bin/env bash -lc" in service
    assert "uv run fashion-radar run" in service
    assert "$(date -u +%%Y-%%m-%%dT%%H:%%M:%%SZ)" in service


def test_render_github_actions_workflow_contains_schedule_and_no_secrets() -> None:
    workflow = render_github_actions_workflow(time="08:30")
    assert "cron: '30 8 * * *'" in workflow
    assert "uv run fashion-radar run" in workflow
    assert "$(date -u +%Y-%m-%dT%H:%M:%SZ)" in workflow
    assert "secrets." not in workflow
```

- [x] Run:

```bash
.venv/bin/python -m pytest tests/test_scheduling.py -q
```

Expected: fails because `fashion_radar.scheduling` does not exist yet.

## Task 3: Scheduling Renderer Implementation

- [x] Create `src/fashion_radar/scheduling.py`:

```python
from __future__ import annotations

import re
from dataclasses import dataclass

HHMM_PATTERN = re.compile(r"^(?P<hour>[01][0-9]|2[0-3]):(?P<minute>[0-5][0-9])$")


@dataclass(frozen=True)
class SchedulePaths:
    project_dir: str
    config_dir: str
    data_dir: str
    reports_dir: str


def validate_hhmm(value: str) -> str:
    if HHMM_PATTERN.fullmatch(value) is None:
        raise ValueError("time must be in 24-hour HH:MM format")
    return value


def raw_as_of_shell() -> str:
    return "$(date -u +%Y-%m-%dT%H:%M:%SZ)"


def cron_as_of_shell() -> str:
    return raw_as_of_shell().replace("%", r"\%")


def systemd_as_of_shell() -> str:
    return raw_as_of_shell().replace("%", "%%")


def _cron_parts(time: str) -> tuple[str, str]:
    valid = validate_hhmm(time)
    hour, minute = valid.split(":", 1)
    return minute, str(int(hour))


def render_cron_example(
    *,
    project_dir: str,
    config_dir: str,
    data_dir: str,
    reports_dir: str,
    time: str,
) -> str:
    minute, hour = _cron_parts(time)
    return f"""# Add with `crontab -e` after reviewing paths.
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin:$HOME/.local/bin:$HOME/.cargo/bin
FASHION_RADAR_CONFIG_DIR={config_dir}
FASHION_RADAR_DATA_DIR={data_dir}
FASHION_RADAR_REPORTS_DIR={reports_dir}

# cron uses the machine's local timezone.
{minute} {hour} * * * cd {project_dir} && uv run fashion-radar run --as-of "{cron_as_of_shell()}" >> {reports_dir}/fashion-radar-cron.log 2>&1
"""


def render_systemd_service(
    *,
    project_dir: str,
    config_dir: str,
    data_dir: str,
    reports_dir: str,
) -> str:
    return f"""[Unit]
Description=Fashion Radar daily run

[Service]
Type=oneshot
WorkingDirectory={project_dir}
Environment=FASHION_RADAR_CONFIG_DIR={config_dir}
Environment=FASHION_RADAR_DATA_DIR={data_dir}
Environment=FASHION_RADAR_REPORTS_DIR={reports_dir}
ExecStart=/usr/bin/env bash -lc 'uv run fashion-radar run --as-of "{systemd_as_of_shell()}"'
"""


def render_systemd_timer(*, time: str) -> str:
    valid = validate_hhmm(time)
    return f"""[Unit]
Description=Run Fashion Radar daily

[Timer]
# systemd OnCalendar uses the machine's local timezone unless configured otherwise.
OnCalendar=*-*-* {valid}:00
Persistent=true

[Install]
WantedBy=timers.target
"""


def render_github_actions_workflow(*, time: str) -> str:
    minute, hour = _cron_parts(time)
    return f"""name: Fashion Radar Daily Run

on:
  workflow_dispatch:
  schedule:
    # GitHub Actions schedule times are UTC.
    - cron: '{minute} {hour} * * *'

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - name: Install dependencies
        run: uv sync --locked --dev
      - name: Run Fashion Radar
        run: uv run fashion-radar run --as-of "{raw_as_of_shell()}"
"""
```

- [x] Run:

```bash
.venv/bin/python -m pytest tests/test_scheduling.py -q
```

Expected: passes.

## Task 4: CLI `schedule-example`

- [x] Extend `tests/test_cli.py` with tests:

```python
def test_schedule_example_prints_cron_snippet(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        app,
        [
            "schedule-example",
            "--mode",
            "cron",
            "--project-dir",
            str(tmp_path),
            "--config-dir",
            str(tmp_path / "configs"),
            "--data-dir",
            str(tmp_path / "data"),
            "--reports-dir",
            str(tmp_path / "reports"),
            "--time",
            "08:30",
        ],
    )

    assert result.exit_code == 0
    assert "crontab -e" in result.output
    assert "uv run fashion-radar run" in result.output
    assert "30 8 * * *" in result.output


def test_schedule_example_rejects_invalid_time(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        app,
        [
            "schedule-example",
            "--mode",
            "cron",
            "--project-dir",
            str(tmp_path),
            "--time",
            "25:00",
        ],
    )

    assert result.exit_code == 1
    assert "HH:MM" in result.output
```

- [x] Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py::test_schedule_example_prints_cron_snippet tests/test_cli.py::test_schedule_example_rejects_invalid_time -q
```

Expected: fails because the command does not exist.

- [x] Modify `src/fashion_radar/cli.py`:

```python
from typing import Literal

from fashion_radar.scheduling import (
    render_cron_example,
    render_github_actions_workflow,
    render_systemd_service,
    render_systemd_timer,
    validate_hhmm,
)
```

Add command:

```python
@app.command(name="schedule-example")
def schedule_example(
    mode: Literal["cron", "systemd", "github-actions"] = typer.Option(
        "cron",
        help="Snippet type to print.",
    ),
    project_dir: Path = typer.Option(Path.cwd(), help="Project working directory."),
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    reports_dir: Path = REPORTS_DIR_OPTION,
    time: str = typer.Option("08:00", help="Daily run time in 24-hour HH:MM format."),
) -> None:
    """Print safe daily scheduling examples without installing them."""
    try:
        validate_hhmm(time)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc

    if mode == "cron":
        typer.echo(
            render_cron_example(
                project_dir=str(project_dir),
                config_dir=str(config_dir),
                data_dir=str(data_dir),
                reports_dir=str(reports_dir),
                time=time,
            )
        )
    elif mode == "systemd":
        typer.echo("# ~/.config/systemd/user/fashion-radar.service")
        typer.echo(
            render_systemd_service(
                project_dir=str(project_dir),
                config_dir=str(config_dir),
                data_dir=str(data_dir),
                reports_dir=str(reports_dir),
            )
        )
        typer.echo("# ~/.config/systemd/user/fashion-radar.timer")
        typer.echo(render_systemd_timer(time=time))
    else:
        typer.echo(render_github_actions_workflow(time=time))
```

- [x] Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py tests/test_scheduling.py -q
```

Expected: passes.

## Task 5: Public Source Pack

- [x] Create `configs/source-packs/fashion-public.example.yaml` with:

```yaml
# Example public source pack. Review source terms before enabling.
version: 1
sources:
  - name: Fashionista
    type: rss
    url: https://fashionista.com/.rss/excerpt
    enabled: true
    weight: 1.0
    tags: [fashion_media, industry_news]
    article:
      enabled: false
  - name: Fashion Week Daily
    type: rss
    url: https://fashionweekdaily.com/feed
    enabled: true
    weight: 0.9
    tags: [fashion_media, celebrity_style]
    article:
      enabled: false
  - name: FashionUnited
    type: rss
    url: https://fashionunited.info/rss-news
    enabled: true
    weight: 0.8
    tags: [industry_news, retail]
    article:
      enabled: false
  - name: The Industry Fashion
    type: rss
    url: https://www.theindustry.fashion/feed
    enabled: true
    weight: 0.9
    tags: [industry_news, brand_news]
    article:
      enabled: false
  - name: Highsnobiety
    type: rss
    url: https://www.highsnobiety.com/feed/
    enabled: true
    weight: 0.8
    tags: [streetwear, culture]
    article:
      enabled: false
  - name: WWD
    type: rss
    url: https://wwd.com/feed/rss
    enabled: true
    weight: 1.1
    tags: [trade_media, industry_news]
    article:
      enabled: false
  - name: GDELT Luxury Fashion
    type: gdelt
    query: '(luxury fashion OR designer fashion OR "fashion week")'
    enabled: true
    weight: 0.9
    tags: [gdelt, luxury, industry_news]
    gdelt:
      lookback_hours: 24
      max_records: 100
      rate_limit_per_second: 1.0
  - name: GDELT Celebrity Style
    type: gdelt
    query: '("celebrity style" OR "red carpet fashion" OR "red carpet look")'
    enabled: true
    weight: 0.8
    tags: [gdelt, celebrity_style]
    gdelt:
      lookback_hours: 24
      max_records: 100
      rate_limit_per_second: 1.0
  - name: GDELT Bags Shoes Products
    type: gdelt
    query: '("designer bag" OR handbag OR sneakers OR "ballet flats" OR loafer) (fashion OR luxury)'
    enabled: true
    weight: 0.8
    tags: [gdelt, products, accessories, shoes]
    gdelt:
      lookback_hours: 24
      max_records: 100
      rate_limit_per_second: 1.0
  - name: GDELT Emerging Designers
    type: gdelt
    query: '("emerging designer" OR "independent designer" OR "LVMH Prize" OR "ANDAM fashion")'
    enabled: true
    weight: 0.8
    tags: [gdelt, emerging_designers]
    gdelt:
      lookback_hours: 24
      max_records: 100
      rate_limit_per_second: 1.0
```

- [x] Replace the default root and packaged `sources.example.yaml` first RSS source with `Fashionista` and `https://fashionista.com/.rss/excerpt`, keeping root and packaged files byte-identical.
- [x] Update `tests/test_stage1_hardening.py` so the init-generated starter
  config assertion expects `Fashionista` instead of the old `Vogue Business RSS`
  source name.
- [x] Add tests to `tests/test_config.py`:

```python
from pathlib import Path

from fashion_radar.settings import load_source_config


def test_public_fashion_source_pack_loads() -> None:
    config = load_source_config(Path("configs/source-packs/fashion-public.example.yaml"))

    assert len(config.sources) >= 10
    assert {source.type.value for source in config.sources} == {"rss", "gdelt"}
    assert all(source.article.enabled is False for source in config.sources if source.type.value == "rss")


def test_root_and_packaged_sources_template_are_synchronized() -> None:
    root = Path("configs/sources.example.yaml").read_text(encoding="utf-8")
    packaged = Path("src/fashion_radar/templates/configs/sources.example.yaml").read_text(
        encoding="utf-8"
    )
    assert root == packaged
```

- [x] Run:

```bash
.venv/bin/python -m pytest tests/test_config.py -q
```

Expected: passes.

## Task 6: Scheduling And Source-Pack Docs

- [x] Create `docs/scheduling.md` covering:
  - recommended local cron usage
  - systemd user timer usage
  - GitHub Actions caveat that generated reports in Actions are ephemeral unless committed/uploaded by the user
  - GitHub Actions precondition that real `sources.yaml`, `entities.yaml`, and
    `scoring.yaml` files must exist in the checkout or be created by the user's
    workflow before `run`
  - timezone behavior: cron/systemd use local machine time, GitHub Actions schedule uses UTC
  - `%` escaping is handled by `schedule-example`, and manual scheduler snippets must keep those escapes
  - cron PATH caveat for finding `uv`
  - `run --as-of` uses a run-time UTC timestamp for both collection and report window time
  - dashboard is not required for scheduled runs
  - token/secrets warning
  - `fashion-radar schedule-example` command examples
- [x] Create `docs/source-packs.md` covering:
  - how to copy `configs/source-packs/fashion-public.example.yaml` into `sources.yaml`
  - source pack is an example, not endorsement
  - RSS endpoints were checked during planning but users should verify terms and availability
  - article extraction disabled by default
  - GDELT queries can be tuned
  - no social scraping included
- [x] Update `README.md` links and quickstart with:

```bash
uv run fashion-radar schedule-example --mode cron --project-dir "$PWD"
```

- [x] Update `docs/source-boundaries.md` to state source packs are examples and not automatic subscriptions.
- [x] Update `CHANGELOG.md` Stage 7 `Added` entries.

## Task 7: Verification And Claude Code Code Review

- [x] Run:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
uv lock --check
uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
```

- [x] Run package smoke:

```bash
rm -rf /tmp/fashion-radar-dist-stage7 /tmp/fashion-radar-wheel-smoke-stage7
uv build --out-dir /tmp/fashion-radar-dist-stage7
python3 -m venv /tmp/fashion-radar-wheel-smoke-stage7
/tmp/fashion-radar-wheel-smoke-stage7/bin/python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple /tmp/fashion-radar-dist-stage7/fashion_radar-0.1.0-py3-none-any.whl
/tmp/fashion-radar-wheel-smoke-stage7/bin/fashion-radar schedule-example --mode cron --project-dir /tmp/fashion-radar
/tmp/fashion-radar-wheel-smoke-stage7/bin/python -c "from importlib import resources; text = resources.files('fashion_radar.templates').joinpath('daily_report.md').read_text(encoding='utf-8'); assert 'Fashion Radar Daily Report' in text"
```

- [x] Run dashboard extra smoke:

```bash
python3 -m venv /tmp/fashion-radar-dashboard-smoke-stage7
/tmp/fashion-radar-dashboard-smoke-stage7/bin/python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple '/tmp/fashion-radar-dist-stage7/fashion_radar-0.1.0-py3-none-any.whl[dashboard]'
/tmp/fashion-radar-dashboard-smoke-stage7/bin/python -c "import fashion_radar.dashboard.app; import fashion_radar.dashboard.queries"
```

- [x] Sync CodeGraph:

```bash
codegraph sync /home/ubuntu/fashion-radar
codegraph status /home/ubuntu/fashion-radar
```

- [x] Create `docs/reviews/claude-code-stage-7-code-review-prompt.md` with implemented files, verification output, and Stage 8 plan suggestion.
- [x] Run:

```bash
claude -p --effort max --permission-mode bypassPermissions < docs/reviews/claude-code-stage-7-code-review-prompt.md
```

- [x] Save output to `docs/reviews/claude-code-stage-7-code-review.md`.
- [x] Fix all Critical and Important findings.
- [x] Commit with:

```bash
git add .
git commit -m "feat: add stage 7 daily operations"
```

- [ ] Sync to GitHub using normal git push if available. If Git smart HTTP still hangs but GitHub API works, use GitHub API only when it can preserve remote `main` safely and verify remote content afterward.

## Acceptance Criteria

- `fashion-radar schedule-example` prints cron, systemd, and GitHub Actions examples without installing anything.
- Invalid schedule times fail with a clear `HH:MM` error.
- Public source pack loads through the existing config model.
- Default starter source no longer uses the dead Vogue Business feed URL.
- Root and packaged starter source templates are synchronized.
- Scheduling and source-pack docs clearly state source boundaries and user responsibilities.
- Full tests, lint, format, lock checks, package smoke, dashboard extra smoke, and CodeGraph status pass.
- Claude Code review with `--effort max` has no unfixed Critical or Important findings.

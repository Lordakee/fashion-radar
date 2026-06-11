from __future__ import annotations

import re
import shlex
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


def _shell_quote(value: str) -> str:
    return shlex.quote(value)


def _systemd_quote_assignment(value: str) -> str:
    escaped = (
        value.replace("\\", "\\\\").replace('"', r"\"").replace("%", "%%").replace("\n", r"\n")
    )
    return f'"{escaped}"'


def _systemd_path(value: str) -> str:
    return value.replace("%", "%%")


def render_cron_example(
    *,
    project_dir: str,
    config_dir: str,
    data_dir: str,
    reports_dir: str,
    time: str,
) -> str:
    minute, hour = _cron_parts(time)
    log_path = f"{reports_dir}/fashion-radar-cron.log"
    command = (
        f"{minute} {hour} * * * cd {_shell_quote(project_dir)} && "
        f"FASHION_RADAR_CONFIG_DIR={_shell_quote(config_dir)} "
        f"FASHION_RADAR_DATA_DIR={_shell_quote(data_dir)} "
        f"FASHION_RADAR_REPORTS_DIR={_shell_quote(reports_dir)} "
        'PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH" '
        f'uv run fashion-radar run --as-of "{cron_as_of_shell()}" '
        f">> {_shell_quote(log_path)} 2>&1"
    )
    return f"""# Add with `crontab -e` after reviewing paths.
# cron uses the machine's local timezone.
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin

{command}
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
WorkingDirectory={_systemd_path(project_dir)}
Environment={_systemd_quote_assignment(f"FASHION_RADAR_CONFIG_DIR={config_dir}")}
Environment={_systemd_quote_assignment(f"FASHION_RADAR_DATA_DIR={data_dir}")}
Environment={_systemd_quote_assignment(f"FASHION_RADAR_REPORTS_DIR={reports_dir}")}
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

import shlex

import pytest

from fashion_radar.row_one.ops import render_row_one_local_ops_runbook
from fashion_radar.scheduling import (
    ROW_ONE_SYSTEMD_UNITS,
    cron_as_of_shell,
    raw_as_of_shell,
    render_cron_example,
    render_github_actions_workflow,
    render_row_one_cron_example,
    render_row_one_serve_systemd_service,
    render_row_one_systemd_service,
    render_systemd_service,
    render_systemd_timer,
    systemd_as_of_shell,
    validate_hhmm,
)


def _line_starting_with(text: str, prefix: str) -> str:
    return next(line for line in text.splitlines() if line.startswith(prefix))


def test_validate_hhmm_accepts_24_hour_time() -> None:
    assert validate_hhmm("08:30") == "08:30"
    assert validate_hhmm("23:59") == "23:59"


@pytest.mark.parametrize("value", ["8:30", "24:00", "12:60", "aa:bb"])
def test_validate_hhmm_rejects_invalid_time(value: str) -> None:
    with pytest.raises(ValueError, match="HH:MM"):
        validate_hhmm(value)


def test_as_of_shell_is_escaped_per_scheduler_context() -> None:
    assert raw_as_of_shell() == "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    assert cron_as_of_shell() == r"$(date -u +\%Y-\%m-\%dT\%H:\%M:\%SZ)"
    assert systemd_as_of_shell() == "$(date -u +%%Y-%%m-%%dT%%H:%%M:%%SZ)"


def test_row_one_systemd_unit_names_are_canonical_and_ordered() -> None:
    assert ROW_ONE_SYSTEMD_UNITS == (
        "row-one-refresh.service",
        "row-one-refresh.timer",
        "row-one-serve.service",
    )


def test_render_cron_example_contains_run_command_and_paths() -> None:
    text = render_cron_example(
        project_dir="/opt/fashion-radar",
        config_dir="/opt/fashion-radar/configs",
        data_dir="/opt/fashion-radar/data",
        reports_dir="/opt/fashion-radar/reports",
        time="08:30",
    )
    assert "30 8 * * *" in text
    assert "PATH=/usr/local/bin:/usr/bin:/bin\n" in text
    crontab_path_line = next(line for line in text.splitlines() if line.startswith("PATH="))
    assert crontab_path_line == "PATH=/usr/local/bin:/usr/bin:/bin"
    assert 'PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH" uv run' in text
    assert "uv run fashion-radar run" in text
    assert "FASHION_RADAR_CONFIG_DIR=/opt/fashion-radar/configs" in text
    assert r"$(date -u +\%Y-\%m-\%dT\%H:\%M:\%SZ)" in text
    assert "local timezone" in text


def test_render_cron_example_shell_quotes_paths_with_spaces() -> None:
    text = render_cron_example(
        project_dir="/opt/Fashion Radar",
        config_dir="/opt/Fashion Radar/configs",
        data_dir="/opt/Fashion Radar/data",
        reports_dir="/opt/Fashion Radar/reports",
        time="08:30",
    )
    assert "cd '/opt/Fashion Radar'" in text
    assert "FASHION_RADAR_CONFIG_DIR='/opt/Fashion Radar/configs'" in text
    assert ">> '/opt/Fashion Radar/reports/fashion-radar-cron.log' 2>&1" in text


def test_render_systemd_timer_contains_on_calendar() -> None:
    timer = render_systemd_timer(time="08:30")
    assert "OnCalendar=*-*-* 08:30:00" in timer
    assert "Persistent=true" in timer
    assert "local timezone" in timer


def test_render_systemd_service_contains_environment_and_run_command() -> None:
    service = render_systemd_service(
        project_dir="/opt/fashion-radar",
        config_dir="/opt/fashion-radar/configs",
        data_dir="/opt/fashion-radar/data",
        reports_dir="/opt/fashion-radar/reports",
    )
    assert "WorkingDirectory=/opt/fashion-radar" in service
    assert 'Environment="FASHION_RADAR_DATA_DIR=/opt/fashion-radar/data"' in service
    assert "ExecStart=/usr/bin/env bash -lc" in service
    assert "uv run fashion-radar run" in service
    assert "$(date -u +%%Y-%%m-%%dT%%H:%%M:%%SZ)" in service


def test_render_systemd_service_quotes_paths_with_spaces() -> None:
    service = render_systemd_service(
        project_dir="/opt/Fashion Radar",
        config_dir="/opt/Fashion Radar/configs",
        data_dir="/opt/Fashion Radar/data",
        reports_dir="/opt/Fashion Radar/reports",
    )
    assert "WorkingDirectory=/opt/Fashion Radar" in service
    assert 'Environment="FASHION_RADAR_CONFIG_DIR=/opt/Fashion Radar/configs"' in service
    assert 'Environment="FASHION_RADAR_REPORTS_DIR=/opt/Fashion Radar/reports"' in service


def test_render_row_one_cron_uses_one_timestamp_shared_env_and_grouped_log() -> None:
    text = render_row_one_cron_example(
        project_dir="/opt/fashion-radar",
        config_dir="/opt/fashion-radar/configs",
        data_dir="/opt/fashion-radar/data",
        reports_dir="/opt/fashion-radar/reports",
        output_dir="/opt/fashion-radar/reports/row-one/site",
        time="04:00",
    )

    assert "0 4 * * *" in text
    assert "ROW ONE scheduled refresh runs the single refresh command." in text
    assert text.count("date -u") == 1
    assert 'AS_OF="$(date -u +\\%Y-\\%m-\\%dT\\%H:\\%M:\\%SZ)"' in text
    assert 'uv run fashion-radar row-one refresh --as-of "$AS_OF"' in text
    assert "--output-dir /opt/fashion-radar/reports/row-one/site" in text
    assert "fashion-radar run" not in text
    assert "fashion-radar row-one build" not in text
    assert "export FASHION_RADAR_CONFIG_DIR=/opt/fashion-radar/configs" in text
    assert "FASHION_RADAR_DATA_DIR=/opt/fashion-radar/data" in text
    assert "FASHION_RADAR_REPORTS_DIR=/opt/fashion-radar/reports" in text
    assert '{ uv run fashion-radar row-one refresh --as-of "$AS_OF" ' in text
    assert "--latest-only" not in text
    assert (
        "--output-dir /opt/fashion-radar/reports/row-one/site; } >> "
        "/opt/fashion-radar/reports/row-one-cron.log 2>&1"
    ) in text


def test_render_row_one_cron_quotes_output_dir_with_spaces_and_single_quotes() -> None:
    text = render_row_one_cron_example(
        project_dir="/opt/Fashion Radar",
        config_dir="/opt/Fashion Radar/configs",
        data_dir="/opt/Fashion Radar/data",
        reports_dir="/opt/Fashion Radar/reports",
        output_dir="/tmp/ROW ONE's site",
        time="04:00",
    )

    assert "cd '/opt/Fashion Radar'" in text
    assert "--output-dir '/tmp/ROW ONE'\"'\"'s site'" in text
    assert ">> '/opt/Fashion Radar/reports/row-one-cron.log' 2>&1" in text


def test_render_row_one_local_ops_runbook_prints_refresh_serve_and_cron() -> None:
    output = render_row_one_local_ops_runbook(
        project_dir="/repo",
        config_dir="/repo/configs",
        data_dir="/repo/data",
        reports_dir="/repo/reports",
        output_dir="/repo/reports/row-one/site",
        time="04:00",
        host="0.0.0.0",
        port=8787,
    )

    assert "ROW ONE local daily ops" in output
    assert 'AS_OF="$(date -u +%Y-%m-%dT%H:%M:%SZ)"' in output
    assert "fashion-radar row-one refresh" in output
    assert "Source checkout commands:" in output
    source_checkout_block = output.split("Source checkout commands:", maxsplit=1)[1].split(
        "Access:", maxsplit=1
    )[0]
    assert 'AS_OF="$(date -u +%Y-%m-%dT%H:%M:%SZ)"' in source_checkout_block
    assert "cd /repo" in output
    assert "uv run fashion-radar row-one refresh" in output
    assert "uv run fashion-radar row-one preview" in output
    assert (
        "uv run fashion-radar row-one status --site-dir /repo/reports/row-one/site --json" in output
    )
    assert "uv run fashion-radar row-one serve" in output
    assert "fashion-radar run" not in output
    assert "fashion-radar row-one build" not in output
    assert "--config-dir /repo/configs" in output
    assert "--data-dir /repo/data" in output
    assert "--reports-dir /repo/reports" in output
    assert "--output-dir /repo/reports/row-one/site" in output
    assert '--as-of "$AS_OF"' in output
    refresh_line = _line_starting_with(output, "fashion-radar row-one refresh")
    assert "--latest-only" not in refresh_line
    assert shlex.split(refresh_line) == [
        "fashion-radar",
        "row-one",
        "refresh",
        "--config-dir",
        "/repo/configs",
        "--data-dir",
        "/repo/data",
        "--reports-dir",
        "/repo/reports",
        "--output-dir",
        "/repo/reports/row-one/site",
        "--as-of",
        "$AS_OF",
    ]
    assert shlex.split(_line_starting_with(output, "fashion-radar row-one preview")) == [
        "fashion-radar",
        "row-one",
        "preview",
        "--config-dir",
        "/repo/configs",
        "--data-dir",
        "/repo/data",
        "--reports-dir",
        "/repo/reports",
        "--output-dir",
        "/repo/reports/row-one/site",
        "--as-of",
        "$AS_OF",
        "--latest-only",
        "--host",
        "0.0.0.0",
        "--port",
        "8787",
        "--dry-run-serve-url",
    ]
    assert shlex.split(_line_starting_with(output, "fashion-radar row-one status")) == [
        "fashion-radar",
        "row-one",
        "status",
        "--site-dir",
        "/repo/reports/row-one/site",
        "--json",
    ]
    assert shlex.split(_line_starting_with(output, "fashion-radar row-one serve")) == [
        "fashion-radar",
        "row-one",
        "serve",
        "--site-dir",
        "/repo/reports/row-one/site",
        "--host",
        "0.0.0.0",
        "--port",
        "8787",
    ]
    assert shlex.split(_line_starting_with(output, "uv run fashion-radar row-one refresh")) == [
        "uv",
        "run",
        "fashion-radar",
        "row-one",
        "refresh",
        "--config-dir",
        "/repo/configs",
        "--data-dir",
        "/repo/data",
        "--reports-dir",
        "/repo/reports",
        "--output-dir",
        "/repo/reports/row-one/site",
        "--as-of",
        "$AS_OF",
    ]
    assert shlex.split(_line_starting_with(output, "uv run fashion-radar row-one preview")) == [
        "uv",
        "run",
        "fashion-radar",
        "row-one",
        "preview",
        "--config-dir",
        "/repo/configs",
        "--data-dir",
        "/repo/data",
        "--reports-dir",
        "/repo/reports",
        "--output-dir",
        "/repo/reports/row-one/site",
        "--as-of",
        "$AS_OF",
        "--latest-only",
        "--host",
        "0.0.0.0",
        "--port",
        "8787",
        "--dry-run-serve-url",
    ]
    assert shlex.split(_line_starting_with(output, "uv run fashion-radar row-one status")) == [
        "uv",
        "run",
        "fashion-radar",
        "row-one",
        "status",
        "--site-dir",
        "/repo/reports/row-one/site",
        "--json",
    ]
    assert "fashion-radar row-one preview" in output
    assert "--dry-run-serve-url" in output
    assert "fashion-radar row-one status --site-dir /repo/reports/row-one/site --json" in output
    assert "fashion-radar row-one serve" in output
    assert "--host 0.0.0.0" in output
    assert "--port 8787" in output
    assert "Open locally: http://127.0.0.1:8787" in output
    assert "Open from LAN: http://<LAN-IP>:8787" in output
    assert "0 4 * * *" in output
    assert "ROW ONE scheduled refresh runs the single refresh command." in output
    assert "/repo/reports/row-one/site" in output
    assert "directory marked with a .row-one-site file" in output


def test_render_row_one_local_ops_runbook_quotes_source_checkout_project_dir() -> None:
    output = render_row_one_local_ops_runbook(
        project_dir="/opt/Fashion Radar",
        config_dir="/opt/Fashion Radar/configs",
        data_dir="/opt/Fashion Radar/data",
        reports_dir="/opt/Fashion Radar/reports",
        output_dir="/tmp/ROW ONE's site",
        time="04:00",
        host="127.0.0.1",
        port=8787,
    )

    assert "Source checkout commands:" in output
    source_checkout_block = output.split("Source checkout commands:", maxsplit=1)[1].split(
        "Access:", maxsplit=1
    )[0]
    assert 'AS_OF="$(date -u +%Y-%m-%dT%H:%M:%SZ)"' in source_checkout_block
    assert "cd '/opt/Fashion Radar'" in output
    assert (
        "uv run fashion-radar row-one status --site-dir '/tmp/ROW ONE'\"'\"'s site' --json"
        in output
    )
    assert shlex.split(_line_starting_with(output, "fashion-radar row-one status")) == [
        "fashion-radar",
        "row-one",
        "status",
        "--site-dir",
        "/tmp/ROW ONE's site",
        "--json",
    ]
    assert shlex.split(_line_starting_with(output, "uv run fashion-radar row-one refresh")) == [
        "uv",
        "run",
        "fashion-radar",
        "row-one",
        "refresh",
        "--config-dir",
        "/opt/Fashion Radar/configs",
        "--data-dir",
        "/opt/Fashion Radar/data",
        "--reports-dir",
        "/opt/Fashion Radar/reports",
        "--output-dir",
        "/tmp/ROW ONE's site",
        "--as-of",
        "$AS_OF",
    ]
    assert shlex.split(_line_starting_with(output, "uv run fashion-radar row-one preview")) == [
        "uv",
        "run",
        "fashion-radar",
        "row-one",
        "preview",
        "--config-dir",
        "/opt/Fashion Radar/configs",
        "--data-dir",
        "/opt/Fashion Radar/data",
        "--reports-dir",
        "/opt/Fashion Radar/reports",
        "--output-dir",
        "/tmp/ROW ONE's site",
        "--as-of",
        "$AS_OF",
        "--latest-only",
        "--host",
        "127.0.0.1",
        "--port",
        "8787",
        "--dry-run-serve-url",
    ]
    assert shlex.split(_line_starting_with(output, "uv run fashion-radar row-one serve")) == [
        "uv",
        "run",
        "fashion-radar",
        "row-one",
        "serve",
        "--site-dir",
        "/tmp/ROW ONE's site",
        "--host",
        "127.0.0.1",
        "--port",
        "8787",
    ]


def test_render_row_one_local_ops_runbook_rejects_invalid_time() -> None:
    with pytest.raises(ValueError, match="time must be in 24-hour HH:MM format"):
        render_row_one_local_ops_runbook(
            project_dir="/repo",
            config_dir="/repo/configs",
            data_dir="/repo/data",
            reports_dir="/repo/reports",
            output_dir="/repo/reports/row-one/site",
            time="4am",
            host="127.0.0.1",
            port=8787,
        )


def test_render_row_one_systemd_uses_one_timestamp_and_output_env() -> None:
    service = render_row_one_systemd_service(
        project_dir="/opt/Fashion Radar",
        config_dir="/opt/Fashion Radar/configs",
        data_dir="/opt/Fashion Radar/data",
        reports_dir="/opt/Fashion Radar/reports",
        output_dir="/tmp/ROW ONE's site",
    )

    assert service.count("date -u") == 1
    assert 'AS_OF="$(date -u +%%Y-%%m-%%dT%%H:%%M:%%SZ)"' in service
    assert 'uv run fashion-radar row-one refresh --as-of "$AS_OF"' in service
    assert '--output-dir "$ROW_ONE_OUTPUT_DIR"' in service
    assert "fashion-radar run" not in service
    assert "fashion-radar row-one build" not in service
    assert "--latest-only" not in service
    assert 'Environment="ROW_ONE_OUTPUT_DIR=/tmp/ROW ONE\'s site"' in service
    assert 'Environment="PATH=%h/.local/bin:%h/.cargo/bin:/usr/local/bin:/usr/bin:/bin"' in service
    assert "ROW ONE'\"'\"'s site" not in service


def test_render_row_one_serve_systemd_service_uses_fixed_site_and_socket() -> None:
    service = render_row_one_serve_systemd_service(
        project_dir="/opt/Fashion Radar",
        site_dir="/tmp/ROW ONE's site",
        host="0.0.0.0",
        port=8787,
    )

    assert "[Service]" in service
    assert "Type=simple" in service
    assert "Restart=on-failure" in service
    assert "WorkingDirectory=/opt/Fashion Radar" in service
    assert "uv run fashion-radar row-one serve" in service
    assert '--site-dir "$ROW_ONE_SITE_DIR"' in service
    assert '--host "$ROW_ONE_HOST"' in service
    assert '--port "$ROW_ONE_PORT"' in service
    assert 'Environment="ROW_ONE_SITE_DIR=/tmp/ROW ONE\'s site"' in service
    assert 'Environment="ROW_ONE_HOST=0.0.0.0"' in service
    assert 'Environment="ROW_ONE_PORT=8787"' in service
    assert 'Environment="PATH=%h/.local/bin:%h/.cargo/bin:/usr/local/bin:/usr/bin:/bin"' in service


def test_render_github_actions_workflow_contains_schedule_and_no_secrets() -> None:
    workflow = render_github_actions_workflow(time="08:30")
    assert "cron: '30 8 * * *'" in workflow
    assert "GitHub Actions schedule times are UTC" in workflow
    assert "uv run fashion-radar run" in workflow
    assert "$(date -u +%Y-%m-%dT%H:%M:%SZ)" in workflow
    assert "secrets." not in workflow

import pytest

from fashion_radar.scheduling import (
    cron_as_of_shell,
    raw_as_of_shell,
    render_cron_example,
    render_github_actions_workflow,
    render_row_one_cron_example,
    render_row_one_systemd_service,
    render_systemd_service,
    render_systemd_timer,
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
    assert raw_as_of_shell() == "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    assert cron_as_of_shell() == r"$(date -u +\%Y-\%m-\%dT\%H:\%M:\%SZ)"
    assert systemd_as_of_shell() == "$(date -u +%%Y-%%m-%%dT%%H:%%M:%%SZ)"


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
    assert text.count("date -u") == 1
    assert 'AS_OF="$(date -u +\\%Y-\\%m-\\%dT\\%H:\\%M:\\%SZ)"' in text
    assert 'uv run fashion-radar run --as-of "$AS_OF"' in text
    assert 'uv run fashion-radar row-one build --as-of "$AS_OF"' in text
    assert "export FASHION_RADAR_CONFIG_DIR=/opt/fashion-radar/configs" in text
    assert "FASHION_RADAR_DATA_DIR=/opt/fashion-radar/data" in text
    assert "FASHION_RADAR_REPORTS_DIR=/opt/fashion-radar/reports" in text
    assert '{ uv run fashion-radar run --as-of "$AS_OF" && ' in text
    assert "--latest-only; } >> /opt/fashion-radar/reports/row-one-cron.log 2>&1" in text


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
    assert 'uv run fashion-radar run --as-of "$AS_OF"' in service
    assert 'uv run fashion-radar row-one build --as-of "$AS_OF"' in service
    assert '--output-dir "$ROW_ONE_OUTPUT_DIR" --latest-only' in service
    assert 'Environment="ROW_ONE_OUTPUT_DIR=/tmp/ROW ONE\'s site"' in service
    assert "ROW ONE'\"'\"'s site" not in service


def test_render_github_actions_workflow_contains_schedule_and_no_secrets() -> None:
    workflow = render_github_actions_workflow(time="08:30")
    assert "cron: '30 8 * * *'" in workflow
    assert "GitHub Actions schedule times are UTC" in workflow
    assert "uv run fashion-radar run" in workflow
    assert "$(date -u +%Y-%m-%dT%H:%M:%SZ)" in workflow
    assert "secrets." not in workflow

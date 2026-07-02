from __future__ import annotations

import shlex

from fashion_radar.row_one.server import format_row_one_site_access_message
from fashion_radar.scheduling import (
    raw_as_of_shell,
    render_row_one_cron_example,
    validate_hhmm,
)


def _shell_quote(value: str) -> str:
    return shlex.quote(value)


def render_row_one_local_ops_runbook(
    *,
    project_dir: str,
    config_dir: str,
    data_dir: str,
    reports_dir: str,
    output_dir: str,
    time: str,
    host: str,
    port: int,
) -> str:
    validate_hhmm(time)
    access_message = format_row_one_site_access_message(host, port)
    quoted_config_dir = _shell_quote(config_dir)
    quoted_data_dir = _shell_quote(data_dir)
    quoted_reports_dir = _shell_quote(reports_dir)
    quoted_output_dir = _shell_quote(output_dir)
    quoted_host = _shell_quote(host)
    run_command = (
        f"fashion-radar run --config-dir {quoted_config_dir} "
        f"--data-dir {quoted_data_dir} --reports-dir {quoted_reports_dir} "
        '--as-of "$AS_OF"'
    )
    build_command = (
        f"fashion-radar row-one build --config-dir {quoted_config_dir} "
        f"--data-dir {quoted_data_dir} --reports-dir {quoted_reports_dir} "
        f"--output-dir {quoted_output_dir} "
        '--as-of "$AS_OF" --latest-only'
    )
    preview_command = (
        f"fashion-radar row-one preview --config-dir {quoted_config_dir} "
        f"--data-dir {quoted_data_dir} --reports-dir {quoted_reports_dir} "
        f"--output-dir {quoted_output_dir} "
        f'--as-of "$AS_OF" --latest-only --host {quoted_host} --port {port} '
        "--dry-run-serve-url"
    )
    serve_command = (
        f"fashion-radar row-one serve --site-dir {quoted_output_dir} "
        f"--host {quoted_host} --port {port}"
    )
    cron_snippet = render_row_one_cron_example(
        project_dir=project_dir,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
        output_dir=output_dir,
        time=time,
    ).rstrip()
    return f"""ROW ONE local daily ops

Manual refresh:
AS_OF="{raw_as_of_shell()}"
{run_command}
{build_command}

Preview before serving:
{preview_command}

Serve fixed local URL:
{serve_command}

Access:
{access_message}

Daily {time} cron snippet:
{cron_snippet}

Storage:
--latest-only keeps only the latest generated ROW ONE site children inside a
directory marked with a .row-one-site file.
"""

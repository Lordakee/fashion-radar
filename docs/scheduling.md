# Scheduling

Fashion Radar does not run a background daemon. Use your operating system or
GitHub Actions to run the existing serial command:

```bash
fashion-radar run --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

`run` executes `collect -> match -> report` in one local process. The generated
`--as-of` timestamp is evaluated at run time in UTC and is used as both the
collection timestamp and the report window timestamp.

Do not schedule overlapping runs against the same SQLite database. If a previous
run is still active, wait for it to finish before starting another.

## Local Digest Artifacts

You can add digest flags to the scheduled `run` command when you want local
helper files for daily review:

```bash
fashion-radar run \
  --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --digest-latest copy \
  --digest-index \
  --digest-summary
```

These flags write local files such as `latest.md`, `latest.json`, and
`report-index.json`, and optionally print a short local observed summary. They
do not send email, call webhooks, open a browser, or install a notification
daemon. Use `--digest-eml` only when you want a local `.eml` handoff file that
you review yourself.

## Generate Examples

Use `schedule-example` to print snippets. It does not install anything:

```bash
uv run fashion-radar schedule-example --mode cron --project-dir "$PWD"
uv run fashion-radar schedule-example --mode systemd --project-dir "$PWD"
uv run fashion-radar schedule-example --mode github-actions --project-dir "$PWD"
```

You can pass explicit paths:

```bash
uv run fashion-radar schedule-example \
  --mode cron \
  --project-dir "$PWD" \
  --config-dir "$PWD/configs" \
  --data-dir "$PWD/data" \
  --reports-dir "$PWD/reports" \
  --time 08:00
```

## Timezones

- cron uses the machine's local timezone.
- systemd `OnCalendar` uses the machine's local timezone unless configured
  otherwise.
- GitHub Actions scheduled workflows use UTC.

The generated snippets preserve the required `%` escaping for their scheduler.
If you copy snippets manually, keep those escapes intact:

- cron needs `\%` in date format strings.
- systemd needs `%%` in unit files.
- GitHub Actions shell commands can use raw `%`.

## cron

Print a cron example:

```bash
uv run fashion-radar schedule-example --mode cron --project-dir "$PWD" --time 08:00
```

Review the output, then install it manually with:

```bash
crontab -e
```

cron often runs with a minimal `PATH`. The generated snippet keeps the crontab
`PATH` to system locations and prepends common user-local `uv` locations inside
the command, where bash expands `$HOME`. Adjust it if your `uv` binary lives
elsewhere.

Redirect logs to a file you review regularly. The generated snippet writes to:

```text
<reports-dir>/fashion-radar-cron.log
```

Use your normal log rotation or cleanup process for this file if the job runs
long term.

## systemd User Timer

Print service and timer examples:

```bash
uv run fashion-radar schedule-example --mode systemd --project-dir "$PWD" --time 08:00
```

Review the output, then place files manually:

```text
~/.config/systemd/user/fashion-radar.service
~/.config/systemd/user/fashion-radar.timer
```

Enable manually:

```bash
systemctl --user daemon-reload
systemctl --user enable --now fashion-radar.timer
systemctl --user list-timers
```

The generated service quotes environment assignments for systemd unit-file
syntax. If you edit paths manually, keep the quotes around `Environment=` values
that may contain spaces or other special characters.

The service runs through `bash -lc`, so `uv` must be available through the
login shell environment for that user. If your profile does not add `uv` to
`PATH`, change `ExecStart=` to use the absolute path to `uv`.

## GitHub Actions

Print a workflow example:

```bash
uv run fashion-radar schedule-example --mode github-actions --time 08:00
```

GitHub Actions scheduled workflows run in UTC. Generated reports are ephemeral
unless your workflow uploads artifacts or commits outputs. The example does not
use repository secrets.

The checkout must contain real `sources.yaml`, `entities.yaml`, and
`scoring.yaml` files, or your workflow must create them before running
`fashion-radar run`. The repository ships `*.example.yaml` files only.

## Cleanup

Run retention cleanup separately and start with a dry run:

```bash
uv run fashion-radar clean-old-data --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --retention-days 30 --dry-run
```

See [data-retention.md](data-retention.md).

See [daily-digest.md](daily-digest.md) for local digest artifact details.

## Dashboard

The dashboard is not required for scheduled runs. It is a local read-only
inspection UI and has no authentication layer. See [dashboard.md](dashboard.md).

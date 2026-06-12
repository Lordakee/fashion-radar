# Stage 11 Local Digest Design

## Goal

Add a local daily digest packaging layer so users can quickly find, review, and
optionally hand off the latest Fashion Radar report after a scheduled `report`
or `run` command.

Stage 11 keeps the core daily workflow free-first and local-first. It packages
already-generated Markdown and JSON reports into optional local artifacts such
as `latest.md`, `latest.json`, `report-index.json`, and a local `.eml` file.
It does not send email, open browsers, call webhooks, or collect new sources.

## Non-Goals

Stage 11 does not implement:

- SMTP, Sendmail, webhooks, push notifications, desktop notifications, browser
  opening, or any network delivery mechanism.
- Social platform search, scraping, crawling, browser automation, account
  automation, social login/session use, unofficial social APIs, platform export
  acquisition instructions, CAPTCHA bypass, rate-limit bypass, anti-bot
  workarounds, or bulk media download.
- Instagram, TikTok, X/Twitter, Xiaohongshu, Reddit, or other platform
  collectors.
- Private data collection, comments, DMs, account IDs, follower lists, cookies,
  session artifacts, images, videos, or raw media storage.
- New scoring logic, report content changes, dashboard writes, schema
  migrations, persistent delivery tables, or background daemons.

Any social or platform label remains provenance supplied by the user through
already-local rows or configured source metadata. It must not be described as
platform coverage, complete social listening, market-wide truth, verified
demand, real-time social monitoring, or top social trends.

## Recommended Approach

Add a small `fashion_radar.digests` module that receives the report paths
returned by `write_daily_report_files()` and writes optional companion files.
Keep `reports.py` responsible only for building/rendering report content and
keep `workflows.write_daily_report_files()` responsible only for date-stamped
Markdown/JSON generation.

Wire digest packaging into the existing `report` and `run` CLI commands after
the report files have been written. Defaults remain no-op, so existing behavior
does not change unless users pass explicit digest options.

## Public Interface

New optional CLI flags on both `fashion-radar report` and `fashion-radar run`:

```bash
fashion-radar report --digest-latest copy --digest-index --digest-summary
fashion-radar report --digest-latest symlink --digest-eml
fashion-radar run --digest-latest copy --digest-index --digest-eml --digest-summary
```

Options:

- `--digest-latest none|copy|symlink`: write local `latest.md` and
  `latest.json` artifacts. Default is `none`.
- `--digest-index / --no-digest-index`: write `report-index.json`. Default is
  false.
- `--digest-eml / --no-digest-eml`: write a local `.eml` file with the
  generated report attached. Default is false.
- `--digest-summary / --no-digest-summary`: print a concise local observed
  digest summary to stdout. Default is false.

Stage 11 intentionally avoids recipient, sender, SMTP, webhook, browser, and
desktop notification options. The `.eml` file is a local handoff artifact only.

## Artifact Names

Date-stamped reports keep the existing names:

```text
fashion-radar-YYYY-MM-DD.md
fashion-radar-YYYY-MM-DD.json
```

Optional Stage 11 artifacts:

```text
latest.md
latest.json
report-index.json
fashion-radar-YYYY-MM-DD.eml
```

Stage 11 must not create `fashion-radar-latest.json` or
`fashion-radar-index.json` because the dashboard currently discovers daily JSON
reports with a `fashion-radar-*.json` glob. The safer `latest.json` and
`report-index.json` names avoid that collision.

## Data Flow

```text
configured collection/import data
  -> write_daily_report_files()
  -> fashion-radar-YYYY-MM-DD.md/json
  -> package_daily_digest()
  -> optional latest files, report index, local .eml, stdout summary
```

The digest module reads only the generated Markdown/JSON report files. It does
not open SQLite, run collectors, call platform tooling, or modify report
content.

## Digest Module

Create `src/fashion_radar/digests.py` with:

- `DigestLatestMode`: `none`, `copy`, `symlink`.
- `DigestOptions`: selected local packaging options.
- `DigestResult`: generated artifact paths plus optional summary text.
- `package_daily_digest(markdown_path, json_path, reports_dir, options)`.
- `write_latest_artifacts(markdown_path, json_path, reports_dir, mode)`.
- `write_report_index(reports_dir)`.
- `write_eml_digest(markdown_path, json_path, reports_dir)`.
- `render_digest_summary(markdown_path, json_path, result)`.

Implementation requirements:

- Validate that both source report files exist before packaging.
- Use strict filename parsing for date-stamped reports:
  `fashion-radar-YYYY-MM-DD.md` and `fashion-radar-YYYY-MM-DD.json`.
- Build `report-index.json` from matched date-stamped Markdown/JSON pairs only.
  Ignore malformed report-like names, `latest.*`, `report-index.json`, and any
  non-report helper files.
- Sort report-index entries by report date descending.
- Write copy, index, and `.eml` outputs through temporary files and
  `Path.replace()` where practical.
- Use relative symlinks for `latest.md` and `latest.json` in symlink mode.
- Fail clearly if symlink creation is unavailable or if any packaging write
  fails.
- Generate `.eml` with Python stdlib `email.message.EmailMessage`, local
  subject/body text, deterministic minimal headers, and Markdown/JSON
  attachments. Do not send the message. Do not set `To`, `Cc`, or `Bcc`.
- Use local observed wording in summaries and `.eml` body.
- Keep `digests.py` independent from database, collector, dashboard, scoring,
  and source modules. It may import only stdlib helpers and its own local types.

`report-index.json` should be a stable object with an `entries` array:

```json
{
  "entries": [
    {
      "report_date": "2026-06-12",
      "markdown_path": "fashion-radar-2026-06-12.md",
      "json_path": "fashion-radar-2026-06-12.json"
    }
  ]
}
```

The date component must be a real ISO calendar date, not just a regex-shaped
string. Ignore malformed helper files such as `fashion-radar-2026-99-99.json`.
For local symlink mode, replace existing `latest.md` and `latest.json` entries
inside `reports_dir` without following an existing symlink target outside the
reports directory.

## CLI Behavior

`report` and `run` should:

- Keep existing output when no digest flags are passed.
- Package digest artifacts only after `write_daily_report_files()` succeeds.
- Print each generated digest artifact path with concise labels.
- Print the digest summary only when `--digest-summary` is set.
- If packaging fails, print `Could not package digest: <error>` and exit non-zero.
  Date-stamped report files may already exist; Stage 11 should not attempt to
  delete them.

## Documentation

Add `docs/daily-digest.md` and update:

- `README.md`
- `docs/architecture.md`
- `docs/scheduling.md`
- `reports/README.md`
- `.gitignore`
- `CHANGELOG.md`

Docs must state that digest artifacts are local files. They must not imply
email sending, complete social listening, platform-wide coverage, real-time
social monitoring, verified demand, or market-wide trend proof.

## Verification

Focused verification:

```bash
.venv/bin/python -m pytest tests/test_digests.py tests/test_cli.py -k "digest or report_command or run_command" -q
.venv/bin/python -m ruff check src/fashion_radar/digests.py src/fashion_radar/cli.py tests/test_digests.py tests/test_cli.py
.venv/bin/python -m ruff format --check src/fashion_radar/digests.py src/fashion_radar/cli.py tests/test_digests.py tests/test_cli.py
```

Final verification:

```bash
git diff --check
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
uv lock --check
uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
uv build --out-dir /tmp/fashion-radar-dist-stage11
```

Then run an installed-wheel smoke test for the digest CLI path and ask Claude
Code to review the new Stage 11 code and docs before commit/push.

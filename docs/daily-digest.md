# Local Daily Digest

Fashion Radar can package generated daily reports into optional local helper
artifacts after `report` or `run` completes. This is useful for scheduled
workflows where you want the latest report to have a stable filename or a local
handoff file.

Digest packaging reads only the Markdown and JSON report files that were just
generated. It does not collect sources, open SQLite, send email, call webhooks,
open a browser, or install a notification daemon.

## CLI Usage

Write stable latest-report copies and an index:

```bash
uv run fashion-radar report \
  --config-dir "$PWD/configs" \
  --data-dir "$PWD/data" \
  --reports-dir "$PWD/reports" \
  --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --digest-latest copy \
  --digest-index
```

Do the same at the end of the serial daily workflow:

```bash
uv run fashion-radar run \
  --config-dir "$PWD/configs" \
  --data-dir "$PWD/data" \
  --reports-dir "$PWD/reports" \
  --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --digest-latest copy \
  --digest-index \
  --digest-summary
```

Create relative symlinks instead of copies when your filesystem supports them:

```bash
uv run fashion-radar report \
  --config-dir "$PWD/configs" \
  --data-dir "$PWD/data" \
  --reports-dir "$PWD/reports" \
  --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --digest-latest symlink
```

Write a local `.eml` file for manual review:

```bash
uv run fashion-radar report \
  --config-dir "$PWD/configs" \
  --data-dir "$PWD/data" \
  --reports-dir "$PWD/reports" \
  --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --digest-eml
```

The `.eml` file has local subject/body text and Markdown/JSON attachments. It
has no `To`, `Cc`, or `Bcc` headers, and Fashion Radar never sends it.

## Artifacts

The date-stamped report files keep their existing names:

```text
fashion-radar-YYYY-MM-DD.md
fashion-radar-YYYY-MM-DD.json
```

Digest packaging can add:

```text
latest.md
latest.json
report-index.json
fashion-radar-YYYY-MM-DD.eml
```

`report-index.json` uses this shape:

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

The index includes only matched date-stamped Markdown/JSON report pairs with
real ISO calendar dates. Helper files and malformed names are ignored.

## Scheduling

Use your existing cron, systemd, or GitHub Actions command and add digest flags
to the `fashion-radar run` line:

```bash
fashion-radar run \
  --config-dir "$PWD/configs" \
  --data-dir "$PWD/data" \
  --reports-dir "$PWD/reports" \
  --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --digest-latest copy \
  --digest-index \
  --digest-summary
```

Digest artifacts are generated locally inside the configured reports directory.
They are ignored by git with the rest of the generated reports.

## Review Boundary

Digest summaries describe local observed signals from your configured source
set and imported local signals. They are review aids, not claims about demand
outside that source set.

Reports can contain source links, snippets/metadata, matched entities, candidate
signals, and score components. Review source attribution and any internal feed
metadata before sharing a report or `.eml` file.

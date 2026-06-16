# Community Tool Handoff Directory Example

This directory shows a local export layout for a user-controlled external
community tool.

- Use `csv/*.csv` with `--input-format csv --pattern "*.csv"`.
- Use `json/*.json` with `--input-format json --pattern "*.json"`.

The `csv/` and `json/` directories are separate because Fashion Radar reads one
input format and one matched filename pattern per directory command. The
directory commands read matching regular files directly under the supplied
directory; they do not recurse into nested directories.

Do not save a `community-handoff-manifest --format json` output as a matched
handoff file inside `json/`. Save manifests outside the matched export
directory, or use an excluded filename or pattern.

These examples are sanitized local CSV/JSON handoff files only. They are not
platform collection and do not add connectors, scraping, browser automation,
platform APIs, monitoring, scheduling, source acquisition, demand proof,
ranking, or coverage verification. The sample rows do not include raw,
private, account, cookie, session, token, or media fields.

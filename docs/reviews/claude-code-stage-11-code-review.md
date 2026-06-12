APPROVED: no blocking issues; may commit/push.

Minor non-blocking notes:

- `src/fashion_radar/digests.py` stays within the intended stdlib-only local packaging boundary; I found no imports from database, collector, dashboard, source, scoring, or workflow modules.
- Latest copy/symlink, index, and `.eml` behavior appears deterministic and local-only. `.eml` generation sets no `To`, `Cc`, or `Bcc` headers and does not include any sending path.
- Symlink replacement uses a temporary sibling symlink followed by `Path.replace(destination)`, which replaces the destination directory entry rather than following an existing `latest.*` symlink target. This satisfies the outside-target safety requirement.
- `report-index.json` generation enforces the strict `fashion-radar-YYYY-MM-DD.{md,json}` naming pattern and real ISO calendar dates, and ignores helper/malformed files. Minor possible hardening: require the matched JSON path to be a file, not just `exists()`, though this is not blocking for the current objective.
- CLI default behavior is preserved: without digest flags, `report` and `run` return before packaging and keep their prior stdout shape.
- CLI packaging failures happen after report generation, print `Could not package digest: <error>`, and exit non-zero as specified.
- Tests cover the main behavior and safety boundaries: no-op defaults, copy/symlink latest artifacts, index shape/order/filtering, invalid dates, local `.eml` recipients/attachments, digest CLI flags, default no-artifact CLI behavior, and packaging error handling.
- Docs and stdout copy consistently use local observed / configured-source-set wording and do not add delivery, platform collection, social scraping, or broad coverage claims.
- `.gitignore` covers generated report/digest artifacts including Markdown, JSON, `.eml`, and text files under `reports/`, while preserving `reports/README.md`.

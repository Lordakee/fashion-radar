Approved for Stage 11 implementation

- `Critical:` None.

- `Important:` None.

- `Minor:` In `docs/superpowers/plans/2026-06-12-stage-11-local-digest-plan.md`, Task 4’s `.gitignore` update lists `reports/*.eml`, `reports/*.txt`, `reports/**/*.eml`, and `reports/**/*.txt`, but the planned digest artifacts also include local helper files such as `latest.md`, `latest.json`, and `report-index.json`. Existing `.gitignore` already ignores `reports/*.md`, `reports/*.json`, `reports/**/*.md`, and `reports/**/*.json`, so this is covered today, but the plan should explicitly call out that those existing rules intentionally cover Stage 11 latest/index artifacts. This avoids a future cleanup accidentally narrowing ignore rules and committing local digest artifacts.

- `Minor:` The `.eml` design is appropriately bounded as a local handoff artifact, but the plan should specify deterministic, minimal headers more explicitly: no `To`, no `Cc`, no `Bcc`, no SMTP/sendmail integration, and only local subject/body plus Markdown/JSON attachments. This is already implied, but making it explicit will make code review simpler.

- `Minor:` The report-index format should include a short example in the design or docs plan. The fields `report_date`, `markdown_path`, and `json_path` are good and safe, but an example would lock in whether the top-level JSON is an array or object and help tests assert stable output.

- `Minor:` For strict filename parsing, the implementation plan should clarify that dates must be real ISO calendar dates, not just regex-shaped strings. For example, `fashion-radar-2026-99-99.json` should be ignored/rejected rather than indexed.

- `Minor:` For symlink mode, the plan correctly asks for relative symlinks and clear failure if unavailable. Consider specifying the replacement behavior for existing `latest.md`/`latest.json`: remove/replace an existing file or symlink atomically where practical, but never follow an existing symlink target and overwrite outside `reports_dir`.

- `Minor:` The CLI test list covers digest wiring, error handling, help text, and default-output stability indirectly. Add an explicit test that default `report` and `run` output contains exactly the existing report lines and creates no digest artifacts when no digest flags are passed. This directly protects the no-op-by-default requirement.

- `Minor:` Task 5 includes `uv sync --locked --dev --check` and `UV_DEFAULT_INDEX=... uv sync --frozen --dev --check`. Those may call package indexes depending on environment/cache behavior. That is fine for implementation verification, but not for this read-only plan review. If documenting review-mode commands, keep them separate from no-network plan review instructions.

- `Minor:` The proposed `digests.py` boundary is the right fit. It keeps `reports.py` focused on rendering report content and keeps `write_daily_report_files()` focused on date-stamped report generation. The plan should preserve this by ensuring `digests.py` reads only the two generated report paths and the reports directory listing for index generation, and does not import database, collector, dashboard, or scoring modules.

- `Minor:` Artifact naming avoids the dashboard collision correctly. Existing dashboard discovery uses `reports_dir.glob("fashion-radar-*.json")`, so avoiding `fashion-radar-latest.json` and `fashion-radar-index.json` is necessary. `latest.json` and `report-index.json` are safe.

- `Minor:` The docs wording constraints are strong and appropriate. During implementation, pay special attention to scheduling/GitHub Actions examples so they do not imply delivery, notification, platform-wide monitoring, or committed report artifacts.

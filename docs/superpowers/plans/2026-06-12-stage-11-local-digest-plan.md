# Stage 11 Local Digest Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an optional local digest packaging layer for daily Fashion Radar reports so scheduled runs can produce easy-to-find local latest files, an index manifest, a local `.eml` handoff file, and a concise stdout summary.

**Architecture:** Keep report rendering unchanged. Create a focused `fashion_radar.digests` module that packages the Markdown/JSON report paths returned by `write_daily_report_files()`, then wire explicit no-op-by-default digest flags into `report` and `run`.

**Tech Stack:** Python 3.11+, dataclasses, `enum.StrEnum`, pathlib, stdlib `email.message.EmailMessage`, Typer, pytest, ruff, uv.

---

## Scope Guard

Stage 11 may package only already-generated local report files. It must not add
or document SMTP sending, Sendmail sending, webhooks, push services, desktop
notifications, browser opening, background daemons, platform search, crawler
development, automated social extraction, browser automation, account
automation, social login/session use, CAPTCHA or rate-limit bypass, anti-bot
workarounds, unofficial platform APIs, bulk media download, private data
collection, or instructions for obtaining platform exports.

Stage 11 must not add Instagram, TikTok, X/Twitter, Xiaohongshu, Reddit, or
other platform connectors. Any social/platform label remains provenance from
already-local rows or configured source metadata and must not be described as
platform coverage, complete social listening, verified demand, market-wide
truth, real-time social monitoring, or top social trends.

Stage 11 must not alter scoring, candidate discovery, trend delta semantics,
database schema, dashboard writes, source collection behavior, or default
`report`/`run` behavior without explicit digest flags.

Codex subagents must use `reasoning_effort: "xhigh"`. Claude Code review must
use `--effort max`.

## Files

- Create: `src/fashion_radar/digests.py`
- Create: `tests/test_digests.py`
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`
- Create: `docs/daily-digest.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/scheduling.md`
- Modify: `reports/README.md`
- Modify: `.gitignore`
- Modify: `CHANGELOG.md`
- Create before implementation: `docs/reviews/claude-code-stage-11-plan-review-prompt.md`
- Create after plan review: `docs/reviews/claude-code-stage-11-plan-review.md`
- Create after implementation: `docs/reviews/claude-code-stage-11-code-review-prompt.md`
- Create after code review: `docs/reviews/claude-code-stage-11-code-review.md`

## Public Interfaces

New options on `fashion-radar report` and `fashion-radar run`:

```bash
fashion-radar report --digest-latest copy --digest-index --digest-summary
fashion-radar report --digest-latest symlink --digest-eml
fashion-radar run --digest-latest copy --digest-index --digest-eml --digest-summary
```

Options:

- `--digest-latest none|copy|symlink`
- `--digest-index / --no-digest-index`
- `--digest-eml / --no-digest-eml`
- `--digest-summary / --no-digest-summary`

Generated local artifact names:

```text
latest.md
latest.json
report-index.json
fashion-radar-YYYY-MM-DD.eml
```

Do not create `fashion-radar-latest.json` or `fashion-radar-index.json`.

## Task 1: Claude Code Plan Gate

- [ ] Create `docs/reviews/claude-code-stage-11-plan-review-prompt.md` with the Stage 11 goal, design, plan, explicit no-network/no-edit review instruction, scope guard, tests, docs, and response format.
- [ ] Run Claude Code in plan/read-only mode:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-11-plan-review-prompt.md
```

- [ ] Save the review to `docs/reviews/claude-code-stage-11-plan-review.md`.
- [ ] Fix every Critical and Important finding before Task 2. If Claude Code is not approved, save follow-up prompts/results as `docs/reviews/claude-code-stage-11-plan-rereview*.md` and repeat until approved.

## Task 2: Digest Module

**Files:**

- Create: `src/fashion_radar/digests.py`
- Create: `tests/test_digests.py`

- [ ] Add failing tests in `tests/test_digests.py` for these behaviors:
  - `test_package_daily_digest_no_options_writes_nothing`
  - `test_package_daily_digest_writes_latest_copies`
  - `test_package_daily_digest_writes_latest_symlinks`
  - `test_write_report_index_lists_date_stamped_pairs_descending`
  - `test_write_report_index_ignores_helper_and_malformed_files`
  - `test_package_daily_digest_writes_local_eml_with_attachments`
  - `test_render_digest_summary_uses_local_observed_wording`
  - `test_package_daily_digest_rejects_missing_report_files`
  - `test_package_daily_digest_rejects_non_daily_report_names`

- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_digests.py -q
```

Expected: fails because `fashion_radar.digests` does not exist.

- [ ] Implement `src/fashion_radar/digests.py` with:

```python
class DigestLatestMode(StrEnum):
    NONE = "none"
    COPY = "copy"
    SYMLINK = "symlink"


@dataclass(frozen=True)
class DigestOptions:
    latest: DigestLatestMode = DigestLatestMode.NONE
    write_index: bool = False
    write_eml: bool = False
    print_summary: bool = False


@dataclass(frozen=True)
class DigestResult:
    latest_markdown_path: Path | None = None
    latest_json_path: Path | None = None
    index_path: Path | None = None
    eml_path: Path | None = None
    summary_text: str | None = None
```

- [ ] Implement `package_daily_digest()` so it validates the source report files, writes only selected artifacts, and returns a `DigestResult`.
- [ ] Implement atomic text/copy helpers using temporary sibling paths and `Path.replace()`.
- [ ] Implement strict daily report filename parsing with the pattern `fashion-radar-YYYY-MM-DD.{md,json}`.
- [ ] Implement filename date validation with `datetime.date.fromisoformat()` so regex-shaped invalid dates such as `2026-99-99` are ignored or rejected.
- [ ] Implement `write_report_index()` so it writes a stable JSON object with sorted `entries`, where each entry contains `report_date`, `markdown_path`, and `json_path` relative filenames.
- [ ] Use this report-index shape:

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

- [ ] Implement `write_eml_digest()` with stdlib `EmailMessage`, deterministic minimal headers, a local observed body, Markdown attachment, and JSON attachment. Do not set `To`, `Cc`, or `Bcc`, and do not send the message.
- [ ] Implement `render_digest_summary()` with local observed wording and source-review language.
- [ ] Keep `src/fashion_radar/digests.py` free of imports from database, collector, dashboard, source, scoring, and workflow modules.
- [ ] Ensure symlink mode replaces existing `latest.md` and `latest.json` entries in `reports_dir` without following an existing symlink target outside `reports_dir`.
- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_digests.py -q
.venv/bin/python -m ruff check src/fashion_radar/digests.py tests/test_digests.py
.venv/bin/python -m ruff format --check src/fashion_radar/digests.py tests/test_digests.py
```

Expected: all pass.

## Task 3: CLI Wiring

**Files:**

- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`

- [ ] Add failing CLI tests:
  - `test_report_command_packages_digest_artifacts`
  - `test_report_command_digest_packaging_error_exits_nonzero`
  - `test_run_command_packages_digest_after_report`
  - `test_report_command_help_lists_digest_options`
  - `test_report_command_default_output_creates_no_digest_artifacts`
  - `test_run_command_default_output_creates_no_digest_artifacts`

- [ ] Run focused tests:

```bash
.venv/bin/python -m pytest tests/test_cli.py -k "digest or report_command or run_command" -q
```

Expected: new digest tests fail because CLI options are missing.

- [ ] Import digest models/helpers in `src/fashion_radar/cli.py`.
- [ ] Add a reusable `DIGEST_LATEST_OPTION` and boolean digest options near existing Typer option constants.
- [ ] Add digest options to `report()` and `run()` signatures.
- [ ] Add a private helper such as `_package_digest_or_exit(markdown_path, json_path, reports_dir, digest_latest, digest_index, digest_eml, digest_summary)` that:
  - returns immediately when all options are default/no-op,
  - calls `package_daily_digest()`,
  - prints generated artifact paths,
  - prints summary text only when present,
  - converts packaging exceptions into `typer.Exit(1)` with `Could not package digest: <error>`.
- [ ] Call the helper after existing report path output in `report()`.
- [ ] Call the helper after existing report path output in `run()`.
- [ ] Keep current CLI output unchanged when no digest options are passed.
- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -k "digest or report_command or run_command" -q
.venv/bin/python -m ruff check src/fashion_radar/cli.py tests/test_cli.py
.venv/bin/python -m ruff format --check src/fashion_radar/cli.py tests/test_cli.py
```

Expected: all pass.

## Task 4: Documentation And Ignore Rules

**Files:**

- Create: `docs/daily-digest.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/scheduling.md`
- Modify: `reports/README.md`
- Modify: `.gitignore`
- Modify: `CHANGELOG.md`

- [ ] Add `reports/*.eml`, `reports/*.txt`, `reports/**/*.eml`, and `reports/**/*.txt` to `.gitignore` while preserving `reports/README.md`.
- [ ] Document in `.gitignore` or `reports/README.md` that existing `reports/*.md`, `reports/*.json`, `reports/**/*.md`, and `reports/**/*.json` ignore the Stage 11 `latest.md`, `latest.json`, and `report-index.json` artifacts.
- [ ] Add `docs/daily-digest.md` documenting:
  - what local digest artifacts are,
  - exact CLI examples,
  - no sending/no network behavior,
  - how to add digest flags to existing cron/systemd/GitHub Actions examples,
  - local observed wording and sharing cautions.
- [ ] Update README report/storage docs to link to `docs/daily-digest.md`.
- [ ] Update architecture docs to show optional post-report packaging.
- [ ] Update scheduling docs with an example `fashion-radar run --digest-latest copy --digest-index --digest-summary`.
- [ ] Update `reports/README.md` to list optional ignored local digest artifacts.
- [ ] Update `CHANGELOG.md`.
- [ ] Run wording guard:

```bash
rg -n "top social trend|social trends|platform-wide|market-wide|verified demand|complete social listening|real-time social monitoring" \
  README.md docs/daily-digest.md docs/architecture.md docs/scheduling.md reports/README.md src tests
```

Expected: no matches in Stage 11 user-facing docs, source code, or tests except
tests that explicitly assert those phrases are absent.

## Task 5: Final Verification And Claude Code Review

- [ ] Run focused verification:

```bash
.venv/bin/python -m pytest tests/test_digests.py tests/test_cli.py -k "digest or report_command or run_command" -q
.venv/bin/python -m ruff check src/fashion_radar/digests.py src/fashion_radar/cli.py tests/test_digests.py tests/test_cli.py
.venv/bin/python -m ruff format --check src/fashion_radar/digests.py src/fashion_radar/cli.py tests/test_digests.py tests/test_cli.py
```

- [ ] Run full verification:

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

- [ ] Run installed-wheel smoke from `/tmp/fashion-radar-dist-stage11` for a digest CLI help or no-op command.
- [ ] Confirm CodeGraph status can read the new module.
- [ ] Secret/generated-file sanity check:

```bash
git status --short
git diff --stat
```

- [ ] Run a local secret scan for GitHub personal-access-token prefixes,
  private-key headers, session artifacts, and cookie artifacts without writing
  token-shaped regular expressions into committed documentation.

- [ ] Create `docs/reviews/claude-code-stage-11-code-review-prompt.md` with changed files, behavior summary, verification results, and the next-stage plan.
- [ ] Run Claude Code review:

```bash
claude -p --effort max --allowedTools=Read,Grep,Glob < docs/reviews/claude-code-stage-11-code-review-prompt.md
```

- [ ] Save the review to `docs/reviews/claude-code-stage-11-code-review.md`.
- [ ] Fix every Critical and Important finding and re-review if needed.
- [ ] Commit and push only after Claude Code approves.

## Acceptance Criteria

- Default `fashion-radar report` and `fashion-radar run` behavior remains unchanged without digest flags.
- `--digest-latest copy` writes `latest.md` and `latest.json` as local copies.
- `--digest-latest symlink` writes `latest.md` and `latest.json` as local relative symlinks on supported systems.
- `--digest-index` writes `report-index.json` from strict date-stamped report pairs only.
- `--digest-eml` writes a local `.eml` file and never sends it.
- `--digest-summary` prints local observed summary wording.
- Docs describe digest artifacts as local files and avoid platform/social coverage claims.
- Full verification and Claude Code review pass before commit/push.

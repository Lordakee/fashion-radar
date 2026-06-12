# Stage 16 Community Signal File Diagnostics Design

## Goal

Add a local, read-only diagnostics command for community signal CSV/JSON files
before they are imported with `fashion-radar import-signals`. The command should
help external tools controlled by the user produce stable handoff files that fit
Fashion Radar's existing community signal contract.

Stage 16 improves local file quality feedback. It does not add source
collection, platform connectors, platform search, scraping, browser automation,
account automation, source acquisition, real-time monitoring, ranking claims,
or market-wide demand proof.

## Context

Stage 9 added `import-signals`, which validates and stores local CSV/JSON rows
as `manual_import`. Stage 13 added a strict community signal handoff contract:

- `examples/community-signals.example.csv`
- `examples/community-signals.example.json`
- `schemas/community-signals.schema.json`
- `docs/community-signal-import.md`

The runtime importer intentionally ignores unknown fields for backwards
compatibility with manual imports. That is useful for manual flexibility, but it
means external tools can accidentally produce unsupported or raw fields without
seeing a clear warning until a separate schema validator is used.

Stage 16 should add a first-party lint command that checks one local signal file
against the community contract, explains import readiness, and remains
read-only.

## Recommended Approach

Create a new diagnostics module:

```text
src/fashion_radar/community_signals.py
```

Expose:

```python
class CommunitySignalFindingSeverity(StrEnum): ...
class CommunitySignalFinding(BaseModel): ...
class CommunitySignalLintResult(BaseModel): ...

def lint_community_signal_file(
    path: Path,
    *,
    input_format: ManualSignalFormat,
    default_source_name: str = "Community Signal Import",
) -> CommunitySignalLintResult: ...
def render_community_signal_lint_table(result: CommunitySignalLintResult) -> list[str]: ...
```

Add a flat Typer command:

```bash
fashion-radar community-signal-lint PATH --input-format csv
fashion-radar community-signal-lint PATH --input-format json
fashion-radar community-signal-lint PATH --input-format csv --format json
fashion-radar community-signal-lint PATH --input-format csv --strict
fashion-radar community-signal-lint PATH --input-format csv --source-name "Community Tool Export"
```

Command behavior:

- `--input-format csv|json` identifies the file format.
- `--format table|json` controls output, matching other lint commands.
- `--source-name TEXT` uses the same fallback source-name semantics as
  `import-signals` for rows that omit or blank `source_name`.
- `--strict` exits non-zero when warnings are present.
- errors always exit non-zero.
- output is printed before exit handling.
- the command has no `--config-dir`, `--data-dir`, or `--reports-dir`.
- the command does not open SQLite, create directories, import rows, collect
  sources, match entities, score reports, call network, or run platform tooling.

The linter should read raw rows directly so it can detect unknown fields before
the existing importer ignores them. For import-readiness validation, it should
use the same `ManualSignalRow` model and fallback source-name behavior used by
`load_manual_signal_rows()`.

## Contract

Allowed community signal fields are:

- `url`
- `title`
- `published_at`
- `summary`
- `source_name`
- `platform`
- `source_weight`
- `collected_at`

The linter should treat these raw/private/account/media field names as errors
when they appear in CSV headers or JSON objects:

- `author_handle`
- `raw_comment`
- `account_id`
- `follower_count`
- `image_url`
- `video_url`
- `profile_url`
- `full_post_body`
- `direct_message`
- `cookie`
- `session`
- `token`

Other unknown fields are errors under the community signal contract because
external tools should produce only the documented handoff fields.

## Diagnostics

Errors:

- `invalid_file`: the file cannot be read, parsed, or shaped as CSV rows, a JSON
  list, or a JSON object with an `items` list.
- `csv_extra_cells`: a CSV row has more cells than headers.
- `unknown_field`: a row contains a field outside the community contract and
  outside the explicit prohibited-field list.
- `prohibited_field`: a row contains a raw/private/account/media/session field
  that the community contract excludes. Prohibited fields should not also emit
  `unknown_field`.
- `invalid_row`: a row fails the same required-field, timestamp, or
  `source_weight` validation used by manual import.

Warnings:

- `empty_signal_file`: the file contains zero rows.
- `missing_source_name`: a row omits `source_name`, so import would use the CLI
  fallback source name.
- `missing_platform`: a row omits `platform`, reducing local provenance detail.
- `missing_summary`: a row omits a short review note.
- `duplicate_url`: two or more rows share the same URL. Import can upsert by
  normalized URL, so duplicate rows may not add separate items.
- `collected_before_published`: `collected_at` is earlier than `published_at`.

Info:

- `implicit_source_weight`: a row omits `source_weight`, so the default local
  score weight is used.
- `implicit_collected_at`: a row omits `collected_at`, so import time is used.

## Output Shape

JSON output should be stable:

```json
{
  "path": "examples/community-signals.example.csv",
  "input_format": "csv",
  "row_count": 2,
  "valid_row_count": 2,
  "field_counts": {
    "collected_at": 2,
    "platform": 2,
    "published_at": 2,
    "source_name": 2,
    "source_weight": 2,
    "summary": 2,
    "title": 2,
    "url": 2
  },
  "source_name_counts": {
    "Community Tool Export": 2
  },
  "platform_counts": {
    "community": 2
  },
  "findings": []
}
```

Table output should mirror existing lint commands:

```text
Community signal file: examples/community-signals.example.csv
Input format: csv
Rows: 2 total, 2 import-ready
Fields: collected_at=2, platform=2, published_at=2, source_name=2, source_weight=2, summary=2, title=2, url=2
Sources: Community Tool Export=2
Platforms: community=2
Findings: 0 errors, 0 warnings, 0 info
No community-signal quality findings.
```

When findings exist:

```text
Severity | Code | Row | Field | Message
error | prohibited_field | 2 | author_handle | Field is excluded from the community signal contract.
```

## Files

Create:

- `src/fashion_radar/community_signals.py`
- `tests/test_community_signal_lint.py`
- `docs/community-signal-quality.md`

Modify:

- `src/fashion_radar/cli.py`
- `tests/test_cli.py`
- `docs/community-signal-import.md`
- `README.md`
- `docs/architecture.md`
- `CHANGELOG.md`

Process artifacts:

- `docs/superpowers/specs/2026-06-12-stage-16-community-signal-file-diagnostics-design.md`
- `docs/superpowers/plans/2026-06-12-stage-16-community-signal-file-diagnostics-plan.md`
- `docs/reviews/claude-code-stage-16-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-16-plan-review.md`
- later Stage 16 code review prompts/results.

## Non-Goals

Stage 16 does not implement or document:

- social-platform connectors, platform search, remote community ingestion, or
  automated social collection;
- web scraping, crawler development, browser automation, account automation, or
  unofficial platform APIs;
- login cookies, session files, browser profiles, tokens, credentials, proxy
  pools, fingerprint evasion, CAPTCHA bypass, rate-limit bypass,
  access-control bypass, or paywall bypass;
- instructions for obtaining exports from social/community platforms;
- raw comments, full post bodies, private messages, author handles, account IDs,
  follower lists, profile URLs, images, videos, media downloading, reposting, or
  archive redistribution;
- platform-wide, community-wide, social-wide, or market-wide coverage claims;
- current-hotness rankings, demand proof, real-time trend monitoring, or top
  social trend lists;
- DB migrations, source-health changes, collector changes, dashboard changes,
  report semantics changes, matcher changes, scoring changes, persistent
  adapter tables, or network calls;
- product-facing compliance review, audit workflow, safety workflow, approval
  UI, policy checklist, or legal review feature.

## Testing

Focused tests should prove:

- repository CSV and JSON examples lint cleanly;
- unknown and prohibited fields are errors;
- invalid rows use the same validation semantics as import;
- duplicate URLs, missing provenance fields, missing summary, and implicit
  defaults emit deterministic findings;
- collected-before-published emits a warning;
- result JSON shape and table rendering are stable;
- CLI help, table output, JSON output, strict mode, invalid file behavior, and
  no-artifact behavior are covered;
- the command does not create config, data, reports, SQLite, digest, report, or
  workflow artifacts.

No test should call the network, run collectors, invoke platform/social tooling,
or require external account data.

## Documentation

Add `docs/community-signal-quality.md` with command examples, output examples,
severity meanings, finding codes, why findings matter, tuning guidance for
external tool handoff files, and limits.

Update `docs/community-signal-import.md` to recommend
`community-signal-lint --strict` before `import-signals --dry-run`. Docs should
explain that the linter checks local files only and that `platform` and
`source_name` are provenance labels, not coverage claims.

## Verification

Required before Stage 16 code review:

- focused community-signal lint tests;
- full `pytest -q`;
- `ruff check .`;
- `ruff format --check .`;
- `git diff --check`;
- CodeGraph status;
- Claude Code code review with `--effort max`.

Optional release operations, not part of Stage 16 implementation acceptance:

- `uv lock --check --default-index https://pypi.org/simple`;
- `uv sync --locked --dev --check --default-index https://pypi.org/simple`;
- `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check`;
- package build;
- installed-wheel smoke checks;
- secret/generated-artifact sanity checks before GitHub upload.

# Stage 53 Community Handoff Guardrails Design

## Objective

Strengthen the community handoff quality guardrails added in recent stages
without changing runtime behavior or adding any source acquisition capability.

## Background

The community handoff path now exposes a local producer profile, directory
workflow, directory manifest, directory linting, directory candidate preview,
and directory import flow. Those commands deliberately accept sanitized local
CSV/JSON files produced by user-controlled tools. The current implementation
already rejects platform connector behavior and avoids reading files in the
print-only profile/workflow/manifest commands.

The remaining risk is drift in the public handoff contract:

- Prohibited fields are defined centrally, but lint tests only directly cover
  one prohibited field in CSV.
- The producer profile exposes `recommended_commands`, but tests mostly freeze
  the generated example rather than the command sequence semantics.
- `community-candidates-dir` has strong CLI safety coverage, but lacks the
  same invalid output-format parser test as the single-file command.
- Documentation describes the producer profile command sequence, but there is
  no focused drift test tying the documented directory command order back to
  the profile sequence.

## Technical Stack

- Python 3.11+
- Existing pytest suite and Typer `CliRunner` tests.
- Existing community signal modules and constants.
- Existing documentation drift test helpers.
- No new runtime or development dependencies.

## Scope

This stage is a guardrail stage. It should add tests and small documentation
clarifications only. Production code should remain unchanged unless a test
reveals a real existing bug.

The stage will add:

- Parameterized lint coverage for every
  `PROHIBITED_COMMUNITY_SIGNAL_FIELDS` member across supported row envelopes:
  CSV, JSON top-level array, and JSON object with only `items`.
- Trap tests documenting that CSV extra cell values and JSON top-level envelope
  keys are not treated as row-level prohibited fields.
- A profile test that parses `recommended_commands` and asserts the command
  sequence, dry-run/import distinction, timestamp flag, and source-name
  alignment.
- A documentation drift test that confirms
  `docs/community-signal-import.md` lists the profile's recommended directory
  command names in the same relative order.
- A `community-candidates-dir --format xml` CLI parser test proving the command
  body is not entered.
- A short documentation note and changelog entry explaining that the profile
  JSON contains the exact producer-facing sequence, while prose examples may
  add `uv run` and temporary paths.

## Behavior

No user-facing command behavior changes are planned.

The new tests should preserve the existing boundaries:

- No scraping, crawling, browser automation, platform APIs, account login,
  cookies/sessions, source acquisition, scheduling, monitoring, media download,
  or connector code.
- No compliance-review workflow.
- No new dependency or network requirement.
- No generated config, data, report, dashboard, SQLite, cache, or token files.

## Implementation Plan

1. Add lint tests in `tests/test_community_signal_lint.py`.
2. Add producer profile command-sequence tests in
   `tests/test_community_signal_profile.py`.
3. Add documentation drift coverage in `tests/test_cli_docs.py`.
4. Add the missing `community-candidates-dir` invalid output-format parser test
   in `tests/test_cli.py`.
5. Update `docs/community-signal-import.md` and `CHANGELOG.md`.
6. Run targeted tests, full verification, Claude Code release review, commit,
   upload to GitHub, and confirm Actions.

## Testing Strategy

Targeted test commands:

```bash
uv run pytest tests/test_community_signal_lint.py tests/test_community_signal_profile.py tests/test_cli_docs.py::test_community_signal_import_doc_keeps_profile_recommended_command_order tests/test_cli.py::test_community_candidates_dir_invalid_output_format_does_not_enter_command_body -q
```

Full release verification:

```bash
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv sync --locked --dev --check
```

Use the existing release hygiene, package archive, and first-run smoke checks
before upload, matching the prior stage workflow.

## Out Of Scope

- New source/platform integrations for Instagram, TikTok, X, Xiaohongshu, or
  other services.
- Browser automation, login, cookies, sessions, platform APIs, scraping,
  crawling, media download, scheduling, monitoring, or watching.
- A compliance-review feature.
- Runtime behavior changes unless the new tests expose a genuine bug.

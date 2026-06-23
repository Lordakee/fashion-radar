# Stage 173 XPOZ Readiness Docs Discoverability Design

## Objective

Make `xpoz_mcp` discoverable in the user-facing `external-tool-readiness`
documentation and guard that discoverability with a docs parity test.

## Current Gap

The runtime registry already contains XPOZ:

- `src/fashion_radar/external_tool_adapters.py` defines `xpoz_mcp`.
- `src/fashion_radar/external_tool_readiness.py` has XPOZ readiness metadata.
- `tests/test_external_tool_adapters.py` and
  `tests/test_external_tool_readiness.py` already cover XPOZ behavior.
- `README.md` and `docs/cli-reference.md` adapter matrices already list
  `xpoz_mcp`.

The readiness prose still enumerates known free external/community tools as
Rednote MCP, Xiaohongshu crawler, Instaloader, TikTok-Api, yt-dlp, and
X/search exports. That makes XPOZ harder to discover in the readiness workflow,
especially for users preparing social/community exports from Instagram,
TikTok, X, Reddit, or other platforms through an external XPOZ workflow.

## Scope

In scope:

- Add XPOZ wording to the existing user-facing `external-tool-readiness` known
  tool lists.
- Use the careful wording `XPOZ MCP / Social Data API exports` so the docs
  describe sanitized local handoff exports, not a built-in connector.
- Add a copyable readiness command for `xpoz_mcp` in the CLI reference and
  upload checklist.
- Add one docs parity test in `tests/test_cli_docs.py` so XPOZ does not drift
  out of readiness docs again.

Out of scope:

- No changes to `src/fashion_radar/external_tool_adapters.py`.
- No changes to `src/fashion_radar/external_tool_readiness.py`.
- No changes to `scripts/check_first_run_smoke.py`.
- No changes to adapter metadata, readiness payload shapes, validators,
  command order, install hints, or mirror hints.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, MCP execution, API keys, login, cookies, monitoring, scheduling,
  demand proof, ranking, coverage verification, or compliance-review product
  feature.

## Architecture

Modify only documentation and documentation tests:

```text
tests/test_cli_docs.py
README.md
docs/cli-reference.md
docs/community-signal-import.md
docs/community-signal-quality.md
docs/source-boundaries.md
docs/architecture.md
docs/github-upload-checklist.md
CHANGELOG.md
```

The docs test should introduce a narrow tuple for the files that actually
enumerate readiness discoverability:

```python
EXTERNAL_TOOL_READINESS_XPOZ_DISCOVERABILITY_DOCS = (
    README,
    CLI_REFERENCE,
    ROOT / "docs" / "community-signal-import.md",
    ROOT / "docs" / "community-signal-quality.md",
    ROOT / "docs" / "source-boundaries.md",
    ROOT / "docs" / "architecture.md",
    UPLOAD_CHECKLIST,
    ROOT / "CHANGELOG.md",
)
```

Do not add `AGENTS.md` to that tuple. It is an internal future-work boundary
document and does not need to become a known-tool list.

Add a focused docs test that requires:

- `xpoz mcp`
- `social data api`
- `external-tool-readiness`
- `sanitized csv/json local file handoff`

in each discoverability doc, plus exact command checks for:

```text
fashion-radar external-tool-readiness --adapter xpoz_mcp --format json
"$tmp_env/venv/bin/fashion-radar" external-tool-readiness --adapter xpoz_mcp --format json
```

## Wording

Use this wording family when adding XPOZ to known-tool prose:

```text
Rednote MCP, Xiaohongshu crawler, Instaloader, TikTok-Api, yt-dlp,
X/search exports, and XPOZ MCP / Social Data API exports
```

Use this framing in new changelog text:

```text
XPOZ MCP / Social Data API external-tool-readiness discoverability for
sanitized CSV/JSON local file handoff rows from user-controlled
external/community tools
```

Avoid wording that says Fashion Radar runs XPOZ, calls XPOZ APIs, manages MCP
servers, stores API keys, validates access, verifies platform coverage, or
collects platform data.

## Tech Stack

- Markdown docs.
- Existing `tests/test_cli_docs.py` helpers: `_read(...)` and
  `_normalized_text(...)`.
- Pytest.
- `uv --no-config run --frozen`.
- Local opencode reviews with `zhipuai-coding-plan/glm-5.2 --variant max`.

## Implementation Method

Use TDD:

1. Add the XPOZ discoverability docs test before changing docs.
2. Run the new test and confirm it fails because readiness docs omit XPOZ.
3. Update the readiness prose and copyable command examples.
4. Re-run the focused docs tests and related XPOZ runtime tests.
5. Run opencode code review, release gate, opencode release review, commit, and
   push.

## Expected Behavior

- Users reading readiness docs can find XPOZ alongside the other external
  tool handoff options.
- Users can copy a `fashion-radar external-tool-readiness --adapter xpoz_mcp
  --format json` command from the CLI reference and upload checklist.
- The docs keep the existing local read-only boundary and do not imply built-in
  platform collection.

## Risks

- Overstating XPOZ could imply a built-in connector or API integration. The
  wording must describe local sanitized handoff exports only.
- Requiring XPOZ in every boundary document would be brittle. The test should
  cover user-facing docs and changelog discoverability, not internal future-work
  rules in `AGENTS.md`.
- Adding too many command examples can make docs noisy. The required copyable
  examples are limited to CLI reference and upload checklist.

## Verification

Focused:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_external_tool_readiness_docs_include_xpoz_discoverability -q
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_external_tool_readiness_docs_are_linked_and_bounded tests/test_cli_docs.py::test_external_tool_readiness_upload_checklist_help_loop_and_smoke tests/test_cli_docs.py::test_external_tool_readiness_docs_include_xpoz_discoverability -q
uv --no-config run --frozen pytest tests/test_cli_docs.py -q
uv --no-config run --frozen pytest tests/test_external_tool_readiness.py::test_readiness_upstream_command_mapping tests/test_external_tool_adapters.py::test_xpoz_mcp_adapter_has_expected_mapping_and_commands -q
uv --no-config run --frozen ruff check tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
```

Release gate:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader
```

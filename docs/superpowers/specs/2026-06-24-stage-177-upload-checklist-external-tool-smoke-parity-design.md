# Stage 177 Upload Checklist External-Tool Smoke Parity Design

## Objective

Keep `docs/github-upload-checklist.md` aligned with the first-run smoke
documentation by naming the local external-tool JSON contracts that the
first-run smoke already validates.

## Current Gap

Stage 174 updated `README.md` and `docs/first-run.md` to say the automated
first-run smoke validates:

- `external-tool-adapters --format json` across all eight adapters
- `external-tool-template --adapter rednote_mcp --format json`
- `external-tool-workflow --adapter rednote_mcp --format json`
- `external-tool-readiness --adapter rednote_mcp --format json`

Those docs also say the checks are command-output contract checks only and do
not run adapters or upstream external/community tools, call platform APIs, or
perform source acquisition.

The GitHub upload checklist still says only that the smoke validates sample
rows, matched starter entities, report content, trend deltas, empty untracked
candidates, and directory handoff dry-run counts. That statement is not false,
but it omits the external-tool JSON contract coverage that release operators
should know before pushing.

## Scope

In scope:

- Update `docs/github-upload-checklist.md` in the package smoke section.
- Extend the existing upload checklist smoke docs test in
  `tests/test_cli_docs.py` so the checklist must include the external-tool
  smoke claim fragments from `FIRST_RUN_EXTERNAL_TOOL_SMOKE_PHRASES`.
- Keep the checklist wording concise and checklist-appropriate.

Out of scope:

- No changes to `README.md` or `docs/first-run.md`.
- No changes to `scripts/check_first_run_smoke.py`.
- No changes to `tests/test_first_run_smoke.py`.
- No changes to runtime CLI commands, external-tool payloads, adapters,
  templates, workflows, readiness builders, install hints, mirror hints,
  dependency manifests, or `uv.lock`.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, MCP execution, login, cookies, monitoring, scheduling, demand proof,
  ranking, coverage verification, or compliance-review product feature.

## Architecture

Modify only:

```text
tests/test_cli_docs.py
docs/github-upload-checklist.md
```

The existing `FIRST_RUN_EXTERNAL_TOOL_SMOKE_PHRASES` tuple in
`tests/test_cli_docs.py` already contains the exact fragments used to guard the
README and detailed first-run guide. Reuse it in
`test_upload_checklist_documents_first_run_smoke_boundary` rather than
duplicating another phrase tuple.

Update the package smoke prose in `docs/github-upload-checklist.md` after the
existing sentence:

```text
The smoke also validates sample rows, matched starter entities, report content,
trend deltas, empty untracked candidates, and directory handoff dry-run counts.
```

Add one concise paragraph:

```text
The automated first-run smoke also validates local external-tool JSON
contracts: `external-tool-adapters --format json` across all eight adapters,
plus the `external-tool-template --adapter rednote_mcp --format json`,
`external-tool-workflow --adapter rednote_mcp --format json`, and
`external-tool-readiness --adapter rednote_mcp --format json` outputs generated
with the `rednote_mcp` adapter. These are command-output contract checks only;
they do not run adapters or upstream external/community tools, do not call
platform APIs, and do not perform source acquisition.
```

This mirrors README/first-run wording so all first-run smoke documentation
shares the same factual contract. It does not imply the smoke runs adapters or
calls upstream tools.

## Tech Stack

- Markdown docs.
- Pytest.
- Existing `tests/test_cli_docs.py` helpers and phrase tuple.
- `uv --no-config run --frozen`.
- Local opencode reviews with `zhipuai-coding-plan/glm-5.2 --variant max`.

## Implementation Method

Use TDD:

1. Extend `test_upload_checklist_documents_first_run_smoke_boundary` to require
   every phrase from `FIRST_RUN_EXTERNAL_TOOL_SMOKE_PHRASES`.
2. Run the focused test and confirm it fails against current
   `docs/github-upload-checklist.md`.
3. Update only the checklist smoke prose.
4. Re-run focused tests and lint checks.
5. Run opencode code review, release gate, opencode release review, commit, and
   push.

## Expected Behavior

- The upload checklist names the same four local external-tool JSON contract
  surfaces as README and `docs/first-run.md`.
- The upload checklist preserves the local/no-live-collection boundary.
- Runtime behavior remains unchanged.

## Risks

- The upload checklist can become dense. This node adds one concise paragraph
  in the package smoke section instead of duplicating broader onboarding prose.
- Overstating the claim could imply external tool execution. The wording must
  say command-output contract checks only.
- Changing smoke scripts or runtime adapter behavior would expand the node
  unnecessarily and is out of scope.

## Verification

Focused:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_upload_checklist_documents_first_run_smoke_boundary -q
uv --no-config run --frozen pytest tests/test_cli_docs.py -q -k "upload_checklist or first_run_smoke"
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

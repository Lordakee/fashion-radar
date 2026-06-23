# Stage 174 First-Run External Tool Smoke Claim Parity Design

## Objective

Make the first-run documentation accurately describe every external-tool JSON
contract surface that the automated first-run smoke already validates.

## Current Gap

`scripts/check_first_run_smoke.py` already validates four external-tool JSON
surfaces during the first-run smoke:

- `external-tool-adapters --format json`
- `external-tool-template --adapter rednote_mcp --format json`
- `external-tool-workflow --adapter rednote_mcp --format json`
- `external-tool-readiness --adapter rednote_mcp --format json`

The README first-run section and detailed first-run guide currently say only:

```text
The automated first-run smoke also validates the external-tool adapter registry
JSON contract from `external-tool-adapters --format json` across all eight
adapters.
```

That statement is not false, but it is incomplete. The first-run docs should
also mention the rednote `external-tool-template`, `external-tool-workflow`, and
`external-tool-readiness` JSON contracts already covered by the smoke.

## Scope

In scope:

- Add a focused docs test in `tests/test_first_run_docs.py` that guards the
  detailed first-run guide's external-tool smoke claim.
- Update the shared first-run docs assertion in `tests/test_cli_docs.py` so the
  README and detailed first-run guide stay aligned.
- Update the first-run smoke claim in `README.md` and `docs/first-run.md` so it
  names all four external-tool JSON contract surfaces already exercised by
  `scripts/check_first_run_smoke.py`.
- Preserve the existing local/no-live-collection boundary wording.

Out of scope:

- No changes to `scripts/check_first_run_smoke.py`.
- No changes to `tests/test_first_run_smoke.py`.
- No changes to runtime CLI commands, external-tool payloads, adapters,
  templates, workflows, readiness builders, install hints, or mirror hints.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, MCP execution, API keys, login, cookies, monitoring, scheduling, demand
  proof, ranking, coverage verification, or compliance-review product feature.

## Architecture

Modify only:

```text
README.md
docs/first-run.md
tests/test_first_run_docs.py
tests/test_cli_docs.py
```

The test should read the existing "Installed-Wheel Smoke" section because the
external-tool smoke paragraph lives there and describes both automated smoke
paths.

Add a test shaped like:

```python
def test_first_run_docs_name_external_tool_smoke_contracts() -> None:
    installed_smoke = _section(_read_first_run_doc(), "Installed-Wheel Smoke")
    normalized = _normalized(installed_smoke)

    for phrase in (
        "automated first-run smoke also validates local external-tool json contracts",
        "`external-tool-adapters --format json` across all eight adapters",
        "`external-tool-template --adapter rednote_mcp --format json`",
        "`external-tool-workflow --adapter rednote_mcp --format json`",
        "`external-tool-readiness --adapter rednote_mcp --format json`",
        "do not run adapters or upstream external/community tools",
        "do not call platform apis",
        "do not perform source acquisition",
    ):
        assert phrase in normalized
```

`tests/test_cli_docs.py` should replace the single old
`FIRST_RUN_EXTERNAL_ADAPTER_SMOKE_PHRASE` with a tuple of stable fragments, then
assert every fragment in both the README first-run section and the detailed
first-run guide. The tuple should include the adapter registry all-eight
coverage, the three rednote-only surfaces, and the local/no-platform boundary.

The new prose should keep the existing adapter registry coverage but add the
other surfaces:

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

## Tech Stack

- Markdown docs.
- Pytest.
- Existing `tests/test_first_run_docs.py` helpers: `_read_first_run_doc`,
  `_normalized`, and `_section`.
- `uv --no-config run --frozen`.
- Local opencode reviews with `zhipuai-coding-plan/glm-5.2 --variant max`.

## Implementation Method

Use TDD:

1. Add the first-run docs parity test before changing docs.
2. Run the new test and confirm it fails because the first-run guide does not
   yet mention the template/workflow/readiness JSON contracts or the
   no-external-tool boundary near the smoke claim.
3. Update `docs/first-run.md`.
4. Re-run the focused docs test and related first-run smoke checks.
5. Run opencode code review, release gate, opencode release review, commit, and
   push.

## Expected Behavior

- The README and detailed first-run guide name all four external-tool JSON contract
  surfaces already covered by the smoke.
- The docs stay accurate about scope: local command-output contract checks
  only, no adapter/upstream external/community tool execution, no platform APIs,
  and no source
  acquisition.
- Runtime smoke behavior remains unchanged.

## Risks

- Overstating the smoke claim could imply live external platform coverage. The
  wording must say JSON contract validation only.
- Understating the claim leaves first-run onboarding incomplete. The docs should
  name the template, workflow, and readiness contracts because the script
  already runs and validates them.
- Changing the runtime script would expand the node unnecessarily and is out of
  scope.

## Verification

Focused:

```bash
uv --no-config run --frozen pytest tests/test_first_run_docs.py::test_first_run_docs_name_external_tool_smoke_contracts -q
uv --no-config run --frozen pytest tests/test_first_run_docs.py -q
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_readme_documents_manual_sample_flow_and_automated_smoke_boundary tests/test_cli_docs.py::test_first_run_guide_documents_paths_outputs_dashboard_reset_and_boundaries -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -k "external_tool or deterministic_local_command_sequence" -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen ruff check tests/test_first_run_docs.py tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_first_run_docs.py tests/test_cli_docs.py
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

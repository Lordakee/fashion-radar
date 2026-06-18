# Stage 84 Readiness Installed Smoke Design

## Goal

Make the GitHub upload checklist match its own external-tool-readiness smoke
claim by including the installed-wheel `external-tool-readiness --format table`
command and pinning both installed-wheel table and JSON readiness commands in
the docs drift test.

## Scope

This is a documentation and test drift node only.

Modify:

- `docs/github-upload-checklist.md`
- `tests/test_cli_docs.py`
- Stage 84 spec/plan/review artifacts

Do not modify:

- Runtime code under `src/`
- Dependency manifests or `uv.lock`
- CI workflows
- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`

## Current Gap

The upload checklist readiness section says the CLI reference and installed
wheel smoke include both:

- `fashion-radar external-tool-readiness --adapter instaloader --format table`
- `fashion-radar external-tool-readiness --adapter instaloader --format json`

The installed-wheel smoke block currently includes only the JSON
`instaloader` readiness command plus a `rednote_mcp` JSON command. The docs
test only pins the JSON `instaloader` command and a loose `rednote_mcp`
substring, so it would not catch the missing installed-wheel table smoke.

## Design

Add this command to the installed-wheel smoke block immediately after
`"$tmp_env/venv/bin/fashion-radar" external-tool-readiness --help` and before
the existing JSON readiness command:

```bash
"$tmp_env/venv/bin/fashion-radar" external-tool-readiness --adapter instaloader --format table
```

Update `test_external_tool_readiness_upload_checklist_help_loop_and_smoke` to
assert the exact installed-path table and JSON commands:

```python
for format_name in ("table", "json"):
    assert (
        '"$tmp_env/venv/bin/fashion-radar" external-tool-readiness '
        f"--adapter instaloader --format {format_name}"
    ) in checklist
```

Keep the existing help-loop assertion, `rednote_mcp` assertion, and
`scripts/check_first_run_smoke.py` assertion.

## Boundaries

This does not add source acquisition, platform connectors, scraping, browser
automation, platform APIs, login/cookie/session/token behavior, media
downloads, monitoring, scheduling, demand proof, ranking, coverage
verification, or compliance-review product features.

## Verification

Run focused docs checks:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_external_tool_readiness_upload_checklist_help_loop_and_smoke -q
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_external_tool_readiness_docs_are_linked_and_bounded -q
uv --no-config run --frozen pytest tests/test_cli_docs.py -q
uv --no-config run --frozen ruff check tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
git diff --check -- docs/github-upload-checklist.md tests/test_cli_docs.py
```

Before completion, run full release verification and confirm `uv.lock` remains
mirror-free and unchanged.

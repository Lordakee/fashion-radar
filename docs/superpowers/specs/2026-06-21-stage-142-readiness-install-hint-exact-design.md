# Stage 142 Readiness Install Hint Exactness Design

## Goal

Harden the first-run smoke validator for `external-tool-readiness` so the Rednote MCP `install_hint` is checked as an exact expected string instead of substring membership.

## Background

`validate_external_tool_readiness()` currently validates the readiness check's `install_hint` by requiring these substrings:

- `registry.npmmirror.com`
- `npm install -g rednote-mcp`

That catches missing pieces, but it would accept command-like text that wraps the expected hint with extra shell operations, duplicated commands, or unrelated instructions.

The runtime builder already has a single source of truth for the Rednote MCP install hint:

```python
"npm config set registry https://registry.npmmirror.com && npm install -g rednote-mcp"
```

The test fixture already mirrors that string and is covered by `test_external_tool_readiness_payload_matches_real_rednote_readiness()`. Stage 142 tightens the smoke validator to require the same exact string.

## Scope

Modify only:

- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- Stage 142 plan/review artifacts

Do not change runtime builders or readiness payload output.

## Design

Add a smoke-check constant near other expected external-tool values:

```python
EXPECTED_EXTERNAL_TOOL_READINESS_INSTALL_HINT = (
    "npm config set registry https://registry.npmmirror.com && npm install -g rednote-mcp"
)
```

Replace the substring loop in `validate_external_tool_readiness()`:

```python
for expected in ("registry.npmmirror.com", "npm install -g rednote-mcp"):
    if expected not in install_hint:
        raise SmokeError(f"{command_name} check install_hint missing {expected!r}")
```

with:

```python
assert_equal(
    f"{command_name} check install_hint",
    install_hint,
    EXPECTED_EXTERNAL_TOOL_READINESS_INSTALL_HINT,
)
```

This preserves the existing empty/non-string guard first, so missing hints still produce the existing population error before exact comparison.

## TDD Strategy

Add a RED test that preserves the two old substrings but changes the full install hint:

```python
def test_validate_external_tool_readiness_rejects_install_hint_extra_shell_text() -> None:
    payload = external_tool_readiness_payload()
    checks = payload["checks"]
    assert isinstance(checks, list)
    checks[0]["install_hint"] = (
        "npm install -g rednote-mcp using registry.npmmirror.com; "
        "do not set the npm registry first"
    )

    with pytest.raises(smoke.SmokeError, match="install_hint"):
        smoke.validate_external_tool_readiness("external-tool-readiness", payload)
```

This should fail before implementation because the old substring checks accept it. After exact equality, it should pass.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_readiness"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
git diff --check
```

Release gate:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
if rg -n 'ghp_[A-Za-z0-9]+' .; then echo 'GitHub token pattern found in worktree' >&2; exit 1; fi
if git config --get-all http.https://github.com/.extraheader; then echo 'Persistent GitHub auth header configured' >&2; exit 1; fi
```

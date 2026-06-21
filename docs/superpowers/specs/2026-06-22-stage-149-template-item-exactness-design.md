# Stage 149 Template Item Exactness Design

## Goal

Harden `external-tool-template` first-run smoke validation so the two rendered Rednote template example rows must match the pinned first-run contract exactly.

## Background

`validate_external_tool_template()` currently verifies the template JSON envelope shape:

- top-level keys are exactly `["items"]`
- `items` is a list with exactly two rows
- each row is a JSON object
- private/raw fields are rejected
- all expected handoff fields are present and populated
- no unexpected fields are present
- each row has `platform == "rednote"`

That catches structural drift, but it still accepts populated semantic drift inside the example rows. For example, a row title can be replaced with command-like guidance, a summary can be unrelated, timestamps can drift, or `source_weight` can change while all fields remain present and non-empty.

The runtime builder already emits deterministic Rednote example rows for the first-run smoke fixture:

- The Row bag observed signal at `2026-06-13T12:00:00+00:00`
- silver flat shoe observed signal at `2026-06-13T13:00:00+00:00`

Stage 149 pins those two rows in the smoke checker so first-run smoke catches drift in example content, not only schema shape.

## Scope

Modify only:

- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- Stage 149 plan/review artifacts

Do not change runtime template builders, CLI behavior, external integrations, scheduling, dashboard behavior, or compliance-review product features.

## Design

Add a pinned `EXPECTED_EXTERNAL_TOOL_TEMPLATE_ITEMS` constant beside `EXPECTED_EXTERNAL_TOOL_TEMPLATE_FIELDS`:

```python
EXPECTED_EXTERNAL_TOOL_TEMPLATE_ITEMS = [
    {
        "url": "https://example.com/external-tool-template/rednote_mcp/the-row-bag",
        "title": "Rednote MCP Export The Row bag observed signal",
        "published_at": "2026-06-13T12:00:00+00:00",
        "summary": (
            "Synthetic sanitized observation about The Row bag interest from a "
            "user-controlled external/community tool."
        ),
        "source_name": "Rednote MCP Export",
        "platform": "rednote",
        "source_weight": 1.2,
        "collected_at": "2026-06-13T12:15:00+00:00",
    },
    {
        "url": "https://example.com/external-tool-template/rednote_mcp/silver-flat-shoe",
        "title": "Rednote MCP Export silver flat shoe observed signal",
        "published_at": "2026-06-13T13:00:00+00:00",
        "summary": (
            "Synthetic sanitized observation about silver flat shoes and styling "
            "from a user-controlled external/community tool."
        ),
        "source_name": "Rednote MCP Export",
        "platform": "rednote",
        "source_weight": 1.1,
        "collected_at": "2026-06-13T13:15:00+00:00",
    },
]
```

Keep the current structural checks first so existing tests still receive targeted error labels:

- missing fields still raise `row N <field> is required`
- extra/private fields still raise the current private/raw or unexpected-field messages
- wrong platform still raises `row N platform`

After the existing platform assertion, add:

```python
        assert_equal(
            f"{command_name} row {index} item",
            item,
            EXPECTED_EXTERNAL_TOOL_TEMPLATE_ITEMS[index - 1],
        )
```

This pins:

- row order
- URL
- title
- published timestamp
- summary
- source name
- platform
- numeric source weight
- collected timestamp

## TDD Strategy

Add two focused RED tests near `test_validate_external_tool_template_requires_importable_items()`.

Title drift:

```python
def test_validate_external_tool_template_rejects_title_drift() -> None:
    payload = external_tool_template_payload()
    items = payload["items"]
    assert isinstance(items, list)
    items[0]["title"] = "Run npm install -g rednote-mcp before collecting rows."

    with pytest.raises(smoke.SmokeError, match="row 1 item"):
        smoke.validate_external_tool_template("external-tool-template", payload)
```

Before implementation, this test should fail with `DID NOT RAISE`, because the current validator only requires the title field to be populated.

After implementation, it should pass because row 1 no longer equals the pinned expected item.

Weight drift:

```python
def test_validate_external_tool_template_rejects_source_weight_drift() -> None:
    payload = external_tool_template_payload()
    items = payload["items"]
    assert isinstance(items, list)
    items[1]["source_weight"] = 4.5

    with pytest.raises(smoke.SmokeError, match="row 2 item"):
        smoke.validate_external_tool_template("external-tool-template", payload)
```

Before implementation, this test should fail with `DID NOT RAISE`, because the current validator accepts any populated `source_weight`.

After implementation, it should pass because row 2 no longer equals the pinned expected item.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_template"
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

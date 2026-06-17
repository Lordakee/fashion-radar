# Stage 72 Adapter JSON Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Broaden the `external-tool-adapters --format json` CLI contract test so it validates every registered adapter.

**Architecture:** This is a test-only hardening stage. The existing CLI test will loop over all serialized adapters and assert stable metadata, field mappings, command order, and readiness command flags. Runtime adapter code should remain unchanged unless the broader test exposes real drift.

**Tech Stack:** Python 3.11, pytest, Typer `CliRunner`, `json`, `shlex`, ruff, uv.

---

## File Map

- Modify `tests/test_cli.py`
  - Extend `test_external_tool_adapters_command_prints_json`.
- Create review artifacts:
  - `docs/reviews/opencode-stage-72-plan-review-prompt.md`
  - `docs/reviews/opencode-stage-72-plan-review.md`
  - `docs/reviews/opencode-stage-72-code-review-prompt.md`
  - `docs/reviews/opencode-stage-72-code-review.md`

## Task 1: Broaden The CLI JSON Contract Test

**Files:**
- Modify: `tests/test_cli.py`

- [x] **Step 1: Run the current baseline test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli.py::test_external_tool_adapters_command_prints_json -q
```

Expected: pass.

- [x] **Step 2: Add expected adapter metadata**

Inside `test_external_tool_adapters_command_prints_json`, after parsing
`payload`, add:

```python
    expected_adapters = {
        "rednote_mcp": ("rednote", "Rednote MCP Export", "json", "*.json"),
        "xiaohongshu_crawler": (
            "xiaohongshu",
            "Xiaohongshu Crawler Export",
            "csv",
            "*.csv",
        ),
        "instaloader": ("instagram", "Instaloader Export", "json", "*.json"),
        "tiktok_api": ("tiktok", "TikTok-Api Export", "json", "*.json"),
        "yt_dlp": ("media", "yt-dlp Metadata Export", "json", "*.json"),
        "x_search_export": ("x", "X Search Export", "csv", "*.csv"),
        "generic_community_export": (
            "community",
            "Generic Community Export",
            "csv",
            "*.csv",
        ),
    }
```

- [x] **Step 3: Pin shared JSON shape and field mappings**

Replace the single first-adapter field mapping assertion with:

```python
    adapters = payload["adapters"]
    expected_field_mappings = adapters[0]["field_mappings"]
    config_dirs: list[str] = []
    data_dirs: list[str] = []
    assert expected_field_mappings[0] == {
        "field": "url",
        "required": True,
        "note": "Stable source URL or local reference URL for the observed item.",
    }
    expected_adapter_keys = [
        "id",
        "display_name",
        "platform_label",
        "suggested_source_name",
        "recommended_input_format",
        "recommended_pattern",
        "suggested_export_directory",
        "description",
        "upstream_tool_examples",
        "field_mappings",
        "recommended_commands",
        "boundaries",
    ]
```

- [x] **Step 4: Add command sequence helper assertions**

Inside the test, add the expected command sequence:

```python
    expected_command_names = [
        "community-signal-profile",
        "external-tool-readiness",
        "community-handoff-manifest",
        "community-handoff-workflow",
        "community-signal-lint-dir",
        "community-handoff-check-dir",
        "import-signals-dir",
        "import-signals-dir",
        "imported-review-workflow",
    ]
```

- [x] **Step 5: Add a flag helper and loop over every adapter**

Add a helper before the adapter loop so it does not close over loop-local
variables:

```python
    def flag_value(parts: list[str], flag: str) -> str:
        index = parts.index(flag)
        assert index + 1 < len(parts)
        value = parts[index + 1]
        assert value
        assert not value.startswith("--")
        return value
```

Then add a loop over `adapters`:

```python
    for adapter in adapters:
        adapter_id = adapter["id"]
        platform_label, source_name, input_format, pattern = expected_adapters[adapter_id]
        assert list(adapter) == expected_adapter_keys
        assert adapter["display_name"] == source_name
        assert adapter["platform_label"] == platform_label
        assert adapter["suggested_source_name"] == source_name
        assert adapter["recommended_input_format"] == input_format
        assert adapter["recommended_pattern"] == pattern
        assert adapter["suggested_export_directory"] == "exports"
        assert adapter["upstream_tool_examples"]
        assert adapter["field_mappings"] == expected_field_mappings

        commands = adapter["recommended_commands"]
        command_parts = [shlex.split(command) for command in commands]
        assert [parts[:2] for parts in command_parts] == [
            ["fashion-radar", name] for name in expected_command_names
        ]
        readiness_parts = command_parts[1]

        assert readiness_parts[:2] == ["fashion-radar", "external-tool-readiness"]
        assert flag_value(readiness_parts, "--adapter") == adapter_id
        assert flag_value(readiness_parts, "--directory") == "exports"
        config_dirs.append(flag_value(readiness_parts, "--config-dir"))
        data_dirs.append(flag_value(readiness_parts, "--data-dir"))
        assert flag_value(readiness_parts, "--as-of") == "2026-06-13T12:00:00+00:00"
        assert flag_value(readiness_parts, "--input-format") == input_format
        assert flag_value(readiness_parts, "--pattern") == pattern
        assert flag_value(readiness_parts, "--source-name") == source_name
        assert flag_value(readiness_parts, "--format") == "table"

    assert len(set(config_dirs)) == 1
    assert len(set(data_dirs)) == 1
```

Delete the old first-adapter-only `commands`, `readiness_command`,
`readiness_parts`, single-argument `flag_value`, and `rednote_mcp` readiness
assertion block after adding the loop.

- [x] **Step 6: Run targeted and nearby tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli.py::test_external_tool_adapters_command_prints_json -q
uv --no-config run --frozen pytest tests/test_cli.py -q -k "external_tool_adapters or external_tool_template or external_tool_workflow or external_tool_readiness"
```

Expected: pass.

## Task 2: Review, Verification, And Commit

**Files:**
- Create: `docs/reviews/opencode-stage-72-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-72-code-review.md`
- Include Stage 72 spec/plan/review artifacts in commit.

- [x] **Step 1: Run file and full verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli.py -q
uv --no-config run --frozen ruff check tests/test_cli.py
uv --no-config run --frozen ruff format --check tests/test_cli.py
uv --no-config run --frozen python scripts/check_release_hygiene.py
git diff --check
uv --no-config run --frozen pytest
```

Expected: pass.

- [x] **Step 2: Request opencode code review**

Create `docs/reviews/opencode-stage-72-code-review-prompt.md` with the Stage 72
goal, touched files, implementation summary, and verification results. Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-72-code-review-prompt.md)" > docs/reviews/opencode-stage-72-code-review.md
```

Fix Critical/Important findings before proceeding.

- [x] **Step 3: Commit**

Run:

```bash
git add tests/test_cli.py docs/superpowers/specs/2026-06-18-stage-72-adapter-json-contract-design.md docs/superpowers/plans/2026-06-18-stage-72-adapter-json-contract-plan.md docs/reviews/opencode-stage-72-plan-review-prompt.md docs/reviews/opencode-stage-72-plan-review.md docs/reviews/opencode-stage-72-code-review-prompt.md docs/reviews/opencode-stage-72-code-review.md
git commit -m "Harden adapter JSON contract coverage"
```

- [ ] **Step 4: Publish and verify CI**

Use the GitHub Git Data API path if normal git HTTPS push remains unreliable.
Verify remote `main`, local `origin/main`, release hygiene, credential-free git
config, and GitHub Actions CI success.

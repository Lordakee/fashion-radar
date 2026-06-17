# Stage 73 Adapter Smoke Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend first-run smoke validation of `external-tool-adapters --format json` from the first adapter to all seven adapters.

**Architecture:** This is a smoke/test hardening stage. The validator keeps using static JSON payload checks and shell parsing; runtime CLI and adapter registry code remain unchanged.

**Tech Stack:** Python 3.11, pytest, `shlex`, uv, ruff.

**Review Protocol Note:** Per the current user instruction for this stage,
local review is performed with `opencode run --model
zhipuai-coding-plan/glm-5.2 --variant max`. This stage-local review path does
not change the repository's broader review protocol documents.

---

## File Map

- Modify `scripts/check_first_run_smoke.py`
  - Add expected adapter map.
  - Refactor `validate_external_tool_adapters` to loop all adapters.
- Modify `tests/test_first_run_smoke.py`
  - Expand `external_tool_adapters_payload` to all seven adapters.
  - Update negative tests to prove later adapters are validated.
- Create review artifacts:
  - `docs/reviews/opencode-stage-73-plan-review-prompt.md`
  - `docs/reviews/opencode-stage-73-plan-review.md`
  - `docs/reviews/opencode-stage-73-code-review-prompt.md`
  - `docs/reviews/opencode-stage-73-code-review.md`

## Task 1: Broaden First-Run Smoke Adapter Validation

**Files:**
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_first_run_smoke.py`

- [x] **Step 1: Run the current baseline test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_validate_external_tool_adapters_requires_print_only_registry_contract -q
```

Expected: pass before changes.

- [x] **Step 2: Add the expected adapter map**

In `scripts/check_first_run_smoke.py`, near the other expected external-tool
constants, add:

```python
# Pinned independently from the runtime registry so first-run smoke catches
# adapter registry drift instead of importing the code under test.
EXPECTED_EXTERNAL_TOOL_ADAPTERS = {
    "rednote_mcp": ("rednote", "json", "*.json", "Rednote MCP Export"),
    "xiaohongshu_crawler": ("xiaohongshu", "csv", "*.csv", "Xiaohongshu Crawler Export"),
    "instaloader": ("instagram", "json", "*.json", "Instaloader Export"),
    "tiktok_api": ("tiktok", "json", "*.json", "TikTok-Api Export"),
    "yt_dlp": ("media", "json", "*.json", "yt-dlp Metadata Export"),
    "x_search_export": ("x", "csv", "*.csv", "X Search Export"),
    "generic_community_export": ("community", "csv", "*.csv", "Generic Community Export"),
}
```

Also add the expected recommended command name sequence:

```python
EXPECTED_EXTERNAL_TOOL_COMMAND_NAMES = (
    "community-signal-profile",
    "external-tool-readiness",
    "community-handoff-manifest",
    "community-handoff-workflow",
    "community-signal-lint-dir",
    "community-handoff-check-dir",
    "import-signals-dir",
    "import-signals-dir",
    "imported-review-workflow",
)
```

- [x] **Step 3: Refactor readiness flag helper**

Inside `validate_external_tool_adapters`, replace the first-adapter-only
`required_readiness_value(flag)` helper with:

```python
    def required_readiness_value(parts: list[str], adapter_id: str, flag: str) -> str:
        if flag not in parts:
            raise SmokeError(f"{command_name} {adapter_id} readiness command missing {flag!r}")
        index = parts.index(flag)
        if index + 1 >= len(parts):
            raise SmokeError(
                f"{command_name} {adapter_id} readiness command missing value for {flag!r}"
            )
        value = parts[index + 1]
        if not value or value.startswith("--"):
            raise SmokeError(
                f"{command_name} {adapter_id} readiness command missing value for {flag!r}"
            )
        return value
```

- [x] **Step 4: Loop all adapters in the validator**

Keep the existing prelude: payload must be a dict, `contract_version` must be
`external-tool-adapters/v1`, `execution_mode` must be `print_only`, and
`adapters` must be a non-empty list. Replace only the first-adapter-only block
beginning with `first_adapter = adapters[0]`.

Use an all-adapter loop that:

- Asserts exact adapter id order.
- Checks each adapter's public metadata fields against the pinned adapter map:
  `display_name`, `platform_label`, `suggested_source_name`,
  `recommended_input_format`, `recommended_pattern`, and
  `suggested_export_directory`.
- Parses every recommended command with `shlex.split(...)`.
- Asserts the exact nine `fashion-radar <command>` prefixes in order.
- Requires exactly one `external-tool-readiness` command per adapter.
- Checks the readiness command flags shown below.

The core loop shape is:

```python
    adapter_ids: list[str] = []
    for index, adapter in enumerate(adapters, start=1):
        if not isinstance(adapter, dict):
            raise SmokeError(f"{command_name} adapter {index} must be a JSON object")
        adapter_id = str(adapter.get("id", ""))
        adapter_ids.append(adapter_id)

    assert_equal(
        f"{command_name} adapter ids",
        adapter_ids,
        list(EXPECTED_EXTERNAL_TOOL_ADAPTERS),
    )

    for adapter in adapters:
        adapter_id = str(adapter["id"])
        platform_label, input_format, pattern, source_name = EXPECTED_EXTERNAL_TOOL_ADAPTERS[
            adapter_id
        ]
        assert_equal(f"{command_name} {adapter_id} display_name", adapter.get("display_name"), source_name)
        assert_equal(f"{command_name} {adapter_id} platform_label", adapter.get("platform_label"), platform_label)
        assert_equal(f"{command_name} {adapter_id} suggested_source_name", adapter.get("suggested_source_name"), source_name)
        assert_equal(f"{command_name} {adapter_id} recommended_input_format", adapter.get("recommended_input_format"), input_format)
        assert_equal(f"{command_name} {adapter_id} recommended_pattern", adapter.get("recommended_pattern"), pattern)
        assert_equal(f"{command_name} {adapter_id} suggested_export_directory", adapter.get("suggested_export_directory"), "exports")
        recommended_commands = adapter.get("recommended_commands")
        if not isinstance(recommended_commands, list):
            raise SmokeError(f"{command_name} {adapter_id} recommended_commands must be a list")
        command_parts = [shlex.split(str(command)) for command in recommended_commands]
        readiness_commands = [
            parts
            for parts in command_parts
            if parts[:2] == ["fashion-radar", "external-tool-readiness"]
        ]
        if not readiness_commands:
            raise SmokeError(
                f"{command_name} {adapter_id} missing external-tool-readiness command"
            )
        if len(readiness_commands) != 1:
            raise SmokeError(
                f"{command_name} {adapter_id} must contain exactly one "
                "external-tool-readiness command"
            )
        assert_equal(
            f"{command_name} {adapter_id} command prefixes",
            [parts[:2] for parts in command_parts],
            [
                ["fashion-radar", expected_name]
                for expected_name in EXPECTED_EXTERNAL_TOOL_COMMAND_NAMES
            ],
        )
        readiness_parts = readiness_commands[0]
        assert_equal(
            f"{command_name} {adapter_id} readiness command prefix",
            readiness_parts[:2],
            ["fashion-radar", "external-tool-readiness"],
        )
        assert_equal(
            f"{command_name} {adapter_id} readiness adapter",
            required_readiness_value(readiness_parts, adapter_id, "--adapter"),
            adapter_id,
        )
        assert_equal(
            f"{command_name} {adapter_id} readiness directory",
            required_readiness_value(readiness_parts, adapter_id, "--directory"),
            "exports",
        )
        required_readiness_value(readiness_parts, adapter_id, "--config-dir")
        required_readiness_value(readiness_parts, adapter_id, "--data-dir")
        required_readiness_value(readiness_parts, adapter_id, "--as-of")
        assert_equal(
            f"{command_name} {adapter_id} readiness input_format",
            required_readiness_value(readiness_parts, adapter_id, "--input-format"),
            input_format,
        )
        assert_equal(
            f"{command_name} {adapter_id} readiness pattern",
            required_readiness_value(readiness_parts, adapter_id, "--pattern"),
            pattern,
        )
        assert_equal(
            f"{command_name} {adapter_id} readiness source_name",
            required_readiness_value(readiness_parts, adapter_id, "--source-name"),
            source_name,
        )
        assert_equal(
            f"{command_name} {adapter_id} readiness output format",
            required_readiness_value(readiness_parts, adapter_id, "--format"),
            "table",
        )
```

- [x] **Step 5: Expand the test fixture to all seven adapters**

In `tests/test_first_run_smoke.py::external_tool_adapters_payload`, replace the
single adapter list with seven registry-like adapter dictionaries. Add a test
module helper table:

```python
EXTERNAL_TOOL_ADAPTER_CASES = (
    ("rednote_mcp", "rednote", "json", "*.json", "Rednote MCP Export"),
    ("xiaohongshu_crawler", "xiaohongshu", "csv", "*.csv", "Xiaohongshu Crawler Export"),
    ("instaloader", "instagram", "json", "*.json", "Instaloader Export"),
    ("tiktok_api", "tiktok", "json", "*.json", "TikTok-Api Export"),
    ("yt_dlp", "media", "json", "*.json", "yt-dlp Metadata Export"),
    ("x_search_export", "x", "csv", "*.csv", "X Search Export"),
    ("generic_community_export", "community", "csv", "*.csv", "Generic Community Export"),
)
```

Add a command helper that uses `shlex.join(...)` so glob patterns and multi-word
`--source-name` values stay shell-parseable:

```python
def external_tool_command(*parts: str) -> str:
    return shlex.join(("fashion-radar", *parts))
```

Add `import shlex` at the top of `tests/test_first_run_smoke.py` for this
helper.

Each fixture adapter should include at least:

- `id`
- `display_name`
- `platform_label`
- `suggested_source_name`
- `recommended_input_format`
- `recommended_pattern`
- `suggested_export_directory`
- `field_mappings`
- `recommended_commands`
- `boundaries`

The `recommended_commands` list should use the same nine command names as the
real registry:

```python
(
    "community-signal-profile",
    "external-tool-readiness",
    "community-handoff-manifest",
    "community-handoff-workflow",
    "community-signal-lint-dir",
    "community-handoff-check-dir",
    "import-signals-dir",
    "import-signals-dir",
    "imported-review-workflow",
)
```

Only the `external-tool-readiness` command needs full flag details for this
stage; the other eight commands may be minimal parseable strings with the right
`fashion-radar <command-name>` prefix.

- [x] **Step 6: Update negative tests for all-adapter behavior**

In `test_validate_external_tool_adapters_requires_print_only_registry_contract`:

- Change the wrong-id assertion to expect `"adapter ids"` instead of
  `"first adapter id"`.
- Add a reorder negative case that swaps two valid adapter entries and expects
  `"adapter ids"`.
- Mutate at least one later adapter, for example `adapters[1]["id"] =
  "unexpected_adapter"`.
- Add a metadata drift negative case, for example mutate
  `adapters[1]["platform_label"]` and expect an adapter-specific
  `platform_label` error.
- Change at least one `recommended_commands` negative case to mutate a later
  adapter, for example `adapters[1].pop("recommended_commands")`.
- Add a recommended command prefix negative case and a duplicate readiness
  command negative case.
- Add one later-adapter readiness-value drift, for example mutate
  `adapters[1]["recommended_commands"][1]` so `--input-format json` is present
  where `xiaohongshu_crawler` expects `csv`, and assert the error mentions
  `xiaohongshu_crawler readiness input_format`.
- Keep existing missing flag, malformed shell, missing value, and invalid
  `--format` cases valid; they may continue to use `adapters[0]` unless a later
  adapter mutation is clearer.

- [x] **Step 7: Run targeted tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_validate_external_tool_adapters_requires_print_only_registry_contract -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_run_first_run_flow_uses_deterministic_local_command_sequence -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_adapters"
uv --no-config run --frozen pytest tests/test_cli.py::test_external_tool_adapters_command_prints_json tests/test_first_run_smoke.py::test_validate_external_tool_adapters_requires_print_only_registry_contract -q
```

Expected: pass.

## Task 2: Review, Verification, And Commit

**Files:**
- Create: `docs/reviews/opencode-stage-73-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-73-code-review.md`
- Include Stage 73 spec/plan/review artifacts in commit.

- [x] **Step 1: Run full local verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen python scripts/check_release_hygiene.py
git diff --check
uv --no-config run --frozen pytest
```

Expected: pass.

- [x] **Step 2: Request opencode code review**

Create `docs/reviews/opencode-stage-73-code-review-prompt.md` with the Stage 73
goal, touched files, implementation summary, and verification results. Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-73-code-review-prompt.md)" > docs/reviews/opencode-stage-73-code-review.md
```

Fix Critical/Important findings before proceeding.

- [x] **Step 3: Commit**

Run:

```bash
git add scripts/check_first_run_smoke.py tests/test_first_run_smoke.py docs/superpowers/specs/2026-06-18-stage-73-adapter-smoke-contract-design.md docs/superpowers/plans/2026-06-18-stage-73-adapter-smoke-contract-plan.md docs/reviews/opencode-stage-73-plan-review-prompt.md docs/reviews/opencode-stage-73-plan-review.md docs/reviews/opencode-stage-73-code-review-prompt.md docs/reviews/opencode-stage-73-code-review.md
git commit -m "Harden first-run adapter smoke contract"
```

- [ ] **Step 4: Publish and verify CI**

Use the GitHub Git Data API path if normal git HTTPS push remains unreliable.
Verify remote `main`, local `origin/main`, release hygiene, credential-free git
config, and GitHub Actions CI success.

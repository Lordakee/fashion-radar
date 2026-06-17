# Stage 76 Adapter Smoke Full Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend first-run smoke validation of
`external-tool-adapters --format json` to cover adapter descriptions, upstream
examples, field mappings, full recommended command strings, boundaries, and
JSON key order.

**Architecture:** Smoke/test hardening only. The smoke script keeps static
expected values pinned independently from the runtime registry, still parses
commands with `shlex`, and never runs generated recommended commands. Runtime
CLI code remains unchanged. The smoke command environment sets
`FASHION_RADAR_CONFIG_DIR=configs` and `FASHION_RADAR_DATA_DIR=data` so the
print-only adapter registry emits deterministic handoff paths without changing
the `run_first_run_flow()` command sequence.

**Tech Stack:** Python 3.11, pytest, uv, ruff.

**Review Protocol Note:** Per the current user instruction for this stage,
local review is performed with `opencode run --model
zhipuai-coding-plan/glm-5.2 --variant max`. This stage-local review path does
not change the repository's broader review protocol documents.

---

## File Map

- Modify `tests/test_first_run_smoke.py`
  - Add a command-environment test for deterministic adapter registry defaults.
  - Add helper-driven parameterized negative tests for the currently unvalidated
    adapter registry contract fields.
  - Add a helper-parity test for the smoke script's expected command helper.
- Modify `scripts/check_first_run_smoke.py`
  - Set smoke-local config/data env vars in `command_environment`.
  - Add static expected full-contract metadata and boundary constants.
  - Add a full recommended-command helper based on `shlex.join`.
  - Extend `validate_external_tool_adapters` to check the full static contract.
- Create review artifacts:
  - `docs/reviews/opencode-stage-76-plan-review-prompt.md`
  - `docs/reviews/opencode-stage-76-plan-review.md`
  - `docs/reviews/opencode-stage-76-code-review-prompt.md`
  - `docs/reviews/opencode-stage-76-code-review.md`

## Task 1: Add Full-Contract Negative Tests

**Files:**
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add command-environment red test**

Add this test after the existing command environment tests:

```python
def test_command_environment_sets_deterministic_adapter_registry_dirs(
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)

    source_env = smoke.command_environment(context)
    installed_env = smoke.command_environment(context, source_checkout=False)

    assert source_env["FASHION_RADAR_CONFIG_DIR"] == "configs"
    assert source_env["FASHION_RADAR_DATA_DIR"] == "data"
    assert installed_env["FASHION_RADAR_CONFIG_DIR"] == "configs"
    assert installed_env["FASHION_RADAR_DATA_DIR"] == "data"
```

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_command_environment_sets_deterministic_adapter_registry_dirs -q
```

Expected before implementation: fail with `KeyError` because
`command_environment` does not set those env vars yet.

- [ ] **Step 2: Add mutation helpers**

Add these helpers after `external_tool_adapter_entries`:

```python
def external_tool_adapter_entry(
    payload: dict[str, object],
    adapter_id: str,
) -> dict[str, object]:
    for adapter in external_tool_adapter_entries(payload):
        if adapter.get("id") == adapter_id:
            return adapter
    raise AssertionError(f"missing adapter {adapter_id}")


def assert_external_tool_adapter_contract_drift(
    payload: dict[str, object],
    match: str,
) -> None:
    with pytest.raises(smoke.SmokeError, match=match):
        smoke.validate_external_tool_adapters("external-tool-adapters", payload)
```

- [ ] **Step 3: Add parameterized mutation cases**

Add these mutation helpers after the assertion helper:

```python
def add_external_tool_registry_extra_key(payload: dict[str, object]) -> None:
    payload["runs_adapters"] = False


def remove_external_tool_registry_boundary(payload: dict[str, object]) -> None:
    boundaries = payload["boundaries"]
    assert isinstance(boundaries, list)
    payload["boundaries"] = boundaries[:-1]


def add_external_tool_adapter_extra_key(payload: dict[str, object]) -> None:
    adapter = external_tool_adapter_entry(payload, "rednote_mcp")
    adapter["runs_adapter"] = False


def remove_external_tool_adapter_key(payload: dict[str, object]) -> None:
    adapter = external_tool_adapter_entry(payload, "rednote_mcp")
    adapter.pop("description")


def drift_external_tool_later_adapter_description(payload: dict[str, object]) -> None:
    adapter = external_tool_adapter_entry(payload, "xiaohongshu_crawler")
    adapter["description"] = "Unexpected crawler description."


def drift_external_tool_upstream_examples(payload: dict[str, object]) -> None:
    adapter = external_tool_adapter_entry(payload, "x_search_export")
    adapter["upstream_tool_examples"] = ["other export"]


def drift_external_tool_field_mapping_required(payload: dict[str, object]) -> None:
    adapter = external_tool_adapter_entry(payload, "rednote_mcp")
    field_mappings = adapter["field_mappings"]
    assert isinstance(field_mappings, list)
    first_mapping = field_mappings[0]
    assert isinstance(first_mapping, dict)
    first_mapping["required"] = False


def drift_external_tool_field_mapping_note(payload: dict[str, object]) -> None:
    adapter = external_tool_adapter_entry(payload, "rednote_mcp")
    field_mappings = adapter["field_mappings"]
    assert isinstance(field_mappings, list)
    second_mapping = field_mappings[1]
    assert isinstance(second_mapping, dict)
    second_mapping["note"] = "Changed note."


def drift_external_tool_adapter_boundaries(payload: dict[str, object]) -> None:
    adapter = external_tool_adapter_entry(payload, "rednote_mcp")
    adapter["boundaries"] = ["Local producer-discovery metadata only."]


def drift_external_tool_later_manifest_command(payload: dict[str, object]) -> None:
    adapter = external_tool_adapter_entry(payload, "xiaohongshu_crawler")
    commands = adapter["recommended_commands"]
    assert isinstance(commands, list)
    commands[2] = external_tool_command(
        "community-handoff-manifest",
        "exports",
        "--input-format",
        "csv",
        "--pattern",
        "*.csv",
        "--config-dir",
        "configs",
        "--data-dir",
        "data",
        "--as-of",
        "2026-06-13T12:00:00+00:00",
        "--source-name",
        "Xiaohongshu Crawler Export",
        "--format",
        "table",
    )


def drift_external_tool_readiness_extra_flag(payload: dict[str, object]) -> None:
    replace_external_tool_readiness_command(
        payload,
        external_tool_command(
            "external-tool-readiness",
            "--adapter",
            "rednote_mcp",
            "--directory",
            "exports",
            "--config-dir",
            "configs",
            "--data-dir",
            "data",
            "--as-of",
            "2026-06-13T12:00:00+00:00",
            "--input-format",
            "json",
            "--pattern",
            "*.json",
            "--source-name",
            "Rednote MCP Export",
            "--format",
            "table",
            "--verbose",
        ),
    )
```

- [ ] **Step 4: Add the failing parameterized test**

Add this test after
`test_validate_external_tool_adapters_requires_print_only_registry_contract`:

```python
@pytest.mark.parametrize(
    ("mutate", "match"),
    (
        (add_external_tool_registry_extra_key, "external-tool-adapters keys"),
        (remove_external_tool_registry_boundary, "external-tool-adapters boundaries"),
        (add_external_tool_adapter_extra_key, "rednote_mcp keys"),
        (remove_external_tool_adapter_key, "rednote_mcp keys"),
        (drift_external_tool_later_adapter_description, "xiaohongshu_crawler description"),
        (drift_external_tool_upstream_examples, "x_search_export upstream_tool_examples"),
        (drift_external_tool_field_mapping_required, "rednote_mcp field_mappings"),
        (drift_external_tool_field_mapping_note, "rednote_mcp field_mappings"),
        (drift_external_tool_adapter_boundaries, "rednote_mcp boundaries"),
        (drift_external_tool_later_manifest_command, "xiaohongshu_crawler recommended_commands"),
        (drift_external_tool_readiness_extra_flag, "rednote_mcp recommended_commands"),
    ),
)
def test_validate_external_tool_adapters_rejects_full_static_contract_drift(
    mutate: Callable[[dict[str, object]], None],
    match: str,
) -> None:
    payload = external_tool_adapters_payload()
    mutate(payload)

    assert_external_tool_adapter_contract_drift(payload, match)
```

Also add `Callable` to the existing `typing` import if it is not already
present:

```python
from typing import Callable, cast
```

- [ ] **Step 5: Run the focused test and verify red state**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_validate_external_tool_adapters_rejects_full_static_contract_drift -q
```

Expected before validator updates: fail with `DID NOT RAISE` because the current
validator does not reject the first unvalidated full-contract mutation.

- [ ] **Step 6: Add command helper parity test**

Add this test near the external-tool adapter parity tests:

```python
@pytest.mark.parametrize(
    ("adapter_id", "input_format", "pattern", "source_name"),
    (
        ("rednote_mcp", "json", "*.json", "Rednote MCP Export"),
        ("xiaohongshu_crawler", "csv", "*.csv", "Xiaohongshu Crawler Export"),
    ),
)
def test_expected_external_tool_adapter_commands_match_fixture_helper(
    adapter_id: str,
    input_format: str,
    pattern: str,
    source_name: str,
) -> None:
    assert smoke.expected_external_tool_adapter_commands(
        adapter_id=adapter_id,
        input_format=input_format,
        pattern=pattern,
        source_name=source_name,
    ) == external_tool_adapter_commands(
        adapter_id=adapter_id,
        input_format=input_format,
        pattern=pattern,
        source_name=source_name,
    )
```

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_expected_external_tool_adapter_commands_match_fixture_helper -q
```

Expected before validator updates: fail with `AttributeError` because the smoke
script helper does not exist yet.

## Task 2: Extend Smoke Validator Full-Contract Checks

**Files:**
- Modify: `scripts/check_first_run_smoke.py`

- [ ] **Step 1: Set deterministic smoke env vars**

In `command_environment`, immediately after creating `env`, add:

```python
    env["FASHION_RADAR_CONFIG_DIR"] = "configs"
    env["FASHION_RADAR_DATA_DIR"] = "data"
```

This must happen before the `if not source_checkout` branch so installed-wheel
smoke uses the same deterministic print-only adapter registry defaults. Do not
change the `run_first_run_flow()` command sequence.

- [ ] **Step 2: Add static expected key, metadata, and boundary constants**

Near `EXPECTED_EXTERNAL_TOOL_ADAPTERS`, add:

```python
EXPECTED_EXTERNAL_TOOL_REGISTRY_KEYS = (
    "contract_version",
    "execution_mode",
    "adapters",
    "boundaries",
)
EXPECTED_EXTERNAL_TOOL_ADAPTER_KEYS = (
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
)
EXPECTED_EXTERNAL_TOOL_ADAPTER_DETAILS = {
    "rednote_mcp": {
        "description": (
            "Metadata target for Rednote/Xiaohongshu MCP exports that already "
            "produce sanitized local observations."
        ),
        "upstream_tool_examples": ["rednote-mcp"],
    },
    "xiaohongshu_crawler": {
        "description": (
            "Metadata target for user-controlled Xiaohongshu crawler exports "
            "converted to the community signal row shape."
        ),
        "upstream_tool_examples": ["xiaohongshu-crawler"],
    },
    "instaloader": {
        "description": (
            "Metadata target for sanitized Instagram post or profile exports "
            "created outside Fashion Radar."
        ),
        "upstream_tool_examples": ["Instaloader"],
    },
    "tiktok_api": {
        "description": (
            "Metadata target for sanitized TikTok observations exported by a "
            "user-controlled upstream tool."
        ),
        "upstream_tool_examples": ["TikTok-Api"],
    },
    "yt_dlp": {
        "description": (
            "Metadata target for sanitized media metadata exports, not media "
            "downloads or stored video assets."
        ),
        "upstream_tool_examples": ["yt-dlp"],
    },
    "x_search_export": {
        "description": "Metadata target for sanitized X/search exports created outside Fashion Radar.",
        "upstream_tool_examples": ["AnySearch X export", "snscrape export"],
    },
    "generic_community_export": {
        "description": (
            "Metadata target for any user-controlled community source already "
            "converted to sanitized local signal rows."
        ),
        "upstream_tool_examples": ["manual spreadsheet export", "community research export"],
    },
}
EXPECTED_EXTERNAL_TOOL_FIELD_MAPPINGS = [
    {
        "field": "url",
        "required": True,
        "note": "Stable source URL or local reference URL for the observed item.",
    },
    {
        "field": "title",
        "required": True,
        "note": "Short observed text, headline, caption summary, or normalized signal phrase.",
    },
    {
        "field": "published_at",
        "required": True,
        "note": "ISO 8601-compatible publication or observation timestamp.",
    },
    {
        "field": "summary",
        "required": False,
        "note": "Short sanitized local review note without raw comments or full post bodies.",
    },
    {
        "field": "source_name",
        "required": False,
        "note": "Producer/export display name for the local handoff rows.",
    },
    {
        "field": "platform",
        "required": False,
        "note": "Short local provenance label for review summaries.",
    },
    {
        "field": "source_weight",
        "required": False,
        "note": "Optional local weight in the existing community signal range (0, 5].",
    },
    {
        "field": "collected_at",
        "required": False,
        "note": "Timestamp for when the upstream tool produced the sanitized row.",
    },
]
EXPECTED_EXTERNAL_TOOL_ADAPTER_BOUNDARIES = [
    "Local producer-discovery metadata only.",
    "Writes should target sanitized CSV/JSON local handoff rows.",
    "Platform label is local provenance only.",
    "No platform collection, connector execution, scraping, browser automation, or API calls.",
]
EXPECTED_EXTERNAL_TOOL_REGISTRY_BOUNDARIES = [
    "Does not run adapters.",
    "Does not inspect the supplied directory.",
    "Does not read handoff files, validate files, import rows, or open SQLite.",
    "Does not create config, data, report, dashboard, or workflow artifacts.",
    (
        "Does not fetch URLs, search platforms, log in, store cookies, automate "
        "browsers, call platform APIs, monitor communities, schedule work, add "
        "source/platform connectors, acquire sources, prove demand, rank sources, "
        "or verify platform coverage."
    ),
    "Does not provide a compliance-review workflow.",
]
```

- [ ] **Step 3: Add expected command helpers**

Near the external-tool adapter validation code, add:

```python
def expected_external_tool_command(*parts: str) -> str:
    return shlex.join(("fashion-radar", *parts))
```

Then add a helper named `expected_external_tool_adapter_commands(...)` that
returns the same nine commands already generated by
`tests/test_first_run_smoke.py::external_tool_adapter_commands`. Use
`expected_external_tool_command(...)` for every command and the same fixed
arguments: `exports`, `configs`, `data`, and
`2026-06-13T12:00:00+00:00`. These values match the smoke-local env vars
from Step 1 and the adapter CLI's pinned default `as_of` value.

The helper must return commands in this exact order:

1. `community-signal-profile --format json`
2. `external-tool-readiness ... --format table`
3. `community-handoff-manifest ... --format json`
4. `community-handoff-workflow ... --format json`
5. `community-signal-lint-dir ...`
6. `community-handoff-check-dir ... --strict`
7. `import-signals-dir ... --dry-run`
8. `import-signals-dir ...` without `--dry-run`
9. `imported-review-workflow ...`

- [ ] **Step 4: Preserve existing diagnostics and add full adapter checks after them**

Keep the existing checks in `validate_external_tool_adapters` in their current
diagnostic order:

- payload type;
- `contract_version`;
- `execution_mode`;
- adapters list and adapter object type;
- adapter id order;
- core public metadata;
- `recommended_commands` type;
- shell parseability;
- command prefix sequence;
- readiness command count;
- readiness required flag/value diagnostics.

Do not insert the new adapter key or full `recommended_commands` assertions
before those checks. That would change the existing Stage 73 negative-test
labels and make the shell/readiness diagnostics unreachable.

After the existing readiness output-format assertion inside the per-adapter
loop, add:

```python
        assert_equal(
            f"{command_name} {adapter_id} keys",
            list(adapter),
            list(EXPECTED_EXTERNAL_TOOL_ADAPTER_KEYS),
        )
        adapter_details = EXPECTED_EXTERNAL_TOOL_ADAPTER_DETAILS[adapter_id]
        assert_equal(
            f"{command_name} {adapter_id} description",
            adapter.get("description"),
            adapter_details["description"],
        )
        assert_equal(
            f"{command_name} {adapter_id} upstream_tool_examples",
            adapter.get("upstream_tool_examples"),
            adapter_details["upstream_tool_examples"],
        )
        assert_equal(
            f"{command_name} {adapter_id} field_mappings",
            adapter.get("field_mappings"),
            EXPECTED_EXTERNAL_TOOL_FIELD_MAPPINGS,
        )
        assert_equal(
            f"{command_name} {adapter_id} recommended_commands",
            adapter.get("recommended_commands"),
            expected_external_tool_adapter_commands(
                adapter_id=adapter_id,
                input_format=input_format,
                pattern=pattern,
                source_name=source_name,
            ),
        )
        assert_equal(
            f"{command_name} {adapter_id} boundaries",
            adapter.get("boundaries"),
            EXPECTED_EXTERNAL_TOOL_ADAPTER_BOUNDARIES,
        )
```

- [ ] **Step 5: Assert top-level keys and registry boundaries after adapter loop**

After the per-adapter loop completes, add:

```python
    assert_equal(
        f"{command_name} keys",
        list(payload),
        list(EXPECTED_EXTERNAL_TOOL_REGISTRY_KEYS),
    )
    assert_equal(
        f"{command_name} boundaries",
        payload.get("boundaries"),
        EXPECTED_EXTERNAL_TOOL_REGISTRY_BOUNDARIES,
    )
```

- [ ] **Step 6: Run focused tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_command_environment_sets_deterministic_adapter_registry_dirs tests/test_first_run_smoke.py::test_validate_external_tool_adapters_rejects_full_static_contract_drift tests/test_first_run_smoke.py::test_expected_external_tool_adapter_commands_match_fixture_helper tests/test_first_run_smoke.py::test_validate_external_tool_adapters_requires_print_only_registry_contract tests/test_first_run_smoke.py::test_external_tool_adapters_payload_matches_real_registry tests/test_first_run_smoke.py::test_run_first_run_flow_uses_deterministic_local_command_sequence -q
```

Expected: pass.

## Task 3: Review, Verification, Commit, Publish

**Files:**
- Create: `docs/reviews/opencode-stage-76-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-76-code-review.md`
- Include Stage 76 spec/plan/review artifacts in commit.

- [ ] **Step 1: Run local verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_command_environment_sets_deterministic_adapter_registry_dirs tests/test_first_run_smoke.py::test_validate_external_tool_adapters_rejects_full_static_contract_drift tests/test_first_run_smoke.py::test_expected_external_tool_adapter_commands_match_fixture_helper tests/test_first_run_smoke.py::test_validate_external_tool_adapters_requires_print_only_registry_contract tests/test_first_run_smoke.py::test_external_tool_adapters_payload_matches_real_registry tests/test_first_run_smoke.py::test_run_first_run_flow_uses_deterministic_local_command_sequence -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen python scripts/check_release_hygiene.py
git diff --check
uv --no-config run --frozen pytest
```

Expected: pass.

- [ ] **Step 2: Request opencode code review**

Create `docs/reviews/opencode-stage-76-code-review-prompt.md` with the Stage 76
goal, touched files, implementation summary, and verification results. Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-76-code-review-prompt.md)" > docs/reviews/opencode-stage-76-code-review.md
```

Fix Critical/Important findings before proceeding.

- [ ] **Step 3: Commit**

Run:

```bash
git add scripts/check_first_run_smoke.py tests/test_first_run_smoke.py docs/superpowers/specs/2026-06-18-stage-76-adapter-smoke-full-contract-design.md docs/superpowers/plans/2026-06-18-stage-76-adapter-smoke-full-contract-plan.md docs/reviews/opencode-stage-76-plan-review-prompt.md docs/reviews/opencode-stage-76-plan-review.md docs/reviews/opencode-stage-76-code-review-prompt.md docs/reviews/opencode-stage-76-code-review.md
git commit -m "Harden adapter smoke metadata contract"
```

- [ ] **Step 4: Publish and verify CI**

Use the GitHub Git Data API path if normal git HTTPS push remains unreliable.
Verify remote `main`, local `origin/main`, release hygiene, credential-free git
config, and GitHub Actions CI success.

# Hermes GPT-5.6 Max Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the active Hermes profile and active project rule use `gpt-5.6-sol` with `max` reasoning, including Gateway `/reasoning max`, and prove the setting reaches the live provider.

**Architecture:** Treat `~/.hermes/config.yaml` as the authoritative runtime policy, patch the one stale Gateway command allowlist in the active Hermes 0.18.2 installation, and keep the `fashion-radar` rule synchronized with its documentation contract test. Preserve history and unrelated work; verify local parsing and payload construction before restarting the Gateway and sending one minimal live request.

**Tech Stack:** Hermes Agent 0.18.2, Python 3.11, PyYAML, pytest, systemd user services, OpenAI Responses-compatible custom provider.

---

### Task 1: Add failing Hermes policy and Gateway regression tests

**Files:**
- Create: `/home/ubuntu/.hermes/tests/test_gpt_5_6_max_policy.py`
- Test: `/home/ubuntu/.hermes/tests/test_gpt_5_6_max_policy.py`

- [ ] **Step 1: Create the policy regression test**

```python
from __future__ import annotations

import asyncio
from pathlib import Path

import yaml

from gateway.config import Platform
from gateway.platforms.base import MessageEvent
from gateway.session import SessionSource
from gateway.slash_commands import GatewaySlashCommandsMixin


HERMES_HOME = Path("/home/ubuntu/.hermes")


class ReasoningCommandHarness(GatewaySlashCommandsMixin):
    def __init__(self) -> None:
        self.overrides: dict[str, dict | None] = {}

    @staticmethod
    def _parse_reasoning_command_args(raw_args: str) -> tuple[str, bool]:
        return raw_args, False

    @staticmethod
    def _normalize_source_for_session_key(source: SessionSource) -> SessionSource:
        return source

    @staticmethod
    def _session_key_for_source(source: SessionSource) -> str:
        return f"{source.platform.value}:{source.chat_id}"

    @staticmethod
    def _load_show_reasoning() -> bool:
        return False

    @staticmethod
    def _resolve_session_reasoning_config(*, source, session_key):
        return None

    def _set_session_reasoning_override(self, session_key, value) -> None:
        self.overrides[session_key] = value

    @staticmethod
    def _evict_cached_agent(session_key: str) -> None:
        return None


def test_active_config_pins_gpt_5_6_sol_and_max() -> None:
    config = yaml.safe_load((HERMES_HOME / "config.yaml").read_text(encoding="utf-8"))

    assert config["model"]["default"] == "gpt-5.6-sol"
    assert config["agent"]["reasoning_effort"] == "max"
    assert config["delegation"]["reasoning_effort"] == "max"
    assert config["providers"]["openai"]["default_model"] == "gpt-5.6-sol"
    assert all(
        provider["model"] == "gpt-5.6-sol"
        for provider in config["custom_providers"]
    )


def test_gateway_reasoning_command_accepts_max() -> None:
    harness = ReasoningCommandHarness()
    source = SessionSource(platform=Platform.LOCAL, chat_id="max-policy-test")
    event = MessageEvent(text="/reasoning max", source=source)

    asyncio.run(harness._handle_reasoning_command(event))

    assert harness.overrides["local:max-policy-test"] == {
        "enabled": True,
        "effort": "max",
    }


def test_timeout_comment_matches_active_policy() -> None:
    env_text = (HERMES_HOME / ".env").read_text(encoding="utf-8")
    assert "gpt-5.6-sol with max reasoning" in env_text
    assert "gpt-5.5 with xhigh reasoning" not in env_text
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 \
  /home/ubuntu/.hermes/hermes-agent/venv/bin/python -B -m pytest \
  -p no:cacheprovider -q /home/ubuntu/.hermes/tests/test_gpt_5_6_max_policy.py
```

Expected: three failures showing the active config is still `xhigh`, Gateway
does not store a `max` override, and `.env` still names `gpt-5.5`/`xhigh`.

### Task 2: Add the failing project-rule contract

**Files:**
- Modify: `/home/ubuntu/fashion-radar/tests/test_review_protocol_docs.py:114`
- Test: `/home/ubuntu/fashion-radar/tests/test_review_protocol_docs.py`

- [ ] **Step 1: Change the expected Codex subagent reasoning rule**

Replace:

```python
assert "reasoning effort to `xhigh`" in _normalized_text(agents_text)
```

with:

```python
assert "reasoning effort to `max`" in _normalized_text(agents_text)
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
uv --no-config run --frozen pytest -q \
  tests/test_review_protocol_docs.py::test_active_review_protocol_documents_opencode_gate_and_claude_primary
```

Expected: failure because `AGENTS.md` still says `xhigh`.

### Task 3: Apply the minimum active Hermes changes

**Files:**
- Modify: `/home/ubuntu/.hermes/config.yaml`
- Modify: `/home/ubuntu/.hermes/.env`
- Modify: `/home/ubuntu/.hermes/hermes-agent/venv/lib/python3.11/site-packages/gateway/slash_commands.py:2714`
- Modify: `/home/ubuntu/.hermes/hermes-agent/venv/lib/python3.11/site-packages/hermes_cli/cli_commands_mixin.py:2474`
- Modify: `/home/ubuntu/.hermes/hermes-agent/venv/lib/python3.11/site-packages/hermes_cli/cli_commands_mixin.py:2496`
- Modify: `/home/ubuntu/.hermes/hermes-agent/venv/lib/python3.11/site-packages/hermes_cli/cli_commands_mixin.py:2537`
- Test: `/home/ubuntu/.hermes/tests/test_gpt_5_6_max_policy.py`

- [ ] **Step 1: Back up each active non-Git file**

Create timestamped sibling copies of `config.yaml`, `.env`,
`gateway/slash_commands.py`, and `hermes_cli/cli_commands_mixin.py`. Do not
alter the existing state snapshot or historical backups.

- [ ] **Step 2: Update structured policy values**

Set these YAML values without changing credentials, endpoints, API modes,
timeouts, context limits, or unrelated models:

```yaml
model:
  default: gpt-5.6-sol
providers:
  openai:
    default_model: gpt-5.6-sol
agent:
  reasoning_effort: max
delegation:
  reasoning_effort: max
```

Set every `custom_providers[*].model` value to `gpt-5.6-sol`.

- [ ] **Step 3: Update the active timeout comment**

Replace only the old model/reasoning wording with:

```text
# gpt-5.6-sol with max reasoning can sit silent for several minutes on
```

- [ ] **Step 4: Accept and document max in runtime commands**

In Gateway, change the effort allowlist to:

```python
elif effort in {"minimal", "low", "medium", "high", "xhigh", "max"}:
```

In classic CLI docstrings and usage/error strings, append `max` after `xhigh`.
Do not remove `xhigh` from compatibility lists.

- [ ] **Step 5: Run the Hermes policy test and verify GREEN**

Run the Task 1 pytest command. Expected: `3 passed`.

### Task 4: Update the active Fashion Radar rule

**Files:**
- Modify: `/home/ubuntu/fashion-radar/AGENTS.md:29`
- Modify: `/home/ubuntu/fashion-radar/tests/test_review_protocol_docs.py:114`

- [ ] **Step 1: Change only the Codex subagent rule**

Change `reasoning effort to xhigh` to `reasoning effort to max`. Keep Claude
`--effort max`, OpenCode `--variant max`, and every unrelated rule unchanged.

- [ ] **Step 2: Run the focused test and verify GREEN**

Run the Task 2 pytest command. Expected: `1 passed`.

### Task 5: Verify request construction, live provider behavior, and Gateway reload

**Files:**
- Verify: `/home/ubuntu/.hermes/config.yaml`
- Verify: active Hermes venv modules
- Verify: `hermes-gateway.service`

- [ ] **Step 1: Verify local parser and Responses payload**

Run a Python assertion that `parse_reasoning_effort("max")` returns
`{"enabled": True, "effort": "max"}` and the Responses transport builds
`{"effort": "max", "summary": "auto"}` for `gpt-5.6-sol`.

- [ ] **Step 2: Send one minimal live request before restarting Gateway**

Load the active endpoint and credential from parsed YAML inside the process,
send `Reply only: MAX_OK` with `reasoning.effort=max`, and print only the
sanitized status, returned model, and response text. Never print the endpoint
credential or raw request headers.

Expected: successful Responses result containing `MAX_OK`. If the endpoint
rejects `max`, restore the backed-up reasoning policy, do not restart into a
broken configuration, and report the upstream incompatibility.

- [ ] **Step 3: Restart and verify Gateway**

Record the old PID, restart `hermes-gateway.service`, and poll systemd until it
is `active/running` with a different nonzero PID. Inspect fresh startup logs for
tracebacks or configuration errors.

- [ ] **Step 4: Run the full scoped verification set**

Run the Hermes policy test, the complete Fashion Radar review protocol test
file, YAML assertions, local payload assertion, systemd status check, and a
scoped residual scan of active files. Expected: all commands exit zero; no
active model preset remains on `gpt-5.5`; no pinned active rule/config remains
on `xhigh`.

- [ ] **Step 5: Review and commit only task-owned repository files**

Review `git diff` for `AGENTS.md`,
`tests/test_review_protocol_docs.py`, and this plan. Do not stage or commit the
user's unrelated Stage 381 changes. Commit only task-owned repository files
after fresh verification.

# Hermes GPT-5.6 Max Migration Design

## Goal

Make the active Hermes installation use `gpt-5.6-sol` with `max` reasoning
consistently across its global configuration, selectable provider presets, and
active project rules. Verify both the local request construction and the live
custom-provider path without rewriting historical evidence.

## Current State

- Hermes was upgraded from `0.18.0` to `0.18.2` before this design was
  approved.
- The active CLI and Gateway import Hermes from
  `/home/ubuntu/.hermes/hermes-agent/venv/lib/python3.11/site-packages`.
- Hermes `0.18.2` natively parses `max` as
  `{"enabled": true, "effort": "max"}`.
- `/home/ubuntu/.hermes/config.yaml` already uses `gpt-5.6-sol` as its active
  top-level model, but its global reasoning effort is still `xhigh`.
- The same config retains one OpenAI provider default and four selectable
  custom-provider presets on `gpt-5.5`.
- The Gateway `/reasoning` command still rejects `max`, and classic CLI help
  text still omits `max`, despite the central parser accepting it.
- `fashion-radar/AGENTS.md` requires Codex subagents to use `xhigh`; its
  documentation test requires that exact rule.

## Considered Approaches

### 1. Complete active-state migration (selected)

Update every currently effective configuration, selectable preset, runtime
command path, project rule, and contract test. Preserve backups, logs, old
sessions, caches, and review history.

This is selected because it makes the operational state internally consistent
while retaining evidence of earlier configurations.

### 2. Configuration-only migration

Change only `agent.reasoning_effort` in `config.yaml`. This is lower risk but
leaves selectable `gpt-5.5` presets, misleading environment comments, an
inconsistent Gateway slash command, and the `fashion-radar` `xhigh` rule.

This does not satisfy the approved requirement.

### 3. Historical global replacement

Replace `gpt-5.5` and `xhigh` in backups, logs, sessions, caches, and archived
plans as well as active state. This destroys audit history and may corrupt
generated or structured state.

This was explicitly rejected in favor of approach 1.

## Approved Scope

### Hermes configuration

Update `/home/ubuntu/.hermes/config.yaml` as structured YAML:

- Keep `model.default` at `gpt-5.6-sol`.
- Set `agent.reasoning_effort` to `max`.
- Set `delegation.reasoning_effort` to `max` so delegated agents remain pinned
  to the approved level even if parent inheritance behavior changes later.
- Change `providers.openai.default_model` from `gpt-5.5` to `gpt-5.6-sol`.
- Change all four selectable custom-provider entries currently set to
  `gpt-5.5` to `gpt-5.6-sol`.
- Leave endpoint URLs, API modes, credentials, context limits, timeouts, and
  unrelated models unchanged.

Update `/home/ubuntu/.hermes/.env` comments so the timeout explanation refers
to `gpt-5.6-sol` with `max` reasoning. Do not change the timeout values or any
secret-bearing entry.

### Hermes runtime consistency

Patch the active Hermes `0.18.2` installation so:

- Gateway `/reasoning max` accepts and persists `max`.
- Gateway and classic CLI help list `max` as a valid level.
- Existing provider-specific compatibility mappings remain unchanged; `xhigh`
  remains a valid compatibility level and must not be globally deleted from
  Hermes source.

Because files under `site-packages` can be replaced by a future Hermes update,
verification must detect the inconsistency again after upgrades. The patch is
limited to the active `0.18.2` installation and must not reinstall from the
unrelated top-level `0.14.0` source snapshot.

### Active project rule

Update `/home/ubuntu/fashion-radar/AGENTS.md` so Codex subagents use `max`
instead of `xhigh`. Update
`/home/ubuntu/fashion-radar/tests/test_review_protocol_docs.py` to enforce the
new rule.

Do not change the existing Claude Code `--effort max` or OpenCode
`--variant max` review rules.

## Explicit Exclusions

Do not rewrite:

- `config.yaml.bak*`, `.env.bak*`, state snapshots, or upgrade backups.
- Hermes logs, sessions, request dumps, shell history, or old repair reports.
- Model catalogs, model metadata, discovery caches, or provider compatibility
  lists that legitimately mention `gpt-5.5` or `xhigh`.
- Archived plans, specs, code-review records, or generated artifacts.
- The inactive `/home/ubuntu/.hermes/hermes-agent` `0.14.0` source snapshot.
- Unrelated dirty files already present in the `fashion-radar` worktree.

## Change Safety

- Preserve the pre-update state snapshot
  `20260711-040921-pre-gpt-5.6-sol-max-migration`.
- Create targeted timestamped backups of each active non-Git Hermes file before
  editing it.
- Never print, log, commit, or include API keys in test commands or reports.
- Restart the Gateway only after configuration and local tests pass.
- If the live active endpoint rejects `max`, restore the active reasoning
  setting to its pre-change value, restart the Gateway, and report the upstream
  incompatibility instead of leaving messaging unavailable.

## Verification

Verification is layered so each claim has direct evidence:

1. Parse `config.yaml` as YAML and assert the active model, provider presets,
   parent reasoning, and delegated reasoning have the approved values.
2. Assert Hermes parses `max` and its Responses transport builds
   `{"effort": "max", "summary": "auto"}` for `gpt-5.6-sol`.
3. Exercise the Gateway reasoning command without network access and assert
   `/reasoning max` is accepted rather than returning `unknown_arg`.
4. Run the focused `fashion-radar` review-protocol documentation test.
5. Restart `hermes-gateway.service`, then assert a new PID and
   `active/running` state with no startup traceback.
6. Send one minimal live request through the configured active
   `gpt-5.6-sol` custom provider using `max`; require a successful response.
7. Run a scoped residual scan over active configuration and active rule files.
   Require no operational `gpt-5.5` preset or pinned `xhigh` reasoning rule.
8. Confirm historical backups, logs, sessions, caches, and unrelated dirty
   project files were not modified.

Selectable non-active providers may be probed without switching the active
Gateway. Their endpoint support is best-effort because they are independent
third-party services; a failed probe is reported separately and does not
invalidate a successful active-provider migration.

## Success Criteria

- The active profile reports `gpt-5.6-sol`.
- Parent and delegated reasoning configuration both report `max`.
- Hermes constructs and the active endpoint accepts a real `max` request.
- Gateway remains `active/running` after restart.
- `/reasoning max` is accepted by the current Gateway runtime.
- The `fashion-radar` rule and its focused test require `max`.
- No approved active surface retains a `gpt-5.5` model preset or pinned
  `xhigh` reasoning setting.
- Historical and unrelated files remain untouched.

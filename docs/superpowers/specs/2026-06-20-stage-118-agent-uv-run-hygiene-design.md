# Stage 118 Agent UV Run Hygiene Design

## Goal

Prevent agent-run verification commands from accidentally rewriting `uv.lock`
through user-level mirror configuration while keeping mirror installs available
for local dependency setup.

## Reviewer Context

This design is for local opencode review before implementation. Use:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-118-plan-review-prompt.md)" > docs/reviews/opencode-stage-118-plan-review.md
```

## Background

The project already documents two separate practices:

- local dependency installation may use mirrors with `UV_DEFAULT_INDEX=...` and
  `uv sync --frozen`;
- public release checks must keep `uv.lock` mirror-free and use
  `UV_NO_CONFIG=1` for lockfile validation.

During Stage 117, a worker ran `uv run` without `--no-config` / `--frozen` and
temporarily rewrote `uv.lock` with mirror URLs. The release gate caught and
removed that drift, but the agent-facing docs should make the safer default
explicit before future nodes repeat the mistake.

## Decision

Add a docs/tests-only hygiene node that documents this distinction:

- mirror-backed commands are for local dependency/software installation;
- agent-run verification commands should prefer `uv --no-config run --frozen`
  and should not be combined with mirror-backed user config;
- public lockfile checks still use `UV_NO_CONFIG=1 uv lock --check` plus the
  explicit mirror marker scan.

Use docs drift coverage so the rule remains visible in:

- `AGENTS.md`
- `README.md`
- `docs/dependency-mirrors.md`
- `docs/github-upload-checklist.md`

## In Scope

- Add concise agent verification guidance to the dependency/mirror docs.
- Add a focused docs drift test in `tests/test_cli_docs.py`.
- Add Stage 118 review artifacts.

## Out of Scope

- No runtime behavior changes.
- No source code changes under `src/`.
- No dependency, `pyproject.toml`, or `uv.lock` changes.
- No CI workflow changes.
- No connector, scraping, browser automation, platform API, account/session,
  monitoring, scheduling, source acquisition, demand proof, ranking, coverage
  verification, or compliance/audit product feature.

## Expected User-Facing Behavior

Developers and agents reading the project docs should see one clear rule:

- use mirrors for frozen local installs, for example
  `UV_DEFAULT_INDEX=... uv sync --frozen --dev`;
- use `uv --no-config run --frozen ...` for agent-run verification commands
  that should not mutate the lockfile or observe user-level mirror config;
- validate public lockfile state with `UV_NO_CONFIG=1 uv lock --check`, the
  mirror-marker `rg` scan, and `git diff --exit-code -- uv.lock pyproject.toml`.

## Acceptance Criteria

- `AGENTS.md` dependency guidance includes `uv --no-config run --frozen` for
  agent-run verification commands.
- `README.md` development guidance points agents to `uv --no-config run --frozen`
  and keeps mirror use limited to frozen installs.
- `docs/dependency-mirrors.md` `Project Practice` explains the split between
  frozen mirror installs and no-config frozen verification runs.
- `docs/github-upload-checklist.md` warns before upload that agent-run
  verification should use no-config frozen `uv run` and that mirror-backed
  local operations must not rewrite public lockfiles.
- `tests/test_cli_docs.py` asserts these docs keep the split visible.
- Existing release hygiene, full tests, ruff, format, lockfile, mirror scan, and
  diff checks remain green.

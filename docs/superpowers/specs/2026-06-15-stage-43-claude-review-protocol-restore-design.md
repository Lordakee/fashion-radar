# Stage 43 Claude Review Protocol Restore Design

## Goal

Restore local Claude Code as the active plan and release review authority after
the temporary opencode/GLM 5.2 rule was canceled.

## Scope

In scope:

- Update `AGENTS.md` active project instructions so future plan/code review gates
  use local Claude Code with `--effort max`.
- Update `docs/REVIEW_PROTOCOL.md` so the current process again names Claude
  Code as the review tool, uses `claude-code-stage-N-*` record names, and
  treats Stage 40 `opencode-*` records as historical audit records.
- Keep `docs/github-upload-checklist.md` aligned with the same Claude Code
  command form used by the active agent instructions and review protocol.
- Add a lightweight pytest guard that keeps active review workflow docs from
  drifting back to opencode/GLM 5.2 as the review authority.
- Record Stage 43 Claude Code plan and release review artifacts under
  `docs/reviews/`.

Out of scope:

- Rewriting historical `docs/reviews/opencode-stage-40-*` records.
- Rewriting historical staged specs/plans that mention opencode or Claude Code
  as part of prior audit history.
- Runtime behavior, source collection, imports, reports, dashboards, database
  schema, package metadata, CI YAML, lockfiles, dependencies, generated data, or
  config template changes.
- Source connectors, scraping, crawling, browser automation, login/cookie/
  account/proxy/CAPTCHA flows, platform APIs, source acquisition, schedulers,
  watchers, monitors, or external services.

## Design

`AGENTS.md` and `docs/REVIEW_PROTOCOL.md` are active workflow entry points.
They should match the user's restored rule:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "review prompt..."
```

The docs should keep the existing staged review structure:

- plan review before coding;
- fresh verification before release/code review;
- Critical and Important findings block progress;
- review artifacts are recorded in `docs/reviews/`;
- Codex subagents use `reasoning_effort: "xhigh"`;
- dependency checks continue to use mirror commands where appropriate.

`docs/REVIEW_PROTOCOL.md` should use these active record names:

```text
docs/reviews/claude-code-stage-N-plan-review.md
docs/reviews/claude-code-stage-N-release-review.md
docs/reviews/claude-code-stage-N-plan-rereview.md
docs/reviews/claude-code-stage-N-release-rereview.md
```

`docs/github-upload-checklist.md` already names Claude Code in its Final Review
section. It should remain in scope for the guard test and use the same
`--tools Read,Grep,Glob,LS,Bash` command form as the other active workflow docs,
so future edits keep the three active workflow docs aligned.

Create `tests/test_review_protocol_docs.py` with read-only assertions over only
the active workflow docs:

- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/github-upload-checklist.md`

The test should assert active docs do not contain active opencode authority
terms: `local opencode`, `opencode run`, `zhipuai-coding-plan/glm-5.2`,
`GLM 5.2`, or `docs/reviews/opencode-stage-N`. It should still allow the narrow
historical note that older `opencode-*` records under `docs/reviews/` are audit
records and do not need rewriting.

## Verification

Focused checks:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_review_protocol_docs.py -q
UV_NO_CONFIG=1 uv run ruff check tests/test_review_protocol_docs.py
UV_NO_CONFIG=1 uv run ruff format --check tests/test_review_protocol_docs.py
rg -n "local opencode|opencode run|zhipuai-coding-plan/glm-5.2|GLM 5.2|docs/reviews/opencode-stage-N" AGENTS.md docs/REVIEW_PROTOCOL.md docs/github-upload-checklist.md
rg -n "Claude Code|claude --effort max|claude-code-stage-N" AGENTS.md docs/REVIEW_PROTOCOL.md docs/github-upload-checklist.md
git diff --check
```

Release checks:

```bash
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
UV_NO_CONFIG=1 uv run pytest tests/test_review_protocol_docs.py tests/test_cli_docs.py -q
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```

# Stage 40 Opencode Review Workflow Design

## Goal

Update the active repository review workflow docs so future plan and release
reviews use local `opencode` with the GLM 5.2 model, matching the user's
current rule.

## Scope

In scope:

- Update `AGENTS.md` active project instructions so future review gates use
  local opencode with GLM 5.2.
- Update `docs/REVIEW_PROTOCOL.md` from Claude Code review gates to local
  opencode review gates.
- Update `docs/github-upload-checklist.md` final review language so it points to
  local opencode with GLM 5.2 before upload.
- Record Stage 40 opencode plan and release review artifacts under
  `docs/reviews/`.
- Keep the change documentation-only.

Out of scope:

- Changing historical stage records that mention Claude Code.
- Changing source code, tests, dependencies, lockfiles, CI behavior, packaging,
  database schema, commands, source collection, imports, reports, dashboards, or
  scheduling behavior.
- Adding source connectors, scraping, crawling, browser automation,
  login/cookie/account/proxy/CAPTCHA flows, platform APIs, watchers, monitors,
  or source acquisition.

## Design

`AGENTS.md` and `docs/REVIEW_PROTOCOL.md` should describe the current active
gate:

```bash
opencode run -m zhipuai-coding-plan/glm-5.2 "review prompt..."
```

It should state that this model ID is the local opencode name for GLM 5.2. The
document should keep the existing review-gated structure: plan review before
coding, release review before commit/push, Critical and Important findings as
blockers, and review records stored in `docs/reviews/`.

`docs/REVIEW_PROTOCOL.md` should update every active Claude Code reference in
the Before Coding, During Development, Before GitHub Upload, and Review Record
Naming sections. New records should use `opencode-stage-N-...` names. Historical
`claude-code-*` names remain accepted only as legacy audit records.

`docs/github-upload-checklist.md` should keep the existing verification
commands and artifact exclusion lists. Only the final review step should change
from Claude Code to local opencode with GLM 5.2.

Historical docs under `docs/superpowers/plans/` and prior `docs/reviews/`
records are not rewritten. They are audit history, not current process policy.

## Verification

Focused documentation checks:

```bash
rg -n "opencode|zhipuai-coding-plan/glm-5.2|GLM 5.2" AGENTS.md docs/REVIEW_PROTOCOL.md docs/github-upload-checklist.md
if rg -qn "Claude Code" AGENTS.md docs/REVIEW_PROTOCOL.md docs/github-upload-checklist.md; then
  echo "FAIL: active Claude Code review requirements remain"
  exit 1
fi
if git diff HEAD --name-only | rg '^docs/reviews/claude-code'; then
  echo "FAIL: historical Claude Code review records changed"
  exit 1
fi
if git diff HEAD --name-only | rg '^docs/superpowers/plans/' | rg -v '^docs/superpowers/plans/2026-06-14-stage-40-opencode-review-workflow-plan.md$'; then
  echo "FAIL: unrelated historical plan files changed"
  exit 1
fi
if git diff HEAD --name-only | rg '^docs/superpowers/specs/' | rg -v '^docs/superpowers/specs/2026-06-14-stage-40-opencode-review-workflow-design.md$'; then
  echo "FAIL: unrelated historical spec files changed"
  exit 1
fi
git diff --check
```

Release checks:

```bash
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```

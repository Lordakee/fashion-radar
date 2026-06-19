# Stage 119 Review Protocol Opencode Alignment Design

## Goal

Align the active project review protocol with the local opencode review route
used in recent stages while keeping Claude Code max-effort review documented as
an explicit alternate route.

## Reviewer Context

This design is for local opencode review before implementation. Use:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-119-plan-review-prompt.md)" > docs/reviews/opencode-stage-119-plan-review.md
```

## Background

Recent Stage 117 and Stage 118 reviews repeatedly flagged a process mismatch:

- the active stage artifacts use local opencode with
  `zhipuai-coding-plan/glm-5.2 --variant max`;
- `AGENTS.md`, `docs/REVIEW_PROTOCOL.md`, and
  `docs/github-upload-checklist.md` still describe local Claude Code
  `--effort max` as the active review gate;
- `tests/test_review_protocol_docs.py` currently enforces the stale Claude Code
  default and forbids active opencode wording.

The project needs the docs and drift tests to match the active user preference
for local opencode review, without deleting the previously useful Claude Code
review command. The command should remain available as an alternate route when a
future stage explicitly asks for Claude Code.

## Decision

Make local opencode the documented active review engine:

- plan and code/release review commands use
  `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`;
- active review artifact names use `docs/reviews/opencode-stage-N-...`;
- Codex subagents continue to use reasoning effort `xhigh`;
- Claude Code remains documented as an optional alternate review route with
  `--effort max`, read-only plan mode, and `claude-code-stage-N-...` artifact
  names only when explicitly requested.

Use docs drift coverage to prevent the three active workflow docs from
diverging again:

- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/github-upload-checklist.md`

## In Scope

- Replace the stale active-Claude review assertions in
  `tests/test_review_protocol_docs.py` with active-opencode assertions.
- Update the review gate wording in `AGENTS.md`.
- Update the canonical protocol in `docs/REVIEW_PROTOCOL.md`.
- Update the final review section in `docs/github-upload-checklist.md`.
- Add Stage 119 review artifacts.

## Out of Scope

- No runtime behavior changes.
- No source code changes under `src/`.
- No dependency, `pyproject.toml`, or `uv.lock` changes.
- No CI workflow changes.
- No connector, scraping, browser automation, platform API, account/session,
  monitoring, scheduling, source acquisition, demand proof, ranking, coverage
  verification, or compliance/audit product feature.

## Expected User-Facing Behavior

Agents and contributors should see one consistent staged review route:

- submit plans to local opencode before implementation;
- use `zhipuai-coding-plan/glm-5.2` with `--variant max`;
- store plan, code, release, and rereview records under
  `docs/reviews/opencode-stage-N-...`;
- fix Critical and Important findings before continuing;
- use Claude Code `--effort max` only as an alternate route when explicitly
  requested.

## Acceptance Criteria

- `tests/test_review_protocol_docs.py` has a failing test first that requires
  active opencode wording across `AGENTS.md`, `docs/REVIEW_PROTOCOL.md`, and
  `docs/github-upload-checklist.md`.
- `AGENTS.md` documents local opencode as the active plan/code review route and
  preserves Codex subagent `xhigh` guidance.
- `docs/REVIEW_PROTOCOL.md` documents opencode plan, code, release, and
  rereview artifact names, plus a clearly optional Claude Code route.
- The optional Claude Code route keeps its own `claude-code-stage-N-...`
  artifact naming convention documented in `docs/REVIEW_PROTOCOL.md`.
- `docs/github-upload-checklist.md` final review instructions use the active
  opencode command.
- The stale statement that older `opencode-*` records are historical-only is
  removed or rewritten so it no longer contradicts active opencode usage.
- Focused review protocol docs tests pass after implementation.
- Existing release hygiene, full tests, ruff, format, lockfile, mirror scan, and
  diff checks remain green.

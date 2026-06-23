# Stage 173 XPOZ Readiness Docs Discoverability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make XPOZ MCP / Social Data API exports discoverable in the `external-tool-readiness` docs and guard that discoverability with a docs parity test.

**Architecture:** Docs/test-only. Add a narrow docs tuple and a focused pytest in `tests/test_cli_docs.py`, then update existing readiness prose and copyable command examples in user-facing docs. Runtime adapter and readiness builders remain unchanged.

**Tech Stack:** Markdown, pytest, existing `tests/test_cli_docs.py` helpers, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `tests/test_cli_docs.py`
  - Add an `EXTERNAL_TOOL_READINESS_XPOZ_DISCOVERABILITY_DOCS` tuple.
  - Add `test_external_tool_readiness_docs_include_xpoz_discoverability`.
- Modify: `README.md`
  - Add XPOZ to readiness known-tool prose.
- Modify: `docs/cli-reference.md`
  - Add XPOZ to readiness known-tool prose.
  - Add a copyable `xpoz_mcp` readiness JSON command.
- Modify: `docs/community-signal-import.md`
  - Add XPOZ to readiness known-tool prose.
- Modify: `docs/community-signal-quality.md`
  - Add XPOZ to readiness known-tool prose.
- Modify: `docs/source-boundaries.md`
  - Add XPOZ to readiness known-tool prose.
- Modify: `docs/architecture.md`
  - Add XPOZ to readiness known-tool prose.
- Modify: `docs/github-upload-checklist.md`
  - Add XPOZ to readiness known-tool prose.
  - Add CLI reference/checklist and installed-wheel smoke command examples.
- Modify: `CHANGELOG.md`
  - Add a Stage 173 docs/test-only entry under `[Unreleased]`.
- Add: `docs/superpowers/specs/2026-06-23-stage-173-xpoz-readiness-docs-discoverability-design.md`
- Add: `docs/superpowers/plans/2026-06-23-stage-173-xpoz-readiness-docs-discoverability-plan.md`
- Add: `docs/reviews/opencode-stage-173-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-173-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-173-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-173-code-review.md`
- Add after release verification: `docs/reviews/opencode-stage-173-release-review-prompt.md`
- Add after release verification: `docs/reviews/opencode-stage-173-release-review.md`

## Task 1: Add RED Docs Discoverability Test

**Files:**

- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Add the XPOZ discoverability docs tuple**

Immediately after `EXTERNAL_TOOL_READINESS_DOCS`, add:

```python
EXTERNAL_TOOL_READINESS_XPOZ_DISCOVERABILITY_DOCS = (
    README,
    CLI_REFERENCE,
    ROOT / "docs" / "community-signal-import.md",
    ROOT / "docs" / "community-signal-quality.md",
    ROOT / "docs" / "source-boundaries.md",
    ROOT / "docs" / "architecture.md",
    UPLOAD_CHECKLIST,
    ROOT / "CHANGELOG.md",
)
```

- [ ] **Step 2: Add the failing docs parity test**

Immediately after `test_external_tool_readiness_docs_are_linked_and_bounded`,
add:

```python
def test_external_tool_readiness_docs_include_xpoz_discoverability() -> None:
    for path in EXTERNAL_TOOL_READINESS_XPOZ_DISCOVERABILITY_DOCS:
        normalized = _normalized_text(_read(path)).casefold()
        for phrase in (
            "xpoz mcp",
            "social data api",
            "external-tool-readiness",
            "sanitized csv/json local file handoff",
        ):
            assert phrase.casefold() in normalized, (
                f"{path.relative_to(ROOT)} missing {phrase!r}"
            )

    cli_reference = _read(CLI_REFERENCE)
    checklist = _read(UPLOAD_CHECKLIST)
    command = "fashion-radar external-tool-readiness --adapter xpoz_mcp --format json"
    installed_wheel_command = (
        '"$tmp_env/venv/bin/fashion-radar" external-tool-readiness '
        "--adapter xpoz_mcp --format json"
    )

    assert command in cli_reference
    assert command in checklist
    assert installed_wheel_command in checklist
```

- [ ] **Step 3: Run RED check**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_external_tool_readiness_docs_include_xpoz_discoverability -q
```

Expected before docs updates: fails because at least one readiness doc is
missing `xpoz mcp`, `social data api`, or the copyable `xpoz_mcp` readiness
command.

## Task 2: Update XPOZ Readiness Documentation

**Files:**

- Modify: `README.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/community-signal-quality.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/architecture.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update known-tool prose**

Where readiness docs currently enumerate:

```text
Rednote MCP, Xiaohongshu crawler, Instaloader, TikTok-Api, yt-dlp, and
X/search exports
```

rewrite it as:

```text
Rednote MCP, Xiaohongshu crawler, Instaloader, TikTok-Api, yt-dlp, X/search
exports, and XPOZ MCP / Social Data API exports
```

Apply this in:

- `README.md`
- `docs/cli-reference.md`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `docs/source-boundaries.md`
- `docs/architecture.md`
- `docs/github-upload-checklist.md`

- [ ] **Step 2: Add copyable XPOZ readiness commands**

In `docs/cli-reference.md`, add this line to the local import/community handoff
command block immediately after the `instaloader` readiness JSON command:

```bash
fashion-radar external-tool-readiness --adapter xpoz_mcp --format json
```

In `docs/github-upload-checklist.md`, add the same command to the readiness
docs check command block:

```bash
fashion-radar external-tool-readiness --adapter xpoz_mcp --format json
```

In the installed-wheel smoke command list in
`docs/github-upload-checklist.md`, add:

```bash
"$tmp_env/venv/bin/fashion-radar" external-tool-readiness --adapter xpoz_mcp --format json
```

- [ ] **Step 3: Add Stage 173 changelog entry**

Under `## [Unreleased]` / `### Added`, add:

```markdown
- Stage 173 docs/test parity for XPOZ MCP / Social Data API
  `external-tool-readiness` discoverability for sanitized CSV/JSON local file
  handoff rows from user-controlled external/community tools. This is
  docs/test-only and adds no XPOZ API calls, MCP execution, API keys,
  connectors, scraping, browser automation, platform APIs, login/cookie/token
  behavior, source acquisition, demand proof, ranking, coverage verification,
  or compliance-review product feature.
```

- [ ] **Step 4: Run GREEN focused checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_external_tool_readiness_docs_include_xpoz_discoverability -q
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_external_tool_readiness_docs_are_linked_and_bounded tests/test_cli_docs.py::test_external_tool_readiness_upload_checklist_help_loop_and_smoke tests/test_cli_docs.py::test_external_tool_readiness_docs_include_xpoz_discoverability -q
uv --no-config run --frozen pytest tests/test_cli_docs.py -q
uv --no-config run --frozen pytest tests/test_external_tool_readiness.py::test_readiness_upstream_command_mapping tests/test_external_tool_adapters.py::test_xpoz_mcp_adapter_has_expected_mapping_and_commands -q
uv --no-config run --frozen ruff check tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
```

Expected: all focused tests and checks pass.

## Task 3: Review, Release Gate, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-173-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-173-code-review.md`
- Add: `docs/reviews/opencode-stage-173-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-173-release-review.md`

- [ ] **Step 1: Create code review prompt**

Create `docs/reviews/opencode-stage-173-code-review-prompt.md` with a prompt
that asks local opencode to review the Stage 173 implementation. The prompt
must require the response to start with:

```text
# Stage 173 Code Review
```

- [ ] **Step 2: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-173-code-review-prompt.md)" > "$tmp_review"
sed -n '1,320p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-173-code-review.md
rm -f "$tmp_review"
```

Expected: completed review output with no critical or important findings. Clean
the artifact if opencode includes process chatter or command logs.

- [ ] **Step 3: Run release gate**

Run:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader
```

Expected: all commands pass; token and extraheader checks report no secrets.

- [ ] **Step 4: Create and run release review**

Create `docs/reviews/opencode-stage-173-release-review-prompt.md` requiring the
review body to start with:

```text
# Stage 173 Release Review
```

Then run the same temp-file `opencode run --model zhipuai-coding-plan/glm-5.2
--variant max` capture flow used for prior stages, copying the completed review
to `docs/reviews/opencode-stage-173-release-review.md`.

Expected: completed review output with no critical or important findings. Clean
the artifact if needed.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short
git add \
  tests/test_cli_docs.py \
  README.md \
  docs/cli-reference.md \
  docs/community-signal-import.md \
  docs/community-signal-quality.md \
  docs/source-boundaries.md \
  docs/architecture.md \
  docs/github-upload-checklist.md \
  CHANGELOG.md \
  docs/superpowers/specs/2026-06-23-stage-173-xpoz-readiness-docs-discoverability-design.md \
  docs/superpowers/plans/2026-06-23-stage-173-xpoz-readiness-docs-discoverability-plan.md \
  docs/reviews/opencode-stage-173-plan-review-prompt.md \
  docs/reviews/opencode-stage-173-plan-review.md \
  docs/reviews/opencode-stage-173-code-review-prompt.md \
  docs/reviews/opencode-stage-173-code-review.md \
  docs/reviews/opencode-stage-173-release-review-prompt.md \
  docs/reviews/opencode-stage-173-release-review.md
git commit -m "docs: surface xpoz readiness guidance"
git push origin main
```

Expected: commit succeeds and `main` pushes to GitHub.

## Self-Review Notes

- Spec coverage: Task 1 covers the docs guard, Task 2 covers user-facing docs
  discoverability, and Task 3 covers review, release gate, commit, and push.
- Placeholder scan: no placeholders or deferred implementation notes.
- Boundary check: runtime source, readiness builder behavior, adapter registry,
  scripts, payloads, install hints, connectors, scraping, platform APIs, MCP
  execution, API keys, login/cookie behavior, monitoring, scheduling, demand
  proof, ranking, coverage verification, and compliance-review product
  features remain out of scope.

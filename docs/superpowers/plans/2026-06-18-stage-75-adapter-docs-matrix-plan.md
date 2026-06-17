# Stage 75 Adapter Docs Matrix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a public docs matrix for every external-tool adapter id, document
the first-run smoke adapter-registry contract, and guard both with CLI docs
tests.

**Architecture:** Documentation/test-only hardening. The adapter registry and
runtime CLI remain unchanged. Docs tests pin the exact public docs strings as
static contracts.

**Tech Stack:** Markdown, Python 3.11, pytest, uv, ruff.

**Review Protocol Note:** Per the current user instruction for this stage,
local review is performed with `opencode run --model
zhipuai-coding-plan/glm-5.2 --variant max`. This stage-local review path does
not change the repository's broader review protocol documents.

---

## File Map

- Modify `README.md`
  - Add a complete external-tool adapter matrix near the existing
    `external-tool-adapters` section.
  - Add one first-run smoke sentence saying the automated first-run smoke
    validates the external-tool adapter registry JSON contract from
    `external-tool-adapters --format json` across all seven adapters.
- Modify `docs/cli-reference.md`
  - Add the same complete adapter matrix near the command reference entry.
- Modify `docs/first-run.md`
  - Add the same first-run smoke adapter-registry contract sentence.
- Modify `CHANGELOG.md`
  - Add a Stage 75 docs entry under `[Unreleased]`.
- Modify `docs/reviews/opencode-stage-74-code-review.md`
  - Add a correction note for the stale M1 finding because that issue was fixed
    before Stage 74 commit/publish.
- Modify `tests/test_cli_docs.py`
  - Add static expected adapter matrix row strings.
  - Extend the external-tool adapter docs guard to require every full adapter
    row in both README and CLI reference.
  - Extend first-run smoke docs guards to require the adapter-registry contract
    sentence in both README and first-run guide.
- Create review artifacts:
  - `docs/reviews/opencode-stage-75-plan-review-prompt.md`
  - `docs/reviews/opencode-stage-75-plan-review.md`
  - `docs/reviews/opencode-stage-75-code-review-prompt.md`
  - `docs/reviews/opencode-stage-75-code-review.md`

## Task 1: Add Failing Docs Guards

**Files:**
- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Add static docs constants**

Near the external-tool docs constants, add:

```python
EXTERNAL_TOOL_ADAPTER_DOC_ROWS = (
    "| `rednote_mcp` | Rednote MCP Export | `rednote` | `json` | `*.json` |",
    (
        "| `xiaohongshu_crawler` | Xiaohongshu Crawler Export | "
        "`xiaohongshu` | `csv` | `*.csv` |"
    ),
    "| `instaloader` | Instaloader Export | `instagram` | `json` | `*.json` |",
    "| `tiktok_api` | TikTok-Api Export | `tiktok` | `json` | `*.json` |",
    "| `yt_dlp` | yt-dlp Metadata Export | `media` | `json` | `*.json` |",
    "| `x_search_export` | X Search Export | `x` | `csv` | `*.csv` |",
    (
        "| `generic_community_export` | Generic Community Export | "
        "`community` | `csv` | `*.csv` |"
    ),
)

FIRST_RUN_EXTERNAL_ADAPTER_SMOKE_PHRASE = (
    "The automated first-run smoke also validates the external-tool adapter "
    "registry JSON contract from `external-tool-adapters --format json` across "
    "all seven adapters."
)
```

- [ ] **Step 2: Add the failing matrix docs assertion**

In `test_external_tool_adapter_registry_docs_are_linked_and_bounded`, after the
existing command checks, add:

```python
    for doc_path, doc_text in ((README, readme), (CLI_REFERENCE, cli_reference)):
        normalized = _normalized_text(doc_text)
        for row in EXTERNAL_TOOL_ADAPTER_DOC_ROWS:
            assert row in normalized, f"{doc_path.relative_to(ROOT)} missing {row!r}"
```

- [ ] **Step 3: Add the failing first-run smoke docs assertion**

In `test_readme_documents_manual_sample_flow_and_automated_smoke_boundary`, add
the phrase to the existing `for term in (...)` loop that checks normalized
automated smoke wording:

```python
        FIRST_RUN_EXTERNAL_ADAPTER_SMOKE_PHRASE,
```

In `test_first_run_guide_documents_paths_outputs_dashboard_reset_and_boundaries`,
add the same phrase to the existing normalized first-run smoke term loop:

```python
        FIRST_RUN_EXTERNAL_ADAPTER_SMOKE_PHRASE,
```

- [ ] **Step 4: Run focused tests to verify they fail before docs updates**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_external_tool_adapter_registry_docs_are_linked_and_bounded tests/test_cli_docs.py::test_readme_documents_manual_sample_flow_and_automated_smoke_boundary tests/test_cli_docs.py::test_first_run_guide_documents_paths_outputs_dashboard_reset_and_boundaries -q
```

Expected before doc updates: fail because README, CLI reference, and first-run
docs do not yet contain the new matrix rows or first-run smoke sentence.

## Task 2: Add Adapter Matrix And Smoke Documentation

**Files:**
- Modify: `README.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/first-run.md`
- Modify: `CHANGELOG.md`
- Modify: `docs/reviews/opencode-stage-74-code-review.md`

- [ ] **Step 1: Add matrix to README**

Immediately after the existing first `external-tool-adapters` prose block, add:

```markdown
Known adapter ids:

| Adapter id | Display/source name | Platform label | Format | Pattern |
| --- | --- | --- | --- | --- |
| `rednote_mcp` | Rednote MCP Export | `rednote` | `json` | `*.json` |
| `xiaohongshu_crawler` | Xiaohongshu Crawler Export | `xiaohongshu` | `csv` | `*.csv` |
| `instaloader` | Instaloader Export | `instagram` | `json` | `*.json` |
| `tiktok_api` | TikTok-Api Export | `tiktok` | `json` | `*.json` |
| `yt_dlp` | yt-dlp Metadata Export | `media` | `json` | `*.json` |
| `x_search_export` | X Search Export | `x` | `csv` | `*.csv` |
| `generic_community_export` | Generic Community Export | `community` | `csv` | `*.csv` |
```

- [ ] **Step 2: Add matrix to CLI reference**

Immediately after the `external-tool-adapters` bullet in
`docs/cli-reference.md`, add the same `Known adapter ids:` matrix.

- [ ] **Step 3: Add first-run smoke sentence to README and first-run guide**

In both automated smoke sections, add this sentence after the existing list of
sample row/report/trend/candidate checks:

```markdown
The automated first-run smoke also validates the external-tool adapter registry
JSON contract from `external-tool-adapters --format json` across all seven
adapters.
```

- [ ] **Step 4: Add changelog entry**

Under `[Unreleased]` `### Added`, add:

```markdown
- Stage 75 docs for the complete `external-tool-adapters` adapter matrix in
  `README.md` and `docs/cli-reference.md`, guarded by CLI docs tests. This is
  documentation/test-only and adds no runtime adapter or external-platform
  behavior.
```

- [ ] **Step 5: Add Stage 74 review correction note**

Append this note to `docs/reviews/opencode-stage-74-code-review.md`:

```markdown
### Correction Note

The M1 finding above referred to an earlier corrupted draft of
`docs/reviews/opencode-stage-74-plan-review.md`. The committed Stage 74
plan-review artifact is the cleaned single-review version, so M1 is resolved
and does not remain a release blocker.
```

- [ ] **Step 6: Re-run focused docs tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_external_tool_adapter_registry_docs_are_linked_and_bounded tests/test_cli_docs.py::test_readme_documents_manual_sample_flow_and_automated_smoke_boundary tests/test_cli_docs.py::test_first_run_guide_documents_paths_outputs_dashboard_reset_and_boundaries -q
```

Expected: pass.

## Task 3: Review, Verification, Commit, Publish

**Files:**
- Create: `docs/reviews/opencode-stage-75-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-75-code-review.md`
- Include Stage 75 spec/plan/review artifacts in commit.

- [ ] **Step 1: Run local verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_external_tool_adapter_registry_docs_are_linked_and_bounded tests/test_cli_docs.py::test_readme_documents_manual_sample_flow_and_automated_smoke_boundary tests/test_cli_docs.py::test_first_run_guide_documents_paths_outputs_dashboard_reset_and_boundaries -q
uv --no-config run --frozen pytest tests/test_cli_docs.py -q
uv --no-config run --frozen ruff check tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
uv --no-config run --frozen python scripts/check_release_hygiene.py
git diff --check
uv --no-config run --frozen pytest
```

Expected: pass.

- [ ] **Step 2: Request opencode code review**

Create `docs/reviews/opencode-stage-75-code-review-prompt.md` with the Stage 75
goal, touched files, implementation summary, and verification results. Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-75-code-review-prompt.md)" > docs/reviews/opencode-stage-75-code-review.md
```

Fix Critical/Important findings before proceeding.

- [ ] **Step 3: Commit**

Run:

```bash
git add README.md docs/cli-reference.md docs/first-run.md CHANGELOG.md tests/test_cli_docs.py docs/reviews/opencode-stage-74-code-review.md docs/superpowers/specs/2026-06-18-stage-75-adapter-docs-matrix-design.md docs/superpowers/plans/2026-06-18-stage-75-adapter-docs-matrix-plan.md docs/reviews/opencode-stage-75-plan-review-prompt.md docs/reviews/opencode-stage-75-plan-review.md docs/reviews/opencode-stage-75-code-review-prompt.md docs/reviews/opencode-stage-75-code-review.md
git commit -m "Document external adapter registry matrix"
```

- [ ] **Step 4: Publish and verify CI**

Use the GitHub Git Data API path if normal git HTTPS push remains unreliable.
Verify remote `main`, local `origin/main`, release hygiene, credential-free git
config, and GitHub Actions CI success.

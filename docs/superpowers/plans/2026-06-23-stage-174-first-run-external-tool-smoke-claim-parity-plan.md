# Stage 174 First-Run External Tool Smoke Claim Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make first-run documentation accurately describe every external-tool JSON contract surface that the automated first-run smoke already validates.

**Architecture:** Docs/test-only. Add one focused first-run docs test, update the shared first-run docs assertion in `tests/test_cli_docs.py`, then update the README and detailed first-run smoke paragraphs. Runtime smoke logic, CLI behavior, payloads, and source acquisition boundaries remain unchanged.

**Tech Stack:** Markdown, pytest, existing `tests/test_first_run_docs.py` helpers, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `tests/test_first_run_docs.py`
  - Add `test_first_run_docs_name_external_tool_smoke_contracts`.
- Modify: `tests/test_cli_docs.py`
  - Replace the old single adapter-registry smoke sentence with a tuple of
    first-run external-tool smoke claim fragments used for both README and the
    detailed first-run guide.
- Modify: `README.md`
  - Expand the automated smoke claim in the first-run section.
- Modify: `docs/first-run.md`
  - Expand the automated smoke claim in the "Installed-Wheel Smoke" section.
- Add: `docs/superpowers/specs/2026-06-23-stage-174-first-run-external-tool-smoke-claim-parity-design.md`
- Add: `docs/superpowers/plans/2026-06-23-stage-174-first-run-external-tool-smoke-claim-parity-plan.md`
- Add: `docs/reviews/opencode-stage-174-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-174-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-174-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-174-code-review.md`
- Add after release verification: `docs/reviews/opencode-stage-174-release-review-prompt.md`
- Add after release verification: `docs/reviews/opencode-stage-174-release-review.md`

## Task 1: Add RED First-Run Docs Test

**Files:**

- Modify: `tests/test_first_run_docs.py`

- [ ] **Step 1: Add the failing docs parity test**

Immediately after `test_first_run_docs_keep_local_sample_boundary`, add:

```python
def test_first_run_docs_name_external_tool_smoke_contracts() -> None:
    installed_smoke = _section(_read_first_run_doc(), "Installed-Wheel Smoke")
    normalized = _normalized(installed_smoke)

    for phrase in (
        "automated first-run smoke also validates local external-tool json contracts",
        "`external-tool-adapters --format json` across all eight adapters",
        "`external-tool-template --adapter rednote_mcp --format json`",
        "`external-tool-workflow --adapter rednote_mcp --format json`",
        "`external-tool-readiness --adapter rednote_mcp --format json`",
        "do not run adapters or upstream external/community tools",
        "do not call platform apis",
        "do not perform source acquisition",
    ):
        assert phrase in normalized
```

- [ ] **Step 2: Replace the shared CLI docs phrase constant with RED fragments**

In `tests/test_cli_docs.py`, replace `FIRST_RUN_EXTERNAL_ADAPTER_SMOKE_PHRASE`
with:

```python
FIRST_RUN_EXTERNAL_TOOL_SMOKE_PHRASES = (
    "The automated first-run smoke also validates local external-tool JSON contracts",
    "`external-tool-adapters --format json` across all eight adapters",
    "`external-tool-template --adapter rednote_mcp --format json`",
    "`external-tool-workflow --adapter rednote_mcp --format json`",
    "`external-tool-readiness --adapter rednote_mcp --format json`",
    "command-output contract checks only",
    "do not run adapters or upstream external/community tools",
    "do not call platform APIs",
    "do not perform source acquisition",
)
```

Then replace both uses of:

```python
FIRST_RUN_EXTERNAL_ADAPTER_SMOKE_PHRASE,
```

with:

```python
*FIRST_RUN_EXTERNAL_TOOL_SMOKE_PHRASES,
```

- [ ] **Step 3: Run RED checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_docs.py::test_first_run_docs_name_external_tool_smoke_contracts -q
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_readme_documents_manual_sample_flow_and_automated_smoke_boundary tests/test_cli_docs.py::test_first_run_guide_documents_paths_outputs_dashboard_reset_and_boundaries -q
```

Expected before docs updates: both commands fail because `README.md` and
`docs/first-run.md` currently name only the
`external-tool-adapters --format json` registry check and do not name the
template, workflow, readiness, or no-external-tool boundary terms near the smoke
claim.

## Task 2: Update First-Run Smoke Claim

**Files:**

- Modify: `README.md`
- Modify: `docs/first-run.md`

- [ ] **Step 1: Replace the incomplete smoke claim**

Replace:

```markdown
The automated first-run smoke also validates the external-tool adapter registry
JSON contract from `external-tool-adapters --format json` across all eight
adapters.
```

with:

```markdown
The automated first-run smoke also validates local external-tool JSON
contracts: `external-tool-adapters --format json` across all eight adapters,
plus the `external-tool-template --adapter rednote_mcp --format json`,
`external-tool-workflow --adapter rednote_mcp --format json`, and
`external-tool-readiness --adapter rednote_mcp --format json` outputs generated
with the `rednote_mcp` adapter. These are command-output contract checks only;
they do not run adapters or upstream external/community tools, do not call
platform APIs, and do not perform source acquisition.
```

Apply the replacement in both `README.md` and `docs/first-run.md`.

- [ ] **Step 2: Run GREEN focused checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_docs.py::test_first_run_docs_name_external_tool_smoke_contracts -q
uv --no-config run --frozen pytest tests/test_first_run_docs.py -q
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_readme_documents_manual_sample_flow_and_automated_smoke_boundary tests/test_cli_docs.py::test_first_run_guide_documents_paths_outputs_dashboard_reset_and_boundaries -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -k "external_tool or deterministic_local_command_sequence" -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen ruff check tests/test_first_run_docs.py tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_first_run_docs.py tests/test_cli_docs.py
```

Expected: all focused tests and checks pass.

## Task 3: Review, Release Gate, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-174-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-174-code-review.md`
- Add: `docs/reviews/opencode-stage-174-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-174-release-review.md`

- [ ] **Step 1: Create code review prompt**

Create `docs/reviews/opencode-stage-174-code-review-prompt.md` with a prompt
that asks local opencode to review the Stage 174 implementation. The prompt
must require the response to start with:

```text
# Stage 174 Code Review
```

- [ ] **Step 2: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-174-code-review-prompt.md)" > "$tmp_review"
sed -n '1,320p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-174-code-review.md
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

Create `docs/reviews/opencode-stage-174-release-review-prompt.md` requiring the
review body to start with:

```text
# Stage 174 Release Review
```

Then run the same temp-file `opencode run --model zhipuai-coding-plan/glm-5.2
--variant max` capture flow used for prior stages, copying the completed review
to `docs/reviews/opencode-stage-174-release-review.md`.

Expected: completed review output with no critical or important findings. Clean
the artifact if needed.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short
git add \
  docs/first-run.md \
  README.md \
  tests/test_first_run_docs.py \
  tests/test_cli_docs.py \
  docs/superpowers/specs/2026-06-23-stage-174-first-run-external-tool-smoke-claim-parity-design.md \
  docs/superpowers/plans/2026-06-23-stage-174-first-run-external-tool-smoke-claim-parity-plan.md \
  docs/reviews/opencode-stage-174-plan-review-prompt.md \
  docs/reviews/opencode-stage-174-plan-review.md \
  docs/reviews/opencode-stage-174-code-review-prompt.md \
  docs/reviews/opencode-stage-174-code-review.md \
  docs/reviews/opencode-stage-174-release-review-prompt.md \
  docs/reviews/opencode-stage-174-release-review.md
git commit -m "docs: clarify first-run external tool smoke"
git push origin main
```

Expected: commit succeeds and `main` pushes to GitHub.

## Self-Review Notes

- Spec coverage: Task 1 covers the RED docs guards, Task 2 covers the README
  and first-run docs wording update, and Task 3 covers review, release gate,
  commit, and push.
- Placeholder scan: no placeholders or deferred implementation notes.
- Boundary check: runtime smoke logic, CLI behavior, external-tool payloads,
  adapters, templates, workflows, readiness builders, source acquisition,
  connectors, scraping, browser automation, platform APIs, MCP execution, API
  keys, login/cookie behavior, monitoring, scheduling, demand proof, ranking,
  coverage verification, and compliance-review product features remain out of
  scope.

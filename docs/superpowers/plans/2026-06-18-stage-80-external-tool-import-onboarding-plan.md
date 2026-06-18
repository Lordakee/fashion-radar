# Stage 80 External Tool Import Onboarding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clarify the local external/community tool export import route from user-controlled CSV/JSON export directories into Fashion Radar review commands.

**Architecture:** Docs and docs drift tests only. The stage adds orientation text around existing local handoff commands and pins the route with tests; it does not change runtime CLI behavior or add source/platform capabilities.

**Tech Stack:** Markdown, pytest, uv, ruff.

**Review Protocol Note:** The current stage-local review instruction for Stage
80 is to use local opencode with `opencode run --model
zhipuai-coding-plan/glm-5.2 --variant max`. Keep that instruction in Stage 80
planning and review artifacts only. Do not alter `AGENTS.md`,
`docs/REVIEW_PROTOCOL.md`, or `docs/github-upload-checklist.md`. Public
`uv.lock` must remain free of mirror-bound URLs per `AGENTS.md`; the
pre-existing local `uv.lock` mirror rewrite is not part of this stage and must
not be staged.

---

## File Map

- Modify `README.md`
  - Add an external tool import path summary near the external tool handoff text.
- Modify `docs/community-signal-import.md`
  - Add `## External Tool Import Roadmap` before `## External Tool Handoff Templates`.
- Modify `docs/cli-reference.md`
  - Add one local import orientation paragraph under `## Local Import And Community Handoff`.
- Modify `tests/test_cli_docs.py`
  - Add docs drift tests for the external import route and boundaries.
- Modify `CHANGELOG.md`
  - Add Stage 80 entry.
- Add review/spec/plan artifacts:
  - `docs/superpowers/specs/2026-06-18-stage-80-external-tool-import-onboarding-design.md`
  - `docs/superpowers/plans/2026-06-18-stage-80-external-tool-import-onboarding-plan.md`
  - `docs/reviews/opencode-stage-80-plan-review-prompt.md`
  - `docs/reviews/opencode-stage-80-plan-review.md`
  - `docs/reviews/opencode-stage-80-code-review-prompt.md`
  - `docs/reviews/opencode-stage-80-code-review.md`
- Do not modify:
  - `src/`
  - `AGENTS.md`
  - `docs/REVIEW_PROTOCOL.md`
  - `docs/github-upload-checklist.md`
  - dependency manifests
  - `uv.lock`

## Task 1: Add Failing Docs Drift Tests

**Files:**
- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Add README external import path test**

Add near existing README external tool docs tests:

```python
def test_readme_external_tool_import_path_points_to_local_handoff_route() -> None:
    text = _read(README)
    normalized = _normalized_doc_text(README).casefold()

    for term in (
        "External Tool Import Path",
        "user-controlled external export directory",
        "sanitized CSV/JSON local file handoff",
        "external-tool-adapters",
        "external-tool-readiness",
        "external-tool-workflow",
        "community-signal-lint-dir",
        "community-candidates-dir",
        "community-handoff-check-dir",
        "import-signals-dir",
        "imported-review-workflow",
        "[docs/community-signal-import.md](docs/community-signal-import.md)",
    ):
        assert term in text

    for term in (
        "does not run upstream tools",
        "does not search platforms",
        "does not scrape",
        "does not call platform apis",
        "does not add connectors",
        "does not prove demand",
        "does not rank brands",
        "does not verify platform coverage",
    ):
        assert term in normalized
```

- [ ] **Step 2: Add community import roadmap test**

Add near community-signal-import docs tests:

```python
def test_community_signal_import_docs_have_external_tool_import_roadmap() -> None:
    text = _read(COMMUNITY_SIGNAL_IMPORT_DOC)
    normalized = _normalized_doc_text(COMMUNITY_SIGNAL_IMPORT_DOC).casefold()

    roadmap = text.split("## External Tool Import Roadmap", 1)[1].split(
        "## External Tool Handoff Templates",
        1,
    )[0]

    for term in (
        "| Phase | Existing Commands | Purpose |",
        "Discover",
        "`external-tool-adapters`, `external-tool-template`",
        "Prepare",
        "`external-tool-readiness`, `external-tool-workflow`",
        "Validate",
        "`community-signal-lint-dir`, `community-candidates-dir`, `community-handoff-check-dir`",
        "Import",
        "`import-signals-dir --dry-run`, `import-signals-dir`",
        "Review",
        "`imported-signals`, `candidates`, `trends`, `imported-review-workflow`",
        "user-controlled external export directory",
        "sanitized CSV/JSON local file handoff",
    ):
        assert term in roadmap

    for term in (
        "does not run upstream tools",
        "does not search platforms",
        "does not scrape",
        "does not call platform apis",
        "does not add connectors",
        "does not prove demand",
        "does not rank brands",
        "does not verify platform coverage",
    ):
        assert term in normalized
```

- [ ] **Step 3: Add CLI reference orientation test**

Add near `test_cli_reference_has_beginner_roadmap_with_existing_commands`:

```python
def test_cli_reference_local_import_section_has_external_tool_route() -> None:
    text = _read(CLI_REFERENCE)
    normalized = _normalized_doc_text(CLI_REFERENCE).casefold()

    section = text.split("## Local Import And Community Handoff", 1)[1].split(
        "Print adapter registry examples:",
        1,
    )[0]
    normalized_section = _normalized_text(section)

    for term in (
        "External tool import uses existing local commands only",
        "[community-signal-import.md](community-signal-import.md)",
        "user-controlled external export directory",
        "sanitized CSV/JSON local file handoff",
    ):
        assert term in section

    for term in (
        "external-tool-adapters -> external-tool-readiness -> external-tool-workflow",
        "community-signal-lint-dir -> community-candidates-dir -> community-handoff-check-dir",
        "import-signals-dir -> imported-review-workflow",
    ):
        assert term in normalized_section

    for term in (
        "does not run upstream tools",
        "does not search platforms",
        "does not scrape",
        "does not call platform apis",
        "does not add connectors",
    ):
        assert term in normalized
```

- [ ] **Step 4: Run tests and verify they fail before docs are updated**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_cli_docs.py::test_readme_external_tool_import_path_points_to_local_handoff_route \
  tests/test_cli_docs.py::test_community_signal_import_docs_have_external_tool_import_roadmap \
  tests/test_cli_docs.py::test_cli_reference_local_import_section_has_external_tool_route \
  -q
```

Expected before docs updates: failures because the new sections are missing.

## Task 2: Add Onboarding Docs

**Files:**
- Modify: `README.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/cli-reference.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add README external tool import path summary**

Near the existing external tool handoff template paragraph in `README.md`, add:

```markdown
### External Tool Import Path

When a user-controlled external export directory already contains sanitized
CSV/JSON rows, use [docs/community-signal-import.md](docs/community-signal-import.md)
for the local handoff route. The path is:
`external-tool-adapters -> external-tool-readiness -> external-tool-workflow ->
community-signal-lint-dir -> community-candidates-dir ->
community-handoff-check-dir -> import-signals-dir -> imported-review-workflow`.

Fashion Radar treats this as a sanitized CSV/JSON local file handoff from a
user-controlled external export directory. It does not run upstream tools, does
not search platforms, does not scrape, does not call platform APIs, does not add
connectors, does not prove demand, does not rank brands, and does not verify
platform coverage.
```

- [ ] **Step 2: Add community import roadmap section**

In `docs/community-signal-import.md`, before `## External Tool Handoff
Templates`, add:

```markdown
## External Tool Import Roadmap

Use this route when a user-controlled external export directory already contains
sanitized CSV/JSON local file handoff rows. The route uses existing local
commands only:

| Phase | Existing Commands | Purpose |
| --- | --- | --- |
| Discover | `external-tool-adapters`, `external-tool-template` | Inspect adapter labels, field mappings, example rows, and local handoff commands. |
| Prepare | `external-tool-readiness`, `external-tool-workflow` | Check local command availability and print the producer-facing workflow without running upstream tools. |
| Validate | `community-signal-lint-dir`, `community-candidates-dir`, `community-handoff-check-dir` | Lint matched files, preview candidate phrases, and review local handoff readiness before import. |
| Import | `import-signals-dir --dry-run`, `import-signals-dir` | Dry-run every matched local file, then import accepted local rows into SQLite. |
| Review | `imported-signals`, `candidates`, `trends`, `imported-review-workflow` | Review retained imported rows, local candidates, local trend deltas, and post-import review guidance. |

This roadmap does not run upstream tools, does not search platforms, does not
scrape, does not call platform APIs, does not add connectors, does not prove
demand, does not rank brands, and does not verify platform coverage.
```

- [ ] **Step 3: Add CLI reference orientation paragraph**

Under `## Local Import And Community Handoff`, before the command list, add:

```markdown
External tool import uses existing local commands only. For a user-controlled
external export directory that already contains a sanitized CSV/JSON local file
handoff, use [community-signal-import.md](community-signal-import.md) and follow:
`external-tool-adapters -> external-tool-readiness -> external-tool-workflow ->
community-signal-lint-dir -> community-candidates-dir ->
community-handoff-check-dir -> import-signals-dir -> imported-review-workflow`.
This route does not run upstream tools, does not search platforms, does not
scrape, does not call platform APIs, and does not add connectors.
```

- [ ] **Step 4: Add changelog entry**

Under `### Added` in `CHANGELOG.md`, add:

```markdown
- Stage 80 external tool import onboarding docs for the local route from a
  user-controlled external export directory to sanitized CSV/JSON handoff,
  directory lint, candidate preview, readiness review, import, and post-import
  review. This is docs/test-only and adds no upstream tool execution, platform
  search, scraping, platform APIs, connectors, demand proof, ranking, or
  platform coverage verification.
```

- [ ] **Step 5: Run focused docs checks**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_cli_docs.py::test_readme_external_tool_import_path_points_to_local_handoff_route \
  tests/test_cli_docs.py::test_community_signal_import_docs_have_external_tool_import_roadmap \
  tests/test_cli_docs.py::test_cli_reference_local_import_section_has_external_tool_route \
  -q
uv --no-config run --frozen pytest tests/test_cli_docs.py -q
uv --no-config run --frozen ruff check tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
git diff --check -- README.md docs/community-signal-import.md docs/cli-reference.md CHANGELOG.md tests/test_cli_docs.py
```

Expected after docs updates: all pass.

## Task 3: Review, Verification, Commit, And Publish

**Files:**
- Add: `docs/reviews/opencode-stage-80-plan-review-prompt.md`
- Add: `docs/reviews/opencode-stage-80-plan-review.md`
- Add: `docs/reviews/opencode-stage-80-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-80-code-review.md`

- [ ] **Step 1: Run opencode plan review before implementation**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-80-plan-review-prompt.md)" > docs/reviews/opencode-stage-80-plan-review.md
```

Fix Critical and Important findings before implementation.

- [ ] **Step 2: Run opencode code review after implementation**

Create `docs/reviews/opencode-stage-80-code-review-prompt.md` and run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-80-code-review-prompt.md)" > docs/reviews/opencode-stage-80-code-review.md
```

Fix Critical and Important findings before release verification.

- [ ] **Step 3: Run full verification**

Because this workspace may carry an out-of-stage mirror-rewritten `uv.lock`,
preserve that local file and temporarily restore the public HEAD lock before
running `UV_NO_CONFIG=1 uv lock --check`:

```bash
stage80_uv_lock_backup="$(mktemp)"
cp uv.lock "$stage80_uv_lock_backup"
git show HEAD:uv.lock > uv.lock
```

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
tmp_public_lock="$(mktemp)"
git show HEAD:uv.lock > "$tmp_public_lock"
! rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' "$tmp_public_lock"
rm -f "$tmp_public_lock"
! git diff --cached --name-only | rg -x 'uv.lock'
git diff --check
```

Restore the local mirror lock after verification and keep it unstaged:

```bash
cp "$stage80_uv_lock_backup" uv.lock
rm -f "$stage80_uv_lock_backup"
! git diff --cached --name-only | rg -x 'uv.lock'
```

- [ ] **Step 4: Stage only Stage 80 files**

Run:

```bash
git add README.md \
  docs/community-signal-import.md \
  docs/cli-reference.md \
  tests/test_cli_docs.py \
  CHANGELOG.md \
  docs/superpowers/specs/2026-06-18-stage-80-external-tool-import-onboarding-design.md \
  docs/superpowers/plans/2026-06-18-stage-80-external-tool-import-onboarding-plan.md \
  docs/reviews/opencode-stage-80-plan-review-prompt.md \
  docs/reviews/opencode-stage-80-plan-review.md \
  docs/reviews/opencode-stage-80-code-review-prompt.md \
  docs/reviews/opencode-stage-80-code-review.md
```

Do not stage `AGENTS.md`, `docs/REVIEW_PROTOCOL.md`,
`docs/github-upload-checklist.md`, dependency manifests, `src/`, or `uv.lock`.

Then run:

```bash
! git diff --cached --name-only | rg -x 'uv.lock'
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --cached --check
git grep --cached -n -E 'gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{82,255}|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' -- . ':!uv.lock' && exit 1 || true
```

- [ ] **Step 5: Commit and publish through GitHub Git Data API**

Commit:

```bash
git commit -m "Document external tool import path"
```

Publish using the existing GitHub Git Data API flow with token read only from
`/home/ubuntu/.config/fashion-radar/github-token`, `force:false`, no token in
remote URLs, and no persistent `http.*.extraheader`.

- [ ] **Step 6: Verify remote and CI**

Run:

```bash
git fetch origin main
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
test "$(git remote get-url origin)" = "https://github.com/Lordakee/fashion-radar.git"
git config --show-origin --get-regexp '^http\..*\.extraheader$' && exit 1 || true
git config --show-origin --list | rg -i 'gh[pousr]_|github_pat_|x-access-token|authorization' && exit 1 || true
! git diff --cached --name-only | rg -x 'uv.lock'
```

Poll the latest `main` GitHub Actions run and require `completed success`.

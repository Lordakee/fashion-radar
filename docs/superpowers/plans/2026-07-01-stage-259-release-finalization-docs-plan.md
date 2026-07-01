# Stage 259 Release Finalization Docs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the final v0.1.0 release-documentation drift around generated HTML reports, Stage 256-258 release notes, the `0.1.0` changelog cut, and the release gate before tagging.

**Architecture:** This is a docs/test/review-only release-finalization node. It does not change runtime code, collectors, report rendering, workflow behavior, dependencies, packaging metadata, or `uv.lock`; it tightens release-facing docs and docs guards so the public repo describes the current collect -> match -> report output accurately before release review.

**Tech Stack:** Markdown docs, pytest docs guards, existing release hygiene scripts, `uv --no-config run --frozen`, package build checks, Claude Code primary review with opencode GLM 5.2 max fallback.

---

## Files

- Modify `README.md`
  - Update the opening summary from Markdown/JSON-only reports to Markdown, JSON, and companion HTML reports.
- Modify `docs/architecture.md`
  - Update the flow and Reports component to say Markdown/JSON/HTML reports.
- Modify `docs/PROJECT_BRIEF.md`
  - Update product-positioning and v0.1.0 promise wording to include the companion HTML report output now shipped by the tool.
- Modify `CHANGELOG.md`
  - Cut a dated `0.1.0` section for July 1, 2026 and include concise entries for Stage 256 companion HTML reports, the Stage 256 HTML escaping fix, Stage 257 HTML recent news and buyer brands pack, and Stage 258 HTML artifact hygiene parity.
- Modify `docs/github-upload-checklist.md`
  - Add a narrow pre-tag note that tagging is user-controlled and should happen only after the release gate, changelog cut, final review, and clean pushed branch.
- Modify `tests/test_cli_docs.py`
  - Add docs guards for README/architecture/CHANGELOG release-facing HTML report wording and the pre-tag checklist note.
- Modify `tests/test_project_brief_docs.py`
  - Add a docs guard for PROJECT_BRIEF report-output wording.
- Create review records under `docs/reviews/`.

## Scope Out

- No runtime code changes.
- No changes to `src/`, `scripts/`, configs, examples, package metadata, `pyproject.toml`, or `uv.lock`.
- No new collectors, social/platform integrations, scraping, browser automation, platform APIs, scheduling, source acquisition, demand proof, ranking semantics, or platform coverage verification.
- No generated report examples, screenshots, build artifacts, local SQLite databases, or release artifact uploads committed to the repo.
- No tag creation in this node unless explicitly requested after the final release review passes.

## Tasks

### Task 1: Write Release-Docs Drift Guards

**Files:**
- Modify: `tests/test_cli_docs.py`
- Modify: `tests/test_project_brief_docs.py`

- [ ] **Step 1: Add README/architecture/changelog guard tests**

In `tests/test_cli_docs.py`, add a focused test near the existing README and release-documentation tests:

```python
def test_release_docs_describe_current_html_report_outputs() -> None:
    readme = _normalized_doc_text(README)
    architecture = _normalized_doc_text(ARCHITECTURE_DOC)
    changelog = _normalized_doc_text(CHANGELOG)
    checklist = _normalized_doc_text(UPLOAD_CHECKLIST)

    assert "## [0.1.0] - 2026-07-01" in _read(CHANGELOG)

    for phrase in (
        "Markdown, JSON, and companion HTML reports",
        "daily Markdown, JSON, and companion HTML reports",
    ):
        assert phrase.casefold() in readme.casefold()

    for phrase in (
        "write Markdown/JSON/HTML reports",
        "Markdown, JSON, and companion HTML daily reports",
    ):
        assert phrase.casefold() in architecture.casefold()

    for phrase in (
        "Stage 256 adds styled companion HTML reports",
        "Stage 256 fix escapes all generated HTML report values",
        "Stage 257 adds deterministic latest collected news to HTML reports",
        "configs/entity-packs/buyer-brands.example.yaml",
        "Stage 258 aligns first-run smoke, cleanup, data-retention, and docs guards with generated HTML report artifacts",
    ):
        assert phrase.casefold() in changelog.casefold()

    for phrase in (
        "Tagging is user-controlled",
        "only after the release gate passes",
        "the changelog has a dated `0.1.0` section",
        "`HEAD == origin/main`",
    ):
        assert phrase.casefold() in checklist.casefold()
```

- [ ] **Step 2: Add PROJECT_BRIEF report-output guard**

In `tests/test_project_brief_docs.py`, add:

```python
def test_project_brief_docs_describe_current_report_outputs() -> None:
    normalized = _normalized(_read_project_brief_doc())

    for phrase in (
        "Generate a daily Markdown/JSON/HTML report.",
        "Markdown, JSON, and companion HTML report generation.",
        "Daily Markdown, JSON, and companion HTML reports.",
    ):
        assert phrase.casefold() in normalized
```

- [ ] **Step 3: Run the focused tests and verify they fail**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_release_docs_describe_current_html_report_outputs tests/test_project_brief_docs.py::test_project_brief_docs_describe_current_report_outputs -q
```

Expected before docs edits: both tests fail because the current release-facing docs still contain Markdown/JSON-only wording, the changelog lacks a dated `0.1.0` section with Stage 256-258 release notes, and the upload checklist lacks an explicit user-controlled tag note.

### Task 2: Update Release-Facing Docs

**Files:**
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/PROJECT_BRIEF.md`
- Modify: `CHANGELOG.md`
- Modify: `docs/github-upload-checklist.md`

- [ ] **Step 1: Update README opening summary**

Change:

```text
Markdown/JSON reports and a read-only dashboard.
```

to:

```text
Markdown, JSON, and companion HTML reports and a read-only dashboard.
```

- [ ] **Step 2: Update architecture report flow and component wording**

In `docs/architecture.md`, change:

```text
-> write Markdown/JSON reports
```

to:

```text
-> write Markdown/JSON/HTML reports
```

and change the Reports component sentence from Markdown and JSON only to:

```text
- **Reports:** Markdown, JSON, and companion HTML daily reports rendered from packaged templates and local report models.
```

Preserve nearby source-attribution and boundary wording.

- [ ] **Step 3: Update project brief report-output wording**

In `docs/PROJECT_BRIEF.md`, update the three report-output bullets/sentences to:

```text
5. Generate a daily Markdown/JSON/HTML report.
```

```text
- Markdown, JSON, and companion HTML report generation.
```

```text
- Daily Markdown, JSON, and companion HTML reports.
```

- [ ] **Step 4: Cut CHANGELOG 0.1.0 entries**

Keep `## [Unreleased]` present for future work, but add a dated section directly
below it:

```markdown
## [0.1.0] - 2026-07-01
```

Under the new `## [0.1.0] - 2026-07-01` section, include the existing
Unreleased content plus the Stage 256-258 additions. Add these concise entries.

Under `### Added`:

```markdown
- Stage 257 adds deterministic latest collected news to HTML reports and the
  optional local `configs/entity-packs/buyer-brands.example.yaml` pack for buyer
  brands, Chinese designer brands, and bag/shoe trend terms.
- Stage 256 adds styled companion HTML reports alongside Markdown and JSON
  reports, including CLI output for the generated HTML path.
```

Under `### Fixed`:

```markdown
- Stage 258 aligns first-run smoke, cleanup, data-retention, and docs guards
  with generated HTML report artifacts so the companion HTML file is treated
  consistently with Markdown and JSON outputs.
- Stage 256 fix escapes all generated HTML report values and keeps unsafe URLs
  from being linked in the companion HTML report.
```

Keep the entries bounded: no platform coverage, demand proof, scraping, or connector claims.

- [ ] **Step 5: Add pre-tag note to upload checklist**

In `docs/github-upload-checklist.md`, add a short section after the "Before
Upload" command guidance:

```markdown
## Before Tagging

Tagging is user-controlled. Create or push a `v0.1.0` tag only after the
release gate passes, the changelog has a dated `0.1.0` section, final release
review has no Critical or Important blockers, and `HEAD == origin/main` on a
clean branch.
```

Do not add commands that create tags; this node documents the boundary only.

- [ ] **Step 6: Run focused tests and verify they pass**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_release_docs_describe_current_html_report_outputs tests/test_project_brief_docs.py::test_project_brief_docs_describe_current_report_outputs -q
```

Expected: both tests pass.

### Task 3: Focused Verification And Code Review

**Files:**
- Create: `docs/reviews/claude-code-stage-259-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-259-code-review.md`
- Create: `docs/reviews/opencode-stage-259-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-259-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py tests/test_project_brief_docs.py tests/test_architecture_boundary_docs.py -q
uv --no-config run --frozen ruff check tests/test_cli_docs.py tests/test_project_brief_docs.py
uv --no-config run --frozen ruff format --check tests/test_cli_docs.py tests/test_project_brief_docs.py
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --check
```

Expected: all commands pass.

- [ ] **Step 2: Request code/docs review**

Use Claude Code primary review first:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-259-code-review-prompt.md)"
```

If Claude Code is unavailable, record that honestly and use opencode fallback:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-259-code-review-prompt.md)"
```

- [ ] **Step 3: Fix Critical and Important findings only**

Evaluate review findings technically. Fix any valid Critical or Important issues, then rerun focused verification.

### Task 4: Full Release Gate And Push

**Files:**
- Create: `docs/reviews/claude-code-stage-259-release-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-259-release-review.md`
- Create: `docs/reviews/opencode-stage-259-release-review-prompt.md`
- Create: `docs/reviews/opencode-stage-259-release-review.md`

- [ ] **Step 1: Run full release gate**

Run:

```bash
git status --short --untracked-files=all
git status --ignored --short
git diff --check
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
git diff --exit-code -- uv.lock pyproject.toml
```

Then run package build and archive validation:

```bash
tmp_build="$(mktemp -d)"
uv --no-config build --out-dir "$tmp_build"
uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"
```

Then run installed-wheel smoke:

```bash
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
tmp_run="$(mktemp -d)"
"$tmp_env/venv/bin/fashion-radar" --help
"$tmp_env/venv/bin/python" -m fashion_radar --help
"$tmp_env/venv/bin/fashion-radar" init --config-dir "$tmp_run/config" --data-dir "$tmp_run/data" --reports-dir "$tmp_run/reports"
"$tmp_env/venv/bin/fashion-radar" doctor --config-dir "$tmp_run/config" --data-dir "$tmp_run/data" --reports-dir "$tmp_run/reports"
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
"$tmp_env/venv/bin/python" -c "from importlib import resources; text = resources.files('fashion_radar.templates').joinpath('daily_report.md').read_text(encoding='utf-8'); assert 'Fashion Radar Daily Report' in text"
```

Then run dashboard extra import smoke from the built wheel without launching
Streamlit:

```bash
tmp_dash="$(mktemp -d)"
uv venv "$tmp_dash/venv"
wheel_path="$(ls "$tmp_build"/*.whl | head -n 1)"
uv pip install --python "$tmp_dash/venv/bin/python" "${wheel_path}[dashboard]"
"$tmp_dash/venv/bin/python" -c "import fashion_radar.dashboard.app; import fashion_radar.dashboard.queries"
```

Expected: all commands pass. Do not commit `tmp_build`, `tmp_env`, `tmp_run`,
or `tmp_dash`; they live under `/tmp`.

- [ ] **Step 2: Request release review**

Use Claude Code primary release review first. If unavailable, record it and use opencode fallback.

- [ ] **Step 3: Commit and push**

If release review has no valid Critical or Important blockers and the full gate passes:

```bash
git add README.md docs/architecture.md docs/PROJECT_BRIEF.md docs/github-upload-checklist.md CHANGELOG.md tests/test_cli_docs.py tests/test_project_brief_docs.py docs/superpowers/plans/2026-07-01-stage-259-release-finalization-docs-plan.md docs/reviews/claude-code-stage-259-*.md docs/reviews/opencode-stage-259-*.md
git commit -m "Stage 259: finalize release docs and gate"
git push origin main
```

Expected after push:

```bash
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
```

The branch is clean and `HEAD == origin/main`.

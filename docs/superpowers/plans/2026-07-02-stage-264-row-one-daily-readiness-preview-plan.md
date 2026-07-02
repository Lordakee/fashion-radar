# Stage 264 ROW ONE Daily Readiness & Preview Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a daily readiness layer and preview command so ROW ONE clearly tells the user whether today's generated edition is ready to open.

**Architecture:** Keep ROW ONE as a local static site generator. Add shared ROW ONE utility helpers, add a derived readiness helper from existing `RowOneEdition`, render the readiness summary into the homepage, expose it through a new `row-one preview` CLI command, and extend first-run/package guardrails without changing source collection, matching, scoring, ranking, scheduling semantics, or the `row-one-app/v1` JSON contract.

**Tech Stack:** Python 3.11+, existing Typer CLI, existing Pydantic ROW ONE models, static HTML/CSS/JS strings, stdlib path/time handling, pytest, Ruff, Claude Code/opencode review gates.

---

## Stage Boundary

Stage 264 closes the ROW ONE daily-readiness gap in the `collect -> match -> report -> ROW ONE` path. Stages 260-263 already generate the site, detail pages, reader orientation, editorial synthesis, schedule snippets, and the versioned app JSON contract. This stage adds readiness visibility and preview ergonomics only.

This stage does not add new source acquisition, social scraping, browser automation, platform APIs, account/session behavior, translation, LLM calls, image generation, paid APIs, remote deployment, public hosting, authentication, scoring changes, demand proof, platform coverage verification, or compliance-review product behavior.

## Files And Artifacts

- Create: `src/fashion_radar/row_one/readiness.py`
- Create: `src/fashion_radar/row_one/utils.py`
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `src/fashion_radar/row_one/__init__.py`
- Modify: `src/fashion_radar/workflows.py`
- Modify: `src/fashion_radar/cli.py`
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `scripts/check_package_archives.py`
- Modify: `tests/test_row_one_render.py`
- Modify: `tests/test_row_one_cli.py`
- Modify: `tests/test_package_archives.py`
- Modify: `docs/row-one.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/github-upload-checklist.md`
- Create: `tests/test_row_one_readiness.py`
- Create: `docs/superpowers/specs/2026-07-02-stage-264-row-one-daily-readiness-preview-design.md`
- Create: `docs/superpowers/plans/2026-07-02-stage-264-row-one-daily-readiness-preview-plan.md`
- Create: `docs/reviews/claude-code-stage-264-plan-review-prompt.md`
- Create after review: `docs/reviews/claude-code-stage-264-plan-review.md`
- Create: `docs/reviews/opencode-stage-264-plan-review-prompt.md`
- Create after review: `docs/reviews/opencode-stage-264-plan-review.md`
- Create after implementation: `docs/reviews/claude-code-stage-264-code-review-prompt.md`
- Create after implementation if Claude completes: `docs/reviews/claude-code-stage-264-code-review.md`
- Create if fallback needed: `docs/reviews/opencode-stage-264-code-review-prompt.md`
- Create if fallback needed: `docs/reviews/opencode-stage-264-code-review.md`
- Create before push: `docs/reviews/claude-code-stage-264-release-review-prompt.md`
- Create before push if Claude completes: `docs/reviews/claude-code-stage-264-release-review.md`
- Create if fallback needed: `docs/reviews/opencode-stage-264-release-review-prompt.md`
- Create if fallback needed: `docs/reviews/opencode-stage-264-release-review.md`

## Task 1: Add Readiness Summary Model And Tests

**Files:**
- Create: `src/fashion_radar/row_one/utils.py`
- Create: `src/fashion_radar/row_one/readiness.py`
- Modify: `src/fashion_radar/row_one/__init__.py`
- Create: `tests/test_row_one_readiness.py`

- [ ] **Step 1: Write failing readiness tests**

Create `tests/test_row_one_readiness.py` using `_edition()` from `tests/test_row_one_render.py`:

```python
from __future__ import annotations

from fashion_radar.row_one.readiness import build_row_one_readiness
from tests.test_row_one_render import _edition


def test_build_row_one_readiness_counts_only_safe_evidence_links() -> None:
    readiness = build_row_one_readiness(_edition())

    assert readiness.story_count == 1
    assert readiness.section_count == 2
    assert readiness.safe_evidence_count == 1
    assert readiness.empty_section_keys == ["brand_moves"]
    assert readiness.empty_sections.en == "Brand Moves"
    assert readiness.empty_sections.zh == "品牌动态"
    assert readiness.readiness.en == "ready"
    assert readiness.readiness.zh == "可阅读"
    assert readiness.generated_at == "2026-07-02T04:00:00Z"
    assert readiness.edition_date == "2026-07-02"
```

Add an empty-edition test:

```python
def test_build_row_one_readiness_marks_empty_edition() -> None:
    edition = _edition()
    edition.stories = []

    readiness = build_row_one_readiness(edition)

    assert readiness.story_count == 0
    assert readiness.safe_evidence_count == 0
    assert readiness.empty_section_keys == ["top_stories", "brand_moves"]
    assert readiness.empty_sections.en == "Top Stories, Brand Moves"
    assert readiness.empty_sections.zh == "今日重点，品牌动态"
    assert readiness.readiness.en == "empty"
    assert readiness.readiness.zh == "暂无故事"
```

- [ ] **Step 2: Run tests and confirm RED**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_readiness.py -q
```

Expected: FAIL because `fashion_radar.row_one.readiness` does not exist.

- [ ] **Step 3: Implement readiness helper**

Create `src/fashion_radar/row_one/utils.py` first. This module must not import
from `templates.py`, `render.py`, or `readiness.py`.

```python
from __future__ import annotations

from datetime import UTC, datetime
from urllib.parse import urlsplit


def safe_external_url(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return url


def isoformat_z(value: datetime) -> str:
    return utc_datetime(value).isoformat().replace("+00:00", "Z")


def utc_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
```

Then create `src/fashion_radar/row_one/readiness.py`:

```python
from __future__ import annotations

from dataclasses import dataclass

from fashion_radar.row_one.models import LocalizedText, RowOneEdition
from fashion_radar.row_one.utils import isoformat_z, safe_external_url, utc_datetime


@dataclass(frozen=True)
class RowOneReadiness:
    generated_at: str
    edition_date: str
    story_count: int
    section_count: int
    safe_evidence_count: int
    empty_section_keys: list[str]
    empty_sections: LocalizedText
    readiness: LocalizedText


def build_row_one_readiness(edition: RowOneEdition) -> RowOneReadiness:
    empty_sections = [
        section for section in edition.sections if not edition.section_stories(section.key)
    ]
    safe_evidence_count = sum(
        1
        for story in edition.stories
        for link in story.evidence
        if safe_external_url(link.url) is not None
    )
    story_count = len(edition.stories)
    return RowOneReadiness(
        generated_at=isoformat_z(edition.generated_at),
        edition_date=utc_datetime(edition.edition_date).date().isoformat(),
        story_count=story_count,
        section_count=len(edition.sections),
        safe_evidence_count=safe_evidence_count,
        empty_section_keys=[section.key for section in empty_sections],
        empty_sections=LocalizedText(
            zh="，".join(section.title.zh for section in empty_sections) or "无",
            en=", ".join(section.title.en for section in empty_sections) or "none",
        ),
        readiness=LocalizedText(zh="可阅读" if story_count else "暂无故事", en="ready" if story_count else "empty"),
    )
```

Update `templates.py` and `render.py` in later tasks to import the shared helpers
from `row_one.utils`, so there is no `templates -> readiness -> templates`
circular import.

- [ ] **Step 4: Export readiness helper**

Add `RowOneReadiness` and `build_row_one_readiness` to `src/fashion_radar/row_one/__init__.py`.

- [ ] **Step 5: Verify Task 1**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_readiness.py -q
```

Expected: PASS.

## Task 2: Render Latest Edition Status Strip

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Write failing render tests**

In `tests/test_row_one_render.py`, add:

```python
def test_render_row_one_site_includes_latest_edition_status_strip(tmp_path) -> None:
    render_row_one_site(_edition(), tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert 'class="edition-status"' in index_html
    assert "Latest Edition" in index_html
    assert "今日状态" in index_html
    assert "Generated" in index_html
    assert "2026-07-02T04:00:00Z" in index_html
    assert "Stories" in index_html
    assert "1" in index_html
    assert "Evidence links" in index_html
    assert "1" in index_html
    assert "Empty sections" in index_html
    assert "Brand Moves" in index_html
    assert "品牌动态" in index_html
    assert "ready" in index_html
    assert "可阅读" in index_html
```

Add an empty-edition assertion:

```python
def test_render_row_one_site_status_strip_handles_empty_edition(tmp_path) -> None:
    edition = _edition()
    edition.stories = []

    render_row_one_site(edition, tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert "empty" in index_html
    assert "暂无故事" in index_html
    assert "0" in index_html
    assert "Top Stories, Brand Moves" in index_html
```

- [ ] **Step 2: Run tests and confirm RED**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_includes_latest_edition_status_strip tests/test_row_one_render.py::test_render_row_one_site_status_strip_handles_empty_edition -q
```

Expected: FAIL because the status strip is not rendered.

- [ ] **Step 3: Render status strip after masthead summary**

In `templates.py`, import `build_row_one_readiness` and call:

```python
status_strip = _render_edition_status(edition)
```

Insert `{status_strip}` between `</header>` and `<main>`.

Add:

```python
def _render_edition_status(edition: RowOneEdition) -> str:
    readiness = build_row_one_readiness(edition)
    return f"""<section class="edition-status" aria-label="Latest edition status">
  <div>
    <p class="story-section">
      <span data-lang="en">Latest Edition</span>
      <span data-lang="zh">今日状态</span>
    </p>
    <strong>
      <span data-lang="en">{_esc(readiness.readiness.en)}</span>
      <span data-lang="zh">{_esc(readiness.readiness.zh)}</span>
    </strong>
  </div>
  {_render_status_metric("Generated", "生成时间", readiness.generated_at, readiness.generated_at)}
  {_render_status_metric("Edition date", "刊期", readiness.edition_date, readiness.edition_date)}
  {_render_status_metric("Stories", "故事", str(readiness.story_count), f"{readiness.story_count} 条")}
  {_render_status_metric("Evidence links", "证据链接", str(readiness.safe_evidence_count), f"{readiness.safe_evidence_count} 条")}
  {_render_status_metric("Empty sections", "空栏目", readiness.empty_sections.en, readiness.empty_sections.zh)}
</section>"""
```

Add `_render_status_metric()` below it.

Use this helper shape so all dynamic values remain escaped:

```python
def _render_status_metric(label_en: str, label_zh: str, value_en: str, value_zh: str) -> str:
    return f"""<div class="edition-status-metric">
    <span class="edition-status-label">
      <span data-lang="en">{_esc(label_en)}</span>
      <span data-lang="zh">{_esc(label_zh)}</span>
    </span>
    <strong>
      <span data-lang="en">{_esc(value_en)}</span>
      <span data-lang="zh">{_esc(value_zh)}</span>
    </strong>
  </div>"""
```

- [ ] **Step 4: Add CSS for the status strip**

In `row_one_css()`, add `.edition-status` rules with a responsive grid, thin borders, compact labels, and no card nesting. On mobile it should collapse to one column.

- [ ] **Step 5: Verify Task 2**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_row_one_readiness.py -q
```

Expected: PASS.

## Task 3: Add `row-one preview` CLI Command

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `src/fashion_radar/workflows.py`
- Modify: `tests/test_row_one_cli.py`

- [ ] **Step 1: Write failing CLI tests**

In `tests/test_row_one_cli.py`, reuse the existing `_write_minimal_config`
pattern and inline `CliRunner().invoke(app, ...)` style. Add:

```python
def test_row_one_preview_builds_site_and_prints_readiness(tmp_path) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    _write_minimal_config(config_dir)
    output_dir = tmp_path / "row-one-site"

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "preview",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--output-dir",
            str(output_dir),
            "--as-of",
            "2026-07-02T04:00:00Z",
            "--latest-only",
            "--dry-run-serve-url",
        ],
    )

    assert result.exit_code == 0, result.output
    assert (output_dir / "index.html").exists()
    assert (output_dir / "data" / "edition.json").exists()
    assert "ROW ONE preview" in result.output
    assert f"Site: {output_dir / 'index.html'}" in result.output
    assert f"JSON: {output_dir / 'data' / 'edition.json'}" in result.output
    assert "Stories:" in result.output
    assert "Sections:" in result.output
    assert "Evidence links:" in result.output
    assert "Empty sections:" in result.output
    assert "Generated at:" in result.output
    assert "Readiness:" in result.output
    assert "Open:" in result.output
```

Add a help test asserting `row-one preview --help` appears in CLI help output.

- [ ] **Step 2: Run CLI tests and confirm RED**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_cli.py::test_row_one_preview_builds_site_and_prints_readiness tests/test_row_one_cli.py::test_row_one_preview_help_is_discoverable -q
```

Expected: FAIL because `preview` does not exist.

- [ ] **Step 3: Implement `row_one_preview` command**

Add `@row_one_app.command(name="preview")` next to build/serve/schedule. Reuse the same config-loading code as `row_one_build`.

First extend `RowOneRenderResult` in `render.py` with the internal edition:

```python
@dataclass(frozen=True)
class RowOneRenderResult:
    output_dir: Path
    index_path: Path
    story_count: int
    edition: RowOneEdition
```

Update `render_row_one_site()` to set `edition=edition`. Because this is an
internal Python dataclass only, it does not change the `row-one-app/v1` JSON
contract. `workflows.write_row_one_site_files()` already returns the render
result, so no workflow signature change is needed.

Then avoid duplicate CLI build logic by extracting:

```python
def _write_row_one_site_from_cli_options(...) -> RowOneRenderResult:
    ...
```

Use it from both `row_one_build()` and `row_one_preview()`. Compute readiness in
preview with `build_row_one_readiness(result.edition)`.

After building, print:

```python
typer.echo("ROW ONE preview")
typer.echo(f"Site: {result.index_path}")
typer.echo(f"JSON: {result.output_dir / 'data' / 'edition.json'}")
typer.echo(f"Stories: {readiness.story_count}")
typer.echo(f"Sections: {readiness.section_count}")
typer.echo(f"Evidence links: {readiness.safe_evidence_count}")
typer.echo(f"Empty sections: {readiness.empty_sections.en}")
typer.echo(f"Generated at: {readiness.generated_at}")
typer.echo(f"Readiness: {readiness.readiness.en}")
```

If `--dry-run-serve-url` is true, print `format_row_one_site_access_message(host, port)`.

- [ ] **Step 4: Verify Task 3**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_cli.py tests/test_row_one_readiness.py -q
```

Expected: PASS.

## Task 4: Extend First-Run And Package Guardrails

**Files:**
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `scripts/check_package_archives.py`
- Modify: `tests/test_package_archives.py`

- [ ] **Step 1: Write failing guardrail tests**

In `tests/test_package_archives.py`, add ROW ONE required sdist files:

```python
"docs/row-one.md",
"src/fashion_radar/row_one/__init__.py",
"src/fashion_radar/row_one/edition.py",
"src/fashion_radar/row_one/models.py",
"src/fashion_radar/row_one/readiness.py",
"src/fashion_radar/row_one/render.py",
"src/fashion_radar/row_one/server.py",
"src/fashion_radar/row_one/templates.py",
"src/fashion_radar/row_one/utils.py",
```

Add a failure test that removes `docs/row-one.md` from the fixture and expects a
missing sdist required path error.

- [ ] **Step 2: Run package test and confirm RED**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q
```

Expected: FAIL until the checker's `SDIST_REQUIRED_PATHS` includes the new files.

- [ ] **Step 3: Update package archive checker**

Add the same ROW ONE paths to `SDIST_REQUIRED_PATHS` in
`scripts/check_package_archives.py`. Explicitly extend the existing module-level
`SDIST_FILES` list in `tests/test_package_archives.py` with the same paths, so
the fixture and checker remain synchronized.

- [ ] **Step 4: Add first-run smoke checks**

In `scripts/check_first_run_smoke.py`, add checks that run:

```bash
fashion-radar row-one --help
fashion-radar row-one build --help
fashion-radar row-one serve --help
fashion-radar row-one schedule --help
fashion-radar row-one preview --help
fashion-radar row-one schedule --time 04:00
```

Assert the schedule output contains `fashion-radar run` before
`fashion-radar row-one build --latest-only`.

- [ ] **Step 5: Verify Task 4**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

Expected: PASS.

## Task 5: Update Documentation

**Files:**
- Modify: `docs/row-one.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Add failing docs tests**

In `tests/test_row_one_docs.py`, add assertions that docs mention:

- `row-one preview`;
- `Latest Edition` status strip;
- readiness labels `ready` and `empty`;
- `Stories`, `Evidence links`, and `Empty sections`;
- `row-one preview --dry-run-serve-url`;
- first-run smoke covers ROW ONE preview help.

- [ ] **Step 2: Run docs tests and confirm RED**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_docs.py -q
```

Expected: FAIL until docs are updated.

- [ ] **Step 3: Update docs**

Update:

- `docs/row-one.md`: add "Daily Readiness And Preview" section.
- `docs/cli-reference.md`: document `row-one preview` options.
- `docs/github-upload-checklist.md`: mention `row-one preview --help` and first-run smoke coverage.

- [ ] **Step 4: Verify Task 5**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_docs.py -q
```

Expected: PASS.

## Task 6: Code Review, Release Verification, Commit, Push

**Files:**
- Create review artifacts under `docs/reviews/`.

- [ ] **Step 1: Run focused verification**

Run:

```bash
git diff --check
UV_NO_CONFIG=1 uv lock --check
uv --no-config run --frozen ruff check src/fashion_radar/row_one src/fashion_radar/cli.py scripts/check_first_run_smoke.py scripts/check_package_archives.py tests/test_row_one*.py tests/test_package_archives.py
uv --no-config run --frozen ruff format --check src/fashion_radar/row_one src/fashion_radar/cli.py scripts/check_first_run_smoke.py scripts/check_package_archives.py tests/test_row_one*.py tests/test_package_archives.py
uv --no-config run --frozen pytest tests/test_row_one_readiness.py tests/test_row_one_render.py tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_row_one_app_contract.py tests/test_package_archives.py -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

- [ ] **Step 2: Request Claude Code code review**

Create `docs/reviews/claude-code-stage-264-code-review-prompt.md` describing the implementation and ask Claude Code to review changed code in read-only plan mode:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-264-code-review-prompt.md)" > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-264-code-review.md
rm -f "$tmp_review"
```

If Claude Code times out or fails, create an opencode fallback prompt and review with:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-264-code-review-prompt.md)" > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-264-code-review.md
rm -f "$tmp_review"
```

- [ ] **Step 3: Fix critical and important findings**

Apply any required fixes, then rerun focused verification and request rereview if needed.

- [ ] **Step 4: Run release gate**

Run:

```bash
git diff --check
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config run --frozen pytest -q
uv --no-config build
uv --no-config run --frozen python scripts/check_package_archives.py dist
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
```

- [ ] **Step 5: Request release review**

Create release review prompt and run Claude Code first. Use opencode fallback only if Claude Code is unavailable. Committed release review records must contain one coherent completed review body.

- [ ] **Step 6: Commit and push**

Stage all Stage 264 tracked and untracked files, verify staged file names, commit:

```bash
git add -A
git diff --cached --name-only
git commit -m "Stage 264: add ROW ONE daily readiness preview"
git push origin main
git status --short --branch --untracked-files=all
```

Expected final status: clean `main...origin/main`.

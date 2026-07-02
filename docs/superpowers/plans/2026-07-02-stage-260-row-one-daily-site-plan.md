# Stage 260 ROW ONE Daily Site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use task-list checkbox syntax for tracking.

**Goal:** Build the first local ROW ONE daily fashion-news website generator and server on top of the existing Fashion Radar report pipeline.

**Architecture:** Add a focused `fashion_radar.row_one` package that maps existing report data into presentation-only edition models, renders static HTML/CSS/JSON output, and serves it through Python's stdlib HTTP server. Reuse the existing Fashion Radar collection, matching, scoring, report, scheduling, and retention primitives rather than adding a web framework or new source acquisition layer.

**Tech Stack:** Python 3.11+, Typer, Pydantic, SQLAlchemy, existing Fashion Radar report models, stdlib `http.server`, static HTML/CSS/JS, pytest, Ruff.

---

## Stage Boundary

This stage closes a product gap in the collect -> match -> report pipeline: it turns the existing technical daily report into an end-user ROW ONE editorial website with detail pages and daily cleanup. It does not add new data acquisition, platform scraping, translation services, paid APIs, deployment automation, or compliance-review features.

## Review Fixes Applied Before Coding

The opencode Stage 260 plan review required these pre-coding fixes, all incorporated below:

- `--latest-only` cleanup deletes only known ROW ONE generated children, not the whole user-supplied directory.
- `row-one schedule` prints a two-step refresh command: existing `fashion-radar run` first, then `fashion-radar row-one build --latest-only`.
- Bilingual fields have explicit non-empty deterministic fallbacks without pretending to translate.
- Detail paths use a bounded ASCII slug plus stable hash to avoid duplicate-headline
  collisions and non-Latin filename issues.
- Task 5 includes opencode fallback code review and a narrowed Claude Code code-review prompt.
- CLI build tests pin temporary config/data/report directories and assert empty-state output.
- Section story caps prevent one source category from dominating the edition.

## Files

- Create: `src/fashion_radar/row_one/__init__.py`
- Create: `src/fashion_radar/row_one/models.py`
- Create: `src/fashion_radar/row_one/edition.py`
- Create: `src/fashion_radar/row_one/render.py`
- Create: `src/fashion_radar/row_one/server.py`
- Create: `src/fashion_radar/row_one/templates.py`
- Modify: `src/fashion_radar/workflows.py`
- Modify: `src/fashion_radar/cli.py`
- Modify: `src/fashion_radar/scheduling.py`
- Modify: `docs/architecture.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/scheduling.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `README.md`
- Create: `docs/row-one.md`
- Create: `tests/test_row_one_edition.py`
- Create: `tests/test_row_one_render.py`
- Create: `tests/test_row_one_cli.py`
- Create: `tests/test_row_one_docs.py`

## Task 1: ROW ONE Presentation Models And Edition Builder

**Files:**
- Create: `src/fashion_radar/row_one/__init__.py`
- Create: `src/fashion_radar/row_one/models.py`
- Create: `src/fashion_radar/row_one/edition.py`
- Test: `tests/test_row_one_edition.py`

- [x] **Step 1: Write failing model and builder tests**

Create tests that build a tiny `DailyReport` fixture with one brand entity, one celebrity entity, one product candidate, and three recent items. Assert:

```python
def test_build_row_one_edition_groups_editorial_sections():
    edition = build_row_one_edition(report=sample_report(), recent_items=sample_recent_items())
    assert edition.brand == "ROW ONE"
    assert [section.key for section in edition.sections] == [
        "top_stories",
        "brand_moves",
        "celebrity_style",
        "hot_products",
        "rising_radar",
    ]
    assert edition.sections[0].title.zh == "今日重点"
    assert edition.sections[0].title.en == "Top Stories"
    assert edition.stories[0].headline
    assert edition.stories[0].detail_path.startswith("details/")
```

Add focused tests for slug stability, duplicate-headline collision handling, bilingual summary fallback, source attribution, per-section caps, and empty report output.

- [x] **Step 2: Run tests and verify they fail**

Run: `uv --no-config run --frozen pytest tests/test_row_one_edition.py -q`

Expected: FAIL because `fashion_radar.row_one` does not exist.

- [x] **Step 3: Implement models**

Use Pydantic models because the project already depends on Pydantic and uses typed report models:

```python
class LocalizedText(BaseModel):
    zh: str
    en: str

class RowOneLink(BaseModel):
    title: str
    url: str | None = None
    source_name: str

class RowOneStory(BaseModel):
    id: str
    section_key: str
    headline: str
    summary: LocalizedText
    why_it_matters: LocalizedText
    source_name: str
    source_url: str | None = None
    published_at: str | None = None
    detail_path: str
    tags: list[str] = Field(default_factory=list)
    evidence: list[RowOneLink] = Field(default_factory=list)
```

Keep the models presentation-only. Do not alter `fashion_radar.models.report`.

- [x] **Step 4: Implement edition building**

Implement `build_row_one_edition(report, recent_items, as_of=None, max_stories=30)` with deterministic helpers:

- entities with `entity_type == "brand"` go to `brand_moves`;
- entities with `entity_type == "celebrity"` go to `celebrity_style`;
- candidates with product/bag/shoe-like labels go to `hot_products`;
- remaining high-scoring candidates go to `rising_radar`;
- the highest-scoring entities/candidates and newest recent items feed `top_stories`;
- section story caps default to `top_stories=6`, `brand_moves=8`, `celebrity_style=8`, `hot_products=8`, and `rising_radar=8`;
- story ids and detail paths use `<readable-slug>-<stable-short-hash>` so duplicate headlines never overwrite detail pages;
- Chinese and English summaries are always non-empty; when no real translation exists, use source text plus deterministic labels such as `Original source summary` and `来源摘要`;
- empty input returns all sections with empty story lists and an empty-state summary.

- [x] **Step 5: Verify Task 1**

Run: `uv --no-config run --frozen pytest tests/test_row_one_edition.py -q`

Expected: PASS.

## Task 2: Static Site Renderer And Detail Pages

**Files:**
- Create: `src/fashion_radar/row_one/render.py`
- Create: `src/fashion_radar/row_one/templates.py`
- Test: `tests/test_row_one_render.py`

- [x] **Step 1: Write failing renderer tests**

Assert that rendering writes:

- `index.html`
- `details/<story-id>.html`
- `assets/row-one.css`
- `assets/row-one.js`
- `data/edition.json`

Assert HTML contains escaped story text, `lang="en"`, `ROW ONE`, bilingual toggle controls, section anchors, and no unsafe `javascript:` links.

- [x] **Step 2: Run tests and verify they fail**

Run: `uv --no-config run --frozen pytest tests/test_row_one_render.py -q`

Expected: FAIL because the renderer does not exist.

- [x] **Step 3: Implement safe static rendering**

Implement:

```python
def render_row_one_site(edition: RowOneEdition, output_dir: Path, *, latest_only: bool = False) -> RowOneRenderResult:
    if latest_only:
        clean_row_one_site_children(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")
    write_assets(output_dir)
    write_index(edition, output_dir / "index.html")
    write_detail_pages(edition, output_dir / "details")
    write_json(edition, output_dir / "data" / "edition.json")
    return RowOneRenderResult(output_dir=output_dir, index_path=output_dir / "index.html", story_count=len(edition.stories))
```

Use `html.escape` for all dynamic HTML values and the existing safe URL pattern from `html_report.py`. Implement `clean_row_one_site_children(output_dir)` to remove only `index.html`, `.row-one-site`, `details/`, `assets/`, and `data/`; add a test proving an unrelated `keep.txt` file survives `latest_only=True`.

- [x] **Step 4: Implement editorial CSS and language switch**

Write static CSS and minimal no-build JavaScript:

- `data-lang="zh"` and `data-lang="en"` spans;
- a segmented language control;
- responsive two-column desktop layout;
- single-column mobile layout;
- strong ROW ONE masthead;
- detail pages with story summary, why it matters, and evidence links.

- [x] **Step 5: Verify Task 2**

Run: `uv --no-config run --frozen pytest tests/test_row_one_render.py -q`

Expected: PASS.

## Task 3: Workflow And CLI Commands

**Files:**
- Modify: `src/fashion_radar/workflows.py`
- Modify: `src/fashion_radar/cli.py`
- Create: `src/fashion_radar/row_one/server.py`
- Test: `tests/test_row_one_cli.py`

- [x] **Step 1: Write failing workflow and CLI tests**

Add tests for:

- `fashion-radar row-one build --as-of 2026-07-02T04:00:00Z --output-dir <tmp> --latest-only`
- `fashion-radar row-one serve --site-dir <tmp> --host 127.0.0.1 --port 8787 --dry-run`
- `fashion-radar row-one schedule --time 04:00`

Expected assertions:

```python
assert result.exit_code == 0
assert (output_dir / "index.html").exists()
assert "http://127.0.0.1:8787" in result.output
assert "04:00" in result.output
```

The build test must use temporary config, data, and report directories with a valid minimal `scoring.yaml`; it should assert the empty-state ROW ONE site renders cleanly when no items are stored.

- [x] **Step 2: Run tests and verify they fail**

Run: `uv --no-config run --frozen pytest tests/test_row_one_cli.py -q`

Expected: FAIL because the CLI commands are missing.

- [x] **Step 3: Add workflow wrapper**

Add `write_row_one_site_files(...)` in `workflows.py`. It should:

1. initialize/read the existing SQLite database;
2. build the existing `DailyReport`;
3. query recent items using the same bounded approach as `write_daily_report_files`;
4. build a `RowOneEdition`;
5. render the ROW ONE site.

- [x] **Step 4: Add Typer sub-app**

Add a `row_one_app = typer.Typer(help="ROW ONE local daily site commands.")` with:

- `build`
- `serve`
- `schedule`

Register it as `app.add_typer(row_one_app, name="row-one")`.

- [x] **Step 5: Implement server dry-run and runtime path**

`serve --dry-run` prints the URL without blocking. Without dry-run, validate `index.html`
exists and serve with `ThreadingHTTPServer`. Default `--host` to `127.0.0.1`; document
`--host 0.0.0.0` as the explicit LAN-access option. Add a threaded smoke test that starts
the server on an ephemeral port and verifies `GET /` returns HTTP 200.

- [x] **Step 6: Verify Task 3**

Run: `uv --no-config run --frozen pytest tests/test_row_one_cli.py -q`

Expected: PASS.

## Task 4: Scheduling, Cleanup, And Documentation

**Files:**
- Modify: `src/fashion_radar/scheduling.py`
- Create: `docs/row-one.md`
- Modify: `docs/architecture.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/scheduling.md`
- Modify: `README.md`
- Test: `tests/test_row_one_docs.py`

- [x] **Step 1: Write failing docs and scheduling tests**

Assert docs mention:

- ROW ONE
- `row-one build`
- `row-one serve`
- `row-one schedule`
- 04:00 local scheduling
- latest-only cleanup
- IP:port local-network serving

Assert schedule output calls `fashion-radar row-one build`, not the old report-only command.
Assert schedule output also calls the existing `fashion-radar run` before `row-one build --latest-only`.

- [x] **Step 2: Run tests and verify they fail**

Run: `uv --no-config run --frozen pytest tests/test_row_one_docs.py -q`

Expected: FAIL until docs and schedule helpers are updated.

- [x] **Step 3: Add ROW ONE schedule helper**

Add `render_row_one_cron_example(...)` and `render_row_one_systemd_service(...)` if this keeps
the existing Fashion Radar scheduling helpers stable. These helpers must print both commands
in order:

```bash
uv run fashion-radar run --as-of "<timestamp>"
uv run fashion-radar row-one build --as-of "<same timestamp>" --latest-only
```

Do not break existing scheduling tests.

- [x] **Step 4: Write user docs**

Document:

```bash
AS_OF="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar run --as-of "$AS_OF"
uv run fashion-radar row-one build --as-of "$AS_OF" --latest-only
uv run fashion-radar row-one serve --site-dir reports/row-one/site --host 127.0.0.1 --port 8787
uv run fashion-radar row-one serve --site-dir reports/row-one/site --host 0.0.0.0 --port 8787
uv run fashion-radar row-one schedule --time 04:00
```

State that Open Design imagery is optional and not required for tests.

- [x] **Step 5: Verify Task 4**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_scheduling.py tests/test_scheduling_docs.py -q
```

Expected: PASS.

## Task 5: Full Verification, Review, And Handoff

**Files:**
- Create: `docs/reviews/opencode-stage-260-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-260-code-review.md`

- [x] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_edition.py tests/test_row_one_render.py tests/test_row_one_cli.py tests/test_row_one_docs.py -q
```

Expected: PASS.

- [x] **Step 2: Run full verification**

Run:

```bash
uv --no-config run --frozen pytest -q
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
```

Expected: PASS.

- [x] **Step 3: Request primary code review**

Use:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "<diff-scoped Stage 260 code review prompt>"
```

The review prompt must include the base SHA, head SHA, spec path, plan path, and verification commands. Keep it diff-scoped and concise to reduce reviewer load.

- [x] **Step 4: Use opencode fallback if primary review is unavailable**

If the primary review route is unavailable, do not commit partial unavailable-review
records as completed review artifacts. Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-260-code-review-prompt.md)"
```

Critical and Important findings from either reviewer must be fixed before continuing.

- [x] **Step 5: Fix Critical and Important findings**

Apply fixes before moving to the next stage. Minor polish can be deferred only if it does not affect correctness, tests, user requirements, or review protocol.

- [x] **Step 6: Handoff Summary**

Write a concise handoff summary with:

- repo status;
- verified commands;
- uncommitted files;
- next step.

## Review Notes For Claude Code

Please review this stage for:

- whether the static-site approach is appropriate for the user's local IP:port requirement;
- whether the latest-only cleanup boundary is safe and narrow;
- whether the plan preserves existing source/platform boundaries;
- whether bilingual UI without default translation is acceptable for the MVP;
- whether the task sequence is testable and small enough for staged implementation.

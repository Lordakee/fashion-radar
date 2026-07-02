# Stage 266 ROW ONE App Discovery And Editorial Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a small ROW ONE app discovery manifest, improve the static edition with a lead story and SEO/social metadata, and document the source-checkout path for opening the local ROW ONE site.

**Architecture:** Keep the new manifest as a sidecar discovery contract generated from the existing `RowOneEdition`, while preserving `row-one-app/v1` as the full edition payload. Keep site polish in `templates.py` as presentation-only HTML/CSS metadata and lead-story rendering. Update docs and package guards so the new schema ships but generated site data does not.

**Tech Stack:** Python 3.11+, Pydantic models already in place, JSON Schema Draft 2020-12, Typer CLI output already in place, pytest, jsonschema, ruff, uv.

---

## Files

- Modify: `src/fashion_radar/row_one/render.py`
  - Add manifest contract constant and `build_row_one_manifest_payload(...)`.
  - Write `data/manifest.json` next to `data/edition.json`.
- Modify: `src/fashion_radar/row_one/templates.py`
  - Add index/detail metadata helpers.
  - Add a lead story block to the homepage.
  - Add CSS for lead story presentation.
- Create: `schemas/row-one-manifest.schema.json`
  - Strict schema for `data/manifest.json`.
- Modify: `tests/test_row_one_render.py`
  - Assert manifest file output, lead story HTML, and metadata.
- Modify: `tests/test_row_one_app_contract.py`
  - Add manifest schema validation and drift tests.
- Modify: `scripts/check_package_archives.py`
  - Add `schemas/row-one-manifest.schema.json` to sdist required paths.
- Modify: `tests/test_package_archives.py`
  - Add the new schema to the sdist fixture.
- Modify: `docs/row-one.md`
  - Document the app discovery manifest, generated file, lead story, and SEO/social metadata.
- Modify: `docs/first-run.md`
  - Add the source-checkout ROW ONE sample-site path.
- Modify: `README.md`
  - Add ROW ONE to the quickstart/documentation discovery path.
- Modify: `docs/github-upload-checklist.md`
  - Add upload-facing docs check for ROW ONE source-checkout path and generated artifact boundary.
- Modify: `tests/test_row_one_docs.py`
  - Pin the new public docs language.

---

### Task 1: Manifest Payload And Schema

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Create: `schemas/row-one-manifest.schema.json`
- Test: `tests/test_row_one_app_contract.py`

- [ ] **Step 1: Write failing manifest schema tests**

Add constants and helpers in `tests/test_row_one_app_contract.py`:

```python
MANIFEST_SCHEMA = ROOT / "schemas" / "row-one-manifest.schema.json"


def _manifest_schema_validator() -> Draft202012Validator:
    schema = json.loads(MANIFEST_SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _manifest_payload(tmp_path: Path, edition: RowOneEdition | None = None) -> dict[str, object]:
    render_row_one_site(edition or _edition(), tmp_path)
    return json.loads((tmp_path / "data" / "manifest.json").read_text(encoding="utf-8"))
```

Add tests:

```python
def test_row_one_manifest_schema_validates_generated_payload(tmp_path: Path) -> None:
    manifest = _manifest_payload(tmp_path)

    _manifest_schema_validator().validate(manifest)


def test_row_one_manifest_points_to_app_contract_and_site_paths(tmp_path: Path) -> None:
    manifest = _manifest_payload(tmp_path)

    assert manifest["contract_version"] == "row-one-manifest/v1"
    assert manifest["brand"] == "ROW ONE"
    assert manifest["manifest_schema_path"] == "schemas/row-one-manifest.schema.json"
    assert manifest["app_contract"] == {
        "version": "row-one-app/v1",
        "path": "data/edition.json",
        "schema_path": "schemas/row-one-app.schema.json",
    }
    assert manifest["site"] == {
        "index_path": "index.html",
        "data_path": "data/edition.json",
        "manifest_path": "data/manifest.json",
        "assets_path": "assets/",
        "details_path": "details/",
    }


def test_row_one_manifest_counts_match_app_payload(tmp_path: Path) -> None:
    app_payload = _payload(tmp_path)
    manifest = json.loads((tmp_path / "data" / "manifest.json").read_text(encoding="utf-8"))

    assert manifest["generated_at"] == app_payload["generated_at"]
    assert manifest["edition_date"] == app_payload["edition_date"]
    assert manifest["counts"]["story_count"] == app_payload["story_count"]
    assert manifest["counts"]["section_count"] == len(app_payload["sections"])
    assert manifest["counts"]["evidence_count"] == app_payload["evidence_count"]
    assert manifest["readiness"]["status"] == "ready"


def test_empty_row_one_manifest_payload_validates(tmp_path: Path) -> None:
    edition = RowOneEdition(
        generated_at=AS_OF,
        edition_date=AS_OF,
        summary=LocalizedText(zh="暂无信号。", en="No signals yet."),
        sections=[
            RowOneSection(
                key="top_stories",
                title=LocalizedText(zh="今日重点", en="Top Stories"),
                dek=LocalizedText(zh="今日最值得先看的时尚信号。", en="Read first."),
            )
        ],
        stories=[],
    )

    manifest = _manifest_payload(tmp_path, edition)

    assert manifest["counts"]["story_count"] == 0
    assert manifest["readiness"]["status"] == "empty"
    _manifest_schema_validator().validate(manifest)
```

Add schema drift test:

```python
@pytest.mark.parametrize(
    ("mutation", "match"),
    [
        (
            lambda payload: payload.__setitem__("contract_version", "row-one-manifest/v2"),
            "was expected",
        ),
        (lambda payload: payload.__setitem__("extra", True), "Additional properties"),
        (lambda payload: payload.__setitem__("generated_at", "not-a-date"), "does not match"),
        (
            lambda payload: payload["app_contract"].__setitem__("path", "/abs/edition.json"),
            "was expected",
        ),
        (
            lambda payload: payload["readiness"].__setitem__("status", "partial"),
            "is not one of",
        ),
        (
            lambda payload: payload["capabilities"].__setitem__("absolute_urls", True),
            "Additional properties",
        ),
    ],
)
def test_row_one_manifest_schema_rejects_contract_drift(
    tmp_path: Path,
    mutation,
    match: str,
) -> None:
    manifest = copy.deepcopy(_manifest_payload(tmp_path))
    mutation(manifest)

    with pytest.raises(ValidationError, match=match):
        _manifest_schema_validator().validate(manifest)
```

- [ ] **Step 2: Run tests and verify they fail**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_app_contract.py::test_row_one_manifest_schema_validates_generated_payload tests/test_row_one_app_contract.py::test_row_one_manifest_points_to_app_contract_and_site_paths tests/test_row_one_app_contract.py::test_row_one_manifest_counts_match_app_payload tests/test_row_one_app_contract.py::test_empty_row_one_manifest_payload_validates -q
```

Expected: FAIL because `schemas/row-one-manifest.schema.json` and `data/manifest.json` do not exist.

- [ ] **Step 3: Add manifest payload builder**

In `src/fashion_radar/row_one/render.py`, add:

```python
ROW_ONE_MANIFEST_CONTRACT_VERSION = "row-one-manifest/v1"
ROW_ONE_MANIFEST_SCHEMA_PATH = "schemas/row-one-manifest.schema.json"
```

Add:

```python
def build_row_one_manifest_payload(
    edition: RowOneEdition,
    app_payload: dict[str, object] | None = None,
) -> dict[str, object]:
    app_payload = app_payload or build_row_one_app_payload(edition)
    story_count = int(app_payload["story_count"])
    return {
        "contract_version": ROW_ONE_MANIFEST_CONTRACT_VERSION,
        "brand": edition.brand,
        "generated_at": app_payload["generated_at"],
        "edition_date": app_payload["edition_date"],
        "manifest_schema_path": ROW_ONE_MANIFEST_SCHEMA_PATH,
        "app_contract": {
            "version": ROW_ONE_APP_CONTRACT_VERSION,
            "path": "data/edition.json",
            "schema_path": "schemas/row-one-app.schema.json",
        },
        "site": {
            "index_path": "index.html",
            "data_path": "data/edition.json",
            "manifest_path": "data/manifest.json",
            "assets_path": "assets/",
            "details_path": "details/",
        },
        "counts": {
            "story_count": story_count,
            "section_count": len(edition.sections),
            "evidence_count": app_payload["evidence_count"],
        },
        "readiness": {
            "status": "ready" if story_count > 0 else "empty",
        },
        "capabilities": {
            "bilingual": True,
            "static_site": True,
            "detail_pages": True,
            "sanitized_external_urls": True,
            "latest_only_cleanup": True,
            "seo_metadata": True,
        },
    }
```

In `render_row_one_site()`, after writing `edition.json`, write:

```python
manifest_payload = build_row_one_manifest_payload(edition, app_payload)
(data_dir / "manifest.json").write_text(
    json.dumps(manifest_payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
```

- [ ] **Step 4: Add strict manifest schema**

Create `schemas/row-one-manifest.schema.json` with:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/Lordakee/fashion-radar/blob/main/schemas/row-one-manifest.schema.json",
  "title": "Fashion Radar ROW ONE Manifest Payload",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "contract_version",
    "brand",
    "generated_at",
    "edition_date",
    "manifest_schema_path",
    "app_contract",
    "site",
    "counts",
    "readiness",
    "capabilities"
  ],
  "properties": {
    "contract_version": { "const": "row-one-manifest/v1" },
    "brand": { "type": "string", "minLength": 1 },
    "generated_at": { "$ref": "#/$defs/utcTimestamp" },
    "edition_date": { "$ref": "#/$defs/utcTimestamp" },
    "manifest_schema_path": { "const": "schemas/row-one-manifest.schema.json" },
    "app_contract": {
      "type": "object",
      "additionalProperties": false,
      "required": ["version", "path", "schema_path"],
      "properties": {
        "version": { "const": "row-one-app/v1" },
        "path": { "const": "data/edition.json" },
        "schema_path": { "const": "schemas/row-one-app.schema.json" }
      }
    },
    "site": {
      "type": "object",
      "additionalProperties": false,
      "required": ["index_path", "data_path", "manifest_path", "assets_path", "details_path"],
      "properties": {
        "index_path": { "const": "index.html" },
        "data_path": { "const": "data/edition.json" },
        "manifest_path": { "const": "data/manifest.json" },
        "assets_path": { "const": "assets/" },
        "details_path": { "const": "details/" }
      }
    },
    "counts": {
      "type": "object",
      "additionalProperties": false,
      "required": ["story_count", "section_count", "evidence_count"],
      "properties": {
        "story_count": { "type": "integer", "minimum": 0 },
        "section_count": { "type": "integer", "minimum": 0 },
        "evidence_count": { "type": "integer", "minimum": 0 }
      }
    },
    "readiness": {
      "type": "object",
      "additionalProperties": false,
      "required": ["status"],
      "properties": {
        "status": { "enum": ["ready", "empty"] }
      }
    },
    "capabilities": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "bilingual",
        "static_site",
        "detail_pages",
        "sanitized_external_urls",
        "latest_only_cleanup",
        "seo_metadata"
      ],
      "properties": {
        "bilingual": { "const": true },
        "static_site": { "const": true },
        "detail_pages": { "const": true },
        "sanitized_external_urls": { "const": true },
        "latest_only_cleanup": { "const": true },
        "seo_metadata": { "const": true }
      }
    }
  },
  "$defs": {
    "utcTimestamp": {
      "type": "string",
      "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$"
    }
  }
}
```

- [ ] **Step 5: Run manifest tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_app_contract.py -q
```

Expected: PASS.

---

### Task 2: Manifest Render And Package Guardrails

**Files:**
- Modify: `tests/test_row_one_render.py`
- Modify: `scripts/check_package_archives.py`
- Modify: `tests/test_package_archives.py`

- [ ] **Step 1: Add render output assertions**

In `tests/test_row_one_render.py`, update `test_render_row_one_site_writes_static_site_files`:

```python
assert (tmp_path / "data" / "manifest.json").exists()
```

In `test_render_row_one_site_writes_json_payload`, read manifest and assert:

```python
manifest = json.loads((tmp_path / "data" / "manifest.json").read_text(encoding="utf-8"))
assert manifest["contract_version"] == "row-one-manifest/v1"
assert manifest["app_contract"]["path"] == "data/edition.json"
assert manifest["counts"]["story_count"] == payload["story_count"]
assert manifest["counts"]["evidence_count"] == payload["evidence_count"]
```

- [ ] **Step 2: Add package archive schema guard**

Add `schemas/row-one-manifest.schema.json` to `SDIST_REQUIRED_PATHS` in
`scripts/check_package_archives.py`.

Add `schemas/row-one-manifest.schema.json` to `SDIST_FILES` in
`tests/test_package_archives.py`.

- [ ] **Step 3: Run focused tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_package_archives.py -q
```

Expected: PASS.

---

### Task 3: Lead Story And Metadata Rendering

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Test: `tests/test_row_one_render.py`

- [ ] **Step 1: Write failing render tests**

Add to `tests/test_row_one_render.py`:

```python
def test_render_row_one_site_includes_lead_story_block(tmp_path) -> None:
    render_row_one_site(_edition(), tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert 'class="lead-story"' in index_html
    assert "Lead Story" in index_html
    assert "今日头条" in index_html
    assert "The Row &lt;signals&gt; &quot;quiet&quot; demand" in index_html
    assert "The Row is today&#x27;s priority signal." in index_html


def test_render_row_one_site_includes_index_and_detail_metadata(tmp_path) -> None:
    render_row_one_site(_edition(), tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )

    assert '<meta name="description" content="ROW ONE organized 1 local fashion signal for today.">' in index_html
    assert '<meta property="og:title" content="ROW ONE' in index_html
    assert '<meta property="og:type" content="website">' in index_html
    assert '<meta name="twitter:card" content="summary">' in index_html

    assert (
        '<meta name="description" content="Original source summary: The Row signal '
        'with &lt;angle&gt; detail.">'
    ) in detail_html
    assert '<meta property="og:title" content="The Row &lt;signals&gt;' in detail_html
    assert '<meta property="og:type" content="article">' in detail_html
    assert (
        '<meta name="twitter:title" content="The Row &lt;signals&gt; '
        '&quot;quiet&quot; demand">'
    ) in detail_html
```

- [ ] **Step 2: Run tests and verify they fail**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_includes_lead_story_block tests/test_row_one_render.py::test_render_row_one_site_includes_index_and_detail_metadata -q
```

Expected: FAIL because lead story and metadata are not rendered yet.

- [ ] **Step 3: Add metadata helpers**

In `src/fashion_radar/row_one/templates.py`, add helpers:

```python
def _meta_description(text: str, *, limit: int = 180) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "…"


def _render_meta_tags(*, title: str, description: str, page_type: str) -> str:
    safe_title = _esc(title)
    safe_description = _esc(_meta_description(description))
    safe_type = _esc(page_type)
    return f"""<meta name="description" content="{safe_description}">
<meta property="og:title" content="{safe_title}">
<meta property="og:description" content="{safe_description}">
<meta property="og:type" content="{safe_type}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{safe_title}">
<meta name="twitter:description" content="{safe_description}">"""
```

In `render_index_html()`, insert metadata in `<head>` after viewport:

```python
{_render_meta_tags(
    title=f"{edition.brand} — {edition.edition_date.date().isoformat()}",
    description=edition.summary.en,
    page_type="website",
)}
```

In `render_detail_html()`, insert metadata after viewport:

```python
{_render_meta_tags(
    title=story.headline,
    description=story.summary.en,
    page_type="article",
)}
```

- [ ] **Step 4: Add lead story renderer**

In `render_index_html()`, compute:

```python
lead_story = _lead_story(edition)
lead_story_block = _render_lead_story(lead_story, _section_title(edition, lead_story.section_key)) if lead_story else ""
```

Place `{lead_story_block}` after `{contents_nav}` and before `{story_cards}`.

Add helpers:

```python
def _lead_story(edition: RowOneEdition) -> RowOneStory | None:
    top_stories = edition.section_stories("top_stories")
    if top_stories:
        return top_stories[0]
    return edition.stories[0] if edition.stories else None


def _render_lead_story(story: RowOneStory, section_title: LocalizedText) -> str:
    detail_href = _internal_detail_href(story.detail_path)
    return f"""<section class="lead-story" aria-label="Lead story">
  <p class="story-section">
    <span data-lang="en">Lead Story</span>
    <span data-lang="zh">今日头条</span>
  </p>
  <div class="lead-story-grid">
    <div>
      <h2><a href="{detail_href}">{_esc(story.headline)}</a></h2>
      {_render_story_orientation(story, section_title)}
    </div>
    <div>
      <p class="story-takeaway">
        <span data-lang="en">{_esc(story.editorial_takeaway.en)}</span>
        <span data-lang="zh">{_esc(story.editorial_takeaway.zh)}</span>
      </p>
      <p>
        <span data-lang="en">{_esc(story.summary.en)}</span>
        <span data-lang="zh">{_esc(story.summary.zh)}</span>
      </p>
      <a class="lead-story-link" href="{detail_href}">
        <span data-lang="en">Read the brief</span>
        <span data-lang="zh">查看详情</span>
      </a>
    </div>
  </div>
</section>"""
```

Add CSS inside `row_one_css()`:

```css
.lead-story {
  border-top: 1px solid var(--ink);
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 32px 0;
}
.lead-story-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(260px, 0.75fr);
  gap: 32px;
  align-items: end;
}
.lead-story h2 {
  margin: 10px 0 0;
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(3rem, 8vw, 7.5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.9;
}
.lead-story h2 a, .lead-story-link {
  color: var(--ink);
  text-decoration: none;
}
.lead-story-link {
  border-bottom: 1px solid var(--accent);
  color: var(--accent);
  display: inline-block;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  margin-top: 12px;
  padding-bottom: 4px;
  text-transform: uppercase;
}
```

In the mobile media query, add:

```css
.lead-story-grid { grid-template-columns: 1fr; gap: 18px; }
```

- [ ] **Step 5: Run render tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_render.py -q
```

Expected: PASS.

---

### Task 4: Docs And First-Run Path

**Files:**
- Modify: `docs/row-one.md`
- Modify: `docs/first-run.md`
- Modify: `README.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Add failing docs assertions**

In `tests/test_row_one_docs.py`, add assertions to the existing ROW ONE docs tests or add a new test:

```python
def test_row_one_docs_describe_manifest_and_editorial_polish() -> None:
    row_one_doc = _read(ROW_ONE_DOC)
    readme = _read(ROOT / "README.md")
    first_run = _read(ROOT / "docs" / "first-run.md")
    checklist = _read(ROOT / "docs" / "github-upload-checklist.md")

    for phrase in (
        "`data/manifest.json`",
        "`row-one-manifest/v1`",
        "`schemas/row-one-manifest.schema.json`",
        "app discovery manifest",
        "lead story",
        "SEO/social metadata",
    ):
        assert phrase.lower() in row_one_doc.lower()

    assert "Inspect The Sample In ROW ONE".lower() in first_run.lower()
    assert "row-one preview --config-dir \"$PWD/configs\"".lower() in first_run.lower()
    assert "row-one serve --site-dir reports/row-one/site --host 127.0.0.1 --port 8787".lower() in first_run.lower()
    assert "docs/row-one.md" in readme
    assert "ROW ONE local static site" in readme
    assert "data/manifest.json" in checklist
    assert "do not upload generated ROW ONE site artifacts".lower() in checklist.lower()
```

- [ ] **Step 2: Run docs test and verify it fails**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_manifest_and_editorial_polish -q
```

Expected: FAIL because docs do not mention the new manifest/polish path.

- [ ] **Step 3: Update `docs/row-one.md`**

Add `data/manifest.json` to Generated Files.

Add a new `App Discovery Manifest` section after `App JSON Contract`:

```markdown
## App Discovery Manifest

`data/manifest.json` is the `row-one-manifest/v1` app discovery manifest. It is
validated by `schemas/row-one-manifest.schema.json` and points clients to
`data/edition.json`, the `row-one-app/v1` edition payload, and stable generated
site paths such as `index.html`, `assets/`, and `details/`.

The manifest contains only discovery metadata, counts, readiness status, and
capabilities. It does not duplicate story arrays, section arrays, absolute
host/port URLs, LAN preview URLs, local machine paths, source collection output,
or deployment state.
```

Add presentation note:

```markdown
The homepage also renders a lead story presentation block and the index/detail
HTML include deterministic SEO/social metadata derived from existing edition and
story summaries.
```

- [ ] **Step 4: Update `docs/first-run.md`**

After the dashboard/sample report inspection section, add:

```markdown
## Inspect The Sample In ROW ONE

Use the same repo-local sample data to build the ROW ONE local static site:

```bash
AS_OF="2026-06-13T12:00:00Z"
uv run fashion-radar row-one build --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --output-dir reports/row-one/site --as-of "$AS_OF" --latest-only
uv run fashion-radar row-one preview --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --output-dir reports/row-one/site --as-of "$AS_OF" --latest-only --dry-run-serve-url
uv run fashion-radar row-one serve --site-dir reports/row-one/site --host 127.0.0.1 --port 8787
```

Open `http://127.0.0.1:8787` locally. The generated ROW ONE site under
`reports/row-one/site` is a local artifact and should not be committed.
```

- [ ] **Step 5: Update README and checklist**

In `README.md`, add a concrete documentation-list bullet so the literal path is
discoverable:

```markdown
- [ROW ONE local static site](docs/row-one.md)
```

Also add a sentence near the ROW ONE section:

```markdown
For a source-checkout first run, follow [docs/first-run.md](docs/first-run.md)
and then inspect the same sample in the ROW ONE local static site.
```

In `docs/github-upload-checklist.md`, add a docs check:

```markdown
- [ ] ROW ONE source-checkout docs describe `data/manifest.json`, the
      `row-one-manifest/v1` discovery contract, and how to build/preview/serve
      the local site. Do not upload generated ROW ONE site artifacts.
```

- [ ] **Step 6: Run docs tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_docs.py -q
```

Expected: PASS.

---

### Task 5: Focused Verification And Review Packet

**Files:**
- Modify only files touched by Tasks 1-4.
- Create: `docs/reviews/opencode-stage-266-code-review-prompt.md` after implementation.

- [ ] **Step 1: Run focused checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_row_one_app_contract.py tests/test_row_one_docs.py tests/test_package_archives.py -q
uv --no-config run --frozen ruff check src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_app_contract.py tests/test_row_one_docs.py scripts/check_package_archives.py tests/test_package_archives.py
uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_app_contract.py tests/test_row_one_docs.py scripts/check_package_archives.py tests/test_package_archives.py
```

Expected: all pass.

- [ ] **Step 2: Run full release gate**

Run:

```bash
rm -rf dist
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

Expected: all pass.

- [ ] **Step 3: Write opencode code review prompt**

Create `docs/reviews/opencode-stage-266-code-review-prompt.md` with:

```markdown
Review the Stage 266 implementation before commit/push.

Repo: /home/ubuntu/fashion-radar
Design doc: docs/superpowers/specs/2026-07-02-stage-266-row-one-app-discovery-editorial-polish-design.md
Plan doc: docs/superpowers/plans/2026-07-02-stage-266-row-one-app-discovery-editorial-polish-plan.md

Goal:
Add a ROW ONE app discovery manifest, homepage lead story presentation,
deterministic SEO/social metadata, and source-checkout docs for opening the
local ROW ONE site.

Review criteria:
- Manifest remains a small discovery contract and does not duplicate edition stories/sections.
- `row-one-app/v1` remains backwards compatible.
- Manifest schema is strict and shipped in sdist.
- Lead story and metadata are presentation-only and do not change ranking/scoring/collection.
- Docs give a clear GitHub/source-checkout local ROW ONE path.
- No compliance-review product features, new collectors, LLM calls, image generation, deployment, or system service installation were added.
- Tests and release gate outputs support shipping.

Return Critical / Important / Minor findings and a verdict.
```

- [ ] **Step 4: Run local opencode code review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-266-code-review-prompt.md)" > docs/reviews/opencode-stage-266-code-review.md
```

Expected: no Critical/Important findings before commit.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short
git add src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py schemas/row-one-manifest.schema.json tests/test_row_one_render.py tests/test_row_one_app_contract.py scripts/check_package_archives.py tests/test_package_archives.py docs/row-one.md docs/first-run.md README.md docs/github-upload-checklist.md tests/test_row_one_docs.py docs/reviews/opencode-stage-266-code-review-prompt.md docs/reviews/opencode-stage-266-code-review.md
git diff --cached --check
git commit -m "Stage 266: add ROW ONE app discovery manifest"
git push origin main
```

Expected: commit and push succeed.
*** Add File: /home/ubuntu/fashion-radar/docs/reviews/opencode-stage-266-plan-review-prompt.md
Review the Stage 266 plan before implementation.

Repo: /home/ubuntu/fashion-radar
Design doc: docs/superpowers/specs/2026-07-02-stage-266-row-one-app-discovery-editorial-polish-design.md
Plan doc: docs/superpowers/plans/2026-07-02-stage-266-row-one-app-discovery-editorial-polish-plan.md

Goal:
Add a ROW ONE app discovery manifest, homepage lead story presentation,
deterministic SEO/social metadata, and source-checkout docs for opening the
local ROW ONE site.

Review criteria:
- Plan feasibility and correctness against the current codebase.
- Whether the manifest contract is small, stable, schema-validated, and does not
  duplicate edition stories/sections.
- Whether `row-one-app/v1` remains backwards compatible.
- Whether generated `data/manifest.json` and shipped
  `schemas/row-one-manifest.schema.json` boundaries are correct.
- Whether lead story and SEO/social metadata are presentation-only and do not
  alter collection, matching, scoring, ranking, scheduling, server, cleanup, or
  app payload semantics.
- Whether docs changes give a clearer GitHub/source-checkout ROW ONE path.
- Whether tests are executable as written and cover the new public behavior.
- Confirm no compliance-review product feature, new collector, LLM call, image
  generation, paid API, deployment, or system service installation is introduced.

Do not edit files. Return a concise review with Critical / Important / Minor
findings and a verdict.

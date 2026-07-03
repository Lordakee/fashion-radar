# Stage 269 ROW ONE Display Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a stable story display/media contract and professional visual slots to ROW ONE without requiring generated images yet.

**Architecture:** Extend the ROW ONE Pydantic story model with optional display metadata, generate deterministic display metadata during edition synthesis, and make render/app payload helpers produce a required sanitized `display` object for every story. Templates render safe images when available and fallback editorial visuals otherwise. Browser language state remains static-site friendly by using guarded `localStorage`.

**Tech Stack:** Python 3.11+, Pydantic v2, existing ROW ONE static renderer, JSON Schema draft 2020-12, pytest, ruff, uv.

---

## Files

- Modify: `src/fashion_radar/row_one/models.py`
  - Add `RowOneStoryImage` and `RowOneStoryDisplay`.
  - Add optional `display` to `RowOneStory`.
  - Export new models from `src/fashion_radar/row_one/__init__.py`.
- Create: `src/fashion_radar/row_one/display.py`
  - Keep section display mapping and image-source sanitation in one place.
- Modify: `src/fashion_radar/row_one/edition.py`
  - Assign deterministic display metadata with the shared display helper.
- Modify: `src/fashion_radar/row_one/render.py`
  - Emit a required sanitized `display` object for each story in `data/edition.json`.
  - Reuse the shared image-source sanitation helper for safe generated asset image paths and safe http(s) image URLs.
- Modify: `src/fashion_radar/row_one/templates.py`
  - Render lead, card, and detail visual slots.
  - Update CSS to a colder ROW ONE editorial palette.
  - Persist language preference with guarded `localStorage`.
- Modify: `schemas/row-one-app.schema.json`
  - Add `display`, `storyDisplay`, `storyImage`, and image source schema definitions.
- Modify: `tests/test_row_one_edition.py`
  - Add deterministic display assignment coverage.
- Modify: `tests/test_row_one_app_contract.py`
  - Add schema and unsafe image coverage.
- Modify: `tests/test_row_one_render.py`
  - Add HTML/CSS/JS visual slot and language persistence coverage.
- Modify: `tests/test_row_one_docs.py`
  - Add docs coverage for display/media readiness.
- Modify: `docs/row-one.md`
  - Document display/media readiness and the future OpenDesign image boundary.

---

## Parallel Ownership

Use workers only after opencode plan review passes.

- Worker A owns models, edition generation, and edition tests:
  - `src/fashion_radar/row_one/models.py`
  - `src/fashion_radar/row_one/display.py`
  - `src/fashion_radar/row_one/__init__.py`
  - `src/fashion_radar/row_one/edition.py`
  - `tests/test_row_one_edition.py`
- Worker B owns app contract/schema:
  - `src/fashion_radar/row_one/render.py`
  - `schemas/row-one-app.schema.json`
  - `tests/test_row_one_app_contract.py`
- Worker C owns templates and render tests:
  - `src/fashion_radar/row_one/templates.py`
  - `tests/test_row_one_render.py`
- Worker D owns docs:
  - `docs/row-one.md`
  - `tests/test_row_one_docs.py`

Execution order:

1. Run Worker A and Worker D in parallel. Worker D is independent because it only changes docs/tests.
2. Integrate Worker A first because B and C import the new shared display helpers.
3. After Worker A lands, run Worker B and Worker C in parallel.
4. Run the integration/review gate after all workers are closed.

Workers must not edit files outside their ownership without returning `NEEDS_CONTEXT`. They are not alone in the codebase and must not revert edits from other workers.

---

### Task 1: Story Display Models And Deterministic Edition Metadata

**Files:**
- Modify: `src/fashion_radar/row_one/models.py`
- Create: `src/fashion_radar/row_one/display.py`
- Modify: `src/fashion_radar/row_one/__init__.py`
- Modify: `src/fashion_radar/row_one/edition.py`
- Modify: `tests/test_row_one_edition.py`

- [ ] **Step 1: Add failing edition test**

Add `test_build_row_one_edition_assigns_deterministic_display_metadata` to `tests/test_row_one_edition.py`.

The test should build an edition with one story in each ROW ONE section and assert:

```python
assert edition.section_stories("top_stories")[0].display.variant == "editorial"
assert edition.section_stories("top_stories")[0].display.accent == "ink"
assert edition.section_stories("brand_moves")[0].display.variant == "editorial"
assert edition.section_stories("brand_moves")[0].display.accent == "graphite"
assert edition.section_stories("celebrity_style")[0].display.variant == "portrait"
assert edition.section_stories("celebrity_style")[0].display.accent == "rose"
assert edition.section_stories("hot_products")[0].display.variant == "product"
assert edition.section_stories("hot_products")[0].display.accent == "cobalt"
assert edition.section_stories("rising_radar")[0].display.variant == "signal"
assert edition.section_stories("rising_radar")[0].display.accent == "steel"
assert all(story.display.image is None for story in edition.stories)
```

Build the fixture using the existing `_entity`, `_candidate`, and `_recent_items` helpers already defined in `tests/test_row_one_edition.py` so the test deterministically produces top stories, brand moves, celebrity style, hot products, and rising radar stories.

- [ ] **Step 2: Run red test**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_edition.py::test_build_row_one_edition_assigns_deterministic_display_metadata -q
```

Expected: FAIL because `RowOneStory.display` does not exist.

- [ ] **Step 3: Implement models**

In `src/fashion_radar/row_one/models.py`, add:

```python
RowOneDisplayVariant = Literal["editorial", "portrait", "product", "signal"]
RowOneDisplayAccent = Literal["ink", "graphite", "steel", "cobalt", "rose"]


class RowOneStoryImage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    src: str
    alt: LocalizedText
    credit: str | None = None
    source_url: str | None = None


class RowOneStoryDisplay(BaseModel):
    model_config = ConfigDict(extra="forbid")

    variant: RowOneDisplayVariant
    accent: RowOneDisplayAccent
    image: RowOneStoryImage | None = None
```

Then add this field to `RowOneStory`:

```python
display: RowOneStoryDisplay | None = None
```

Export `RowOneStoryDisplay` and `RowOneStoryImage` from `src/fashion_radar/row_one/__init__.py`.

- [ ] **Step 4: Implement shared display helpers and deterministic assignment**

Create `src/fashion_radar/row_one/display.py` with the shared helper:

```python
from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from fashion_radar.row_one.models import (
    RowOneDisplayAccent,
    RowOneDisplayVariant,
    RowOneSectionKey,
    RowOneStoryDisplay,
)
from fashion_radar.row_one.utils import safe_external_url

if TYPE_CHECKING:
    from fashion_radar.row_one.models import RowOneStory


def display_for_section(section_key: str) -> RowOneStoryDisplay:
    mapping: dict[RowOneSectionKey, tuple[RowOneDisplayVariant, RowOneDisplayAccent]] = {
        "top_stories": ("editorial", "ink"),
        "brand_moves": ("editorial", "graphite"),
        "celebrity_style": ("portrait", "rose"),
        "hot_products": ("product", "cobalt"),
        "rising_radar": ("signal", "steel"),
    }
    variant, accent = mapping.get(section_key, ("editorial", "ink"))
    return RowOneStoryDisplay(variant=variant, accent=accent)


def display_for_story(story: RowOneStory) -> RowOneStoryDisplay:
    return story.display or display_for_section(story.section_key)


def safe_story_image_src(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized or any(ord(character) < 32 for character in normalized):
        return None
    if "\\" in normalized:
        return None
    external_url = safe_external_url(normalized)
    if external_url is not None:
        return external_url
    if not normalized.startswith("assets/"):
        return None
    pure_path = PurePosixPath(normalized)
    if pure_path.is_absolute() or ".." in pure_path.parts:
        return None
    if len(pure_path.parts) < 2:
        return None
    return str(pure_path)
```

In `src/fashion_radar/row_one/edition.py`, import `display_for_section` and pass `display=display_for_section(section_key)` in `_story_from_entity`, `_story_from_candidate`, and `_story_from_recent_item`.

- [ ] **Step 5: Run focused edition tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_edition.py -q
```

Expected: PASS.

---

### Task 2: App Payload And Schema Display Contract

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `schemas/row-one-app.schema.json`
- Modify: `tests/test_row_one_app_contract.py`

- [ ] **Step 1: Add failing app contract tests**

In `tests/test_row_one_app_contract.py`, import `RowOneStoryDisplay` and `RowOneStoryImage`.

Add `test_row_one_app_payload_includes_story_display_metadata`:

```python
payload = _payload(tmp_path)
story = payload["stories"][0]
assert story["display"] == {
    "variant": "editorial",
    "accent": "ink",
    "image": None,
}
_schema_validator().validate(payload)
```

Add `test_row_one_app_payload_sanitizes_display_image_sources`:

```python
edition = _edition()
edition.stories[0].display = RowOneStoryDisplay(
    variant="product",
    accent="cobalt",
    image=RowOneStoryImage(
        src="../secret.png",
        alt=LocalizedText(zh="坏图", en="Bad image"),
        credit="ROW ONE",
        source_url="javascript:alert(1)",
    ),
)
payload = _payload(tmp_path, edition)
assert payload["stories"][0]["display"] == {
    "variant": "product",
    "accent": "cobalt",
    "image": None,
}
_schema_validator().validate(payload)
```

Extend `test_row_one_app_schema_rejects_contract_drift` with this mutation:

```python
(
    lambda payload: payload["stories"][0]["display"].__setitem__("variant", "unknown"),
    "is not one of",
)
```

- [ ] **Step 2: Run red tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_app_contract.py::test_row_one_app_payload_includes_story_display_metadata tests/test_row_one_app_contract.py::test_row_one_app_payload_sanitizes_display_image_sources -q
```

Expected: FAIL because payload stories do not include `display`.

- [ ] **Step 3: Implement render payload helpers**

In `src/fashion_radar/row_one/render.py`, import `display_for_story` and `safe_story_image_src` from `fashion_radar.row_one.display`. Add helpers:

```python
def _display_payload(story: RowOneStory) -> dict[str, object]:
    display = display_for_story(story)
    return {
        "variant": display.variant,
        "accent": display.accent,
        "image": _image_payload(display.image),
    }


def _image_payload(image: RowOneStoryImage | None) -> dict[str, object] | None:
    if image is None:
        return None
    safe_src = safe_story_image_src(image.src)
    if safe_src is None:
        return None
    return {
        "src": safe_src,
        "alt": image.alt.model_dump(mode="json"),
        "credit": image.credit,
        "source_url": safe_external_url(image.source_url),
    }
```

Add `"display": _display_payload(story)` to `_story_payload`.

- [ ] **Step 4: Update schema**

In `schemas/row-one-app.schema.json`:

- add `"display"` to story `required`;
- add story property `"display": {"$ref": "#/$defs/storyDisplay"}`;
- add `$defs.storyDisplay`:

```json
{
  "type": "object",
  "required": ["variant", "accent", "image"],
  "additionalProperties": false,
  "properties": {
    "variant": {
      "enum": ["editorial", "portrait", "product", "signal"]
    },
    "accent": {
      "enum": ["ink", "graphite", "steel", "cobalt", "rose"]
    },
    "image": {
      "anyOf": [
        {"$ref": "#/$defs/storyImage"},
        {"type": "null"}
      ]
    }
  }
}
```

Add `$defs.storyImage` with required `src`, `alt`, `credit`, and `source_url`. `src` should accept safe http(s) URLs or `assets/...` paths. `source_url` should use the existing safe external URL definition. `credit` may be string or null.

Pin `src` with `anyOf`, not a broad string fallback:

```json
"imageSrc": {
  "anyOf": [
    {
      "type": "string",
      "format": "uri",
      "pattern": "^https?://[^\\s/]+"
    },
    {
      "type": "string",
      "pattern": "^assets/(?!.*(?:^|/)\\.\\.)(?!.*[\\\\\\x00-\\x1F])[A-Za-z0-9._~!$&'()*+,;=:@%/-]+$"
    }
  ]
}
```

Add a safe-image happy-path assertion so the `storyImage` schema is exercised:

```python
edition = _edition()
edition.stories[0].display = RowOneStoryDisplay(
    variant="product",
    accent="cobalt",
    image=RowOneStoryImage(
        src="assets/images/the-row.png",
        alt=LocalizedText(zh="The Row 图片", en="The Row image"),
        credit="ROW ONE",
        source_url="https://example.com/image-source",
    ),
)
payload = _payload(tmp_path, edition)
assert payload["stories"][0]["display"]["image"] == {
    "src": "assets/images/the-row.png",
    "alt": {"zh": "The Row 图片", "en": "The Row image"},
    "credit": "ROW ONE",
    "source_url": "https://example.com/image-source",
}
_schema_validator().validate(payload)
```

- [ ] **Step 5: Run focused app contract tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_app_contract.py -q
```

Expected: PASS.

---

### Task 3: Static Site Visual Slots And Language Persistence

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add failing render tests**

In `tests/test_row_one_render.py`, import `RowOneStoryDisplay` and `RowOneStoryImage`.

Add `test_render_row_one_site_includes_story_display_visual_slots`:

```python
render_row_one_site(_edition(), tmp_path)
index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
    encoding="utf-8"
)
css = (tmp_path / "assets" / "row-one.css").read_text(encoding="utf-8")

assert 'class="story-visual story-visual--editorial story-visual--ink"' in index_html
assert 'data-display-variant="editorial"' in index_html
assert 'class="lead-story-visual"' in index_html
assert 'class="story-card-visual"' in index_html
assert 'class="detail-visual"' in detail_html
assert "THE ROW" in index_html
assert "--paper: #f4f6f8" in css
assert "--accent: #2454ff" in css
assert "#f5f1ea" not in css
assert "#7d1f2d" not in css
```

Add `test_render_row_one_site_renders_safe_display_image_and_omits_unsafe_image`:

```python
edition = _edition()
edition.stories[0].display = RowOneStoryDisplay(
    variant="product",
    accent="cobalt",
    image=RowOneStoryImage(
        src="assets/images/the-row.png",
        alt=LocalizedText(zh="The Row 图片", en="The Row image"),
        credit="ROW ONE",
        source_url="https://example.com/image-source",
    ),
)
render_row_one_site(edition, tmp_path)
index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
assert '<img src="assets/images/the-row.png"' in index_html
assert 'alt="The Row image"' in index_html
detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
    encoding="utf-8"
)
assert '<img src="../assets/images/the-row.png"' in detail_html
assert 'class="detail-visual"' in detail_html

edition.stories[0].display.image.src = "../secret.png"
render_row_one_site(edition, tmp_path / "unsafe")
unsafe_html = (tmp_path / "unsafe" / "index.html").read_text(encoding="utf-8")
assert "../secret.png" not in unsafe_html
assert 'class="story-visual-fallback"' in unsafe_html
```

Add `test_row_one_js_persists_language_preference`:

```python
render_row_one_site(_edition(), tmp_path)
script = (tmp_path / "assets" / "row-one.js").read_text(encoding="utf-8")
assert 'const storageKey = "row-one:language"' in script
assert "localStorage.getItem(storageKey)" in script
assert "localStorage.setItem(storageKey, lang)" in script
assert 'stored === "zh" || stored === "en"' in script
assert 'setLang(initialLang, { persist: false })' in script
```

- [ ] **Step 2: Run red tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_includes_story_display_visual_slots tests/test_row_one_render.py::test_render_row_one_site_renders_safe_display_image_and_omits_unsafe_image tests/test_row_one_render.py::test_row_one_js_persists_language_preference -q
```

Expected: FAIL because visual slots, image rendering, and language persistence are not implemented.

- [ ] **Step 3: Implement template helpers**

In `src/fashion_radar/row_one/templates.py`, import `display_for_story` and `safe_story_image_src` from `fashion_radar.row_one.display`. Add helpers:

- `_render_story_visual(story: RowOneStory, section_title: LocalizedText, *, context: str) -> str`
- `_story_visual_initials(story: RowOneStory) -> str`

`_render_story_visual` should call `display_for_story(story)` and render:

- an `<img>` only when `safe_story_image_src(image.src)` returns a value;
- otherwise a fallback block containing the escaped initials, display variant, and localized section title.

Use context classes:

- lead: `lead-story-visual`
- card: `story-card-visual`
- detail: `detail-visual`

- [ ] **Step 4: Wire visual slots into index and detail**

Update `_render_lead_story`, `_render_story_card`, and the detail template path so:

- lead story includes a visual slot in the lead grid;
- every story card begins with a card visual slot;
- detail pages include a detail visual slot near the story header;
- all visible strings remain escaped;
- unsafe image paths never enter HTML.

- [ ] **Step 5: Update CSS**

In `row_one_css()`, update tokens to the colder editorial palette:

```css
--paper: #f4f6f8;
--ink: #101216;
--muted: #626a73;
--line: #d6dce3;
--panel: #ffffff;
--accent: #2454ff;
--steel: #e8edf3;
--chrome: #c8d0da;
```

Add styles for:

- `.story-visual`
- `.story-visual--editorial`
- `.story-visual--portrait`
- `.story-visual--product`
- `.story-visual--signal`
- `.story-visual--ink`
- `.story-visual--graphite`
- `.story-visual--steel`
- `.story-visual--cobalt`
- `.story-visual--rose`
- `.story-visual img`
- `.story-visual-fallback`
- `.story-visual-mark`
- `.story-visual-meta`
- `.lead-story-visual`
- `.story-card-visual`
- `.detail-visual`

Keep layout stable on mobile with explicit grid collapse and fixed aspect ratios. Do not add generated images, gradients blobs, or external assets.

- [ ] **Step 6: Persist language preference**

Replace `row_one_js()` with guarded storage logic:

```javascript
(() => {
  const storageKey = "row-one:language";
  const buttons = Array.from(document.querySelectorAll("[data-lang-toggle]"));
  const readStoredLang = () => {
    try {
      const stored = window.localStorage.getItem(storageKey);
      return stored === "zh" || stored === "en" ? stored : "en";
    } catch (_error) {
      return "en";
    }
  };
  const writeStoredLang = (lang) => {
    try {
      window.localStorage.setItem(storageKey, lang);
    } catch (_error) {
      return;
    }
  };
  const setLang = (lang, options = {}) => {
    document.body.classList.toggle("lang-zh", lang === "zh");
    document.documentElement.lang = lang === "zh" ? "zh-Hans" : "en";
    buttons.forEach((button) => {
      button.setAttribute("aria-pressed", button.dataset.langToggle === lang ? "true" : "false");
    });
    if (options.persist !== false) {
      writeStoredLang(lang);
    }
  };
  buttons.forEach((button) => {
    button.addEventListener("click", () => setLang(button.dataset.langToggle || "en"));
  });
  const initialLang = readStoredLang();
  setLang(initialLang, { persist: false });
})();
```

- [ ] **Step 7: Run focused render tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q
```

Expected: PASS.

---

### Task 4: ROW ONE Display Readiness Documentation

**Files:**
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Add failing docs assertion**

In `tests/test_row_one_docs.py`, add `test_row_one_docs_describe_display_media_readiness`:

```python
normalized = _normalized(_read(ROW_ONE_DOC))
for phrase in (
    "display/media readiness",
    "`display` object",
    "`display.image` is `null` until a safe image path is available",
    "safe `assets/...` image paths",
    "typographic fallback visual",
    "opendesign imagery is optional and not required for tests.",
    "open design imagery is optional and not required for tests.",
):
    assert phrase in normalized
```

- [ ] **Step 2: Run red docs test**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_display_media_readiness -q
```

Expected: FAIL because the docs do not describe display/media readiness.

- [ ] **Step 3: Update docs**

In `docs/row-one.md`, add a short section named `Display/Media Readiness` that states:

- every app story includes a `display` object with `variant`, `accent`, and `image`;
- `display.image` is `null` until a safe image path is available;
- safe image sources are `assets/...` generated site paths or safe http(s) URLs;
- generated pages render a typographic fallback visual when no image is present;
- OpenDesign imagery is optional and not required for tests.
- preserve the existing `Open Design imagery is optional and not required for tests.` wording while also mentioning OpenDesign as the local image-generation integration name, so both existing and new docs tests remain stable.

- [ ] **Step 4: Run docs tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py -q
```

Expected: PASS.

---

### Task 5: Integration, Review, And Release Gate

**Files:**
- Review all files changed in Tasks 1-4.

- [ ] **Step 1: Run focused integration tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_edition.py tests/test_row_one_app_contract.py tests/test_row_one_render.py tests/test_row_one_docs.py -q
```

Expected: PASS.

- [ ] **Step 2: Run ruff focused checks**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one tests/test_row_one_edition.py tests/test_row_one_app_contract.py tests/test_row_one_render.py tests/test_row_one_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one tests/test_row_one_edition.py tests/test_row_one_app_contract.py tests/test_row_one_render.py tests/test_row_one_docs.py
```

Expected: PASS.

- [ ] **Step 3: Submit code to opencode review**

The current user instruction makes local opencode the temporary review authority for this node. Do not add a Claude Code review gate unless the user changes that instruction again.

Create `docs/reviews/opencode-stage-269-code-review-prompt.md` describing the objective, files changed, and required review focus. Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-269-code-review-prompt.md)" > docs/reviews/opencode-stage-269-code-review.md
```

Fix all Critical and Important findings, then rerun focused tests.

- [ ] **Step 4: Run full release gate**

Run:

```bash
rm -rf dist
git diff --check
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config build
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_package_archives.py dist
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
```

Expected: PASS.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short
git add src/fashion_radar/row_one/models.py src/fashion_radar/row_one/display.py src/fashion_radar/row_one/__init__.py src/fashion_radar/row_one/edition.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py schemas/row-one-app.schema.json tests/test_row_one_edition.py tests/test_row_one_app_contract.py tests/test_row_one_render.py tests/test_row_one_docs.py docs/row-one.md docs/superpowers/specs/2026-07-02-stage-269-row-one-display-readiness-design.md docs/superpowers/plans/2026-07-02-stage-269-row-one-display-readiness-plan.md docs/reviews/opencode-stage-269-plan-review-prompt.md docs/reviews/opencode-stage-269-plan-review.md docs/reviews/opencode-stage-269-plan-rereview-prompt.md docs/reviews/opencode-stage-269-plan-rereview.md docs/reviews/opencode-stage-269-code-review-prompt.md docs/reviews/opencode-stage-269-code-review.md
git commit -m "Stage 269: prepare ROW ONE story display media"
git push origin main
```

After push, stop and provide a Handoff Summary with repo status, verified commands, uncommitted files, and next step.

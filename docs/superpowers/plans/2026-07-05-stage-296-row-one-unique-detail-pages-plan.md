# Stage 296 ROW ONE Unique Detail Pages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ensure every ROW ONE story has a unique local detail page and, when available, a matching local article sidecar instead of silently overwriting duplicate `story_id` / `detail_path` files.

**Architecture:** Fix the source of today's duplicate generated stories by de-duplicating story lists by `story.id` before section caps are applied, preserving the first ranked occurrence. Add a render-time invariant that rejects duplicate `story.id` or duplicate `detail_path` in any `RowOneEdition`, preventing future silent HTML/article overwrites from hand-built editions or new generators.

**Tech Stack:** Python 3.12, Pydantic models, static HTML rendering, pytest, ruff, uv with `UV_NO_CONFIG=1 uv --no-config run --frozen`.

---

## Product Gap Closed

Stage 296 closes a content-publication integrity gap in the report layer. The current generated `2026-07-05` site has `story_count=19` but only `17` unique story ids/detail hrefs, so two detail pages are overwritten and only `17` local article sidecars can be published. This stage makes `story_count`, unique detail pages, and local article sidecars agree whenever story content exists.

## File Structure

- Modify `src/fashion_radar/row_one/edition.py`
  - Add `_unique_stories_by_id(...)`.
  - Apply it before each section cap and after `max_stories` as a final guard.
- Modify `src/fashion_radar/row_one/render.py`
  - Add `_validate_unique_story_routes(...)`.
  - Call it before writing index/detail/data files.
- Modify `tests/test_row_one_edition.py`
  - Add RED coverage for duplicate candidate report inputs with the same title/source URL.
- Modify `tests/test_row_one_render.py`
  - Add RED coverage that duplicate ids/detail paths raise instead of overwriting detail pages.
- Add Stage 296 review artifacts under `docs/reviews/`.

## Task 1: Plan Review Gate

- [ ] **Step 1: Write plan-review prompts**

Create:

- `docs/reviews/claude-code-stage-296-plan-review-prompt.md`
- `docs/reviews/opencode-stage-296-plan-review-prompt.md`

Both prompts should ask whether generation de-dupe plus render fail-fast is the right boundary, whether preserving the first ranked story is correct, and whether any contract bump is unnecessary.

- [ ] **Step 2: Attempt Claude Code plan review**

Run:

```bash
timeout 180s claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-296-plan-review-prompt.md)"
```

If unavailable, record `docs/reviews/claude-code-stage-296-plan-review.md` as `Verdict: UNAVAILABLE`, not approval.

- [ ] **Step 3: Run opencode fallback plan review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-296-plan-review-prompt.md)"
```

Save a clean completed body to `docs/reviews/opencode-stage-296-plan-review.md`. Fix Critical/Important findings before implementation.

## Task 2: RED Tests

- [ ] **Step 1: Add edition de-dupe test**

In `tests/test_row_one_edition.py`, add:

```python
def test_build_row_one_edition_dedupes_duplicate_candidate_story_ids() -> None:
    shared_item = _representative_item(
        "Saint Laurent: a Shoulder Pad for Every Occasion",
        source_name="Fashion Week Daily",
        source_url="https://fashionweekdaily.com/saint-laurent-spring-summer-2027-menswear/",
    )
    duplicate_candidates = [
        _candidate(
            "Saint Laurent",
            "brand_or_designer",
            score=9.5,
            representative_items=[shared_item],
        ),
        _candidate(
            "Saint Laurent duplicate",
            "brand_or_designer",
            score=9.0,
            representative_items=[shared_item],
        ),
    ]

    edition = build_row_one_edition(
        report=_report(candidates=duplicate_candidates),
        as_of=AS_OF,
    )
    brand_stories = edition.section_stories("brand_moves")

    assert len(brand_stories) == 1
    assert len({story.id for story in edition.stories}) == len(edition.stories)
    assert len({story.detail_path for story in edition.stories}) == len(edition.stories)
```

Expected before implementation: FAIL because both duplicate candidate stories are retained.

- [ ] **Step 2: Add render fail-fast test**

In `tests/test_row_one_render.py`, add:

```python
def test_render_row_one_site_rejects_duplicate_story_routes(tmp_path) -> None:
    edition = _edition()
    duplicate = edition.stories[0].model_copy(deep=True)
    edition.stories = [edition.stories[0], duplicate]

    with pytest.raises(ValueError, match="Duplicate ROW ONE story id"):
        render_row_one_site(edition, tmp_path)

    assert not (tmp_path / "details" / "the-row-signal-1234567890.html").exists()
```

Expected before implementation: FAIL because render silently writes one detail file.

- [ ] **Step 3: Run RED tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_edition.py::test_build_row_one_edition_dedupes_duplicate_candidate_story_ids \
  tests/test_row_one_render.py::test_render_row_one_site_rejects_duplicate_story_routes \
  -q
```

Expected: both tests fail for the intended reasons.

## Task 3: GREEN Implementation

- [ ] **Step 1: Implement `_unique_stories_by_id(...)`**

In `src/fashion_radar/row_one/edition.py`, add near `_top_stories(...)`:

```python
def _unique_stories_by_id(stories: Iterable[RowOneStory]) -> list[RowOneStory]:
    unique_stories: list[RowOneStory] = []
    seen: set[str] = set()
    for story in stories:
        if story.id in seen:
            continue
        seen.add(story.id)
        unique_stories.append(story)
    return unique_stories
```

In `build_row_one_edition(...)`, change section extension to:

```python
unique_section_stories = _unique_stories_by_id(section_stories)
stories.extend(unique_section_stories[: SECTION_CAPS[section_key]])
```

After optional `max_stories`, add:

```python
stories = _unique_stories_by_id(stories)
```

- [ ] **Step 2: Implement render invariant**

In `src/fashion_radar/row_one/render.py`, add:

```python
def _validate_unique_story_routes(edition: RowOneEdition) -> None:
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for story in edition.stories:
        if story.id in seen_ids:
            raise ValueError(f"Duplicate ROW ONE story id: {story.id}")
        seen_ids.add(story.id)
        if story.detail_path in seen_paths:
            raise ValueError(f"Duplicate ROW ONE detail path: {story.detail_path}")
        seen_paths.add(story.detail_path)
```

Call it at the start of `render_row_one_site(...)`, before creating or cleaning output files.

- [ ] **Step 3: Run GREEN tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_edition.py::test_build_row_one_edition_dedupes_duplicate_candidate_story_ids \
  tests/test_row_one_render.py::test_render_row_one_site_rejects_duplicate_story_routes \
  -q
```

Expected: both pass.

## Task 4: Verification And Generated Site Proof

- [ ] **Step 1: Run focused ROW ONE tests and ruff**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_edition.py \
  tests/test_row_one_render.py \
  tests/test_row_one_app_contract.py \
  -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check \
  src/fashion_radar/row_one/edition.py \
  src/fashion_radar/row_one/render.py \
  tests/test_row_one_edition.py \
  tests/test_row_one_render.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check \
  src/fashion_radar/row_one/edition.py \
  src/fashion_radar/row_one/render.py \
  tests/test_row_one_edition.py \
  tests/test_row_one_render.py
```

- [ ] **Step 2: Run release gate**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
UV_NO_CONFIG=1 uv lock --check
```

- [ ] **Step 3: Rebuild today's site and prove counts agree**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one build \
  --config-dir configs \
  --data-dir data \
  --reports-dir reports \
  --as-of 2026-07-05T04:00:00Z \
  --output-dir reports/row-one/site \
  --latest-only
```

Then assert:

- `payload["story_count"] == len(payload["stories"])`
- unique story ids equal story count
- unique detail hrefs equal story count
- number of `details/*.html` equals story count
- local article sidecars equal detail pages when local article extraction produced one per story

## Task 5: Code Review, Commit, Push

- [ ] **Step 1: Create code-review prompts and attempt Claude Code**

Create:

- `docs/reviews/claude-code-stage-296-code-review-prompt.md`
- `docs/reviews/opencode-stage-296-code-review-prompt.md`

Attempt Claude Code with `--effort max`; record `Verdict: UNAVAILABLE` if it does not return a completed body.

- [ ] **Step 2: Run opencode code review**

Save clean completed review to `docs/reviews/opencode-stage-296-code-review.md`; fix Critical/Important findings.

- [ ] **Step 3: Commit and push**

Commit message:

```bash
git commit -m "Stage 296: enforce row one unique detail pages"
git push origin main
```

## Handoff Summary Template

```markdown
**Handoff Summary**
- Repo: `/home/ubuntu/fashion-radar`
- Branch/commit: `main` at `<sha>`, pushed to `origin/main`
- Verified commands: focused tests, full suite, ruff, release hygiene, uv lock, today's site rebuild/count proof
- Uncommitted files: `<git status --short>`
- Generated site: `reports/row-one/site` rebuilt but ignored
- Next step: continue content completeness/publishing polish.
```

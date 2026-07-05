Now I have enough to give a complete, grounded review. Let me compile it.

---

## Verdict

**Approve with Important fixes.**

The plan is architecturally sound. The scope is tight for a single node: one new module, two modified tests, one modified script, docs, and a snapshot refresh. The read-only constraint is correctly upheld — no rebuild, no writes, no external probes, and the JSON contracts are unchanged. A handful of implementation-level errors need correcting before the agentic worker starts.

---

## Critical Findings

**None.** No correctness-breaking issue was found that would cause the feature to be unimplementable or that would silently corrupt the site.

---

## Important Findings

**1. `paragraphs_zh` length check is wrong as written**
- Plan location: Task 2, Step 2 — `_load_article_sidecars` behavior.
- Issue: "Reject if `paragraphs_zh` is present and length differs from `paragraphs`." In `models.py`, `paragraphs_zh: list[str] = Field(default_factory=list)` — the field always exists and defaults to `[]`. Applying the check as written would reject any sidecar that has `paragraphs: ["..."]` and `paragraphs_zh: []` (no zh translation yet), which is a legitimate state.
- Why it matters: Would cause false-positive `row-one status` failures on valid sites with English-only articles.
- Fix: Change the check to: "If `paragraphs_zh` is non-empty, its length must equal `len(paragraphs)`."

**2. JS and CSS content assertions in the HTTP smoke are brittle**
- Plan location: Task 3, Step 2 — fetch assertions for `/assets/row-one.css` (checks `RowOneSerif`) and `/assets/row-one.js` (checks `row-one:language`).
- Issue: These are content-level assertions about bundle internals. Any stylesheet refactor or JS minifier change would break the smoke without indicating a real site problem. For a smoke test, HTTP 200 with a non-empty body is the correct bar for static assets.
- Why it matters: Turns a flaky smoke into a real blocker for unrelated asset changes, and undermines the "not a schema/app contract change" guarantee.
- Fix: Drop the content substring checks for CSS and JS. Assert only `response.status == 200` and `len(body) > 0`. Keep the `contract_version` JSON checks for the three data files — those are stable and meaningful.

**3. `_render_status_site_with_local_article` is referenced but never defined or stubbed in the plan**
- Plan location: Task 1, Step 3 — four tests call this helper; the plan only says "use existing `RowOneLocalArticle` fixture patterns from `tests/test_row_one_render.py`."
- Issue: There is no guarantee a suitable helper exists in `test_row_one_render.py`, and no shape is given for what this helper must produce. The implementer has no clear spec for whether the rendered local article needs a sidecar at `data/articles/`, what the `paragraph_indices` structure must look like, or how `data/local-intelligence.json` is populated.
- Why it matters: Under-specified helpers are the main cause of partially-correct implementations that pass their own scaffolded tests but fail the integrity checks they're supposed to exercise.
- Fix: Add a skeleton for `_render_status_site_with_local_article(tmp_path)` to Task 1, Step 3, showing the minimum: render a site with one story that has a local article sidecar at `data/articles/{story_id}.json` and a `data/local-intelligence.json` with at least one item whose `detail_path` points to that story.

**4. Polling loop in smoke helper has no sleep interval**
- Plan location: Task 3, Step 2 — "Poll HTTP until ready for up to 10 seconds. Do not wait on stdout."
- Issue: No inter-attempt sleep is specified. A naive tight loop calling `_fetch_local_http_path` every iteration will spin-wait for 10 seconds burning CPU if the server is slow, and will produce hundreds of failed connection attempts per second — some CI environments log each refused connection, creating noise and masking the real error.
- Why it matters: Makes the smoke unnecessarily noisy and resource-intensive under slow startup.
- Fix: Add "sleep 0.1 s between poll attempts" to the step description.

---

## Minor Findings

**1. `Path(tmp_path / str(story["detail_href"])).unlink()` path join assumption**
- Plan location: Task 1, Step 2 — `test_row_one_status_rejects_missing_current_detail_page`.
- Issue: `Path(a) / "/abs/path"` in Python discards `a` and returns `/abs/path`. If `detail_href` ever starts with `/`, the unlink targets the wrong path. The existing edition JSON uses relative paths like `details/foo.html`, so this works in practice — but the plan should state this assumption explicitly.
- Fix: Note that `detail_href` values in the edition JSON are relative paths; the test relies on this and should assert it or use `site_dir / Path(story["detail_href"])` syntax.

**2. `_detail_href_path` helper name vs. actual field name**
- Plan location: Task 2, Step 1.
- Issue: The field in `RowOneDailyLocalIntelligenceItem` is `detail_path` (not `detail_href`). The helper name `_detail_href_path` conflates the two concepts and will confuse the implementer.
- Fix: Name it `_validate_detail_path(value,*, label)` to match the model field.

**3. `_safe_local_intelligence_href` fragment spec omits empty-string anchor explicitly**
- Plan location: Task 2, Step 1 — "accepts only `""`, `local-article`, or `local-article-paragraph-N` fragments with `N >= 1`."
- Issue: The empty string case (`""`) means no fragment at all (just a page-level link). The `N >= 1` constraint is correct (paragraph indices are 1-based in fragments), but the spec doesn't clarify whether `N` is 1-indexed (fragment) vs0-indexed (Python list). The validator in Step 3 translates this as "sidecar paragraph index `N - 1` exists", confirming 1-based. This is correct but should be stated once in Step 1 to avoid an off-by-one bug.
- Fix: Add "fragment `N` is 1-based; use `paragraphs[N-1]`" to the Step 1 spec.

**4. `! rg` negation in Task 5 shell block**
- Plan location: Task 5, Step 2.
- Issue: `! rg ...` is a bash built-in negation. This works in interactive bash and in scripts with `set -e`, but the behavior differs between `bash -e` and non-`-e` modes, and it is not portable to `sh`. The rest of the verification commands in the plan all use plain exit-code semantics.
- Fix: Replace with: `rg --no-ignore -q '<a class="daily-local-intelligence-card"' reports/row-one/site/index.html && echo "FAIL: forbidden element found" && exit 1 || true`. Or verify the run context always uses `bash -e`.

**5. `AS_OF` constant assumed available in test**
- Plan location: Task 1, Step 1 — helper uses `AS_OF`.
- Issue: The plan doesn't confirm whether `AS_OF` is already defined in `tests/test_row_one_cli.py` from prior stages, or whether the implementer needs to add it.
- Fix: Add a note: "Reuse the existing `AS_OF` constant from the test module; do not add a second definition."

---

## Suggested Plan Adjustments

1. **Task 2, Step 2** — replace:
   > Reject if `paragraphs_zh` is present and length differs from `paragraphs`.
   with:
   > Reject if `paragraphs_zh` is non-empty and `len(paragraphs_zh) != len(paragraphs)`.

2. **Task 3, Step 2** — replace the two asset content assertions:
   > `/assets/row-one.css` contains `RowOneSerif`
   > `/assets/row-one.js` contains `row-one:language`
   
   with:
   > `/assets/row-one.css` returns HTTP 200 with a non-empty body  
   > `/assets/row-one.js` returns HTTP 200 with a non-empty body

3. **Task 3, Step 2** — add to the polling description:
   > Sleep 0.1 s between poll attempts to avoid a spin-wait.

4. **Task 1, Step 3** — add before the four test functions, a helper skeleton:```python
   def _render_status_site_with_local_article(tmp_path: Path) -> dict[str, object]:
       """Render a site with one story that has a local article sidecar and local-intelligence entry."""
       story = _render_populated_status_site(tmp_path)
       story_id = story["id"]
       articles_dir = tmp_path / "data" / "articles"
       articles_dir.mkdir(parents=True, exist_ok=True)
       (articles_dir / f"{story_id}.json").write_text(
           json.dumps({
               "story_id": story_id,
               "url": "https://example.com/local-article",
               "source_name": "Local Desk",
               "extracted_at": AS_OF,
               "paragraphs": ["First paragraph.", "Second paragraph."],
           }),encoding="utf-8",
       )
       local_intel_path = tmp_path / "data" / "local-intelligence.json"
       local_intel_path.write_text(
           json.dumps([{
               "key": "strongest_reads",
               "title": {"en": "Strongest Reads", "zh": "最强阅读"},
               "dek": {"en": "Key local signals.", "zh": "关键本地信号。"},
               "items": [{
                   "title": {"en": "Local insight", "zh": "本地洞察"},
                   "body": {"en": "Insight body.", "zh": "洞察正文。"},
                   "detail_path": str(story["detail_href"]) + "#local-article",
                   "paragraph_indices": [0],}],
           }]),
           encoding="utf-8",
       )
       return story
   ```Adjust to match the actual `RowOneDailyLocalIntelligenceItem` shape if the existing test helpers already produce a valid local article site.

5. **Task 2, Step 1** — rename `_detail_href_path` → `_validate_detail_path(value, *, label)` and `_safe_local_intelligence_href` → `_validate_local_intelligence_href(value, *, label)` for clarity and consistency with the model field names.

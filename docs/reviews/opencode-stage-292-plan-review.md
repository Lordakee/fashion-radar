# opencode Stage 292 Plan Review

Cross-checked against `render.py`, `templates.py`, `workflows.py`, `cli.py`, `collectors/article.py`, `row_one/models.py`, `tests/test_row_one_app_contract.py`, `tests/test_source_boundaries_docs.py`, `AGENTS.md`, `docs/source-boundaries.md`, `docs/PROJECT_BRIEF.md`, `CONTRIBUTING.md`, and the stage 290/291 lineage.

## Verdict
**Release-blocking issues exist. Do not implement until C1–C3 are resolved.** The render-layer shape is sound, but the plan understates a direct policy conflict, an absent source-config wiring dependency, and a determinism/network risk that the current scope does not cover.

## Critical

**C1. Direct conflict with the documented "avoid republishing full articles" boundary.**
The user goal — render downloaded article text on ROW ONE detail pages by default — collides with rules repeated across the repo:
- `AGENTS.md:73` — "Reports must preserve source attribution and avoid republishing full articles."
- `docs/PROJECT_BRIEF.md:187` — "Reports must use short snippets and links, not republished full articles."
- `docs/source-boundaries.md:301` — "Avoid storing full article text by default." — **this exact phrase is pinned by `tests/test_source_boundaries_docs.py:35`**.
- `CONTRIBUTING.md:80` — "Reports should store snippets/metadata and links, not republished full [articles]."

The plan's "generated-site-only, default SQLite unchanged" carve-out does **not** resolve this: `reports/row-one/site/` is still under `reports/`, and the rule is stated for *Reports*, not just storage. Stage 271's design (`docs/superpowers/specs/2027-07-03-stage-271-row-one-app-content-organization-design.md:117`) explicitly says ROW ONE "does not claim to produce full article text or translations of source articles."

**Resolution required (pick one before implementation):**
- (a) Reframe as **opt-in**: extraction is off by default, gated by an explicit config flag (e.g. `row_one.local_articles.enabled: false`), and the default `row-one build/preview/refresh` continues to render summary-only detail pages. This keeps the documented default intact and needs no docs/test phrase changes.
- (b) If the PM wants it on by default, the boundary docs (`AGENTS.md:73`, `docs/PROJECT_BRIEF.md:187`, `docs/source-boundaries.md:301`, `CONTRIBUTING.md:80`) and `tests/test_source_boundaries_docs.py:35` must be explicitly amended in this stage's plan with new wording that names the ROW ONE local-article exception and its safeguards (attribution retained, external-source fallback link preserved, robots+paywall respected, length-capped, off when trafilatura unavailable). The current plan does not list any of these as touched files.

**C2. `write_row_one_site_files` has no `SourceDefinition` context, so the existing safe-extraction pipeline cannot be reused as described.**
`collectors/article.py:extract_article` / `extract_article_with_metadata` require a `SourceDefinition` to gate on `source.article.enabled`, `source.article.paywalled_domains`, `source.article.respect_robots_txt`, and `source.http.user_agent`, plus a `RobotsPolicyChecker`. But `workflows.py:169 write_row_one_site_files` only receives `engine`, `scoring`, `candidate_discovery`, `entity_config`, and `recent_items` — **no sources**. The plan's phrase "use existing safe URL checks" maps only to `row_one/utils.safe_external_url`, which is a scheme sanitizer (rejects `javascript:`, non-http), **not** a robots/paywall/extractor gate.

The plan must specify, concretely:
- Where `row_one/articles.py` obtains the paywalled-domain list and user-agent (a new config block? `configs/scoring.yaml` extension? a static conservative default baked into `row_one/articles.py`?).
- How `RobotsPolicyChecker` is constructed and cached per host (one fetch of robots.txt per source host, cached across stories sharing that host).
- Whether extraction is skipped entirely when `trafilatura` is not importable (must be — and currently `pyproject.toml` makes trafilatura an optional extra, so default installs will hit this path).

Without this, `row_one/articles.py` either duplicates a weaker extraction pipeline (policy risk) or requires non-trivial new wiring the plan does not scope.

**C3. Network fetches during site build break the deterministic-render property and have no timeout/cache/concurrency/kill-switch policy.**
Today `render_row_one_site(edition, output_dir)` is a pure function of its inputs, and `tests/test_row_one_app_contract.py:_payload` (and many other tests) depend on that. The plan keeps that purity for `render_row_one_site` itself (good — `local_articles_by_story_id` threaded as data), but step 5 makes the CLI build path perform N network fetches (one per story) **by default**. The plan does not specify:
- Per-request timeout and max-bytes.
- Concurrency (sequential vs. thread pool) — sequential will make `row-one refresh` painfully slow for non-trivial editions.
- Cache read-back semantics for `data/articles/<story-id>.json` — is it a freshness-TTL cache (skip refetch if fresh), an always-overwrite artifact, or read-only-when-present? The plan implies the latter two without committing.
- A kill switch (env var or config) to disable extraction without code changes when offline / rate-limited.
- Behavior when the build is offline (the default fashion-radar free-first/local-first story) — extraction failure must never block site generation, which the plan does state ("do not block"), but tests must pin it.

## Important

**I1. `_render_article_contents()` nav is hardcoded and unconditional.**
`templates.py:1825` returns a static nav whose first entry is Summary, and `templates.py:125` renders it unconditionally inside `render_detail_html`. The plan says "render a new detail section before Summary" and "update article contents nav accordingly" — but for the nav to stay consistent with body order, and for the new nav entry to appear only when local content exists, the plan must commit to:
- Making `_render_article_contents` accept the local-article presence flag and emit the new anchor conditionally as the first entry.
- Making `render_detail_html` accept the per-story `RowOneLocalArticle | None` so both the section body and the nav are driven by one presence check.

**I2. `data/articles/` cleanup only fires under `latest_only=True`.**
`GENERATED_CHILDREN` (`render.py:28`) includes `"data"`, and `clean_row_one_site_children` `rmtree`s the whole `data/` dir — so `data/articles/` is covered **only when `latest_only=True`**. The plan claims "included in generated cleanup via existing data cleanup" without naming the gate. Verify every CLI refresh/build path passes `latest_only=True` (the `refresh` command does; double-check `build`/`preview`), otherwise stale `data/articles/<removed-story-id>.json` files leak across editions.

**I3. Pin `RowOneLocalArticle` model location.**
The plan says "Add `RowOneLocalArticle` model or equivalent" without a file. Put it in `row_one/models.py` to match every other ROW ONE Pydantic value object (`RowOneLink`, `RowOneStoryDisplay`, etc. all live there with `ConfigDict(extra="forbid")`), and keep `row_one/articles.py` for build/extraction logic only. This matters because the model is the contract for both the renderer and the JSON cache.

**I4. Story-ID filename safety.**
`data/articles/<story-id>.json` uses the story ID as a filename. Test fixtures follow `[a-z0-9-]+-[0-9a-f]{10}` (matching `_DETAIL_FILENAME_RE` at `templates.py:19`), but `RowOneStory.id` is not regex-validated by the model (it's a plain string field). Before writing the file, the plan must mandate a story-ID regex check (or `PurePosixPath(name).name == name` plus a charset allowlist) to prevent path traversal, `/`, `\`, `..`, or unicode surprises from a future story ID source.

**I5. The TDD seam must be a real protocol, not a callback.**
The plan says "injected extractor/fetcher to avoid live network." `collectors/article.py` already defines `HtmlFetcher(Protocol)` and takes `robots_checker` — mirror that in `row_one/articles.py`: define a local `ArticleExtractor(Protocol)` (or reuse `extract_article_with_metadata` directly by passing `source`, `html_fetcher`, `robots_checker`), so test fakes can be plugged at the seam. The plan should name this protocol explicitly so the implementation cannot accidentally hardcode `trafilatura.extract` inside the build path.

## Minor

**M1.** `skipped`/`reason` should be logged to build stdout (one line per skipped story) and **not** rendered in the HTML detail page. Stating "extractor unavailable" or "robots disallowed" on a public-facing page is undignified and leaks policy.

**M2.** A bilingual header (`Local Article / 本地正文`) on a mono-lingual extracted body will confuse readers. Add a sub-line like "Extracted from source (en)" / "本地正文（自动抽取，原文语言）" or detect and show the source language tag.

## Answers to the plan's review questions

1. **Technically reasonable for the current repo?** The render-layer shape is reasonable and minimal; the policy and source-wiring assumptions are not (C1, C2).
2. **Conflicts with source boundary tests?** **Yes** — `tests/test_source_boundaries_docs.py:35` pins "Avoid storing full article text by default.", and `AGENTS.md:73` / `PROJECT_BRIEF.md:187` / `source-boundaries.md:301` / `CONTRIBUTING.md:80` carry the rule. Either go opt-in (a) or amend docs+tests in this stage (b).
3. **App contract risks?** Low for `data/edition.json` if it stays unchanged (plan says so, and v7 base is correct since stage 290 was plan-only and stage 291 didn't bump). `data/articles/*.json` is a new generated cache, not part of the app contract, and `data/` is already in `GENERATED_CHILDREN` — safe under `latest_only=True`.
4. **Exact places to change:**
   - NEW `src/fashion_radar/row_one/articles.py` — build/extraction with injectable `HtmlFetcher` + `RobotsPolicyChecker`, paywall list, user-agent, timeout, cache TTL.
   - `src/fashion_radar/row_one/models.py` — add `RowOneLocalArticle`.
   - `src/fashion_radar/row_one/render.py:44` — `render_row_one_site(..., local_articles_by_story_id=None)`.
   - `src/fashion_radar/row_one/render.py:106` — `_write_detail_pages` threads article + writes `data/articles/<id>.json` (with story-ID filename check).
   - `src/fashion_radar/row_one/templates.py:119` — `render_detail_html(edition, story, local_article=None)`.
   - `src/fashion_radar/row_one/templates.py:125, 1825` — conditional nav entry + new section before Summary.
   - `src/fashion_radar/workflows.py:169` — `write_row_one_site_files` wires extraction; **must solve the SourceDefinition gap (C2)**.
   - `src/fashion_radar/cli.py:1551, 1409, 1448, 1511` — pass-through for the three call sites.
   - `docs/row-one.md` — brief note (per plan step 6).
   - If option (b): `AGENTS.md:73`, `docs/PROJECT_BRIEF.md:187`, `docs/source-boundaries.md:301`, `CONTRIBUTING.md:80`, `tests/test_source_boundaries_docs.py:35`.
   - Tests: new `tests/test_row_one_articles.py`, escape + cache-write cases in `tests/test_row_one_render.py`, and (only if option b) the boundary-docs test above.

**Recommendation:** Resolve C1 first (opt-in vs. docs amendment is a product decision, not an implementation detail), then re-scope C2/C3 in a revised plan before coding.

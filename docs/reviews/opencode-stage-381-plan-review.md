
## Status Of Previously Reported Findings

**C1 (singular count assertion) — FIXED.** Task 4 Step 2 now reads `assert "1 local read" in section_html` (singular), matching `_count_label(1, "local read", "local reads")`. GREEN will pass.

**I1 (signal/source count asymmetry) — FIXED.** The builder now sets `signal_count = len(signal_references)` and `source_count = len(source_names)`, both derived from the capped display tuples. The Data Contract prose was updated to say "displayed ... capped at `SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS`" for both counters. The caps test is internally consistent: 4 unique references → `signal_count == MAX_REFS == len(signal_references)`; 3 unique sources → `source_count == 3 == len(source_names)`.

**I2 (duplicate import block) — FIXED.** Task 2 Step 1 now says "Update the existing import block to add:" and lists only the two genuinely new symbols (`RowOneSavedArticleLocalRelatedReadEvidenceBridge`, `build_row_one_saved_article_local_related_read_connection_brief`).

**M1 (metric concatenation) — FIXED.** Metrics now built via `"\n".join((...))`.

**M2 (CSS insertion point) — FIXED.** Task 5 Step 4 now says "immediately after the `.saved-article-local-related-read-lane-header p` rule and before `.saved-article-local-related-read-card`."

**M3 (redundant `.strip()`) — acceptable.** Retained, matching the existing `_render_saved_article_local_related_read_references` pattern; harmless.

No remaining Critical findings. No remaining Important findings.

---

## Remaining Minor Findings

**m1 — `dek` is computed but never rendered or asserted (dead field).**

The Data Contract and Builder Rules define `dek` with concrete localized copy (`Why these saved local reads belong together.` / `说明这些本地保存阅读如何关联。`), the builder populates it, but the Render Rules template and the Task 5 Step 3 renderer emit only `title` (inside `<h3>`) and `lead` (inside `<p>`). No builder test reads `brief.dek`; no render test checks for the dek string. The copy section has no slot for it. Either render the dek (e.g., as a subtitle in `.saved-article-local-related-read-connection-brief-copy`) or drop the field and its copy so the data model carries only surfaces that reach the page.

**m2 — Task 6 Step 3 RED rationale is stale.**

The expected-failure note says "FAIL because docs paragraphs are not yet present and the renderer helper does not exist until Task 5 is complete." By Task 6, Task 5 is already done, so `_render_saved_article_local_related_read_connection_brief` exists and the workflow sentinel monkeypatch (`raising=True`) succeeds. The workflow sentinel and denylist assertions pass; only the docs boundary test fails. The net RED result is correct, but the stated reason should drop the renderer clause and say RED is docs-only.

**m3 — `git add` in Task 8 Step 6 omits rereview artifacts.**

The explicit path list includes the four primary review files but not `claude-code-stage-381-plan-rereview.md`, `opencode-stage-381-plan-rereview.md`, `claude-code-stage-381-code-rereview.md`, or `opencode-stage-381-code-rereview.md`. If any rereview runs (Task 1 Step 3 / Task 8 Step 4), those files stay uncommitted. Either add them conditionally or broaden the `git add docs/reviews/*stage-381*` pattern.

**m4 — `renderable_cards` extraction is assumed, not shown.**

Task 5 Step 2 uses `renderable_cards` directly in the brief-builder call, and the File Map says "compute `renderable_cards` once," but the plan never shows how to obtain the variable if the existing `_render_saved_article_local_related_reads` computes safe cards inline or under a different name. If the current code stores them under another symbol, the snippet as written raises `NameError`. Add a one-line note to reuse the existing `_renderable_saved_article_local_related_read_cards(...)` result into a local `renderable_cards` before both the brief and lane rendering.

**m5 — Hyphenation drift in the docs paragraph.**

The paragraph text says "generated-site only" (missing the second hyphen) while the Goal and title use "generated-site-only". The test and docs implementation strings match each other exactly, so no test fails, but the body copy is grammatically inconsistent with the feature name.

---

## Cross-Checks Performed (no issues)

- Lane-label ordering, dedup, and `_LANE_COPY[...][0]` access are consistent with the existing lane builder; the `summarizes_cards` assertions hold under `dataclasses.replace` reference inheritance (same_source inherits `references=("The Row",)`, exercised as a cross-card dedup case).
- Caps helper early-return logic produces exactly `MAX_REFS` entries for both signals and sources without off-by-one.
- Escape test depends on `normalize_row_one_paragraph` preserving markup while `_esc` escapes it — consistent with the existing reference-chip rendering path.
- `generated_contract_payload` denylist (JSON-only) and the file-stem denylist (file-name-only) will not false-positive on the CSS class `saved-article-local-related-read-connection-brief` rendered inside `articles/<story-id>.html`; the stem `related-read-connection-brief` is a substring of the CSS class but the stem check targets file names, matching the Stage 377–380 pattern.
- Docs stale-phrase negations use "creates/writes/adds/publishes" forms that are not substrings of the paragraph's "create/.../change" phrasing, so no false negatives.
- Lead copy, title copy, metric labels, and `_count_label` singular/plural forms all line up between Data Contract, builder, renderer, and tests.

END_OF_REVIEW

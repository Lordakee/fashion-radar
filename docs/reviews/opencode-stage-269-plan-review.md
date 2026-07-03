# Stage 269 ROW ONE Plan Review

I read the design spec, the plan, and the actual sources (`models.py`, `edition.py`, `render.py`, `templates.py`, `utils.py`, the app schema, and all four referenced test files) plus the docs test fixture. Findings below.

## Critical

None. The plan is feasible, additive, and does not break the generated app payload or the `row-one-app/v1` contract. The schema's new required `display` field is always satisfied because `_story_payload` will emit it (with fallback) for every story, including the empty-edition and undated paths covered by existing tests. No committed `edition.json` sample is schema-validated (the `test_first_run_smoke.py` stub is an unvalidated CLI mock), so the required-field change is safe.

## Important

1. **Workers are not actually parallel — there is a hard A → (B‖C) → D dependency.** `render.py` (Worker B) and `templates.py` (Worker C) both need `RowOneStoryDisplay`/`RowOneStoryImage` from `models.py` (Worker A). B's and C's red tests cannot turn green until A's models + `__init__.py` exports land. "Parallel Ownership" (plan:43-63) never states merge order. Recommend explicitly sequencing A first, then B+C, then D, or noting that workers run against a shared evolving branch.

2. **The display + image-safety logic is duplicated in three places.** The section→(variant,accent) mapping appears in `edition.py._display_for_section` (A), `render.py._fallback_display` (B), and `templates.py._story_display` (C); and `_safe_image_src` is implemented twice (B and C). The spec itself says "templates should use the same safe image decision." Two/three copies of security-sensitive and contract-sensitive logic will drift. Recommend a single source (e.g., a public `display_for_section` and `safe_image_src` in `utils.py` or a new `display.py`) owned by one worker, imported read-only by the others.

3. **Docs phrase trap in Task 4.** The existing `test_row_one_docs_include_user_required_phrases` requires (casefolded) `"open design imagery is optional and not required for tests."` — currently satisfied by `docs/row-one.md:39` ("Open Design", two words). The plan's new test requires `"opendesign imagery is optional and not required for tests."` ("OpenDesign", one word). Both must coexist. The plan never flags that line 39 must be preserved verbatim; a diligent implementer who "normalizes" the spelling will break one test or the other. Add a note.

4. **Task 5 Step 3 omits the primary reviewer.** `AGENTS.md` designates Claude Code as the primary reviewer for code reviews, but the plan only runs an opencode self-review (`opencode run --model glm-5.2 ...`). Either add the Claude Code code-review step, or explicitly record why opencode is the fallback reviewer for this stage.

## Minor

- **`storyImage` schema is never exercised by a happy-path test.** Only the unsafe-image→`null` path and the variant enum-drift are tested. Add one app-payload assertion with a safe `assets/...` (or safe `https://`) image so `_image_payload` and the `storyImage` schema def are actually validated end-to-end.
- **Detail-page `<img>` is not asserted.** The render image test only checks `index.html`. Assert the safe image also appears in the `detail-visual` slot.
- **Edition test fixture is under-specified.** The plan shows assertions for all five sections but not the report/recent-item fixture needed to guarantee one story per section. Point the implementer at the existing `_entity`/`_candidate`/`_recent_items` helpers in `tests/test_row_one_edition.py`.
- **Schema `src` pattern is left open.** "src should accept safe http(s) URLs or `assets/...` paths" risks an overly-permissive `{"type": "string"}` backstop. Pin a pattern so the schema stays a real contract.
- **CSS modifier classes are asserted in HTML but absent from the CSS task list.** The render test pins `class="story-visual story-visual--editorial story-visual--ink"`, but Step 5's "Add styles for" list omits the `.story-visual--{variant}`/`.story-visual--{accent}` modifiers. Cosmetic, but make the HTML contract and CSS task consistent.
- **Review-artifact authoring step is implicit.** The commit list includes `opencode-stage-269-plan-review*.md`, but no step writes the prompt/review files. Per `AGENTS.md`, ensure they are complete (no stubs/truncation) before commit.

## Non-goals check

No contradiction detected: no OpenDesign call, no raster generation, no image download, no new media cache, no collector/platform change, no schedule install or deploy, no compliance-review feature. The release-gate commands in Task 5 Step 4 are the repo's standard hygiene gates, not new deploy behavior.

## Verdict

**Acceptable with revisions.** The scope is correct and the app-contract behavior is preserved. Address the four Important findings before implementation — most of all, collapse the triplicated display/image-sanitation logic into one owned module and fix the worker sequencing/wording, otherwise B and C will ship divergent safety code.

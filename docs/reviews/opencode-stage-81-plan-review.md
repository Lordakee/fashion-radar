I'll review the Stage 81 plan. Let me start by exploring the relevant files in parallel.
Found the Stage 81 artifacts. Let me read them along with the baseline Stage 80 artifacts and the current test file.
Let me read the rest of the test file and the Stage 80 plan/spec for context.
Let me look at the actual README and CLI reference sections being targeted, plus check for existing Stage 81 review artifacts.
Let me read the Stage 80 code review (which flagged this issue), the actual doc sections, and existing Stage 81 review artifacts.
Let me read the existing Stage 81 plan review artifacts and look at the CLI reference downstream boundary to assess split hazards.
I have full context now. Here is my Stage 81 plan review.

## Stage 81 Plan Review — Verdict

**0 Critical, 1 Important, 4 Minor.** Scope is clean (tests + review artifacts only, no `src/`, prose, manifests, `uv.lock`, `AGENTS.md`, or boundary-diluting features). The local-only handoff boundary is preserved — the stage only *tightens* assertion scoping on phrases that already exist. One design defect needs fixing before implementation.

### Critical
None.

### Important

**I-1. README section terminator in the design is buggy and will truncate the boundary phrases.**
The design spec (`docs/superpowers/specs/2026-06-18-stage-81-...-design.md:26-28`) says to extract "the text between `### External Tool Import Path` and the next `external-tool-readiness` paragraph." But `external-tool-readiness` appears as a **route component inside the target section itself** at `README.md:184` (`external-tool-adapters -> external-tool-readiness -> external-tool-workflow`), well before the standalone readiness paragraph at `README.md:194`. A literal `split(..., "external-tool-readiness", 1)` lands on the route string and yields a slice ending at line 184 — **excluding the boundary phrases at `README.md:189-192`** ("does not run upstream tools" … "does not verify platform coverage"). Result: the tightened assertions fail, or an implementer "fixes" it by dropping the boundary loop, silently defeating the stage's purpose.

Fix: terminate at the next Markdown heading (`## Quickstart`, `README.md:218`) using the existing helper — `_markdown_section_matching_heading(_read(README), r"external tool import path")` — consistent with how the heat-movers tests (`tests/test_cli_docs.py:408-409`) scope sections. That helper returns heading-inclusive text, which also keeps the `"External Tool Import Path"` anchor assertion valid. The plan (`Task 2`) should name this method explicitly.

### Minor

**M-1. Task 5 allowlist is generic.** The plan says "Stage only Stage 81 allowlist files" without enumerating them, unlike Stage 80's explicit `git add` list (`stage-80-...-plan.md:359-369`). The separate "Confirm `uv.lock` is not staged" item partially compensates, but given the project's hard `uv.lock`-leak guardrail, an explicit list is safer.

**M-2. Community roadmap test left as-is is defensible but inconsistent.** The design (`spec:33-35`) keeps `test_community_signal_import_docs_have_external_tool_import_roadmap` unchanged because its boundary phrases are asserted against whole-doc `normalized` (`tests/test_cli_docs.py:1169-1179`), not the section. The rationale (unique anchors pin the section) is reasonable and matches Stage 80's "adequate" call, so this is out of scope — but for consistency the same scoping could apply later.

**M-3. README extraction method not pinned.** Even with I-1 fixed, the plan/design doesn't say whether the slice is heading-inclusive. If an implementer uses `text.split("### External Tool Import Path", 1)[1]`, the heading text is consumed and the `"External Tool Import Path" in section` assertion breaks. Recommend the helper in I-1, which is heading-inclusive.

**M-4. Live-capture review artifact hygiene.** `docs/reviews/opencode-stage-81-plan-review.md` is currently a 5-line exploration stub. Ensure the final committed review is the completed review, not the in-progress capture (same pattern Stage 80 used).

### What's solid
- No Markdown split hazards for *other* tests: Stage 81 makes no doc edits, so `_markdown_section` / `_markdown_section_matching_heading` bounds are untouched. The plan explicitly warns against inline `## ...` literals (`plan:35-36`).
- CLI test tightening (`plan:33-34`) is sound: the section bounds `## Local Import And Community Handoff` … `Print adapter registry examples:` already exist and pass at HEAD; moving the 5 boundary phrases from whole-doc `normalized` to `normalized_section` is correct since all five appear at `docs/cli-reference.md:88-89`.
- Boundary language is preserved and better enforced — no scope creep into connectors/scraping/platform APIs/ranking/demand proof.
- Verification (Task 3 focused → Task 4 full pytest/ruff/release-hygiene + the `uv.lock` public-lock dance) and the `! git diff --cached uv.lock` guard are adequate and consistent with Stage 80.

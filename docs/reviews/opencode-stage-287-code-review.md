## Verdict

**Approve with revisions.** Claude Code was unavailable (401 API key is disabled, recorded in `docs/reviews/claude-code-stage-287-code-review.md`), so this is the opencode fallback review using `zhipuai-coding-plan/glm-5.2` variant `max`. The Stage 287 **code** implementation is correct, complete, deterministic, and safe: all eight review requirements are satisfied, the full suite passes (1907 tests, including 406 targeted ROW ONE tests), `ruff check`, `ruff format --check`, `uv lock --check`, and `git diff --check` are all clean, and `git diff` touches exactly the 13 planned source/test/doc files with no lockfile, dependency, or unrelated change. The only release-gate blocker is in the **review artifacts** themselves, not the code. Two untracked review records fail `scripts/check_release_hygiene.py` (exit 1) due to captured process chatter at the start of the file, which violates both the AGENTS.md "no tool-status messages / live-capture stubs" rule and the automated release gate.

## Critical Findings

None. Verified against `render.py:149-312` (helpers), `templates.py:1380-1491` (renderer + href guard), `schemas/row-one-app.schema.json:323-437` and `:47-49` + `:13` (required top-level field + nested `$defs`), `schemas/row-one-manifest.schema.json:30` (v6 const), `cli.py:1775-2000` (status validator), `scripts/check_first_run_smoke.py:1298-1372` (smoke validator), `briefing_topics.py:78-88` (shared normalizer), and the full test scaffold. The deterministic rules (group order, sort key, dek trigger on `signal_count == 0`, `_plural_word` summaries, boundary text) all match the approved plan, including the I1 fix from the plan rereview.

## Important Findings

**I1. Review artifacts fail the release-hygiene gate (process chatter at start).**
- **Where:** `docs/reviews/opencode-stage-287-plan-review.md:1-7` ("I'll review the Stage 287 plan. Let me start by reading ...") and `docs/reviews/opencode-stage-287-plan-rereview.md:1-8` ("I'll perform a read-only rereview ... Let me first gather ...").
- **Evidence:** `UV_NO_CONFIG=1 uv --no-config run python scripts/check_release_hygiene.py --repo-root .` exits 1 with `forbidden review capture artifact in untracked file: docs/reviews/opencode-stage-287-plan-rereview.md:1: process chatter at start` and the same for `opencode-stage-287-plan-review.md:1`.
- **Why it matters:** Both files are in the Stage 287 changed scope and are committed alongside the code. The release gate (Task 5, Step 1) explicitly runs `check_release_hygiene.py`, so this currently blocks the Stage 287 release. AGENTS.md also requires every review record to contain "completed review output and no live-capture stubs, duplicated or truncated text, tool-status messages, or empty output."
- **Smallest safe fix:** Delete the conversational preamble lines (plan-review lines 1-7 up to the `---` separator; plan-rereview lines 1-8 up to the `---` separator) so each file begins directly with its `## Verdict` section. No content changes to the actual verdict/findings are needed; both reviews' substantive output is already complete and correct.

## Minor Findings

- **M1.** `src/fashion_radar/row_one/templates.py:1471-1476` — the `.signal-synthesis-meta` row renders English-only labels (`"stories"`, `"evidence"`, `"+N local delta"`) without `data-lang="en"`/`data-lang="zh"` wrappers, so the meta stays English when the page is toggled to Chinese. The section title/dek/boundaries/summary are all correctly bilingual, and the sibling `.briefing-topic-meta` (`templates.py:1556-1569`) does use bilingual spans, so this is an i18n polish gap. Non-blocking; no safety or contract impact.
- **M2.** No test exercises intra-group multi-signal ordering (Deterministic Rule 5: `positive_heat_delta_sum` desc, `evidence_count` desc, `story_count` desc, name asc). Every populated case has at most one signal per group, so the `_signal_synthesis_sort_key` tiebreak at `render.py:305-312` is unverified. Carried over from the plan rereview (M2 there); explicitly optional and non-blocking.
- **M3.** `docs/reviews/claude-code-stage-287-code-review.md` currently contains only `Failed to authenticate. API Error: 401 API key is disabled`. This is intentional per Task 5 Step 2 ("record that in the Claude review artifact") and `check_release_hygiene.py` does not flag it, but it is technically a tool-status message. Prior stages use the same pattern, so no action is required; flagged only for completeness.

## Recommended Fixes

1. **Block release (I1):** strip the process-chatter preambles from `docs/reviews/opencode-stage-287-plan-review.md` and `docs/reviews/opencode-stage-287-plan-rereview.md` so each starts at its `## Verdict` heading, then rerun `check_release_hygiene.py` to confirm exit 0.
2. **Optional (M1):** wrap the `.signal-synthesis-meta` label/count spans in `data-lang="en"`/`data-lang="zh"` pairs (or reuse the bilingual label pattern from `_render_briefing_topic_card`) for Chinese-locale parity.
3. **Optional (M2):** add a two-brand-signal case to `tests/test_row_one_app_contract.py` to lock the Rule 5 sort tiebreak.

With I1 fixed, the Stage 287 implementation is safe to commit and push. The code itself has no Critical or Important findings.

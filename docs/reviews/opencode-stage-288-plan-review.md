## Stage 288 Plan Review — Findings

### Critical
None.

### Important
None.

### Minor

**M1. Missing `--frozen` on `uv run` verification (Task 3 & 4, lines 178, 209, etc.)**
AGENTS.md states: *"For agent-run verification commands, prefer `uv --no-config run --frozen ...`"*. The plan uses `UV_NO_CONFIG=1 uv --no-config run pytest ...` without `--frozen`. Risk is low because `UV_NO_CONFIG=1` already blocks user-level mirror config and the plan forbids `pyproject.toml` changes, so relocking should not trigger. Recommend adding `--frozen` for full compliance and as belt-and-suspenders against silent lockfile rewrites. The Task 4 `git diff --exit-code -- uv.lock pyproject.toml` guard would catch any accidental change regardless.

**M2. Plan-review artifacts listed but not tasked (File Structure vs. Task 3, lines 22-24 vs. 168-171)**
The File Structure section promises *"Save Stage 288 plan review prompt and review output"* in `docs/reviews/`, but Task 3 only creates the four **code** review artifacts (`claude-code-stage-288-code-review-*`, `opencode-stage-288-code-review-*`). No step creates `...-stage-288-plan-review-*` files. Per AGENTS.md, plan reviews must be recorded under `docs/reviews/`. Either (a) add a task step to write the plan-review prompt + this review output before Task 1, or (b) clarify in the File Structure that plan-review artifacts are owned by the review workflow, not this plan's implementer.

**M3. Task 1 ordering test setup is non-trivial (Task 1 Step 1, lines 41-48)**
Building four same-group brand signals that cleanly exercise all four tiebreak tiers (`positive_heat_delta_sum` → `evidence_count` → `story_count` → casefold `name`) requires the implementer to understand how `briefing_topics_payload()` aggregates per-brand metrics from multiple stories (see `render.py:174-198`, `_signal_payload_from_topic`). The plan gives the assertion target but no concrete fixture. Not a flaw, but the implementer should model data like the existing `test_row_one_app_daily_digest_includes_briefing_topics_for_clients` (test_row_one_app_contract.py:599) and verify each tier with a distinct brand name. Note the sort key in the plan (lines 65-73) is **identical** to the current `_signal_synthesis_sort_key`, so this is a pure regression lock, not a bug fix — the plan already acknowledges this at line 58.

### Answers to the five questions

1. **Scope reasonable and small?** Yes — two test additions, one rendering helper, review artifacts. Narrow and additive; no payload-contract change, so no `row-one-app/v6` bump needed.
2. **Tests aligned with architecture?** Yes. Task 1 reads the rendered payload (public path through `render_row_one_site`), not the private sort key directly. Task 2 matches the exact strings the proposed helper emits (verified: `1 story`, `1 evidence link`, `+0 local delta` / `1 条故事`, `1 条证据链接`, `+0 本地增量`). Existing escape test (`test_render_row_one_site_escapes_signal_synthesis_payload_values`) remains valid because the helper still routes `label` through `_esc`.
3. **Unnecessary/risky files?** No. Only existing source/test files plus standard review records under `docs/reviews/`.
4. **Verification sufficient?** Mostly yes. Focused + full pytest, ruff check/format, lockfile check, release hygiene, and `git diff --check` plus a `uv.lock`/`pyproject.toml` drift guard. Only gap is the `--frozen` flag (M1).
5. **Change before implementation?** Address M1 (add `--frozen`) and M2 (resolve the plan-review artifact ownership). M3 is implementer guidance, not a plan edit. No blockers — safe to proceed after the minor fixes.

**Recommendation:** Proceed after applying M1 and clarifying M2. The core technical approach (bilingual meta helper + ordering regression) is correct and well-matched to the codebase.

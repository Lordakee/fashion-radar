# Stage 212 Plan Review

**Verdict:** APPROVE_WITH_NITS

## Critical

None.

## Important

**Task 5 Step 5: unconditional `git add` of conditional opencode review files will abort the final commit.**

Both opencode review files are declared conditional ("Conditionally add"), yet the final `git add` command lists them unconditionally:

```bash
git add docs/reviews/claude-code-stage-212-code-review.md docs/reviews/opencode-stage-212-code-review.md ... docs/reviews/opencode-stage-212-plan-review.md
```

If either opencode pass was skipped (the normal case for a clean review), the file doesn't exist, `git add` exits non-zero with *"pathspec did not match any files"*, and the release commit never runs. Fix: use `--ignore-missing` on that line, e.g.:

```bash
git add --ignore-missing docs/reviews/claude-code-stage-212-code-review.md docs/reviews/opencode-stage-212-code-review.md docs/superpowers/plans/2026-06-29-stage-212-source-model-plumbing-plan.md docs/reviews/claude-code-stage-212-plan-review.md docs/reviews/opencode-stage-212-plan-review.md
```

## Nits

1. **`sed -n '1,260p'` review cap (Task 0 Step 1 and Step 2):** A detailed Claude Code review routinely exceeds 260 lines. The truncated output is stored in the `.md` artifact, so later readers get an incomplete record. Consider `sed -n '1,500p'` or removing the cap and relying on terminal scroll.

2. **Both RED stub-collector tests created before either is run (Task 2 Steps 1–2):** Both `test_collectors_html.py` and `test_collectors_sitemap.py` are written in sequence before any run step. This is harmless but the combined Step 3 run masks which file caused an error. True TDD purity would write + run each independently. Not a blocker.

3. **`MANUAL_IMPORT` ordering in enum patch:** The plan moves `MANUAL_IMPORT` to the end (after `SITEMAP`), which matches the spec's section 5.1 snippet exactly. Noted only to confirm this is intentional alignment with the spec, not a mistake.

## Résumé

Line numbers, class/method signatures, and import paths all check out against the real code: `SourceType` lines 8–13✅, `url` on line 66 ✅, `validate_source_target` lines 83–91 ✅, `_default_collectors` lines 116–121 ✅, enrichment block lines 91–104 ✅, `SourceType` already on runner.py line 18 ✅, `SourceType` already imported in `tests/test_workflows.py` line 11 ✅. `CollectorResult.success` signature matches the stubs' call sites. The enrichment-skip test correctly exercises `source.type`-driven skip with an explicit extractor spy, proving the guard is not confused by `article.enabled`. Scope is tight (no extraction, no schema change, no new dep). Iron rules respected in both Task 0 and Task 5. The one operational fix needed (`--ignore-missing`) is a one-word change.

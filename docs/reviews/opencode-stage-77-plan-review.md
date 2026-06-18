I'll review the Stage 77 plan documents. Let me start by reading the spec and plan, plus relevant context files.
Now let me verify the plan's claims against actual repo state in parallel.
Let me verify remaining critical files referenced by the plan.
Let me verify remaining critical context: scoring config, docs structure, and the match_entities signature.
Let me check the REVIEW_PROTOCOL.md to verify the deviation from Claude Code review is acceptable, and verify trends JSON structure.
# Stage 77 Plan Review

Reviewed both documents against repo state (entity pack contents, existing tests, `scripts/check_package_archives.py`, `docs/REVIEW_PROTOCOL.md`, `AGENTS.md`, `cli.py` output strings, `models/trend.py`, current `git status`). All 10 expected entities and 6 entity types exist in `configs/entity-packs/fashion-watchlist.example.yaml:1`.

## Critical

**C1 — Review tooling and file naming deviate from `docs/REVIEW_PROTOCOL.md` and `AGENTS.md` without reconciling them.**
- `AGENTS.md:21-28` and `docs/REVIEW_PROTOCOL.md:8,13-18,57-58` mandate `claude --effort max --permission-mode plan --no-session-persistence` and file names `claude-code-stage-N-{plan,release}-review.md`.
- `docs/REVIEW_PROTOCOL.md:68` explicitly states "Older `opencode-*` records under `docs/reviews/` are historical audit records" (i.e., opencode naming is deprecated).
- The plan (Task 6 Step 3 and File Map) uses `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max` and creates `docs/reviews/opencode-stage-77-*.md`. The plan's "Review Protocol Note" admits the deviation: "This stage-local review path does not change repository review-protocol documents."

This self-acknowledged deviation must be resolved before implementation: either (a) update `docs/REVIEW_PROTOCOL.md` and `AGENTS.md` to bless opencode/glm-5.2 as an allowed reviewer and add `opencode-stage-N-*` as a current naming pattern (not "historical"), or (b) follow the protocol and use Claude Code with `claude-code-stage-77-*` file names. The current plan leaves the docs inconsistent with the actual practice.

## Important

**I1 — Task 7 Step 1 lockfile verification is not actionable as written.**
`uv.lock` is currently modified with a mirror rewrite (`git status` shows `M uv.lock`). `UV_NO_CONFIG=1 uv lock --check` will therefore fail. The plan's expected output ("public lockfile check passes after excluding or fixing any local mirror rewrite") gives no concrete remediation. Add an explicit step (e.g., `git stash push -- uv.lock` or `git checkout -- uv.lock`) before the lockfile check, with a restore step after, or move the lockfile check to a state where the public canonical is restored. Without this, Task 7 Step 1 cannot pass.

**I2 — Task 1 Step 3 dry-run artifact check is weaker than the established pattern and misses SQLite sidecars.**
The proposed test uses `assert list(tmp_path.rglob("*.sqlite")) == []`. The existing analogue at `tests/test_community_signal_import_contract.py:246-250` uses `*.sqlite*` (catching `.sqlite-wal`/`.sqlite-shm`) plus globs for `fashion-radar-*.json`, `fashion-radar-*.md`, `latest.*`, `report-index.json`. Mirror the existing strictness so the new sample is held to the same dry-run guarantee.

**I3 — Workflow test (Task 3) relies on trends producing entity deltas without setting `--baseline-as-of`.**
The test asserts `EXPECTED_REPORT_ENTITIES <= {delta["name"] for delta in trend_payload["deltas"]}` but only passes `--as-of`. `TrendComparison` at `src/fashion_radar/models/trend.py:60` requires both `as_of` and `baseline_as_of`, and the CLI at `src/fashion_radar/cli.py:1516,1589` can construct comparisons with `deltas=[]`. If the default baseline resolves to a snapshot that doesn't exist in the temp DB, deltas could be empty. Either pass `--baseline-as-of` explicitly with a value guaranteed to produce NEW-status deltas for the matched entities, or verify the default baseline behavior by running the trends command once against the watchlist pack before finalizing the assertion.

**I4 — Task 5 Step 3 under-specifies first-run.md content vs. its docs test.**
Step 3 says only "Add the same command block and expected-match/boundary wording to `docs/first-run.md`." But the docs test (Task 5 Step 1, `test_first_run_guide_documents_optional_watchlist_local_sample`) requires six specific boundary phrases (`optional local sample does not fetch URLs`, `does not collect platform data`, `does not prove demand`, `does not rank brands`, `does not verify platform coverage`, `does not add connectors`) plus five entity names (`Khaite`, `Alaia Le Teckel`, `Miu Miu Arcadie`, `Mary Jane Shoes`, `Boho Revival`) and `fashion-watchlist.example.yaml`. Spell out the full required block in Step 3 so implementation cannot ship only the commands.

## Minor

**M1 — Task 4 SDIST path position is ambiguous.**
Step 1 says "after the existing community signal examples" in `scripts/check_package_archives.py`. Step 2 pins the test file position to "after `examples/community-signals.example.json`". Use the same pinned position in both files (between `examples/community-signals.example.json` and `examples/community-signal-profile.example.json` at `scripts/check_package_archives.py:55` and `tests/test_package_archives.py:54`).

**M2 — README section placement interacts with an existing test slice.**
`tests/test_cli_docs.py:658-661` slices README between `### Manual Repo-Local Sample Flow` and `### Automated First-Run Smoke`. Inserting `### Optional Expanded Watchlist Sample` between them (Task 5 Step 2) includes the new section in that slice. The existing assertions still hold (first `match --config-dir` precedes `imported-signals-summary`), but inserting the new section *after* `### Automated First-Run Smoke` keeps the existing slice clean. Either move the insertion point or update the test's split markers.

**M3 — Boundary wording style diverges from surrounding docs.**
The plan uses "does not X" (`does not fetch URLs`, `does not collect platform data`, ...). `AGENTS.md`, `docs/source-boundaries.md`, and other Stage docs predominantly use "no X" (`no scraping`, `no platform APIs`, ...). Both styles pass the proposed tests, but matching the prevailing local style keeps the docs corpus consistent.

**M4 — Long single-line pytest selectors.**
Task 1 Step 5 and Task 5 Step 1 verification commands are single very long lines. Backslash-continuation or `-k` filters would improve readability and reduce copy-paste error risk.

## Notes

**N1 — Scope boundary is clean.** Spec and plan explicitly enumerate every prohibited behavior (scraping, browser automation, platform APIs, account/session/cookie/token/proxy/CAPTCHA, media downloads, monitoring, scheduling, source acquisition, demand proof, ranking, coverage verification, compliance-review). The sample is synthetic local CSV only. ✓

**N2 — Producer contract boundary preserved.** Plan explicitly keeps the new sample out of `COMMUNITY_SIGNAL_EXAMPLES` (the canonical two-row producer example tuple at `tests/test_community_signal_lint.py:22-27` and `tests/test_community_signal_import_contract.py:20-25`) and out of `example_paths` in the community-signal profile. Existing two-row assertions at `tests/test_community_signal_lint.py:63-66` and `tests/test_community_signal_import_contract.py:104-106` are untouched. ✓

**N3 — Default first-run smoke untouched.** No changes to `examples/community-signals.example.{csv,json}`, `configs/entities.example.yaml`, `scripts/check_first_run_smoke.py`, or starter entity expectations. ✓

**N4 — Package archive coverage is adequate.** `SDIST_REQUIRED_PATHS` extension plus the new `test_rejects_sdist_without_watchlist_community_signal_sample` regression test mirror the existing pattern at `tests/test_package_archives.py:294-331`. ✓

**N5 — uv.lock mirror exclusion is correctly handled in commit staging.** Task 7's `git add` list omits `uv.lock`. But see I1 — the verification step itself still needs a concrete remediation. ✓

**N6 — All expected entities and types verified present** in `configs/entity-packs/fashion-watchlist.example.yaml:1`: brands (`Khaite`, `Loewe`, `Miu Miu`), products (`Khaite Lotus Bag`, `Loewe Puzzle Bag`, `Alaia Le Teckel`, `Miu Miu Arcadie`), designer (`Jonathan Anderson`), celebrity (`Bella Hadid`), category (`Mary Jane Shoes`), trend (`Boho Revival`). Six types, satisfying "at least four" and "at least one product and one trend." ✓

**N7 — CSV is well-formed.** 8 rows × 8 fields, no embedded commas, `source_weight` values 1.0–1.3 within schema bounds (`exclusiveMinimum: 0`, `maximum: 5`), all timestamps UTC June 2026, all URLs under `https://example.com/community-watchlist/`. ✓

**N8 — CLI output strings verified** in `src/fashion_radar/cli.py`: `Validated {N} manual signal rows` (1968, 1983), `Imported {N} manual signal rows` (1984), `Processed {N} items` (2029). The workflow test's `Processed 8 items` assertion depends on `summary.items_processed == 8` after import — this matches the manual importer's one-item-per-row behavior. ✓

**N9 — Trend JSON shape verified.** `TrendDelta.name: str` at `src/fashion_radar/models/trend.py:31`; `TrendComparison.deltas: list[TrendDelta]` at line 60. Test structure `{delta["name"] for delta in trend_payload["deltas"]}` is correct, conditional on I3.

**N10 — CLI auto-creates `reports_dir`.** `src/fashion_radar/cli.py:496` calls `reports_dir.mkdir(parents=True, exist_ok=True)`, so the workflow test not pre-creating `reports_dir` is safe.

---

## Answers to the six review questions

1. **Useful starter coverage without runtime/default-smoke change?** Yes — sample is additive, no `src/` changes, default smoke untouched. (N1, N3)
2. **Tests strong enough?** Mostly — lint, fields, importer, dry-run, entity match, end-to-end workflow, archive, and docs drift are all covered. Weaknesses: I2 (dry-run artifact strictness) and I3 (trends baseline determinism) must be tightened before this can be called deterministic.
3. **Package archive/docs drift adequate?** Yes — see N4 and Task 4/5 coverage; M1 is cosmetic.
4. **Boundary clear (no scraping/APIs/etc.)?** Yes — see N1.
5. **uv.lock mirror rewrite correctly avoided?** Partially — commit staging excludes it (N5) but the verification step is not actionable as written (I1).
6. **Optional sample kept out of producer contract and two-row example assumptions?** Yes — see N2.

**Recommendation:** Fix C1, I1, I2, I3, and I4 before implementation. M1–M4 can be addressed during implementation.

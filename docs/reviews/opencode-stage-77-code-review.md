I'll review the Stage 77 worktree changes. Let me start by examining the current state.
Let me read the new sample, the new test file, and review all in-scope changes in parallel.
Now let me review the test changes and the package archive script.
Let me check the entity pack YAML, the producer profile (to verify the sample is NOT in example_paths), and the schema to verify allowed fields.
Let me verify the allowed schema fields, producer profile example_paths, and check the trends baseline logic.
Let me verify the watchlist sample is NOT in the canonical producer profile example_paths, and check the schema fields.
Let me look at the review artifacts and verify the trends command handles the baseline correctly, plus check the schema for source_weight constraints.
Let me run the verification suite to confirm the prior verification holds, and double-check the scoring example exists.
Let me verify the new sample doesn't get picked up by any glob-based first-run smoke or example discovery (critical for the "doesn't change default first-run smoke" criterion).
Let me run the first-run smoke test specifically to confirm the new sample doesn't disturb default behavior.
## Stage 77 Code Review — Result

I inspected the worktree, ran the verification commands, and cross-checked the scope boundaries in `AGENTS.md`.

### Verification (re-run independently)
- `pytest tests/test_community_signal_lint.py tests/test_community_signal_import_contract.py tests/test_entity_packs.py tests/test_watchlist_sample_workflow.py tests/test_package_archives.py tests/test_cli_docs.py` → **199 passed**
- `pytest tests/test_first_run_smoke.py` → **67 passed** (default smoke unchanged)
- `ruff check` + `ruff format --check` on the six in-scope test files → **clean**
- `git diff --check` → **clean**

### Findings against acceptance criteria
- **Allowed fields / shape**: `examples/community-signals.watchlist.example.csv:1` header is exactly the 8 `ALLOWED_COMMUNITY_SIGNAL_FIELDS` from `src/fashion_radar/community_signals.py:16`; 8 rows, all `source_name=Community Watchlist Sample`, `platform=community`, `source_weight` in `(0, 5]`. ✅
- **Outside canonical profile**: `src/fashion_radar/community_signal_profile.py:14-19` `COMMUNITY_SIGNAL_EXAMPLE_PATHS` still lists only the 4 original files; the watchlist sample is intentionally excluded, and `test_first_run_smoke.py:1319` still anchors on the non-watchlist example. ✅
- **Sample/pack consistency**: every entity named in README/first-run/test (`Khaite`, `Khaite Lotus Bag`, `Loewe`, `Loewe Puzzle Bag`, `Jonathan Anderson`, `Bella Hadid`, `Alaia Le Teckel`, `Miu Miu Arcadie`, `Mary Jane Shoes`, `Boho Revival`) exists in `configs/entity-packs/fashion-watchlist.example.yaml` and the CSV rows target them. ✅
- **Archive guard**: `scripts/check_package_archives.py:56` adds the sample to `SDIST_REQUIRED_PATHS`; `tests/test_package_archives.py:314` proves an sdist without it is rejected. ✅
- **Boundary statements**: README, `docs/first-run.md`, `docs/entity-packs.md`, and `docs/github-upload-checklist.md` all carry the "no fetch URLs / no platform collection / no demand proof / no ranking / no coverage verification / no connectors" language, asserted by `tests/test_cli_docs.py:780-872`. ✅
- **Scope untouched**: no `src/` changes, no dependency-manifest changes. The `uv.lock` diff is purely the pre-existing `pypi.org → tsinghua` mirror rewrite (out of scope per prompt; must not be staged).

### Verdict
**No Critical findings. No Important findings. No Minor findings worth changing.**

The redundant `--source-name` CLI flag in the documented commands (the CSV column is already populated) is intentional defensive redundancy and matches the existing `examples/community-signals.example.csv` convention; I would not change it.

Stage 77 is clear to commit, excluding the locally-dirty `uv.lock`.

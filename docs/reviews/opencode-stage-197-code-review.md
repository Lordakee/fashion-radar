# Stage 197 Code Review

Scope: optional public RSS source-pack expansion. Files reviewed against
`docs/reviews/opencode-stage-197-code-review-prompt.md`:

- `configs/source-packs/fashion-public.example.yaml`
- `docs/source-packs.md`
- `docs/source-pack-quality.md`
- `CHANGELOG.md`
- `tests/test_cli.py`
- `docs/superpowers/plans/2026-06-25-stage-197-public-rss-pack-expansion-plan.md`

## Verdict: APPROVED

No Critical or Important findings. The change is a conservative, deterministic
expansion of the optional public pack only. All blocking verification is
offline and passes. Live `source-liveness` remains advisory, as required.

## Question-by-Question

1. **Four intended RSS feeds only?** Yes. After `WWD` and before the first
   GDELT lane, exactly four new `rss` entries are added
   (`configs/source-packs/fashion-public.example.yaml:57-88`): Vogue, Business
   of Fashion, Red Carpet Fashion Awards, PurseBlog. Each has an explicit
   weight (`1.0`, `1.0`, `0.8`, `0.8`), non-empty lane tags, and
   `article.enabled: false`. No other RSS entries were added or removed.

2. **Default compact `configs/sources.example.yaml` unchanged?** Yes. The file
   is not in the working-tree diff; only the optional public pack, its docs,
   the changelog, and one test assertion are modified. No `src/` runtime file
   is touched.

3. **Docs and quality samples match current `source-pack-lint` output?** Yes.
   I ran both output modes against the current YAML. The table summary in
   `docs/source-pack-quality.md` and the JSON blocks in
   `docs/source-packs.md` and `docs/source-pack-quality.md` reconcile
   byte-for-byte with runtime: `source_count=20`, `enabled_count=20`,
   `disabled_count=0`, `type_counts={gdelt: 10, rss: 10}`, and the expanded
   `tag_counts` (including the intentional new `red_carpet`, `bags`, and
   `handbags` lanes). The parity is also enforced at runtime by
   `tests/test_source_packs_docs.py::test_source_packs_docs_example_json_matches_public_pack_lint_output`
   and the two guards in `tests/test_source_pack_quality_docs.py`, which
   compare the embedded samples to live `lint_source_pack` output rather than
   hard-coded counts. All passed.

4. **Public-pack CLI count assertion updated correctly?** Yes.
   `tests/test_cli.py:9715-9716` now asserts `source_count == 20` and
   `type_counts == {"gdelt": 10, "rss": 10}`. The focused test passes.

5. **Scope boundaries respected?** Yes. The change adds only existing `rss`
   source entries with article extraction disabled. There are no social or
   platform connectors, no scraping, no browser automation, no platform APIs,
   no login/cookie/proxy behavior, no access-control or paywall bypass, no
   source ranking logic, no demand proof, no platform coverage verification,
   and no compliance-review product feature. The boundary paragraph in
   `docs/source-packs.md` is preserved, and the CHANGELOG entry restates the
   exclusions.

6. **Tests and verification adequate?** Yes. Deterministic coverage is
   sufficient: the focused JSON CLI test, the docs/runtime parity guards, the
   source-pack boundary tests, and `--strict` lint (0 findings). Live
   `source-liveness` is correctly treated as advisory only and is not a
   release blocker.

## Critical Findings

None.

## Important Findings

None.

## Minor Findings (non-blocking)

- The YAML header comment now stacks two dated planning notes (Stage 7 and
  Stage 197). This reads correctly today; a future pack-expansion stage may
  want a single generic "verified at various planning dates" line to avoid
  further comment stacking. Not required for this stage.
- `Red Carpet Fashion Awards` and `PurseBlog` carry `weight: 0.8` while
  `Vogue` and `Business of Fashion` carry `weight: 1.0`, consistent with the
  conservative weighting convention already used by `FashionUnited`,
  `Highsnobiety`, and the GDELT lanes, and below `WWD` at `1.1`. No weight
  sanity concern.
- New singleton-ish tag lanes (`red_carpet`, `bags`, `handbags`) are
  explicitly called out as intentional free-form source-pack tags in the plan.
  They surface correctly in `tag_counts`. No action needed.

## Verification Observed

- `fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --strict`:
  `0 errors, 0 warnings, 0 info`.
- `fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --format json`:
  `source_count=20`, `enabled_count=20`, `disabled_count=0`,
  `type_counts={gdelt: 10, rss: 10}`, `findings=[]`, tag counts match docs.
- `pytest tests/test_cli.py::test_source_pack_lint_prints_json_for_public_pack`:
  1 passed.
- `pytest tests/test_source_packs.py tests/test_source_packs_docs.py tests/test_source_pack_quality_docs.py tests/test_source_boundaries_docs.py tests/test_config.py`:
  47 passed.
- `pytest tests/test_cli.py -k "source_pack_lint or source_liveness"`:
  17 passed.
- `pytest tests/test_source_liveness.py`: 20 passed.
- `ruff check tests/test_cli.py`: all checks passed.
- `ruff format --check tests/test_cli.py`: already formatted.
- `git diff --stat HEAD -- src/`: empty (no runtime change).
- `configs/sources.example.yaml`: absent from working-tree diff (default
  starter config untouched).

## Verification Recommended (release gate)

Per plan Task 4 Step 4, before tagging: full `pytest tests/ -q`,
`pytest tests/test_release_hygiene.py`, `ruff check`/`ruff format --check` on
the full tree, `UV_NO_CONFIG=1 uv lock --check`, `git diff --exit-code -- uv.lock pyproject.toml`,
the mirror-URL grep over `uv.lock`, and `git diff --check`.

## Concrete Fixes Required Before Release

None. The stage is ready to proceed to release review.

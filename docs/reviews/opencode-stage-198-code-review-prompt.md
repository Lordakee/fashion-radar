# Stage 198 Code Review Prompt

Review the Stage 198 implementation diff.

Changed files:

- `configs/entity-packs/fashion-watchlist.example.yaml`
- `examples/community-signals.watchlist.example.csv`
- `tests/test_entity_packs.py`
- `tests/test_watchlist_sample_workflow.py`
- `tests/test_community_signal_import_contract.py`
- `tests/test_community_signal_lint.py`
- `docs/entity-packs.md`
- `docs/entity-pack-quality.md`
- `CHANGELOG.md`
- `docs/superpowers/plans/2026-06-25-stage-198-deterministic-entity-watchlist-coverage-plan.md`
- Stage 198 review artifacts under `docs/reviews/`

Implementation summary:

- Adds optional watchlist brands `Savette` and `Aeyde`.
- Adds optional parent-brand-gated products `Savette Symmetry Bag` and
  `Aeyde Uma Mary Jane`.
- Adds two synthetic local community-signal sample rows using `example.com`.
- Updates deterministic tests for pack size/type mix, parent brand references,
  bare shorthand non-registration, positive product matching, sample row count,
  report/trends workflow, and community-signal lint/import contracts.
- Regenerates `docs/entity-pack-quality.md` count samples from
  `entity-pack-lint`.
- Keeps compact starter entity config and packaged template unchanged.

Boundary requirements:

- No source pack or default source config changes.
- No collectors, connectors, scraping, crawling, browser automation, platform
  APIs, login/cookie/session/token handling, proxy behavior, monitoring, or
  scheduling.
- No current-hotness detector, hot-list, brand ranking, source ranking, demand
  proof, market-wide proof, or platform coverage verification.
- No compliance-review, audit, legal-review, policy-review, or authorization
  product feature.
- No dependency or lockfile changes.

Verification already run:

```bash
uv --no-config run --frozen pytest \
  tests/test_entity_packs.py \
  tests/test_watchlist_sample_workflow.py \
  tests/test_community_signal_import_contract.py::test_watchlist_community_signal_csv_example_loads_expected_rows \
  tests/test_community_signal_lint.py::test_watchlist_community_signal_example_lints_cleanly \
  -q
```

Result: `15 passed`.

```bash
uv --no-config run --frozen pytest \
  tests/test_entity_packs.py \
  tests/test_entity_pack_lint.py \
  tests/test_entity_pack_quality_docs.py \
  tests/test_watchlist_sample_workflow.py \
  tests/test_community_signal_import_contract.py \
  tests/test_community_signal_lint.py \
  tests/test_entity_packs_docs.py \
  tests/test_cli_docs.py::test_readme_documents_optional_watchlist_local_sample \
  tests/test_cli_docs.py::test_first_run_guide_documents_optional_watchlist_local_sample \
  tests/test_cli_docs.py::test_entity_pack_docs_link_optional_watchlist_sample_to_local_pack \
  tests/test_cli_docs.py::test_entity_pack_docs_describe_optional_matching_layer_sequence \
  tests/test_cli_docs.py::test_github_upload_checklist_mentions_watchlist_sample_archive_guard \
  -q
```

Result: `158 passed`.

```bash
uv --no-config run --frozen fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml --format json
uv --no-config run --frozen fashion-radar community-signal-lint examples/community-signals.watchlist.example.csv --input-format csv --source-name "Community Watchlist Sample" --format json
UV_NO_CONFIG=1 uv lock --check
git diff --exit-code -- uv.lock pyproject.toml
rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock
```

Results:

- entity-pack lint: `entity_count=32`; first finding is existing
  `context_terms_no_effect` for `Boat Shoes`; zero errors.
- community-signal lint: `row_count=13`, `valid_row_count=13`, no findings.
- lockfile check: resolved 84 packages; `uv.lock` and `pyproject.toml` have no
  diff.
- mirror scan: no matches.

Review questions:

1. Are the new entity aliases and context terms technically safe under current
   matcher semantics?
2. Do the tests cover the intended deterministic behavior without creating
   brittle or impossible assertions?
3. Are docs and changelog synchronized with runtime lint output?
4. Does the implementation preserve all scope boundaries listed above?
5. Are there Critical or Important issues that must be fixed before release
   review?

Return:

- Verdict: APPROVED / NEEDS_WORK
- Critical findings
- Important findings
- Minor findings
- Concrete fixes required before release review

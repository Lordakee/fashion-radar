# Stage 77 Code Review Prompt

You are reviewing Stage 77 of `fashion-radar`.

Use this repository state as authoritative:

- Repository: `/home/ubuntu/fashion-radar`
- Base branch: `main`
- Current change: optional expanded local watchlist sample
- Review tool requested by the user for this node:
  `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`

## Goal

Review the current uncommitted Stage 77 worktree changes before commit. The
stage adds a static optional local CSV sample,
`examples/community-signals.watchlist.example.csv`, that demonstrates the
existing `configs/entity-packs/fashion-watchlist.example.yaml` pack through the
existing local `community-signal-lint`, `import-signals`, `match`, `report`, and
`trends` commands.

## In Scope

- `examples/community-signals.watchlist.example.csv`
- `tests/test_watchlist_sample_workflow.py`
- `tests/test_community_signal_lint.py`
- `tests/test_community_signal_import_contract.py`
- `tests/test_entity_packs.py`
- `scripts/check_package_archives.py`
- `tests/test_package_archives.py`
- `README.md`
- `docs/first-run.md`
- `docs/entity-packs.md`
- `docs/github-upload-checklist.md`
- `tests/test_cli_docs.py`
- `CHANGELOG.md`
- Stage-local review artifacts under `docs/reviews/`
- Stage plan/spec artifacts under `docs/superpowers/`

## Out Of Scope

- `uv.lock` is locally dirty from a pre-existing mirror URL rewrite and must not
  be staged as part of Stage 77.
- Do not require changes to runtime collectors, adapters, source acquisition,
  scraping, browser automation, platform APIs, login/session/cookie/token/proxy
  behavior, media download, monitoring, scheduling, demand proof, ranking, or
  coverage verification.
- Do not require a compliance-review product feature; the user explicitly said
  this tool does not need compliance-review functionality.

## Acceptance Criteria

- The optional watchlist sample is local-only, synthetic, and uses only the
  allowed community-signal fields.
- The sample has eight import-ready rows with `source_name` set to
  `Community Watchlist Sample` and `platform` set to `community`.
- The sample remains outside the canonical producer profile `example_paths` and
  does not change default first-run smoke behavior.
- Tests prove the sample lints, loads, dry-runs without artifacts, matches
  expected watchlist entities and types, and runs through the existing local
  import/match/report/trends workflow.
- Package archive checks require the sample in source distributions.
- Public docs present the sample as optional/local and do not claim live
  platform collection, demand proof, ranking, or connector support.
- `src/`, dependency manifests, and public `uv.lock` are not changed by this
  stage.

## Prior Verification

The controller already ran these commands successfully after integration:

```bash
uv --no-config run --frozen pytest tests/test_community_signal_lint.py::test_watchlist_community_signal_example_lints_cleanly tests/test_community_signal_import_contract.py::test_watchlist_community_signal_csv_example_uses_allowed_fields tests/test_community_signal_import_contract.py::test_watchlist_community_signal_csv_example_loads_expected_rows tests/test_community_signal_import_contract.py::test_import_signals_dry_run_validates_watchlist_sample_without_artifacts tests/test_entity_packs.py::test_fashion_watchlist_sample_matches_expected_entities_and_types tests/test_watchlist_sample_workflow.py::test_optional_watchlist_sample_runs_local_import_match_report_and_trends tests/test_package_archives.py::test_accepts_archives_with_required_files_and_metadata tests/test_package_archives.py::test_rejects_sdist_without_watchlist_community_signal_sample tests/test_cli_docs.py::test_readme_documents_optional_watchlist_local_sample tests/test_cli_docs.py::test_first_run_guide_documents_optional_watchlist_local_sample tests/test_cli_docs.py::test_entity_pack_docs_link_optional_watchlist_sample_to_local_pack tests/test_cli_docs.py::test_github_upload_checklist_mentions_watchlist_sample_archive_guard -q
uv --no-config run --frozen pytest tests/test_community_signal_lint.py tests/test_community_signal_import_contract.py tests/test_entity_packs.py tests/test_watchlist_sample_workflow.py tests/test_package_archives.py tests/test_cli_docs.py -q
uv --no-config run --frozen ruff check tests/test_community_signal_lint.py tests/test_community_signal_import_contract.py tests/test_entity_packs.py tests/test_watchlist_sample_workflow.py tests/test_package_archives.py tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_community_signal_lint.py tests/test_community_signal_import_contract.py tests/test_entity_packs.py tests/test_watchlist_sample_workflow.py tests/test_package_archives.py tests/test_cli_docs.py
git diff --check
```

Independent read-only subagents also reported no findings for:

- sample/entity-pack consistency;
- documentation drift and optional-local boundaries;
- package archive guard behavior.

## Review Request

Please inspect the current worktree and report only actionable issues.

Classify findings as:

- Critical: must fix before commit.
- Important: should fix before commit.
- Minor: optional polish.

For every finding, include file and line references and explain the concrete
failure mode. If there are no Critical or Important findings, say so clearly.

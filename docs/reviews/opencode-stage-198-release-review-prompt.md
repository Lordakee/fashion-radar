# Stage 198 Release Review Prompt

Review the current `/home/ubuntu/fashion-radar` worktree for Stage 198 before commit/push.

## Stage Goal

Improve optional deterministic entity watchlist coverage for emerging designer labels and named fashion products:

- Brands: `Savette`, `Aeyde`
- Products: `Savette Symmetry Bag`, `Aeyde Uma Mary Jane`

The stage must stay limited to optional deterministic matching quality. It must not add source collection, source packs, social/Xiaohongshu/Instagram/TikTok/X connectors, scraping/crawling/browser automation, login/cookie/session/proxy behavior, ranking/hotness/demand-proof/platform-coverage features, or compliance-review/audit/legal-review product features.

## Expected Changed Files

- `CHANGELOG.md`
- `configs/entity-packs/fashion-watchlist.example.yaml`
- `docs/entity-pack-quality.md`
- `docs/entity-packs.md`
- `docs/reviews/opencode-stage-198-plan-review-prompt.md`
- `docs/reviews/opencode-stage-198-plan-review.md`
- `docs/reviews/opencode-stage-198-code-review-prompt.md`
- `docs/reviews/opencode-stage-198-code-review.md`
- `docs/reviews/opencode-stage-198-release-review-prompt.md`
- `docs/reviews/opencode-stage-198-release-review.md`
- `docs/superpowers/plans/2026-06-25-stage-198-deterministic-entity-watchlist-coverage-plan.md`
- `examples/community-signals.watchlist.example.csv`
- `tests/test_community_signal_import_contract.py`
- `tests/test_community_signal_lint.py`
- `tests/test_entity_packs.py`
- `tests/test_review_protocol_docs.py`
- `tests/test_watchlist_sample_workflow.py`

Note: `tests/test_review_protocol_docs.py` was not part of the initial entity-watchlist scope. It was reformatted only because the full release gate `ruff format --check .` failed on pre-existing formatting drift. The diff is mechanical formatting only and has now been recorded in the Stage 198 plan and expected file list. Please decide whether this is acceptable for the release commit or should be removed before push.

## Implementation Summary

- Added `Savette` and `Aeyde` as distinctive `safe_single_word` brand aliases in the optional broader watchlist pack.
- Added parent-brand-gated products `Savette Symmetry Bag` and `Aeyde Uma Mary Jane`.
- Avoided bare product aliases like `Symmetry` or `Uma`.
- Avoided self-gating context terms by not using `bag` for `Savette Symmetry Bag` and not using `mary jane` for `Aeyde Uma Mary Jane`.
- Added two synthetic `example.com` rows to the optional watchlist community signal sample.
- Updated tests, docs, and changelog counts.
- Kept compact starter configs unchanged:
  - `configs/entities.example.yaml`
  - `src/fashion_radar/templates/configs/entities.example.yaml`

## Verification Already Run

- `git diff --check`: passed.
- `UV_NO_CONFIG=1 uv lock --check`: passed, resolved 84 packages.
- `git diff --exit-code -- uv.lock pyproject.toml`: passed.
- `rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock`: no matches.
- `UV_NO_CONFIG=1 uv sync --locked --dev`: passed.
- `UV_NO_CONFIG=1 uv sync --locked --dev --check`: passed.
- `uv --no-config run --frozen ruff check .`: passed.
- `uv --no-config run --frozen ruff format --check .`: initially failed on `tests/test_review_protocol_docs.py`; after mechanical `ruff format tests/test_review_protocol_docs.py`, passed with `148 files already formatted`.
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`: passed.
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`: passed.
- Temporary package build with `uv --no-config build --out-dir "$tmp_build"`: passed.
- `uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"`: passed.
- Installed-wheel smoke, including installed first-run smoke and all documented CLI `--help` commands: passed.
- `uv --no-config run --frozen pytest tests/ -q --tb=short`: `1471 passed`.

## Review Questions

1. Are there any Critical or Important issues that should block commit/push?
2. Does the final changed-file scope remain acceptable after explicitly including the mechanical `tests/test_review_protocol_docs.py` formatting fix?
3. Are the new entities, aliases, parent-brand gates, and context terms safe under the deterministic matcher semantics?
4. Are tests/docs/changelog synchronized with current row counts and entity-pack lint counts?
5. Are review artifacts sufficiently complete and clean for release?
6. Are lockfile, mirror, package archive, installed-wheel, and secret/local-artifact boundaries satisfied?
7. Did this stage accidentally add any prohibited source/social/connector/ranking/hotness/compliance-review product behavior?

Start the response exactly with:

```markdown
# Stage 198 Release Review
```

Then provide:

- Verdict
- Critical findings
- Important findings
- Minor findings
- Verification notes
- Release decision

Do not include tool-status chatter, live command transcripts, duplicated drafts, or process narration. If no Critical or Important findings remain, say release is approved.

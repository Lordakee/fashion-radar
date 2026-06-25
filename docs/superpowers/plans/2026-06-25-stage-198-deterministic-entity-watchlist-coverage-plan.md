# Stage 198 Deterministic Entity Watchlist Coverage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve optional deterministic fashion entity matching coverage for emerging designer brands, named bags, and named shoes without adding sources, connectors, scraping, ranking, or compliance-review product features.

**Architecture:** Keep Fashion Radar's compact starter entity config unchanged and update only the optional `fashion-watchlist` pack plus its synthetic local sample. Add two emerging designer brands and two parent-brand-gated products so matching remains precise under the existing deterministic matcher. Regenerate docs and tests from local lint/import/match/report output, preserving the entity-pack boundary as an optional local matching layer.

**Tech Stack:** YAML entity-pack config, checked-in synthetic CSV community-signal sample, existing deterministic entity matcher, entity-pack/community-signal lint CLIs, pytest docs/workflow guards, ruff, uv, local OpenCode review with `zhipuai-coding-plan/glm-5.2 --variant max`, no new dependencies.

---

## Scope Boundary

This stage closes the "deterministic matching quality" core product gap called
out by the full-project reviews. It does not change collection, scoring,
reporting contracts, source packs, default starter configs, external-tool
handoff surfaces, community-handoff commands, or imported-review commands.

Do not add:

- new source packs or default source config changes
- collectors, source types, browser automation, scraping, crawling, monitoring,
  scheduling, platform APIs, login/cookie/token/session handling, or proxy
  behavior
- social/Xiaohongshu/Instagram/TikTok/X connectors
- current-hotness detection, hot-lists, brand ranking, source ranking, demand
  proof, market-wide proof, or platform coverage verification
- compliance-review, audit, legal-review, policy-review, or authorization
  product features

Keep all new sample rows synthetic and local. Use `example.com` URLs only.

## Files And Responsibilities

- Modify `configs/entity-packs/fashion-watchlist.example.yaml`: add
  `Savette`, `Aeyde`, `Savette Symmetry Bag`, and `Aeyde Uma Mary Jane` to the
  optional broader watchlist only.
- Modify `examples/community-signals.watchlist.example.csv`: add two synthetic
  local sample rows that exercise the new bag and shoe product coverage.
- Modify `tests/test_entity_packs.py`: pin the new entities, type mix, matched
  sample names, and bare short-name non-alias coverage.
- Modify `tests/test_watchlist_sample_workflow.py`: update expected matched
  entities and row-count assertions for the optional local workflow.
- Modify `tests/test_community_signal_import_contract.py`: update watchlist row
  count and last-row assertion.
- Modify `tests/test_community_signal_lint.py`: update watchlist row count.
- Modify `tests/test_review_protocol_docs.py`: release-gate mechanical
  `ruff format` repair only; no assertion or behavior changes.
- Modify `docs/entity-packs.md`: describe the optional pack as covering
  emerging designer labels and named bag/shoe examples while preserving local
  matching boundaries.
- Modify `docs/entity-pack-quality.md`: regenerate table and JSON count
  examples from `entity-pack-lint`.
- Modify `CHANGELOG.md`: add a Stage 198 entry under `[Unreleased]`.
- Create `docs/reviews/opencode-stage-198-plan-review-prompt.md`,
  `docs/reviews/opencode-stage-198-plan-review.md`,
  `docs/reviews/opencode-stage-198-code-review-prompt.md`,
  `docs/reviews/opencode-stage-198-code-review.md`,
  `docs/reviews/opencode-stage-198-release-review-prompt.md`, and
  `docs/reviews/opencode-stage-198-release-review.md`.

Do not modify:

- `configs/entities.example.yaml`
- `src/fashion_radar/templates/configs/entities.example.yaml`
- `configs/sources.example.yaml`
- `configs/source-packs/*.yaml`
- collector/source/adapter/community/imported command modules unless a
  release-blocking defect appears during verification

## Entity Additions

Add these entities after `Sandy Liang` in the brand section and after
`Tory Burch Pierced Mule` in the product section.

Brand entries:

```yaml
  - name: Savette
    type: brand
    aliases:
      - value: Savette
        safe_single_word: true
        reason: Distinct fashion brand name.
    tags: [designer_brand, bags, emerging_label]
    active_from: "2024-01-01T00:00:00Z"
  - name: Aeyde
    type: brand
    aliases:
      - value: Aeyde
        safe_single_word: true
        reason: Distinct fashion brand name.
    tags: [designer_brand, footwear, emerging_label]
    active_from: "2024-01-01T00:00:00Z"
```

Product entries:

```yaml
  - name: Savette Symmetry Bag
    type: product
    parent_brand: Savette
    aliases:
      - value: Savette Symmetry
      - value: Symmetry Bag
    context_terms: [savette, handbag, top handle]
    category_tags: [bag, handbag, top_handle]
    active_from: "2024-01-01T00:00:00Z"
  - name: Aeyde Uma Mary Jane
    type: product
    parent_brand: Aeyde
    aliases:
      - value: Aeyde Uma
      - value: Uma Mary Jane
    context_terms: [aeyde, shoe, footwear]
    category_tags: [shoe, flats, mary_jane]
    active_from: "2024-01-01T00:00:00Z"
```

Precision rules:

- Do not add bare product aliases `Symmetry`, `Uma`, `Marfa`, `Teckel`, or
  `Puzzle`.
- Do not add new broad category/trend phrases in this stage.
- Use `parent_brand` and product-specific `context_terms` for named products.
- Do not include tokens from the short product aliases as their own
  `context_terms`; the matcher accepts a parent-branded product when any
  context term appears anywhere in the text.
- Use `safe_single_word` only for distinctive brand names with an explicit
  reason.

## Task 0: Create Plan Review Artifacts

**Files:**
- Create: `docs/reviews/opencode-stage-198-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-198-plan-review.md`

- [ ] **Step 1: Write the plan review prompt**

Create `docs/reviews/opencode-stage-198-plan-review-prompt.md` with a concise
request for local OpenCode to review:

- the Stage 198 objective, architecture, tech stack, implementation method, and
  staged plan
- optional local watchlist boundaries
- new entity/product precision rules
- docs/test coverage
- dependency/lockfile/mirror and review-artifact hygiene

- [ ] **Step 2: Run local OpenCode plan review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-198-plan-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-198-plan-review.md
rm -f "$tmp_review"
```

Expected: a completed review record with no Critical or Important blockers.
Fix Critical/Important planning findings and run a plan rereview before Task 1.

## Task 1: Add Failing Watchlist Coverage Tests

**Files:**
- Modify: `tests/test_entity_packs.py`
- Modify: `tests/test_watchlist_sample_workflow.py`
- Modify: `tests/test_community_signal_import_contract.py`
- Modify: `tests/test_community_signal_lint.py`

- [ ] **Step 1: Pin the new optional watchlist entities**

In `tests/test_entity_packs.py`, update
`test_fashion_watchlist_entity_pack_loads()`:

```python
assert len(config.entities) >= 32
```

Update `test_fashion_watchlist_entity_pack_has_expected_type_mix()`:

```python
assert type_counts[EntityType.BRAND] >= 12
assert type_counts[EntityType.PRODUCT] >= 8
```

Keep category, designer, celebrity, and trend thresholds unchanged.

Update `test_fashion_watchlist_entity_pack_includes_requested_watchlist_examples()`
so the expected name list also includes:

```python
"Savette",
"Aeyde",
"Savette Symmetry Bag",
"Aeyde Uma Mary Jane",
```

- [ ] **Step 2: Add bare short-name non-alias coverage**

Add a new test after
`test_fashion_watchlist_matcher_rejects_generic_broad_alias_mentions()`:

```python
def test_fashion_watchlist_matcher_does_not_register_bare_new_product_shorthands() -> None:
    entities = _entities()

    for text, entity_name in [
        ("The symmetry of the geometry was noted.", "Savette Symmetry Bag"),
        ("Uma joined the dinner list.", "Aeyde Uma Mary Jane"),
    ]:
        decisions = [
            decision
            for decision in evaluate_entity_matches(text, entities)
            if decision.entity_name == entity_name
        ]
        assert decisions == []
```

Expected before YAML implementation: the test passes vacuously because the new
entities do not exist. After implementation, it proves the risky bare product
shorthands `Symmetry` and `Uma` were not registered as aliases.

- [ ] **Step 3: Update accepted-context coverage**

In `test_fashion_watchlist_matcher_accepts_parent_brand_or_fashion_context()`,
extend the sample text with:

```text
Savette Symmetry Bag, Aeyde Uma Mary Jane shoe
```

Add these names to the expected accepted set:

```python
"Savette Symmetry Bag",
"Aeyde Uma Mary Jane",
```

- [ ] **Step 4: Update sample matched names**

In `test_fashion_watchlist_sample_matches_expected_entities_and_types()`, add:

```python
"Savette",
"Savette Symmetry Bag",
"Aeyde",
"Aeyde Uma Mary Jane",
```

- [ ] **Step 5: Update optional workflow expected entities and row counts**

In `tests/test_watchlist_sample_workflow.py`, add the same four names to
`EXPECTED_REPORT_ENTITIES`.

Update all local sample row-count assertions from `11` to `13`:

```python
assert lint_payload["valid_row_count"] == 13
assert "Validated 13 manual signal rows" in dry_run_output
assert "Imported 13 manual signal rows" in import_output
assert "Processed 13 items" in match_output
```

- [ ] **Step 6: Update community signal contract row counts**

In `tests/test_community_signal_import_contract.py`, update:

```python
WATCHLIST_EXPECTED_ROWS = 13
```

Update the direct row assertion:

```python
assert len(rows) == WATCHLIST_EXPECTED_ROWS
```

Update the last-row assertion so it matches the final new sample row:

```python
assert rows[-1].title == "Aeyde Uma Mary Jane footwear watchlist note"
```

In `tests/test_community_signal_lint.py`, update:

```python
WATCHLIST_EXPECTED_ROWS = 13
```

- [ ] **Step 7: Run focused tests to verify the expected failure**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_entity_packs.py \
  tests/test_watchlist_sample_workflow.py \
  tests/test_community_signal_import_contract.py::test_watchlist_community_signal_csv_example_loads_expected_rows \
  tests/test_community_signal_lint.py::test_watchlist_community_signal_example_lints_cleanly \
  -q
```

Expected before implementation: failures showing the new entities and two new
sample rows are missing.

## Task 2: Add Optional Watchlist Entities And Sample Rows

**Files:**
- Modify: `configs/entity-packs/fashion-watchlist.example.yaml`
- Modify: `examples/community-signals.watchlist.example.csv`

- [ ] **Step 1: Add the two brand entities**

Insert the `Savette` and `Aeyde` brand entries after `Sandy Liang` in
`configs/entity-packs/fashion-watchlist.example.yaml`.

- [ ] **Step 2: Add the two product entities**

Insert the `Savette Symmetry Bag` and `Aeyde Uma Mary Jane` product entries
after `Tory Burch Pierced Mule`.

- [ ] **Step 3: Append two synthetic local sample rows**

Append these rows to `examples/community-signals.watchlist.example.csv`:

```csv
https://example.com/community-watchlist/savette-symmetry-bag,Savette Symmetry Bag local watchlist note,2026-06-12T15:15:00Z,Sanitized local note about Savette Symmetry Bag and Savette top handle handbag styling,Community Watchlist Sample,community,1.1,2026-06-12T15:35:00Z
https://example.com/community-watchlist/aeyde-uma-mary-jane,Aeyde Uma Mary Jane footwear watchlist note,2026-06-12T15:30:00Z,Sanitized local note about Aeyde Uma Mary Jane shoe and Aeyde footwear styling,Community Watchlist Sample,community,1.1,2026-06-12T15:50:00Z
```

- [ ] **Step 4: Run focused tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_entity_packs.py \
  tests/test_watchlist_sample_workflow.py \
  tests/test_community_signal_import_contract.py::test_watchlist_community_signal_csv_example_loads_expected_rows \
  tests/test_community_signal_lint.py::test_watchlist_community_signal_example_lints_cleanly \
  -q
```

Expected after implementation: pass.

## Task 3: Regenerate Entity-Pack Quality Docs

**Files:**
- Modify: `docs/entity-packs.md`
- Modify: `docs/entity-pack-quality.md`
- Modify: `CHANGELOG.md`
- Test: `tests/test_entity_pack_quality_docs.py`
- Test: `tests/test_cli_docs.py`

- [ ] **Step 1: Refresh entity-pack prose**

In `docs/entity-packs.md`, update the introductory pack description to include
emerging designer labels:

```markdown
It is a seed watchlist for designer brands, emerging designer labels, named
bags and shoes, product categories, designers, celebrity style signals, and
style terms.
```

In `## Try The Optional Local Sample`, update the first sentence:

```markdown
Use the optional local sample when you want to exercise the broader
`fashion-watchlist` pack against checked-in synthetic community-signal rows,
including named bag and shoe examples for emerging designer labels.
```

- [ ] **Step 2: Regenerate table and JSON samples**

Run:

```bash
uv --no-config run --frozen fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml
uv --no-config run --frozen fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml --format json
```

Replace the summary block in `docs/entity-pack-quality.md` with the first five
lines of table output.

Replace scalar counts, `type_counts`, `tag_counts`, `category_tag_counts`, and
matcher-gate counts in the JSON excerpt so they match current lint output.
Keep `findings` abbreviated to exactly the first warning finding from the lint
JSON output.

- [ ] **Step 3: Add changelog entry**

Under `[Unreleased]` / `### Added`, add:

```markdown
- Stage 198 expands the optional local fashion watchlist pack with two
  emerging designer labels and two parent-brand-gated named product entries
  for bag and shoe coverage, plus synthetic local sample rows and deterministic
  matcher/docs guards. It does not change default starter configs, add
  sources, scrape, add social/platform connectors, prove demand, rank brands,
  verify platform coverage, or add compliance-review product features.
```

- [ ] **Step 4: Run docs-focused tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_entity_pack_quality_docs.py \
  tests/test_cli_docs.py::test_entity_pack_docs_link_optional_watchlist_sample_to_local_pack \
  tests/test_cli_docs.py::test_entity_pack_docs_describe_optional_matching_layer_sequence \
  tests/test_entity_packs_docs.py \
  -q
```

Expected: pass.

## Task 4: Deterministic Workflow Verification And Review

**Files:**
- Create: `docs/reviews/opencode-stage-198-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-198-code-review.md`
- Create: `docs/reviews/opencode-stage-198-release-review-prompt.md`
- Create: `docs/reviews/opencode-stage-198-release-review.md`

- [ ] **Step 1: Run deterministic lints**

Run:

```bash
uv --no-config run --frozen fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml --format json
uv --no-config run --frozen fashion-radar community-signal-lint examples/community-signals.watchlist.example.csv --input-format csv --source-name "Community Watchlist Sample" --format json
```

Expected: entity-pack lint has zero errors; community-signal lint reports
`valid_row_count` `13` and no findings.

`entity-pack-lint --strict` may still fail on pre-existing advisory warnings
for broad multi-word category aliases. Treat strict warning output as advisory
unless this stage introduces new warnings for the new entities. The blocking
gate is zero errors plus tests that pin the intentional boundaries.

- [ ] **Step 2: Run the optional local watchlist workflow**

Run:

```bash
tmp_watchlist="$(mktemp -d)"
AS_OF="2026-06-13T12:00:00Z"
mkdir -p "$tmp_watchlist/configs" "$tmp_watchlist/data" "$tmp_watchlist/reports"
cp configs/entity-packs/fashion-watchlist.example.yaml "$tmp_watchlist/configs/entities.yaml"
cp configs/scoring.example.yaml "$tmp_watchlist/configs/scoring.yaml"

uv --no-config run --frozen fashion-radar community-signal-lint examples/community-signals.watchlist.example.csv --input-format csv --source-name "Community Watchlist Sample"
uv --no-config run --frozen fashion-radar import-signals examples/community-signals.watchlist.example.csv --format csv --source-name "Community Watchlist Sample" --imported-at "$AS_OF" --data-dir "$tmp_watchlist/data"
uv --no-config run --frozen fashion-radar match --config-dir "$tmp_watchlist/configs" --data-dir "$tmp_watchlist/data"
uv --no-config run --frozen fashion-radar report --config-dir "$tmp_watchlist/configs" --data-dir "$tmp_watchlist/data" --reports-dir "$tmp_watchlist/reports" --as-of "$AS_OF"
uv --no-config run --frozen fashion-radar trends --config-dir "$tmp_watchlist/configs" --data-dir "$tmp_watchlist/data" --as-of "$AS_OF" --limit 50 --format json
```

Expected: import reports `13` rows, match reports `13` items, report/trends
complete using only the temp local workspace. The explicit trend limit keeps
the optional sample's full entity set visible instead of relying on the CLI's
default display limit.

- [ ] **Step 3: Run focused pytest coverage**

Run:

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

Expected: pass.

- [ ] **Step 4: Create and run local OpenCode code review**

Create `docs/reviews/opencode-stage-198-code-review-prompt.md` with a concise
review request covering:

- changed files
- optional local watchlist boundary
- new entity/product precision rules
- sample row count and workflow tests
- docs count regeneration
- no sources, connectors, scraping, ranking, platform coverage verification, or
  compliance-review features

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-198-code-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-198-code-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important blockers. Fix any Critical/Important
findings and run a `code-rereview` before release review.

## Task 5: Release Verification, Release Review, Commit, And Push

**Files:**
- Create: `docs/reviews/opencode-stage-198-release-review-prompt.md`
- Create: `docs/reviews/opencode-stage-198-release-review.md`
- Modify: any file needed to fix Critical or Important release findings

- [ ] **Step 1: Run release verification**

Run:

```bash
git status --short --untracked-files=all
git diff --check
UV_NO_CONFIG=1 uv lock --check
git diff --exit-code -- uv.lock pyproject.toml
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then exit 1; fi
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
tmp_build="$(mktemp -d)"
uv --no-config build --out-dir "$tmp_build"
uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"
uv --no-config run --frozen pytest tests/ -q --tb=short
```

Expected: all commands pass. If full pytest discovers an unrelated failure,
debug it before commit. If the full-repo `ruff format --check .` gate exposes
pre-existing formatting drift, apply the formatter's mechanical output and
record the extra file explicitly in the release review.

- [ ] **Step 2: Run secret/local-artifact scans**

Run:

```bash
rg -n "ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+" --glob '!uv.lock' --glob '!dist/**' --glob '!build/**' . || true
git status --short --untracked-files=all
```

Expected: no secret hits and no untracked local artifacts that should be
committed accidentally.

- [ ] **Step 3: Create and run local OpenCode release review**

Create `docs/reviews/opencode-stage-198-release-review-prompt.md` covering:

- final diff and changed-file scope
- verification command results
- review artifact hygiene
- lockfile/mirror/secret checks
- packaging/resource checks
- no prohibited source/social/connector/ranking/compliance feature expansion

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-198-release-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-198-release-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important blockers. Fix any Critical/Important
findings and run a `release-rereview` before commit.

- [ ] **Step 4: Check review artifact hygiene**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
rg -n "I'll|Let me|Now let me|->|build \\xC2\\xB7|\\x1b|\\$ |Wrote|errored" docs/reviews/*stage-198*.md || true
```

Expected: release hygiene passes. The `rg` command should not show process
chatter in committed review records. Inspect any match before staging.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short --untracked-files=all
git add \
  CHANGELOG.md \
  configs/entity-packs/fashion-watchlist.example.yaml \
  docs/entity-pack-quality.md \
  docs/entity-packs.md \
  docs/reviews/opencode-stage-198-plan-review-prompt.md \
  docs/reviews/opencode-stage-198-plan-review.md \
  docs/reviews/opencode-stage-198-code-review-prompt.md \
  docs/reviews/opencode-stage-198-code-review.md \
  docs/reviews/opencode-stage-198-release-review-prompt.md \
  docs/reviews/opencode-stage-198-release-review.md \
  docs/superpowers/plans/2026-06-25-stage-198-deterministic-entity-watchlist-coverage-plan.md \
  examples/community-signals.watchlist.example.csv \
  tests/test_community_signal_import_contract.py \
  tests/test_community_signal_lint.py \
  tests/test_entity_packs.py \
  tests/test_review_protocol_docs.py \
  tests/test_watchlist_sample_workflow.py
git commit -m "Stage 198: expand deterministic entity watchlist coverage"
git push origin main
```

Expected: push succeeds and `origin/main` points to the new commit.

## Handoff Summary Template

At node completion, report:

```markdown
Handoff Summary
- Repo status: branch, HEAD SHA, origin/main SHA, clean/dirty state.
- Verified commands: concise list with pass/fail status.
- Uncommitted files: exact `git status --short --untracked-files=all` result.
- Next step: the next recommended stage after Stage 198.
```

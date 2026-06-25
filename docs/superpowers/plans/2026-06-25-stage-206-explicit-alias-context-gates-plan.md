# Stage 206 Explicit Alias Context Gates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an explicit alias-level context gate for deterministic matching, then use it to reduce high-risk optional watchlist category false positives without changing source acquisition, scoring, reporting, social connectors, scraping, demand proof, or compliance-review behavior.

**Architecture:** Extend `AliasDefinition` with a backward-compatible `requires_context` boolean. The existing matcher already has a context-required branch; route explicit aliases through that branch before `safe_single_word` can bypass it. Apply the new field only in the optional `fashion-watchlist` entity pack for broad multi-word category aliases whose existing `context_terms` currently have no effect.

**Tech Stack:** Pydantic models, existing deterministic matcher, existing entity-pack linter, YAML entity pack config, pytest, Markdown docs, `uv --no-config run --frozen`, local OpenCode review with `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Scope

This stage closes a real `collect -> match -> report` quality gap: optional
watchlist category aliases such as `boat shoes`, `Mary Jane shoes`,
`east-west bag`, and `suede sneakers` can currently match without context even
though their entities define `context_terms`. The linter reports this as
`context_terms_no_effect` and `ungated_alias_with_context_terms`.

In scope:

- Add `requires_context: bool = False` to `AliasDefinition`.
- Make explicit `requires_context` aliases require at least one entity
  `context_terms` match for non-product aliases.
- Keep products with `parent_brand` on the existing parent-brand-or-context
  branch.
- Validate that explicit context aliases have entity-level `context_terms`.
- Teach `entity-pack-lint` to classify explicit gates as context-gated.
- Update only the optional `configs/entity-packs/fashion-watchlist.example.yaml`
  high-risk category aliases:
  - `Mary Jane Shoes`
  - `East-West Bags`
  - `Boat Shoes`
  - `Suede Sneakers`
- Tune those category `context_terms` so the alias text itself does not satisfy
  the gate where that would make the gate ineffective.
- Update matcher, config, linter, entity-pack, docs, and sample-workflow tests.
- Update docs and changelog.
- Add Stage 206 OpenCode plan/code/release review artifacts.

Out of scope:

- No changes to default starter entity config.
- No new brands, products, celebrities, categories, trends, or source packs.
- No scoring formula, candidate discovery, report generation, dashboard, DB
  schema, importer, collector, source-liveness, community-handoff, imported,
  external-tool, social/platform connector, scraping, browser automation,
  account/cookie/token/session, proxy, demand proof, platform coverage
  verification, ranking, hot-list, or compliance-review behavior changes.
- No dependency, `pyproject.toml`, or `uv.lock` changes.

## File Map

- Modify `src/fashion_radar/models/entity.py`
  - Add `requires_context: bool = False` to `AliasDefinition`.
- Modify `src/fashion_radar/extract/entities.py`
  - Route explicit alias context gates through the context branch.
- Modify `src/fashion_radar/settings.py`
  - Reject `requires_context: true` aliases when the entity has no
    `context_terms`.
- Modify `src/fashion_radar/entity_packs.py`
  - Classify explicit alias gates as context-gated.
- Modify `configs/entity-packs/fashion-watchlist.example.yaml`
  - Add `requires_context: true` to broad category aliases and tune category
    context terms.
- Modify `tests/test_matcher.py`
  - Add RED matcher tests for explicit multi-word context gates.
- Modify `tests/test_config.py`
  - Add config validation coverage for explicit context gates without
    `context_terms`.
- Modify `tests/test_entity_pack_lint.py`
  - Add linter coverage proving explicit multi-word context aliases are not
    reported as ungated and count as context-gated.
- Modify `tests/test_entity_packs.py`
  - Add watchlist negative and positive regression coverage.
- Modify `tests/test_watchlist_sample_workflow.py`
  - Keep the optional sample workflow green after the watchlist context tuning.
- Modify `docs/entity-packs.md`
  - Document `requires_context` as an optional precision knob.
- Modify `docs/entity-pack-quality.md`
  - Document the field and update linter sample counts/output.
- Modify `tests/test_entity_packs_docs.py`
  - Pin the new user-facing wording.
- Modify `tests/test_entity_pack_quality_docs.py`
  - Keep docs sample parity with current `entity-pack-lint` output.
- Modify `CHANGELOG.md`
  - Add Stage 206 entry under `### Added`.
- Add `docs/reviews/opencode-stage-206-plan-review-prompt.md`
- Add `docs/reviews/opencode-stage-206-plan-review.md`
- Later add Stage 206 code/release review prompts and bodies.

## Task 0: Plan Review

**Files:**

- Add: `docs/reviews/opencode-stage-206-plan-review-prompt.md`
- Add: `docs/reviews/opencode-stage-206-plan-review.md`

- [ ] **Step 1: Create the plan-review prompt**

Create `docs/reviews/opencode-stage-206-plan-review-prompt.md` asking
OpenCode to review this plan for correctness, scope control, matcher semantics,
TDD coverage, docs/lint sample updates, release hygiene, and roadmap fit.

- [ ] **Step 2: Run OpenCode plan review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-206-plan-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-206-plan-review.md
rm -f "$tmp_review"
```

Expected: completed review artifact with no Critical or Important blockers.
Fix Critical/Important planning findings and run a rereview before Task 1.

## Task 1: RED Tests For Explicit Alias Context Gates

**Files:**

- Modify: `tests/test_matcher.py`
- Modify: `tests/test_config.py`
- Modify: `tests/test_entity_pack_lint.py`

- [ ] **Step 1: Add matcher RED coverage**

Add to `tests/test_matcher.py`:

```python
def test_multi_word_alias_can_explicitly_require_context() -> None:
    entities = [
        _entity(
            "Boat Shoes",
            EntityType.CATEGORY,
            [{"value": "boat shoes", "requires_context": True}],
            context_terms=["footwear", "runway"],
            match_confidence=0.7,
        )
    ]

    rejected = evaluate_entity_matches("Boat shoes were required on the dock.", entities)
    assert len(rejected) == 1
    assert not rejected[0].accepted
    assert rejected[0].reason == "missing_context"

    accepted = match_entities("Boat shoes returned in runway footwear styling.", entities)
    assert len(accepted) == 1
    assert accepted[0].entity_name == "Boat Shoes"
    assert accepted[0].reason == "context"
    assert accepted[0].context_terms == ["footwear", "runway"]
    assert accepted[0].confidence == 0.7
```

- [ ] **Step 2: Add config validation RED coverage**

Add to `tests/test_config.py`:

```python
def test_alias_requires_context_needs_entity_context_terms(tmp_path: Path) -> None:
    path = tmp_path / "entities.yaml"
    path.write_text(
        """
version: 1
entities:
  - name: Boat Shoes
    type: category
    aliases:
      - value: boat shoes
        requires_context: true
    category_tags: [shoes]
""".strip()
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="requires context but entity has no context_terms"):
        load_entity_config(path)
```

- [ ] **Step 3: Add entity-pack linter RED coverage**

Add to `tests/test_entity_pack_lint.py`:

```python
def test_explicit_multi_word_context_alias_is_context_gated(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: Boat Shoes
            type: category
            aliases:
              - value: boat shoes
                requires_context: true
            context_terms: [footwear, runway]
            category_tags: [shoes]
            initial_weight: 1.0
            match_confidence: 1.0
        """,
    )

    result = lint_entity_pack(path)

    assert "ungated_alias_with_context_terms" not in finding_codes(result)
    assert "context_terms_no_effect" not in finding_codes(result)
    assert result.context_gated_aliases == 1
    assert result.accepted_without_context_aliases == 0


def test_explicit_context_alias_takes_precedence_over_safe_alias_lint(
    tmp_path: Path,
) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: Acme
            type: brand
            aliases:
              - value: Acme
                safe_single_word: true
                reason: Distinct local test brand.
                requires_context: true
            context_terms: [runway]
            tags: [brand]
            initial_weight: 1.0
            match_confidence: 1.0
        """,
    )

    result = lint_entity_pack(path)

    assert result.context_gated_aliases == 1
    assert result.safe_aliases == 0
    assert "safe_alias_bypasses_context" not in finding_codes(result)
```

- [ ] **Step 4: Run RED tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_matcher.py::test_multi_word_alias_can_explicitly_require_context \
  tests/test_config.py::test_alias_requires_context_needs_entity_context_terms \
  tests/test_entity_pack_lint.py::test_explicit_multi_word_context_alias_is_context_gated \
  tests/test_entity_pack_lint.py::test_explicit_context_alias_takes_precedence_over_safe_alias_lint \
  -q
```

Expected: fail before implementation because `AliasDefinition` rejects the
unknown `requires_context` field.

## Task 2: Implement Alias-Level Context Gates

**Files:**

- Modify: `src/fashion_radar/models/entity.py`
- Modify: `src/fashion_radar/extract/entities.py`
- Modify: `src/fashion_radar/settings.py`
- Modify: `src/fashion_radar/entity_packs.py`
- Test: `tests/test_matcher.py`
- Test: `tests/test_config.py`
- Test: `tests/test_entity_pack_lint.py`

- [ ] **Step 1: Add the model field**

In `AliasDefinition`, add:

```python
requires_context: bool = False
```

Do not change `coerce_aliases`; string aliases continue to become
`{"value": item}` and default to `requires_context=False`.

- [ ] **Step 2: Update matcher semantics**

In `src/fashion_radar/extract/entities.py`, change `_evaluate_alias(...)` so
explicit context gates run before the existing safe-alias branch:

```python
    if alias.requires_context:
        if context_terms:
            return True, REASON_CONTEXT
        return False, REASON_MISSING_CONTEXT
```

Place that block after the product parent-brand branch and before:

```python
    if not _requires_context(alias):
```

Then update `_requires_context(...)`:

```python
def _requires_context(alias: AliasDefinition) -> bool:
    key = normalize_alias_key(alias.value)
    return len(key.split()) == 1 or key in UNSAFE_COMMON_ALIASES
```

- [ ] **Step 3: Update config validation**

In `EntityConfig.validate_aliases()`, after computing `key`, add:

```python
                if alias.requires_context and not entity.context_terms:
                    raise ValueError(
                        f"Alias {alias.value!r} for entity {entity.name!r} "
                        "requires context but entity has no context_terms"
                    )
```

Keep the existing unsafe/common alias validation.

- [ ] **Step 4: Update linter gate classification**

In `src/fashion_radar/entity_packs.py`, change `_alias_requires_context(...)`:

```python
def _alias_requires_context(alias: AliasDefinition) -> bool:
    key = normalize_alias_key(alias.value)
    return alias.requires_context or len(key.split()) == 1 or key in UNSAFE_COMMON_ALIASES
```

In `_classify_alias_gate(...)`, check explicit alias context gates before
consulting `safe_single_word`:

```python
def _classify_alias_gate(entity: EntityDefinition, alias: AliasDefinition) -> AliasGateKind:
    if entity.type == EntityType.PRODUCT and entity.parent_brand:
        return AliasGateKind.PRODUCT_PARENT_OR_CONTEXT

    if alias.requires_context:
        return AliasGateKind.CONTEXT_REQUIRED

    if _alias_requires_context(alias):
        if alias.safe_single_word and alias.reason:
            return AliasGateKind.SAFE_ALIAS
        return AliasGateKind.CONTEXT_REQUIRED

    return AliasGateKind.ACCEPTED_WITHOUT_CONTEXT
```

No new finding code is required for this stage.

- [ ] **Step 5: Run GREEN tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_matcher.py::test_multi_word_alias_can_explicitly_require_context \
  tests/test_config.py::test_alias_requires_context_needs_entity_context_terms \
  tests/test_entity_pack_lint.py::test_explicit_multi_word_context_alias_is_context_gated \
  tests/test_entity_pack_lint.py::test_explicit_context_alias_takes_precedence_over_safe_alias_lint \
  -q
```

Expected: pass.

- [ ] **Step 6: Run focused implementation tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_matcher.py tests/test_config.py tests/test_entity_pack_lint.py -q
uv --no-config run --frozen ruff check src/fashion_radar/models/entity.py src/fashion_radar/extract/entities.py src/fashion_radar/settings.py src/fashion_radar/entity_packs.py tests/test_matcher.py tests/test_config.py tests/test_entity_pack_lint.py
uv --no-config run --frozen ruff format --check src/fashion_radar/models/entity.py src/fashion_radar/extract/entities.py src/fashion_radar/settings.py src/fashion_radar/entity_packs.py tests/test_matcher.py tests/test_config.py tests/test_entity_pack_lint.py
```

## Task 3: Apply Explicit Gates To Optional Watchlist Categories

**Files:**

- Modify: `configs/entity-packs/fashion-watchlist.example.yaml`
- Modify: `tests/test_entity_packs.py`
- Modify: `tests/test_watchlist_sample_workflow.py`

- [ ] **Step 1: Add RED watchlist matcher tests**

Add to `tests/test_entity_packs.py` near the watchlist matcher tests:

```python
def test_fashion_watchlist_context_gates_broad_category_aliases() -> None:
    entities = _entities()

    generic_texts = [
        ("Mary Janes joined the dinner list.", "Mary Jane Shoes"),
        ("Mary Jane shoes were noted.", "Mary Jane Shoes"),
        ("Mary Jane flats were noted.", "Mary Jane Shoes"),
        ("Boat shoes were required on the dock.", "Boat Shoes"),
        ("The east-west bag sat in storage.", "East-West Bags"),
        ("The east west tote sat in storage.", "East-West Bags"),
        ("Suede sneakers appeared in a court filing.", "Suede Sneakers"),
    ]
    for text, entity_name in generic_texts:
        decisions = [
            decision
            for decision in evaluate_entity_matches(text, entities)
            if decision.entity_name == entity_name
        ]
        assert decisions, f"Expected evaluated decisions for {entity_name!r}"
        assert all(not decision.accepted for decision in decisions)
        assert {decision.reason for decision in decisions} == {"missing_context"}
```

Expected before YAML changes: at least `Boat Shoes` and `Suede Sneakers` are
accepted without context.

- [ ] **Step 2: Update optional watchlist aliases**

In `configs/entity-packs/fashion-watchlist.example.yaml`, add
`requires_context: true` to aliases for:

```yaml
  - name: Mary Jane Shoes
    aliases:
      - value: Mary Jane shoes
        requires_context: true
      - value: Mary Janes
        requires_context: true
      - value: Mary Jane flats
        requires_context: true
    context_terms: [footwear, runway, styling]
```

```yaml
  - name: East-West Bags
    aliases:
      - value: east-west bag
        requires_context: true
      - value: east-west bags
        requires_context: true
      - value: east west tote
        requires_context: true
    context_terms: [handbag, runway, styling]
```

```yaml
  - name: Boat Shoes
    aliases:
      - value: boat shoes
        requires_context: true
      - value: boat shoe
        requires_context: true
    context_terms: [footwear, loafer, runway, styling]
```

```yaml
  - name: Suede Sneakers
    aliases:
      - value: suede sneakers
        requires_context: true
      - value: suede sneaker
        requires_context: true
    context_terms: [footwear, shoes, trainer]
```

Do not change `Sandy Liang` in this stage; that brand-name recall/precision
choice remains a user-editable seed-pack tradeoff.

- [ ] **Step 3: Run watchlist tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_entity_packs.py::test_fashion_watchlist_context_gates_broad_category_aliases \
  tests/test_entity_packs.py::test_fashion_watchlist_matcher_accepts_parent_brand_or_fashion_context \
  tests/test_entity_packs.py::test_fashion_watchlist_sample_matches_expected_entities_and_types \
  tests/test_watchlist_sample_workflow.py::test_optional_watchlist_sample_runs_local_import_match_report_and_trends \
  -q
```

Expected: pass after YAML changes. If the optional sample workflow drops
`Mary Jane Shoes` or `East-West Bags`, adjust only the `summary` column in
`examples/community-signals.watchlist.example.csv` so it includes non-self
context terms such as `runway footwear` or `handbag styling`; keep URLs as
`example.com`.

## Task 4: Update Docs, Docs Tests, And Changelog

**Files:**

- Modify: `docs/entity-packs.md`
- Modify: `docs/entity-pack-quality.md`
- Modify: `tests/test_entity_packs_docs.py`
- Modify: `tests/test_entity_pack_quality_docs.py`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update entity-pack docs wording**

In `docs/entity-packs.md`, update the alias guidance to say:

```markdown
For ordinary multi-word aliases that are useful but too broad for your source
set, set `requires_context: true` on that alias and provide `context_terms` on
the entity. Avoid context terms that are satisfied only by the alias text
itself; use surrounding fashion terms such as `runway`, `footwear`, `handbag`,
or `styling`.
```

Keep the existing local-only/no-demand-proof boundaries.

- [ ] **Step 2: Update entity-pack quality docs**

In `docs/entity-pack-quality.md`:

- Document `requires_context` in the matcher-rule notes.
- Update the JSON/table examples to match current output from:

```bash
uv --no-config run --frozen fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml --format json
uv --no-config run --frozen fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml
```

- [ ] **Step 3: Update docs tests**

Update `tests/test_entity_packs_docs.py` so it asserts the docs mention:

```python
"requires_context: true"
"provide `context_terms`"
"avoid context terms that are satisfied only by the alias text itself"
```

Update `tests/test_entity_pack_quality_docs.py` only if the current sample
shape changes from one representative finding to no findings or a new first
finding.

- [ ] **Step 4: Add changelog entry**

Prepend under `[Unreleased]` / `### Added`:

```markdown
- Stage 206 adds an explicit alias-level context gate for deterministic
  matching and applies it to high-risk optional watchlist category aliases,
  without changing sources, scoring, report generation, dashboard behavior,
  social/platform connectors, scraping, demand proof, platform coverage
  verification, dependency files, or compliance-review behavior.
```

- [ ] **Step 5: Run docs-focused tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_entity_packs_docs.py tests/test_entity_pack_quality_docs.py -q
uv --no-config run --frozen ruff check docs/entity-packs.md docs/entity-pack-quality.md tests/test_entity_packs_docs.py tests/test_entity_pack_quality_docs.py CHANGELOG.md
uv --no-config run --frozen ruff format --check tests/test_entity_packs_docs.py tests/test_entity_pack_quality_docs.py
```

## Task 5: Focused Verification And Code Review

**Files:**

- Add: `docs/reviews/opencode-stage-206-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-206-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_matcher.py tests/test_config.py tests/test_entity_pack_lint.py tests/test_entity_packs.py tests/test_watchlist_sample_workflow.py tests/test_entity_packs_docs.py tests/test_entity_pack_quality_docs.py -q
uv --no-config run --frozen fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml --format json
uv --no-config run --frozen ruff check src/fashion_radar/models/entity.py src/fashion_radar/extract/entities.py src/fashion_radar/settings.py src/fashion_radar/entity_packs.py tests/test_matcher.py tests/test_config.py tests/test_entity_pack_lint.py tests/test_entity_packs.py tests/test_watchlist_sample_workflow.py tests/test_entity_packs_docs.py tests/test_entity_pack_quality_docs.py docs/entity-packs.md docs/entity-pack-quality.md CHANGELOG.md docs/superpowers/plans/2026-06-25-stage-206-explicit-alias-context-gates-plan.md docs/reviews/opencode-stage-206-plan-review.md docs/reviews/opencode-stage-206-plan-review-prompt.md
uv --no-config run --frozen ruff format --check src/fashion_radar/models/entity.py src/fashion_radar/extract/entities.py src/fashion_radar/settings.py src/fashion_radar/entity_packs.py tests/test_matcher.py tests/test_config.py tests/test_entity_pack_lint.py tests/test_entity_packs.py tests/test_watchlist_sample_workflow.py tests/test_entity_packs_docs.py tests/test_entity_pack_quality_docs.py
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --exit-code -- uv.lock pyproject.toml
git diff --check
```

- [ ] **Step 2: Run OpenCode code review**

Create `docs/reviews/opencode-stage-206-code-review-prompt.md`, then run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-206-code-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-206-code-review.md
rm -f "$tmp_review"
```

Clean the artifact and fix any Critical or Important findings.

## Task 6: Release Verification, Release Review, Commit, Push

**Files:**

- Add: `docs/reviews/opencode-stage-206-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-206-release-review.md`

- [ ] **Step 1: Run release verification**

Run:

```bash
uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
git diff --exit-code -- uv.lock pyproject.toml
git diff --check
```

- [ ] **Step 2: Run OpenCode release review**

Create `docs/reviews/opencode-stage-206-release-review-prompt.md`, then run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-206-release-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-206-release-review.md
rm -f "$tmp_review"
```

Clean the artifact and fix any Critical or Important findings.

- [ ] **Step 3: Commit and push**

Run:

```bash
git status --short --untracked-files=all
git add src/fashion_radar/models/entity.py src/fashion_radar/extract/entities.py src/fashion_radar/settings.py src/fashion_radar/entity_packs.py configs/entity-packs/fashion-watchlist.example.yaml tests/test_matcher.py tests/test_config.py tests/test_entity_pack_lint.py tests/test_entity_packs.py tests/test_watchlist_sample_workflow.py docs/entity-packs.md docs/entity-pack-quality.md tests/test_entity_packs_docs.py tests/test_entity_pack_quality_docs.py CHANGELOG.md docs/superpowers/plans/2026-06-25-stage-206-explicit-alias-context-gates-plan.md docs/reviews/opencode-stage-206-*.md
git commit -m "Stage 206: add explicit alias context gates"
git push origin main
git status --short --branch --untracked-files=all
```

## Self-Review

- Spec coverage: The plan covers model, matcher, config validation, linter,
  optional watchlist data, docs, changelog, review artifacts, focused gates,
  release gates, and push.
- Placeholder scan: No TBD/TODO/fill-in placeholders remain.
- Type consistency: The new field is consistently named `requires_context`.
- Scope check: This is a deterministic matching-quality node. It deliberately
  avoids source acquisition, social/platform connectors, scraping, ranking,
  demand proof, platform coverage verification, dependencies, dashboard/report
  behavior, and compliance-review product features.

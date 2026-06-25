# Stage 207 Context Term Containment Lint Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an advisory entity-pack lint finding for context terms that are wholly contained in a gated alias, so broad aliases with `requires_context: true` do not accidentally satisfy themselves through generic alias words.

**Architecture:** Extend the existing entity-pack linter only. The matcher, entity schema, source acquisition, scoring, reports, dashboard, importers, and optional watchlist semantics stay unchanged. The new lint check should run inside `_alias_findings(...)`, reuse normalized alias/context keys, and emit a warning only when a gated alias can be satisfied by a context term that is a proper token subset of that alias.

**Tech Stack:** Pydantic models, existing deterministic entity-pack lint helpers, pytest, Markdown docs, `uv --no-config run --frozen`, local OpenCode review with `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Scope

This stage closes a deterministic matching quality gap in the local
`collect -> match -> report` pipeline by making optional entity-pack lint
highlight a user-editable precision risk. Stage 206 added explicit alias
context gates. Stage 207 should make it easier to catch a bad local pack edit
such as:

```yaml
aliases:
  - value: Mary Jane shoes
    requires_context: true
context_terms: [shoes]
```

In that configuration, the alias text itself can provide the context term, so
the gate is weaker than the user probably intended.

In scope:

- Add one warning finding code, tentatively
  `contained_context_term_for_gated_alias`.
- Emit the finding for gated aliases when a context term is a proper normalized
  token subset of the alias key.
- Keep the existing `self_context_term` finding for exact alias/context equality.
- Add focused linter tests for exact equality, substring/token containment, and
  non-contained surrounding context terms.
- Cover both single-token and multi-token proper containment, plus an
  equal-length reordered phrase that should not warn.
- Update `docs/entity-pack-quality.md` and docs parity tests as needed.
- Add Stage 207 OpenCode plan/code/release review artifacts when implementing.

Out of scope:

- No matcher behavior changes.
- No model/schema changes.
- No config-validation changes.
- No changes to optional watchlist YAML unless a failing test proves the
  current checked-in watchlist trips the new warning.
- No product parent-brand containment warning in this stage. Products with
  `parent_brand` are intentionally left on the existing parent-brand-or-context
  path; a future lint stage can evaluate product-specific heuristics separately.
- No default starter config changes.
- No source packs, collectors, social/platform connectors, scraping, browser
  automation, cookies/tokens, scoring, report generation, dashboard, DB schema,
  demand proof, platform coverage verification, dependency, lockfile, or
  compliance-review behavior changes.

## File Map

- Modify `src/fashion_radar/entity_packs.py`
  - Add helper logic for proper token-containment context terms.
  - Add the new warning finding inside `_alias_findings(...)`.
- Modify `tests/test_entity_pack_lint.py`
  - Add RED/GREEN coverage for exact equality, proper containment, and safe
    surrounding context terms.
- Modify `docs/entity-pack-quality.md`
  - Document the new finding code and explain the user action.
- Modify `tests/test_entity_pack_quality_docs.py`
  - Update docs sample parity only if live watchlist lint sample changes.
- Modify `CHANGELOG.md`
  - Add a Stage 207 entry when implemented.
- Add review artifacts under `docs/reviews/`.

## Task 0: Plan Review

**Files:**

- Add: `docs/reviews/opencode-stage-207-plan-review-prompt.md`
- Add: `docs/reviews/opencode-stage-207-plan-review.md`

- [ ] **Step 1: Create the plan-review prompt**

Create `docs/reviews/opencode-stage-207-plan-review-prompt.md` asking OpenCode
to review this plan for matcher non-regression, lint semantics, false-positive
risk, docs sample impact, release hygiene, and scope control.

- [ ] **Step 2: Run OpenCode plan review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-207-plan-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-207-plan-review.md
rm -f "$tmp_review"
```

Expected: completed review artifact with no Critical or Important blockers.
Fix Critical/Important planning findings and run a rereview before Task 1.

## Task 1: RED Tests For Contained Context Terms

**Files:**

- Modify: `tests/test_entity_pack_lint.py`

- [ ] **Step 1: Add containment warning RED coverage**

Add:

```python
def test_contained_context_term_warns_for_explicit_gated_alias(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: Mary Jane Shoes
            type: category
            aliases:
              - value: Mary Jane shoes
                requires_context: true
            context_terms: [shoes, runway]
            category_tags: [shoes]
            initial_weight: 1.0
            match_confidence: 1.0
        """,
    )

    result = lint_entity_pack(path)

    finding = findings_by_code(result, "contained_context_term_for_gated_alias")[0]
    assert finding.severity == EntityPackFindingSeverity.WARNING
    assert finding.entity_name == "Mary Jane Shoes"
    assert finding.alias == "Mary Jane shoes"
    assert finding.field == "context_terms"
```

- [ ] **Step 2: Add non-contained context regression**

Add:

```python
def test_surrounding_context_term_does_not_warn_for_explicit_gated_alias(
    tmp_path: Path,
) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: Mary Jane Shoes
            type: category
            aliases:
              - value: Mary Jane shoes
                requires_context: true
            context_terms: [footwear, runway, styling]
            category_tags: [shoes]
            initial_weight: 1.0
            match_confidence: 1.0
        """,
    )

    result = lint_entity_pack(path)

    assert "contained_context_term_for_gated_alias" not in finding_codes(result)
    assert "self_context_term" not in finding_codes(result)
```

- [ ] **Step 3: Add multi-token containment coverage**

Add:

```python
def test_multi_token_context_term_contained_in_gated_alias_warns(
    tmp_path: Path,
) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: Mary Jane Shoes
            type: category
            aliases:
              - value: Mary Jane shoes
                requires_context: true
            context_terms: [mary jane, runway]
            category_tags: [shoes]
            initial_weight: 1.0
            match_confidence: 1.0
        """,
    )

    result = lint_entity_pack(path)

    finding = findings_by_code(result, "contained_context_term_for_gated_alias")[0]
    assert finding.entity_name == "Mary Jane Shoes"
    assert finding.alias == "Mary Jane shoes"
```

- [ ] **Step 4: Add equal-length reordered phrase negative coverage**

Add:

```python
def test_equal_length_reordered_context_term_does_not_warn_for_gated_alias(
    tmp_path: Path,
) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: Mary Jane
            type: category
            aliases:
              - value: Mary Jane
                requires_context: true
            context_terms: [jane mary, runway]
            category_tags: [shoes]
            initial_weight: 1.0
            match_confidence: 1.0
        """,
    )

    result = lint_entity_pack(path)

    assert "contained_context_term_for_gated_alias" not in finding_codes(result)
    assert "self_context_term" not in finding_codes(result)
```

- [ ] **Step 5: Keep exact equality behavior pinned**

Update or keep the existing exact-equality test so it continues to assert
`self_context_term` for:

```yaml
aliases:
  - value: boat shoes
    requires_context: true
context_terms: [boat shoes, footwear]
```

Do not require the new containment finding for exact equality; exact equality
is already covered by `self_context_term`. Also assert:

```python
assert "contained_context_term_for_gated_alias" not in finding_codes(result)
```

- [ ] **Step 6: Run RED tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_entity_pack_lint.py::test_contained_context_term_warns_for_explicit_gated_alias \
  tests/test_entity_pack_lint.py::test_surrounding_context_term_does_not_warn_for_explicit_gated_alias \
  tests/test_entity_pack_lint.py::test_multi_token_context_term_contained_in_gated_alias_warns \
  tests/test_entity_pack_lint.py::test_equal_length_reordered_context_term_does_not_warn_for_gated_alias \
  tests/test_entity_pack_lint.py::test_explicit_context_alias_warns_when_context_term_matches_alias \
  -q
```

Expected before implementation: the new containment test fails because the new
finding code is not emitted; the surrounding-context and exact-equality tests
should pass or fail only for the expected missing-code reason.

## Task 2: Implement Lint Finding

**Files:**

- Modify: `src/fashion_radar/entity_packs.py`
- Test: `tests/test_entity_pack_lint.py`

- [ ] **Step 1: Add helper logic**

Add a private helper near `_alias_requires_context(...)`:

```python
def _context_term_contained_in_alias(alias_key: str, context_key: str) -> bool:
    if not alias_key or not context_key or alias_key == context_key:
        return False
    alias_tokens = alias_key.split()
    context_tokens = context_key.split()
    if not context_tokens or len(context_tokens) >= len(alias_tokens):
        return False
    for start in range(0, len(alias_tokens) - len(context_tokens) + 1):
        if alias_tokens[start : start + len(context_tokens)] == context_tokens:
            return True
    return False
```

This catches token-containment cases such as `shoes` or `mary jane` inside
`mary jane shoes` without warninging for exact equality, reordered equal-length
phrases, or unrelated surrounding context terms.

- [ ] **Step 2: Emit warning inside `_alias_findings(...)`**

Within the per-alias loop, after the existing `self_context_term` check, add a
deterministically sorted loop over normalized context keys:

```python
        if gate == AliasGateKind.CONTEXT_REQUIRED:
            for context_key in sorted(context_keys):
                if not _context_term_contained_in_alias(alias_key, context_key):
                    continue
                findings.append(
                    EntityPackFinding(
                        severity=EntityPackFindingSeverity.WARNING,
                        code="contained_context_term_for_gated_alias",
                        message=(
                            "Context term is contained in a gated alias; choose "
                            "surrounding context terms so the alias text alone "
                            "does not satisfy the gate."
                        ),
                        entity_name=entity.name,
                        alias=alias.value,
                        field="context_terms",
                    )
                )
                break
```

Preserve the existing `self_context_term` behavior for exact equality.

- [ ] **Step 3: Run GREEN tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_entity_pack_lint.py::test_contained_context_term_warns_for_explicit_gated_alias \
  tests/test_entity_pack_lint.py::test_surrounding_context_term_does_not_warn_for_explicit_gated_alias \
  tests/test_entity_pack_lint.py::test_multi_token_context_term_contained_in_gated_alias_warns \
  tests/test_entity_pack_lint.py::test_equal_length_reordered_context_term_does_not_warn_for_gated_alias \
  tests/test_entity_pack_lint.py::test_explicit_context_alias_warns_when_context_term_matches_alias \
  -q
```

Expected: pass.

- [ ] **Step 4: Run focused linter tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_entity_pack_lint.py tests/test_entity_packs.py -q
uv --no-config run --frozen ruff check src/fashion_radar/entity_packs.py tests/test_entity_pack_lint.py
uv --no-config run --frozen ruff format --check src/fashion_radar/entity_packs.py tests/test_entity_pack_lint.py
```

## Task 3: Docs, Changelog, And Review

**Files:**

- Modify: `docs/entity-pack-quality.md`
- Modify: `tests/test_entity_pack_quality_docs.py` only if sample output changes
- Modify: `CHANGELOG.md`
- Add: `docs/reviews/opencode-stage-207-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-207-code-review.md`

- [ ] **Step 1: Update docs**

In `docs/entity-pack-quality.md`, add the finding code:

```markdown
- `contained_context_term_for_gated_alias`: a context term is contained in a
  gated alias, so the alias text may satisfy its own context gate. Prefer
  surrounding fashion terms such as `runway`, `footwear`, `handbag`, or
  `styling`. This is an advisory token-containment heuristic, not a full
  matcher simulation.
```

If the checked-in watchlist live lint output changes, regenerate the table/JSON
samples and update parity tests. If live output remains unchanged, do not
change the sample counts.

- [ ] **Step 2: Update changelog**

Add a Stage 207 entry under `[Unreleased]` / `### Added` or `### Fixed`
depending on final behavior:

```markdown
- Stage 207 adds advisory entity-pack lint coverage for context terms contained
  in gated aliases, without changing matcher behavior, source acquisition,
  scoring, report generation, dashboard behavior, social/platform connectors,
  scraping, demand proof, platform coverage verification, dependency files, or
  compliance-review behavior.
```

- [ ] **Step 3: Run docs-focused tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_entity_pack_quality_docs.py -q
uv --no-config run --frozen ruff check docs/entity-pack-quality.md CHANGELOG.md
```

- [ ] **Step 4: Run OpenCode code review**

Create `docs/reviews/opencode-stage-207-code-review-prompt.md`, then run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-207-code-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-207-code-review.md
rm -f "$tmp_review"
```

Fix Critical and Important findings before release verification.

## Task 4: Release Verification, Release Review, Commit, Push

**Files:**

- Add: `docs/reviews/opencode-stage-207-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-207-release-review.md`

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

- [ ] **Step 2: Run release review**

Create `docs/reviews/opencode-stage-207-release-review-prompt.md`, then run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-207-release-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-207-release-review.md
rm -f "$tmp_review"
```

Fix Critical and Important findings.

- [ ] **Step 3: Commit and push**

Run:

```bash
git status --short
git add src/fashion_radar/entity_packs.py tests/test_entity_pack_lint.py docs/entity-pack-quality.md tests/test_entity_pack_quality_docs.py CHANGELOG.md docs/reviews/opencode-stage-207-*.md docs/superpowers/plans/2026-06-26-stage-207-context-term-containment-lint-plan.md
git commit -m "Stage 207: flag contained context terms"
git push origin main
```

## Self-review

- Spec coverage: the plan covers RED tests, linter implementation, docs,
  changelog, OpenCode plan/code/release reviews, and release verification.
- Placeholder scan: no TODO/TBD/fill-in placeholders are present.
- Type consistency: the finding code, helper names, and test names are used
  consistently across tasks.

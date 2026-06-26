# Stage 208 Context Term Warning Detail Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Stage 207 `contained_context_term_for_gated_alias` entity-pack lint warning name the specific context term and gated alias in its message, so local pack authors can fix the precision risk without manually comparing every term.

**Architecture:** Keep this stage inside the existing entity-pack linter. Preserve `EntityPackFinding` and `EntityPackLintResult` schemas, matcher behavior, config loading, source acquisition, scoring, reports, dashboard, importers, and source packs. Replace the Stage 207 normalized context-key set used by `_alias_findings(...)` with a deterministic normalized-key to display-term lookup, then include the selected display context term and gated alias in the existing warning message.

**Tech Stack:** Pydantic models, existing deterministic entity-pack lint helpers, pytest, Markdown docs, `uv --no-config run --frozen`, local OpenCode review with `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Scope

This stage closes a matching-quality explainability gap in the local
`collect -> match -> report` pipeline. Stage 207 can identify that a gated
alias may satisfy its own context gate, but its message is generic. Stage 208
should make the finding actionable by naming the offending local context term
and gated alias in the free-text message.

Example current warning shape:

```text
Context term is contained in a gated alias; choose surrounding context terms so
the alias text alone does not satisfy the gate.
```

Desired warning shape:

```text
Context term 'shoes' is contained in gated alias 'Mary Jane shoes'; choose
surrounding context terms that the alias text does not satisfy by itself.
```

In scope:

- Keep finding code `contained_context_term_for_gated_alias`.
- Preserve the one-warning-per-offending-alias behavior from Stage 207.
- Preserve exact equality behavior through `self_context_term`; do not create a
  second containment warning for exact equality.
- Select the offending context term deterministically by sorted normalized
  context key.
- Preserve display text from the first configured context term for a normalized
  key so messages remain human-readable.
- Add focused tests that prove the message names the contained term and gated
  alias for single-token and multi-token contexts.
- Add focused tests that prove deterministic selection when multiple contained
  terms exist.
- Update entity-pack quality docs and changelog.
- Add Stage 208 OpenCode plan/code/release review artifacts.

Out of scope:

- No new fields on `EntityPackFinding`.
- No JSON contract or CLI table contract changes beyond the existing `message`
  string content.
- No matcher behavior changes.
- No config-validation or entity-schema changes.
- No optional watchlist YAML changes unless a failing test proves the checked-in
  pack now trips changed lint semantics.
- No product parent-brand containment heuristics.
- No default starter config changes.
- No source packs, collectors, source liveness, social/platform connectors,
  scraping, browser automation, cookies/tokens, scoring, report generation,
  dashboard, DB schema, demand proof, platform coverage verification,
  dependency, lockfile, or compliance-review behavior changes.

## File Map

- Modify `src/fashion_radar/entity_packs.py`
  - Preserve the existing linter helper surface.
  - Add a small deterministic helper for normalized context key display lookup.
  - Include the display context term in the containment warning message.
- Modify `tests/test_entity_pack_lint.py`
  - Extend Stage 207 containment tests to assert useful message details.
  - Add a deterministic multi-contained-term message selection test.
- Modify `docs/entity-pack-quality.md`
  - Document that the warning message identifies the offending context term.
- Modify `CHANGELOG.md`
  - Add a Stage 208 entry.
- Add review artifacts under `docs/reviews/`.

## Task 0: Plan Review

**Files:**

- Add: `docs/reviews/opencode-stage-208-plan-review-prompt.md`
- Add: `docs/reviews/opencode-stage-208-plan-review.md`

- [ ] **Step 1: Create the plan-review prompt**

Create `docs/reviews/opencode-stage-208-plan-review-prompt.md` asking OpenCode
to review this plan for linter-only scope, schema non-regression, deterministic
term selection, false-positive risk, docs impact, release hygiene, and scope
control.

- [ ] **Step 2: Run OpenCode plan review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-208-plan-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-208-plan-review.md
rm -f "$tmp_review"
```

Expected: completed review artifact with no Critical or Important blockers.
Fix Critical/Important planning findings and run a rereview before Task 1.

## Task 1: RED Tests For Named Context Terms

**Files:**

- Modify: `tests/test_entity_pack_lint.py`

- [ ] **Step 1: Extend single-token containment message coverage**

In `test_contained_context_term_warns_for_explicit_gated_alias`, add:

```python
assert "'shoes'" in finding.message
assert "'Mary Jane shoes'" in finding.message
```

- [ ] **Step 2: Extend multi-token containment message coverage**

In `test_multi_token_context_term_contained_in_gated_alias_warns`, add:

```python
assert "'mary jane'" in finding.message
assert "'Mary Jane shoes'" in finding.message
```

- [ ] **Step 3: Add deterministic multiple-contained-terms coverage**

Add:

```python
def test_contained_context_term_message_uses_first_sorted_context_key(
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
            context_terms: [shoes, mary jane, runway]
            category_tags: [shoes]
            initial_weight: 1.0
            match_confidence: 1.0
        """,
    )

    result = lint_entity_pack(path)

    finding = findings_by_code(result, "contained_context_term_for_gated_alias")[0]
    assert finding.alias == "Mary Jane shoes"
    assert finding.message.count("Context term") == 1
    assert "'mary jane'" in finding.message
    assert "'shoes'" not in finding.message
```

The expected selected context key is `mary jane` because `_alias_findings(...)`
must preserve Stage 207's sorted normalized context-key iteration.

- [ ] **Step 4: Run RED tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_entity_pack_lint.py::test_contained_context_term_warns_for_explicit_gated_alias \
  tests/test_entity_pack_lint.py::test_multi_token_context_term_contained_in_gated_alias_warns \
  tests/test_entity_pack_lint.py::test_contained_context_term_message_uses_first_sorted_context_key \
  -q
```

Expected: the first two tests fail because the Stage 207 message does not name
the context term, and the new deterministic test fails for the same reason or
because it does not exist yet.

## Task 2: GREEN Linter Message Implementation

**Files:**

- Modify: `src/fashion_radar/entity_packs.py`

- [ ] **Step 1: Add deterministic context display lookup helper**

Add this helper near `_context_term_contained_in_alias(...)`:

```python
def _context_display_by_key(context_terms: Sequence[str]) -> dict[str, str]:
    display_by_key: dict[str, str] = {}
    for context_term in context_terms:
        context_key = normalize_alias_key(context_term)
        if context_key and context_key not in display_by_key:
            display_by_key[context_key] = context_term
    return display_by_key
```

- [ ] **Step 2: Use the helper in `_alias_findings(...)`**

Change the local context key preparation from:

```python
context_keys = {
    normalize_alias_key(term)
    for term in entity.context_terms
    if term.strip() and normalize_alias_key(term)
}
```

to:

```python
context_display_by_key = _context_display_by_key(entity.context_terms)
context_keys = set(context_display_by_key)
```

- [ ] **Step 3: Include display context term and alias in the warning message**

Change the Stage 207 warning message construction from the current baseline:

```python
message=(
    "Context term is contained in a gated alias; choose "
    "surrounding context terms so the alias text alone "
    "does not satisfy the gate."
),
```

to:

```python
context_term = context_display_by_key[context_key]
message=(
    f"Context term '{context_term}' is contained in gated alias "
    f"'{alias.value}'; choose surrounding context terms that the alias text "
    "does not satisfy by itself."
),
```

Keep the `break` so the linter emits one containment warning per alias.
Changing the free-text `message` can affect sort order only for findings that
tie on severity, code, entity, alias, and field because `_sort_findings(...)`
uses `finding.message` as a final deterministic tie breaker. This stage should
not change the checked-in watchlist lint sample because the current watchlist
does not emit `contained_context_term_for_gated_alias`; if focused or full
verification proves otherwise, update the docs sample and parity tests in the
same node.

- [ ] **Step 4: Run GREEN focused tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_entity_pack_lint.py::test_contained_context_term_warns_for_explicit_gated_alias \
  tests/test_entity_pack_lint.py::test_multi_token_context_term_contained_in_gated_alias_warns \
  tests/test_entity_pack_lint.py::test_contained_context_term_message_uses_first_sorted_context_key \
  -q
```

Expected: all selected tests pass.

## Task 3: Docs And Changelog

**Files:**

- Modify: `docs/entity-pack-quality.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update entity-pack quality docs**

Update the `contained_context_term_for_gated_alias` description so it says the
message identifies the contained context term.

- [ ] **Step 2: Add changelog entry**

Add this entry under `[Unreleased] -> Added`:

```markdown
- Stage 208 makes the advisory contained-context-term entity-pack lint warning
  name the offending context term and gated alias in its message, without
  changing matcher behavior, lint schemas, source acquisition, scoring, report
  generation, dashboard behavior, social/platform connectors, scraping, demand
  proof, platform coverage verification, dependency files, or compliance-review
  behavior.
```

- [ ] **Step 3: Run docs-focused tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_entity_pack_lint.py \
  tests/test_entity_pack_quality_docs.py \
  -q
```

Expected: all selected tests pass.

## Task 4: Code Review And Fixes

**Files:**

- Add: `docs/reviews/opencode-stage-208-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-208-code-review.md`
- Add if needed: `docs/reviews/opencode-stage-208-code-rereview-prompt.md`
- Add if needed: `docs/reviews/opencode-stage-208-code-rereview.md`

- [ ] **Step 1: Create the code-review prompt**

Create `docs/reviews/opencode-stage-208-code-review-prompt.md` describing the
Stage 208 goal, changed files, baseline SHA, expected verification, and review
focus.

- [ ] **Step 2: Run OpenCode code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-208-code-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-208-code-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important findings. Fix Critical/Important findings
and run a rereview before Task 5.

## Task 5: Release Verification, Release Review, Commit, Push

**Files:**

- Add: `docs/reviews/opencode-stage-208-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-208-release-review.md`
- Add if needed: `docs/reviews/opencode-stage-208-release-rereview-prompt.md`
- Add if needed: `docs/reviews/opencode-stage-208-release-rereview.md`

- [ ] **Step 1: Run full verification**

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

Expected: every command exits 0, with no lockfile or dependency changes.

- [ ] **Step 2: Create the release-review prompt**

Create `docs/reviews/opencode-stage-208-release-review-prompt.md` summarizing
the Stage 208 changes, full verification evidence, review artifacts, and release
hygiene scope.

- [ ] **Step 3: Run OpenCode release review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-208-release-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-208-release-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important findings. Fix Critical/Important findings
and run a rereview before committing.

- [ ] **Step 4: Stage and inspect the release diff**

Run:

```bash
git add CHANGELOG.md docs/entity-pack-quality.md docs/reviews/opencode-stage-208-*.md \
  docs/superpowers/plans/2026-06-26-stage-208-context-term-warning-detail-plan.md \
  src/fashion_radar/entity_packs.py tests/test_entity_pack_lint.py
git diff --cached --check
git diff --cached | rg -n "ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|BEGIN (RSA|OPENSSH|PRIVATE) KEY|xox[baprs]-[A-Za-z0-9-]{20,}|sk-[A-Za-z0-9]{20,}" || true
```

Expected: whitespace check exits 0 and the secret scan returns no matches.

- [ ] **Step 5: Commit and push**

Run:

```bash
git commit -m "Stage 208: name contained context terms"
git push origin main
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
```

Expected: local `main` and `origin/main` point to the same new Stage 208 commit,
with a clean working tree.

## Self-Review Checklist

- This plan closes a local deterministic matching-quality explainability gap in
  the `collect -> match -> report` pipeline.
- The plan includes RED tests before production-code changes.
- The plan keeps the finding result schema unchanged.
- The plan preserves Stage 207 warning semantics and only improves message
  detail.
- The plan avoids source acquisition, social/platform connectors, scraping,
  browser automation, cookies/tokens, dependency, lockfile, demand proof,
  platform coverage verification, and compliance-review product work.
- The plan includes OpenCode plan/code/release review gates.
- The plan includes full release verification and secret-scan hygiene before
  push.

# Stage 196 Latin Fold Parity And Starter Doc Guards Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make deterministic normalization and runtime alias matching use the same Latin-folding coverage for common fashion names, and add a small offline documentation guard for the compact default starter source config.

**Architecture:** Keep the Stage 195 source boundary unchanged. Preserve the existing NFD/combining-mark stripping path, then add a narrow explicit override map for the current non-decomposing Latin misses whose lowercase forms are already implied by `_DIACRITIC_CLASS_BY_ASCII`, plus the uppercase counterpart needed before lowercasing: `ø -> o`, `Ø -> O`, and `ı -> i`. Do not derive future normalization behavior automatically from the regex inventory, and do not add broad transliteration. Add tests that prove normalized keys, content hashes, parent-brand keys, and runtime alias regexes agree on representative non-decomposing characters. Add a README Configuration-section guard that checks the default starter is documented as compact while the public source pack remains broader.

**Tech Stack:** Python 3.11+, stdlib `unicodedata`, existing regex helper in `fashion_radar.extract.text`, pytest, checked-in YAML configs, no new dependencies.

---

## Scope Boundary

This stage must not add source connectors, social scraping, browser automation, platform APIs, login/cookie/proxy behavior, live URL guarantees, source ranking, demand proof, platform-wide coverage claims, or compliance-review product features.

## Files And Responsibilities

- Modify `src/fashion_radar/extract/text.py`: make `_fold_diacritics()` use a narrow explicit override fallback for current non-decomposing Latin misses.
- Modify `tests/test_text.py`: add failing tests for `Søster/Soster`, `Loewe/Løewe`, uppercase `Ø`, and dotless `ı` normalization and runtime matching parity.
- Modify `tests/test_dedupe.py`: add a content-hash regression for non-decomposing Latin folds.
- Modify `tests/test_matcher.py`: add a parent-brand key regression for non-decomposing Latin folds.
- Modify `tests/test_cli_docs.py`: add an offline docs guard for the exact README Configuration section starter-source wording and public-pack distinction.
- Modify docs only if the new guard requires precise wording: likely `README.md` only.
- Create Stage 196 review artifacts under `docs/reviews/`.

## Task 1: Latin Fold Parity For Non-Decomposing Characters

**Files:**
- Modify: `tests/test_text.py`
- Modify: `src/fashion_radar/extract/text.py`

- [ ] **Step 1: Add failing tests**

Add assertions to `tests/test_text.py`:

```python
def test_normalize_text_folds_non_decomposing_latin_variants() -> None:
    assert normalize_text("Løewe MØ ı bag") == "loewe mo i bag"


def test_alias_pattern_matches_non_decomposing_latin_variants() -> None:
    loewe_pattern = alias_pattern("Loewe")
    soster_pattern = alias_pattern("Søster Studio")

    assert loewe_pattern.search("Løewe puzzle bag")
    assert soster_pattern.search("Soster Studio bag")
```

- [ ] **Step 2: Verify red on a fresh pre-implementation tree**

Run:

```bash
uv --no-config run --frozen pytest tests/test_text.py::test_normalize_text_folds_non_decomposing_latin_variants tests/test_text.py::test_alias_pattern_matches_non_decomposing_latin_variants -q
```

Expected on a fresh pre-implementation tree: at least the normalization
assertion fails because NFD does not decompose `ø`, `Ø`, or `ı`. If this stage
has already been partially implemented in the working tree, record that this
step is no longer reproducibly red and continue with focused verification.

- [ ] **Step 3: Implement minimal map-backed fallback**

In `src/fashion_radar/extract/text.py`, add a narrow private override map:

```python
_ASCII_FOLD_OVERRIDES = {
    "ø": "o",
    "Ø": "O",
    "ı": "i",
}
```

Then update `_fold_diacritics()` so it keeps NFD/combining-mark stripping as the primary path and applies the override while appending non-combining characters:

```python
folded: list[str] = []
for char in unicodedata.normalize("NFD", value):
    if unicodedata.combining(char):
        continue
    folded.append(_ASCII_FOLD_OVERRIDES.get(char, char))
return "".join(folded)
```

This preserves the invariant that normalization and runtime alias matching agree for the explicitly supported non-decomposing characters without making future regex-class additions silently change content hashes or entity keys.

- [ ] **Step 4: Verify focused tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_text.py tests/test_dedupe.py tests/test_matcher.py -q
```

Expected: all pass.

- [ ] **Step 5: Add downstream focused regressions**

Add to `tests/test_dedupe.py` a regression that `content_hash()` treats `Søster/MØ` and `Soster/MO` as the same normalized content. In `tests/test_matcher.py`, use the existing Stage 196 parent-brand-key red coverage if present; otherwise add a regression that a product with `parent_brand="Soster Studio"` accepts text containing `Søster Studio` via `parent_brand`. Do not duplicate the same parent-brand assertion if the test already exists.

Run:

```bash
uv --no-config run --frozen pytest tests/test_dedupe.py tests/test_matcher.py tests/test_entity_packs.py tests/test_trends.py -q
```

Expected: all pass.

## Task 2: Default Starter Documentation Guard

**Files:**
- Modify: `tests/test_cli_docs.py`
- Modify if needed: `README.md`

- [ ] **Step 1: Add a docs guard**

Add `test_readme_documents_compact_default_source_starter()` to `tests/test_cli_docs.py`. It must use the existing `_markdown_section_exact_heading()` helper to extract only the `## Configuration` section from `README.md`, normalize the section with `_normalized_text(...).casefold()`, and assert the section contains the current README wording after casefolding:

```python
"compact rss/gdelt fashion starter set"
"starter lanes for industry news"
"celebrity style"
"designer/luxury"
"emerging designers"
"fashion week"
"bags"
"shoes"
"broader optional public-source starter packs"
"sources.example.yaml"
"configs/source-packs"
"docs/source-packs.md"
```

The test should compare with `.casefold()` on both sides, for example `assert phrase.casefold() in normalized`, so `RSS/GDELT` capitalization in README does not matter. It should also assert that the compact default starter wording appears before the broader optional public-source starter-pack wording inside the same Configuration section. The test must not read network sources or run CLI commands, and it must not pass based on unrelated README sections.

- [ ] **Step 2: Verify red or existing coverage**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_readme_documents_compact_default_source_starter -q
```

Expected: if the wording already exists, this may pass immediately. If it passes immediately, record that Stage 195 already added the documented wording and keep the guard as regression coverage.

- [ ] **Step 3: Update README only if needed**

If the new test fails, update only the Configuration section in `README.md` to include the exact factual wording. Do not add broader source-coverage, ranking, demand, platform coverage, or live URL claims.

- [ ] **Step 4: Verify docs tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py tests/test_project_brief_docs.py tests/test_review_protocol_docs.py -q
```

Expected: all pass.

## Task 3: Review, Release, Commit

**Files:**
- Create concise Stage 196 code and release review artifacts under `docs/reviews/`.

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_text.py tests/test_dedupe.py tests/test_matcher.py tests/test_cli_docs.py tests/test_project_brief_docs.py tests/test_review_protocol_docs.py -q
```

Expected: all pass.

- [ ] **Step 2: Run full verification**

Run:

```bash
uv --no-config run --frozen pytest tests/ -q --tb=short
uv --no-config run --frozen pytest tests/test_release_hygiene.py -q
uv --no-config run --frozen ruff check src/fashion_radar/extract/text.py tests/test_text.py tests/test_dedupe.py tests/test_matcher.py tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check src/fashion_radar/extract/text.py tests/test_text.py tests/test_dedupe.py tests/test_matcher.py tests/test_cli_docs.py
git diff --check
UV_NO_CONFIG=1 uv lock --check
git diff --exit-code -- uv.lock pyproject.toml
! rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock
```

Expected: all pass.

- [ ] **Step 3: Run local code review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "Review Stage 196 changes for plan compliance, technical correctness, tests, and scope boundaries. Do not suggest adding compliance-review product features."
```

Expected: no critical or important findings. Fix any blocking findings before commit.

- [ ] **Step 4: Run release review**

Create `docs/reviews/opencode-stage-196-release-review-prompt.md` and
`docs/reviews/opencode-stage-196-release-review.md` after final verification.
The release review must record the verification commands, lockfile hygiene
checks, final scope boundary, uncommitted files, and handoff summary. Fix any
Critical or Important release findings before commit.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short
git add src/fashion_radar/extract/text.py tests/test_text.py tests/test_dedupe.py tests/test_matcher.py tests/test_cli_docs.py docs/reviews/*stage-196*.md docs/superpowers/plans/2026-06-25-stage-196-latin-fold-parity-and-starter-doc-guards-plan.md
git commit -m "Stage 196: align latin folding and guard starter docs"
git push origin main
```

Expected: push succeeds.

## Self-Review Checklist

- [ ] Tests cover normalization and runtime alias matching parity for non-decomposing Latin characters.
- [ ] No new dependency is added.
- [ ] README guard is offline and exact enough to prevent starter/public-pack wording drift.
- [ ] Stage 196 does not modify source-pack configs, collectors, social/community handoff surfaces, scoring, DB schema, or dashboard behavior.

# Stage 195 Source Coverage And Diacritics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close two cross-validated product gaps without changing the core boundary: make entity alias matching handle common Latin diacritics, and bring the default starter source config closer to the already-broader public source pack.

**Architecture:** Keep v0.1.x source collection limited to configured RSS/RSSHub/GDELT sources and keep social/community tooling as opt-in local handoff surfaces. Add a small diacritic-folding helper in `extract/text.py`, then use it both for normalized keys and for runtime `alias_pattern()` regex construction so existing entity matching call sites do not change. Verification must prove that `alias_pattern(...).search(raw_text)` matches accented and plain forms at runtime, not only that normalized keys compare equal. Expand only the root/package default `sources.example.yaml` starter configs, keeping them byte-identical and intentionally smaller than the full public source pack; do not change `configs/source-packs/fashion-public.example.yaml` in this stage.

**Tech Stack:** Python 3.11+, Typer CLI, Pydantic config models in `settings.py` and `models/source.py`, pytest, YAML source configs, existing offline source-pack/config tests.

---

## Scope Boundary

This stage must not add social-platform scraping, login cookies, browser automation, platform APIs, proxy pools, scheduling, monitoring, source acquisition automation, live URL guarantees, demand proof, ranking claims, compliance-review product features, or coverage verification claims. It only improves local deterministic matching and checked-in starter YAML examples.

## Current-State Corrections From Plan Review

- `configs/source-packs/fashion-public.example.yaml` is already broad: 16 enabled sources, 6 RSS entries, and 10 GDELT lanes. It is not the target for Stage 195.
- `configs/sources.example.yaml` and `src/fashion_radar/templates/configs/sources.example.yaml` are the small default starter configs used by docs and `fashion-radar init`; these are the source-coverage target for this stage.
- `alias_pattern()` currently searches raw text, so changing only `normalize_text()` does not make alias matching diacritic-insensitive. This stage must cover `alias_pattern()`.
- Existing test names differ from the first draft. Use `tests/test_text.py`, `tests/test_config.py`, `tests/test_stage1_hardening.py`, `tests/test_candidate_extraction.py`, `tests/test_candidate_scoring.py`, `tests/test_entity_pack_lint.py`, and `tests/test_entity_packs.py`.
- `CHANGELOG.md` exists in the repository and is an accepted release-status file for this stage's concise user-visible change note.

## Files And Responsibilities

- Modify `src/fashion_radar/extract/text.py`: add diacritic folding helper; use it in `normalize_text()` and `alias_pattern()`.
- Modify `tests/test_text.py`: add failing tests for `normalize_text()` and runtime alias matching across accented/plain spellings.
- Modify `tests/test_config.py`: add offline guard proving root default starter source config has the intended tags/source types and loads through `load_source_config()`.
- Modify `tests/test_stage1_hardening.py`: keep or extend root/package byte-parity checks for `sources.example.yaml`.
- Modify `configs/sources.example.yaml`: expand the default starter set from 2 sources to a compact public starter set.
- Modify `src/fashion_radar/templates/configs/sources.example.yaml`: keep byte-identical to `configs/sources.example.yaml`.
- Modify docs only if factual wording needs to mention the broader default starter and diacritic folding: prefer `README.md` and `docs/PROJECT_BRIEF.md`; avoid `docs/architecture.md` unless tests require it.
- Record review artifacts under `docs/reviews/` after plan, code, and release reviews.

## Task 1: Runtime Diacritic-Insensitive Alias Matching

**Files:**
- Modify: `tests/test_text.py`
- Modify: `src/fashion_radar/extract/text.py`

- [ ] **Step 1: Add failing tests**

Add these tests to `tests/test_text.py`:

```python
def test_normalize_text_folds_common_latin_diacritics() -> None:
    assert normalize_text("Hermès Chloé Sézane Alaïa") == "hermes chloe sezane alaia"


def test_alias_pattern_matches_plain_alias_against_diacritic_text() -> None:
    pattern = alias_pattern("Hermes")

    assert pattern.search("Hermès Birkin bag")
    assert pattern.search("Hermes Birkin bag")


def test_alias_pattern_matches_diacritic_alias_against_plain_text() -> None:
    pattern = alias_pattern("Chloé")

    assert pattern.search("Chloe runway bag")
    assert pattern.search("Chloé runway bag")


def test_alias_pattern_matches_uppercase_diacritic_alias_variants() -> None:
    pattern = alias_pattern("Édith")

    assert pattern.search("Edith Head costume archive")
    assert pattern.search("ÉDITH Head costume archive")
```

These assertions are runtime regex checks: they call `alias_pattern(...).search(raw_text)` exactly as entity extraction does, so they prove the matching surface and not only normalized-key behavior.

- [ ] **Step 2: Verify red**

Run:

```bash
uv --no-config run --frozen pytest tests/test_text.py -q
```

Expected: the new tests fail because `normalize_text()` currently preserves accents and `alias_pattern()` currently builds a raw literal regex.

- [ ] **Step 3: Implement minimal folding helper**

In `src/fashion_radar/extract/text.py`, add:

```python
def _fold_diacritics(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value)
    return "".join(char for char in decomposed if not unicodedata.combining(char))
```

Update `normalize_text()` to call `_fold_diacritics()` after punctuation replacements and before whitespace collapse/lowercasing. This intentionally affects normalized alias keys, candidate keys, trend comparison keys, and content hashes for accented text.

- [ ] **Step 4: Make `alias_pattern()` fold common Latin diacritics**

Replace literal alias escaping with a helper that builds a folded-character regex. The helper should:

- normalize and fold the alias with `_fold_diacritics(alias.strip())`;
- preserve existing multi-space behavior by treating normalized whitespace as `\s+`;
- map common folded Latin letters to character classes that include accented variants used in fashion names;
- keep word-boundary behavior `(?<!\w)` and `(?!\w)`;
- keep `re.IGNORECASE`.

Use a small explicit map rather than a broad transliteration dependency:

```python
_DIACRITIC_CLASS_BY_ASCII = {
    "a": "aàáâãäåāăąǎǟǡǻȁȃạảấầẩẫậắằẳẵặ",
    "c": "cçćĉċč",
    "e": "eèéêëēĕėęěȅȇẹẻẽếềểễệ",
    "i": "iìíîïĩīĭįıǐȉȋịỉ",
    "n": "nñńņň",
    "o": "oòóôõöøōŏőǒȍȏơọỏốồổỗộớờởỡợ",
    "u": "uùúûüũūŭůűųǔȕȗưụủứừửữự",
    "y": "yýÿŷȳỳỵỷỹ",
}
```

For every folded alias character:

- whitespace becomes `\s+`;
- mapped ASCII letters use `char.lower()` for the class lookup and become
  `[chars]` with `re.escape(chars)`;
- all other characters use `re.escape(char)`.

- [ ] **Step 5: Verify focused tests pass**

Run:

```bash
uv --no-config run --frozen pytest tests/test_text.py -q
```

Expected: all `tests/test_text.py` tests pass.

- [ ] **Step 6: Verify affected matching/key surfaces**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_config.py::test_duplicate_aliases_are_rejected \
  tests/test_config.py::test_duplicate_entity_names_are_rejected \
  tests/test_dedupe.py \
  tests/test_matcher.py \
  tests/test_candidate_extraction.py \
  tests/test_candidate_scoring.py \
  tests/test_entity_pack_lint.py \
  tests/test_entity_packs.py \
  -q
```

Expected: all pass.

## Task 2: Default Starter Source Config Coverage

**Files:**
- Modify: `tests/test_config.py`
- Modify: `tests/test_stage1_hardening.py` only if the existing parity guard needs clearer failure output.
- Modify: `configs/sources.example.yaml`
- Modify: `src/fashion_radar/templates/configs/sources.example.yaml`

- [ ] **Step 1: Add failing default-starter coverage test**

In `tests/test_config.py`, add a focused offline test after the existing sample-config tests:

```python
def test_starter_source_config_covers_core_fashion_signals_without_article_fetching() -> None:
    public_pack = load_source_config(Path("configs/source-packs/fashion-public.example.yaml"))
    source_config = load_source_config(Path("configs/sources.example.yaml"))
    enabled_sources = [source for source in source_config.sources if source.enabled]
    public_enabled_sources = [source for source in public_pack.sources if source.enabled]
    tags = {tag for source in enabled_sources for tag in source.tags}

    assert len(enabled_sources) >= 6
    assert len(enabled_sources) < len(public_enabled_sources)
    assert {source.type.value for source in enabled_sources} == {"rss", "gdelt"}
    assert {
        "industry_news",
        "celebrity_style",
        "designer_luxury",
        "emerging_designers",
        "fashion_week",
        "accessories",
        "shoes",
    } <= tags
    assert all(source.article.enabled is False for source in enabled_sources if source.type.value == "rss")
```

This test proves the default starter is broader than before but still intentionally smaller than the public source pack. It does not fetch URLs or GDELT.

- [ ] **Step 2: Verify red**

Run:

```bash
uv --no-config run --frozen pytest tests/test_config.py::test_starter_source_config_covers_core_fashion_signals_without_article_fetching -q
```

Expected: the test fails because the current default starter config has only Fashionista RSS and one GDELT lane.

- [ ] **Step 3: Expand `configs/sources.example.yaml`**

Replace the 2-source sample with a compact 6-source starter:

- Fashionista RSS, tags `[fashion_media, industry_news]`
- Fashion Week Daily RSS, tags `[fashion_media, celebrity_style]`
- GDELT Luxury Fashion, tags `[gdelt, designer_luxury, industry_news]`
- GDELT Celebrity Style, tags `[gdelt, celebrity_style]`
- GDELT Emerging Designers, tags `[gdelt, emerging_designers, fashion_week]`
- GDELT Bags Shoes Products, tags `[gdelt, accessories, bags, shoes]`

For each RSS source, keep:

```yaml
article:
  enabled: false
```

For each GDELT source, keep:

```yaml
gdelt:
  lookback_hours: 24
  max_records: 100
  rate_limit_per_second: 1.0
```

For every source, keep:

```yaml
http:
  timeout_seconds: 10
  per_domain_delay_seconds: 1
health:
  max_failures: 3
  retention_hours: 24
```

- [ ] **Step 4: Sync packaged starter template**

Run:

```bash
cp configs/sources.example.yaml src/fashion_radar/templates/configs/sources.example.yaml
```

This is allowed as a mechanical sync step; do not use shell write tricks for bespoke file editing.

- [ ] **Step 5: Verify root/package parity and config loading**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_config.py::test_sample_configs_load_without_network \
  tests/test_config.py::test_starter_source_config_covers_core_fashion_signals_without_article_fetching \
  tests/test_stage1_hardening.py \
  -q
```

Expected: all pass.

- [ ] **Step 6: Confirm public source pack was not changed**

Run:

```bash
git diff -- configs/source-packs/fashion-public.example.yaml
```

Expected: no output.

## Task 3: Minimal Documentation And Changelog

**Files:**
- Modify: `README.md`
- Modify: `docs/PROJECT_BRIEF.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update README starter-source wording**

Update the README section that mentions `sources.example.yaml` to say the starter config includes a compact RSS/GDELT fashion set and that the broader public pack remains available under `configs/source-packs/`.

- [ ] **Step 2: Update project brief status**

In `docs/PROJECT_BRIEF.md`, update the current-priority wording so it says:

- source-liveness exists for user-run diagnostics;
- the public source pack is already broader than the default starter;
- Stage 195 broadens the default starter and improves diacritic-insensitive matching;
- the starter RSS feeds keep article extraction disabled by default;
- none of this proves demand, source ranking, or platform-wide coverage.

- [ ] **Step 3: Add changelog entry**

In `CHANGELOG.md`, add a concise Stage 195 entry:

- default starter source config broadened to compact curated RSS/GDELT lanes;
- RSS article extraction disabled by default in the starter config;
- deterministic text/alias matching folds common Latin diacritics;
- offline tests added for both.

- [ ] **Step 4: Verify docs guards**

Run:

```bash
uv --no-config run --frozen pytest tests/test_review_protocol_docs.py tests/test_cli_docs.py tests/test_source_packs_docs.py tests/test_project_brief_docs.py -q
```

Expected: all pass.

## Task 4: Verification, Review, Commit, Push

**Files:**
- Create: `docs/reviews/opencode-stage-195-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-195-code-review.md`
- Create: `docs/reviews/opencode-stage-195-release-review-prompt.md`
- Create: `docs/reviews/opencode-stage-195-release-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_text.py \
  tests/test_config.py \
  tests/test_stage1_hardening.py \
  tests/test_dedupe.py \
  tests/test_matcher.py \
  tests/test_candidate_extraction.py \
  tests/test_candidate_scoring.py \
  tests/test_entity_pack_lint.py \
  tests/test_entity_packs.py \
  tests/test_review_protocol_docs.py \
  tests/test_cli_docs.py \
  tests/test_source_packs_docs.py \
  -q
```

Expected: all pass.

- [ ] **Step 2: Run full local suite**

Run:

```bash
uv --no-config run --frozen pytest tests/ -q --tb=short
```

Expected: all pass. If live integration tests are present and require network credentials, run the documented non-live subset and record the reason in the release review.

- [ ] **Step 3: Run local code review**

Use:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "Review Stage 195 code changes for plan compliance, technical correctness, tests, and scope boundaries. Do not suggest adding compliance-review product features."
```

Expected: no critical or important findings. If findings appear, fix and rerun review.

- [ ] **Step 4: Run release hygiene**

Run:

```bash
uv --no-config run --frozen pytest tests/test_release_hygiene.py -q
```

Expected: all pass; review artifacts contain no process chatter or capture stubs.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short
git add src/fashion_radar/extract/text.py tests/test_text.py tests/test_config.py configs/sources.example.yaml src/fashion_radar/templates/configs/sources.example.yaml README.md docs/PROJECT_BRIEF.md CHANGELOG.md docs/reviews/*stage-195*.md docs/superpowers/plans/2026-06-25-stage-195-source-coverage-and-diacritics-plan.md
git commit -m "Stage 195: broaden default sources and fold diacritics"
git push origin main
```

Expected: push succeeds.

## Self-Review Checklist

- [ ] The plan addresses the real current gaps: default starter coverage and runtime alias diacritic matching.
- [ ] The plan does not alter the already-broader public source pack.
- [ ] The plan does not add social scraping, browser automation, platform APIs, live URL guarantees, source ranking, demand proof, or compliance-review product features.
- [ ] Tests fail before production changes and are offline/deterministic.
- [ ] Commands use `uv --no-config run --frozen` where appropriate.
- [ ] Root and packaged starter source examples remain byte-identical.

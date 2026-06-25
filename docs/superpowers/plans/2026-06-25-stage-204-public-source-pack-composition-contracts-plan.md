# Stage 204 Public Source-Pack Composition Contracts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the current optional public fashion source pack composition into an explicit offline contract: 20 enabled sources, 10 RSS feeds, 10 bounded GDELT lanes, conservative RSS article fetching, and docs that list both inventories in pack order.

**Architecture:** This is a test/docs contract stage. It does not change source acquisition or add sources. Tests in `tests/test_source_packs.py`, `tests/test_config.py`, and `tests/test_source_packs_docs.py` pin the current public pack composition and docs sync, while `docs/source-packs.md` explains the composition contract for users.

**Tech Stack:** Existing Python/Pytest test suite, PyYAML for raw YAML explicitness checks, existing `load_source_config()` and `lint_source_pack()` helpers, Markdown docs, local OpenCode review with `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Scope

This stage closes a core `collect -> match -> report` pipeline gap: the project now ships a useful optional public source pack, but the repository only loosely tests that it has RSS and GDELT sources. Users need a stable, reviewable source baseline for daily fashion reports before later matching/report improvements can be trusted.

In scope:

- Pin the optional public pack's current 20-source composition as an offline repository contract.
- Pin exact source names, order, type order, all-enabled state, and RSS article extraction disabled by default.
- Pin public GDELT fetch boundaries: 24-hour lookback, 100 max records, and 1.0 request-per-second rate limit.
- Tighten public source-pack lint expectations to no errors, no warnings, no info findings, exact counts, and no findings.
- Expand direct RSS endpoint coverage from the current five-source subset to all ten RSS sources.
- Add docs inventory for RSS sources in pack order and test it against the YAML file.
- Update changelog and add Stage 204 OpenCode review artifacts.

Out of scope:

- No source-pack source additions, removals, URL changes, query changes, tag changes, or weight changes.
- No live network liveness checks as a release gate.
- No collectors, scoring, reports, dashboard, external/community/imported commands, social/platform connectors, scraping, browser automation, source acquisition, demand proof, platform coverage verification, or compliance-review product features.
- No dependency changes and no `uv.lock` / `pyproject.toml` changes.

## File Map

- Modify `tests/test_source_packs.py`
  - Tighten the public pack lint test into an exact composition/lint contract.
- Modify `tests/test_config.py`
  - Expand canonical RSS URL map to all ten public RSS feeds.
  - Add exact public source composition contract test.
  - Add raw YAML explicit fetch-boundary test for RSS and GDELT entries.
- Modify `tests/test_source_packs_docs.py`
  - Add helper for RSS source names from YAML.
  - Add docs test for RSS source list in pack order.
  - Expand existing boundary docs test to mention the new composition contract.
- Modify `docs/source-packs.md`
  - Add current composition contract wording.
  - Add `## RSS Feeds` inventory list in pack order.
- Modify `CHANGELOG.md`
  - Add Stage 204 entry under `### Added`.
- Add `docs/reviews/opencode-stage-204-plan-review-prompt.md`
- Add `docs/reviews/opencode-stage-204-plan-review.md`
- Later add code/release review prompts and bodies.

## Expected Public Pack Composition

The exact composition contract is:

```python
EXPECTED_PUBLIC_SOURCE_COMPOSITION = [
    ("Fashionista", "rss"),
    ("Fashion Week Daily", "rss"),
    ("FashionUnited", "rss"),
    ("The Industry Fashion", "rss"),
    ("Highsnobiety", "rss"),
    ("WWD", "rss"),
    ("Vogue", "rss"),
    ("Business of Fashion", "rss"),
    ("Red Carpet Fashion Awards", "rss"),
    ("PurseBlog", "rss"),
    ("GDELT Luxury Fashion", "gdelt"),
    ("GDELT Celebrity Style", "gdelt"),
    ("GDELT Bags Shoes Products", "gdelt"),
    ("GDELT Emerging Designers", "gdelt"),
    ("GDELT Runway Fashion Week", "gdelt"),
    ("GDELT Designer Brand Momentum", "gdelt"),
    ("GDELT Retail Resale Fashion", "gdelt"),
    ("GDELT Footwear Sneakers", "gdelt"),
    ("GDELT Creative Director Moves", "gdelt"),
    ("GDELT Beauty Fashion Crossover", "gdelt"),
]
```

The exact RSS URL map is:

```python
CANONICAL_PUBLIC_RSS_URLS = {
    "Fashionista": "https://fashionista.com/.rss/feed/28e21eb8-20ac-4617-a448-e845081591ca.xml",
    "Fashion Week Daily": "https://fashionweekdaily.com/feed/",
    "FashionUnited": "https://fashionunited.info/rss-news",
    "The Industry Fashion": "https://www.theindustry.fashion/feed/",
    "Highsnobiety": "https://www.highsnobiety.com/feeds/rss",
    "WWD": "https://wwd.com/feed/",
    "Vogue": "https://www.vogue.com/feed/rss",
    "Business of Fashion": "https://www.businessoffashion.com/arc/outboundfeeds/rss/",
    "Red Carpet Fashion Awards": "https://www.redcarpet-fashionawards.com/feed/",
    "PurseBlog": "https://www.purseblog.com/feed/",
}
```

## Tasks

### Task 1: Write RED Docs Test For RSS Inventory

**Files:**

- Modify: `tests/test_source_packs_docs.py`
- Later modify: `docs/source-packs.md`

- [ ] **Step 1: Add RSS source helper**

In `tests/test_source_packs_docs.py`, add:

```python
def _public_pack_source_names_by_type(source_type: str) -> list[str]:
    data = yaml.safe_load(PUBLIC_SOURCE_PACK.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    sources = data.get("sources")
    assert isinstance(sources, list)

    names: list[str] = []
    for source in sources:
        assert isinstance(source, dict)
        if source.get("type") == source_type:
            name = source.get("name")
            assert isinstance(name, str)
            names.append(name)
    return names
```

Then replace `_public_pack_gdelt_source_names()` with:

```python
def _public_pack_gdelt_source_names() -> list[str]:
    return _public_pack_source_names_by_type("gdelt")


def _public_pack_rss_source_names() -> list[str]:
    return _public_pack_source_names_by_type("rss")
```

- [ ] **Step 2: Add failing RSS docs test**

Add:

```python
def test_source_packs_docs_list_public_rss_sources_in_pack_order() -> None:
    section = _section(_read_source_packs_doc(), "RSS Feeds")
    documented_rss_sources = _backticked_bullet_values(section)

    assert documented_rss_sources == _public_pack_rss_source_names()
```

- [ ] **Step 3: Run RED docs test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_source_packs_docs.py::test_source_packs_docs_list_public_rss_sources_in_pack_order -q
```

Expected: FAIL because `docs/source-packs.md` does not yet contain a `## RSS Feeds` section.

### Task 2: Tighten Public Pack Offline Contract Tests

**Files:**

- Modify: `tests/test_source_packs.py`
- Modify: `tests/test_config.py`

- [ ] **Step 1: Tighten lint test**

Replace `test_lint_repository_public_pack_has_no_errors()` in `tests/test_source_packs.py` with:

```python
def test_lint_repository_public_pack_matches_composition_contract() -> None:
    result = lint_source_pack(Path("configs/source-packs/fashion-public.example.yaml"))

    assert result.error_count == 0
    assert result.warning_count == 0
    assert result.info_count == 0
    assert result.ok is True
    assert result.source_count == 20
    assert result.enabled_count == 20
    assert result.disabled_count == 0
    assert result.type_counts == {"gdelt": 10, "rss": 10}
    assert result.findings == []
```

- [ ] **Step 2: Add constants and raw YAML helper to `tests/test_config.py`**

Add `import yaml`.

Replace `CANONICAL_PUBLIC_RSS_URLS` with the full ten-source map from
`Expected Public Pack Composition`.

Add:

```python
# Copy EXPECTED_PUBLIC_SOURCE_COMPOSITION from the canonical block above.


def public_pack_raw_sources() -> list[dict[str, object]]:
    data = yaml.safe_load(
        Path("configs/source-packs/fashion-public.example.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert isinstance(data, dict)
    sources = data["sources"]
    assert isinstance(sources, list)
    return sources
```

- [ ] **Step 3: Add exact composition test**

Add near `test_public_fashion_source_pack_loads()`:

```python
def test_public_fashion_source_pack_composition_matches_contract() -> None:
    config = load_source_config(Path("configs/source-packs/fashion-public.example.yaml"))

    assert [(source.name, source.type.value) for source in config.sources] == (
        EXPECTED_PUBLIC_SOURCE_COMPOSITION
    )
    assert all(source.enabled is True for source in config.sources)
```

- [ ] **Step 4: Add explicit raw YAML boundary test**

Add:

```python
def test_public_fashion_source_pack_keeps_fetch_boundaries_explicit() -> None:
    for source in public_pack_raw_sources():
        source_type = source["type"]

        if source_type == "rss":
            assert source.get("article") == {"enabled": False}
            assert "url" in source
            assert "query" not in source

        if source_type == "gdelt":
            assert source.get("gdelt") == {
                "lookback_hours": 24,
                "max_records": 100,
                "rate_limit_per_second": 1.0,
            }
            assert "query" in source
            assert "url" not in source
```

- [ ] **Step 5: Change RSS endpoint test to exact equality**

Replace:

```python
for source_name, expected_url in CANONICAL_PUBLIC_RSS_URLS.items():
    assert urls_by_name[source_name] == expected_url
```

with:

```python
assert urls_by_name == CANONICAL_PUBLIC_RSS_URLS
```

- [ ] **Step 6: Run focused contract tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_source_packs.py::test_lint_repository_public_pack_matches_composition_contract \
  tests/test_config.py::test_public_fashion_source_pack_loads \
  tests/test_config.py::test_public_fashion_source_pack_composition_matches_contract \
  tests/test_config.py::test_public_fashion_source_pack_keeps_fetch_boundaries_explicit \
  tests/test_config.py::test_public_fashion_source_pack_uses_direct_rss_endpoints \
  -q
```

Expected: PASS because the current YAML already matches the intended contract. These are contract-hardening tests over existing behavior, not production code.

### Task 3: Update Source Pack Docs

**Files:**

- Modify: `docs/source-packs.md`
- Test: `tests/test_source_packs_docs.py`

- [ ] **Step 1: Expand public pack overview**

In `docs/source-packs.md`, update the Public Fashion Pack section after the source type bullets to include:

```markdown
Current composition:

- 20 enabled sources.
- 10 RSS feeds followed by 10 GDELT query lanes.
- RSS article extraction disabled by default for every RSS source.
- GDELT lanes explicitly bounded to a 24-hour lookback, 100 max records, and
  one request per second.
```

- [ ] **Step 2: Add RSS Feeds section**

Add before `## Check Pack Quality`:

```markdown
## RSS Feeds

The RSS entries are listed in pack order:

- `Fashionista`: general fashion media and industry news.
- `Fashion Week Daily`: fashion media and celebrity style.
- `FashionUnited`: fashion industry and retail news.
- `The Industry Fashion`: brand and industry news.
- `Highsnobiety`: streetwear and culture signals.
- `WWD`: trade media and industry news.
- `Vogue`: runway, fashion week, and celebrity style.
- `Business of Fashion`: trade, luxury, retail, and emerging-designer coverage.
- `Red Carpet Fashion Awards`: celebrity red-carpet styling.
- `PurseBlog`: bags, handbags, accessories, and luxury product signals.
```

Each bullet must contain only one backticked source name so the existing docs helper can parse it.

- [ ] **Step 3: Expand boundary docs test**

In `test_source_packs_docs_keep_public_pack_source_boundary()`, add phrases:

```python
"20 enabled sources",
"10 rss feeds followed by 10 gdelt query lanes",
"rss article extraction disabled by default",
"24-hour lookback",
"100 max records",
"one request per second",
```

- [ ] **Step 4: Run docs tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_source_packs_docs.py -q
```

Expected: all source-pack docs tests pass.

### Task 4: Update Changelog And Review Artifacts

**Files:**

- Modify: `CHANGELOG.md`
- Add: `docs/reviews/opencode-stage-204-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-204-code-review.md`
- Add: `docs/reviews/opencode-stage-204-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-204-release-review.md`

- [ ] **Step 1: Add changelog entry**

Add under `## [Unreleased]` / `### Added`:

```markdown
- Stage 204 pins the optional public fashion source pack's offline composition
  contract in tests and docs: 20 enabled sources, 10 RSS feeds, 10 bounded GDELT
  lanes, and RSS article extraction disabled by default. It does not add
  sources, live liveness gates, scraping, social/platform connectors, demand
  proof, coverage verification, dependency changes, or compliance-review
  behavior.
```

- [ ] **Step 2: Run focused stage tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_source_packs.py tests/test_config.py tests/test_source_packs_docs.py tests/test_source_pack_quality_docs.py -q
```

- [ ] **Step 3: Run source-pack lint CLI**

Run:

```bash
uv --no-config run --frozen fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --strict
uv --no-config run --frozen fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --format json
```

Expected: strict lint has no errors/warnings/info; JSON shows 20 sources, 20 enabled, `{"gdelt": 10, "rss": 10}`, and empty findings.

- [ ] **Step 4: Run code review**

Create `docs/reviews/opencode-stage-204-code-review-prompt.md`, run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-204-code-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-204-code-review.md
rm -f "$tmp_review"
```

Clean the captured review artifact so it contains one coherent review body and no tool chatter. Fix any Critical or Important findings.

### Task 5: Release Verification, Review, Commit, Push

**Files:**

- All Stage 204 files.

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

Create `docs/reviews/opencode-stage-204-release-review-prompt.md`, run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-204-release-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-204-release-review.md
rm -f "$tmp_review"
```

Clean the captured review artifact. Fix any Critical or Important findings, then rerun relevant verification and rereview.

- [ ] **Step 3: Commit and push**

Run:

```bash
git status --short --untracked-files=all
git add tests/test_source_packs.py tests/test_config.py tests/test_source_packs_docs.py docs/source-packs.md CHANGELOG.md docs/superpowers/plans/2026-06-25-stage-204-public-source-pack-composition-contracts-plan.md docs/reviews/opencode-stage-204-*.md
git commit -m "Stage 204: pin public source pack composition"
git push origin main
git status --short --branch --untracked-files=all
```

## Self-Review

- Spec coverage: The plan pins the public pack composition, RSS inventory docs, GDELT boundary settings, lint cleanliness, and exact RSS endpoint map.
- Placeholder scan: No TBD/TODO/fill-in placeholders remain.
- Scope check: This is one offline contract-hardening stage. It deliberately avoids source additions, live checks, connectors, scraping, dependency changes, and product runtime behavior changes.
- TDD note: The RSS docs test should fail before docs are updated. The exact YAML contract tests may pass immediately because they codify existing intended repository state; they are still useful release guards for future source-pack edits. Do not force RED by temporarily editing the source-pack YAML.

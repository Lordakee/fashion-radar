# Stage 14 Entity Watchlist Pack Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an optional static fashion entity watchlist pack so users can start with broader local tracking coverage for designer brands, products, categories, designers, celebrities, and style terms.

**Architecture:** Do not change runtime code. Add a complete `EntityConfig` YAML pack under `configs/entity-packs/`, focused tests that load it through the existing config validator, and docs that explain copy/edit/use workflow. Keep the default packaged starter config unchanged.

**Tech Stack:** YAML, existing Pydantic entity config models, pytest, Typer existing `doctor/init` docs, Markdown, ruff, uv.

---

## Scope Guard

Stage 14 must not add or document:

- social/platform connectors, platform search, remote community ingestion, or
  automated social collection;
- web scraping, crawler development, browser automation, Playwright, Selenium,
  MCP platform scraping servers, account automation, or source-acquisition
  workflows;
- login cookies, account/session files, browser profiles, tokens, credentials,
  proxy pools, fingerprint evasion, CAPTCHA/rate-limit/access-control/paywall
  bypass;
- official or unofficial social platform APIs;
- instructions for obtaining platform/community exports;
- current hotness claims, platform-wide claims, market-wide trend proof,
  verified demand outside the configured source set, real-time monitoring, or
  top social trend rankings;
- Google News RSS or any new source type;
- paid API requirements, LLM scoring, embeddings, vector databases, image
  recognition, or sentiment analysis;
- DB migrations, source-health changes, collector changes, dashboard changes,
  report semantics changes, or scoring algorithm changes;
- a product-facing compliance review, audit workflow, safety workflow, approval
  UI, policy checklist, or legal review feature.

## Developer Operations Boundary

Commit, push, dependency-index checks, alternate-index checks, package builds,
and installed-wheel smoke tests are development/release operations only. They
are not part of the Stage 14 entity-pack architecture, runtime behavior, or
acceptance criteria. The implementation tasks must stay focused on the static
pack, tests, and docs.

## File Structure

- Create `configs/entity-packs/fashion-watchlist.example.yaml`: complete
  optional `EntityConfig` seed pack.
- Create `tests/test_entity_packs.py`: tests for pack loading, structure,
  expected examples, parent brands, existing matcher guardrails, and narrow
  category aliases.
- Create `docs/entity-packs.md`: user docs for copying/editing/running the pack.
- Modify `README.md`: link the entity-pack docs and show one copy/doctor command.
- Modify `docs/architecture.md`: mention optional entity packs under config.
- Modify `docs/source-boundaries.md`: describe entity packs as local config, not
  source collection.
- Modify `CHANGELOG.md`: record the new optional entity watchlist pack.

## Task 1: Write Failing Entity-Pack Tests

**Files:**
- Create: `tests/test_entity_packs.py`

- [ ] **Step 1: Add focused failing tests**

Create `tests/test_entity_packs.py`:

```python
from pathlib import Path

from fashion_radar.extract.entities import evaluate_entity_matches, match_entities
from fashion_radar.extract.text import normalize_alias_key
from fashion_radar.models.entity import EntityDefinition, EntityType
from fashion_radar.settings import UNSAFE_COMMON_ALIASES, load_entity_config


PACK_PATH = Path("configs/entity-packs/fashion-watchlist.example.yaml")


def _entities() -> list[EntityDefinition]:
    return load_entity_config(PACK_PATH).entities


def _entities_by_name() -> dict[str, EntityDefinition]:
    return {entity.name: entity for entity in _entities()}


def test_fashion_watchlist_entity_pack_loads() -> None:
    config = load_entity_config(PACK_PATH)

    assert config.version == 1
    assert len(config.entities) >= 24


def test_fashion_watchlist_entity_pack_has_expected_type_mix() -> None:
    config = load_entity_config(PACK_PATH)
    type_counts = {
        entity_type: sum(1 for entity in config.entities if entity.type == entity_type)
        for entity_type in EntityType
    }

    assert type_counts[EntityType.BRAND] >= 8
    assert type_counts[EntityType.PRODUCT] >= 6
    assert type_counts[EntityType.CATEGORY] >= 4
    assert type_counts[EntityType.DESIGNER] >= 2
    assert type_counts[EntityType.CELEBRITY] >= 2
    assert type_counts[EntityType.TREND] >= 3


def test_fashion_watchlist_entity_pack_includes_requested_watchlist_examples() -> None:
    entities = _entities_by_name()

    for name in [
        "The Row",
        "Khaite",
        "Alaia",
        "Loewe",
        "Alaia Le Teckel",
        "Miu Miu Arcadie",
        "Mary Jane Shoes",
        "East-West Bags",
    ]:
        assert name in entities


def test_fashion_watchlist_products_reference_existing_parent_brands() -> None:
    config = load_entity_config(PACK_PATH)
    brand_names = {entity.name for entity in config.entities if entity.type == EntityType.BRAND}

    for entity in config.entities:
        if entity.type == EntityType.PRODUCT:
            assert entity.parent_brand in brand_names


def test_fashion_watchlist_high_risk_aliases_use_existing_guardrails_or_narrow_phrases() -> None:
    entities = _entities_by_name()

    assert entities["Coach"].context_terms
    assert entities["Ballet Flats"].context_terms
    assert {alias.value for alias in entities["Mary Jane Shoes"].aliases} == {
        "Mary Jane shoes",
        "Mary Janes",
        "Mary Jane flats",
    }
    assert {alias.value for alias in entities["Boat Shoes"].aliases} == {
        "boat shoes",
        "boat shoe",
    }


def test_fashion_watchlist_all_single_word_and_common_aliases_are_guarded() -> None:
    for entity in _entities():
        for alias in entity.aliases:
            key = normalize_alias_key(alias.value)
            if len(key.split()) == 1 or key in UNSAFE_COMMON_ALIASES:
                assert alias.safe_single_word or entity.context_terms, (
                    f"{entity.name!r} alias {alias.value!r} needs context or safe reason"
                )
                if alias.safe_single_word:
                    assert alias.reason


def test_fashion_watchlist_matcher_rejects_generic_broad_alias_mentions() -> None:
    entities = _entities()

    generic_texts = [
        ("The row after the show was empty.", "The Row"),
        ("The coach gave a speech after practice.", "Coach"),
        ("Margaux joined the dinner list.", "The Row Margaux"),
        ("Arcadie appeared in the novel title.", "Miu Miu Arcadie"),
    ]
    for text, entity_name in generic_texts:
        decisions = [
            decision
            for decision in evaluate_entity_matches(text, entities)
            if decision.entity_name == entity_name
        ]
        assert decisions, f"Expected an evaluated decision for {entity_name!r}"
        assert all(not decision.accepted for decision in decisions)


def test_fashion_watchlist_matcher_accepts_parent_brand_or_fashion_context() -> None:
    entities = _entities()

    accepted_names = {
        decision.entity_name
        for decision in match_entities(
            "The Row Margaux tote, Miu Miu Arcadie bag, Coach Tabby handbag, "
            "Mary Jane flats, and boat shoes appeared in the runway footwear report.",
            entities,
        )
    }

    assert {
        "The Row Margaux",
        "Miu Miu Arcadie",
        "Coach",
        "Mary Jane Shoes",
        "Boat Shoes",
    } <= accepted_names


def test_default_packaged_entity_config_stays_small_and_loadable() -> None:
    root_config = load_entity_config(Path("configs/entities.example.yaml"))
    packaged_config = load_entity_config(
        Path("src/fashion_radar/templates/configs/entities.example.yaml")
    )

    expected_names = [
        "The Row",
        "Miu Miu",
        "Jonathan Anderson",
        "Zendaya",
        "The Row Margaux",
        "Ballet Flats",
        "Quiet Luxury",
    ]

    assert root_config.model_dump(mode="json") == packaged_config.model_dump(mode="json")
    assert [entity.name for entity in root_config.entities] == expected_names
```

- [ ] **Step 2: Run focused test and verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_entity_packs.py -q
```

Expected: FAIL because `configs/entity-packs/fashion-watchlist.example.yaml`
does not exist yet.

## Task 2: Add Optional Entity Watchlist Pack

**Files:**
- Create: `configs/entity-packs/fashion-watchlist.example.yaml`
- Test: `tests/test_entity_packs.py`

- [ ] **Step 1: Create the YAML pack**

Create `configs/entity-packs/fashion-watchlist.example.yaml` with:

```yaml
# Optional broader fashion watchlist. Copy to configs/entities.yaml and edit for
# your own research. This is a seed list, not a ranking or hot-list.
version: 1
entities:
  - name: The Row
    type: brand
    aliases:
      - value: The Row
    context_terms: [margaux, luxury, olsen, handbag, runway]
    tags: [luxury, minimalism, designer_brand]
    initial_weight: 1.1
    active_from: "2024-01-01T00:00:00Z"
  - name: Miu Miu
    type: brand
    aliases:
      - value: Miu Miu
      - value: MiuMiu
        safe_single_word: true
        reason: Compact spelling of the Miu Miu brand name.
    tags: [luxury, prada_group, designer_brand]
    initial_weight: 1.1
    active_from: "2024-01-01T00:00:00Z"
  - name: Khaite
    type: brand
    aliases:
      - value: Khaite
        safe_single_word: true
        reason: Distinct fashion brand name.
    tags: [designer_brand, contemporary_luxury]
    active_from: "2024-01-01T00:00:00Z"
  - name: Toteme
    type: brand
    aliases:
      - value: Toteme
        safe_single_word: true
        reason: Distinct fashion brand name.
    tags: [designer_brand, minimalism]
    active_from: "2024-01-01T00:00:00Z"
  - name: Alaia
    type: brand
    aliases:
      - value: Alaia
        safe_single_word: true
        reason: Distinct fashion brand name, ASCII form of the accented brand name.
    tags: [luxury, designer_brand]
    active_from: "2024-01-01T00:00:00Z"
  - name: Loewe
    type: brand
    aliases:
      - value: Loewe
        safe_single_word: true
        reason: Distinct fashion brand name.
    tags: [luxury, lvmh, designer_brand]
    active_from: "2024-01-01T00:00:00Z"
  - name: Jacquemus
    type: brand
    aliases:
      - value: Jacquemus
        safe_single_word: true
        reason: Distinct fashion brand name.
    tags: [designer_brand, contemporary_luxury]
    active_from: "2024-01-01T00:00:00Z"
  - name: Tory Burch
    type: brand
    aliases:
      - value: Tory Burch
    tags: [designer_brand, accessories]
    active_from: "2024-01-01T00:00:00Z"
  - name: Coach
    type: brand
    aliases:
      - value: Coach
    context_terms: [bag, handbag, tabby, leather, runway]
    tags: [accessories, american_fashion]
    active_from: "2024-01-01T00:00:00Z"
  - name: Sandy Liang
    type: brand
    aliases:
      - value: Sandy Liang
    context_terms: [fashion, runway, bow, ballet]
    tags: [designer_brand, new_york]
    active_from: "2024-01-01T00:00:00Z"

  - name: Jonathan Anderson
    type: designer
    aliases:
      - value: Jonathan Anderson
      - value: JW Anderson
    tags: [creative_director]
    active_from: "2024-01-01T00:00:00Z"
  - name: Pieter Mulier
    type: designer
    aliases:
      - value: Pieter Mulier
    tags: [creative_director]
    active_from: "2024-01-01T00:00:00Z"

  - name: Zendaya
    type: celebrity
    aliases:
      - value: Zendaya
        safe_single_word: true
        reason: Distinct public figure name.
    tags: [red_carpet, celebrity_style]
    active_from: "2024-01-01T00:00:00Z"
  - name: Bella Hadid
    type: celebrity
    aliases:
      - value: Bella Hadid
    tags: [celebrity_style, street_style]
    active_from: "2024-01-01T00:00:00Z"

  - name: The Row Margaux
    type: product
    parent_brand: The Row
    aliases:
      - value: The Row Margaux
      - value: Margaux
    context_terms: [the row, handbag, tote, bag]
    category_tags: [bag, handbag, tote]
    active_from: "2024-01-01T00:00:00Z"
  - name: Alaia Le Teckel
    type: product
    parent_brand: Alaia
    aliases:
      - value: Alaia Le Teckel
      - value: Le Teckel
    context_terms: [alaia, bag, shoulder bag, handbag]
    category_tags: [bag, shoulder_bag]
    active_from: "2024-01-01T00:00:00Z"
  - name: Miu Miu Arcadie
    type: product
    parent_brand: Miu Miu
    aliases:
      - value: Miu Miu Arcadie
      - value: Arcadie
    context_terms: [miu miu, bag, handbag]
    category_tags: [bag, handbag]
    active_from: "2024-01-01T00:00:00Z"
  - name: Loewe Puzzle Bag
    type: product
    parent_brand: Loewe
    aliases:
      - value: Loewe Puzzle
      - value: Puzzle Bag
    context_terms: [loewe, bag, handbag]
    category_tags: [bag, handbag]
    active_from: "2024-01-01T00:00:00Z"
  - name: Khaite Lotus Bag
    type: product
    parent_brand: Khaite
    aliases:
      - value: Khaite Lotus
      - value: Lotus Bag
    context_terms: [khaite, bag, handbag]
    category_tags: [bag, handbag]
    active_from: "2024-01-01T00:00:00Z"
  - name: Tory Burch Pierced Mule
    type: product
    parent_brand: Tory Burch
    aliases:
      - value: Tory Burch Pierced Mule
      - value: Pierced Mule
    context_terms: [tory burch, mule, shoe, footwear]
    category_tags: [shoe, mule]
    active_from: "2024-01-01T00:00:00Z"

  - name: Ballet Flats
    type: category
    aliases:
      - value: ballet flats
      - value: ballet flat
    context_terms: [shoes, footwear, mary jane, runway]
    category_tags: [shoes, flats]
    active_from: "2024-01-01T00:00:00Z"
  - name: Mary Jane Shoes
    type: category
    aliases:
      - value: Mary Jane shoes
      - value: Mary Janes
      - value: Mary Jane flats
    context_terms: [shoes, footwear, flats, runway]
    category_tags: [shoes, flats]
    active_from: "2024-01-01T00:00:00Z"
  - name: East-West Bags
    type: category
    aliases:
      - value: east-west bag
      - value: east-west bags
      - value: east west tote
    context_terms: [bag, handbag, tote]
    category_tags: [bag, tote]
    active_from: "2024-01-01T00:00:00Z"
  - name: Boat Shoes
    type: category
    aliases:
      - value: boat shoes
      - value: boat shoe
    context_terms: [footwear, loafer, runway, styling]
    category_tags: [shoes]
    active_from: "2024-01-01T00:00:00Z"
  - name: Suede Sneakers
    type: category
    aliases:
      - value: suede sneakers
      - value: suede sneaker
    context_terms: [footwear, shoes, trainer]
    category_tags: [shoes, sneakers]
    active_from: "2024-01-01T00:00:00Z"

  - name: Quiet Luxury
    type: trend
    aliases:
      - value: quiet luxury
      - value: stealth wealth
    tags: [aesthetic, consumer_trend]
    active_from: "2024-01-01T00:00:00Z"
  - name: Boho Revival
    type: trend
    aliases:
      - value: boho revival
      - value: boho chic
    tags: [aesthetic, styling]
    active_from: "2024-01-01T00:00:00Z"
  - name: Office Siren
    type: trend
    aliases:
      - value: office siren
    tags: [aesthetic, styling]
    active_from: "2024-01-01T00:00:00Z"
```

- [ ] **Step 2: Run focused tests and verify GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_entity_packs.py -q
```

Expected: PASS.

## Task 3: Add Entity Pack Documentation

**Files:**
- Create: `docs/entity-packs.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/source-boundaries.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Create docs**

Create `docs/entity-packs.md` with:

- purpose and boundary of optional entity packs;
- copy command:

```bash
cp configs/entity-packs/fashion-watchlist.example.yaml configs/entities.yaml
uv run fashion-radar doctor --config-dir "$PWD/configs"
```

- workflow commands after an existing configured-source or local-signal pipeline
  has already produced signals:

```bash
uv run fashion-radar match --config-dir "$PWD/configs"
uv run fashion-radar report --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar candidates --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar trends --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

- boundary wording beside the workflow commands:
  - the entity pack only changes local entity matching;
  - commands use `--config-dir "$PWD/configs"` so they read the copied pack
    instead of a platform default user config directory;
  - the entity-pack guide does not introduce `collect`, source setup, source
    acquisition, platform/community ingestion, scraping, social monitoring,
    current-hotness detection, or ranking semantics;
  - source collection remains documented in existing source workflow docs, not
    in the entity-pack guide;
- explanation that the pack is a seed watchlist, not a hot-list/ranking;
- editing guidance for aliases, context terms, parent brands, and weights;
- matcher semantics wording:
  - existing matching uses context gates for product aliases with
    `parent_brand`, single-word aliases, and aliases listed as unsafe/common by
    the application;
  - `context_terms` are not a universal phrase-level disambiguation system for
    every multi-word category or trend alias;
  - for other multi-word category or trend aliases, use narrower aliases where
    possible;
  - multi-word category aliases such as `Mary Janes` or `boat shoes` may match
    in a retained fashion corpus without context gating; remove or narrow them
    if they are noisy for a user's source set;
- note that candidate discovery can surface untracked phrases even when they
  are not in the pack.
- note how to revert to the default starter by restoring
  `configs/entities.example.yaml` from git or copying the packaged starter from
  `src/fashion_radar/templates/configs/entities.example.yaml`.

- [ ] **Step 2: Update existing docs**

Add concise links/mentions:

- `README.md`: configuration section links `docs/entity-packs.md` and shows one
  lint-free copy/doctor example.
- `docs/architecture.md`: config component mentions optional entity packs.
- `docs/source-boundaries.md`: entity packs are local config only and do not add
  collection.
- `CHANGELOG.md`: add Unreleased bullet.

- [ ] **Step 3: Run wording guard**

Run:

```bash
rg -n "platform-wide|market-wide|verified demand|top social trend|real-time social monitoring|scraper|crawler|Playwright|Selenium|cookie|session|token|proxy|CAPTCHA|fingerprint|source-acquisition|hot-list|ranking" \
  docs/entity-packs.md README.md docs/architecture.md docs/source-boundaries.md CHANGELOG.md configs/entity-packs/fashion-watchlist.example.yaml
```

Expected: manually classify every match. Negative boundary wording for terms
such as `scraper`, `crawler`, `Playwright`, `Selenium`, `cookie`, `session`,
`token`, `proxy`, `CAPTCHA`, `fingerprint`, `hot-list`, or `ranking` is allowed
only when it says the entity pack does not provide that capability. Positive
platform/market claims, ranking claims, source-acquisition instructions, or
capability descriptions must be removed.

Run a targeted entity-pack acquisition guard:

```bash
rg -n "collect|source setup|source acquisition|platform ingestion|community ingestion|scraping|crawler" docs/entity-packs.md
```

Expected: no matches in workflow instructions. If `collect` appears, it must be
only in a negative boundary statement saying the entity-pack guide does not add
or document collection workflows.

## Task 4: Implementation Verification And Claude Code Review

**Files:**
- Create: `docs/reviews/claude-code-stage-14-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-14-code-review.md`

These review files are staged-workflow process artifacts. They are not
product/runtime files and are not part of the entity-pack behavior.

- [ ] **Step 1: Run implementation verification**

Run:

```bash
git diff --check
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
codegraph status
```

`codegraph status` is a local developer-environment check for this repo, not a
portable GitHub CI requirement.

- [ ] **Step 2: Request Claude Code review**

Create and run a code-review prompt with:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-14-code-review-prompt.md | tee docs/reviews/claude-code-stage-14-code-review.md
```

The code-review prompt must repeat the read-only constraints: no edits, no
network, no collectors, no directory creation, no SQLite, and no
platform/social/community tooling. It must also state that review prompt/output
files are staged-process metadata, not product/runtime behavior or package
functionality. Fix Critical/Important findings before release handoff.

- [ ] **Step 3: Static release-readiness handoff**

After verification and Claude Code approval, inspect status and perform
secret/generated-artifact sanity checks:

```bash
git status --short
git ls-files -o --exclude-standard
rg -n "ghp_|github_pat|BEGIN .*PRIVATE|password\\s*=|secret\\s*=|api[_-]?key\\s*=|access[_-]?token\\s*=" README.md CHANGELOG.md docs configs tests src pyproject.toml uv.lock || true
```

Commit and GitHub upload are release operations outside the Stage 14
implementation architecture. Only commit/push after explicit user authorization
for the active implementation session. Keep the remote URL token-free and use
only temporary askpass credentials if HTTPS auth is required.

## Optional Downstream Release Operations

The following checks are optional downstream release operations. They are not
part of Stage 14 implementation or acceptance because this stage changes only
static YAML, tests, and docs:

```bash
uv lock --check --default-index https://pypi.org/simple
uv sync --locked --dev --check --default-index https://pypi.org/simple
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
uv build --out-dir /tmp/fashion-radar-dist-stage14
```

Optional installed-wheel smoke, if a release coordinator chooses to run it:

```bash
tmpdir="$(mktemp -d)"
wheel="$(find /tmp/fashion-radar-dist-stage14 -maxdepth 1 -name 'fashion_radar-*.whl' | sort | tail -1)"
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv venv "$tmpdir/venv"
env -u PYTHONPATH UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple \
  uv pip install --python "$tmpdir/venv/bin/python" "$wheel"
(
  cd "$tmpdir"
  env -u PYTHONPATH "$tmpdir/venv/bin/fashion-radar" --help >/tmp/fashion-radar-stage14-help.txt
  env -u PYTHONPATH "$tmpdir/venv/bin/fashion-radar" doctor --help >/tmp/fashion-radar-stage14-doctor-help.txt
  env -u PYTHONPATH "$tmpdir/venv/bin/fashion-radar" match --help >/tmp/fashion-radar-stage14-match-help.txt
  env -u PYTHONPATH "$tmpdir/venv/bin/fashion-radar" candidates --help >/tmp/fashion-radar-stage14-candidates-help.txt
  env -u PYTHONPATH "$tmpdir/venv/bin/python" -c "import fashion_radar.settings; import fashion_radar.extract.entities"
)
rm -rf "$tmpdir"
```

## Acceptance Criteria

- Optional entity watchlist pack loads through the existing config validator.
- Default small starter `entities.example.yaml` and packaged template stay
  unchanged and loadable.
- Pack includes broader coverage for designer brands, products, categories,
  designers, celebrities, and style terms.
- High-risk aliases use existing matcher guardrails or intentionally narrow
  aliases.
- Docs frame the pack as a local seed watchlist, not a ranking, platform-wide
  signal, or market-wide demand claim.
- No runtime code, dependency, DB schema, collector, report, dashboard, source
  pack, or lockfile change is required.

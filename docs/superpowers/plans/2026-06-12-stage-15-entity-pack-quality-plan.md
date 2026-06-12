# Stage 15 Entity Pack Quality Diagnostics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `fashion-radar entity-pack-lint`, a pure local diagnostics command for entity YAML files and optional entity packs.

**Architecture:** Add a new `entity_packs.py` diagnostics module that mirrors `source_packs.py` without sharing abstractions yet. The module reads raw YAML, validates through `load_entity_config()`, derives deterministic counts/findings from the local file, and returns table or JSON through a flat Typer command. The command has no config/data/report directory options and does not call matching, scoring, collectors, SQLite, network, or platform tooling.

**Tech Stack:** Python 3.12, Typer, Pydantic v2, PyYAML, existing entity config and matcher helper functions, pytest, ruff, uv.

---

## Scope Guard

Stage 15 must not add or document:

- social/platform connectors, platform search, automated community ingestion, or
  source acquisition;
- scraping, crawler development, browser automation, Playwright, Selenium, MCP
  platform scraping servers, account automation, unofficial platform APIs, or
  export-acquisition instructions;
- login cookies, account/session files, browser profiles, tokens, credentials,
  proxy pools, fingerprint evasion, CAPTCHA/rate-limit/access-control/paywall
  bypass;
- current-hotness claims, platform-wide claims, social-wide claims, market-wide
  trend proof, verified demand outside configured local signals, real-time
  monitoring, or top social trend rankings;
- Google News RSS or any new source type;
- DB migrations, source-health changes, collector changes, dashboard changes,
  report semantics changes, matcher behavior changes, or scoring algorithm
  changes;
- product-facing compliance review, audit workflow, safety workflow, approval
  UI, policy checklist, or legal review feature.

## File Structure

- Create `src/fashion_radar/entity_packs.py`: entity-pack diagnostics models,
  linter, matcher-rule helpers, deterministic table rendering.
- Create `tests/test_entity_pack_lint.py`: focused module tests.
- Modify `src/fashion_radar/cli.py`: import linter API, add output format alias,
  add `entity-pack-lint` command near `source-pack-lint`.
- Modify `tests/test_cli.py`: CLI coverage mirroring source-pack lint tests.
- Create `docs/entity-pack-quality.md`: user documentation.
- Modify `docs/entity-packs.md`: link lint command before copy/edit workflow.
- Modify `README.md`: add short command and docs link.
- Modify `docs/architecture.md`: mention optional local entity-pack linting.
- Modify `CHANGELOG.md`: add Stage 15 bullet.

## Task 1: Add Focused Failing Entity-Pack Lint Tests

**Files:**
- Create: `tests/test_entity_pack_lint.py`

- [ ] **Step 1: Create test helpers and repository pack smoke test**

Create `tests/test_entity_pack_lint.py` with helpers:

```python
import json
from pathlib import Path
from textwrap import dedent

from fashion_radar.entity_packs import (
    EntityPackFindingSeverity,
    lint_entity_pack,
    render_entity_pack_lint_table,
)


def write_yaml(path: Path, content: str) -> Path:
    path.write_text(dedent(content).strip() + "\n", encoding="utf-8")
    return path


def finding_codes(result) -> list[str]:
    return [finding.code for finding in result.findings]


def findings_by_code(result, code: str):
    return [finding for finding in result.findings if finding.code == code]


def test_lint_repository_watchlist_pack_has_no_errors() -> None:
    result = lint_entity_pack(Path("configs/entity-packs/fashion-watchlist.example.yaml"))

    assert result.error_count == 0
    assert result.ok is True
    assert result.entity_count >= 24
    assert result.alias_count >= result.entity_count
    assert "brand" in result.type_counts
    assert "product" in result.type_counts
    assert result.product_parent_gated_aliases > 0
```

This smoke test intentionally permits advisory warnings. The public watchlist
pack may include broad category/trend aliases that are useful starter examples
but should still be visible to users before they run with `--strict`.

- [ ] **Step 2: Run the focused test and verify it fails**

Run:

```bash
.venv/bin/python -m pytest tests/test_entity_pack_lint.py::test_lint_repository_watchlist_pack_has_no_errors -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'fashion_radar.entity_packs'`.

- [ ] **Step 3: Add invalid, empty, alias, and normalized-key tests**

Append tests:

```python
def test_invalid_entity_config_returns_error_finding(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: Broken
            type: brand
        """,
    )

    result = lint_entity_pack(path)

    finding = findings_by_code(result, "invalid_config")[0]
    assert result.error_count == 1
    assert finding.severity == EntityPackFindingSeverity.ERROR
    assert "Invalid entity config" in finding.message


def test_empty_entity_pack_is_error(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities: []
        """,
    )

    result = lint_entity_pack(path)

    finding = findings_by_code(result, "empty_entity_pack")[0]
    assert result.ok is False
    assert finding.severity == EntityPackFindingSeverity.ERROR


def test_entity_without_aliases_is_error(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: Aliasless Brand
            type: brand
            aliases: []
            tags: [brand]
        """,
    )

    result = lint_entity_pack(path)

    finding = findings_by_code(result, "entity_without_aliases")[0]
    assert finding.severity == EntityPackFindingSeverity.ERROR
    assert finding.entity_name == "Aliasless Brand"
    assert finding.field == "aliases"


def test_empty_normalized_name_and_alias_are_errors(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: "!!!"
            type: brand
            aliases:
              - value: "???"
            tags: [brand]
        """,
    )

    result = lint_entity_pack(path)

    assert "name_normalizes_empty" in finding_codes(result)
    assert "alias_normalizes_empty" in finding_codes(result)
    assert result.error_count == 2
```

- [ ] **Step 4: Run the focused tests and verify they fail**

Run:

```bash
.venv/bin/python -m pytest tests/test_entity_pack_lint.py -q
```

Expected: FAIL because `fashion_radar.entity_packs` does not exist yet.

## Task 2: Implement Entity-Pack Diagnostics Module

**Files:**
- Create: `src/fashion_radar/entity_packs.py`
- Test: `tests/test_entity_pack_lint.py`

- [ ] **Step 1: Add the module skeleton, models, raw YAML loading, and public lint API**

Create `src/fashion_radar/entity_packs.py` with:

```python
from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field

from fashion_radar.extract.text import normalize_alias_key
from fashion_radar.models.entity import AliasDefinition, EntityDefinition, EntityType
from fashion_radar.settings import ConfigError, UNSAFE_COMMON_ALIASES, load_entity_config


class EntityPackFindingSeverity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class EntityPackFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    severity: EntityPackFindingSeverity
    code: str
    message: str
    entity_name: str | None = None
    alias: str | None = None
    field: str | None = None


class EntityPackLintResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    entity_count: int = 0
    alias_count: int = 0
    type_counts: dict[str, int] = Field(default_factory=dict)
    tag_counts: dict[str, int] = Field(default_factory=dict)
    category_tag_counts: dict[str, int] = Field(default_factory=dict)
    accepted_without_context_aliases: int = 0
    context_gated_aliases: int = 0
    safe_aliases: int = 0
    product_parent_gated_aliases: int = 0
    findings: list[EntityPackFinding] = Field(default_factory=list)

    @property
    def error_count(self) -> int:
        return _count_findings(self.findings, EntityPackFindingSeverity.ERROR)

    @property
    def warning_count(self) -> int:
        return _count_findings(self.findings, EntityPackFindingSeverity.WARNING)

    @property
    def info_count(self) -> int:
        return _count_findings(self.findings, EntityPackFindingSeverity.INFO)

    @property
    def ok(self) -> bool:
        return self.error_count == 0


def lint_entity_pack(path: Path) -> EntityPackLintResult:
    """Read and lint one local entity YAML file."""
    raw_data, raw_error = _read_raw_entity_config(path)
    if raw_error is not None:
        return EntityPackLintResult(path=str(path), findings=[raw_error])

    raw_entities = _raw_entities(raw_data)
    try:
        entity_config = load_entity_config(path)
    except ConfigError as exc:
        return EntityPackLintResult(
            path=str(path),
            entity_count=len(raw_entities),
            findings=[
                EntityPackFinding(
                    severity=EntityPackFindingSeverity.ERROR,
                    code="invalid_config",
                    message=str(exc),
                )
            ],
        )

    entities = entity_config.entities
    findings = _lint_entities(entities, raw_entities)
    gate_counts = _gate_counts(entities)
    return EntityPackLintResult(
        path=str(path),
        entity_count=len(entities),
        alias_count=sum(len(entity.aliases) for entity in entities),
        type_counts=dict(sorted(Counter(entity.type.value for entity in entities).items())),
        tag_counts=dict(sorted(Counter(tag for entity in entities for tag in entity.tags).items())),
        category_tag_counts=dict(
            sorted(
                Counter(
                    tag for entity in entities for tag in entity.category_tags
                ).items()
            )
        ),
        accepted_without_context_aliases=gate_counts["accepted_without_context_aliases"],
        context_gated_aliases=gate_counts["context_gated_aliases"],
        safe_aliases=gate_counts["safe_aliases"],
        product_parent_gated_aliases=gate_counts["product_parent_gated_aliases"],
        findings=_sort_findings(findings),
    )
```

- [ ] **Step 2: Add rendering and common helpers**

Append:

```python
def render_entity_pack_lint_table(result: EntityPackLintResult) -> list[str]:
    """Render a deterministic human-readable lint summary."""
    lines = [
        f"Entity pack: {result.path}",
        f"Entities: {result.entity_count} total",
        f"Aliases: {result.alias_count} total",
        f"Types: {_format_counts(result.type_counts)}",
        (
            f"Findings: {result.error_count} errors, {result.warning_count} warnings, "
            f"{result.info_count} info"
        ),
    ]
    if not result.findings:
        lines.append("No entity-pack quality findings.")
        return lines

    lines.append("Severity | Code | Entity | Alias | Field | Message")
    for finding in result.findings:
        lines.append(
            f"{finding.severity.value} | {finding.code} | "
            f"{finding.entity_name or 'n/a'} | {finding.alias or 'n/a'} | "
            f"{finding.field or 'n/a'} | {finding.message}"
        )
    return lines


def _read_raw_entity_config(path: Path) -> tuple[Mapping[str, Any], EntityPackFinding | None]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except OSError as exc:
        return {}, _invalid_config_finding(f"Could not read config {path}: {exc}")
    except yaml.YAMLError as exc:
        return {}, _invalid_config_finding(f"Invalid YAML in {path}: {exc}")

    if not isinstance(data, Mapping):
        return {}, _invalid_config_finding(f"Config {path} must contain a YAML mapping")
    return data, None


def _raw_entities(raw_data: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    raw_entities = raw_data.get("entities", [])
    if not isinstance(raw_entities, list):
        return []
    return [entity for entity in raw_entities if isinstance(entity, Mapping)]


def _invalid_config_finding(message: str) -> EntityPackFinding:
    return EntityPackFinding(
        severity=EntityPackFindingSeverity.ERROR,
        code="invalid_config",
        message=message,
    )


def _count_findings(
    findings: Sequence[EntityPackFinding],
    severity: EntityPackFindingSeverity,
) -> int:
    return sum(1 for finding in findings if finding.severity == severity)


def _format_counts(counts: Mapping[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))
```

- [ ] **Step 3: Add lint rules and matcher-gate helpers**

Implement `_lint_entities()`, `_entity_findings()`, `_alias_findings()`,
metadata-list checks, parent hierarchy checks, and gate-count helpers. The exact
codes, severities, and messages must match the Stage 15 design. Use
`normalize_alias_key()` and `UNSAFE_COMMON_ALIASES`; do not reimplement duplicate
alias/name or unknown-parent validation already covered by `load_entity_config()`.

Use this exact matcher-classification helper shape so diagnostics match
`extract/entities.py` branch order:

```python
class AliasGateKind(StrEnum):
    PRODUCT_PARENT_OR_CONTEXT = "product_parent_or_context"
    SAFE_ALIAS = "safe_alias"
    CONTEXT_REQUIRED = "context_required"
    ACCEPTED_WITHOUT_CONTEXT = "accepted_without_context"


def _alias_requires_context(alias: AliasDefinition) -> bool:
    key = normalize_alias_key(alias.value)
    return len(key.split()) == 1 or key in UNSAFE_COMMON_ALIASES


def _classify_alias_gate(entity: EntityDefinition, alias: AliasDefinition) -> AliasGateKind:
    if entity.type == EntityType.PRODUCT and entity.parent_brand:
        # This branch checks parent brand and product context first. It does not
        # consult safe_single_word.
        return AliasGateKind.PRODUCT_PARENT_OR_CONTEXT

    if _alias_requires_context(alias):
        if alias.safe_single_word and alias.reason:
            return AliasGateKind.SAFE_ALIAS
        return AliasGateKind.CONTEXT_REQUIRED

    return AliasGateKind.ACCEPTED_WITHOUT_CONTEXT
```

Interpret the classes this way:

- `PRODUCT_PARENT_OR_CONTEXT`: count as `product_parent_gated_aliases` and as a
  context-consulting alias; emit `safe_alias_ignored_for_parent_product` if the
  alias sets `safe_single_word`.
- `SAFE_ALIAS`: count as `safe_aliases`; if the entity also has
  `context_terms`, emit `safe_alias_bypasses_context` because context is not
  required for that alias.
- `CONTEXT_REQUIRED`: count as `context_gated_aliases`; compare normalized
  context terms with the alias key to emit `self_context_term`.
- `ACCEPTED_WITHOUT_CONTEXT`: count as `accepted_without_context_aliases`; if
  the entity has `context_terms`, emit `ungated_alias_with_context_terms`.

Emit `context_terms_no_effect` only when an entity defines `context_terms` and
none of its aliases classify as `PRODUCT_PARENT_OR_CONTEXT` or
`CONTEXT_REQUIRED`.

For omitted-default diagnostics, correlate raw YAML entities to validated
entities by list index after successful validation. Invalid configs should still
return only `invalid_config`; valid configs get deterministic
`implicit_initial_weight` and `implicit_match_confidence` findings from the raw
mapping at the same index.

- [ ] **Step 4: Add deterministic sorting**

Append:

```python
def _sort_findings(findings: Sequence[EntityPackFinding]) -> list[EntityPackFinding]:
    severity_order = {
        EntityPackFindingSeverity.ERROR: 0,
        EntityPackFindingSeverity.WARNING: 1,
        EntityPackFindingSeverity.INFO: 2,
    }
    return sorted(
        findings,
        key=lambda finding: (
            severity_order[finding.severity],
            finding.code,
            finding.entity_name or "",
            finding.alias or "",
            finding.field or "",
            finding.message,
        ),
    )
```

- [ ] **Step 5: Run focused tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_entity_pack_lint.py -q
```

Expected: tests from Task 1 pass after any minimal corrections.

## Task 3: Add Detailed Diagnostics Tests

**Files:**
- Modify: `tests/test_entity_pack_lint.py`

- [ ] **Step 1: Add classification, product, hierarchy, context, safe-alias, and raw-default tests**

Append focused tests for:

- `missing_tags`;
- `missing_category_tags`;
- `product_missing_parent_brand`;
- `product_missing_context_terms`;
- `parent_brand_on_non_product`;
- `product_alias_matches_parent_brand`;
- `parent_self_reference`;
- `parent_cycle`;
- `context_terms_no_effect`;
- `ungated_alias_with_context_terms`;
- `self_context_term`;
- `safe_common_alias`;
- `safe_alias_bypasses_context`;
- `safe_alias_ignored_for_parent_product`;
- `safe_single_word_alias`;
- `safe_single_word_no_effect`;
- `implicit_initial_weight`;
- `implicit_match_confidence`;
- blank/duplicate context/tag/category-tag findings.

Use small YAML fixtures in each test. Keep assertions on stable codes,
severities, `entity_name`, `alias`, and `field`.

Add explicit matcher-contract edge tests:

```python
def test_multi_word_alias_with_context_terms_is_reported_as_ungated(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: Office Siren
            type: trend
            aliases:
              - value: office siren
            context_terms: [fashion, styling]
            tags: [aesthetic]
            initial_weight: 1.0
            match_confidence: 1.0
        """,
    )

    result = lint_entity_pack(path)

    assert "ungated_alias_with_context_terms" in finding_codes(result)
    assert "context_terms_no_effect" in finding_codes(result)
    assert result.accepted_without_context_aliases == 1
    assert result.context_gated_aliases == 0


def test_context_terms_no_effect_not_emitted_when_one_alias_uses_context(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: Coach
            type: brand
            aliases:
              - value: Coach
              - value: Coach Tabby
            context_terms: [bag, handbag]
            tags: [bags]
            initial_weight: 1.0
            match_confidence: 1.0
        """,
    )

    result = lint_entity_pack(path)

    assert "context_terms_no_effect" not in finding_codes(result)
    assert "ungated_alias_with_context_terms" in finding_codes(result)
    assert result.context_gated_aliases == 1
    assert result.accepted_without_context_aliases == 1


def test_safe_non_product_alias_bypasses_context(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: Khaite
            type: brand
            aliases:
              - value: Khaite
                safe_single_word: true
                reason: Distinct brand name.
            context_terms: [runway]
            tags: [brand]
            initial_weight: 1.0
            match_confidence: 1.0
        """,
    )

    result = lint_entity_pack(path)

    assert "safe_alias_bypasses_context" in finding_codes(result)
    assert result.safe_aliases == 1
    assert result.context_gated_aliases == 0


def test_product_parent_brand_alias_ignores_safe_single_word(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: Alaia
            type: brand
            aliases:
              - value: Alaia
                safe_single_word: true
                reason: Distinct brand name.
            tags: [brand]
            initial_weight: 1.0
            match_confidence: 1.0
          - name: Alaia Le Teckel
            type: product
            parent_brand: Alaia
            aliases:
              - value: Teckel
                safe_single_word: true
                reason: Product shorthand.
            context_terms: [bag]
            category_tags: [bag]
            initial_weight: 1.0
            match_confidence: 1.0
        """,
    )

    result = lint_entity_pack(path)

    assert "safe_alias_ignored_for_parent_product" in finding_codes(result)
    assert result.product_parent_gated_aliases == 1
    assert result.safe_aliases == 1


def test_product_parent_brand_alias_counts_parent_and_context_gate(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: The Row
            type: brand
            aliases:
              - value: The Row
            context_terms: [fashion]
            tags: [brand]
            initial_weight: 1.0
            match_confidence: 1.0
          - name: The Row Margaux
            type: product
            parent_brand: The Row
            aliases:
              - value: Margaux
            context_terms: [handbag, tote]
            category_tags: [bag]
            initial_weight: 1.0
            match_confidence: 1.0
        """,
    )

    result = lint_entity_pack(path)

    assert "product_missing_context_terms" not in finding_codes(result)
    assert result.product_parent_gated_aliases == 1
```

- [ ] **Step 2: Add JSON and table-render tests**

Append:

```python
def test_lint_result_json_shape_is_stable(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: Stable Brand
            type: brand
            aliases:
              - value: Stable Brand
            tags: [brand]
            initial_weight: 1.0
            match_confidence: 1.0
        """,
    )

    result = lint_entity_pack(path)
    payload = json.loads(result.model_dump_json(indent=2))

    assert list(payload) == [
        "path",
        "entity_count",
        "alias_count",
        "type_counts",
        "tag_counts",
        "category_tag_counts",
        "accepted_without_context_aliases",
        "context_gated_aliases",
        "safe_aliases",
        "product_parent_gated_aliases",
        "findings",
    ]
    assert payload["path"] == str(path)
    assert payload["entity_count"] == 1
    assert payload["alias_count"] == 1
    assert payload["findings"] == []


def test_render_entity_pack_lint_table_includes_summary_and_findings(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: Untagged Trend
            type: trend
            aliases:
              - value: quiet trend
            initial_weight: 1.0
            match_confidence: 1.0
        """,
    )

    lines = render_entity_pack_lint_table(lint_entity_pack(path))

    assert lines[0] == f"Entity pack: {path}"
    assert "Entities: 1 total" in lines
    assert "Aliases: 1 total" in lines
    assert "Severity | Code | Entity | Alias | Field | Message" in lines
    assert any("missing_tags" in line for line in lines)
```

- [ ] **Step 3: Run focused module tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_entity_pack_lint.py -q
```

Expected: PASS.

## Task 4: Add CLI Command And CLI Tests

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Write failing CLI tests**

Append tests to `tests/test_cli.py` near the existing source-pack lint tests:

```python
def test_entity_pack_lint_help_lists_format_and_strict() -> None:
    result = CliRunner().invoke(app, ["entity-pack-lint", "--help"], env={"COLUMNS": "120"})

    assert result.exit_code == 0
    assert "--format" in result.output
    assert "--strict" in result.output
    assert "without matching, scoring, or collecting sources" in result.output


def test_entity_pack_lint_prints_table_for_public_pack() -> None:
    result = CliRunner().invoke(
        app,
        ["entity-pack-lint", "configs/entity-packs/fashion-watchlist.example.yaml"],
        env={"COLUMNS": "120"},
    )

    assert result.exit_code == 0
    assert "Entity pack: configs/entity-packs/fashion-watchlist.example.yaml" in result.output
    assert "Entities:" in result.output
    assert "Findings:" in result.output


def test_entity_pack_lint_prints_json_for_public_pack() -> None:
    result = CliRunner().invoke(
        app,
        [
            "entity-pack-lint",
            "configs/entity-packs/fashion-watchlist.example.yaml",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["path"] == "configs/entity-packs/fashion-watchlist.example.yaml"
    assert payload["entity_count"] >= 24
    assert "findings" in payload
```

Add strict, invalid-config, and read-only artifact tests mirroring the
source-pack lint tests:

```python
def test_entity_pack_lint_strict_exits_nonzero_on_warnings(tmp_path: Path) -> None:
    path = tmp_path / "entities.yaml"
    path.write_text(
        "version: 1\n"
        "entities:\n"
        "  - name: Untagged Trend\n"
        "    type: trend\n"
        "    aliases:\n"
        "      - value: quiet trend\n"
        "    initial_weight: 1.0\n"
        "    match_confidence: 1.0\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["entity-pack-lint", str(path), "--strict"])

    assert result.exit_code == 1
    assert "missing_tags" in result.output


def test_entity_pack_lint_invalid_config_exits_nonzero_without_traceback(tmp_path: Path) -> None:
    path = tmp_path / "entities.yaml"
    path.write_text("version: 1\nentities:\n  - name: Broken\n    type: brand\n", encoding="utf-8")

    result = CliRunner().invoke(app, ["entity-pack-lint", str(path)])

    assert result.exit_code == 1
    assert "invalid_config" in result.output
    assert "Traceback" not in result.output
```

- [ ] **Step 2: Run CLI tests and verify they fail before CLI implementation**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q -k entity_pack_lint
```

Expected: FAIL because the command is not registered yet.

- [ ] **Step 3: Implement CLI imports, format alias, and command**

Modify `src/fashion_radar/cli.py`:

```python
from fashion_radar.entity_packs import (
    EntityPackFindingSeverity,
    lint_entity_pack,
    render_entity_pack_lint_table,
)
```

Add near format aliases:

```python
EntityPackLintOutputFormat = Literal["table", "json"]
ENTITY_PACK_LINT_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
```

Add near `source_pack_lint_command`:

```python
@app.command(name="entity-pack-lint")
def entity_pack_lint_command(
    path: Path,
    output_format: EntityPackLintOutputFormat = ENTITY_PACK_LINT_FORMAT_OPTION,
    strict: bool = typer.Option(False, help="Exit non-zero when warnings are present."),
) -> None:
    """Lint a local entity pack without matching, scoring, or collecting sources."""
    result = lint_entity_pack(path)
    if output_format == "json":
        typer.echo(result.model_dump_json(indent=2))
    else:
        for line in render_entity_pack_lint_table(result):
            typer.echo(line)

    has_errors = any(
        finding.severity == EntityPackFindingSeverity.ERROR for finding in result.findings
    )
    has_warnings = any(
        finding.severity == EntityPackFindingSeverity.WARNING for finding in result.findings
    )
    if has_errors or (strict and has_warnings):
        raise typer.Exit(1)
```

- [ ] **Step 4: Run CLI tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q -k entity_pack_lint
```

Expected: PASS.

## Task 5: Add Documentation

**Files:**
- Create: `docs/entity-pack-quality.md`
- Modify: `docs/entity-packs.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Create entity-pack quality docs**

Create `docs/entity-pack-quality.md` with these sections:

- title `# Entity-Pack Quality`;
- command examples for table, JSON, and `--strict`;
- table output explanation;
- JSON output explanation;
- severity meanings;
- finding code reference for every Stage 15 code;
- why findings matter;
- tuning aliases, context terms, parents, tags, category tags, weights, and
  match confidence;
- limits.

The limits section must state the command is local and read-only, does not
collect sources, does not inspect SQLite, does not run matching/scoring, does
not create artifacts, does not search social platforms, and is not a hot-list,
ranking, market-wide proof, platform-wide proof, compliance review, or audit
workflow.

Finding documentation for `product_missing_parent_brand` must say products
without `parent_brand` are still valid local configs and follow ordinary alias
semantics. The warning is a precision recommendation for named branded
products, not a correctness or validity failure.

- [ ] **Step 2: Update existing docs**

Update:

- `docs/entity-packs.md`: add a short "Lint The Pack" section before "Use The
  Pack" with `uv run fashion-radar entity-pack-lint ...`.
- `README.md`: add the command near existing source-pack/source-quality docs
  and add `docs/entity-pack-quality.md` to the docs list.
- `docs/architecture.md`: mention the optional read-only entity-pack lint step
  in the config/tooling portion only.
- `CHANGELOG.md`: add an unreleased bullet for entity-pack quality diagnostics.

- [ ] **Step 3: Run docs-sensitive checks**

Run:

```bash
rg -n "entity-pack-lint|Entity-Pack Quality|context_terms|hot-list|platform-wide" README.md docs/entity-packs.md docs/entity-pack-quality.md docs/architecture.md CHANGELOG.md
```

Expected: output shows the new docs and no wording that claims platform-wide or
market-wide current hotness.

Also inspect broader boundary terms:

```bash
rg -n "social monitoring|platform search|exports|demand proof|ranking|current hot|market-wide|platform-wide|source acquisition" README.md docs/entity-packs.md docs/entity-pack-quality.md docs/architecture.md CHANGELOG.md
```

Expected: any matches appear only in limits, non-goals, or warning language that
explicitly says the tool does not provide those capabilities.

## Task 6: Full Verification And Claude Code Review

**Files:**
- Create: `docs/reviews/claude-code-stage-15-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-15-code-review.md`

- [ ] **Step 1: Run focused tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_entity_pack_lint.py tests/test_entity_packs.py tests/test_cli.py -q
```

Expected: PASS.

- [ ] **Step 2: Run full project verification**

Run:

```bash
git diff --check
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
codegraph status
```

Expected: all commands pass and CodeGraph reports the index is up to date.

- [ ] **Step 3: Write Claude Code code-review prompt**

Create `docs/reviews/claude-code-stage-15-code-review-prompt.md` asking Claude
Code to review the Stage 15 code/docs in read-only plan mode with
`--effort max`, focusing on correctness, matcher semantics, read-only behavior,
CLI exit behavior, tests, docs wording, and out-of-scope boundaries.

- [ ] **Step 4: Run Claude Code code review**

Run:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-15-code-review-prompt.md | tee docs/reviews/claude-code-stage-15-code-review.md
```

Expected: Claude Code returns either approval or findings. Fix Critical and
Important findings before proceeding.

- [ ] **Step 5: Optional release checks before GitHub upload**

Run if implementation verification and code review are clean:

```bash
uv lock --check --default-index https://pypi.org/simple
uv sync --locked --dev --check --default-index https://pypi.org/simple
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
uv build --out-dir /tmp/fashion-radar-dist-stage15
```

Do not commit mirror-bound lockfile changes. Do not commit build artifacts,
virtual environments, caches, reports, SQLite files, `.codegraph/`, cookies, or
tokens.

- [ ] **Step 6: Commit and push only after review gates pass**

After verification, code review, and artifact/secret checks:

```bash
git status --short
git add src/fashion_radar/entity_packs.py src/fashion_radar/cli.py tests/test_entity_pack_lint.py tests/test_cli.py docs/entity-pack-quality.md docs/entity-packs.md README.md docs/architecture.md CHANGELOG.md docs/superpowers/specs/2026-06-12-stage-15-entity-pack-quality-design.md docs/superpowers/plans/2026-06-12-stage-15-entity-pack-quality-plan.md docs/reviews/claude-code-stage-15-plan-review-prompt.md docs/reviews/claude-code-stage-15-plan-review.md docs/reviews/claude-code-stage-15-code-review-prompt.md docs/reviews/claude-code-stage-15-code-review.md
git commit -m "Add entity-pack quality diagnostics"
```

Push with temporary `GIT_ASKPASS` only. Keep the remote URL token-free and remove
the askpass file immediately after the push.

## Plan Self-Review

- Spec coverage: every design requirement maps to module, CLI, tests, docs, or
  verification tasks above.
- Placeholder scan: no task depends on undefined future work or external
  decisions.
- Type consistency: public names are consistently
  `EntityPackFindingSeverity`, `EntityPackFinding`, `EntityPackLintResult`,
  `lint_entity_pack`, `render_entity_pack_lint_table`, and
  `entity-pack-lint`.
- Boundary check: no task adds collectors, platform tooling, scraping,
  matching/scoring behavior changes, database changes, or product-facing
  compliance/audit features.

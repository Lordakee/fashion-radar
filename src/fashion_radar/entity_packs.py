from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field

from fashion_radar.extract.text import normalize_alias_key
from fashion_radar.lint_formatting import format_finding_counts
from fashion_radar.models.entity import AliasDefinition, EntityDefinition, EntityType
from fashion_radar.settings import UNSAFE_COMMON_ALIASES, ConfigError, load_entity_config


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


class AliasGateKind(StrEnum):
    PRODUCT_PARENT_OR_CONTEXT = "product_parent_or_context"
    SAFE_ALIAS = "safe_alias"
    CONTEXT_REQUIRED = "context_required"
    ACCEPTED_WITHOUT_CONTEXT = "accepted_without_context"


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
            alias_count=_raw_alias_count(raw_entities),
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
            sorted(Counter(tag for entity in entities for tag in entity.category_tags).items())
        ),
        accepted_without_context_aliases=gate_counts[AliasGateKind.ACCEPTED_WITHOUT_CONTEXT],
        context_gated_aliases=gate_counts[AliasGateKind.CONTEXT_REQUIRED],
        safe_aliases=gate_counts[AliasGateKind.SAFE_ALIAS],
        product_parent_gated_aliases=gate_counts[AliasGateKind.PRODUCT_PARENT_OR_CONTEXT],
        findings=_sort_findings(findings),
    )


def render_entity_pack_lint_table(result: EntityPackLintResult) -> list[str]:
    """Render a deterministic human-readable lint summary."""
    lines = [
        f"Entity pack: {result.path}",
        f"Entities: {result.entity_count} total",
        f"Aliases: {result.alias_count} total",
        f"Types: {_format_counts(result.type_counts)}",
        (
            "Findings: "
            f"{format_finding_counts(result.error_count, result.warning_count, result.info_count)}"
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


def _raw_alias_count(raw_entities: Sequence[Mapping[str, Any]]) -> int:
    count = 0
    for raw_entity in raw_entities:
        aliases = raw_entity.get("aliases", [])
        if isinstance(aliases, list):
            count += len(aliases)
    return count


def _lint_entities(
    entities: Sequence[EntityDefinition],
    raw_entities: Sequence[Mapping[str, Any]],
) -> list[EntityPackFinding]:
    findings: list[EntityPackFinding] = []
    if not entities:
        findings.append(
            EntityPackFinding(
                severity=EntityPackFindingSeverity.ERROR,
                code="empty_entity_pack",
                message="Entity pack has no entities.",
            )
        )

    entities_by_name = {normalize_alias_key(entity.name): entity for entity in entities}
    for index, entity in enumerate(entities):
        raw_entity = raw_entities[index] if index < len(raw_entities) else {}
        findings.extend(_entity_findings(entity, raw_entity, entities_by_name))

    findings.extend(_parent_hierarchy_findings(entities))
    return findings


def _entity_findings(
    entity: EntityDefinition,
    raw_entity: Mapping[str, Any],
    entities_by_name: Mapping[str, EntityDefinition],
) -> list[EntityPackFinding]:
    findings: list[EntityPackFinding] = []
    entity_key = normalize_alias_key(entity.name)
    if not entity_key:
        findings.append(
            EntityPackFinding(
                severity=EntityPackFindingSeverity.ERROR,
                code="name_normalizes_empty",
                message="Entity name normalizes to an empty matcher key.",
                entity_name=entity.name,
                field="name",
            )
        )

    if not entity.aliases:
        findings.append(
            EntityPackFinding(
                severity=EntityPackFindingSeverity.ERROR,
                code="entity_without_aliases",
                message="Entity has no aliases and cannot match text.",
                entity_name=entity.name,
                field="aliases",
            )
        )

    if (
        entity.type
        in {
            EntityType.BRAND,
            EntityType.DESIGNER,
            EntityType.CELEBRITY,
            EntityType.TREND,
        }
        and not entity.tags
    ):
        findings.append(
            EntityPackFinding(
                severity=EntityPackFindingSeverity.WARNING,
                code="missing_tags",
                message="Brand, designer, celebrity, or trend entity has no tags.",
                entity_name=entity.name,
                field="tags",
            )
        )

    if entity.type in {EntityType.PRODUCT, EntityType.CATEGORY} and not entity.category_tags:
        findings.append(
            EntityPackFinding(
                severity=EntityPackFindingSeverity.WARNING,
                code="missing_category_tags",
                message="Product or category entity has no category tags.",
                entity_name=entity.name,
                field="category_tags",
            )
        )

    findings.extend(_product_parent_findings(entity, entities_by_name))
    findings.extend(_metadata_list_findings(entity, entity.context_terms, "context_terms"))
    findings.extend(_metadata_list_findings(entity, entity.tags, "tags"))
    findings.extend(_metadata_list_findings(entity, entity.category_tags, "category_tags"))
    findings.extend(_alias_findings(entity))

    if "initial_weight" not in raw_entity:
        findings.append(
            EntityPackFinding(
                severity=EntityPackFindingSeverity.INFO,
                code="implicit_initial_weight",
                message="Entity omits initial_weight, so scoring uses the default weight.",
                entity_name=entity.name,
                field="initial_weight",
            )
        )
    if "match_confidence" not in raw_entity:
        findings.append(
            EntityPackFinding(
                severity=EntityPackFindingSeverity.INFO,
                code="implicit_match_confidence",
                message="Entity omits match_confidence, so matching uses the default confidence.",
                entity_name=entity.name,
                field="match_confidence",
            )
        )

    return findings


def _product_parent_findings(
    entity: EntityDefinition,
    entities_by_name: Mapping[str, EntityDefinition],
) -> list[EntityPackFinding]:
    findings: list[EntityPackFinding] = []
    if entity.type == EntityType.PRODUCT and not entity.parent_brand:
        findings.append(
            EntityPackFinding(
                severity=EntityPackFindingSeverity.WARNING,
                code="product_missing_parent_brand",
                message=(
                    "Product has no parent_brand; this is a precision recommendation "
                    "for named branded products, not a validity failure."
                ),
                entity_name=entity.name,
                field="parent_brand",
            )
        )
        return findings

    if entity.type != EntityType.PRODUCT and entity.parent_brand:
        findings.append(
            EntityPackFinding(
                severity=EntityPackFindingSeverity.WARNING,
                code="parent_brand_on_non_product",
                message=(
                    "parent_brand is present on a non-product; the current matcher "
                    "only treats it specially for product entities."
                ),
                entity_name=entity.name,
                field="parent_brand",
            )
        )
        return findings

    if entity.type != EntityType.PRODUCT or not entity.parent_brand:
        return findings

    if not entity.context_terms:
        findings.append(
            EntityPackFinding(
                severity=EntityPackFindingSeverity.WARNING,
                code="product_missing_context_terms",
                message=(
                    "Product has parent_brand but no context_terms; product aliases "
                    "without the parent brand will be rejected."
                ),
                entity_name=entity.name,
                field="context_terms",
            )
        )

    parent = entities_by_name.get(normalize_alias_key(entity.parent_brand))
    if parent is None:
        return findings
    parent_keys = {normalize_alias_key(parent.name)}
    parent_keys.update(normalize_alias_key(alias.value) for alias in parent.aliases)
    for alias in entity.aliases:
        alias_key = normalize_alias_key(alias.value)
        if alias_key and alias_key in parent_keys:
            findings.append(
                EntityPackFinding(
                    severity=EntityPackFindingSeverity.WARNING,
                    code="product_alias_matches_parent_brand",
                    message=(
                        "Product alias matches the parent brand name or alias, "
                        "which can make product matches too broad."
                    ),
                    entity_name=entity.name,
                    alias=alias.value,
                    field="aliases",
                )
            )
    return findings


def _metadata_list_findings(
    entity: EntityDefinition,
    values: Sequence[str],
    field: str,
) -> list[EntityPackFinding]:
    blank_code = {
        "context_terms": "blank_context_term",
        "tags": "blank_tag",
        "category_tags": "blank_category_tag",
    }[field]
    duplicate_code = {
        "context_terms": "duplicate_context_term",
        "tags": "duplicate_tag",
        "category_tags": "duplicate_category_tag",
    }[field]
    findings: list[EntityPackFinding] = []
    seen: set[str] = set()
    for value in values:
        if not value.strip():
            findings.append(
                EntityPackFinding(
                    severity=EntityPackFindingSeverity.WARNING,
                    code=blank_code,
                    message=f"{field} contains a blank value.",
                    entity_name=entity.name,
                    field=field,
                )
            )
            continue

        key = normalize_alias_key(value)
        if not key and field == "context_terms":
            findings.append(
                EntityPackFinding(
                    severity=EntityPackFindingSeverity.WARNING,
                    code="context_term_normalizes_empty",
                    message="Context term normalizes to an empty matcher key.",
                    entity_name=entity.name,
                    field=field,
                )
            )
            continue
        if key in seen:
            findings.append(
                EntityPackFinding(
                    severity=EntityPackFindingSeverity.WARNING,
                    code=duplicate_code,
                    message=f"{field} contains duplicate normalized values.",
                    entity_name=entity.name,
                    field=field,
                )
            )
            continue
        seen.add(key)
    return findings


def _alias_findings(entity: EntityDefinition) -> list[EntityPackFinding]:
    findings: list[EntityPackFinding] = []
    gates = [_classify_alias_gate(entity, alias) for alias in entity.aliases]

    if entity.context_terms and not any(
        gate
        in {
            AliasGateKind.PRODUCT_PARENT_OR_CONTEXT,
            AliasGateKind.CONTEXT_REQUIRED,
        }
        for gate in gates
    ):
        findings.append(
            EntityPackFinding(
                severity=EntityPackFindingSeverity.WARNING,
                code="context_terms_no_effect",
                message=(
                    "Entity has context_terms, but none of its aliases consult "
                    "context under current matcher rules."
                ),
                entity_name=entity.name,
                field="context_terms",
            )
        )

    context_keys = {
        normalize_alias_key(term)
        for term in entity.context_terms
        if term.strip() and normalize_alias_key(term)
    }
    for alias, gate in zip(entity.aliases, gates, strict=True):
        alias_key = normalize_alias_key(alias.value)
        if not alias_key:
            findings.append(
                EntityPackFinding(
                    severity=EntityPackFindingSeverity.ERROR,
                    code="alias_normalizes_empty",
                    message="Alias normalizes to an empty matcher key.",
                    entity_name=entity.name,
                    alias=alias.value,
                    field="aliases",
                )
            )

        if entity.context_terms and gate == AliasGateKind.ACCEPTED_WITHOUT_CONTEXT:
            findings.append(
                EntityPackFinding(
                    severity=EntityPackFindingSeverity.WARNING,
                    code="ungated_alias_with_context_terms",
                    message=(
                        "This ordinary multi-word alias is accepted without context "
                        "by the current matcher."
                    ),
                    entity_name=entity.name,
                    alias=alias.value,
                    field="aliases",
                )
            )

        if gate == AliasGateKind.CONTEXT_REQUIRED and alias_key in context_keys:
            findings.append(
                EntityPackFinding(
                    severity=EntityPackFindingSeverity.WARNING,
                    code="self_context_term",
                    message="Context term matches a gated alias on the same entity.",
                    entity_name=entity.name,
                    alias=alias.value,
                    field="context_terms",
                )
            )

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

        if not alias.safe_single_word:
            continue

        if alias_key in UNSAFE_COMMON_ALIASES:
            findings.append(
                EntityPackFinding(
                    severity=EntityPackFindingSeverity.WARNING,
                    code="safe_common_alias",
                    message=(
                        "Alias is marked safe but is listed as unsafe/common; "
                        "context terms are usually safer for this phrase."
                    ),
                    entity_name=entity.name,
                    alias=alias.value,
                    field="aliases.safe_single_word",
                )
            )

        if gate == AliasGateKind.PRODUCT_PARENT_OR_CONTEXT:
            findings.append(
                EntityPackFinding(
                    severity=EntityPackFindingSeverity.WARNING,
                    code="safe_alias_ignored_for_parent_product",
                    message=(
                        "safe_single_word is ignored for products with parent_brand; "
                        "parent brand or product context is still required."
                    ),
                    entity_name=entity.name,
                    alias=alias.value,
                    field="aliases.safe_single_word",
                )
            )
        elif gate == AliasGateKind.SAFE_ALIAS:
            findings.append(
                EntityPackFinding(
                    severity=EntityPackFindingSeverity.INFO,
                    code="safe_single_word_alias",
                    message="Effective safe single-word/common alias is present.",
                    entity_name=entity.name,
                    alias=alias.value,
                    field="aliases.safe_single_word",
                )
            )
            if entity.context_terms:
                findings.append(
                    EntityPackFinding(
                        severity=EntityPackFindingSeverity.WARNING,
                        code="safe_alias_bypasses_context",
                        message=(
                            "Safe non-product alias bypasses available context terms "
                            "under current matcher rules."
                        ),
                        entity_name=entity.name,
                        alias=alias.value,
                        field="aliases.safe_single_word",
                    )
                )
        elif gate == AliasGateKind.ACCEPTED_WITHOUT_CONTEXT:
            findings.append(
                EntityPackFinding(
                    severity=EntityPackFindingSeverity.INFO,
                    code="safe_single_word_no_effect",
                    message=(
                        "safe_single_word is set on an alias that does not require "
                        "context under current matcher rules."
                    ),
                    entity_name=entity.name,
                    alias=alias.value,
                    field="aliases.safe_single_word",
                )
            )

    return findings


def _parent_hierarchy_findings(entities: Sequence[EntityDefinition]) -> list[EntityPackFinding]:
    findings: list[EntityPackFinding] = []
    parent_by_name = {
        normalize_alias_key(entity.name): normalize_alias_key(entity.parent)
        for entity in entities
        if entity.parent
    }
    for entity in entities:
        entity_key = normalize_alias_key(entity.name)
        parent_key = parent_by_name.get(entity_key)
        if not parent_key:
            continue
        if parent_key == entity_key:
            findings.append(
                EntityPackFinding(
                    severity=EntityPackFindingSeverity.WARNING,
                    code="parent_self_reference",
                    message="Entity parent points to itself.",
                    entity_name=entity.name,
                    field="parent",
                )
            )
        if _has_parent_cycle(entity_key, parent_by_name):
            findings.append(
                EntityPackFinding(
                    severity=EntityPackFindingSeverity.WARNING,
                    code="parent_cycle",
                    message="Generic parent links form a cycle.",
                    entity_name=entity.name,
                    field="parent",
                )
            )
    return findings


def _has_parent_cycle(start_key: str, parent_by_name: Mapping[str, str]) -> bool:
    seen: set[str] = set()
    current = start_key
    while current in parent_by_name:
        parent = parent_by_name[current]
        if parent == start_key or parent in seen:
            return True
        seen.add(parent)
        current = parent
    return False


def _gate_counts(entities: Sequence[EntityDefinition]) -> Counter[AliasGateKind]:
    counts: Counter[AliasGateKind] = Counter()
    for entity in entities:
        for alias in entity.aliases:
            counts[_classify_alias_gate(entity, alias)] += 1
    return counts


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


def _alias_requires_context(alias: AliasDefinition) -> bool:
    key = normalize_alias_key(alias.value)
    return alias.requires_context or len(key.split()) == 1 or key in UNSAFE_COMMON_ALIASES


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


def _invalid_config_finding(message: str) -> EntityPackFinding:
    return EntityPackFinding(
        severity=EntityPackFindingSeverity.ERROR,
        code="invalid_config",
        message=message,
    )


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


def _count_findings(
    findings: Sequence[EntityPackFinding],
    severity: EntityPackFindingSeverity,
) -> int:
    return sum(1 for finding in findings if finding.severity == severity)


def _format_counts(counts: Mapping[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))

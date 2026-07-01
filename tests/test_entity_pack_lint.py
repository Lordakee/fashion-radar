import json
from pathlib import Path
from textwrap import dedent

from fashion_radar.entity_packs import (
    EntityPackFinding,
    EntityPackFindingSeverity,
    EntityPackLintResult,
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


def test_lint_repository_buyer_brands_pack_has_no_errors() -> None:
    result = lint_entity_pack(Path("configs/entity-packs/buyer-brands.example.yaml"))

    assert result.error_count == 0
    assert result.entity_count >= 29
    assert result.alias_count >= result.entity_count
    assert result.type_counts["brand"] >= 24
    assert result.type_counts["trend"] >= 3
    assert result.context_gated_aliases > 0


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


def test_missing_classification_tags_are_warnings(tmp_path: Path) -> None:
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
          - name: Untagged Bag
            type: product
            aliases:
              - value: untagged bag
            initial_weight: 1.0
            match_confidence: 1.0
        """,
    )

    result = lint_entity_pack(path)

    missing_tags = findings_by_code(result, "missing_tags")[0]
    missing_category_tags = findings_by_code(result, "missing_category_tags")[0]
    assert missing_tags.severity == EntityPackFindingSeverity.WARNING
    assert missing_tags.entity_name == "Untagged Trend"
    assert missing_tags.field == "tags"
    assert missing_category_tags.severity == EntityPackFindingSeverity.WARNING
    assert missing_category_tags.entity_name == "Untagged Bag"
    assert missing_category_tags.field == "category_tags"


def test_product_parent_and_context_findings(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: Known Brand
            type: brand
            aliases:
              - value: Known Brand
            tags: [brand]
            initial_weight: 1.0
            match_confidence: 1.0
          - name: Generic Product
            type: product
            aliases:
              - value: generic product
            category_tags: [bag]
            initial_weight: 1.0
            match_confidence: 1.0
          - name: Known Brand Bag
            type: product
            parent_brand: Known Brand
            aliases:
              - value: Known Bag
            category_tags: [bag]
            initial_weight: 1.0
            match_confidence: 1.0
        """,
    )

    result = lint_entity_pack(path)

    assert "product_missing_parent_brand" in finding_codes(result)
    assert "product_missing_context_terms" in finding_codes(result)
    parent_finding = findings_by_code(result, "product_missing_parent_brand")[0]
    assert "precision recommendation" in parent_finding.message


def test_parent_brand_on_non_product_is_warning(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: Parent Brand
            type: brand
            aliases:
              - value: Parent Brand Alias
            tags: [brand]
            initial_weight: 1.0
            match_confidence: 1.0
          - name: Creative Person
            type: designer
            parent_brand: Parent Brand
            aliases:
              - value: Creative Person
            tags: [designer]
            initial_weight: 1.0
            match_confidence: 1.0
        """,
    )

    result = lint_entity_pack(path)

    finding = findings_by_code(result, "parent_brand_on_non_product")[0]
    assert finding.severity == EntityPackFindingSeverity.WARNING
    assert finding.entity_name == "Creative Person"
    assert finding.field == "parent_brand"


def test_product_alias_matching_parent_brand_name_is_warning(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: Parent Brand
            type: brand
            aliases:
              - value: Parent Brand Alias
            tags: [brand]
            initial_weight: 1.0
            match_confidence: 1.0
          - name: Parent Brand Bag
            type: product
            parent_brand: Parent Brand
            aliases:
              - value: Parent Brand
            context_terms: [bag]
            category_tags: [bag]
            initial_weight: 1.0
            match_confidence: 1.0
        """,
    )

    result = lint_entity_pack(path)

    finding = findings_by_code(result, "product_alias_matches_parent_brand")[0]
    assert finding.severity == EntityPackFindingSeverity.WARNING
    assert finding.entity_name == "Parent Brand Bag"
    assert finding.alias == "Parent Brand"


def test_parent_self_reference_and_cycle_are_warnings(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: Self Parent
            type: brand
            parent: Self Parent
            aliases:
              - value: Self Parent
            tags: [brand]
            initial_weight: 1.0
            match_confidence: 1.0
          - name: Parent A
            type: brand
            parent: Parent B
            aliases:
              - value: Parent A
            tags: [brand]
            initial_weight: 1.0
            match_confidence: 1.0
          - name: Parent B
            type: brand
            parent: Parent A
            aliases:
              - value: Parent B
            tags: [brand]
            initial_weight: 1.0
            match_confidence: 1.0
        """,
    )

    result = lint_entity_pack(path)

    assert "parent_self_reference" in finding_codes(result)
    assert "parent_cycle" in finding_codes(result)
    assert {finding.severity for finding in findings_by_code(result, "parent_cycle")} == {
        EntityPackFindingSeverity.WARNING
    }


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


def test_explicit_context_alias_warns_when_context_term_matches_alias(tmp_path: Path) -> None:
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
            context_terms: [boat shoes, footwear]
            category_tags: [shoes]
            initial_weight: 1.0
            match_confidence: 1.0
        """,
    )

    result = lint_entity_pack(path)

    finding = findings_by_code(result, "self_context_term")[0]
    assert finding.alias == "boat shoes"
    assert finding.field == "context_terms"
    assert "contained_context_term_for_gated_alias" not in finding_codes(result)


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
    assert "'shoes'" in finding.message
    assert "'Mary Jane shoes'" in finding.message


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
    assert "'mary jane'" in finding.message
    assert "'Mary Jane shoes'" in finding.message


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

    findings = findings_by_code(result, "contained_context_term_for_gated_alias")
    assert len(findings) == 1
    finding = findings[0]
    assert finding.alias == "Mary Jane shoes"
    assert finding.message.count("Context term") == 1
    assert "'mary jane'" in finding.message
    assert "'shoes'" not in finding.message


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


def test_self_context_term_is_warning_for_gated_alias(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: Coach
            type: brand
            aliases:
              - value: Coach
            context_terms: [coach, handbag]
            tags: [brand]
            initial_weight: 1.0
            match_confidence: 1.0
        """,
    )

    result = lint_entity_pack(path)

    finding = findings_by_code(result, "self_context_term")[0]
    assert finding.severity == EntityPackFindingSeverity.WARNING
    assert finding.alias == "Coach"
    assert finding.field == "context_terms"


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

    assert "context_terms_no_effect" in finding_codes(result)
    assert "safe_alias_bypasses_context" in finding_codes(result)
    assert "safe_single_word_alias" in finding_codes(result)
    assert result.safe_aliases == 1
    assert result.context_gated_aliases == 0


def test_safe_common_alias_is_warning(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: Coach
            type: brand
            aliases:
              - value: Coach
                safe_single_word: true
                reason: Intentionally accept the brand name without context.
            tags: [brand]
            initial_weight: 1.0
            match_confidence: 1.0
        """,
    )

    result = lint_entity_pack(path)

    finding = findings_by_code(result, "safe_common_alias")[0]
    assert finding.severity == EntityPackFindingSeverity.WARNING
    assert finding.alias == "Coach"


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
    assert all(
        finding.entity_name != "The Row Margaux"
        for finding in findings_by_code(result, "context_terms_no_effect")
    )
    assert result.product_parent_gated_aliases == 1


def test_safe_single_word_no_effect_is_info_for_multi_word_alias(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: Quiet Luxury
            type: trend
            aliases:
              - value: quiet luxury
                safe_single_word: true
                reason: Intentional no-op for diagnostic visibility.
            tags: [aesthetic]
            initial_weight: 1.0
            match_confidence: 1.0
        """,
    )

    result = lint_entity_pack(path)

    finding = findings_by_code(result, "safe_single_word_no_effect")[0]
    assert finding.severity == EntityPackFindingSeverity.INFO
    assert finding.alias == "quiet luxury"


def test_metadata_list_hygiene_findings(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: Metadata Brand
            type: brand
            aliases:
              - value: Metadata Brand
            context_terms: ["", bag, Bag, "!!!"]
            tags: ["", Runway, runway]
            category_tags: ["", Bag, bag]
            initial_weight: 1.0
            match_confidence: 1.0
        """,
    )

    result = lint_entity_pack(path)

    for code in [
        "blank_context_term",
        "duplicate_context_term",
        "context_term_normalizes_empty",
        "blank_tag",
        "duplicate_tag",
        "blank_category_tag",
        "duplicate_category_tag",
    ]:
        assert code in finding_codes(result)


def test_implicit_weight_and_confidence_are_info(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: Implicit Brand
            type: brand
            aliases:
              - value: Implicit Brand
            tags: [brand]
        """,
    )

    result = lint_entity_pack(path)

    initial_weight = findings_by_code(result, "implicit_initial_weight")[0]
    match_confidence = findings_by_code(result, "implicit_match_confidence")[0]
    assert initial_weight.severity == EntityPackFindingSeverity.INFO
    assert initial_weight.field == "initial_weight"
    assert match_confidence.severity == EntityPackFindingSeverity.INFO
    assert match_confidence.field == "match_confidence"


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


def test_render_entity_pack_lint_table_singularizes_one_finding_count() -> None:
    result = EntityPackLintResult(
        path="entities.yaml",
        entity_count=1,
        alias_count=1,
        type_counts={"brand": 1},
        findings=[
            EntityPackFinding(
                severity=EntityPackFindingSeverity.ERROR,
                code="error_code",
                message="Error message.",
            ),
            EntityPackFinding(
                severity=EntityPackFindingSeverity.WARNING,
                code="warning_code",
                message="Warning message.",
            ),
            EntityPackFinding(
                severity=EntityPackFindingSeverity.INFO,
                code="info_code",
                message="Info message.",
            ),
        ],
    )

    lines = render_entity_pack_lint_table(result)

    assert "Findings: 1 error, 1 warning, 1 info" in lines


def test_render_entity_pack_lint_table_keeps_plural_finding_counts() -> None:
    result = EntityPackLintResult(
        path="entities.yaml",
        entity_count=1,
        alias_count=1,
        type_counts={"brand": 1},
        findings=[
            EntityPackFinding(
                severity=EntityPackFindingSeverity.ERROR,
                code="error_one",
                message="Error one.",
            ),
            EntityPackFinding(
                severity=EntityPackFindingSeverity.ERROR,
                code="error_two",
                message="Error two.",
            ),
            EntityPackFinding(
                severity=EntityPackFindingSeverity.WARNING,
                code="warning_one",
                message="Warning one.",
            ),
            EntityPackFinding(
                severity=EntityPackFindingSeverity.WARNING,
                code="warning_two",
                message="Warning two.",
            ),
            EntityPackFinding(
                severity=EntityPackFindingSeverity.INFO,
                code="info_one",
                message="Info one.",
            ),
            EntityPackFinding(
                severity=EntityPackFindingSeverity.INFO,
                code="info_two",
                message="Info two.",
            ),
        ],
    )

    lines = render_entity_pack_lint_table(result)

    assert "Findings: 2 errors, 2 warnings, 2 info" in lines

import json
from pathlib import Path
from textwrap import dedent

from fashion_radar.source_packs import (
    SourcePackFinding,
    SourcePackFindingSeverity,
    SourcePackLintResult,
    lint_source_pack,
    normalize_source_target,
    render_source_pack_lint_table,
)


def write_yaml(path: Path, content: str) -> Path:
    path.write_text(dedent(content).strip() + "\n", encoding="utf-8")
    return path


def finding_codes(result) -> list[str]:
    return [finding.code for finding in result.findings]


def findings_by_code(result, code: str):
    return [finding for finding in result.findings if finding.code == code]


def test_lint_repository_public_pack_has_no_errors() -> None:
    result = lint_source_pack(Path("configs/source-packs/fashion-public.example.yaml"))

    assert result.error_count == 0
    assert result.ok is True
    assert result.source_count >= 10
    assert "rss" in result.type_counts
    assert "gdelt" in result.type_counts


def test_duplicate_source_names_are_errors_after_normalization(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: Fashion Feed
            type: rss
            url: https://example.com/a.xml
            weight: 1.0
            tags: [fashion_media]
            article:
              enabled: false
          - name: " fashion   feed "
            type: rss
            url: https://example.com/b.xml
            weight: 1.0
            tags: [fashion_media]
            article:
              enabled: false
        """,
    )

    result = lint_source_pack(path)

    duplicate_findings = findings_by_code(result, "duplicate_source_name")
    assert result.ok is False
    assert {finding.severity for finding in duplicate_findings} == {SourcePackFindingSeverity.ERROR}
    assert [finding.source_name for finding in duplicate_findings] == [
        "Fashion Feed",
        "fashion   feed",
    ]


def test_duplicate_feed_urls_are_warnings_after_normalization(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: First Feed
            type: rss
            url: HTTPS://Example.com/Fashion/#section
            weight: 1.0
            tags: [fashion_media]
            article:
              enabled: false
          - name: Second Feed
            type: rss
            url: https://example.com/Fashion
            weight: 1.0
            tags: [fashion_media]
            article:
              enabled: false
        """,
    )

    result = lint_source_pack(path)

    duplicate_findings = findings_by_code(result, "duplicate_source_target")
    assert result.error_count == 0
    assert {finding.severity for finding in duplicate_findings} == {
        SourcePackFindingSeverity.WARNING
    }
    assert [finding.source_name for finding in duplicate_findings] == [
        "First Feed",
        "Second Feed",
    ]


def test_url_normalization_lowercases_scheme_and_host_strips_fragment_and_trailing_slash() -> None:
    assert normalize_source_target("HTTPS://Example.COM/feed/#part") == "https://example.com/feed"
    assert normalize_source_target("https://example.com/feed/") == "https://example.com/feed"
    assert normalize_source_target("https://example.com/feed?a=1") != normalize_source_target(
        "https://example.com/feed?a=2"
    )


def test_duplicate_gdelt_queries_are_warnings_after_normalization(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: GDELT One
            type: gdelt
            query: '"fashion   week" OR runway'
            weight: 0.8
            tags: [gdelt, runway]
          - name: GDELT Two
            type: gdelt
            query: '"fashion week" or runway'
            weight: 0.8
            tags: [gdelt, runway]
        """,
    )

    result = lint_source_pack(path)

    duplicate_findings = findings_by_code(result, "duplicate_gdelt_query")
    assert result.error_count == 0
    assert {finding.severity for finding in duplicate_findings} == {
        SourcePackFindingSeverity.WARNING
    }
    assert [finding.source_name for finding in duplicate_findings] == [
        "GDELT One",
        "GDELT Two",
    ]


def test_missing_tags_are_warnings(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: GDELT Untagged
            type: gdelt
            query: fashion
            weight: 0.8
        """,
    )

    result = lint_source_pack(path)

    finding = findings_by_code(result, "missing_tags")[0]
    assert result.error_count == 0
    assert finding.severity == SourcePackFindingSeverity.WARNING
    assert finding.source_name == "GDELT Untagged"
    assert finding.field == "tags"


def test_implicit_weight_is_info(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: GDELT Default Weight
            type: gdelt
            query: fashion
            tags: [gdelt]
        """,
    )

    result = lint_source_pack(path)

    finding = findings_by_code(result, "implicit_weight")[0]
    assert result.error_count == 0
    assert finding.severity == SourcePackFindingSeverity.INFO
    assert finding.source_name == "GDELT Default Weight"
    assert finding.field == "weight"


def test_all_disabled_sources_are_errors(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: Disabled Feed
            type: rss
            url: https://example.com/feed.xml
            enabled: false
            weight: 1.0
            tags: [fashion_media]
            article:
              enabled: false
        """,
    )

    result = lint_source_pack(path)

    assert "empty_enabled_pack" in finding_codes(result)
    assert "disabled_source" in finding_codes(result)
    assert result.error_count == 1
    assert result.ok is False


def test_invalid_source_config_returns_error_finding(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: Broken Feed
            type: rss
        """,
    )

    result = lint_source_pack(path)

    finding = findings_by_code(result, "invalid_config")[0]
    assert result.error_count == 1
    assert finding.severity == SourcePackFindingSeverity.ERROR
    assert "requires url" in finding.message


def test_lint_result_json_shape_is_stable(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: GDELT Stable
            type: gdelt
            query: fashion
            weight: 0.8
            tags: [gdelt]
        """,
    )

    result = lint_source_pack(path)
    payload = json.loads(result.model_dump_json(indent=2))

    assert list(payload) == [
        "path",
        "source_count",
        "enabled_count",
        "disabled_count",
        "type_counts",
        "tag_counts",
        "findings",
    ]
    assert payload["path"] == str(path)
    assert payload["source_count"] == 1
    assert payload["enabled_count"] == 1
    assert payload["disabled_count"] == 0
    assert payload["type_counts"] == {"gdelt": 1}
    assert payload["tag_counts"] == {"gdelt": 1}
    assert payload["findings"] == []


def test_render_source_pack_lint_table_includes_tag_counts(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: GDELT Runway
            type: gdelt
            query: runway
            weight: 0.8
            tags: [gdelt, runway]
          - name: GDELT Shoes
            type: gdelt
            query: shoes
            weight: 0.8
            tags: [gdelt, shoes]
        """,
    )

    result = lint_source_pack(path)
    lines = render_source_pack_lint_table(result)

    assert lines[:5] == [
        f"Source pack: {path}",
        "Sources: 2 total, 2 enabled, 0 disabled",
        "Types: gdelt=2",
        "Tags: gdelt=2, runway=1, shoes=1",
        "Findings: 0 errors, 0 warnings, 0 info",
    ]
    assert "No source-pack quality findings." in lines


def test_render_source_pack_lint_table_shows_none_for_empty_tag_counts(
    tmp_path: Path,
) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: GDELT Untagged
            type: gdelt
            query: fashion
            weight: 0.8
        """,
    )

    result = lint_source_pack(path)
    lines = render_source_pack_lint_table(result)

    assert lines[:5] == [
        f"Source pack: {path}",
        "Sources: 1 total, 1 enabled, 0 disabled",
        "Types: gdelt=1",
        "Tags: none",
        "Findings: 0 errors, 1 warning, 0 info",
    ]
    assert "warning | missing_tags | GDELT Untagged | tags | Source has no tags." in lines


def test_render_source_pack_lint_table_singularizes_one_finding_count() -> None:
    result = SourcePackLintResult(
        path="sources.yaml",
        source_count=1,
        enabled_count=1,
        disabled_count=0,
        type_counts={"gdelt": 1},
        tag_counts={"gdelt": 1},
        findings=[
            SourcePackFinding(
                severity=SourcePackFindingSeverity.ERROR,
                code="error_code",
                message="Error message.",
            ),
            SourcePackFinding(
                severity=SourcePackFindingSeverity.WARNING,
                code="warning_code",
                message="Warning message.",
            ),
            SourcePackFinding(
                severity=SourcePackFindingSeverity.INFO,
                code="info_code",
                message="Info message.",
            ),
        ],
    )

    lines = render_source_pack_lint_table(result)

    assert "Findings: 1 error, 1 warning, 1 info" in lines


def test_render_source_pack_lint_table_keeps_plural_finding_counts() -> None:
    result = SourcePackLintResult(
        path="sources.yaml",
        source_count=1,
        enabled_count=1,
        disabled_count=0,
        type_counts={"gdelt": 1},
        tag_counts={"gdelt": 1},
        findings=[
            SourcePackFinding(
                severity=SourcePackFindingSeverity.ERROR,
                code="error_one",
                message="Error one.",
            ),
            SourcePackFinding(
                severity=SourcePackFindingSeverity.ERROR,
                code="error_two",
                message="Error two.",
            ),
            SourcePackFinding(
                severity=SourcePackFindingSeverity.WARNING,
                code="warning_one",
                message="Warning one.",
            ),
            SourcePackFinding(
                severity=SourcePackFindingSeverity.WARNING,
                code="warning_two",
                message="Warning two.",
            ),
            SourcePackFinding(
                severity=SourcePackFindingSeverity.INFO,
                code="info_one",
                message="Info one.",
            ),
            SourcePackFinding(
                severity=SourcePackFindingSeverity.INFO,
                code="info_two",
                message="Info two.",
            ),
        ],
    )

    lines = render_source_pack_lint_table(result)

    assert "Findings: 2 errors, 2 warnings, 2 info" in lines

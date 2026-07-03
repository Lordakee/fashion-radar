from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from fashion_radar.community_candidates import (
    CommunityCandidateDirectoryPreview,
    CommunityCandidatePreview,
    preview_community_candidate_directory,
    preview_community_candidates,
    render_community_candidate_directory_table,
    render_community_candidates_table,
)
from fashion_radar.importers.manual_signals import ManualSignalImportError
from fashion_radar.models.entity import EntityDefinition, EntityType
from fashion_radar.settings import CandidateDiscoverySettings, EntityConfig, ScoringSettings

AS_OF = datetime(2026, 6, 13, 12, 0, tzinfo=UTC)


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    headers = [
        "url",
        "title",
        "published_at",
        "summary",
        "source_name",
        "platform",
        "source_weight",
        "collected_at",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def _preview(
    path: Path,
    *,
    settings: CandidateDiscoverySettings | None = None,
    scoring: ScoringSettings | None = None,
    entity_config: EntityConfig | None = None,
    default_source_name: str = "Community Tool Export",
    limit: int | None = 50,
) -> CommunityCandidatePreview:
    return preview_community_candidates(
        path,
        input_format="csv",
        scoring=scoring or ScoringSettings(),
        settings=settings
        or CandidateDiscoverySettings(
            review_min_current_mentions=1,
            review_min_distinct_sources=1,
            min_single_token_mentions=1,
            min_single_token_distinct_sources=1,
        ),
        entity_config=entity_config,
        as_of=AS_OF,
        default_source_name=default_source_name,
        limit=limit,
    )


def _directory_preview(
    directory: Path,
    *,
    pattern: str = "*.csv",
    settings: CandidateDiscoverySettings | None = None,
    scoring: ScoringSettings | None = None,
    entity_config: EntityConfig | None = None,
    default_source_name: str = "Community Tool Export",
    limit: int | None = 50,
) -> CommunityCandidateDirectoryPreview:
    return preview_community_candidate_directory(
        directory,
        input_format="csv",
        pattern=pattern,
        scoring=scoring or ScoringSettings(),
        settings=settings
        or CandidateDiscoverySettings(
            review_min_current_mentions=1,
            review_min_distinct_sources=1,
            min_single_token_mentions=1,
            min_single_token_distinct_sources=1,
        ),
        entity_config=entity_config,
        as_of=AS_OF,
        default_source_name=default_source_name,
        limit=limit,
    )


def _serialized(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def test_preview_community_candidates_counts_current_baseline_and_sources(
    tmp_path: Path,
) -> None:
    path = tmp_path / "community.csv"
    _write_csv(
        path,
        [
            {
                "url": "https://example.com/current-a",
                "title": "Le Teckel bag spotted",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Community A",
                "source_weight": "1.5",
                "collected_at": "2026-06-13T10:00:00Z",
            },
            {
                "url": "https://example.com/current-b",
                "title": "Le Teckel bag street style",
                "published_at": "2026-06-12T09:00:00Z",
                "source_name": "Community B",
                "source_weight": "1",
                "collected_at": "2026-06-12T10:00:00Z",
            },
            {
                "url": "https://example.com/baseline",
                "title": "Le Teckel bag early mention",
                "published_at": "2026-06-01T09:00:00Z",
                "source_name": "Community A",
                "source_weight": "1",
                "collected_at": "2026-06-01T10:00:00Z",
            },
        ],
    )

    preview = _preview(path)

    assert preview.input_format == "csv"
    assert preview.row_count == 3
    assert preview.candidate_count >= 1
    candidate = next(item for item in preview.candidates if item.phrase == "Le Teckel bag")
    assert candidate.current_mentions == 2
    assert candidate.baseline_mentions == 1
    assert candidate.distinct_sources == 2
    assert candidate.growth_ratio is not None
    assert candidate.score > 0


def test_preview_community_candidates_uses_as_of_for_missing_collected_at(
    tmp_path: Path,
) -> None:
    path = tmp_path / "community.csv"
    _write_csv(
        path,
        [
            {
                "url": "https://example.com/current",
                "title": "Slim sneaker appears",
                "published_at": "2026-06-10T09:00:00Z",
                "source_name": "",
            }
        ],
    )

    preview = _preview(path, default_source_name="   ")

    assert preview.source_name == "Community Tool Export"
    assert preview.row_count == 1
    assert preview.candidates[0].first_seen_at == AS_OF.isoformat()
    assert preview.candidates[0].distinct_sources == 1


def test_preview_community_candidates_suppresses_configured_entities(tmp_path: Path) -> None:
    path = tmp_path / "community.csv"
    _write_csv(
        path,
        [
            {
                "url": "https://example.com/margaux",
                "title": "Margaux bag mention",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Community",
                "collected_at": "2026-06-13T10:00:00Z",
            }
        ],
    )
    entity_config = EntityConfig(
        entities=[
            EntityDefinition(
                name="Margaux",
                type=EntityType.PRODUCT,
                aliases=[{"value": "Margaux"}],
                context_terms=["bag"],
            )
        ]
    )

    preview = _preview(path, entity_config=entity_config)

    assert preview.candidates == []


def test_preview_community_candidates_counts_duplicate_phrase_once_per_row(
    tmp_path: Path,
) -> None:
    path = tmp_path / "community.csv"
    _write_csv(
        path,
        [
            {
                "url": "https://example.com/repeated",
                "title": "Le Teckel bag Le Teckel bag Le Teckel bag",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Community",
                "collected_at": "2026-06-13T10:00:00Z",
            }
        ],
    )

    preview = _preview(path)
    candidate = next(item for item in preview.candidates if item.phrase == "Le Teckel bag")

    assert candidate.current_mentions == 1


def test_preview_community_candidates_review_thresholds_filter_candidates(
    tmp_path: Path,
) -> None:
    path = tmp_path / "community.csv"
    _write_csv(
        path,
        [
            {
                "url": "https://example.com/current",
                "title": "Le Teckel bag mention",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Community",
                "collected_at": "2026-06-13T10:00:00Z",
            }
        ],
    )

    preview = _preview(
        path,
        settings=CandidateDiscoverySettings(
            review_min_current_mentions=2,
            review_min_distinct_sources=1,
            min_single_token_mentions=1,
            min_single_token_distinct_sources=1,
        ),
    )

    assert preview.row_count == 1
    assert preview.candidate_count == 0
    assert preview.candidates == []


def test_preview_community_candidates_single_token_threshold_filters_candidates(
    tmp_path: Path,
) -> None:
    path = tmp_path / "community.csv"
    _write_csv(
        path,
        [
            {
                "url": "https://example.com/current",
                "title": "Orion",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Community",
                "collected_at": "2026-06-13T10:00:00Z",
            }
        ],
    )

    preview = _preview(
        path,
        settings=CandidateDiscoverySettings(
            review_min_current_mentions=1,
            review_min_distinct_sources=1,
            min_single_token_mentions=2,
            min_single_token_distinct_sources=1,
        ),
    )

    assert preview.candidate_count == 0
    assert preview.candidates == []


def test_preview_community_candidates_filters_generic_single_token_noise(
    tmp_path: Path,
) -> None:
    path = tmp_path / "community.csv"
    _write_csv(
        path,
        [
            {
                "url": "https://example.com/noise-a",
                "title": "New Plus More Is Spring York",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Community A",
                "collected_at": "2026-06-13T10:00:00Z",
            },
            {
                "url": "https://example.com/noise-b",
                "title": "New Plus More Is Spring York",
                "published_at": "2026-06-13T09:30:00Z",
                "source_name": "Community B",
                "collected_at": "2026-06-13T10:30:00Z",
            },
            {
                "url": "https://example.com/product",
                "title": "Le Teckel bag appears again",
                "published_at": "2026-06-13T11:00:00Z",
                "source_name": "Community C",
                "collected_at": "2026-06-13T11:30:00Z",
            },
        ],
    )

    preview = _preview(
        path,
        settings=CandidateDiscoverySettings(
            review_min_current_mentions=1,
            review_min_distinct_sources=1,
            min_single_token_mentions=1,
            min_single_token_distinct_sources=1,
        ),
    )

    phrases = {candidate.phrase for candidate in preview.candidates}
    assert "Le Teckel bag" in phrases
    assert not {"New", "Plus", "More", "Is", "Spring", "York"} & phrases
    assert "New Plus" not in phrases
    assert "Plus More" not in phrases
    assert "More Is" not in phrases
    assert "Is Spring" not in phrases
    assert "Spring York" not in phrases


def test_preview_community_candidates_disabled_returns_rows_without_candidates(
    tmp_path: Path,
) -> None:
    path = tmp_path / "community.csv"
    _write_csv(
        path,
        [
            {
                "url": "https://example.com/current",
                "title": "Le Teckel bag mention",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Community",
                "collected_at": "2026-06-13T10:00:00Z",
            }
        ],
    )

    preview = _preview(path, settings=CandidateDiscoverySettings(enabled=False))

    assert preview.row_count == 1
    assert preview.candidate_count == 0
    assert preview.candidates == []


def test_preview_community_candidates_limit_zero_preserves_candidate_count(
    tmp_path: Path,
) -> None:
    path = tmp_path / "community.csv"
    _write_csv(
        path,
        [
            {
                "url": "https://example.com/current",
                "title": "Le Teckel bag current mention",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Community",
                "collected_at": "2026-06-13T10:00:00Z",
            }
        ],
    )

    preview = _preview(path, limit=0)

    assert preview.row_count == 1
    assert preview.candidate_count > 0
    assert preview.candidates == []


def test_preview_community_candidate_directory_aggregates_direct_child_csv_files(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "handoffs"
    directory.mkdir()
    nested = directory / "nested"
    nested.mkdir()
    _write_csv(
        directory / "first.csv",
        [
            {
                "url": "https://example.com/current-a",
                "title": "Le Teckel bag spotted",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Community A",
                "collected_at": "2026-06-13T10:00:00Z",
            },
            {
                "url": "https://example.com/baseline",
                "title": "Le Teckel bag early mention",
                "published_at": "2026-06-01T09:00:00Z",
                "source_name": "Community A",
                "collected_at": "2026-06-01T10:00:00Z",
            },
        ],
    )
    _write_csv(
        directory / "second.csv",
        [
            {
                "url": "https://example.com/current-b",
                "title": "Le Teckel bag street style",
                "published_at": "2026-06-12T09:00:00Z",
                "source_name": "Community B",
                "collected_at": "2026-06-12T10:00:00Z",
            }
        ],
    )
    _write_csv(
        nested / "ignored.csv",
        [
            {
                "url": "https://example.com/nested",
                "title": "Nested tote should not count",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Nested Source",
                "collected_at": "2026-06-13T10:00:00Z",
            }
        ],
    )

    preview = _directory_preview(directory)

    assert preview.file_count == 2
    assert preview.row_count == 3
    candidate = next(item for item in preview.candidates if item.phrase == "Le Teckel bag")
    assert candidate.current_mentions == 2
    assert candidate.baseline_mentions == 1
    assert candidate.distinct_sources == 2


def test_preview_community_candidate_directory_pattern_matches_direct_regular_files_only(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "signals"
    directory.mkdir()
    matching_directory = directory / "folder.signal.csv"
    matching_directory.mkdir()
    nested = directory / "nested"
    nested.mkdir()
    _write_csv(
        directory / "direct.signal.csv",
        [
            {
                "url": "https://example.com/direct",
                "title": "Direct tote sighting",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Community Source",
                "collected_at": "2026-06-13T10:00:00Z",
            }
        ],
    )
    _write_csv(
        directory / "ignored.csv",
        [
            {
                "url": "https://example.com/ignored",
                "title": "Ignored bag sighting",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Ignored Source",
                "collected_at": "2026-06-13T10:00:00Z",
            }
        ],
    )
    _write_csv(
        nested / "nested.signal.csv",
        [
            {
                "url": "https://example.com/nested",
                "title": "Nested mule sighting",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Nested Source",
                "collected_at": "2026-06-13T10:00:00Z",
            }
        ],
    )

    preview = _directory_preview(
        directory,
        pattern="*.signal.csv",
        settings=CandidateDiscoverySettings(
            review_min_current_mentions=1,
            review_min_distinct_sources=1,
            min_single_token_mentions=2,
            min_single_token_distinct_sources=1,
        ),
    )

    assert preview.file_count == 1
    assert preview.row_count == 1
    assert [candidate.phrase for candidate in preview.candidates] == ["Direct tote"]
    with pytest.raises(ManualSignalImportError) as exc_info:
        _directory_preview(directory, pattern="**/*.signal.csv")
    message = str(exc_info.value)
    assert message == "input directory could not be read or validated"
    assert "nested.signal.csv" not in message


def test_preview_community_candidate_directory_matches_single_file_preview(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "single"
    directory.mkdir()
    path = directory / "community.csv"
    _write_csv(
        path,
        [
            {
                "url": "https://example.com/current-a",
                "title": "Le Teckel bag spotted",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Community A",
                "collected_at": "2026-06-13T10:00:00Z",
            },
            {
                "url": "https://example.com/baseline",
                "title": "Le Teckel bag early mention",
                "published_at": "2026-06-01T09:00:00Z",
                "source_name": "Community A",
                "collected_at": "2026-06-01T10:00:00Z",
            },
        ],
    )

    single_preview = _preview(path)
    directory_preview = _directory_preview(directory)

    assert directory_preview.file_count == 1
    for field in (
        "input_format",
        "as_of",
        "current_window_start",
        "baseline_window_start",
        "current_days",
        "baseline_days",
        "source_name",
        "row_count",
        "candidate_count",
        "limit",
        "candidates",
    ):
        assert getattr(directory_preview, field) == getattr(single_preview, field)


def test_preview_community_candidate_directory_preserves_row_candidate_rules(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "rules"
    directory.mkdir()
    _write_csv(
        directory / "community.csv",
        [
            {
                "url": "https://example.com/sneaker",
                "title": "Slim sneaker Slim sneaker",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "",
            },
            {
                "url": "https://example.com/margaux",
                "title": "Margaux bag mention",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Community",
                "collected_at": "2026-06-13T10:00:00Z",
            },
        ],
    )
    entity_config = EntityConfig(
        entities=[
            EntityDefinition(
                name="Margaux",
                type=EntityType.PRODUCT,
                aliases=[{"value": "Margaux"}],
                context_terms=["bag"],
            )
        ]
    )

    preview = _directory_preview(
        directory,
        entity_config=entity_config,
        default_source_name="   ",
    )

    assert preview.source_name == "Community Tool Export"
    assert preview.file_count == 1
    assert preview.row_count == 2
    slim = next(candidate for candidate in preview.candidates if candidate.phrase == "Slim sneaker")
    assert slim.first_seen_at == AS_OF.isoformat()
    assert slim.current_mentions == 1
    assert all("Margaux" not in candidate.phrase for candidate in preview.candidates)


def test_preview_community_candidate_directory_thresholds_disable_and_limit_zero(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "thresholds"
    directory.mkdir()
    _write_csv(
        directory / "community.csv",
        [
            {
                "url": "https://example.com/current",
                "title": "Le Teckel bag mention",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Community",
                "collected_at": "2026-06-13T10:00:00Z",
            }
        ],
    )
    token_directory = tmp_path / "single-token"
    token_directory.mkdir()
    _write_csv(
        token_directory / "community.csv",
        [
            {
                "url": "https://example.com/orion",
                "title": "Orion",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Community",
                "collected_at": "2026-06-13T10:00:00Z",
            }
        ],
    )

    thresholded = _directory_preview(
        directory,
        settings=CandidateDiscoverySettings(
            review_min_current_mentions=2,
            review_min_distinct_sources=1,
            min_single_token_mentions=1,
            min_single_token_distinct_sources=1,
        ),
    )
    single_token_thresholded = _directory_preview(
        token_directory,
        settings=CandidateDiscoverySettings(
            review_min_current_mentions=1,
            review_min_distinct_sources=1,
            min_single_token_mentions=2,
            min_single_token_distinct_sources=1,
        ),
    )
    disabled = _directory_preview(directory, settings=CandidateDiscoverySettings(enabled=False))
    limited = _directory_preview(directory, limit=0)

    assert thresholded.file_count == 1
    assert thresholded.row_count == 1
    assert thresholded.candidate_count == 0
    assert thresholded.candidates == []
    assert single_token_thresholded.file_count == 1
    assert single_token_thresholded.row_count == 1
    assert single_token_thresholded.candidate_count == 0
    assert single_token_thresholded.candidates == []
    assert disabled.file_count == 1
    assert disabled.row_count == 1
    assert disabled.candidate_count == 0
    assert disabled.candidates == []
    assert limited.file_count == 1
    assert limited.row_count == 1
    assert limited.candidate_count > 0
    assert limited.candidates == []


def test_preview_community_candidate_directory_labels_scores_and_tie_breaks(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "labels"
    directory.mkdir()
    _write_csv(
        directory / "community.csv",
        [
            {
                "url": "https://example.com/rising-current",
                "title": "Rising mule mention",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Community",
                "collected_at": "2026-06-13T10:00:00Z",
            },
            {
                "url": "https://example.com/rising-baseline",
                "title": "Rising mule mention",
                "published_at": "2026-06-01T09:00:00Z",
                "source_name": "Community",
                "collected_at": "2026-06-01T10:00:00Z",
            },
            {
                "url": "https://example.com/beta",
                "title": "Beta tote mention",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Community",
                "collected_at": "2026-06-13T10:00:00Z",
            },
            {
                "url": "https://example.com/alpha",
                "title": "Alpha tote mention",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Community",
                "collected_at": "2026-06-13T10:00:00Z",
            },
        ],
    )

    preview = _directory_preview(
        directory,
        settings=CandidateDiscoverySettings(
            review_min_current_mentions=1,
            review_min_distinct_sources=1,
            min_single_token_mentions=2,
            min_single_token_distinct_sources=1,
        ),
    )

    by_phrase = {candidate.phrase: candidate for candidate in preview.candidates}
    assert by_phrase["Alpha tote"].label == "new"
    assert by_phrase["Alpha tote"].score > 0
    assert by_phrase["Rising mule"].label == "rising"
    assert by_phrase["Rising mule"].score > 0
    phrases = [candidate.phrase for candidate in preview.candidates]
    assert phrases.index("Alpha tote") < phrases.index("Beta tote")


def test_preview_community_candidate_directory_output_omits_paths_raw_values_and_internals(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "sensitive-client-drop"
    directory.mkdir()
    nested = directory / "private-nested"
    nested.mkdir()
    path = directory / "private-community.csv"
    nested_path = nested / "nested-private.csv"
    _write_csv(
        path,
        [
            {
                "url": "https://private.example.com/local-path",
                "title": "Le Teckel bag PRIVATE_ROW_TITLE",
                "published_at": "2026-06-13T09:00:00Z",
                "summary": "raw private review note",
                "source_name": "Whisper Vault Source",
                "collected_at": "2026-06-13T10:00:00Z",
            }
        ],
    )
    _write_csv(
        nested_path,
        [
            {
                "url": "https://private.example.com/nested",
                "title": "Nested private title",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Nested Source",
                "collected_at": "2026-06-13T10:00:00Z",
            }
        ],
    )

    preview = _directory_preview(directory)
    payload = preview.model_dump(mode="json")
    serialized = _serialized(payload)
    table = "\n".join(render_community_candidate_directory_table(preview))

    assert list(payload) == [
        "input_format",
        "as_of",
        "current_window_start",
        "baseline_window_start",
        "current_days",
        "baseline_days",
        "source_name",
        "file_count",
        "row_count",
        "candidate_count",
        "limit",
        "candidates",
    ]
    assert list(payload["candidates"][0]) == [
        "phrase",
        "candidate_type",
        "label",
        "score",
        "current_mentions",
        "baseline_mentions",
        "distinct_sources",
        "growth_ratio",
        "first_seen_at",
    ]

    forbidden_fragments = {
        str(directory),
        directory.name,
        str(path),
        path.name,
        str(nested_path),
        nested_path.name,
        "https://private.example.com/local-path",
        "https://private.example.com/nested",
        "PRIVATE_ROW_TITLE",
        "raw private review note",
        "Whisper Vault Source",
        "le teckel bag",
        "normalized_key",
        "normalized_phrase",
        "contexts",
        "candidate_contexts",
        "representative_items",
        "source_file",
        "source_path",
        "import_path",
        "account_id",
        "findings",
    }
    for fragment in forbidden_fragments:
        assert fragment not in serialized
        assert fragment not in table


def test_preview_community_candidates_output_omits_paths_raw_values_and_internals(
    tmp_path: Path,
) -> None:
    path = tmp_path / "private-community.csv"
    _write_csv(
        path,
        [
            {
                "url": "https://private.example.com/local-path",
                "title": "Le Teckel bag current mention",
                "published_at": "2026-06-13T09:00:00Z",
                "summary": "raw private review note",
                "source_name": "Community",
                "collected_at": "2026-06-13T10:00:00Z",
            }
        ],
    )

    preview = _preview(path)
    payload = preview.model_dump(mode="json")
    serialized = _serialized(payload)
    table = "\n".join(render_community_candidates_table(preview))

    assert list(payload) == [
        "input_format",
        "as_of",
        "current_window_start",
        "baseline_window_start",
        "current_days",
        "baseline_days",
        "source_name",
        "row_count",
        "candidate_count",
        "limit",
        "candidates",
    ]
    assert list(payload["candidates"][0]) == [
        "phrase",
        "candidate_type",
        "label",
        "score",
        "current_mentions",
        "baseline_mentions",
        "distinct_sources",
        "growth_ratio",
        "first_seen_at",
    ]

    forbidden_fragments = {
        str(path),
        path.name,
        "https://private.example.com/local-path",
        "current mention",
        "raw private review note",
        "normalized_key",
        "normalized_phrase",
        "contexts",
        "representative_items",
        "source_file",
        "source_path",
        "import_path",
        "account_id",
    }
    for fragment in forbidden_fragments:
        assert fragment not in serialized
        assert fragment not in table


def test_render_community_candidates_table_sanitizes_cells() -> None:
    preview = CommunityCandidatePreview(
        input_format="csv",
        as_of="2026-06-13T12:00:00+00:00",
        current_window_start="2026-06-06T12:00:00+00:00",
        baseline_window_start="2026-05-07T12:00:00+00:00",
        source_name="Community | Export",
        row_count=1,
        candidate_count=1,
        candidates=[
            {
                "phrase": "Le Teckel | bag\nprivate",
                "candidate_type": "product",
                "label": "new",
                "score": 1.0,
                "current_mentions": 1,
                "baseline_mentions": 0,
                "distinct_sources": 1,
                "growth_ratio": None,
                "first_seen_at": "2026-06-13T10:00:00+00:00",
            }
        ],
    )

    lines = render_community_candidates_table(preview)
    rendered = "\n".join(lines)

    assert "Source name: Community / Export" in rendered
    assert "Le Teckel / bag private" in rendered

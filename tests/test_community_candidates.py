from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path

from fashion_radar.community_candidates import (
    CommunityCandidatePreview,
    preview_community_candidates,
    render_community_candidates_table,
)
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

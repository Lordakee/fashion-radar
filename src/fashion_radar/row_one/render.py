from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from shutil import rmtree
from typing import Literal

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.briefing_topics import briefing_topics_payload
from fashion_radar.row_one.daily_local_key_signals_digest import (
    build_row_one_daily_local_key_signals_digest,
)
from fashion_radar.row_one.display import display_for_story, safe_story_image_src
from fashion_radar.row_one.local_intelligence import build_row_one_local_article_intelligence
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneDailyLocalIntelligenceSection,
    RowOneEdition,
    RowOneLink,
    RowOneLocalArticle,
    RowOneLocalArticleBriefSection,
    RowOneLocalArticleContentSection,
    RowOneSection,
    RowOneStory,
    RowOneStoryDisplay,
    RowOneStoryImage,
)
from fashion_radar.row_one.readiness import build_row_one_readiness
from fashion_radar.row_one.saved_article_briefs import (
    build_row_one_saved_article_briefs,
)
from fashion_radar.row_one.saved_article_content_organization import (
    RowOneSavedArticleContentOrganization,
    build_row_one_saved_article_content_organization,
)
from fashion_radar.row_one.saved_article_coverage import (
    build_row_one_saved_article_coverage,
)
from fashion_radar.row_one.saved_article_daily_signal_leaderboard import (
    RowOneSavedArticleDailySignalLeaderboard,
    build_row_one_saved_article_daily_signal_leaderboard,
)
from fashion_radar.row_one.saved_article_evidence_board import (
    RowOneSavedArticleEvidenceBoard,
    build_row_one_saved_article_evidence_board,
)
from fashion_radar.row_one.saved_article_key_signals import (
    build_row_one_saved_article_key_signals,
)
from fashion_radar.row_one.saved_article_library import (
    RowOneSavedArticleLibrary,
    build_row_one_saved_article_library,
)
from fashion_radar.row_one.saved_article_local_reading_companion import (
    build_row_one_saved_article_local_reading_companion,
)
from fashion_radar.row_one.saved_article_local_section_binder import (
    build_row_one_saved_article_local_section_binder,
)
from fashion_radar.row_one.saved_article_reading_paths import (
    RowOneSavedArticleReadingPaths,
    build_row_one_saved_article_reading_paths,
)
from fashion_radar.row_one.saved_article_reference_atlas import (
    RowOneSavedArticleReferenceAtlas,
    build_row_one_saved_article_reference_atlas,
)
from fashion_radar.row_one.saved_article_signal_facets import (
    RowOneSavedArticleSignalFacets,
    build_row_one_saved_article_signal_facets,
)
from fashion_radar.row_one.saved_article_theme_digest import (
    RowOneSavedArticleThemeDigest,
    build_row_one_saved_article_theme_digest,
)
from fashion_radar.row_one.saved_signal_index import (
    RowOneSavedSignalIndex,
    build_row_one_saved_signal_index,
)
from fashion_radar.row_one.site_metrics import (
    RowOneLocalArticleSiteMetrics,
    build_row_one_local_article_metrics,
)
from fashion_radar.row_one.templates import (
    EDITORIAL_BRIEF_MAX_ITEMS,
    _EditorialBrief,
    _EditorialBriefItem,
    _EditorialBriefTrailItem,
    _validated_detail_relative_path,
    render_detail_html,
    render_index_html,
    render_local_article_page_html,
    render_saved_article_library_html,
    row_one_css,
    row_one_js,
)
from fashion_radar.row_one.text import clean_row_one_text
from fashion_radar.row_one.utils import isoformat_z, safe_external_url, utc_datetime

# Top-level articles/ is generated HTML. data/articles/ remains the JSON sidecar tree.
GENERATED_CHILDREN = ("index.html", ".row-one-site", "details", "assets", "data", "articles")
ROW_ONE_APP_CONTRACT_VERSION = "row-one-app/v7"
ROW_ONE_MANIFEST_CONTRACT_VERSION = "row-one-manifest/v1"
ROW_ONE_MANIFEST_SCHEMA_PATH = "schemas/row-one-manifest.schema.json"
ROW_ONE_RUNTIME_CONTRACT_VERSION = "row-one-runtime/v1"
ROW_ONE_RUNTIME_SCHEMA_PATH = "schemas/row-one-runtime.schema.json"


@dataclass(frozen=True)
class RowOneRenderResult:
    output_dir: Path
    index_path: Path
    story_count: int
    edition: RowOneEdition
    local_article_metrics: RowOneLocalArticleSiteMetrics


def render_row_one_site(
    edition: RowOneEdition,
    output_dir: Path,
    *,
    latest_only: bool = False,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle] | None = None,
) -> RowOneRenderResult:
    _validate_unique_story_routes(edition)
    if latest_only:
        clean_row_one_site_children(output_dir)
    local_articles_by_story_id = local_articles_by_story_id or {}
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")
    _write_assets(output_dir)
    app_payload = build_row_one_app_payload(edition)
    local_article_intelligence = build_row_one_local_article_intelligence(
        edition,
        local_articles_by_story_id,
    )
    saved_article_coverage = build_row_one_saved_article_coverage(
        edition,
        local_articles_by_story_id,
    )
    saved_article_briefs = build_row_one_saved_article_briefs(
        edition,
        local_articles_by_story_id,
    )
    daily_local_key_signals_digest = build_row_one_daily_local_key_signals_digest(
        edition,
        local_articles_by_story_id,
    )
    saved_article_content_organization = build_row_one_saved_article_content_organization(
        edition,
        local_articles_by_story_id,
    )
    saved_article_library = build_row_one_saved_article_library(
        edition,
        local_articles_by_story_id,
    )
    saved_signal_index = build_row_one_saved_signal_index(
        edition,
        local_articles_by_story_id,
    )
    saved_article_reading_paths = build_row_one_saved_article_reading_paths(
        saved_article_library,
        saved_article_content_organization,
    )
    saved_article_theme_digest = build_row_one_saved_article_theme_digest(
        saved_article_library,
        saved_article_content_organization,
    )
    saved_article_reference_atlas = build_row_one_saved_article_reference_atlas(
        saved_article_library,
        saved_article_content_organization,
    )
    saved_article_signal_facets = build_row_one_saved_article_signal_facets(
        saved_article_library,
        saved_article_content_organization,
    )
    saved_article_daily_signal_leaderboard = build_row_one_saved_article_daily_signal_leaderboard(
        saved_article_signal_facets
    )
    saved_article_evidence_board = build_row_one_saved_article_evidence_board(
        edition,
        saved_article_library,
        saved_article_content_organization,
        local_articles_by_story_id,
    )
    local_article_page_specs = _local_article_page_specs(
        edition,
        local_articles_by_story_id=local_articles_by_story_id,
    )
    local_article_page_hrefs_by_detail_path = _local_article_page_hrefs_by_detail_path(
        local_article_page_specs
    )
    local_article_page_hrefs_by_story_id = _local_article_page_hrefs_by_story_id(
        local_article_page_specs
    )
    editorial_brief = _editorial_brief_payload(edition, local_articles_by_story_id)
    index_path = output_dir / "index.html"
    index_path.write_text(
        render_index_html(
            edition,
            app_payload=app_payload,
            local_article_intelligence=local_article_intelligence,
            saved_article_coverage=saved_article_coverage,
            saved_article_library=saved_article_library,
            saved_signal_index=saved_signal_index,
            saved_article_briefs=saved_article_briefs,
            daily_local_key_signals_digest=daily_local_key_signals_digest,
            daily_local_signal_momentum=saved_article_daily_signal_leaderboard,
            daily_local_signal_momentum_hrefs_by_detail_path=(
                local_article_page_hrefs_by_detail_path
            ),
            daily_local_heat_signals_article_hrefs_by_story_id=(
                local_article_page_hrefs_by_story_id
            ),
            daily_local_article_capsules_article_hrefs_by_story_id=(
                local_article_page_hrefs_by_story_id
            ),
            saved_article_content_organization=saved_article_content_organization,
            editorial_brief=editorial_brief,
            local_articles_by_story_id=local_articles_by_story_id,
        ),
        encoding="utf-8",
    )
    _write_detail_pages(
        edition,
        output_dir / "details",
        local_articles_by_story_id=local_articles_by_story_id,
    )
    _write_saved_article_library_page(
        edition,
        output_dir / "articles",
        saved_article_library=saved_article_library,
        saved_signal_index=saved_signal_index,
        saved_article_content_organization=saved_article_content_organization,
        saved_article_reading_paths=saved_article_reading_paths,
        saved_article_theme_digest=saved_article_theme_digest,
        saved_article_reference_atlas=saved_article_reference_atlas,
        saved_article_signal_facets=saved_article_signal_facets,
        saved_article_daily_signal_leaderboard=saved_article_daily_signal_leaderboard,
        saved_article_evidence_board=saved_article_evidence_board,
        local_articles_by_story_id=local_articles_by_story_id,
        local_article_page_specs=local_article_page_specs,
        local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
    )
    data_dir = output_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "edition.json").write_text(
        json.dumps(app_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    runtime_payload = build_row_one_runtime_payload(edition, app_payload)
    (data_dir / "runtime.json").write_text(
        json.dumps(runtime_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    manifest_payload = build_row_one_manifest_payload(edition, app_payload)
    (data_dir / "manifest.json").write_text(
        json.dumps(manifest_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    writable_local_articles = _writable_local_articles(edition, local_articles_by_story_id)
    _write_local_article_files(data_dir, writable_local_articles)
    _write_local_article_intelligence_file(data_dir, local_article_intelligence)
    return RowOneRenderResult(
        output_dir=output_dir,
        index_path=index_path,
        story_count=len(edition.stories),
        edition=edition,
        local_article_metrics=build_row_one_local_article_metrics(writable_local_articles.values()),
    )


def _validate_unique_story_routes(edition: RowOneEdition) -> None:
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for story in edition.stories:
        if story.id in seen_ids:
            raise ValueError(f"Duplicate ROW ONE story id: {story.id}")
        seen_ids.add(story.id)
        if story.detail_path in seen_paths:
            raise ValueError(f"Duplicate ROW ONE detail path: {story.detail_path}")
        seen_paths.add(story.detail_path)


def clean_row_one_site_children(output_dir: Path) -> None:
    if not output_dir.exists():
        return
    marker = output_dir / ".row-one-site"
    generated_children = [output_dir / child_name for child_name in GENERATED_CHILDREN]
    has_generated_children = any(child.exists() for child in generated_children if child != marker)
    if has_generated_children and not marker.exists():
        raise ValueError(f"ROW ONE output directory is not marked as generated: {output_dir}")
    for child_name in GENERATED_CHILDREN:
        child = output_dir / child_name
        if child.is_dir():
            rmtree(child)
        elif child.exists():
            child.unlink()


def _write_assets(output_dir: Path) -> None:
    assets_dir = output_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    (assets_dir / "row-one.css").write_text(row_one_css(), encoding="utf-8")
    (assets_dir / "row-one.js").write_text(row_one_js(), encoding="utf-8")


def _write_detail_pages(
    edition: RowOneEdition,
    details_dir: Path,
    *,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
) -> None:
    details_dir.mkdir(parents=True, exist_ok=True)
    for story in edition.stories:
        pure_path = _validated_detail_relative_path(story.detail_path)
        if pure_path is None:
            raise ValueError(f"Invalid ROW ONE detail path: {story.detail_path}")
        detail_path = details_dir.parent / Path(*pure_path.parts)
        if detail_path.parent != details_dir:
            raise ValueError(f"Invalid ROW ONE detail path: {story.detail_path}")
        detail_path.write_text(
            render_detail_html(
                edition,
                story,
                local_article=local_articles_by_story_id.get(story.id),
            ),
            encoding="utf-8",
        )


def _write_saved_article_library_page(
    edition: RowOneEdition,
    articles_dir: Path,
    *,
    saved_article_library: RowOneSavedArticleLibrary | None,
    saved_signal_index: RowOneSavedSignalIndex | None,
    saved_article_content_organization: RowOneSavedArticleContentOrganization | None,
    saved_article_reading_paths: RowOneSavedArticleReadingPaths | None,
    saved_article_theme_digest: RowOneSavedArticleThemeDigest | None,
    saved_article_reference_atlas: RowOneSavedArticleReferenceAtlas | None,
    saved_article_signal_facets: RowOneSavedArticleSignalFacets | None,
    saved_article_daily_signal_leaderboard: RowOneSavedArticleDailySignalLeaderboard | None,
    saved_article_evidence_board: RowOneSavedArticleEvidenceBoard | None,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    local_article_page_specs: Sequence[tuple[RowOneStory, RowOneLocalArticle, str, str]]
    | None = None,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None = None,
) -> None:
    if saved_article_library is None:
        return
    articles_dir.mkdir(parents=True, exist_ok=True)
    article_page_hrefs_by_detail_path = _write_local_article_pages(
        edition,
        articles_dir,
        local_articles_by_story_id=local_articles_by_story_id,
        saved_article_library=saved_article_library,
        saved_article_content_organization=saved_article_content_organization,
        local_article_page_specs=local_article_page_specs,
        local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
    )
    (articles_dir / "index.html").write_text(
        render_saved_article_library_html(
            edition,
            saved_article_library,
            saved_signal_index=saved_signal_index,
            saved_article_content_organization=saved_article_content_organization,
            saved_article_reading_paths=saved_article_reading_paths,
            saved_article_theme_digest=saved_article_theme_digest,
            saved_article_reference_atlas=saved_article_reference_atlas,
            saved_article_signal_facets=saved_article_signal_facets,
            saved_article_daily_signal_leaderboard=saved_article_daily_signal_leaderboard,
            saved_article_evidence_board=saved_article_evidence_board,
            local_article_page_hrefs_by_detail_path=article_page_hrefs_by_detail_path,
        ),
        encoding="utf-8",
    )


def _local_article_page_href(story_id: str) -> str | None:
    if not safe_local_article_story_id(story_id):
        return None
    return f"{story_id}.html"


def _local_article_page_hrefs_by_detail_path(
    local_article_page_specs: Sequence[tuple[RowOneStory, RowOneLocalArticle, str, str]],
) -> dict[str, str]:
    return {
        detail_path: article_page_href
        for _story, _article, article_page_href, detail_path in local_article_page_specs
    }


def _local_article_page_hrefs_by_story_id(
    local_article_page_specs: Sequence[tuple[RowOneStory, RowOneLocalArticle, str, str]],
) -> dict[str, str]:
    return {
        story.id: article_page_href
        for story, _article, article_page_href, _detail_path in local_article_page_specs
    }


def _write_local_article_pages(
    edition: RowOneEdition,
    articles_dir: Path,
    *,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    saved_article_library: RowOneSavedArticleLibrary | None = None,
    saved_article_content_organization: RowOneSavedArticleContentOrganization | None = None,
    local_article_page_specs: Sequence[tuple[RowOneStory, RowOneLocalArticle, str, str]]
    | None = None,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None = None,
) -> dict[str, str]:
    if local_article_page_specs is None and local_article_page_hrefs_by_detail_path is not None:
        raise ValueError(
            "local_article_page_hrefs_by_detail_path requires local_article_page_specs"
        )
    page_specs = (
        list(local_article_page_specs)
        if local_article_page_specs is not None
        else _local_article_page_specs(
            edition,
            local_articles_by_story_id=local_articles_by_story_id,
        )
    )
    hrefs_by_detail_path = (
        dict(local_article_page_hrefs_by_detail_path)
        if local_article_page_hrefs_by_detail_path is not None
        else _local_article_page_hrefs_by_detail_path(page_specs)
    )
    for story, article, article_page_href, _detail_path in page_specs:
        companion = build_row_one_saved_article_local_reading_companion(
            story=story,
            local_article=article,
            library=saved_article_library,
            organization=saved_article_content_organization,
            local_article_page_hrefs_by_detail_path=hrefs_by_detail_path,
        )
        binder = build_row_one_saved_article_local_section_binder(
            story=story,
            local_article=article,
        )
        key_signals = build_row_one_saved_article_key_signals(
            story=story,
            local_article=article,
        )
        html = render_local_article_page_html(
            edition,
            story,
            local_article=article,
            saved_article_local_reading_companion=companion,
            saved_article_local_section_binder=binder,
            saved_article_key_signals=key_signals,
        )
        if not html:
            continue
        (articles_dir / article_page_href).write_text(html, encoding="utf-8")
    return hrefs_by_detail_path


def _local_article_page_specs(
    edition: RowOneEdition,
    *,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
) -> list[tuple[RowOneStory, RowOneLocalArticle, str, str]]:
    page_specs: list[tuple[RowOneStory, RowOneLocalArticle, str, str]] = []
    for story in edition.stories:
        article = local_articles_by_story_id.get(story.id)
        if article is None or article.story_id != story.id:
            continue
        if not any(paragraph.strip() for paragraph in article.paragraphs):
            continue
        article_page_href = _local_article_page_href(story.id)
        if article_page_href is None:
            continue
        pure_detail_path = _validated_detail_relative_path(story.detail_path)
        if pure_detail_path is None:
            continue
        page_specs.append((story, article, article_page_href, str(pure_detail_path)))
    return page_specs


def _writable_local_articles(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
) -> dict[str, RowOneLocalArticle]:
    current_story_ids = {story.id for story in edition.stories}
    return {
        story_id: article
        for story_id, article in local_articles_by_story_id.items()
        if story_id in current_story_ids
        and safe_local_article_story_id(story_id)
        and article.paragraphs
    }


def _write_local_article_files(
    data_dir: Path,
    writable_articles: Mapping[str, RowOneLocalArticle],
) -> None:
    if not writable_articles:
        return
    articles_dir = data_dir / "articles"
    articles_dir.mkdir(parents=True, exist_ok=True)
    for story_id, article in sorted(writable_articles.items()):
        (articles_dir / f"{story_id}.json").write_text(
            json.dumps(article.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def _write_local_article_intelligence_file(
    data_dir: Path,
    sections: Sequence[RowOneDailyLocalIntelligenceSection],
) -> None:
    writable_sections = [section for section in sections if section.items]
    if not writable_sections:
        return
    (data_dir / "local-intelligence.json").write_text(
        json.dumps(
            [section.model_dump(mode="json") for section in writable_sections],
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _editorial_brief_payload(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
) -> _EditorialBrief | None:
    story = _lead_story_for_editorial_brief(edition)
    if story is None:
        return None
    local_article = local_articles_by_story_id.get(story.id)
    items = _editorial_brief_items(story, local_article)
    if not items:
        return None
    return _EditorialBrief(items=tuple(items[:EDITORIAL_BRIEF_MAX_ITEMS]))


def _lead_story_for_editorial_brief(edition: RowOneEdition) -> RowOneStory | None:
    # Stories are already ranked for the edition; fall through only if the first row has no prose.
    for story in edition.stories:
        if _story_localized_text_has_content(story.editorial_takeaway):
            return story
        if _story_localized_text_has_content(story.summary):
            return story
    return None


def _story_localized_text_has_content(text: LocalizedText) -> bool:
    return bool(clean_row_one_text(text.en) or clean_row_one_text(text.zh))


def _editorial_brief_items(
    story: RowOneStory,
    local_article: RowOneLocalArticle | None,
) -> list[_EditorialBriefItem]:
    detail_href = _editorial_brief_detail_href(story)
    what_happened = _local_article_brief_section(local_article, "what_happened")
    why_it_matters = _local_article_brief_section(local_article, "why_it_matters")
    watch_next = _local_article_brief_section(local_article, "watch_next")
    items = [
        _EditorialBriefItem(
            title=LocalizedText(en="What changed today", zh="今日变化"),
            body=_combined_editorial_body(
                story.editorial_takeaway
                if _story_localized_text_has_content(story.editorial_takeaway)
                else story.summary,
                what_happened.body if what_happened is not None else None,
            ),
            meta=_editorial_brief_meta(local_article),
            href=detail_href,
            trail=_editorial_brief_source_trail(
                story,
                local_article,
                brief_key="what_happened",
                brief_href_target="paragraph_or_detail",
                content_keys=(),
                include_first_paragraph=False,
            ),
        ),
        _EditorialBriefItem(
            title=LocalizedText(en="Why it matters", zh="为什么重要"),
            body=_combined_editorial_body(
                story.why_it_matters
                if _story_localized_text_has_content(story.why_it_matters)
                else story.signal_context,
                why_it_matters.body if why_it_matters is not None else None,
            ),
            href=detail_href,
            trail=_editorial_brief_source_trail(
                story,
                local_article,
                brief_key="why_it_matters",
                brief_href_target="detail",
                content_keys=("entities", "brand_signals", "takeaways"),
                include_first_paragraph=False,
            ),
        ),
        _EditorialBriefItem(
            title=LocalizedText(en="What to read locally", zh="本地阅读路径"),
            body=_combined_editorial_body(
                watch_next.body if watch_next is not None else story.reader_path,
                None,
            ),
            href=_editorial_brief_paragraph_href(story, local_article) or detail_href,
            trail=_editorial_brief_source_trail(
                story,
                local_article,
                brief_key="watch_next",
                brief_href_target="paragraph_or_detail",
                content_keys=("takeaways",),
                include_first_paragraph=watch_next is None,
            ),
        ),
    ]
    return _deduped_editorial_brief_items(items)


def _deduped_editorial_brief_items(
    items: Sequence[_EditorialBriefItem],
) -> list[_EditorialBriefItem]:
    deduped: list[_EditorialBriefItem] = []
    seen_bodies: set[tuple[str, str]] = set()
    for item in items:
        body = LocalizedText(
            en=clean_row_one_text(item.body.en),
            zh=clean_row_one_text(item.body.zh),
        )
        if not _story_localized_text_has_content(body):
            continue
        body_key = (body.en, body.zh)
        if body_key in seen_bodies:
            continue
        seen_bodies.add(body_key)
        deduped.append(
            _EditorialBriefItem(
                title=item.title,
                body=body,
                meta=item.meta,
                href=item.href,
                trail=item.trail,
            )
        )
    return deduped


def _editorial_brief_source_trail(
    story: RowOneStory,
    local_article: RowOneLocalArticle | None,
    *,
    brief_key: str | None = None,
    brief_href_target: Literal["paragraph_or_detail", "detail"] = "paragraph_or_detail",
    content_keys: tuple[str, ...] = (),
    include_first_paragraph: bool = False,
) -> tuple[_EditorialBriefTrailItem, ...]:
    """Build stable trail payloads; template display-normalized dedupe is a safety net."""
    if local_article is None:
        return ()
    items: list[_EditorialBriefTrailItem] = []
    if brief_key is not None:
        section = _local_article_brief_section(local_article, brief_key)
        if section is not None:
            brief_href = _editorial_brief_detail_href(story)
            if brief_href_target == "paragraph_or_detail":
                brief_href = _editorial_brief_paragraph_href(story, local_article) or brief_href
            elif brief_href_target == "detail":
                pass
            items.append(
                _EditorialBriefTrailItem(
                    label=section.title,
                    href=brief_href,
                )
            )
    content_section = _first_local_article_content_section(local_article, content_keys)
    if content_section is not None:
        position, section = content_section
        content_href = _editorial_brief_content_section_href(story, position)
        if content_href is not None:
            items.append(_EditorialBriefTrailItem(label=section.title, href=content_href))
    if include_first_paragraph:
        paragraph_href = _editorial_brief_paragraph_href(story, local_article)
        existing_hrefs = {item.href for item in items if item.href is not None}
        if paragraph_href is not None and paragraph_href not in existing_hrefs:
            items.append(
                _EditorialBriefTrailItem(
                    label=LocalizedText(en="Saved paragraph 1", zh="保存段落 1"),
                    href=paragraph_href,
                )
            )
    return _deduped_editorial_brief_trail(items)


def _first_local_article_content_section(
    local_article: RowOneLocalArticle | None,
    keys: tuple[str, ...],
) -> tuple[int, RowOneLocalArticleContentSection] | None:
    if local_article is None:
        return None
    for key in keys:
        for position, section in enumerate(local_article.content_sections, start=1):
            if section.key == key:
                return (position, section)
    return None


def _editorial_brief_content_section_href(
    story: RowOneStory,
    position: int,
) -> str | None:
    detail_href = _editorial_brief_detail_href(story)
    if detail_href is None or position < 1:
        return None
    return f"{detail_href}#local-article-content-section-{position}"


def _deduped_editorial_brief_trail(
    items: Sequence[_EditorialBriefTrailItem],
) -> tuple[_EditorialBriefTrailItem, ...]:
    deduped: list[_EditorialBriefTrailItem] = []
    seen: set[tuple[str, str, str | None]] = set()
    for item in items:
        label = LocalizedText(
            en=clean_row_one_text(item.label.en),
            zh=clean_row_one_text(item.label.zh),
        )
        if not (label.en or label.zh):
            continue
        key = (label.en.casefold(), label.zh.casefold(), item.href)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(_EditorialBriefTrailItem(label=label, href=item.href))
    return tuple(deduped)


def _local_article_brief_section(
    local_article: RowOneLocalArticle | None,
    key: str,
) -> RowOneLocalArticleBriefSection | None:
    if local_article is None:
        return None
    for section in local_article.brief_sections:
        if section.key == key and _story_localized_text_has_content(section.body):
            return section
    return None


def _combined_editorial_body(
    primary: LocalizedText,
    extra: LocalizedText | None,
) -> LocalizedText:
    primary_en = clean_row_one_text(primary.en)
    primary_zh = clean_row_one_text(primary.zh)
    if extra is None:
        return LocalizedText(
            en=primary_en,
            zh=primary_zh,
        )
    extra_en = clean_row_one_text(extra.en)
    extra_zh = clean_row_one_text(extra.zh)
    return LocalizedText(
        en=_join_editorial_brief_parts(primary_en, extra_en),
        zh=_join_editorial_brief_parts(primary_zh, extra_zh),
    )


def _join_editorial_brief_parts(primary: str, extra: str) -> str:
    if not primary:
        return extra
    if not extra or extra == primary:
        return primary
    return f"{primary} {extra}"


def _editorial_brief_meta(local_article: RowOneLocalArticle | None) -> LocalizedText | None:
    if local_article is None:
        return None
    title = clean_row_one_text(local_article.title or "")
    source_name = clean_row_one_text(local_article.source_name)
    if source_name and title:
        meta = f"{source_name} · {title}"
    else:
        meta = source_name or title
    return LocalizedText(en=meta, zh=meta) if meta else None


def _editorial_brief_detail_href(story: RowOneStory) -> str | None:
    pure_path = _validated_detail_relative_path(story.detail_path)
    return str(pure_path) if pure_path is not None else None


def _editorial_brief_paragraph_href(
    story: RowOneStory,
    local_article: RowOneLocalArticle | None,
) -> str | None:
    detail_href = _editorial_brief_detail_href(story)
    if detail_href is None or local_article is None:
        return None
    for index, paragraph in enumerate(local_article.paragraphs, start=1):
        if paragraph.strip():
            return f"{detail_href}#local-article-paragraph-{index}"
    return None


def build_row_one_app_payload(edition: RowOneEdition) -> dict[str, object]:
    stories = [_story_payload(edition, story) for story in edition.stories]
    sections = [_section_payload(edition, section) for section in edition.sections]
    content_sections = [_content_section_payload(section, stories) for section in edition.sections]
    daily_digest = _daily_digest_payload(edition, stories)
    story_directory = _story_directory_payload(stories)
    evidence_count = sum(_safe_evidence_count(story.evidence) for story in edition.stories)
    return {
        "contract_version": ROW_ONE_APP_CONTRACT_VERSION,
        "brand": edition.brand,
        "generated_at": isoformat_z(edition.generated_at),
        "edition_date": isoformat_z(edition.edition_date),
        "summary": edition.summary.model_dump(mode="json"),
        "edition_brief": _edition_brief_payload(
            stories,
            content_sections,
            daily_digest,
            story_directory,
            evidence_count,
        ),
        "signal_synthesis": _signal_synthesis_payload(stories),
        "sections": sections,
        "content_sections": content_sections,
        "daily_digest": daily_digest,
        "story_directory": story_directory,
        "stories": stories,
        "story_count": len(stories),
        "evidence_count": evidence_count,
    }


SIGNAL_SYNTHESIS_GROUPS = (
    ("brand", {"zh": "品牌", "en": "Brands"}),
    ("product", {"zh": "单品", "en": "Products"}),
    ("designer", {"zh": "设计师", "en": "Designers"}),
    ("person", {"zh": "人物", "en": "People"}),
)
SIGNAL_SYNTHESIS_BOUNDARIES = {
    "zh": "本地观察，需人工复核。",
    "en": "Local observed signals; review required.",
}


def _signal_synthesis_payload(stories: list[dict[str, object]]) -> dict[str, object]:
    groups = _signal_synthesis_groups(stories)
    signal_count = sum(int(group["signal_count"]) for group in groups)
    return {
        "title": {"zh": "今日信号整理", "en": "Signal Synthesis"},
        "dek": _signal_synthesis_dek(len(stories), signal_count),
        "group_count": len(groups),
        "signal_count": signal_count,
        "boundaries": dict(SIGNAL_SYNTHESIS_BOUNDARIES),
        "groups": groups,
    }


def _signal_synthesis_groups(stories: list[dict[str, object]]) -> list[dict[str, object]]:
    story_href_by_id = _signal_story_href_map(stories)
    grouped: dict[str, list[dict[str, object]]] = {
        key: [] for key, _label in SIGNAL_SYNTHESIS_GROUPS
    }
    for topic in briefing_topics_payload(stories):
        signal = _signal_payload_from_topic(topic, story_href_by_id)
        if signal is None:
            continue
        grouped[str(signal["type"])].append(signal)

    groups: list[dict[str, object]] = []
    for group_key, group_label in SIGNAL_SYNTHESIS_GROUPS:
        signals = sorted(grouped[group_key], key=_signal_synthesis_sort_key)
        if not signals:
            continue
        groups.append(
            {
                "key": group_key,
                "label": dict(group_label),
                "signal_count": len(signals),
                "signals": signals,
            }
        )
    return groups


def _signal_payload_from_topic(
    topic: dict[str, object],
    story_href_by_id: dict[str, str],
) -> dict[str, object] | None:
    topic_type = str(topic.get("topic_type", ""))
    if topic_type not in {group_key for group_key, _label in SIGNAL_SYNTHESIS_GROUPS}:
        return None
    story_ids = [str(story_id) for story_id in topic.get("story_ids", [])]
    if not story_ids:
        return None
    story_refs = _signal_story_refs_from_topic(topic)
    story_ref_ids = [str(ref["story_id"]) for ref in story_refs]
    if story_ref_ids != story_ids:
        raise ValueError("ROW ONE signal story_refs must align with topic story_ids")
    lead_story_id = str(topic.get("lead_story_id") or story_ids[0])
    lead_story_href = story_href_by_id.get(lead_story_id)
    if lead_story_href is None:
        return None
    title = topic.get("title")
    name = ""
    if isinstance(title, dict):
        name = str(title.get("en") or title.get("zh") or "").strip()
    if not name:
        return None
    label = _signal_reference_label(topic.get("source_refs"))
    story_count = int(topic.get("story_count", 0))
    evidence_count = int(topic.get("evidence_count", 0))
    positive_heat_delta_sum = int(topic.get("positive_heat_delta_sum", 0))
    max_heat_delta = int(topic.get("max_heat_delta", 0))
    return {
        "name": name,
        "type": topic_type,
        "label": label,
        "story_count": story_count,
        "evidence_count": evidence_count,
        "positive_heat_delta_sum": max(positive_heat_delta_sum, 0),
        "max_heat_delta": max(max_heat_delta, 0),
        "lead_story_id": lead_story_id,
        "lead_story_href": lead_story_href,
        "summary": _signal_summary(
            name,
            story_count=story_count,
            evidence_count=evidence_count,
            max_heat_delta=max(max_heat_delta, 0),
        ),
        "story_ids": story_ids,
        "story_refs": story_refs,
    }


def _signal_story_refs_from_topic(topic: dict[str, object]) -> list[dict[str, object]]:
    cards = topic.get("cards")
    if not isinstance(cards, list):
        return []
    refs: list[dict[str, object]] = []
    for card in cards:
        if not isinstance(card, dict):
            continue
        section = card.get("section")
        if not isinstance(section, dict):
            continue
        refs.append(
            {
                "story_id": card["id"],
                "headline": card["headline"],
                "section_key": card["section_key"],
                "section_title": section["title"],
                "detail_href": card["detail_href"],
                "source_name": card["source_name"],
                "published_date": card["published_date"],
                "evidence_count": card["evidence_count"],
                "heat_delta": card["heat_delta"],
            }
        )
    return refs


def _signal_reference_label(source_refs: object) -> str:
    if not isinstance(source_refs, list):
        return ""
    for source_ref in source_refs:
        if not isinstance(source_ref, dict):
            continue
        label = str(source_ref.get("label", "")).strip()
        if label:
            return label
    return ""


def _signal_summary(
    name: str,
    *,
    story_count: int,
    evidence_count: int,
    max_heat_delta: int,
) -> dict[str, str]:
    story_word = _plural_word(story_count, "story", "stories")
    evidence_word = _plural_word(evidence_count, "evidence link", "evidence links")
    return {
        "zh": (
            f"{name} 出现在 {story_count} 条故事中，最高本地提及增量 +{max_heat_delta}，"
            f"带有 {evidence_count} 条证据链接。"
        ),
        "en": (
            f"{name} appears in {story_count} {story_word}, with max local mention delta "
            f"+{max_heat_delta} and {evidence_count} {evidence_word}."
        ),
    }


def _signal_synthesis_dek(story_count: int, signal_count: int) -> dict[str, str]:
    if signal_count == 0:
        return {
            "zh": "暂无可整理的 ROW ONE 信号。",
            "en": "No ROW ONE signals are ready to organize yet.",
        }
    signal_word = _plural_word(signal_count, "readable signal", "readable signals")
    story_word = _plural_word(story_count, "story", "stories")
    return {
        "zh": f"ROW ONE 从今日 {story_count} 条故事中整理出 {signal_count} 个可读信号。",
        "en": (
            f"ROW ONE organized {signal_count} {signal_word} from {story_count} {story_word} today."
        ),
    }


def _signal_story_href_map(stories: list[dict[str, object]]) -> dict[str, str]:
    hrefs: dict[str, str] = {}
    for story in stories:
        story_id = str(story.get("id", ""))
        detail_href = str(story.get("detail_href", ""))
        if story_id and detail_href:
            hrefs[story_id] = detail_href
    return hrefs


def _signal_synthesis_sort_key(signal: dict[str, object]) -> tuple[object, ...]:
    return (
        -int(signal["positive_heat_delta_sum"]),
        -int(signal["evidence_count"]),
        -int(signal["story_count"]),
        str(signal["name"]).casefold(),
        str(signal["name"]),
    )


def build_row_one_manifest_payload(
    edition: RowOneEdition,
    app_payload: dict[str, object] | None = None,
) -> dict[str, object]:
    app_payload = app_payload or build_row_one_app_payload(edition)
    story_count = int(app_payload["story_count"])
    return {
        "contract_version": ROW_ONE_MANIFEST_CONTRACT_VERSION,
        "brand": edition.brand,
        "generated_at": app_payload["generated_at"],
        "edition_date": app_payload["edition_date"],
        "manifest_schema_path": ROW_ONE_MANIFEST_SCHEMA_PATH,
        "app_contract": {
            "version": ROW_ONE_APP_CONTRACT_VERSION,
            "path": "data/edition.json",
            "schema_path": "schemas/row-one-app.schema.json",
        },
        "site": {
            "index_path": "index.html",
            "data_path": "data/edition.json",
            "manifest_path": "data/manifest.json",
            "assets_path": "assets/",
            "details_path": "details/",
        },
        "counts": {
            "story_count": story_count,
            "section_count": len(edition.sections),
            "evidence_count": app_payload["evidence_count"],
        },
        "readiness": {
            "status": "ready" if story_count > 0 else "empty",
        },
        "capabilities": {
            "bilingual": True,
            "static_site": True,
            "detail_pages": True,
            "sanitized_external_urls": True,
            "latest_only_cleanup": True,
            "seo_metadata": True,
            "structured_story_metadata": True,
        },
    }


def build_row_one_runtime_payload(
    edition: RowOneEdition,
    app_payload: dict[str, object] | None = None,
) -> dict[str, object]:
    app_payload = app_payload or build_row_one_app_payload(edition)
    readiness = build_row_one_readiness(edition)
    return {
        "contract_version": ROW_ONE_RUNTIME_CONTRACT_VERSION,
        "brand": edition.brand,
        "generated_at": isoformat_z(edition.generated_at),
        "edition_date": isoformat_z(edition.edition_date),
        "runtime_schema_path": ROW_ONE_RUNTIME_SCHEMA_PATH,
        "site": {
            "index_path": "index.html",
            "manifest_path": "data/manifest.json",
            "edition_path": "data/edition.json",
            "runtime_path": "data/runtime.json",
        },
        "refresh": {
            "recommended_time": "04:00",
            "command": (
                'fashion-radar row-one refresh --as-of "$AS_OF" --output-dir reports/row-one/site'
            ),
            "latest_only_cleanup": True,
        },
        "serve": {
            "default_host": "127.0.0.1",
            "default_port": 8787,
            "local_url": "http://127.0.0.1:8787",
            "lan_url_hint": "http://<LAN-IP>:8787",
        },
        "counts": {
            "story_count": int(app_payload["story_count"]),
            "section_count": len(edition.sections),
            "evidence_count": int(app_payload["evidence_count"]),
        },
        "readiness": {
            "status": readiness.readiness.en,
            "zh": readiness.readiness.zh,
            "en": readiness.readiness.en,
        },
    }


def _section_payload(edition: RowOneEdition, section: RowOneSection) -> dict[str, object]:
    return {
        "key": section.key,
        "title": section.title.model_dump(mode="json"),
        "dek": section.dek.model_dump(mode="json"),
        "href": f"#{section.key}",
        "story_count": len(edition.section_stories(section.key)),
    }


def _content_section_payload(
    section: RowOneSection,
    stories: list[dict[str, object]],
) -> dict[str, object]:
    section_stories = [story for story in stories if story["section_key"] == section.key]
    story_ids = [str(story["id"]) for story in section_stories]
    return {
        "key": section.key,
        "title": section.title.model_dump(mode="json"),
        "dek": section.dek.model_dump(mode="json"),
        "href": f"#{section.key}",
        "story_count": len(section_stories),
        "lead_story_id": story_ids[0] if story_ids else None,
        "story_ids": story_ids,
        "cards": [_content_card_payload(story) for story in section_stories],
    }


def _daily_digest_payload(
    edition: RowOneEdition,
    stories: list[dict[str, object]],
) -> dict[str, object]:
    read_first_stories = _read_first_digest_stories(stories)
    return {
        "title": {"zh": "今日简报", "en": "Today's Briefing"},
        "dek": _daily_digest_dek(stories),
        "story_count": len(stories),
        "evidence_count": sum(int(story["evidence_count"]) for story in stories),
        "lead_story_id": str(read_first_stories[0]["id"]) if read_first_stories else None,
        "briefing_topics": [
            _content_cards_for_briefing_topic(topic) for topic in briefing_topics_payload(stories)
        ],
        "blocks": [
            _digest_block_payload(
                "read_first",
                {"zh": "先读", "en": "Read First"},
                {
                    "zh": "今日最值得先打开的一条 ROW ONE 信号。",
                    "en": "The first ROW ONE signal to open today.",
                },
                read_first_stories,
            ),
            _digest_block_payload(
                "key_takeaways",
                {"zh": "重点整理", "en": "Key Takeaways"},
                {
                    "zh": "按栏目顺序整理每个非空板块的第一条信号。",
                    "en": "The first signal from each non-empty section, in section order.",
                },
                _key_takeaway_digest_stories(edition, stories),
            ),
            _digest_block_payload(
                "signals_to_watch",
                {"zh": "升温信号", "en": "Signals To Watch"},
                {
                    "zh": "仅按本地原始提及增量筛出的正向变化信号。",
                    "en": "Positive local raw mention deltas worth watching.",
                },
                _signals_to_watch_digest_stories(stories),
            ),
        ],
    }


def _story_directory_payload(stories: list[dict[str, object]]) -> dict[str, object]:
    return {
        "story_count": len(stories),
        "story_ids": [str(story["id"]) for story in stories],
        "routes": [_story_directory_route_payload(story) for story in stories],
    }


def _story_directory_route_payload(story: dict[str, object]) -> dict[str, object]:
    section = story["section"]
    if not isinstance(section, dict):
        raise TypeError("ROW ONE story section payload must be an object")
    return {
        "story_id": story["id"],
        "detail_href": story["detail_href"],
        "section_key": story["section_key"],
        "section_href": section["href"],
        "published_date": story["published_date"],
    }


def _edition_brief_payload(
    stories: list[dict[str, object]],
    content_sections: list[dict[str, object]],
    daily_digest: dict[str, object],
    story_directory: dict[str, object],
    evidence_count: int,
) -> dict[str, object]:
    active_sections = [section for section in content_sections if int(section["story_count"]) > 0]
    topics = daily_digest.get("briefing_topics", [])
    topic_count = len(topics) if isinstance(topics, list) else 0
    path_blocks = _edition_brief_path_blocks(daily_digest)
    lead_story = _story_by_id(stories, daily_digest.get("lead_story_id"))
    lead_href = lead_story["detail_href"] if lead_story is not None else None
    lead_headline = str(lead_story["headline"]) if lead_story is not None else None
    return {
        "title": {"zh": "今日总览", "en": "Edition Brief"},
        "dek": _edition_brief_dek(
            len(stories), len(active_sections), topic_count, len(path_blocks)
        ),
        "lead_story_id": daily_digest.get("lead_story_id"),
        "lead_story_href": lead_href,
        "lead_story_headline": lead_headline,
        "story_directory_story_count": story_directory["story_count"],
        "metrics": [
            _edition_brief_metric("stories", {"zh": "故事", "en": "Stories"}, len(stories)),
            _edition_brief_metric(
                "sections",
                {"zh": "活跃栏目", "en": "Active Sections"},
                len(active_sections),
            ),
            _edition_brief_metric("topics", {"zh": "主题", "en": "Topics"}, topic_count),
            _edition_brief_metric(
                "evidence",
                {"zh": "证据链接", "en": "Evidence Links"},
                evidence_count,
            ),
        ],
        "summary_points": _edition_brief_summary_points(
            lead_story,
            active_sections,
            topics if isinstance(topics, list) else [],
            path_blocks,
            stories,
        ),
        "links": _edition_brief_links(lead_href, topic_count, path_blocks),
    }


def _edition_brief_metric(key: str, label: dict[str, str], value: int) -> dict[str, object]:
    return {"key": key, "label": label, "value": value}


def _story_by_id(stories: list[dict[str, object]], story_id: object) -> dict[str, object] | None:
    return next((story for story in stories if story["id"] == story_id), None)


def _edition_brief_path_blocks(daily_digest: dict[str, object]) -> list[dict[str, object]]:
    blocks = daily_digest.get("blocks", [])
    if not isinstance(blocks, list):
        return []
    digest_blocks = [block for block in blocks if isinstance(block, dict)]
    excluded_story_ids = _read_first_digest_story_ids(digest_blocks)
    return [
        block
        for block in digest_blocks
        if block.get("key") in {"key_takeaways", "signals_to_watch"}
        and _digest_block_cards(block, excluded_story_ids)
    ]


def _read_first_digest_story_ids(blocks: list[dict[str, object]]) -> set[str]:
    read_first_block = next((block for block in blocks if block.get("key") == "read_first"), None)
    if read_first_block is None:
        return set()
    story_ids = read_first_block.get("story_ids")
    if not isinstance(story_ids, list):
        return set()
    return {str(story_id) for story_id in story_ids}


def _digest_block_cards(
    block: dict[str, object],
    excluded_story_ids: set[str],
) -> list[dict[str, object]]:
    cards = block.get("cards")
    if not isinstance(cards, list):
        return []
    return [
        card
        for card in cards
        if isinstance(card, dict) and str(card.get("id")) not in excluded_story_ids
    ]


def _edition_brief_dek(
    story_count: int,
    active_section_count: int,
    topic_count: int,
    path_block_count: int,
) -> dict[str, str]:
    if story_count == 0:
        return {
            "zh": "暂无可整理的 ROW ONE 故事。",
            "en": "No ROW ONE stories are available to organize yet.",
        }
    return {
        "zh": (
            f"ROW ONE 将今日 {story_count} 条本地时尚信号整理成 "
            f"{active_section_count} 个栏目、{topic_count} 个主题和 "
            f"{path_block_count} 条后续阅读路径。"
        ),
        "en": (
            f"ROW ONE organized {story_count} local fashion signals across "
            f"{active_section_count} sections, "
            f"{topic_count} {_plural_word(topic_count, 'briefing topic', 'briefing topics')}, "
            f"and {path_block_count} "
            f"{_plural_word(path_block_count, 'follow-up path block', 'follow-up path blocks')}."
        ),
    }


def _plural_word(count: int, singular: str, plural: str) -> str:
    return singular if count == 1 else plural


EDITION_BRIEF_TOPIC_TYPE_LABELS = {
    "brand": {"zh": "品牌", "en_singular": "brand", "en_plural": "brands"},
    "product": {"zh": "单品", "en_singular": "product", "en_plural": "products"},
    "designer": {"zh": "设计师", "en_singular": "designer", "en_plural": "designers"},
    "person": {"zh": "人物", "en_singular": "person", "en_plural": "people"},
}


def _edition_brief_topic_mix_point(topics: list[object]) -> dict[str, str] | None:
    counts = {topic_type: 0 for topic_type in EDITION_BRIEF_TOPIC_TYPE_LABELS}
    for topic in topics:
        if not isinstance(topic, dict):
            continue
        topic_type = str(topic.get("topic_type", ""))
        if topic_type in counts:
            counts[topic_type] += 1
    active_counts = [(topic_type, count) for topic_type, count in counts.items() if count > 0]
    if not active_counts:
        return None
    zh_parts = [
        f"{EDITION_BRIEF_TOPIC_TYPE_LABELS[topic_type]['zh']} {count}"
        for topic_type, count in active_counts
    ]
    en_parts = []
    for topic_type, count in active_counts:
        labels = EDITION_BRIEF_TOPIC_TYPE_LABELS[topic_type]
        en_parts.append(
            f"{count} {_plural_word(count, labels['en_singular'], labels['en_plural'])}"
        )
    return {
        "zh": f"主题结构：{'、'.join(zh_parts)}",
        "en": f"Topic mix: {', '.join(en_parts)}",
    }


def _edition_brief_heat_watch_point(
    stories: list[dict[str, object]],
) -> dict[str, str] | None:
    positive_heat_deltas = []
    for story in stories:
        heat_delta = story.get("heat_delta")
        if isinstance(heat_delta, int) and not isinstance(heat_delta, bool) and heat_delta > 0:
            positive_heat_deltas.append(heat_delta)
    if not positive_heat_deltas:
        return None
    signal_count = len(positive_heat_deltas)
    max_heat_delta = max(positive_heat_deltas)
    return {
        "zh": f"升温观察：{signal_count} 条正向热度信号，最高 +{max_heat_delta}",
        "en": (
            f"Heat watch: {signal_count} "
            f"{_plural_word(signal_count, 'positive heat signal', 'positive heat signals')}, "
            f"highest +{max_heat_delta}"
        ),
    }


def _edition_brief_summary_points(
    lead_story: dict[str, object] | None,
    active_sections: list[dict[str, object]],
    topics: list[object],
    path_blocks: list[dict[str, object]],
    stories: list[dict[str, object]],
) -> list[dict[str, str]]:
    points: list[dict[str, str]] = []
    if lead_story is not None:
        headline = str(lead_story["headline"])
        points.append({"zh": f"先读：{headline}", "en": f"Read first: {headline}"})
    if active_sections:
        zh_sections = "、".join(str(section["title"]["zh"]) for section in active_sections)
        en_sections = ", ".join(str(section["title"]["en"]) for section in active_sections)
        points.append({"zh": f"活跃栏目：{zh_sections}", "en": f"Active sections: {en_sections}"})
    topic_titles = [
        str(topic["title"]["en"])
        for topic in topics
        if isinstance(topic, dict) and isinstance(topic.get("title"), dict)
    ][:4]
    if topic_titles:
        topic_text = ", ".join(topic_titles)
        points.append({"zh": f"整理主题：{topic_text}", "en": f"Briefing topics: {topic_text}"})
    topic_mix_point = _edition_brief_topic_mix_point(topics)
    if topic_mix_point is not None:
        points.append(topic_mix_point)
    heat_watch_point = _edition_brief_heat_watch_point(stories)
    if heat_watch_point is not None:
        points.append(heat_watch_point)
    if path_blocks:
        zh_blocks = "、".join(str(block["title"]["zh"]) for block in path_blocks)
        en_blocks = ", ".join(str(block["title"]["en"]) for block in path_blocks)
        points.append({"zh": f"后续路径：{zh_blocks}", "en": f"Follow-up path: {en_blocks}"})
    if not points:
        points.append({"zh": "暂无可整理的故事。", "en": "No stories are ready to organize yet."})
    return points


def _edition_brief_links(
    lead_href: object,
    topic_count: int,
    path_blocks: list[dict[str, object]],
) -> list[dict[str, object]]:
    links: list[dict[str, object]] = []
    if isinstance(lead_href, str):
        links.append(
            {
                "key": "read_first",
                "label": {"zh": "先读", "en": "Read First"},
                "href": lead_href,
            }
        )
    if topic_count > 0:
        links.append(
            {
                "key": "topics",
                "label": {"zh": "今日主题", "en": "Briefing Topics"},
                "href": "#briefing-topics",
            }
        )
    if path_blocks:
        links.append(
            {
                "key": "path",
                "label": {"zh": "阅读路径", "en": "Briefing Path"},
                "href": "#briefing-path",
            }
        )
    return links


def _content_cards_for_briefing_topic(topic: dict[str, object]) -> dict[str, object]:
    payload = dict(topic)
    payload["cards"] = [
        _content_card_payload(card) for card in topic["cards"] if isinstance(card, dict)
    ]
    return payload


def _daily_digest_dek(stories: list[dict[str, object]]) -> dict[str, str]:
    if not stories:
        return {
            "zh": "暂无可整理的 ROW ONE 故事。",
            "en": "No ROW ONE stories are available to organize yet.",
        }
    return {
        "zh": f"ROW ONE 将今日 {len(stories)} 条本地时尚信号整理成可直接阅读的简报。",
        "en": f"ROW ONE organized {len(stories)} local fashion signals into an app-ready briefing.",
    }


def _digest_block_payload(
    key: str,
    title: dict[str, str],
    dek: dict[str, str],
    stories: list[dict[str, object]],
) -> dict[str, object]:
    story_ids = [str(story["id"]) for story in stories]
    return {
        "key": key,
        "title": title,
        "dek": dek,
        "story_count": len(stories),
        "story_ids": story_ids,
        "cards": [_content_card_payload(story) for story in stories],
    }


def _read_first_digest_stories(stories: list[dict[str, object]]) -> list[dict[str, object]]:
    top_story = next((story for story in stories if story["section_key"] == "top_stories"), None)
    if top_story is not None:
        return [top_story]
    return stories[:1]


def _key_takeaway_digest_stories(
    edition: RowOneEdition,
    stories: list[dict[str, object]],
) -> list[dict[str, object]]:
    takeaways: list[dict[str, object]] = []
    for section in edition.sections:
        story = next((item for item in stories if item["section_key"] == section.key), None)
        if story is not None:
            takeaways.append(story)
        if len(takeaways) >= 5:
            break
    return takeaways


def _signals_to_watch_digest_stories(
    stories: list[dict[str, object]],
) -> list[dict[str, object]]:
    signals = [
        story
        for story in stories
        if isinstance(story["heat_delta"], int) and int(story["heat_delta"]) > 0
    ]
    signals.sort(
        key=lambda story: (
            -int(story["heat_delta"]),
            str(story["headline"]).casefold(),
            str(story["headline"]),
        )
    )
    return signals[:5]


def _content_card_payload(story: dict[str, object]) -> dict[str, object]:
    return {
        "id": story["id"],
        "story_type": story["story_type"],
        "headline": story["headline"],
        "summary": story["summary"],
        "why_it_matters": story["why_it_matters"],
        "editorial_takeaway": story["editorial_takeaway"],
        "signal_context": story["signal_context"],
        "reader_path": story["reader_path"],
        "detail_href": story["detail_href"],
        "display": story["display"],
        "source_name": story["source_name"],
        "market_region": story["market_region"],
        "source_region": story["source_region"],
        "published_date": story["published_date"],
        "tags": story["tags"],
        "entity_refs": story["entity_refs"],
        "product_refs": story["product_refs"],
        "designer_refs": story["designer_refs"],
        "heat_delta": story["heat_delta"],
        "heat_delta_metric": story["heat_delta_metric"],
        "evidence_count": story["evidence_count"],
    }


def _story_payload(edition: RowOneEdition, story: RowOneStory) -> dict[str, object]:
    section = _section_for_story(edition, story.section_key)
    detail_href = _app_detail_href(story.detail_path)
    published_at_utc = utc_datetime(story.published_at) if story.published_at else None
    return {
        "id": story.id,
        "section_key": story.section_key,
        "story_type": story.story_type,
        "section": {
            "key": section.key,
            "title": section.title.model_dump(mode="json"),
            "href": f"#{section.key}",
        },
        "headline": story.headline,
        "summary": story.summary.model_dump(mode="json"),
        "why_it_matters": story.why_it_matters.model_dump(mode="json"),
        "editorial_takeaway": story.editorial_takeaway.model_dump(mode="json"),
        "signal_context": story.signal_context.model_dump(mode="json"),
        "reader_path": story.reader_path.model_dump(mode="json"),
        "source_name": story.source_name,
        "source_url": safe_external_url(story.source_url),
        "market_region": story.market_region,
        "source_region": story.source_region,
        "display": _display_payload(display_for_story(story)),
        "published_at": isoformat_z(published_at_utc) if published_at_utc else None,
        "published_date": published_at_utc.date().isoformat() if published_at_utc else None,
        "detail_path": detail_href,
        "href": detail_href,
        "detail_href": detail_href,
        "tags": list(story.tags),
        "entity_refs": [_reference_payload(ref) for ref in story.entity_refs],
        "product_refs": [_reference_payload(ref) for ref in story.product_refs],
        "designer_refs": [_reference_payload(ref) for ref in story.designer_refs],
        "heat_delta": story.heat_delta,
        "heat_delta_metric": "raw_mention_delta" if story.heat_delta is not None else None,
        "evidence_count": _safe_evidence_count(story.evidence),
        "evidence": [_evidence_payload(link) for link in story.evidence],
        "detail_sections": _detail_sections_payload(story),
        "evidence_summary": _evidence_summary_payload(story),
    }


def _reference_payload(reference) -> dict[str, object]:
    return reference.model_dump(mode="json")


def _display_payload(display: RowOneStoryDisplay) -> dict[str, object]:
    return {
        "variant": display.variant,
        "accent": display.accent,
        "image": _image_payload(display.image),
    }


def _image_payload(image: RowOneStoryImage | None) -> dict[str, object] | None:
    if image is None:
        return None
    src = safe_story_image_src(image.src)
    if src is None:
        return None
    return {
        "src": src,
        "alt": image.alt.model_dump(mode="json"),
        "credit": image.credit,
        "source_url": safe_external_url(image.source_url),
    }


def _section_for_story(edition: RowOneEdition, section_key: str) -> RowOneSection:
    for section in edition.sections:
        if section.key == section_key:
            return section
    return RowOneSection(
        key=section_key,
        title=type(edition.summary)(zh=section_key, en=section_key.replace("_", " ").title()),
        dek=type(edition.summary)(zh="", en=""),
    )


def _evidence_payload(link: RowOneLink) -> dict[str, object]:
    safe_url = safe_external_url(link.url)
    return {
        "title": link.title,
        "url": safe_url,
        "href": safe_url,
        "source_name": link.source_name,
    }


def _detail_sections_payload(story: RowOneStory) -> list[dict[str, object]]:
    return [
        {
            "key": "summary",
            "title": {"en": "Summary", "zh": "摘要"},
            "body": story.summary.model_dump(mode="json"),
            "evidence": [],
        },
        {
            "key": "why_it_matters",
            "title": {"en": "Why It Matters", "zh": "为什么重要"},
            "body": story.why_it_matters.model_dump(mode="json"),
            "evidence": [],
        },
        {
            "key": "editorial_takeaway",
            "title": {"en": "Editorial Takeaway", "zh": "编辑整理"},
            "body": story.editorial_takeaway.model_dump(mode="json"),
            "evidence": [],
        },
        {
            "key": "signal_context",
            "title": {"en": "Signal Context", "zh": "信号背景"},
            "body": story.signal_context.model_dump(mode="json"),
            "evidence": [],
        },
        {
            "key": "reader_path",
            "title": {"en": "Reader Path", "zh": "阅读路径"},
            "body": story.reader_path.model_dump(mode="json"),
            "evidence": [],
        },
        {
            "key": "evidence",
            "title": {"en": "Evidence Trail", "zh": "来源线索"},
            "body": None,
            "evidence": [_evidence_payload(link) for link in story.evidence],
        },
    ]


def _evidence_summary_payload(story: RowOneStory) -> dict[str, object]:
    sources: list[str] = []
    for link in story.evidence:
        if link.source_name not in sources:
            sources.append(link.source_name)
    return {
        "safe_link_count": _safe_evidence_count(story.evidence),
        "total_count": len(story.evidence),
        "primary_source_name": story.source_name,
        "sources": sources,
    }


def _safe_evidence_count(evidence: list[RowOneLink]) -> int:
    return sum(1 for link in evidence if safe_external_url(link.url) is not None)


def _app_detail_href(detail_path: str) -> str:
    pure_path = _validated_detail_relative_path(detail_path)
    if pure_path is None:
        raise ValueError(f"Invalid ROW ONE detail path: {detail_path}")
    return str(pure_path)

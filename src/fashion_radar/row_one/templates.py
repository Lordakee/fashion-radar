from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import datetime
from html import escape
from pathlib import PurePosixPath

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.body_source_labels import row_one_body_source_label
from fashion_radar.row_one.daily_local_article_intelligence_brief import (
    RowOneDailyLocalArticleIntelligenceBrief,
    RowOneDailyLocalArticleIntelligenceBriefArticle,
    RowOneDailyLocalArticleIntelligenceBriefLane,
    RowOneDailyLocalArticleIntelligenceBriefLaneChip,
    RowOneDailyLocalArticleIntelligenceBriefRoute,
)
from fashion_radar.row_one.daily_local_brand_product_people_signal_digest import (
    DAILY_LOCAL_BRAND_PRODUCT_PEOPLE_SIGNAL_DIGEST_EXCERPT_CHARS,
    DAILY_LOCAL_BRAND_PRODUCT_PEOPLE_SIGNAL_DIGEST_ITEM_LIMIT,
    DAILY_LOCAL_BRAND_PRODUCT_PEOPLE_SIGNAL_DIGEST_SUPPORT_LIMIT,
    RowOneDailyLocalBrandProductPeopleSignalDigest,
    RowOneDailyLocalBrandProductPeopleSignalDigestBucket,
    RowOneDailyLocalBrandProductPeopleSignalDigestItem,
    RowOneDailyLocalBrandProductPeopleSignalDigestSupport,
)
from fashion_radar.row_one.daily_local_key_signals_digest import (
    RowOneDailyLocalKeySignalsDigest,
    RowOneDailyLocalKeySignalsDigestEntry,
    RowOneDailyLocalKeySignalsDigestGroup,
)
from fashion_radar.row_one.daily_local_news_timeline import (
    RowOneDailyLocalNewsTimeline,
    RowOneDailyLocalNewsTimelineItem,
)
from fashion_radar.row_one.daily_local_reading_itinerary import (
    RowOneDailyLocalReadingItinerary,
    RowOneDailyLocalReadingItineraryCard,
    RowOneDailyLocalReadingItineraryEvidence,
)
from fashion_radar.row_one.daily_local_saved_article_organizer import (
    RowOneDailyLocalSavedArticleOrganizer,
    RowOneDailyLocalSavedArticleOrganizerCard,
    RowOneDailyLocalSavedArticleOrganizerLane,
    RowOneDailyLocalSavedArticleOrganizerReference,
)
from fashion_radar.row_one.daily_local_saved_text_takeaways import (
    RowOneDailyLocalSavedTextTakeawayCard,
    RowOneDailyLocalSavedTextTakeawayLane,
    RowOneDailyLocalSavedTextTakeaways,
)
from fashion_radar.row_one.daily_local_synthesis_brief import (
    RowOneDailyLocalSynthesisBrief,
    RowOneDailyLocalSynthesisBriefCard,
    RowOneDailyLocalSynthesisEvidenceLink,
)
from fashion_radar.row_one.detail_routes import (
    safe_row_one_detail_fragment_href,
    validated_row_one_detail_relative_path,
)
from fashion_radar.row_one.display import display_for_story, safe_story_image_src
from fashion_radar.row_one.local_article_body_section_markers import (
    RowOneLocalArticleBodySectionMarker,
    build_row_one_local_article_body_section_markers,
)
from fashion_radar.row_one.local_article_intelligence_brief import (
    RowOneLocalArticleIntelligenceBrief,
    RowOneLocalArticleIntelligenceChip,
    RowOneLocalArticleIntelligenceEvidence,
    RowOneLocalArticleIntelligenceLane,
    RowOneLocalArticleIntelligenceRoute,
    build_row_one_local_article_intelligence_brief,
)
from fashion_radar.row_one.local_article_synthesis_brief import (
    RowOneLocalArticleSynthesisAnchor,
    RowOneLocalArticleSynthesisBrief,
    build_row_one_local_article_synthesis_brief,
)
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneDailyLocalIntelligenceItem,
    RowOneDailyLocalIntelligenceSection,
    RowOneDailyLocalIntelligenceSegment,
    RowOneDailyLocalIntelligenceSegmentItem,
    RowOneEdition,
    RowOneLink,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneReference,
    RowOneSection,
    RowOneSectionKey,
    RowOneStory,
)
from fashion_radar.row_one.readiness import RowOneReadiness, build_row_one_readiness
from fashion_radar.row_one.saved_article_body_organizer import (
    RowOneLocalArticleBodyOrganizerParagraph,
    RowOneLocalArticleBodyOrganizerSectionRow,
    RowOneSavedArticleBodyOrganizer,
    build_row_one_saved_article_body_organizer,
)
from fashion_radar.row_one.saved_article_briefs import (
    RowOneSavedArticleBriefItem,
    RowOneSavedArticleBriefs,
)
from fashion_radar.row_one.saved_article_content_organization import (
    RowOneSavedArticleContentOrganization,
    RowOneSavedArticleContentOrganizationCard,
    RowOneSavedArticleContentOrganizationGroup,
)
from fashion_radar.row_one.saved_article_coverage import (
    RowOneSavedArticleCoverage,
    RowOneSavedArticleCoverageItem,
)
from fashion_radar.row_one.saved_article_daily_signal_leaderboard import (
    RowOneSavedArticleDailySignalLeaderboard,
    RowOneSavedArticleDailySignalLeaderboardBucket,
    RowOneSavedArticleDailySignalLeaderboardItem,
    RowOneSavedArticleDailySignalLeaderboardSupport,
)
from fashion_radar.row_one.saved_article_evidence_board import (
    RowOneSavedArticleEvidenceBoard,
    RowOneSavedArticleEvidenceBoardCard,
    RowOneSavedArticleEvidenceBoardGroup,
)
from fashion_radar.row_one.saved_article_filing_inbox import (
    RowOneSavedArticleFilingInbox,
    RowOneSavedArticleFilingInboxItem,
    RowOneSavedArticleFilingInboxParagraph,
)
from fashion_radar.row_one.saved_article_key_signals import (
    RowOneSavedArticleKeySignalEvidence,
    RowOneSavedArticleKeySignalGroup,
    RowOneSavedArticleKeySignalReference,
    RowOneSavedArticleKeySignals,
    RowOneSavedArticleKeySignalTheme,
)
from fashion_radar.row_one.saved_article_library import (
    RowOneSavedArticleLibrary,
    RowOneSavedArticleLibraryEntry,
    RowOneSavedArticleLibraryParagraphLink,
    RowOneSavedArticleLibrarySourceGroup,
)
from fashion_radar.row_one.saved_article_local_reading_companion import (
    RowOneSavedArticleLocalReadingCompanion,
    RowOneSavedArticleLocalReadingCompanionItem,
    RowOneSavedArticleLocalReadingCompanionTrailLink,
)
from fashion_radar.row_one.saved_article_local_related_reads import (
    RowOneSavedArticleLocalRelatedReadCard,
    RowOneSavedArticleLocalRelatedReadConnectionBrief,
    RowOneSavedArticleLocalRelatedReadEvidenceBridge,
    RowOneSavedArticleLocalRelatedReadLane,
    RowOneSavedArticleLocalRelatedReads,
    build_row_one_saved_article_local_related_read_connection_brief,
    build_row_one_saved_article_local_related_read_lanes,
)
from fashion_radar.row_one.saved_article_local_section_binder import (
    RowOneSavedArticleLocalSectionBinder,
    RowOneSavedArticleLocalSectionBinderParagraph,
    RowOneSavedArticleLocalSectionBinderRow,
)
from fashion_radar.row_one.saved_article_organization_jump_index import (
    RowOneSavedArticleOrganizationJumpIndex,
    RowOneSavedArticleOrganizationJumpIndexGroup,
    RowOneSavedArticleOrganizationJumpIndexItem,
    RowOneSavedArticleOrganizationJumpIndexSourceRoute,
    build_row_one_saved_article_organization_jump_index,
)
from fashion_radar.row_one.saved_article_read_next_clusters import (
    RowOneSavedArticleReadNextCluster,
    RowOneSavedArticleReadNextClusterItem,
    RowOneSavedArticleReadNextClusters,
    build_row_one_saved_article_read_next_clusters,
)
from fashion_radar.row_one.saved_article_reading_paths import (
    RowOneSavedArticleReadingPath,
    RowOneSavedArticleReadingPaths,
    RowOneSavedArticleReadingPathStep,
)
from fashion_radar.row_one.saved_article_reading_queue import (
    RowOneSavedArticleReadingQueue,
    RowOneSavedArticleReadingQueueItem,
    build_row_one_saved_article_reading_queue,
)
from fashion_radar.row_one.saved_article_reference_atlas import (
    RowOneSavedArticleReferenceAtlas,
    RowOneSavedArticleReferenceAtlasBucket,
    RowOneSavedArticleReferenceAtlasEntry,
    RowOneSavedArticleReferenceAtlasSupport,
)
from fashion_radar.row_one.saved_article_signal_facets import (
    RowOneSavedArticleSignalFacetChip,
    RowOneSavedArticleSignalFacetRow,
    RowOneSavedArticleSignalFacets,
)
from fashion_radar.row_one.saved_article_theme_digest import (
    RowOneSavedArticleThemeDigest,
    RowOneSavedArticleThemeDigestItem,
    RowOneSavedArticleThemeDigestTheme,
)
from fashion_radar.row_one.saved_signal_index import (
    RowOneSavedSignalIndex,
    RowOneSavedSignalIndexEntry,
    RowOneSavedSignalIndexParagraphLink,
    RowOneSavedSignalIndexSupport,
)
from fashion_radar.row_one.text import (
    clean_row_one_sentences,
    clean_row_one_text,
    normalize_row_one_paragraph,
    protect_literal_angle_tokens,
    restore_literal_angle_tokens,
)
from fashion_radar.row_one.utils import safe_external_url

_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE = re.compile(r"local-article-paragraph-[1-9][0-9]*$")
_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE = re.compile(
    r"local-article-content-section-[1-9][0-9]*$"
)
_SAVED_ARTICLE_ORGANIZATION_GROUP_KEY_RE = re.compile(r"[a-z][a-z0-9_]{0,63}$")
_SAVED_ARTICLE_LIBRARY_CARD_PREFIX = "saved-article-library-card-"
_SAVED_ARTICLE_ORGANIZATION_GROUP_PREFIX = "saved-article-organization-group-"
LOCAL_ARTICLE_DIGEST_EXCERPT_CHARS = 160
LOCAL_ARTICLE_DIGEST_MAX_REFERENCES = 4
LOCAL_ARTICLE_CONTENT_PREVIEW_EXCERPT_CHARS = 140
LOCAL_ARTICLE_CONTENT_PREVIEW_MAX_ITEMS = 2
LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_BODY_CHARS = 120
LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_EXCERPT_CHARS = 140
LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_MAX_ITEMS = 4
LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_MAX_REFS = 4
LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_MAX_ROWS = 8
LOCAL_ARTICLE_PARAGRAPH_CONTEXT_LIMIT = 4
LOCAL_ARTICLE_BODY_FILING_CUES_MAX_CONTEXTS = 3
LOCAL_ARTICLE_READER_EXCERPT_CHARS = 120
LOCAL_ARTICLE_INFORMATION_BODY_MAX_CHARS = 120
LOCAL_ARTICLE_INFORMATION_MAX_ITEMS_PER_SECTION = 2
LOCAL_ARTICLE_INFORMATION_MAX_PARAGRAPH_LINKS = 5
LOCAL_ARTICLE_INFORMATION_MAX_REFS = 6
LOCAL_ARTICLE_INFORMATION_MAX_SECTIONS = 4
LOCAL_ARTICLE_CONTENT_SEGMENT_DECK_EXCERPT_CHARS = 180
LOCAL_ARTICLE_CONTENT_SEGMENT_DECK_MAX_ITEMS_PER_SECTION = 3
LOCAL_ARTICLE_CONTENT_SEGMENT_DECK_MAX_PARAGRAPH_LINKS = 3
LOCAL_ARTICLE_CONTENT_SEGMENT_DECK_MAX_REFS_PER_SECTION = 5
LOCAL_ARTICLE_CONTENT_SEGMENT_DECK_MAX_SECTIONS = 4
DETAIL_CONTINUE_READING_EXCERPT_CHARS = 120
DETAIL_CONTINUE_READING_MAX_ITEMS = 3
DETAIL_SIGNAL_BRIEFING_MAX_REFS = 8
DETAIL_SIGNAL_BRIEFING_MAX_CUES = 3
DAILY_EDIT_MAX_CARDS = 4
DAILY_EDIT_MAX_SIGNALS = 3
DAILY_EDIT_MAX_PATH_ITEMS = 3
EDITORIAL_BRIEF_MAX_ITEMS = 3
EDITORIAL_BRIEF_BODY_EXCERPT_CHARS = 220
EDITORIAL_BRIEF_MAX_TRAIL_ITEMS = 3
SAVED_ARTICLE_BODY_GUIDE_ITEMS_PER_CARD = 2
SAVED_ARTICLE_SOURCE_BRIEF_ITEMS_PER_SOURCE = 2
SAVED_ARTICLE_SOURCE_ROUTE_LIMIT = 4
SAVED_ARTICLE_CONTENT_ORGANIZATION_EVIDENCE_LINK_LIMIT = 3
SAVED_ARTICLE_CONTENT_ORGANIZATION_SUMMARY_MAX_REFS = 5
SAVED_ARTICLE_CONTENT_ORGANIZATION_MAX_PARAGRAPH_INDEX = 50
SAVED_ARTICLE_ORGANIZATION_COVERAGE_MAX_ROWS = 6
SAVED_ARTICLE_ORGANIZATION_COVERAGE_MAX_REFS = 5
DAILY_LOCAL_HEAT_SIGNALS_MAX_TOPICS = 6
DAILY_LOCAL_HEAT_SIGNALS_MAX_STORIES = 2
DAILY_LOCAL_ARTICLE_CAPSULES_MAX_ITEMS = 4
DAILY_LOCAL_ARTICLE_CAPSULES_MAX_PARAGRAPHS = 3
DAILY_LOCAL_ARTICLE_CAPSULES_MAX_REFS = 6
DAILY_LOCAL_ARTICLE_CAPSULE_EXCERPT_CHARS = 150
DAILY_LOCAL_ARTICLE_READING_BRIEF_MAX_GROUPS = 3
DAILY_LOCAL_ARTICLE_READING_BRIEF_MAX_ITEMS_PER_GROUP = 3
DAILY_LOCAL_ARTICLE_READING_BRIEF_MAX_TOTAL_ITEMS = 4
DAILY_LOCAL_ARTICLE_READING_BRIEF_EXCERPT_CHARS = 150
DAILY_LOCAL_ARTICLE_READING_BRIEF_MAX_REFS = 4
DAILY_LOCAL_SOURCE_DESK_MAX_SOURCES = 4
DAILY_LOCAL_SOURCE_DESK_MAX_LINKS_PER_SOURCE = 2
DAILY_LOCAL_SOURCE_DESK_MAX_REFS_PER_SOURCE = 5
DAILY_LOCAL_COVERAGE_MAP_MAX_SOURCES = 4
DAILY_LOCAL_COVERAGE_MAP_MAX_BUCKETS_PER_SOURCE = 4
DAILY_LOCAL_COVERAGE_MAP_MAX_REFS_PER_SOURCE = 5
DAILY_LOCAL_COVERAGE_MAP_MAX_LINKS_PER_SOURCE = 2
DAILY_LOCAL_THEME_SUMMARY_STRIP_MAX_THEMES = 4
DAILY_LOCAL_THEME_SUMMARY_STRIP_MAX_LINKS_PER_THEME = 2
DAILY_LOCAL_THEME_SUMMARY_STRIP_MAX_REFS_PER_THEME = 5
DAILY_LOCAL_THEME_SUMMARY_STRIP_SUMMARY_CHARS = 160


@dataclass(frozen=True)
class _EditorialBriefTrailItem:
    label: LocalizedText
    href: str | None = None


@dataclass(frozen=True)
class _EditorialBriefItem:
    title: LocalizedText
    body: LocalizedText
    meta: LocalizedText | None = None
    href: str | None = None
    trail: tuple[_EditorialBriefTrailItem, ...] = ()


@dataclass(frozen=True)
class _EditorialBrief:
    items: tuple[_EditorialBriefItem, ...]


@dataclass(frozen=True)
class _DailyLocalHeatSignalStory:
    title: LocalizedText
    source_name: str
    href: str


@dataclass(frozen=True)
class _DailyLocalHeatSignalTopic:
    title: LocalizedText
    label: LocalizedText
    subtype_label: str | None
    story_count: int
    evidence_count: int
    local_article_count: int
    positive_heat_delta_sum: int
    max_heat_delta: int
    stories: tuple[_DailyLocalHeatSignalStory, ...]


@dataclass(frozen=True)
class _DailyLocalArticleCapsuleParagraph:
    index: int
    excerpt: LocalizedText
    href: str


@dataclass(frozen=True)
class _DailyLocalArticleCapsule:
    title: LocalizedText
    article_title: str
    source_name: str
    body_source: str
    why_it_matters: LocalizedText
    href: str
    paragraphs: tuple[_DailyLocalArticleCapsuleParagraph, ...]
    references: tuple[RowOneReference, ...]


@dataclass(frozen=True)
class _DailyLocalArticleReadingBriefReference:
    name: str
    label: str


@dataclass(frozen=True)
class _DailyLocalArticleReadingBriefItem:
    title: LocalizedText
    article_title: str
    source_name: str
    body_source: str
    reason: LocalizedText
    paragraph_excerpt: LocalizedText
    paragraph_number: int
    href: str
    paragraph_href: str
    references: tuple[_DailyLocalArticleReadingBriefReference, ...]


@dataclass(frozen=True)
class _DailyLocalArticleReadingBriefGroup:
    key: str
    title: LocalizedText
    dek: LocalizedText
    items: tuple[_DailyLocalArticleReadingBriefItem, ...]


@dataclass(frozen=True)
class _DailyLocalSourceDeskLink:
    story_headline: str
    article_title: str | None
    href: str
    paragraph_href: str
    paragraph_number: int


@dataclass(frozen=True)
class _DailyLocalSourceDeskReference:
    name: str
    label: str


@dataclass(frozen=True)
class _DailyLocalSourceDeskSource:
    source_name: str
    article_count: int
    saved_paragraph_count: int
    body_source_labels: tuple[LocalizedText, ...]
    references: tuple[_DailyLocalSourceDeskReference, ...]
    links: tuple[_DailyLocalSourceDeskLink, ...]


@dataclass(frozen=True)
class _DailyLocalCoverageMapBucket:
    title: LocalizedText
    support_count: int


@dataclass(frozen=True)
class _DailyLocalCoverageMapLink:
    title: LocalizedText
    source_name: str
    href: str
    bucket_title: LocalizedText


@dataclass(frozen=True)
class _DailyLocalCoverageMapSource:
    source_name: str
    bucket_count: int
    article_count: int
    card_count: int
    saved_paragraph_count: int
    buckets: tuple[_DailyLocalCoverageMapBucket, ...]
    references: tuple[RowOneReference, ...]
    links: tuple[_DailyLocalCoverageMapLink, ...]


@dataclass(frozen=True)
class _DailyLocalThemeSummaryStripLink:
    title: LocalizedText
    href: str
    source_name: str


@dataclass(frozen=True)
class _DailyLocalThemeSummaryStripTheme:
    title: LocalizedText
    summary: LocalizedText
    card_count: int
    source_count: int
    article_count: int
    saved_paragraph_count: int
    references: tuple[RowOneReference, ...]
    links: tuple[_DailyLocalThemeSummaryStripLink, ...]
    original_index: int


@dataclass(frozen=True)
class _SavedArticleSourceRoute:
    group_index: int
    source_name: str
    anchor_id: str
    article_count: int
    saved_paragraph_count: int


@dataclass(frozen=True)
class _LocalArticleParagraphEvidenceItem:
    section_position: int
    section_title: LocalizedText
    item_label: LocalizedText
    item_body: LocalizedText | None
    references: tuple[RowOneReference, ...]


@dataclass(frozen=True)
class _LocalArticleParagraphEvidenceEntry:
    paragraph_index: int
    excerpt: LocalizedText
    items: tuple[_LocalArticleParagraphEvidenceItem, ...]


@dataclass(frozen=True)
class _LocalArticleParagraphContextCue:
    anchor: str
    label: LocalizedText
    excerpt: LocalizedText


def render_index_html(
    edition: RowOneEdition,
    *,
    app_payload: dict[str, object] | None = None,
    local_article_intelligence: Sequence[RowOneDailyLocalIntelligenceSection] | None = None,
    saved_article_coverage: RowOneSavedArticleCoverage | None = None,
    saved_article_library: RowOneSavedArticleLibrary | None = None,
    saved_signal_index: RowOneSavedSignalIndex | None = None,
    saved_article_briefs: RowOneSavedArticleBriefs | None = None,
    daily_local_key_signals_digest: RowOneDailyLocalKeySignalsDigest | None = None,
    daily_local_signal_momentum: RowOneSavedArticleDailySignalLeaderboard | None = None,
    daily_local_signal_momentum_hrefs_by_detail_path: Mapping[str, str] | None = None,
    daily_local_heat_signals_article_hrefs_by_story_id: Mapping[str, str] | None = None,
    daily_local_article_capsules_article_hrefs_by_story_id: Mapping[str, str] | None = None,
    daily_local_article_reading_brief_article_hrefs_by_story_id: Mapping[str, str] | None = None,
    daily_local_source_desk_article_hrefs_by_story_id: Mapping[str, str] | None = None,
    daily_local_coverage_map_hrefs_by_detail_path: Mapping[str, str] | None = None,
    daily_local_theme_summary_strip_hrefs_by_detail_path: Mapping[str, str] | None = None,
    daily_local_news_timeline: RowOneDailyLocalNewsTimeline | None = None,
    daily_local_article_intelligence_brief: RowOneDailyLocalArticleIntelligenceBrief | None = None,
    daily_local_synthesis_brief: RowOneDailyLocalSynthesisBrief | None = None,
    daily_local_saved_text_takeaways: RowOneDailyLocalSavedTextTakeaways | None = None,
    daily_local_brand_product_people_signal_digest: (
        RowOneDailyLocalBrandProductPeopleSignalDigest | None
    ) = None,
    daily_local_saved_article_organizer: RowOneDailyLocalSavedArticleOrganizer | None = None,
    daily_local_reading_itinerary: RowOneDailyLocalReadingItinerary | None = None,
    saved_article_content_organization: RowOneSavedArticleContentOrganization | None = None,
    editorial_brief: _EditorialBrief | None = None,
    local_articles_by_story_id: dict[str, RowOneLocalArticle] | None = None,
) -> str:
    local_articles_by_story_id = local_articles_by_story_id or {}
    contents_nav = _render_edition_nav(edition)
    briefing_topics = _render_briefing_topics(app_payload)
    briefing_path = _render_briefing_path(app_payload)
    edition_brief = _render_edition_brief(
        app_payload,
        has_topics=bool(briefing_topics),
        has_path=bool(briefing_path),
    )
    signal_synthesis = _render_signal_synthesis(app_payload)
    daily_edit = _render_daily_edit(app_payload)
    daily_local_intelligence = _render_daily_local_intelligence(local_article_intelligence)
    saved_article_coverage_section = _render_saved_article_coverage(saved_article_coverage)
    saved_article_library_entry = _render_saved_article_library_entry(
        saved_article_library,
        saved_signal_index=saved_signal_index,
    )
    saved_article_briefs_section = _render_saved_article_briefs(saved_article_briefs)
    daily_local_key_signals_digest_section = _render_daily_local_key_signals_digest(
        daily_local_key_signals_digest
    )
    daily_local_signal_momentum_section = _render_daily_local_signal_momentum(
        daily_local_signal_momentum,
        local_article_page_hrefs_by_detail_path=daily_local_signal_momentum_hrefs_by_detail_path,
    )
    daily_local_heat_signals_section = _render_daily_local_heat_signals(
        app_payload,
        local_articles_by_story_id=local_articles_by_story_id,
        article_hrefs_by_story_id=daily_local_heat_signals_article_hrefs_by_story_id,
    )
    daily_local_article_capsules_section = _render_daily_local_article_capsules(
        edition,
        local_articles_by_story_id=local_articles_by_story_id,
        article_hrefs_by_story_id=daily_local_article_capsules_article_hrefs_by_story_id,
    )
    daily_local_article_reading_brief_section = _render_daily_local_article_reading_brief(
        edition,
        local_articles_by_story_id=local_articles_by_story_id,
        article_hrefs_by_story_id=daily_local_article_reading_brief_article_hrefs_by_story_id,
    )
    daily_local_source_desk_section = _render_daily_local_source_desk(
        edition,
        local_articles_by_story_id=local_articles_by_story_id,
        article_hrefs_by_story_id=daily_local_source_desk_article_hrefs_by_story_id,
    )
    daily_local_coverage_map_section = _render_daily_local_coverage_map(
        saved_article_content_organization,
        local_articles_by_story_id=local_articles_by_story_id,
        hrefs_by_detail_path=daily_local_coverage_map_hrefs_by_detail_path,
    )
    daily_local_theme_summary_strip_section = _render_daily_local_theme_summary_strip(
        saved_article_content_organization,
        local_articles_by_story_id=local_articles_by_story_id,
        hrefs_by_detail_path=daily_local_theme_summary_strip_hrefs_by_detail_path,
    )
    daily_local_news_timeline_section = _render_daily_local_news_timeline(daily_local_news_timeline)
    daily_local_article_intelligence_brief_section = _render_daily_local_article_intelligence_brief(
        daily_local_article_intelligence_brief
    )
    daily_local_synthesis_brief_section = _render_daily_local_synthesis_brief(
        daily_local_synthesis_brief
    )
    daily_local_saved_text_takeaways_section = _render_daily_local_saved_text_takeaways(
        daily_local_saved_text_takeaways
    )
    daily_local_brand_product_people_signal_digest_section = (
        _render_daily_local_brand_product_people_signal_digest(
            daily_local_brand_product_people_signal_digest
        )
    )
    daily_local_saved_article_organizer_section = _render_daily_local_saved_article_organizer(
        daily_local_saved_article_organizer
    )
    daily_local_reading_itinerary_section = _render_daily_local_reading_itinerary(
        daily_local_reading_itinerary
    )
    saved_article_content_organization_section = _render_saved_article_content_organization(
        saved_article_content_organization
    )
    editorial_brief_section = _render_editorial_brief(editorial_brief)
    readiness = build_row_one_readiness(edition)
    status_strip = _render_edition_status(edition, readiness)
    summary_note_en = (
        f"{readiness.story_count} stories · {readiness.safe_evidence_count} evidence links"
    )
    summary_note_zh = f"{readiness.story_count} 条故事 · {readiness.safe_evidence_count} 条证据链接"
    lead_story = _lead_story(edition)
    lead_story_block = (
        _render_lead_story(
            lead_story,
            _section_title(edition, lead_story.section_key),
            local_article=local_articles_by_story_id.get(lead_story.id),
        )
        if lead_story
        else ""
    )
    story_cards = "\n".join(
        _render_section(
            edition,
            section.key,
            local_articles_by_story_id=local_articles_by_story_id,
        )
        for section in edition.sections
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{
        _render_meta_tags(
            title=f"{edition.brand} — {edition.edition_date.date().isoformat()}",
            description=edition.summary.en,
            page_type="website",
        )
    }
<title>{_esc(edition.brand)} — {_esc(edition.edition_date.date().isoformat())}</title>
<link rel="stylesheet" href="assets/row-one.css">
</head>
<body>
<div class="site-shell">
<header class="site-header">
  <div class="site-header-inner">
    <div class="site-title-block">
      <div class="edition-kicker">Daily Fashion Intelligence</div>
      <h1>{_esc(edition.brand)}</h1>
      <p class="edition-date">{_esc(edition.edition_date.strftime("%B %d, %Y"))}</p>
      <p class="site-dek">
        <span data-lang="en">Local signals, edited for fashion context.</span>
        <span data-lang="zh">本地信号，以时尚语境整理。</span>
      </p>
      <div class="language-toggle" aria-label="Language">
        <button type="button" data-lang-toggle="en" aria-pressed="true">EN</button>
        <button type="button" data-lang-toggle="zh" aria-pressed="false">中文</button>
      </div>
      <p class="edition-summary">
        <span data-lang="en">{_esc(edition.summary.en)}</span>
        <span data-lang="zh">{_esc(edition.summary.zh)}</span>
      </p>
    </div>
    <aside class="edition-summary-panel" aria-label="Edition summary">
      <p class="summary-kicker">
        <span data-lang="en">Edition</span>
        <span data-lang="zh">每日版本</span>
      </p>
      <p class="summary-date">{_esc(edition.edition_date.date().isoformat())}</p>
      <p class="summary-status">
        <span data-lang="en">{_esc(readiness.readiness.en)}</span>
        <span data-lang="zh">{_esc(readiness.readiness.zh)}</span>
      </p>
      <p class="summary-note">
        <span data-lang="en">{_esc(summary_note_en)}</span>
        <span data-lang="zh">{_esc(summary_note_zh)}</span>
      </p>
    </aside>
  </div>
</header>
{status_strip}
<main class="site-main" id="main-content">
{contents_nav}
{edition_brief}
{signal_synthesis}
{daily_edit}
{daily_local_intelligence}
{saved_article_coverage_section}
{saved_article_library_entry}
{saved_article_briefs_section}
{daily_local_key_signals_digest_section}
{daily_local_signal_momentum_section}
{daily_local_heat_signals_section}
{daily_local_article_capsules_section}
{daily_local_article_reading_brief_section}
{daily_local_source_desk_section}
{daily_local_coverage_map_section}
{daily_local_theme_summary_strip_section}
{daily_local_news_timeline_section}
{daily_local_article_intelligence_brief_section}
{daily_local_synthesis_brief_section}
{daily_local_saved_text_takeaways_section}
{daily_local_brand_product_people_signal_digest_section}
{daily_local_saved_article_organizer_section}
{daily_local_reading_itinerary_section}
{saved_article_content_organization_section}
{editorial_brief_section}
{lead_story_block}
{briefing_topics}
{briefing_path}
{story_cards}
</main>
</div>
<script src="assets/row-one.js"></script>
</body>
</html>
"""


def render_saved_article_library_html(
    edition: RowOneEdition,
    library: RowOneSavedArticleLibrary,
    *,
    saved_signal_index: RowOneSavedSignalIndex | None = None,
    saved_article_content_organization: RowOneSavedArticleContentOrganization | None = None,
    saved_article_reading_paths: RowOneSavedArticleReadingPaths | None = None,
    saved_article_theme_digest: RowOneSavedArticleThemeDigest | None = None,
    saved_article_reference_atlas: RowOneSavedArticleReferenceAtlas | None = None,
    saved_article_signal_facets: RowOneSavedArticleSignalFacets | None = None,
    saved_article_daily_signal_leaderboard: RowOneSavedArticleDailySignalLeaderboard | None = None,
    saved_article_organization_jump_index: RowOneSavedArticleOrganizationJumpIndex | None = None,
    saved_article_reading_queue: RowOneSavedArticleReadingQueue | None = None,
    saved_article_read_next_clusters: RowOneSavedArticleReadNextClusters | None = None,
    saved_article_filing_inbox: RowOneSavedArticleFilingInbox | None = None,
    saved_article_evidence_board: RowOneSavedArticleEvidenceBoard | None = None,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None = None,
) -> str:
    snippets_by_detail_path = _saved_article_library_snippets_by_detail_path(
        saved_article_content_organization
    )
    source_routes = _saved_article_source_routes(library.groups)
    source_route_ids_by_index = {route.group_index: route.anchor_id for route in source_routes}
    groups = "\n".join(
        _render_saved_article_library_source(
            group,
            snippets_by_detail_path=snippets_by_detail_path,
            local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
            source_anchor_id=source_route_ids_by_index.get(index),
        )
        for index, group in enumerate(library.groups)
    )
    signal_index = _render_saved_signal_index(
        saved_signal_index,
        section_id="saved-signal-index",
    )
    theme_digest = _render_saved_article_theme_digest(
        saved_article_theme_digest,
        section_id="saved-article-theme-digest",
    )
    reference_atlas = _render_saved_article_reference_atlas(
        saved_article_reference_atlas,
        section_id="saved-article-reference-atlas",
    )
    signal_facets = _render_saved_article_signal_facets(
        saved_article_signal_facets,
        local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
    )
    daily_signal_leaderboard = _render_saved_article_daily_signal_leaderboard(
        saved_article_daily_signal_leaderboard,
        local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
    )
    reading_paths = _render_saved_article_reading_paths(
        saved_article_reading_paths,
        section_id="saved-article-reading-paths",
    )
    evidence_board = _render_saved_article_evidence_board(
        saved_article_evidence_board,
        section_id="saved-article-evidence-board",
    )
    content_organization = _render_saved_article_content_organization(
        saved_article_content_organization,
        href_prefix="../",
        section_id="saved-article-content-organization",
    )
    target_ids = _saved_article_library_page_target_ids(
        source_routes=source_routes,
        content_organization_html=content_organization,
        signal_facets_html=signal_facets,
        daily_signal_leaderboard_html=daily_signal_leaderboard,
    )
    organization_jump_index_model = (
        saved_article_organization_jump_index
        if saved_article_organization_jump_index is not None
        else build_row_one_saved_article_organization_jump_index(
            content_organization=saved_article_content_organization,
            source_routes=_saved_article_organization_jump_index_source_routes(source_routes),
            signal_facets=saved_article_signal_facets,
            daily_signal_leaderboard=saved_article_daily_signal_leaderboard,
        )
    )
    organization_jump_index = _render_saved_article_organization_jump_index(
        organization_jump_index_model,
        target_ids=target_ids,
    )
    reading_queue_model = (
        saved_article_reading_queue
        if saved_article_reading_queue is not None
        else build_row_one_saved_article_reading_queue(
            library,
            local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
        )
    )
    reading_queue = _render_saved_article_reading_queue(reading_queue_model)
    filing_inbox = _render_saved_article_filing_inbox(saved_article_filing_inbox)
    read_next_clusters_model = (
        saved_article_read_next_clusters
        if saved_article_read_next_clusters is not None
        else build_row_one_saved_article_read_next_clusters(
            library,
            saved_article_content_organization,
            local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
        )
    )
    read_next_clusters = _render_saved_article_read_next_clusters(read_next_clusters_model)
    daily_summary = _render_saved_article_daily_summary(
        library,
        source_routes=source_routes,
        signal_index_html=signal_index,
        content_organization_html=content_organization,
        reading_paths_html=reading_paths,
        theme_digest_html=theme_digest,
        reference_atlas_html=reference_atlas,
        signal_facets_html=signal_facets,
        daily_signal_leaderboard_html=daily_signal_leaderboard,
        evidence_board_html=evidence_board,
        local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{
        _render_meta_tags(
            title=f"Daily Saved Article Library - {edition.brand}",
            description="A generated ROW ONE index of today's saved local article bodies.",
            page_type="website",
        )
    }
<title>Daily Saved Article Library - {_esc(edition.brand)}</title>
<link rel="stylesheet" href="../assets/row-one.css">
</head>
<body>
<header class="detail-header">
  <a class="back-link" href="../index.html">ROW ONE</a>
  <div class="language-toggle" aria-label="Language">
    <button type="button" data-lang-toggle="en" aria-pressed="true">EN</button>
    <button type="button" data-lang-toggle="zh" aria-pressed="false">中文</button>
  </div>
</header>
<main class="detail-main saved-article-library-page">
  <section class="saved-article-library-hero" aria-label="Daily saved article library">
    <p class="story-section">
      <span data-lang="en">Saved Local Source Set</span>
      <span data-lang="zh">本地保存来源集合</span>
    </p>
    <h1>
      <span data-lang="en">Daily Saved Article Library</span>
      <span data-lang="zh">每日本地文章库</span>
    </h1>
    <p>
      <span data-lang="en">A current-edition index of saved local fashion articles.</span>
      <span data-lang="zh">当前版本的本地保存时尚文章索引，并链接回已整理的本地正文。</span>
    </p>
    {_render_saved_article_library_metrics(library, css_class="saved-article-library-metrics")}
  </section>
  {daily_summary}
  {organization_jump_index}
  {filing_inbox}
  {reading_queue}
  {read_next_clusters}
  {signal_facets}
  {daily_signal_leaderboard}
  {theme_digest}
  {reference_atlas}
  {signal_index}
  {reading_paths}
  {evidence_board}
  {content_organization}
  <span id="saved-article-library-grid"></span>
  <div class="saved-article-library-grid">{groups}</div>
</main>
<script src="../assets/row-one.js"></script>
</body>
</html>
"""


def render_local_article_page_html(
    edition: RowOneEdition,
    story: RowOneStory,
    *,
    local_article: RowOneLocalArticle,
    saved_article_local_reading_companion: (RowOneSavedArticleLocalReadingCompanion | None) = None,
    saved_article_local_section_binder: (RowOneSavedArticleLocalSectionBinder | None) = None,
    saved_article_key_signals: RowOneSavedArticleKeySignals | None = None,
    saved_article_local_related_reads: RowOneSavedArticleLocalRelatedReads | None = None,
) -> str:
    body_section_markers = build_row_one_local_article_body_section_markers(
        story=story,
        local_article=local_article,
    )
    local_article_section = _render_local_article(
        local_article,
        include_body_filing_cues=True,
        body_section_markers=body_section_markers,
    )
    if not local_article_section:
        return ""
    section_title = _section_title(edition, story.section_key)
    summary_en = _display_summary_text(story.summary.en)
    detail_path = _validated_detail_relative_path(story.detail_path)
    if detail_path is None:
        return ""
    detail_href = f"../{detail_path}"
    information_panel = _render_local_article_information_panel(
        edition,
        story,
        local_article,
        section_title,
    )
    local_reading_companion = _render_saved_article_local_reading_companion(
        saved_article_local_reading_companion
    )
    local_section_binder = _render_saved_article_local_section_binder(
        saved_article_local_section_binder
    )
    key_signals = _render_saved_article_key_signals(saved_article_key_signals)
    content_segment_deck = _render_local_article_content_segment_deck(local_article)
    local_article_body_organizer = _render_local_article_body_organizer(
        build_row_one_saved_article_body_organizer(
            story=story,
            local_article=local_article,
        )
    )
    local_article_intelligence_brief = _render_local_article_intelligence_brief(
        build_row_one_local_article_intelligence_brief(
            story=story,
            local_article=local_article,
        )
    )
    local_article_synthesis_brief = _render_local_article_synthesis_brief(
        build_row_one_local_article_synthesis_brief(
            story=story,
            local_article=local_article,
        ),
        local_article=local_article,
    )
    local_related_reads = _render_saved_article_local_related_reads(
        saved_article_local_related_reads
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{
        _render_meta_tags(
            title=f"{local_article.title or story.headline} - {edition.brand}",
            description=summary_en,
            page_type="article",
        )
    }
<title>{_esc(local_article.title or story.headline)} — {_esc(edition.brand)}</title>
<link rel="stylesheet" href="../assets/row-one.css">
</head>
<body>
<header class="detail-header local-article-page-header">
  <a class="back-link" href="../index.html">ROW ONE</a>
  <nav class="local-article-page-nav" aria-label="Saved article navigation">
    <a href="index.html">
      <span data-lang="en">Saved Article Library</span>
      <span data-lang="zh">本地文章库</span>
    </a>
    <a href="{_esc(detail_href)}">
      <span data-lang="en">Organized Detail</span>
      <span data-lang="zh">整理详情页</span>
    </a>
  </nav>
  <div class="language-toggle" aria-label="Language">
    <button type="button" data-lang-toggle="en" aria-pressed="true">EN</button>
    <button type="button" data-lang-toggle="zh" aria-pressed="false">中文</button>
  </div>
</header>
<main class="detail-main">
  <article class="local-article-page">
    <div class="local-article-page-article">
    <p class="story-section">
      <span data-lang="en">{_esc(section_title.en)}</span>
      <span data-lang="zh">{_esc(section_title.zh)}</span>
    </p>
    <p class="section-return">
      <a href="../index.html#{_esc(story.section_key)}">
        <span data-lang="en">Back to section</span>
        <span data-lang="zh">回到栏目</span>
      </a>
    </p>
    <h1>{_esc(local_article.title or story.headline)}</h1>
    <p class="story-source">{_esc(local_article.source_name)}</p>
{information_panel}
{local_reading_companion}
{local_section_binder}
{key_signals}
{content_segment_deck}
{local_article_body_organizer}
{local_article_intelligence_brief}
{local_article_synthesis_brief}
    {local_article_section}
{local_related_reads}
    </div>
  </article>
</main>
<script src="../assets/row-one.js"></script>
</body>
</html>
"""


def render_detail_html(
    edition: RowOneEdition,
    story: RowOneStory,
    *,
    local_article: RowOneLocalArticle | None = None,
) -> str:
    section_title = _section_title(edition, story.section_key)
    summary_en = _display_summary_text(story.summary.en)
    summary_zh = _display_summary_text(story.summary.zh)
    evidence = "\n".join(_render_evidence(link) for link in story.evidence)
    source_link = _external_link(story.source_url, story.source_name, css_class="source-link")
    source_action = _source_action_link(story.source_url)
    visual = _render_story_visual(story, section_title, context="detail-visual")
    local_article_section = _render_local_article(local_article)
    local_read_path = _render_detail_local_read_path(
        local_article if local_article_section else None
    )
    article_contents = _render_article_contents(include_local_article=bool(local_article_section))
    detail_information_map = _render_detail_information_map(story, section_title)
    detail_signal_briefing = _render_detail_signal_briefing(story, local_article)
    continue_reading = _render_detail_continue_reading(edition, story)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{
        _render_meta_tags(
            title=story.headline,
            description=summary_en,
            page_type="article",
        )
    }
<title>{_esc(story.headline)} — {_esc(edition.brand)}</title>
<link rel="stylesheet" href="../assets/row-one.css">
</head>
<body>
<header class="detail-header">
  <a class="back-link" href="../index.html">ROW ONE</a>
  <div class="language-toggle" aria-label="Language">
    <button type="button" data-lang-toggle="en" aria-pressed="true">EN</button>
    <button type="button" data-lang-toggle="zh" aria-pressed="false">中文</button>
  </div>
</header>
<main class="detail-main">
  <article class="detail-article">
    <p class="story-section">
      <span data-lang="en">{_esc(section_title.en)}</span>
      <span data-lang="zh">{_esc(section_title.zh)}</span>
    </p>
    <p class="section-return">
      <a href="../index.html#{_esc(story.section_key)}">
        <span data-lang="en">Back to section</span>
        <span data-lang="zh">回到栏目</span>
      </a>
    </p>
    <h1>{_esc(story.headline)}</h1>
    {visual}
    <p class="story-source">{source_link}</p>
    {local_read_path}
    {source_action}
    {article_contents}
    {detail_information_map}
    {detail_signal_briefing}
    <section id="summary">
      <h2>
        <span data-lang="en">Summary</span>
        <span data-lang="zh">摘要</span>
      </h2>
      <p>
        <span data-lang="en">{_esc(summary_en)}</span>
        <span data-lang="zh">{_esc(summary_zh)}</span>
      </p>
    </section>
    {local_article_section}
    <section id="why-it-matters">
      <h2>
        <span data-lang="en">Why It Matters</span>
        <span data-lang="zh">为什么重要</span>
      </h2>
      <p>
        <span data-lang="en">{_esc(story.why_it_matters.en)}</span>
        <span data-lang="zh">{_esc(story.why_it_matters.zh)}</span>
      </p>
    </section>
    <section class="detail-panel">
      <h2 id="editorial-takeaway">
        <span data-lang="en">Editorial Takeaway</span>
        <span data-lang="zh">编辑整理</span>
      </h2>
      <p>
        <span data-lang="en">{_esc(story.editorial_takeaway.en)}</span>
        <span data-lang="zh">{_esc(story.editorial_takeaway.zh)}</span>
      </p>
      <h2 id="signal-context">
        <span data-lang="en">Signal Context</span>
        <span data-lang="zh">信号背景</span>
      </h2>
      <p>
        <span data-lang="en">{_esc(story.signal_context.en)}</span>
        <span data-lang="zh">{_esc(story.signal_context.zh)}</span>
      </p>
      <h2 id="reader-path">
        <span data-lang="en">Reader Path</span>
        <span data-lang="zh">阅读路径</span>
      </h2>
      <p>
        <span data-lang="en">{_esc(story.reader_path.en)}</span>
        <span data-lang="zh">{_esc(story.reader_path.zh)}</span>
      </p>
    </section>
    <section id="evidence-trail">
      <h2>
        <span data-lang="en">Evidence Trail</span>
        <span data-lang="zh">来源线索</span>
      </h2>
      <div class="evidence-trail">{evidence}</div>
    </section>
{continue_reading}
  </article>
</main>
<script src="../assets/row-one.js"></script>
</body>
</html>
"""


def row_one_css() -> str:
    return """@font-face { font-family: RowOneSerif; src: local("Georgia"); }
:root {
  --paper: #f4f6f8;
  --ink: #101216;
  --muted: #626a73;
  --line: #d6dce3;
  --panel: #ffffff;
  --accent: #2454ff;
  --steel: #e8edf3;
  --chrome: #c8d0da;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family:
    Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
    sans-serif;
}
.site-shell {
  min-height: 100vh;
}
.site-header {
  min-height: 52vh;
  padding: 44px min(7vw, 88px) 32px;
  border-bottom: 1px solid var(--ink);
  display: grid;
  align-content: space-between;
}
.site-header-inner {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 0.42fr);
  gap: 32px;
  align-items: end;
}
.site-title-block {
  display: grid;
  gap: 14px;
}
.site-dek {
  color: var(--ink);
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.35rem, 2.4vw, 2.6rem);
  line-height: 1.05;
  margin: 0;
  max-width: 820px;
}
.edition-summary-panel {
  align-self: end;
  border: 1px solid var(--ink);
  background: rgba(255, 255, 255, 0.54);
  padding: 20px;
}
.summary-kicker,
.summary-date,
.summary-status,
.summary-note {
  margin: 0;
}
.summary-kicker {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}
.summary-date {
  color: var(--ink);
  font-family: RowOneSerif, Georgia, serif;
  font-size: 2rem;
  line-height: 1;
  margin-top: 12px;
}
.summary-status {
  color: var(--ink);
  font-size: 0.92rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  margin-top: 14px;
  text-transform: uppercase;
}
.summary-note {
  color: var(--muted);
  font-size: 0.86rem;
  margin-top: 8px;
}
.edition-kicker, .story-section {
  color: var(--accent);
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}
h1 {
  margin: 0;
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(4.5rem, 16vw, 13rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.86;
}
.edition-date, .edition-summary {
  max-width: 780px;
  color: var(--muted);
  font-size: 1rem;
}
.language-toggle {
  display: inline-flex;
  width: fit-content;
  border: 1px solid var(--ink);
}
.language-toggle button {
  border: 0;
  border-right: 1px solid var(--ink);
  background: transparent;
  color: var(--ink);
  padding: 8px 13px;
  cursor: pointer;
  font: inherit;
}
.language-toggle button:last-child { border-right: 0; }
.language-toggle button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
main, .site-main { padding: 36px min(7vw, 88px) 72px; }
.edition-status {
  display: grid;
  grid-template-columns: minmax(150px, 1.2fr) repeat(5, minmax(120px, 1fr));
  gap: 0;
  border-bottom: 1px solid var(--ink);
  background: var(--paper);
}
.edition-status > div {
  border-right: 1px solid var(--line);
  padding: 18px min(2vw, 24px);
}
.edition-status > div:last-child { border-right: 0; }
.edition-status strong {
  color: var(--ink);
  display: block;
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.05rem, 1.8vw, 1.8rem);
  font-weight: 500;
  line-height: 1.05;
  margin-top: 6px;
}
.edition-status-label {
  color: var(--muted);
  display: block;
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.edition-nav {
  border-top: 1px solid var(--ink);
  border-bottom: 1px solid var(--ink);
  padding: 24px 0;
  margin-bottom: 32px;
}
.edition-rail {
  margin-top: 18px;
}
.edition-rail-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 1px;
  background: var(--line);
  border: 1px solid var(--line);
}
.edition-nav-item,
.edition-rail-item {
  border: 1px solid var(--line);
  color: var(--ink);
  display: grid;
  gap: 8px;
  min-height: 150px;
  padding: 16px;
  text-decoration: none;
}
.edition-rail-item {
  background: var(--paper);
  border: 0;
  grid-template-columns: 36px minmax(0, 1fr);
  min-height: 168px;
}
.rail-item-index {
  color: var(--accent);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.1em;
}
.rail-item-copy {
  display: grid;
  gap: 8px;
}
.rail-item-title {
  font-family: RowOneSerif, Georgia, serif;
  font-size: 1.25rem;
  line-height: 1;
}
.rail-item-count {
  color: var(--accent);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.edition-nav-title {
  font-family: RowOneSerif, Georgia, serif;
  font-size: 1.25rem;
  line-height: 1;
}
.edition-nav-count {
  color: var(--accent);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.edition-nav-dek {
  color: var(--muted);
  font-size: 0.86rem;
  line-height: 1.35;
}
.edition-brief {
  border: 1px solid var(--ink);
  display: grid;
  gap: 18px;
  margin: 0 0 32px;
  padding: 22px;
}
.edition-brief-header {
  display: grid;
  gap: 8px;
}
.edition-brief-header h2,
.edition-brief-header p {
  margin: 0;
}
.edition-brief-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 4.4vw, 5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.94;
}
.edition-brief-header > p:not(.story-section):not(.edition-brief-lead) {
  color: var(--muted);
  line-height: 1.45;
  max-width: 760px;
}
.edition-brief-lead {
  color: var(--ink);
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.25rem, 2.4vw, 2.4rem);
  line-height: 1;
}
.edition-brief-metrics {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
.edition-brief-metric {
  background: var(--panel);
  display: grid;
  gap: 4px;
  padding: 12px;
}
.edition-brief-metric strong {
  font-family: RowOneSerif, Georgia, serif;
  font-size: 1.6rem;
  line-height: 1;
}
.edition-brief-metric span,
.edition-brief-links a,
.edition-brief-links span {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.edition-brief-points {
  display: grid;
  gap: 8px;
  margin: 0;
  padding-left: 20px;
}
.edition-brief-points li {
  line-height: 1.45;
}
.edition-brief-links {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.edition-brief-links a,
.edition-brief-links span {
  border: 1px solid var(--line);
  padding: 8px 10px;
  text-decoration: none;
}
.signal-synthesis {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.signal-synthesis-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.45fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.signal-synthesis-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.2rem, 5vw, 5.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.92;
  margin: 0;
}
.signal-synthesis-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.signal-synthesis-boundary {
  border: 1px solid var(--line);
  color: var(--accent);
  display: inline-flex;
  font-size: 0.72rem;
  font-weight: 700;
  gap: 8px;
  letter-spacing: 0.12em;
  margin: 0 0 18px;
  padding: 8px 10px;
  text-transform: uppercase;
}
.signal-synthesis-grid {
  display: grid;
  gap: 1px;
  background: var(--line);
  border: 1px solid var(--line);
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
.signal-synthesis-group {
  background: var(--panel);
  display: grid;
  gap: 14px;
  min-height: 260px;
  padding: 18px;
}
.signal-synthesis-group-title {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  margin: 0;
  text-transform: uppercase;
}
.signal-synthesis-card {
  border-top: 1px solid var(--line);
  color: var(--ink);
  display: grid;
  gap: 8px;
  padding-top: 14px;
  text-decoration: none;
}
.signal-synthesis-card h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.35rem, 2.3vw, 2.4rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.96;
  margin: 0;
}
.signal-synthesis-card p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
}
.signal-synthesis-meta {
  color: var(--accent);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.7rem;
  font-weight: 700;
  gap: 8px 12px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.daily-local-intelligence {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.daily-local-intelligence-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.daily-local-intelligence-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.2rem, 5vw, 5.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.92;
  margin: 0;
}
.daily-local-intelligence-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.daily-local-intelligence-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
.daily-local-intelligence-group {
  background: var(--panel);
  display: grid;
  gap: 14px;
  min-height: 280px;
  padding: 18px;
}
.daily-local-intelligence-group-title {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  margin: 0;
  text-transform: uppercase;
}
.daily-local-intelligence-card {
  border-top: 1px solid var(--line);
  color: var(--ink);
  display: grid;
  gap: 8px;
  padding-top: 14px;
  text-decoration: none;
}
.daily-local-intelligence-card h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.25rem, 2vw, 2.1rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
}
.daily-local-intelligence-card p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
}
.daily-local-intelligence-meta {
  color: var(--accent);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.7rem;
  font-weight: 700;
  gap: 8px 12px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.daily-local-intelligence-segments {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 10px;
  margin-top: 4px;
  padding-top: 10px;
}
.daily-local-intelligence-segment {
  display: grid;
  gap: 6px;
}
.daily-local-intelligence-card .daily-local-intelligence-segment-title,
.daily-local-intelligence-card .daily-local-intelligence-segment-item-label {
  color: var(--ink);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.09em;
  margin: 0;
  text-transform: uppercase;
}
.daily-local-intelligence-card .daily-local-intelligence-segment-body,
.daily-local-intelligence-card .daily-local-intelligence-segment-item-body,
.daily-local-intelligence-card .daily-local-intelligence-segment-meta {
  color: var(--muted);
  font-size: 0.78rem;
  line-height: 1.38;
  margin: 0;
}
.daily-local-intelligence-segment-items {
  display: grid;
  gap: 7px;
  margin: 0;
}
.daily-local-intelligence-segment-item {
  display: grid;
  gap: 3px;
}
.daily-local-intelligence-segment-meta {
  color: var(--accent);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.65rem;
  font-weight: 700;
  gap: 6px 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.daily-local-intelligence-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-top: 0.85rem;
}
.daily-local-intelligence-action,
.daily-local-intelligence-paragraph-link {
  color: inherit;
  text-decoration: none;
}
.daily-local-intelligence-action {
  border: 1px solid rgba(255, 255, 255, 0.24);
  border-radius: 999px;
  font-size: 0.78rem;
  letter-spacing: 0.04em;
  padding: 0.35rem 0.7rem;
  text-transform: uppercase;
}
.daily-local-intelligence-paragraph-link {
  border-bottom: 1px solid currentColor;
}
.saved-article-coverage {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.saved-article-coverage-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.saved-article-coverage-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.2rem, 5vw, 5.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.92;
  margin: 0;
}
.saved-article-coverage-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.saved-article-coverage-metrics,
.saved-article-coverage-sources {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  list-style: none;
  margin: 0 0 14px;
  padding: 0;
}
.saved-article-coverage-metrics li,
.saved-article-coverage-sources li {
  border: 1px solid var(--line);
  display: inline-flex;
  flex-wrap: wrap;
  gap: 6px 10px;
  padding: 8px 10px;
}
.saved-article-coverage-source-name {
  color: var(--ink);
  font-weight: 700;
}
.saved-article-coverage-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
.saved-article-coverage-card {
  background: var(--panel);
  color: inherit;
  display: grid;
  gap: 10px;
  min-height: 190px;
  padding: 14px;
  text-decoration: none;
}
.saved-article-coverage-card strong {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.2rem, 2vw, 2rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
}
.saved-article-coverage-card span {
  color: var(--muted);
  font-size: 0.78rem;
  line-height: 1.35;
}
.saved-article-library-entry {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.saved-article-library-entry-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.saved-article-library-entry-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.2rem, 5vw, 5.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.92;
  margin: 0;
}
.saved-article-library-entry-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.saved-article-library-entry-metrics,
.saved-article-library-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  list-style: none;
  margin: 0 0 14px;
  padding: 0;
}
.saved-article-library-entry-metrics li,
.saved-article-library-metrics li {
  border: 1px solid var(--line);
  display: inline-flex;
  flex-wrap: wrap;
  gap: 6px 10px;
  padding: 8px 10px;
}
.saved-article-library-entry-link {
  border: 1px solid var(--ink);
  color: var(--ink);
  display: inline-flex;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  padding: 10px 12px;
  text-decoration: none;
  text-transform: uppercase;
}
.saved-article-library-page {
  display: grid;
  gap: 28px;
}
.saved-article-library-hero {
  border-bottom: 1px solid var(--ink);
  display: grid;
  gap: 14px;
  padding-bottom: 28px;
}
.saved-article-library-hero h1 {
  font-size: clamp(3.2rem, 9vw, 8.5rem);
}
.saved-article-library-hero p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 760px;
}
.saved-article-daily-summary {
  border: 1px solid var(--ink);
  display: grid;
  gap: 16px;
  padding: 16px;
}
.saved-article-daily-summary-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.38fr) minmax(0, 1fr);
}
.saved-article-daily-summary-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.85rem, 4vw, 4.4rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.96;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-daily-summary-header p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-daily-summary-metrics,
.saved-article-source-routes-list,
.saved-article-daily-summary-links {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.saved-article-daily-summary-metrics li {
  border: 1px solid var(--line);
  display: inline-flex;
  flex-wrap: wrap;
  gap: 6px 10px;
  padding: 8px 10px;
}
.saved-article-source-routes {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 10px;
  padding-top: 12px;
}
.saved-article-source-routes-header {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  justify-content: space-between;
}
.saved-article-source-routes-header strong {
  color: var(--ink);
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-article-source-routes-metrics {
  color: var(--muted);
  font-size: 0.74rem;
}
.saved-article-source-routes-item {
  display: inline-flex;
}
.saved-article-source-route,
.saved-article-source-routes-link {
  border: 1px solid var(--line);
  color: var(--ink);
  display: grid;
  gap: 4px;
  min-width: min(100%, 170px);
  padding: 9px 10px;
  text-decoration: none;
}
.saved-article-source-routes-label {
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-article-source-routes-meta {
  color: var(--muted);
  font-size: 0.74rem;
}
.saved-article-daily-summary-link {
  border: 1px solid var(--accent);
  color: var(--accent);
  display: inline-flex;
  flex-wrap: wrap;
  font-size: 0.74rem;
  font-weight: 800;
  gap: 6px;
  letter-spacing: 0.08em;
  padding: 8px 10px;
  text-decoration: none;
  text-transform: uppercase;
}
.saved-article-library-grid {
  display: grid;
  gap: 24px;
}
.saved-article-library-source {
  display: grid;
  gap: 12px;
}
.saved-article-library-source-header {
  border-bottom: 1px solid var(--line);
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  justify-content: space-between;
  padding-bottom: 10px;
}
.saved-article-library-source-header h2,
.saved-article-library-source-header p {
  margin: 0;
}
.saved-article-library-source-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.55rem, 3vw, 3rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-library-source-header p {
  color: var(--muted);
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-article-library-source-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.saved-article-library-card {
  background: var(--panel);
  display: grid;
  gap: 12px;
  min-height: 260px;
  min-width: 0;
  padding: 16px;
}
.saved-article-library-card h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.25rem, 2vw, 2.05rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
  overflow-wrap: anywhere;
}
.saved-article-library-card-meta {
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  font-weight: 700;
  gap: 6px 10px;
  letter-spacing: 0.08em;
  overflow-wrap: anywhere;
  text-transform: uppercase;
}
.saved-article-library-card-counts {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.saved-article-library-card-counts li,
.saved-article-library-ref,
.saved-article-library-paragraphs a {
  border: 1px solid var(--line);
  color: var(--ink);
  display: inline-flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  gap: 4px;
  overflow-wrap: anywhere;
  padding: 5px 7px;
  text-decoration: none;
}
.saved-article-library-actions,
.saved-article-library-refs,
.saved-article-library-paragraphs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.saved-article-body-guide {
  border: 1px solid rgba(18, 18, 18, 0.12);
  background: rgba(255, 255, 255, 0.62);
  display: grid;
  gap: 10px;
  padding: 1rem;
}
.saved-article-body-guide-header {
  color: var(--muted);
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-article-body-guide-list {
  display: grid;
  gap: 10px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.saved-article-body-guide-item {
  border-left: 2px solid var(--accent);
  display: grid;
  gap: 6px;
  padding-left: 12px;
}
.saved-article-body-guide-label {
  color: var(--muted);
  font-size: 0.76rem;
  margin: 0;
  text-transform: uppercase;
}
.saved-article-body-guide-body {
  font-size: 0.95rem;
  line-height: 1.55;
  margin: 0;
}
.saved-article-body-guide-evidence {
  display: contents;
}
.saved-article-body-guide-link,
.saved-article-body-guide-evidence a {
  color: var(--accent);
  display: inline-flex;
  font-size: 0.78rem;
  margin-right: 8px;
  text-decoration: none;
}
.saved-article-source-brief {
  border: 1px solid rgba(18, 18, 18, 0.14);
  background: rgba(244, 241, 235, 0.66);
  display: grid;
  gap: 12px;
  margin: 1rem 0 1.2rem;
  padding: 1rem;
}
.saved-article-source-brief-header {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  justify-content: space-between;
}
.saved-article-source-brief-header strong {
  color: var(--ink);
  font-size: 0.82rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-article-source-brief-metrics {
  color: var(--muted);
  font-size: 0.74rem;
}
.saved-article-source-brief-list {
  display: grid;
  gap: 10px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.saved-article-source-brief-item {
  border-left: 2px solid var(--ink);
  display: grid;
  gap: 6px;
  padding-left: 12px;
}
.saved-article-source-brief-label {
  color: var(--muted);
  font-size: 0.76rem;
  margin: 0;
  text-transform: uppercase;
}
.saved-article-source-brief-body {
  font-size: 0.95rem;
  line-height: 1.55;
  margin: 0;
}
.saved-article-source-brief-link {
  color: var(--accent);
  display: inline-flex;
  font-size: 0.78rem;
  text-decoration: none;
}
.saved-article-library-actions a {
  border: 1px solid var(--accent);
  color: var(--accent);
  display: inline-flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  font-weight: 800;
  gap: 5px;
  letter-spacing: 0.08em;
  padding: 7px 9px;
  text-decoration: none;
  text-transform: uppercase;
}
.saved-article-library-primary-action {
  background: var(--accent);
  color: var(--panel) !important;
}
.local-article-page {
  display: grid;
  gap: 28px;
}
.local-article-page-header {
  align-items: center;
  gap: 18px;
}
.local-article-page-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.local-article-page-nav a {
  border: 1px solid var(--line);
  color: var(--ink);
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  padding: 7px 9px;
  text-decoration: none;
  text-transform: uppercase;
}
.local-article-page-article {
  display: grid;
  gap: 18px;
}
.local-article-information {
  border: 1px solid var(--ink);
  display: grid;
  gap: 16px;
  padding: 18px;
}
.local-article-information-header {
  display: grid;
  gap: 8px;
  grid-template-columns: minmax(180px, 0.34fr) minmax(0, 1fr);
}
.local-article-information-header h2,
.local-article-information-header p {
  margin: 0;
}
.local-article-information-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.7rem, 4vw, 3.6rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.96;
}
.local-article-information-header p {
  color: var(--muted);
  line-height: 1.45;
}
.local-article-information-metrics,
.local-article-information-jumps,
.local-article-information-refs,
.local-article-information-paragraphs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.local-article-information-metric,
.local-article-information-jumps a,
.local-article-information-ref,
.local-article-information-paragraphs a {
  border: 1px solid var(--line);
  color: var(--ink);
  font-size: 0.75rem;
  padding: 7px 9px;
  text-decoration: none;
}
.local-article-information-metric {
  display: grid;
  gap: 3px;
  min-width: 120px;
}
.local-article-information-metric strong {
  font-size: 0.88rem;
}
.local-article-information-jumps a,
.local-article-information-paragraphs a {
  color: var(--accent);
  font-weight: 800;
}
.local-article-information-context-cues {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 8px;
  padding-top: 12px;
}
.local-article-information-context-cues h3,
.local-article-information-context-cues p {
  margin: 0;
}
.local-article-information-context-cues h3 {
  font-size: 0.9rem;
}
.local-article-information-context-cue-list {
  display: grid;
  gap: 7px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.local-article-information-context-cue-list a {
  border: 1px solid var(--line);
  color: var(--ink);
  display: grid;
  gap: 4px;
  padding: 8px 9px;
  text-decoration: none;
}
.local-article-information-context-cue-list strong {
  color: var(--accent);
  font-size: 0.74rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.local-article-information-context-cue-list span:last-child {
  color: var(--muted);
  font-size: 0.82rem;
  line-height: 1.4;
}
.local-article-information-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}
.local-article-information-card {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 9px;
  padding-top: 12px;
}
.local-article-information-card h3,
.local-article-information-card h4,
.local-article-information-card p {
  margin: 0;
}
.local-article-information-card h3 {
  font-size: 0.95rem;
}
.local-article-information-card h4 {
  font-size: 0.84rem;
}
.local-article-information-card p {
  color: var(--muted);
  font-size: 0.86rem;
  line-height: 1.45;
}
.local-article-information-items {
  display: grid;
  gap: 8px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.local-article-content-segment-deck {
  border: 1px solid var(--ink);
  display: grid;
  gap: 16px;
  padding: 18px;
}
.local-article-content-segment-deck-header {
  display: grid;
  gap: 8px;
  grid-template-columns: minmax(180px, 0.34fr) minmax(0, 1fr);
}
.local-article-content-segment-deck-header h2,
.local-article-content-segment-deck-header p,
.local-article-content-segment-deck-card h3,
.local-article-content-segment-deck-card p,
.local-article-content-segment-deck-item h4,
.local-article-content-segment-deck-item p {
  margin: 0;
}
.local-article-content-segment-deck-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.7rem, 4vw, 3.6rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.96;
}
.local-article-content-segment-deck-header p,
.local-article-content-segment-deck-card p,
.local-article-content-segment-deck-item p {
  color: var(--muted);
  line-height: 1.45;
}
.local-article-content-segment-deck-metrics,
.local-article-content-segment-deck-refs,
.local-article-content-segment-deck-paragraphs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.local-article-content-segment-deck-metrics span,
.local-article-content-segment-deck-ref,
.local-article-content-segment-deck-paragraphs a,
.local-article-content-segment-deck-action {
  border: 1px solid var(--line);
  color: var(--ink);
  font-size: 0.75rem;
  padding: 7px 9px;
  text-decoration: none;
}
.local-article-content-segment-deck-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}
.local-article-content-segment-deck-card {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 10px;
  padding-top: 12px;
}
.local-article-content-segment-deck-card h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.35rem, 2.8vw, 2.4rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
}
.local-article-content-segment-deck-items {
  display: grid;
  gap: 10px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.local-article-content-segment-deck-item {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 8px;
  padding-top: 10px;
}
.local-article-content-segment-deck-item h4 {
  font-size: 0.88rem;
}
.local-article-content-segment-deck-ref span {
  color: var(--muted);
}
.local-article-content-segment-deck-paragraphs a,
.local-article-content-segment-deck-action {
  color: var(--accent);
  font-weight: 800;
}
.local-article-body-organizer {
  border: 1px solid var(--ink);
  display: grid;
  gap: 16px;
  padding: 18px;
}
.local-article-body-organizer-header {
  display: grid;
  gap: 8px;
  grid-template-columns: minmax(180px, 0.34fr) minmax(0, 1fr);
}
.local-article-body-organizer-header h2,
.local-article-body-organizer-header p,
.local-article-body-organizer-row h3,
.local-article-body-organizer-row p,
.local-article-body-organizer-unfiled h3,
.local-article-body-organizer-unfiled p {
  margin: 0;
}
.local-article-body-organizer-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.7rem, 4vw, 3.6rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.96;
}
.local-article-body-organizer-header p,
.local-article-body-organizer-row p,
.local-article-body-organizer-unfiled p {
  color: var(--muted);
  line-height: 1.45;
}
.local-article-body-organizer-metrics,
.local-article-body-organizer-route,
.local-article-body-organizer-labels,
.local-article-body-organizer-paragraphs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.local-article-body-organizer-metrics span,
.local-article-body-organizer-route a,
.local-article-body-organizer-label,
.local-article-body-organizer-paragraphs a {
  border: 1px solid var(--line);
  color: var(--ink);
  font-size: 0.75rem;
  padding: 7px 9px;
  text-decoration: none;
}
.local-article-body-organizer-route a,
.local-article-body-organizer-paragraphs a {
  color: var(--accent);
  font-weight: 800;
}
.local-article-body-organizer-sections {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}
.local-article-body-organizer-row,
.local-article-body-organizer-unfiled {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 10px;
  padding-top: 12px;
}
.local-article-body-organizer-row h3,
.local-article-body-organizer-unfiled h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.25rem, 2.4vw, 2rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
}
.local-article-intelligence-brief {
  border: 1px solid var(--ink);
  display: grid;
  gap: 16px;
  padding: 18px;
}
.local-article-intelligence-brief-header {
  display: grid;
  gap: 8px;
  grid-template-columns: minmax(180px, 0.34fr) minmax(0, 1fr);
}
.local-article-intelligence-brief-header h2,
.local-article-intelligence-brief-header p,
.local-article-intelligence-brief-opening,
.local-article-intelligence-brief-lane h3,
.local-article-intelligence-brief-lane p {
  margin: 0;
}
.local-article-intelligence-brief-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.7rem, 4vw, 3.6rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.96;
}
.local-article-intelligence-brief-header p,
.local-article-intelligence-brief-opening,
.local-article-intelligence-brief-lane p,
.local-article-intelligence-brief-evidence a > span,
.local-article-intelligence-brief-route a > span {
  color: var(--muted);
  line-height: 1.45;
}
.local-article-intelligence-brief-opening {
  border-top: 1px solid var(--line);
  padding-top: 12px;
}
.local-article-intelligence-brief-lanes {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}
.local-article-intelligence-brief-lane {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 10px;
  padding-top: 12px;
}
.local-article-intelligence-brief-lane h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.25rem, 2.4vw, 2rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
}
.local-article-intelligence-brief-lane > div,
.local-article-intelligence-brief-evidence,
.local-article-intelligence-brief-route {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.local-article-intelligence-brief-chip,
.local-article-intelligence-brief-evidence a,
.local-article-intelligence-brief-route a {
  border: 1px solid var(--line);
  color: var(--ink);
  font-size: 0.75rem;
  padding: 7px 9px;
  text-decoration: none;
}
.local-article-intelligence-brief-chip span,
.local-article-intelligence-brief-evidence strong,
.local-article-intelligence-brief-evidence a > span,
.local-article-intelligence-brief-route strong,
.local-article-intelligence-brief-route a > span {
  display: block;
}
.local-article-intelligence-brief-chip span:last-child {
  color: var(--muted);
}
.local-article-intelligence-brief-evidence a,
.local-article-intelligence-brief-route a {
  display: grid;
  gap: 5px;
  max-width: 320px;
}
.local-article-intelligence-brief-evidence strong,
.local-article-intelligence-brief-route strong {
  color: var(--accent);
}
.local-article-synthesis-brief {
  border: 1px solid var(--ink);
  display: grid;
  gap: 16px;
  padding: 18px;
}
.local-article-synthesis-brief-header {
  display: grid;
  gap: 8px;
  grid-template-columns: minmax(180px, 0.34fr) minmax(0, 1fr);
}
.local-article-synthesis-brief-header h2,
.local-article-synthesis-brief-header p,
.local-article-synthesis-brief-card h3,
.local-article-synthesis-brief-card p,
.local-article-synthesis-brief-route,
.local-article-synthesis-brief-basis {
  margin: 0;
}
.local-article-synthesis-brief-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.7rem, 4vw, 3.6rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.96;
}
.local-article-synthesis-brief-header p,
.local-article-synthesis-brief-card p,
.local-article-synthesis-brief-route,
.local-article-synthesis-brief-anchor span,
.local-article-synthesis-brief-basis {
  color: var(--muted);
  line-height: 1.45;
}
.local-article-synthesis-brief-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}
.local-article-synthesis-brief-card {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 10px;
  padding-top: 12px;
}
.local-article-synthesis-brief-card h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.25rem, 2.4vw, 2rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
}
.local-article-synthesis-brief-route,
.local-article-synthesis-brief-basis {
  border-top: 1px solid var(--line);
  padding-top: 12px;
}
.local-article-synthesis-brief-anchors {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.local-article-synthesis-brief-anchor {
  border: 1px solid var(--line);
  color: var(--ink);
  display: grid;
  font-size: 0.75rem;
  gap: 5px;
  max-width: 320px;
  padding: 7px 9px;
  text-decoration: none;
}
.local-article-synthesis-brief-anchor strong,
.local-article-synthesis-brief-anchor span {
  display: block;
}
.local-article-synthesis-brief-anchor strong {
  color: var(--accent);
}
.saved-article-local-reading-companion {
  border: 1px solid var(--ink);
  display: grid;
  gap: 16px;
  padding: 18px;
}
.saved-article-local-reading-companion-header {
  display: grid;
  gap: 8px;
  grid-template-columns: minmax(180px, 0.34fr) minmax(0, 1fr);
}
.saved-article-local-reading-companion-header h2,
.saved-article-local-reading-companion-header p,
.saved-article-local-reading-companion-current h3,
.saved-article-local-reading-companion-current p,
.saved-article-local-reading-companion-item h3,
.saved-article-local-reading-companion-item p {
  margin: 0;
}
.saved-article-local-reading-companion-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.7rem, 4vw, 3.6rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.96;
}
.saved-article-local-reading-companion-header p,
.saved-article-local-reading-companion-current p,
.saved-article-local-reading-companion-item p {
  color: var(--muted);
  line-height: 1.45;
}
.saved-article-local-reading-companion-metrics,
.saved-article-local-reading-companion-filing-trail,
.saved-article-local-reading-companion-links,
.saved-article-local-reading-companion-meta,
.saved-article-local-reading-companion-refs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.saved-article-local-reading-companion-metrics span,
.saved-article-local-reading-companion-filing-trail strong,
.saved-article-local-reading-companion-filing-trail a,
.saved-article-local-reading-companion-links a,
.saved-article-local-reading-companion-meta span,
.saved-article-local-reading-companion-refs span {
  border: 1px solid var(--line);
  font-size: 0.75rem;
  padding: 7px 9px;
  text-decoration: none;
}
.saved-article-local-reading-companion-metrics span,
.saved-article-local-reading-companion-filing-trail strong,
.saved-article-local-reading-companion-meta span,
.saved-article-local-reading-companion-refs span {
  color: var(--ink);
}
.saved-article-local-reading-companion-filing-trail {
  border-top: 1px solid var(--line);
  padding-top: 10px;
}
.saved-article-local-reading-companion-filing-trail strong {
  font-weight: 800;
}
.saved-article-local-reading-companion-links a,
.saved-article-local-reading-companion-filing-trail a,
.saved-article-local-reading-companion-action {
  color: var(--accent);
  font-weight: 800;
}
.saved-article-local-reading-companion-current {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 10px;
  padding-top: 12px;
}
.saved-article-local-reading-companion-related {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}
.saved-article-local-reading-companion-item {
  border: 1px solid var(--line);
  display: grid;
  gap: 9px;
  padding: 12px;
}
.saved-article-local-reading-companion-current h3,
.saved-article-local-reading-companion-item h3 {
  font-size: 0.95rem;
}
.saved-article-local-reading-companion-action {
  letter-spacing: 0.08em;
  text-decoration: none;
  text-transform: uppercase;
}
.saved-article-local-related-reads {
  border: 1px solid var(--ink);
  display: grid;
  gap: 16px;
  margin-top: 24px;
  padding: 18px;
}
.saved-article-local-related-reads-header {
  display: grid;
  gap: 8px;
  grid-template-columns: minmax(170px, 0.32fr) minmax(0, 1fr);
}
.saved-article-local-related-reads-header h2,
.saved-article-local-related-reads-header p,
.saved-article-local-related-read-card h3,
.saved-article-local-related-read-card p {
  margin: 0;
}
.saved-article-local-related-reads-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.6rem, 3.6vw, 3.2rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.98;
}
.saved-article-local-related-reads-header p,
.saved-article-local-related-read-card p {
  color: var(--muted);
  line-height: 1.45;
}
.saved-article-local-related-reads-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}
.saved-article-local-related-read-lanes {
  display: grid;
  gap: 14px;
}
.saved-article-local-related-read-lane {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 12px;
  padding-top: 14px;
}
.saved-article-local-related-read-lane-header {
  display: grid;
  gap: 6px;
}
.saved-article-local-related-read-lane-header h3,
.saved-article-local-related-read-lane-header p {
  margin: 0;
}
.saved-article-local-related-read-lane-header h3 {
  font-size: 0.9rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-article-local-related-read-lane-header p {
  color: var(--muted);
  line-height: 1.45;
}
.saved-article-local-related-read-connection-brief {
  border: 1px solid var(--line);
  display: grid;
  gap: 12px;
  padding: 14px;
}
.saved-article-local-related-read-connection-brief-copy {
  display: grid;
  gap: 6px;
}
.saved-article-local-related-read-connection-brief-copy h3,
.saved-article-local-related-read-connection-brief-copy p {
  margin: 0;
}
.saved-article-local-related-read-connection-brief-copy h3 {
  font-size: 0.95rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-article-local-related-read-connection-brief-metrics,
.saved-article-local-related-read-connection-brief-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.saved-article-local-related-read-connection-brief-metrics > span,
.saved-article-local-related-read-connection-chip {
  border: 1px solid var(--line);
  color: var(--ink);
  font-size: 0.75rem;
  padding: 7px 9px;
}
.saved-article-local-related-read-connection-brief-metrics strong,
.saved-article-local-related-read-connection-chip span {
  display: block;
}
.saved-article-local-related-read-card {
  border: 1px solid var(--line);
  display: grid;
  gap: 10px;
  padding: 12px;
}
.saved-article-local-related-read-card h3 {
  font-size: 0.95rem;
}
.saved-article-local-related-read-meta,
.saved-article-local-related-read-references {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.saved-article-local-related-read-meta span,
.saved-article-local-related-read-reference {
  border: 1px solid var(--line);
  color: var(--ink);
  font-size: 0.75rem;
  padding: 7px 9px;
}
.saved-article-local-related-read-reference span {
  display: block;
}
.saved-article-local-related-read-reference span:last-child {
  color: var(--muted);
}
.saved-article-local-related-read-evidence-bridge {
  border-top: 1px solid rgba(26, 24, 20, 0.1);
  display: grid;
  gap: 0.45rem;
  padding-top: 0.75rem;
}
.saved-article-local-related-read-evidence-bridge-label {
  color: var(--muted);
  font-size: 0.72rem;
  text-transform: uppercase;
}
.saved-article-local-related-read-evidence-bridge-row {
  display: grid;
  gap: 0.4rem;
}
.saved-article-local-related-read-evidence-bridge-ref,
.saved-article-local-related-read-evidence-bridge-links {
  align-items: center;
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}
.saved-article-local-related-read-evidence-bridge-ref span,
.saved-article-local-related-read-evidence-bridge-links a {
  border: 1px solid rgba(26, 24, 20, 0.12);
  border-radius: 999px;
  color: var(--ink);
  padding: 0.22rem 0.55rem;
  text-decoration: none;
}
.saved-article-local-related-read-action {
  color: var(--accent);
  font-weight: 800;
  letter-spacing: 0.08em;
  text-decoration: none;
  text-transform: uppercase;
}
.saved-article-local-section-binder {
  border: 1px solid var(--line);
  display: grid;
  gap: 16px;
  padding: 18px;
}
.saved-article-local-section-binder-header {
  display: grid;
  gap: 8px;
  grid-template-columns: minmax(170px, 0.32fr) minmax(0, 1fr);
}
.saved-article-local-section-binder-header h2,
.saved-article-local-section-binder-header p,
.saved-article-local-section-binder-row h3,
.saved-article-local-section-binder-row p {
  margin: 0;
}
.saved-article-local-section-binder-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.5rem, 3.5vw, 3rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.98;
}
.saved-article-local-section-binder-header p,
.saved-article-local-section-binder-row p {
  color: var(--muted);
  line-height: 1.45;
}
.saved-article-local-section-binder-meta,
.saved-article-local-section-binder-chips,
.saved-article-local-section-binder-refs,
.saved-article-local-section-binder-paragraphs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.saved-article-local-section-binder-meta span,
.saved-article-local-section-binder-chips span,
.saved-article-local-section-binder-refs span,
.saved-article-local-section-binder-paragraphs a {
  border: 1px solid var(--line);
  color: var(--ink);
  font-size: 0.74rem;
  padding: 7px 9px;
  text-decoration: none;
}
.saved-article-local-section-binder-paragraphs a,
.saved-article-local-section-binder-row > a {
  color: var(--accent);
  font-weight: 800;
}
.saved-article-local-section-binder-grid {
  display: grid;
  gap: 10px;
}
.saved-article-local-section-binder-row {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 9px;
  padding-top: 12px;
}
.saved-article-local-section-binder-row h3 {
  font-size: 0.95rem;
}
.saved-article-local-section-binder-unfiled {
  background: rgba(16, 18, 22, 0.035);
  border: 1px solid var(--line);
  display: grid;
  gap: 9px;
  padding: 12px;
}
.saved-article-key-signals {
  border: 1px solid var(--ink);
  display: grid;
  gap: 16px;
  padding: 18px;
}
.saved-article-key-signals-header {
  display: grid;
  gap: 8px;
  grid-template-columns: minmax(170px, 0.32fr) minmax(0, 1fr);
}
.saved-article-key-signals-header h2,
.saved-article-key-signals-header p,
.saved-article-key-signal h3,
.saved-article-key-signal p {
  margin: 0;
}
.saved-article-key-signals-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.6rem, 3.8vw, 3.2rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.96;
}
.saved-article-key-signals-header p,
.saved-article-key-signal p {
  color: var(--muted);
  line-height: 1.45;
}
.saved-article-key-signals-meta,
.saved-article-key-signal-refs,
.saved-article-key-signal-themes,
.saved-article-key-signal-evidence {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.saved-article-key-signals-meta span,
.saved-article-key-signal-ref,
.saved-article-key-signal-themes a,
.saved-article-key-signal-evidence a {
  border: 1px solid var(--line);
  color: var(--ink);
  font-size: 0.74rem;
  padding: 7px 9px;
  text-decoration: none;
}
.saved-article-key-signal-themes a,
.saved-article-key-signal-evidence a {
  color: var(--accent);
  font-weight: 800;
}
.saved-article-key-signals-grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}
.saved-article-key-signal {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 9px;
  padding-top: 12px;
}
.saved-article-key-signal h3 {
  font-size: 0.95rem;
}
.saved-article-key-signal-statement {
  color: var(--ink);
}
.saved-signal-index {
  border-bottom: 1px solid var(--ink);
  display: grid;
  gap: 18px;
  padding-bottom: 28px;
}
.saved-signal-index-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.36fr) minmax(0, 1fr);
}
.saved-signal-index-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 5vw, 5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.95;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-signal-index-header p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-signal-index-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.saved-signal-index-metrics li {
  border: 1px solid var(--line);
  display: inline-flex;
  flex-wrap: wrap;
  gap: 6px 10px;
  padding: 8px 10px;
}
.saved-article-organization-jump-index {
  border-bottom: 1px solid var(--ink);
  display: grid;
  gap: 18px;
  padding-bottom: 28px;
}
.saved-article-organization-jump-index-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.36fr) minmax(0, 1fr);
}
.saved-article-organization-jump-index-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 5vw, 5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.95;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-organization-jump-index-header p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-organization-jump-index-grid {
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.saved-article-organization-jump-index-group {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 10px;
  min-width: 0;
  padding-top: 14px;
}
.saved-article-organization-jump-index-group h3 {
  font-size: 0.76rem;
  letter-spacing: 0.08em;
  margin: 0;
  text-transform: uppercase;
}
.saved-article-organization-jump-index-items {
  display: grid;
  gap: 8px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.saved-article-organization-jump-index-link {
  border: 1px solid var(--line);
  color: var(--ink);
  display: grid;
  gap: 5px;
  padding: 10px;
  text-decoration: none;
}
.saved-article-organization-jump-index-label {
  font-family: RowOneSerif, Georgia, serif;
  font-size: 1.05rem;
  line-height: 1.15;
}
.saved-article-organization-jump-index-count {
  color: var(--muted);
  font-size: 0.76rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-article-reading-queue {
  border-bottom: 1px solid var(--ink);
  display: grid;
  gap: 18px;
  padding-bottom: 28px;
}
.saved-article-reading-queue-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.36fr) minmax(0, 1fr);
}
.saved-article-reading-queue-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 5vw, 5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.95;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-reading-queue-header p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-reading-queue-list {
  display: grid;
  gap: 10px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.saved-article-reading-queue-item {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(0, 1fr) auto;
  padding-top: 12px;
}
.saved-article-reading-queue-title {
  color: var(--ink);
  font-family: RowOneSerif, Georgia, serif;
  font-size: 1.16rem;
  line-height: 1.15;
  text-decoration: none;
}
.saved-article-reading-queue-meta {
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.76rem;
  gap: 6px 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-article-reading-queue-action {
  align-self: start;
  border: 1px solid var(--ink);
  color: var(--ink);
  font-size: 0.76rem;
  letter-spacing: 0.08em;
  padding: 8px 10px;
  text-decoration: none;
  text-transform: uppercase;
}
.saved-article-filing-inbox {
  border-bottom: 1px solid var(--ink);
  display: grid;
  gap: 18px;
  padding-bottom: 28px;
}
.saved-article-filing-inbox-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.36fr) minmax(0, 1fr);
}
.saved-article-filing-inbox-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 5vw, 5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.95;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-filing-inbox-header p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-filing-inbox-metrics {
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.76rem;
  gap: 6px 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-article-filing-inbox-list {
  display: grid;
  gap: 14px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.saved-article-filing-inbox-item {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 12px;
  grid-template-columns: minmax(180px, 0.34fr) minmax(0, 1fr);
  padding-top: 14px;
}
.saved-article-filing-inbox-item h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: 1.2rem;
  line-height: 1.15;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-filing-inbox-meta {
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  gap: 6px 9px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-article-filing-inbox-paragraphs {
  display: grid;
  gap: 8px;
}
.saved-article-filing-inbox-paragraph {
  border: 1px solid var(--line);
  color: var(--ink);
  display: grid;
  gap: 6px;
  padding: 10px;
  text-decoration: none;
}
.saved-article-filing-inbox-link {
  color: var(--ink);
  font-size: 0.76rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-article-filing-inbox-paragraph p {
  color: var(--muted);
  line-height: 1.42;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-read-next-clusters {
  border-bottom: 1px solid var(--ink);
  display: grid;
  gap: 18px;
  padding-bottom: 28px;
}
.saved-article-read-next-clusters-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.36fr) minmax(0, 1fr);
}
.saved-article-read-next-clusters-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 5vw, 5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.95;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-read-next-clusters-header p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-read-next-clusters-metrics {
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.76rem;
  gap: 6px 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-article-read-next-clusters-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.saved-article-read-next-clusters-cluster {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 12px;
  min-width: 0;
  padding-top: 14px;
}
.saved-article-read-next-clusters-cluster h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: 1.24rem;
  line-height: 1.12;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-read-next-clusters-cluster p {
  color: var(--muted);
  line-height: 1.4;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-read-next-clusters-item {
  border: 1px solid var(--line);
  display: grid;
  gap: 8px;
  padding: 12px;
}
.saved-article-read-next-clusters-item h4 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: 1.08rem;
  line-height: 1.15;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-read-next-clusters-meta {
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  gap: 6px 9px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-article-read-next-clusters-lead {
  line-height: 1.45;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-read-next-clusters-refs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.saved-article-read-next-clusters-refs span {
  border: 1px solid var(--line);
  border-radius: 999px;
  color: var(--muted);
  font-size: 0.72rem;
  line-height: 1.2;
  padding: 5px 8px;
}
.saved-article-read-next-clusters-action {
  color: var(--ink);
  font-size: 0.76rem;
  letter-spacing: 0.08em;
  text-decoration: underline;
  text-transform: uppercase;
}
.saved-article-signal-facets {
  border-bottom: 1px solid var(--ink);
  display: grid;
  gap: 18px;
  padding-bottom: 28px;
}
.saved-article-signal-facets-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.36fr) minmax(0, 1fr);
}
.saved-article-signal-facets-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 5vw, 5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.95;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-signal-facets-header p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-signal-facets-grid {
  display: grid;
  gap: 12px;
}
.saved-article-signal-facets-row {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 14px;
  grid-template-columns: minmax(220px, 1.4fr) repeat(3, minmax(140px, 1fr));
  padding-top: 14px;
}
.saved-article-signal-facets-article,
.saved-article-signal-facets-column {
  display: grid;
  gap: 8px;
}
.saved-article-signal-facets-article a {
  color: var(--ink);
  font-family: RowOneSerif, Georgia, serif;
  font-size: 1.1rem;
  line-height: 1.15;
  text-decoration: none;
}
.saved-article-signal-facets-source,
.saved-article-signal-facets-metric,
.saved-article-signal-facets-column-label {
  color: var(--muted);
  font-size: 0.76rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-article-signal-facets-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.saved-article-signal-facets-chip {
  border: 1px solid var(--line);
  border-radius: 999px;
  display: inline-flex;
  font-size: 0.78rem;
  line-height: 1.2;
  padding: 5px 9px;
}
.saved-article-signal-facets-empty {
  color: var(--muted);
  font-size: 0.82rem;
}
.saved-article-daily-signal-leaderboard {
  border-bottom: 1px solid var(--ink);
  display: grid;
  gap: 18px;
  padding-bottom: 28px;
}
.saved-article-daily-signal-leaderboard-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.36fr) minmax(0, 1fr);
}
.saved-article-daily-signal-leaderboard-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 5vw, 5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.95;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-daily-signal-leaderboard-header p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-daily-signal-leaderboard-grid {
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.saved-article-daily-signal-leaderboard-bucket {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 12px;
  min-width: 0;
  padding-top: 14px;
}
.saved-article-daily-signal-leaderboard-bucket h3 {
  font-size: 0.76rem;
  letter-spacing: 0.08em;
  margin: 0;
  text-transform: uppercase;
}
.saved-article-daily-signal-leaderboard-item {
  border: 1px solid var(--line);
  display: grid;
  gap: 10px;
  padding: 12px;
}
.saved-article-daily-signal-leaderboard-label {
  font-family: RowOneSerif, Georgia, serif;
  font-size: 1.1rem;
  line-height: 1.15;
}
.saved-article-daily-signal-leaderboard-metrics {
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.76rem;
  gap: 6px 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-article-daily-signal-leaderboard-supports {
  display: grid;
  gap: 6px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.saved-article-daily-signal-leaderboard-support {
  color: var(--muted);
  display: grid;
  font-size: 0.82rem;
  gap: 4px;
}
.saved-article-daily-signal-leaderboard-support a {
  color: var(--ink);
  text-decoration-thickness: 1px;
}
.saved-signal-index-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.saved-signal-index-card {
  background: var(--panel);
  display: grid;
  gap: 12px;
  min-width: 0;
  padding: 16px;
}
.saved-signal-index-card-header {
  display: grid;
  gap: 8px;
}
.saved-signal-index-card-header h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.45rem, 3vw, 2.6rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-signal-index-card-meta {
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  font-weight: 800;
  gap: 6px 10px;
  letter-spacing: 0.08em;
  overflow-wrap: anywhere;
  text-transform: uppercase;
}
.saved-signal-index-support {
  display: grid;
  gap: 8px;
}
.saved-signal-index-support-row {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 8px;
  min-width: 0;
  padding-top: 10px;
}
.saved-signal-index-support-row strong,
.saved-signal-index-support-meta {
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-signal-index-support-meta,
.saved-signal-index-actions,
.saved-signal-index-paragraphs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 10px;
}
.saved-signal-index-support-meta {
  color: var(--muted);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-signal-index-support-excerpt {
  margin: 0;
  color: var(--ink);
  font-size: 0.9rem;
  line-height: 1.55;
  overflow-wrap: anywhere;
}
.saved-signal-index-actions a,
.saved-signal-index-paragraphs a {
  border: 1px solid var(--line);
  color: var(--ink);
  display: inline-flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  gap: 4px;
  overflow-wrap: anywhere;
  padding: 5px 7px;
  text-decoration: none;
}
.saved-article-theme-digest {
  border-bottom: 1px solid var(--ink);
  display: grid;
  gap: 18px;
  padding-bottom: 28px;
}
.saved-article-theme-digest-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.36fr) minmax(0, 1fr);
}
.saved-article-theme-digest-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 5vw, 5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.95;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-theme-digest-header p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-theme-digest-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.saved-article-theme-digest-metrics li {
  border: 1px solid var(--line);
  display: inline-flex;
  flex-wrap: wrap;
  gap: 6px 10px;
  padding: 8px 10px;
}
.saved-article-theme-digest-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
}
.saved-article-theme-digest-card {
  background: var(--panel);
  display: grid;
  gap: 12px;
  min-width: 0;
  padding: 16px;
}
.saved-article-theme-digest-card-header {
  display: grid;
  gap: 8px;
}
.saved-article-theme-digest-card-header h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.45rem, 3vw, 2.6rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-theme-digest-card-header p {
  margin: 0;
}
.saved-article-theme-digest-card-meta,
.saved-article-theme-digest-item-meta {
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  font-weight: 800;
  gap: 6px 10px;
  letter-spacing: 0.08em;
  overflow-wrap: anywhere;
  text-transform: uppercase;
}
.saved-article-theme-digest-items {
  display: grid;
  gap: 10px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.saved-article-theme-digest-item {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 8px;
  min-width: 0;
  padding-top: 10px;
}
.saved-article-theme-digest-item h4 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.15rem, 2vw, 1.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-theme-digest-lead {
  font-size: 0.92rem;
  line-height: 1.5;
  margin: 0;
  overflow-wrap: anywhere;
}
.saved-article-theme-digest-actions,
.saved-article-theme-digest-evidence,
.saved-article-theme-digest-refs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.saved-article-theme-digest-link,
.saved-article-theme-digest-ref {
  border: 1px solid var(--line);
  color: var(--ink);
  display: inline-flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  gap: 4px;
  overflow-wrap: anywhere;
  padding: 5px 7px;
  text-decoration: none;
}
.saved-article-reference-atlas {
  border-bottom: 1px solid var(--ink);
  display: grid;
  gap: 18px;
  padding-bottom: 28px;
}
.saved-article-reference-atlas-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.36fr) minmax(0, 1fr);
}
.saved-article-reference-atlas-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 5vw, 5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.95;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-reference-atlas-header p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-reference-atlas-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.saved-article-reference-atlas-metrics li {
  border: 1px solid var(--line);
  display: inline-flex;
  flex-wrap: wrap;
  gap: 6px 10px;
  padding: 8px 10px;
}
.saved-article-reference-atlas-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
}
.saved-article-reference-atlas-bucket {
  background: var(--panel);
  display: grid;
  gap: 12px;
  min-width: 0;
  padding: 16px;
}
.saved-article-reference-atlas-bucket-header {
  display: grid;
  gap: 8px;
}
.saved-article-reference-atlas-bucket-header h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.45rem, 3vw, 2.6rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-reference-atlas-bucket-header p,
.saved-article-reference-atlas-lead {
  line-height: 1.5;
  margin: 0;
  overflow-wrap: anywhere;
}
.saved-article-reference-atlas-entry-meta,
.saved-article-reference-atlas-support-meta {
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  font-weight: 800;
  gap: 6px 10px;
  letter-spacing: 0.08em;
  overflow-wrap: anywhere;
  text-transform: uppercase;
}
.saved-article-reference-atlas-list {
  display: grid;
  gap: 12px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.saved-article-reference-atlas-entry {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 10px;
  min-width: 0;
  padding-top: 10px;
}
.saved-article-reference-atlas-entry h4 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.15rem, 2vw, 1.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-reference-atlas-support {
  display: grid;
  gap: 7px;
  min-width: 0;
}
.saved-article-reference-atlas-actions,
.saved-article-reference-atlas-evidence {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.saved-article-reference-atlas-link,
.saved-article-reference-atlas-ref {
  border: 1px solid var(--line);
  color: var(--ink);
  display: inline-flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  gap: 4px;
  overflow-wrap: anywhere;
  padding: 5px 7px;
  text-decoration: none;
}
.saved-article-reading-paths {
  border-bottom: 1px solid var(--ink);
  display: grid;
  gap: 18px;
  padding-bottom: 28px;
}
.saved-article-reading-paths-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.36fr) minmax(0, 1fr);
}
.saved-article-reading-paths-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 5vw, 5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.95;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-reading-paths-header p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-reading-paths-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
}
.saved-article-reading-path-card {
  background: var(--panel);
  display: grid;
  gap: 12px;
  min-width: 0;
  padding: 16px;
}
.saved-article-reading-path-card-header {
  display: grid;
  gap: 8px;
}
.saved-article-reading-path-card-header h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.45rem, 3vw, 2.6rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-reading-path-card-header p {
  margin: 0;
}
.saved-article-reading-path-count {
  color: var(--muted);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-article-reading-path-steps {
  display: grid;
  gap: 10px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.saved-article-reading-path-step {
  display: grid;
  gap: 6px;
  min-width: 0;
}
.saved-article-reading-path-step-link {
  border-top: 1px solid var(--line);
  color: inherit;
  display: grid;
  gap: 10px;
  grid-template-columns: auto minmax(0, 1fr);
  padding-top: 10px;
  text-decoration: none;
}
.saved-article-reading-path-step-number {
  align-items: center;
  border: 1px solid var(--line);
  display: inline-flex;
  font-size: 0.72rem;
  font-weight: 800;
  height: 24px;
  justify-content: center;
  width: 24px;
}
.saved-article-reading-path-step-copy {
  display: grid;
  gap: 5px;
  min-width: 0;
}
.saved-article-reading-path-step-meta {
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.7rem;
  font-weight: 800;
  gap: 5px 9px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-article-reading-path-step-lead {
  font-size: 0.92rem;
  line-height: 1.5;
}
.saved-article-reading-path-link,
.saved-article-reading-path-evidence a {
  color: var(--accent);
  display: inline-flex;
  font-size: 0.78rem;
  font-weight: 800;
  gap: 5px;
  letter-spacing: 0.08em;
  text-decoration: none;
  text-transform: uppercase;
}
.saved-article-reading-path-evidence {
  display: contents;
}
.saved-article-evidence-board {
  border-bottom: 1px solid var(--ink);
  display: grid;
  gap: 18px;
  padding-bottom: 28px;
}
.saved-article-evidence-board-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.36fr) minmax(0, 1fr);
}
.saved-article-evidence-board-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 5vw, 5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.95;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-evidence-board-header p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-evidence-board-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.saved-article-evidence-board-metrics li {
  border: 1px solid var(--line);
  display: inline-flex;
  flex-wrap: wrap;
  gap: 6px 10px;
  padding: 8px 10px;
}
.saved-article-evidence-board-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
}
.saved-article-evidence-board-group {
  background: var(--panel);
  display: grid;
  gap: 14px;
  min-width: 0;
  padding: 16px;
}
.saved-article-evidence-board-group-header {
  display: grid;
  gap: 8px;
}
.saved-article-evidence-board-group-header h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.45rem, 3vw, 2.6rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-evidence-board-group-header p {
  margin: 0;
}
.saved-article-evidence-board-cards {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
}
.saved-article-evidence-board-card {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 8px;
  min-width: 0;
  padding-top: 10px;
}
.saved-article-evidence-board-card h4 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.15rem, 2vw, 1.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-evidence-board-card-meta,
.saved-article-evidence-board-paragraph {
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  font-weight: 800;
  gap: 6px 10px;
  letter-spacing: 0.08em;
  overflow-wrap: anywhere;
  text-transform: uppercase;
}
.saved-article-evidence-board-excerpt {
  font-size: 0.92rem;
  line-height: 1.5;
  margin: 0;
  overflow-wrap: anywhere;
}
.saved-article-evidence-board-actions,
.saved-article-evidence-board-refs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.saved-article-evidence-board-link,
.saved-article-evidence-board-ref {
  border: 1px solid var(--line);
  color: var(--ink);
  display: inline-flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  gap: 4px;
  overflow-wrap: anywhere;
  padding: 5px 7px;
  text-decoration: none;
}
.saved-article-briefs {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.saved-article-briefs-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.saved-article-briefs-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.2rem, 5vw, 5.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.92;
  margin: 0;
}
.saved-article-briefs-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.saved-article-briefs-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
.saved-article-brief-card {
  background: var(--panel);
  color: inherit;
  display: grid;
  gap: 12px;
  min-height: 260px;
  padding: 16px;
  text-decoration: none;
}
.saved-article-brief-card h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.25rem, 2vw, 2.05rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
}
.saved-article-brief-meta {
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  font-weight: 700;
  gap: 6px 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-article-brief-body {
  color: var(--ink);
  font-size: 0.9rem;
  line-height: 1.42;
  margin: 0;
}
.saved-article-brief-chip-groups {
  display: grid;
  gap: 10px;
}
.saved-article-brief-chip-group {
  display: grid;
  gap: 6px;
}
.saved-article-brief-chip-heading {
  color: var(--muted);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-article-brief-chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.saved-article-brief-chip {
  border: 1px solid var(--line);
  color: var(--ink);
  display: inline-flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  gap: 4px;
  padding: 5px 7px;
}
.saved-article-brief-chip span:last-child {
  color: var(--muted);
}
.daily-local-key-signals-digest {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.daily-local-key-signals-digest-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.daily-local-key-signals-digest-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.2rem, 5vw, 5.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.92;
  margin: 0;
}
.daily-local-key-signals-digest-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.daily-local-key-signals-digest-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 0 0 14px;
}
.daily-local-key-signals-digest-metrics span {
  border: 1px solid var(--line);
  color: var(--muted);
  display: inline-flex;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  padding: 5px 8px;
  text-transform: uppercase;
}
.daily-local-key-signals-digest-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(5, minmax(0, 1fr));
}
.daily-local-key-signals-digest-group {
  background: var(--panel);
  display: grid;
  gap: 12px;
  min-height: 260px;
  padding: 14px;
}
.daily-local-key-signals-digest-group h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.25rem, 2vw, 2.05rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
}
.daily-local-key-signals-digest-total {
  color: var(--muted);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  margin: 0;
  text-transform: uppercase;
}
.daily-local-key-signals-digest-entry {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 7px;
  padding-top: 10px;
}
.daily-local-key-signals-digest-entry h4 {
  font-size: 0.95rem;
  line-height: 1.15;
  margin: 0;
}
.daily-local-key-signals-digest-entry p {
  color: var(--ink);
  font-size: 0.85rem;
  line-height: 1.4;
  margin: 0;
}
.daily-local-key-signals-digest-meta {
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.68rem;
  font-weight: 700;
  gap: 6px 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.daily-local-key-signals-digest-action {
  border: 1px solid var(--ink);
  color: var(--ink);
  display: inline-flex;
  font-size: 0.72rem;
  font-weight: 700;
  justify-content: center;
  letter-spacing: 0.08em;
  padding: 7px 9px;
  text-decoration: none;
  text-transform: uppercase;
}
.daily-local-signal-momentum {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.daily-local-signal-momentum-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.daily-local-signal-momentum-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.1rem, 4.5vw, 5.2rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.94;
  margin: 0;
}
.daily-local-signal-momentum-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.daily-local-signal-momentum-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 0 0 14px;
}
.daily-local-signal-momentum-metrics span {
  border: 1px solid var(--line);
  color: var(--muted);
  display: inline-flex;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  padding: 5px 8px;
  text-transform: uppercase;
}
.daily-local-signal-momentum-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.daily-local-signal-momentum-bucket {
  background: var(--panel);
  display: grid;
  gap: 12px;
  min-height: 260px;
  padding: 14px;
}
.daily-local-signal-momentum-bucket h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.25rem, 2vw, 2.05rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
}
.daily-local-signal-momentum-item {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 8px;
  padding-top: 10px;
}
.daily-local-signal-momentum-label {
  font-size: 1rem;
  font-weight: 700;
  line-height: 1.15;
}
.daily-local-signal-momentum-counts {
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.68rem;
  font-weight: 700;
  gap: 6px 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.daily-local-signal-momentum-supports {
  display: grid;
  gap: 6px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.daily-local-signal-momentum-support {
  display: grid;
  gap: 3px;
}
.daily-local-signal-momentum-support a {
  color: var(--ink);
  font-size: 0.84rem;
  line-height: 1.35;
  text-decoration-color: var(--line);
  text-underline-offset: 3px;
}
.daily-local-signal-momentum-support > span {
  color: var(--muted);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.daily-local-heat-signals {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.daily-local-heat-signals-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.daily-local-heat-signals-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.1rem, 4.5vw, 5.2rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.94;
  margin: 0;
}
.daily-local-heat-signals-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.daily-local-heat-signals-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 0 0 14px;
}
.daily-local-heat-signals-metrics span {
  border: 1px solid var(--line);
  color: var(--muted);
  display: inline-flex;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  padding: 5px 8px;
  text-transform: uppercase;
}
.daily-local-heat-signals-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.daily-local-heat-signals-topic {
  background: var(--panel);
  display: grid;
  gap: 14px;
  min-height: 280px;
  padding: 14px;
}
.daily-local-heat-signals-topic-header {
  display: grid;
  gap: 12px;
}
.daily-local-heat-signals-topic-title {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.35rem, 2.2vw, 2.25rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.98;
  margin: 0 0 10px;
}
.daily-local-heat-signals-topic-badges,
.daily-local-heat-signals-topic-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.daily-local-heat-signals-topic-badges span,
.daily-local-heat-signals-topic-metrics span {
  border: 1px solid var(--line);
  color: var(--muted);
  display: inline-flex;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  padding: 5px 8px;
  text-transform: uppercase;
}
.daily-local-heat-signals-topic-metrics span:first-child {
  border-color: var(--ink);
  color: var(--ink);
}
.daily-local-heat-signals-topic-stories {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 10px;
  list-style: none;
  margin: 0;
  padding: 12px 0 0;
}
.daily-local-heat-signals-story {
  display: grid;
  gap: 4px;
}
.daily-local-heat-signals-story a {
  color: var(--ink);
  font-size: 0.9rem;
  font-weight: 700;
  line-height: 1.3;
  text-decoration-color: var(--line);
  text-underline-offset: 3px;
}
.daily-local-heat-signals-story-meta {
  color: var(--muted);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.daily-local-article-capsules {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.daily-local-article-capsules-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.daily-local-article-capsules-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.1rem, 4.5vw, 5.2rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.94;
  margin: 0;
}
.daily-local-article-capsules-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.daily-local-article-capsules-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 0 0 14px;
}
.daily-local-article-capsules-metrics span {
  border: 1px solid var(--line);
  color: var(--muted);
  display: inline-flex;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  padding: 5px 8px;
  text-transform: uppercase;
}
.daily-local-article-capsules-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: 1fr;
}
.daily-local-article-capsule {
  background: var(--panel);
  display: grid;
  gap: 14px;
  min-height: 320px;
  padding: 16px;
}
.daily-local-article-capsule-header {
  display: grid;
  gap: 10px;
}
.daily-local-article-capsule-title {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.4rem, 2.2vw, 2.35rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.98;
  margin: 0;
}
.daily-local-article-capsule-title a {
  color: var(--ink);
  text-decoration-color: var(--line);
  text-underline-offset: 4px;
}
.daily-local-article-capsule-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.daily-local-article-capsule-meta span,
.daily-local-article-capsule-ref span {
  border: 1px solid var(--line);
  color: var(--muted);
  display: inline-flex;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  padding: 5px 8px;
  text-transform: uppercase;
}
.daily-local-article-capsule-source-title {
  color: var(--ink) !important;
}
.daily-local-article-capsule-why {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
}
.daily-local-article-capsule-paragraphs {
  display: grid;
  gap: 8px;
}
.daily-local-article-capsule-paragraph {
  border-top: 1px solid var(--line);
  color: var(--ink);
  display: grid;
  gap: 5px;
  line-height: 1.42;
  padding-top: 8px;
  text-decoration: none;
}
.daily-local-article-capsule-paragraph-label {
  color: var(--muted);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.daily-local-article-capsule-refs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.daily-local-article-capsule-ref {
  display: inline-flex;
  gap: 4px;
}
.daily-local-article-capsule-link {
  align-self: end;
  color: var(--ink);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-decoration-color: var(--line);
  text-transform: uppercase;
  text-underline-offset: 4px;
}
.daily-local-article-reading-brief {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.daily-local-article-reading-brief-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.daily-local-article-reading-brief-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.1rem, 4.5vw, 5.2rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.94;
  margin: 0;
}
.daily-local-article-reading-brief-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.daily-local-article-reading-brief-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 0 0 14px;
}
.daily-local-article-reading-brief-metrics span {
  border: 1px solid var(--line);
  color: var(--muted);
  display: inline-flex;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  padding: 5px 8px;
  text-transform: uppercase;
}
.daily-local-article-reading-brief-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: 1fr;
}
.daily-local-article-reading-brief-group {
  background: var(--panel);
  display: grid;
  gap: 14px;
  min-height: 320px;
  padding: 16px;
}
.daily-local-article-reading-brief-group-header {
  display: grid;
  gap: 8px;
}
.daily-local-article-reading-brief-group-header h3,
.daily-local-article-reading-brief-group-header p {
  margin: 0;
}
.daily-local-article-reading-brief-group-header h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.45rem, 2.4vw, 2.5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.98;
}
.daily-local-article-reading-brief-group-header p {
  color: var(--muted);
  line-height: 1.45;
}
.daily-local-article-reading-brief-items {
  display: grid;
  gap: 12px;
}
.daily-local-article-reading-brief-item {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 10px;
  padding-top: 12px;
}
.daily-local-article-reading-brief-title {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.2rem, 2vw, 1.9rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
}
.daily-local-article-reading-brief-title a {
  color: var(--ink);
  text-decoration-color: var(--line);
  text-underline-offset: 4px;
}
.daily-local-article-reading-brief-meta,
.daily-local-article-reading-brief-refs,
.daily-local-article-reading-brief-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.daily-local-article-reading-brief-meta span,
.daily-local-article-reading-brief-ref,
.daily-local-article-reading-brief-ref span {
  border: 1px solid var(--line);
  color: var(--muted);
  display: inline-flex;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  padding: 5px 8px;
  text-transform: uppercase;
}
.daily-local-article-reading-brief-source {
  color: var(--ink) !important;
}
.daily-local-article-reading-brief-article-title {
  color: var(--ink) !important;
}
.daily-local-article-reading-brief-ref {
  gap: 4px;
}
.daily-local-article-reading-brief-reason {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
}
.daily-local-article-reading-brief-excerpt {
  border-top: 1px solid var(--line);
  color: var(--ink);
  display: grid;
  gap: 5px;
  line-height: 1.42;
  padding-top: 8px;
  text-decoration-color: var(--line);
  text-underline-offset: 3px;
}
.daily-local-article-reading-brief-action {
  color: var(--ink);
  font-size: 0.76rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-decoration-color: var(--line);
  text-transform: uppercase;
  text-underline-offset: 4px;
}
.daily-local-source-desk {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.daily-local-source-desk-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.daily-local-source-desk-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.1rem, 4.5vw, 5.2rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.94;
  margin: 0;
}
.daily-local-source-desk-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.daily-local-source-desk-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 0 0 14px;
}
.daily-local-source-desk-metrics span,
.daily-local-source-desk-counts span,
.daily-local-source-desk-body-sources span,
.daily-local-source-desk-ref,
.daily-local-source-desk-ref span {
  border: 1px solid var(--line);
  color: var(--muted);
  display: inline-flex;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  padding: 5px 8px;
  text-transform: uppercase;
}
.daily-local-source-desk-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: 1fr;
}
.daily-local-source-desk-source {
  background: var(--panel);
  display: grid;
  gap: 14px;
  min-height: 280px;
  padding: 16px;
}
.daily-local-source-desk-source-header,
.daily-local-source-desk-links,
.daily-local-source-desk-link {
  display: grid;
  gap: 10px;
}
.daily-local-source-desk-source-title {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.45rem, 2.4vw, 2.5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.98;
  margin: 0;
}
.daily-local-source-desk-counts,
.daily-local-source-desk-body-sources,
.daily-local-source-desk-refs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.daily-local-source-desk-body-sources span,
.daily-local-source-desk-counts span {
  color: var(--ink);
}
.daily-local-source-desk-ref {
  gap: 4px;
}
.daily-local-source-desk-link {
  border-top: 1px solid var(--line);
  padding-top: 12px;
}
.daily-local-source-desk-link a {
  color: var(--ink);
  display: grid;
  gap: 4px;
  text-decoration-color: var(--line);
  text-underline-offset: 4px;
}
.daily-local-source-desk-link a > span:first-child {
  font-family: RowOneSerif, Georgia, serif;
  font-size: 1.2rem;
  line-height: 1;
}
.daily-local-source-desk-link-article-title {
  color: var(--muted);
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.daily-local-source-desk-paragraph-link {
  color: var(--accent) !important;
  font-size: 0.76rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-decoration-color: var(--line);
  text-transform: uppercase;
}
.daily-local-coverage-map {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.daily-local-coverage-map-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.daily-local-coverage-map-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.1rem, 4.5vw, 5.2rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.94;
  margin: 0;
}
.daily-local-coverage-map-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.daily-local-coverage-map-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 0 0 14px;
}
.daily-local-coverage-map-metrics span,
.daily-local-coverage-map-counts span,
.daily-local-coverage-map-bucket,
.daily-local-coverage-map-bucket span,
.daily-local-coverage-map-ref,
.daily-local-coverage-map-ref span,
.daily-local-coverage-map-link-bucket {
  border: 1px solid var(--line);
  color: var(--muted);
  display: inline-flex;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  padding: 5px 8px;
  text-transform: uppercase;
}
.daily-local-coverage-map-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: 1fr;
}
.daily-local-coverage-map-source {
  background: var(--panel);
  display: grid;
  gap: 14px;
  min-height: 280px;
  padding: 16px;
}
.daily-local-coverage-map-source-header,
.daily-local-coverage-map-links,
.daily-local-coverage-map-link {
  display: grid;
  gap: 10px;
}
.daily-local-coverage-map-source-title {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.45rem, 2.4vw, 2.5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.98;
  margin: 0;
}
.daily-local-coverage-map-counts,
.daily-local-coverage-map-buckets,
.daily-local-coverage-map-refs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.daily-local-coverage-map-counts span {
  color: var(--ink);
}
.daily-local-coverage-map-ref,
.daily-local-coverage-map-bucket {
  gap: 4px;
}
.daily-local-coverage-map-link {
  border-top: 1px solid var(--line);
  padding-top: 12px;
}
.daily-local-coverage-map-link a {
  color: var(--ink);
  display: grid;
  gap: 4px;
  text-decoration-color: var(--line);
  text-underline-offset: 4px;
}
.daily-local-coverage-map-link a > span:first-child {
  font-family: RowOneSerif, Georgia, serif;
  font-size: 1.2rem;
  line-height: 1;
}
.daily-local-coverage-map-link-bucket {
  color: var(--accent) !important;
  width: fit-content;
}
.daily-local-theme-summary-strip {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.daily-local-theme-summary-strip-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.daily-local-theme-summary-strip-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.1rem, 4.5vw, 5.2rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.94;
  margin: 0;
}
.daily-local-theme-summary-strip-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.daily-local-theme-summary-strip-metrics,
.daily-local-theme-summary-strip-meta,
.daily-local-theme-summary-strip-refs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.daily-local-theme-summary-strip-metrics {
  margin: 0 0 14px;
}
.daily-local-theme-summary-strip-metrics span,
.daily-local-theme-summary-strip-meta span,
.daily-local-theme-summary-strip-ref,
.daily-local-theme-summary-strip-ref span,
.daily-local-theme-summary-strip-source {
  border: 1px solid var(--line);
  color: var(--muted);
  display: inline-flex;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  overflow-wrap: anywhere;
  padding: 5px 8px;
  text-transform: uppercase;
}
.daily-local-theme-summary-strip-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: 1fr;
}
.daily-local-theme-summary-strip-theme {
  background: var(--panel);
  display: grid;
  gap: 14px;
  min-height: 260px;
  padding: 16px;
}
.daily-local-theme-summary-strip-theme-header,
.daily-local-theme-summary-strip-links,
.daily-local-theme-summary-strip-link {
  display: grid;
  gap: 10px;
}
.daily-local-theme-summary-strip-title {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.45rem, 2.4vw, 2.5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.98;
  margin: 0;
}
.daily-local-theme-summary-strip-summary {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
}
.daily-local-theme-summary-strip-ref {
  gap: 4px;
}
.daily-local-theme-summary-strip-link {
  border-top: 1px solid var(--line);
  padding-top: 12px;
}
.daily-local-theme-summary-strip-link a {
  color: var(--ink);
  display: grid;
  gap: 4px;
  text-decoration-color: var(--line);
  text-underline-offset: 4px;
}
.daily-local-theme-summary-strip-link a > span:first-child {
  font-family: RowOneSerif, Georgia, serif;
  font-size: 1.2rem;
  line-height: 1;
}
.daily-local-theme-summary-strip-source {
  color: var(--accent) !important;
  width: fit-content;
}
.daily-local-news-timeline {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.daily-local-news-timeline-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.daily-local-news-timeline-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.1rem, 4.8vw, 5.5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.94;
  margin: 0;
}
.daily-local-news-timeline-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.daily-local-news-timeline-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 0 0 14px;
}
.daily-local-news-timeline-meta span,
.daily-local-news-timeline-date,
.daily-local-news-timeline-source {
  border: 1px solid var(--line);
  color: var(--muted);
  display: inline-flex;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  overflow-wrap: anywhere;
  padding: 5px 8px;
  text-transform: uppercase;
  width: fit-content;
}
.daily-local-news-timeline-list {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.daily-local-news-timeline-item {
  background: var(--panel);
  display: grid;
  gap: 10px;
  min-height: 245px;
  padding: 16px;
}
.daily-local-news-timeline-link {
  color: var(--ink);
  display: grid;
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.35rem, 2.25vw, 2.45rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.98;
  text-decoration-color: var(--line);
  text-underline-offset: 4px;
}
.daily-local-news-timeline-source {
  color: var(--accent);
  margin: 0;
}
.daily-local-news-timeline-excerpt {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
}
.daily-local-news-timeline-link:hover,
.daily-local-news-timeline-link:focus-visible {
  opacity: 0.75;
}
.daily-local-article-intelligence-brief {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.daily-local-article-intelligence-brief-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.daily-local-article-intelligence-brief-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.1rem, 4.8vw, 5.5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.94;
  margin: 0;
}
.daily-local-article-intelligence-brief-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.daily-local-article-intelligence-brief-metrics,
.daily-local-article-intelligence-brief-card-meta,
.daily-local-article-intelligence-brief-chips,
.daily-local-article-intelligence-brief-routes {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.daily-local-article-intelligence-brief-metrics {
  margin: 0 0 14px;
}
.daily-local-article-intelligence-brief-metrics span,
.daily-local-article-intelligence-brief-card-meta span,
.daily-local-article-intelligence-brief-chip,
.daily-local-article-intelligence-brief-chip span,
.daily-local-article-intelligence-brief-lane-header span,
.daily-local-article-intelligence-brief-route {
  border: 1px solid var(--line);
  color: var(--muted);
  display: inline-flex;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  overflow-wrap: anywhere;
  padding: 5px 8px;
  text-transform: uppercase;
}
.daily-local-article-intelligence-brief-summary {
  color: var(--muted);
  line-height: 1.45;
  margin: 0 0 16px;
  max-width: 860px;
}
.daily-local-article-intelligence-brief-lanes {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin: 0 0 18px;
}
.daily-local-article-intelligence-brief-lane {
  background: var(--panel);
  display: grid;
  gap: 12px;
  min-height: 175px;
  padding: 14px;
}
.daily-local-article-intelligence-brief-lane-header {
  display: grid;
  gap: 8px;
}
.daily-local-article-intelligence-brief-lane-header h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.25rem, 2vw, 2rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
}
.daily-local-article-intelligence-brief-chip {
  color: var(--ink);
  gap: 4px;
}
.daily-local-article-intelligence-brief-chip span:last-child {
  color: var(--muted);
}
.daily-local-article-intelligence-brief-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.daily-local-article-intelligence-brief-card {
  background: var(--panel);
  display: grid;
  gap: 12px;
  min-height: 285px;
  padding: 16px;
}
.daily-local-article-intelligence-brief-card-title {
  color: var(--ink);
  display: grid;
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.35rem, 2.25vw, 2.45rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.98;
  text-decoration-color: var(--line);
  text-underline-offset: 4px;
}
.daily-local-article-intelligence-brief-card p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
}
.daily-local-article-intelligence-brief-route {
  color: var(--accent);
  text-decoration: none;
}
.daily-local-article-intelligence-brief-card-title:hover,
.daily-local-article-intelligence-brief-card-title:focus-visible,
.daily-local-article-intelligence-brief-route:hover,
.daily-local-article-intelligence-brief-route:focus-visible {
  opacity: 0.75;
}
.daily-local-synthesis-brief {
  background: var(--ink);
  color: var(--panel);
  margin: 28px 0;
  padding: 22px;
}
.daily-local-synthesis-brief-header {
  display: grid;
  gap: 18px;
  grid-template-columns: minmax(0, 1.15fr) minmax(220px, 0.85fr);
  margin-bottom: 18px;
}
.daily-local-synthesis-brief-header h2,
.daily-local-synthesis-brief-header p {
  margin: 0;
}
.daily-local-synthesis-brief-header h2 {
  color: var(--panel);
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 4vw, 4.6rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.96;
  text-transform: none;
}
.daily-local-synthesis-brief-header p {
  color: var(--steel);
  line-height: 1.55;
}
.daily-local-synthesis-brief-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 16px;
}
.daily-local-synthesis-brief-metrics span,
.daily-local-synthesis-brief-card-meta span,
.daily-local-synthesis-brief-route {
  border: 1px solid rgba(244, 246, 248, 0.24);
  color: var(--chrome);
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  padding: 6px 8px;
  text-transform: uppercase;
}
.daily-local-synthesis-brief-opening,
.daily-local-synthesis-brief-thesis {
  margin: 0 0 14px;
}
.daily-local-synthesis-brief-opening {
  color: var(--panel);
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.45rem, 2.5vw, 2.55rem);
  line-height: 1.05;
}
.daily-local-synthesis-brief-thesis {
  color: var(--steel);
  line-height: 1.55;
}
.daily-local-synthesis-brief-grid {
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin-top: 18px;
}
.daily-local-synthesis-brief-card {
  background: #15181d;
  border: 1px solid rgba(244, 246, 248, 0.16);
  display: grid;
  gap: 12px;
  min-width: 0;
  padding: 16px;
}
.daily-local-synthesis-brief-card h3,
.daily-local-synthesis-brief-card p {
  margin: 0;
}
.daily-local-synthesis-brief-card h3 {
  color: var(--panel);
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.2rem, 1.8vw, 1.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1.02;
  overflow-wrap: anywhere;
  text-transform: none;
}
.daily-local-synthesis-brief-card p {
  color: var(--steel);
  line-height: 1.5;
  overflow-wrap: anywhere;
}
.daily-local-synthesis-brief-card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  min-width: 0;
}
.daily-local-synthesis-brief-card-meta span {
  overflow-wrap: anywhere;
}
.daily-local-synthesis-brief-route {
  color: var(--panel);
  overflow-wrap: anywhere;
  text-decoration: none;
}
.daily-local-synthesis-brief-evidence-trail {
  border-top: 1px solid rgba(244, 246, 248, 0.14);
  display: grid;
  gap: 8px;
  min-width: 0;
  padding-top: 10px;
}
.daily-local-synthesis-brief-evidence-trail p {
  color: var(--chrome);
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  margin: 0;
  text-transform: uppercase;
}
.daily-local-synthesis-brief-evidence-link {
  color: var(--panel);
  display: grid;
  gap: 3px;
  line-height: 1.3;
  overflow-wrap: anywhere;
  text-decoration-color: rgba(244, 246, 248, 0.26);
  text-underline-offset: 3px;
}
.daily-local-synthesis-brief-evidence-support {
  color: var(--steel);
  font-size: 0.82rem;
  overflow-wrap: anywhere;
}
.daily-local-synthesis-brief-route:hover,
.daily-local-synthesis-brief-route:focus-visible {
  background: var(--panel);
  color: var(--ink);
}
.daily-local-synthesis-brief-basis {
  border-top: 1px solid rgba(244, 246, 248, 0.22);
  color: var(--chrome);
  font-size: 0.78rem;
  line-height: 1.45;
  margin: 18px 0 0;
  padding-top: 14px;
}
.daily-local-saved-text-takeaways {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.daily-local-saved-text-takeaways-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.44fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.daily-local-saved-text-takeaways-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 4.6vw, 5.2rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.94;
  margin: 0;
}
.daily-local-saved-text-takeaways-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.daily-local-saved-text-takeaways-metrics,
.daily-local-saved-text-takeaways-card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  min-width: 0;
}
.daily-local-saved-text-takeaways-metrics {
  margin: 0 0 18px;
}
.daily-local-saved-text-takeaways-metrics span,
.daily-local-saved-text-takeaways-card-meta span,
.daily-local-saved-text-takeaways-lane-count,
.daily-local-saved-text-takeaways-card-link {
  border: 1px solid var(--line);
  color: var(--muted);
  display: inline-flex;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  overflow-wrap: anywhere;
  padding: 5px 8px;
  text-transform: uppercase;
}
.daily-local-saved-text-takeaways-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.daily-local-saved-text-takeaways-lane {
  background: var(--panel);
  display: grid;
  gap: 14px;
  min-height: 300px;
  min-width: 0;
  padding: 16px;
}
.daily-local-saved-text-takeaways-lane-header {
  display: grid;
  gap: 8px;
}
.daily-local-saved-text-takeaways-lane-header h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.3rem, 2vw, 2rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
}
.daily-local-saved-text-takeaways-lane-header p {
  color: var(--muted);
  line-height: 1.4;
  margin: 0;
}
.daily-local-saved-text-takeaways-cards {
  display: grid;
  gap: 12px;
}
.daily-local-saved-text-takeaways-card {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 10px;
  min-width: 0;
  padding-top: 12px;
}
.daily-local-saved-text-takeaways-card h4 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.12rem, 1.7vw, 1.75rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
  overflow-wrap: anywhere;
}
.daily-local-saved-text-takeaways-card p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  overflow-wrap: anywhere;
}
.daily-local-saved-text-takeaways-card-link {
  color: var(--accent);
  text-decoration: none;
  width: fit-content;
}
.daily-local-saved-text-takeaways-card-link:hover,
.daily-local-saved-text-takeaways-card-link:focus-visible {
  opacity: 0.75;
}
.daily-local-brand-product-people-signal-digest {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.daily-local-brand-product-people-signal-digest-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.44fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.daily-local-brand-product-people-signal-digest-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 4.6vw, 5.2rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.94;
  margin: 0;
}
.daily-local-brand-product-people-signal-digest-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.daily-local-brand-product-people-signal-digest-metrics,
.daily-local-brand-product-people-signal-digest-item-meta,
.daily-local-brand-product-people-signal-digest-support-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  min-width: 0;
}
.daily-local-brand-product-people-signal-digest-metrics {
  margin: 0 0 18px;
}
.daily-local-brand-product-people-signal-digest-metrics > span,
.daily-local-brand-product-people-signal-digest-bucket-header > span,
.daily-local-brand-product-people-signal-digest-item-meta > span,
.daily-local-brand-product-people-signal-digest-support-meta > span,
.daily-local-brand-product-people-signal-digest-link {
  border: 1px solid var(--line);
  color: var(--muted);
  display: inline-flex;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  overflow-wrap: anywhere;
  padding: 5px 8px;
  text-transform: uppercase;
}
.daily-local-brand-product-people-signal-digest-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.daily-local-brand-product-people-signal-digest-bucket {
  background: var(--panel);
  display: grid;
  gap: 14px;
  min-width: 0;
  padding: 16px;
}
.daily-local-brand-product-people-signal-digest-bucket-header {
  align-items: start;
  display: flex;
  gap: 8px;
  justify-content: space-between;
}
.daily-local-brand-product-people-signal-digest-bucket-header h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.3rem, 2vw, 2rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
  overflow-wrap: anywhere;
}
.daily-local-brand-product-people-signal-digest-items,
.daily-local-brand-product-people-signal-digest-supports {
  display: grid;
  gap: 12px;
  min-width: 0;
}
.daily-local-brand-product-people-signal-digest-item {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 10px;
  min-width: 0;
  padding-top: 12px;
}
.daily-local-brand-product-people-signal-digest-item h4 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.12rem, 1.7vw, 1.75rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
  overflow-wrap: anywhere;
}
.daily-local-brand-product-people-signal-digest-support {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 8px;
  min-width: 0;
  padding-top: 10px;
}
.daily-local-brand-product-people-signal-digest-support h5 {
  font-size: 0.9rem;
  line-height: 1.25;
  margin: 0;
  overflow-wrap: anywhere;
}
.daily-local-brand-product-people-signal-digest-support-excerpt {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  overflow-wrap: anywhere;
}
.daily-local-brand-product-people-signal-digest-link {
  color: var(--accent);
  text-decoration: none;
  width: fit-content;
}
.daily-local-brand-product-people-signal-digest-link:hover,
.daily-local-brand-product-people-signal-digest-link:focus-visible {
  opacity: 0.75;
}
.daily-local-saved-article-organizer {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.daily-local-saved-article-organizer-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.daily-local-saved-article-organizer-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.1rem, 4.8vw, 5.5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.94;
  margin: 0;
}
.daily-local-saved-article-organizer-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.daily-local-saved-article-organizer-metrics,
.daily-local-saved-article-organizer-card-meta,
.daily-local-saved-article-organizer-refs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.daily-local-saved-article-organizer-metrics {
  margin: 0 0 18px;
}
.daily-local-saved-article-organizer-metrics span,
.daily-local-saved-article-organizer-card-meta span,
.daily-local-saved-article-organizer-lane-count,
.daily-local-saved-article-organizer-ref,
.daily-local-saved-article-organizer-card-link {
  border: 1px solid var(--line);
  color: var(--muted);
  display: inline-flex;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  overflow-wrap: anywhere;
  padding: 5px 8px;
  text-transform: uppercase;
}
.daily-local-saved-article-organizer-lanes {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
.daily-local-saved-article-organizer-lane {
  background: var(--panel);
  display: grid;
  gap: 14px;
  min-height: 320px;
  padding: 16px;
}
.daily-local-saved-article-organizer-lane-header {
  display: grid;
  gap: 8px;
}
.daily-local-saved-article-organizer-lane-header h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.35rem, 2.2vw, 2.2rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
}
.daily-local-saved-article-organizer-lane-header p {
  color: var(--muted);
  line-height: 1.4;
  margin: 0;
}
.daily-local-saved-article-organizer-cards {
  display: grid;
  gap: 12px;
}
.daily-local-saved-article-organizer-card {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 10px;
  padding-top: 12px;
}
.daily-local-saved-article-organizer-card h4 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.15rem, 1.8vw, 1.9rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
}
.daily-local-saved-article-organizer-card p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
}
.daily-local-saved-article-organizer-ref {
  color: var(--ink);
  gap: 4px;
}
.daily-local-saved-article-organizer-ref span:last-child {
  color: var(--muted);
}
.daily-local-saved-article-organizer-card-link {
  color: var(--accent);
  text-decoration: none;
  width: fit-content;
}
.daily-local-saved-article-organizer-card-link:hover,
.daily-local-saved-article-organizer-card-link:focus-visible {
  opacity: 0.75;
}
.daily-local-reading-itinerary {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.daily-local-reading-itinerary-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.38fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.daily-local-reading-itinerary-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 4.4vw, 5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.96;
  margin: 0;
}
.daily-local-reading-itinerary-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 680px;
}
.daily-local-reading-itinerary-metrics,
.daily-local-reading-itinerary-labels,
.daily-local-reading-itinerary-evidence {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.daily-local-reading-itinerary-metrics {
  margin: 0 0 18px;
}
.daily-local-reading-itinerary-metrics span,
.daily-local-reading-itinerary-card-meta span,
.daily-local-reading-itinerary-label,
.daily-local-reading-itinerary-chip,
.daily-local-reading-itinerary-card-link {
  border: 1px solid var(--line);
  color: var(--muted);
  display: inline-flex;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  overflow-wrap: anywhere;
  padding: 5px 8px;
  text-transform: uppercase;
}
.daily-local-reading-itinerary-grid {
  display: grid;
  gap: 18px;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
}
.daily-local-reading-itinerary-panel {
  background: var(--panel);
  border: 1px solid var(--line);
  display: grid;
  gap: 14px;
  padding: 16px;
}
.daily-local-reading-itinerary-panel h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.35rem, 2.2vw, 2.2rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
}
.daily-local-reading-itinerary-stack {
  display: grid;
  gap: 12px;
}
.daily-local-reading-itinerary-card {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 10px;
  padding-top: 12px;
}
.daily-local-reading-itinerary-start {
  border-top: 0;
  padding-top: 0;
}
.daily-local-reading-itinerary-card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.daily-local-reading-itinerary-card h4 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.2rem, 2vw, 2rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
}
.daily-local-reading-itinerary-card p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
}
.daily-local-reading-itinerary-label,
.daily-local-reading-itinerary-chip {
  color: var(--ink);
}
.daily-local-reading-itinerary-card-link,
.daily-local-reading-itinerary-chip {
  color: var(--accent);
  text-decoration: none;
  width: fit-content;
}
.daily-local-reading-itinerary-card-link:hover,
.daily-local-reading-itinerary-card-link:focus-visible,
.daily-local-reading-itinerary-chip:hover,
.daily-local-reading-itinerary-chip:focus-visible {
  opacity: 0.75;
}
.saved-article-content-organization {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.saved-article-content-organization-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.saved-article-content-organization-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.2rem, 5vw, 5.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.92;
  margin: 0;
}
.saved-article-content-organization-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.saved-article-organization-coverage-matrix {
  border: 1px solid var(--line);
  display: grid;
  gap: 12px;
  margin: 0 0 18px;
  padding: 12px;
}
.saved-article-organization-coverage-header {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  justify-content: space-between;
}
.saved-article-organization-coverage-header h3,
.saved-article-organization-coverage-header p {
  margin: 0;
}
.saved-article-organization-coverage-header h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.35rem, 2.2vw, 2.35rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
}
.saved-article-organization-coverage-header p {
  color: var(--muted);
  max-width: 560px;
}
.saved-article-organization-coverage-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
}
.saved-article-organization-coverage-row {
  background: var(--panel);
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.85fr) minmax(0, 1.4fr);
  padding: 12px;
}
.saved-article-organization-coverage-title {
  display: grid;
  gap: 6px;
}
.saved-article-organization-coverage-title h4 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.12rem, 1.7vw, 1.7rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
}
.saved-article-organization-coverage-title p,
.saved-article-organization-coverage-meta {
  color: var(--muted);
  font-size: 0.74rem;
  margin: 0;
}
.saved-article-organization-coverage-meta,
.saved-article-organization-coverage-chips,
.saved-article-organization-coverage-refs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.saved-article-organization-coverage-chip,
.saved-article-organization-coverage-ref {
  border: 1px solid var(--line);
  color: var(--ink);
  display: inline-flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  gap: 5px;
  padding: 6px 8px;
}
.saved-article-organization-coverage-ref span:last-child {
  color: var(--muted);
}
.saved-article-organization-coverage-link {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-decoration: none;
  text-transform: uppercase;
}
.saved-article-content-organization-groups {
  display: grid;
  gap: 18px;
}
.saved-article-content-organization-group {
  display: grid;
  gap: 12px;
}
.saved-article-content-organization-group-header {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  justify-content: space-between;
}
.saved-article-content-organization-group-header h3,
.saved-article-content-organization-group-header p {
  margin: 0;
}
.saved-article-content-organization-group-header h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.4rem, 2.4vw, 2.6rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
}
.saved-article-content-organization-group-header p {
  color: var(--muted);
  max-width: 520px;
}
.saved-article-content-organization-summary {
  border: 1px solid var(--line);
  display: grid;
  gap: 8px;
  padding: 10px;
}
.saved-article-content-organization-summary-metrics,
.saved-article-content-organization-summary-refs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.saved-article-content-organization-summary-metric,
.saved-article-content-organization-summary-ref {
  border: 1px solid var(--line);
  color: var(--ink);
  display: inline-flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  gap: 5px;
  padding: 6px 8px;
}
.saved-article-content-organization-summary-ref span:last-child {
  color: var(--muted);
}
.saved-article-content-organization-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
.saved-article-content-organization-card {
  background: var(--panel);
  color: inherit;
  display: grid;
  gap: 12px;
  min-height: 285px;
  padding: 16px;
  text-decoration: none;
}
.saved-article-content-organization-card h4 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.18rem, 1.8vw, 1.85rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
}
.saved-article-content-organization-meta {
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  font-weight: 700;
  gap: 6px 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-article-content-organization-lead {
  color: var(--ink);
  font-size: 0.9rem;
  line-height: 1.42;
  margin: 0;
}
.saved-article-content-organization-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.saved-article-content-organization-chip {
  border: 1px solid var(--line);
  color: var(--ink);
  display: inline-flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  gap: 4px;
  padding: 5px 7px;
}
.saved-article-content-organization-chip span:last-child {
  color: var(--muted);
}
.saved-article-content-organization-card-link {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-decoration: none;
  text-transform: uppercase;
}
.saved-article-content-organization-evidence {
  display: contents;
}
.saved-article-content-organization-evidence-link {
  border: 1px solid var(--accent);
  color: var(--accent);
  display: inline-flex;
  flex-wrap: wrap;
  font-size: 0.68rem;
  font-weight: 800;
  gap: 5px;
  letter-spacing: 0.08em;
  padding: 5px 7px;
  text-decoration: none;
  text-transform: uppercase;
}
.editorial-brief {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.editorial-brief-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.editorial-brief-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.2rem, 5vw, 5.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.92;
  margin: 0;
}
.editorial-brief-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.editorial-brief-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.editorial-brief-card {
  background: var(--panel);
  color: var(--ink);
  display: grid;
  gap: 12px;
  min-height: 275px;
  padding: 18px;
  text-decoration: none;
}
.editorial-brief-card h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.35rem, 2.2vw, 2.4rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.98;
  margin: 0;
}
.editorial-brief-card p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
}
.editorial-brief-meta {
  align-self: end;
  border-top: 1px solid var(--line);
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  padding-top: 12px;
  text-transform: uppercase;
}
.editorial-brief-trail {
  border-top: 1px solid var(--line);
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding-top: 12px;
}
.editorial-brief-trail-item,
.editorial-brief-trail a {
  border-radius: 999px;
  border: 1px solid var(--line);
  color: var(--accent);
  display: inline-flex;
  font-size: 0.72rem;
  font-weight: 700;
  gap: 4px;
  letter-spacing: 0.08em;
  padding: 5px 7px;
  text-decoration: none;
  text-transform: uppercase;
}
.editorial-brief-trail a:hover,
.editorial-brief-trail a:focus-visible,
.editorial-brief-link:hover,
.editorial-brief-link:focus-visible {
  opacity: 0.75;
}
.editorial-brief-link {
  align-items: center;
  color: var(--accent);
  display: inline-flex;
  font-size: 0.74rem;
  font-weight: 800;
  gap: 6px;
  letter-spacing: 0.12em;
  text-decoration: none;
  text-transform: uppercase;
}
.editorial-brief-link::after {
  content: "↗";
}
.daily-edit {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.daily-edit-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.daily-edit-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.2rem, 5vw, 5.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.92;
  margin: 0;
}
.daily-edit-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.daily-edit-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
.daily-edit-card {
  background: var(--panel);
  color: var(--ink);
  display: grid;
  gap: 12px;
  min-height: 245px;
  padding: 18px;
  text-decoration: none;
}
.daily-edit-card h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.35rem, 2.2vw, 2.4rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.98;
  margin: 0;
}
.daily-edit-card p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
}
.daily-edit-card-meta {
  align-self: end;
  border-top: 1px solid var(--line);
  color: var(--accent);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  font-weight: 700;
  gap: 8px 14px;
  letter-spacing: 0.1em;
  padding-top: 12px;
  text-transform: uppercase;
}
.daily-edit-link {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-decoration: none;
  text-transform: uppercase;
}
.briefing-topics {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.briefing-topics-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.45fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.briefing-topics-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.2rem, 5vw, 5.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.92;
  margin: 0;
}
.briefing-topics-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.briefing-topic-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1px;
  background: var(--line);
  border: 1px solid var(--line);
}
.briefing-topic-card {
  background: var(--panel);
  color: var(--ink);
  display: grid;
  gap: 14px;
  min-height: 230px;
  padding: 18px;
  text-decoration: none;
}
.briefing-topic-card h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.5rem, 2.6vw, 2.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.95;
  margin: 0;
}
.briefing-topic-card p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
}
.briefing-topic-label,
.briefing-topic-count {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.briefing-topic-meta {
  align-self: end;
  border-top: 1px solid var(--line);
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  padding-top: 12px;
}
.briefing-topic-empty {
  border: 1px solid var(--line);
  color: var(--muted);
  margin: 0;
  padding: 18px;
}
.briefing-path {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.briefing-path-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.45fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.briefing-path-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 4.4vw, 5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.94;
  margin: 0;
}
.briefing-path-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.briefing-path-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1px;
  background: var(--line);
  border: 1px solid var(--line);
}
.briefing-path-block {
  background: var(--paper);
  display: grid;
  gap: 14px;
  padding: 18px;
}
.briefing-path-block h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.55rem, 2.8vw, 3rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.98;
  margin: 0;
}
.briefing-path-block > p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
}
.briefing-path-card {
  border-top: 1px solid var(--line);
  color: var(--ink);
  display: grid;
  gap: 8px;
  padding-top: 14px;
  text-decoration: none;
}
.briefing-path-card h4 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.2rem, 2vw, 2rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
}
.briefing-path-card p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
}
.briefing-path-meta {
  color: var(--accent);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  font-weight: 700;
  gap: 8px 14px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.lead-story {
  border-top: 1px solid var(--ink);
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 32px 0;
}
.lead-story-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(260px, 0.75fr);
  gap: 32px;
  align-items: end;
}
.lead-story h2 {
  margin: 10px 0 0;
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(3rem, 8vw, 7.5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.9;
}
.lead-story h2 a, .lead-story-link {
  color: var(--ink);
  text-decoration: none;
}
.lead-story-link {
  border-bottom: 1px solid var(--accent);
  color: var(--accent);
  display: inline-block;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  margin-top: 12px;
  padding-bottom: 4px;
  text-transform: uppercase;
}
.story-visual {
  border: 1px solid var(--ink);
  background: var(--panel);
  display: grid;
  margin: 0;
  min-height: 220px;
  overflow: hidden;
  position: relative;
}
.story-visual img {
  display: block;
  height: 100%;
  object-fit: cover;
  width: 100%;
}
.story-visual-fallback {
  align-content: space-between;
  background:
    linear-gradient(90deg, rgba(16, 18, 22, 0.08) 1px, transparent 1px),
    linear-gradient(0deg, rgba(16, 18, 22, 0.08) 1px, transparent 1px),
    var(--steel);
  background-size: 28px 28px;
  color: var(--ink);
  display: grid;
  min-height: inherit;
  padding: 16px;
}
.story-visual-mark {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 7vw, 6rem);
  line-height: 0.88;
  max-width: 8ch;
}
.story-visual-meta {
  color: var(--accent);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  font-weight: 700;
  gap: 8px 14px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.story-visual--editorial { background: var(--panel); }
.story-visual--portrait { background: var(--chrome); }
.story-visual--product { background: var(--steel); }
.story-visual--signal { background: var(--paper); }
.story-visual--ink { border-color: var(--ink); }
.story-visual--graphite { border-color: var(--muted); }
.story-visual--steel { border-color: var(--chrome); }
.story-visual--cobalt { border-color: var(--accent); }
.story-visual--rose { border-color: var(--muted); }
.lead-story-visual { min-height: clamp(280px, 36vw, 520px); }
.story-card-visual {
  margin-bottom: 16px;
  min-height: 180px;
}
.detail-visual {
  margin: 24px 0 30px;
  min-height: clamp(260px, 45vw, 520px);
}
.section-block {
  display: grid;
  grid-template-columns: minmax(180px, 0.45fr) minmax(0, 1fr);
  gap: 32px;
  border-top: 1px solid var(--line);
  padding: 32px 0;
}
.section-heading h2 {
  margin: 0 0 10px;
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 4vw, 4.4rem);
  font-weight: 500;
  letter-spacing: 0;
}
.section-heading p { color: var(--muted); margin: 0; }
.story-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}
.story-card {
  min-height: 230px;
  border: 1px solid var(--line);
  background: var(--panel);
  padding: 20px;
  display: grid;
  align-content: space-between;
}
.story-card-header,
.story-card-body,
.story-card-footer {
  display: flex;
  gap: 16px;
  justify-content: space-between;
}
.story-card-header {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.11em;
  margin-bottom: 14px;
  text-transform: uppercase;
}
.story-card-body {
  display: grid;
}
.story-card-footer {
  align-items: center;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  margin-top: 14px;
  padding-top: 12px;
  text-transform: uppercase;
}
.story-detail-link {
  color: var(--accent);
  font-weight: 700;
}
.local-read-path {
  align-items: center;
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.74rem;
  gap: 8px 10px;
  letter-spacing: 0.08em;
  margin: 12px 0 0;
  text-transform: uppercase;
}
.local-read-path-badge {
  border: 1px solid var(--accent);
  color: var(--accent);
  font-weight: 700;
  padding: 4px 7px;
}
.local-read-action {
  border-bottom: 1px solid var(--accent);
  color: var(--accent);
  font-weight: 800;
  padding-bottom: 3px;
  text-decoration: none;
}
.detail-local-read-path {
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  padding: 12px 0;
}
.story-tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 14px 0 0;
}
.story-tag-list span {
  border: 1px solid var(--line);
  color: var(--muted);
  font-size: 0.7rem;
  letter-spacing: 0.08em;
  padding: 5px 7px;
  text-transform: uppercase;
}
.story-card a {
  color: var(--ink);
  text-decoration: none;
}
.story-card h3 {
  margin: 0;
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.45rem, 2.4vw, 2.35rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
}
.story-takeaway {
  color: var(--ink);
  font-family: RowOneSerif, Georgia, serif;
  font-size: 1.06rem;
  margin: 8px 0;
}
.story-card p, .detail-article p { color: var(--muted); line-height: 1.55; }
.story-orientation {
  color: var(--muted);
  font-size: 0.78rem;
  letter-spacing: 0.04em;
  margin: 10px 0 0;
  text-transform: uppercase;
}
.story-meta {
  color: var(--accent);
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.detail-header {
  padding: 24px min(7vw, 88px);
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid var(--line);
}
.back-link, .source-link, .source-action-link, .evidence-item a {
  color: var(--accent);
  text-decoration: none;
}
.source-action {
  margin: 10px 0 0;
}
.source-action-link {
  border: 1px solid var(--accent);
  display: inline-flex;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  padding: 10px 12px;
  text-transform: uppercase;
}
.detail-main { max-width: 920px; margin: 0 auto; }
.detail-article h1 { font-size: clamp(3rem, 8vw, 7rem); margin: 18px 0 24px; }
.detail-article h2 {
  font-size: 0.78rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--accent);
  margin-top: 36px;
}
.article-contents {
  border-bottom: 1px solid var(--line);
  border-top: 1px solid var(--line);
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 28px 0;
  padding: 14px 0;
}
.article-contents a {
  border: 1px solid var(--line);
  color: var(--ink);
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  padding: 8px 10px;
  text-decoration: none;
  text-transform: uppercase;
}
.local-article {
  border-bottom: 1px solid var(--line);
  border-top: 1px solid var(--line);
  margin: 36px 0;
  padding: 28px 0;
}
.local-article-source {
  color: var(--muted);
  font-size: 0.84rem;
  margin: 0 0 18px;
}
.local-article-provenance {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 0 0 18px;
}
.local-article-provenance-item {
  border: 1px solid var(--line);
  border-radius: 4px;
  color: var(--muted);
  display: inline-flex;
  font-size: 0.76rem;
  gap: 6px;
  padding: 6px 8px;
  text-decoration: none;
}
.local-article-provenance-link { color: var(--accent); font-weight: 700; }
.local-article-provenance-value { color: var(--ink); }
.local-article h3 {
  font-size: 1.35rem;
  font-weight: 700;
  margin: 0 0 18px;
}
.local-article-map {
  border: 1px solid var(--line);
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 0 0 22px;
  padding: 12px;
}
.local-article-map a,
.local-article-content-paragraph-links a {
  border: 1px solid var(--line);
  color: var(--accent);
  font-size: 0.78rem;
  font-weight: 700;
  padding: 7px 9px;
  text-decoration: none;
}
.local-article-content-paragraph-links a {
  display: inline-block;
  margin: 0 4px 4px 0;
}
.local-article-paragraph-context {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  line-height: 1.35;
  text-transform: uppercase;
}
.local-article-paragraph-context-label {
  color: var(--muted);
}
.local-article-paragraph-context-links {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 6px;
}
.local-article-paragraph-context a {
  border-bottom: 1px solid rgba(36, 84, 255, 0.3);
  color: var(--accent);
  text-decoration: none;
}
.local-article-body-filing-cue {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  line-height: 1.35;
  text-transform: uppercase;
}
.local-article-body-filing-cue-label {
  color: var(--muted);
}
.local-article-body-filing-cue-links {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 6px;
}
.local-article-body-filing-cue-unfiled {
  border: 1px solid var(--line);
  color: var(--muted);
  padding: 2px 6px;
}
.local-article-body-filing-cue a {
  border-bottom: 1px solid rgba(36, 84, 255, 0.3);
  color: var(--accent);
  text-decoration: none;
}
.local-article-body-section-marker {
  border: 1px solid var(--line);
  border-left: 3px solid var(--accent);
  border-radius: 4px;
  display: grid;
  gap: 10px;
  margin: 22px 0 12px;
  padding: 14px 16px;
}
.local-article-body-section-marker-header {
  align-items: center;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: space-between;
}
.local-article-body-section-marker-header span {
  color: var(--muted);
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.local-article-body-section-marker-title {
  font-size: 1rem;
  margin: 0;
}
.local-article-body-section-marker-support {
  color: var(--muted);
  margin: 0;
}
.local-article-body-section-marker-chips,
.local-article-body-section-marker-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.local-article-body-section-marker-chip,
.local-article-body-section-marker-ref,
.local-article-body-section-marker-actions a {
  border: 1px solid var(--line);
  color: var(--ink);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  padding: 6px 8px;
  text-decoration: none;
  text-transform: uppercase;
}
.local-article-body-section-marker-ref span {
  color: var(--muted);
  margin-left: 6px;
}
.local-article-body-section-marker-actions a {
  color: var(--accent);
}
.local-article-paragraph-evidence {
  border: 1px solid var(--line);
  border-radius: 4px;
  margin: 14px 0 16px;
  padding: 14px;
}
.local-article-paragraph-evidence-header {
  display: grid;
  gap: 6px;
  margin: 0 0 12px;
}
.local-article-paragraph-evidence-header h4,
.local-article-paragraph-evidence-header p {
  margin: 0;
}
.local-article-paragraph-evidence-header h4 {
  font-size: 0.9rem;
}
.local-article-paragraph-evidence-header p {
  color: var(--muted);
  font-size: 0.82rem;
}
.local-article-paragraph-evidence-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.local-article-paragraph-evidence-row {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 8px;
  padding-top: 10px;
}
.local-article-paragraph-evidence-link {
  color: var(--accent);
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-decoration: none;
  text-transform: uppercase;
}
.local-article-paragraph-evidence-excerpt {
  line-height: 1.45;
  margin: 0;
}
.local-article-paragraph-evidence-supports {
  display: grid;
  gap: 8px;
}
.local-article-paragraph-evidence-support {
  border-left: 2px solid var(--line);
  display: grid;
  gap: 5px;
  padding-left: 10px;
}
.local-article-paragraph-evidence-support a {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  text-decoration: none;
}
.local-article-paragraph-evidence-support strong {
  font-size: 0.82rem;
}
.local-article-paragraph-evidence-support p {
  color: var(--muted);
  font-size: 0.78rem;
  line-height: 1.4;
  margin: 0;
}
.local-article-paragraph-evidence-ref {
  border: 1px solid var(--line);
  color: var(--muted);
  display: inline-block;
  font-size: 0.7rem;
  margin: 0 4px 4px 0;
  padding: 4px 6px;
}
.local-article-reader {
  border: 1px solid var(--line);
  border-radius: 4px;
  padding: 14px;
  margin: 14px 0 16px;
}
.local-article-reader h4 {
  margin: 0 0 6px;
  font-size: 0.9rem;
}
.local-article-reader-meta {
  margin: 0 0 10px;
  color: var(--muted);
  font-size: 0.82rem;
}
.local-article-reader-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 8px;
}
.local-article-reader-list a {
  display: grid;
  grid-template-columns: 36px minmax(0, 1fr);
  gap: 10px;
  align-items: start;
  color: inherit;
  text-decoration: none;
}
.local-article-reader-list a:hover {
  color: var(--accent);
}
.local-article-reader-number {
  color: var(--muted);
  font-size: 0.72rem;
  letter-spacing: 0;
  text-transform: uppercase;
}
.local-article-reader-excerpt {
  min-width: 0;
}
.local-article-digest {
  border: 1px solid var(--line);
  border-radius: 4px;
  margin: 14px 0 16px;
  padding: 14px;
}
.local-article-digest-header {
  display: grid;
  gap: 6px;
  margin: 0 0 12px;
}
.local-article-digest-header h4,
.local-article-digest-header p {
  margin: 0;
}
.local-article-digest-header h4 {
  font-size: 0.9rem;
}
.local-article-digest-header p {
  color: var(--muted);
  font-size: 0.82rem;
}
.local-article-digest-grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.local-article-digest-card {
  border-top: 1px solid var(--line);
  padding-top: 10px;
}
.local-article-digest-card h4 {
  font-size: 0.76rem;
  letter-spacing: 0.08em;
  margin: 0 0 8px;
  text-transform: uppercase;
}
.local-article-digest-card p {
  line-height: 1.45;
  margin: 0 0 8px;
}
.local-article-digest-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.local-article-digest-link-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.local-article-digest-chip,
.local-article-digest-link-list a {
  border: 1px solid var(--line);
  color: var(--accent);
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 6px 8px;
  text-decoration: none;
}
.local-article-brief {
  border: 1px solid var(--line);
  display: grid;
  gap: 0;
  margin: 0 0 22px;
}
.local-article-brief-card {
  border-bottom: 1px solid var(--line);
  padding: 16px 18px;
}
.local-article-brief-card:last-child { border-bottom: 0; }
.local-article-brief-card h4 {
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  margin: 0 0 8px;
  text-transform: uppercase;
}
.local-article-brief-card p {
  color: var(--ink);
  line-height: 1.55;
  margin: 0;
}
.local-article-content-sections {
  display: grid;
  gap: 14px;
  margin: 0 0 24px;
}
.local-article-content-card {
  border-left: 2px solid var(--ink);
  padding: 0 0 0 16px;
}
.local-article-content-card h4 {
  font-size: 0.82rem;
  letter-spacing: 0.08em;
  margin: 0 0 8px;
  text-transform: uppercase;
}
.local-article-content-card p {
  color: var(--ink);
  line-height: 1.55;
  margin: 0 0 10px;
}
.local-article-content-items {
  display: grid;
  gap: 10px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.local-article-content-items li {
  border-top: 1px solid var(--line);
  padding-top: 10px;
}
.local-article-content-items strong {
  display: block;
  font-size: 0.82rem;
  margin-bottom: 4px;
}
.local-article-content-previews {
  display: grid;
  gap: 8px;
  list-style: none;
  margin: 10px 0 0;
  padding: 0;
}
.local-article-content-preview a {
  border: 1px solid var(--line);
  color: inherit;
  display: grid;
  gap: 4px;
  padding: 10px;
  text-decoration: none;
}
.local-article-content-preview a > span:first-child,
.local-article-content-preview a > span:nth-child(2) {
  color: var(--muted);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.local-article-content-preview a > span:last-child {
  line-height: 1.45;
}
.local-article-content-meta {
  color: var(--muted);
  font-size: 0.78rem;
  margin: 4px 0 0;
}
.local-article-body {
  display: grid;
  gap: 16px;
}
.local-article-body p {
  font-size: 1.05rem;
  line-height: 1.75;
  margin: 0;
}
.local-article-body p:target {
  background: var(--panel);
  outline: 1px solid var(--accent);
  outline-offset: 4px;
}
.detail-information-map {
  background: var(--panel);
  border: 1px solid var(--ink);
  margin: 28px 0;
  padding: 20px;
}
.detail-information-map-header {
  display: grid;
  gap: 6px;
  margin-bottom: 18px;
}
.detail-information-map-header p,
.detail-information-map-header h2 {
  margin: 0;
}
.detail-information-map-header p {
  color: var(--muted);
  font-size: 0.72rem;
  letter-spacing: 0;
  text-transform: uppercase;
}
.detail-information-map-header h2 {
  color: var(--ink);
  font-size: 1.2rem;
  letter-spacing: 0;
  margin-top: 0;
  text-transform: none;
}
.detail-information-map-grid {
  background: var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
}
.detail-information-map-card {
  background: var(--panel);
  display: grid;
  gap: 8px;
  min-width: 0;
  padding: 14px;
}
.detail-information-map-card h3,
.detail-information-map-card p {
  margin: 0;
  min-width: 0;
}
.detail-information-map-card h3 {
  color: var(--ink);
  font-size: 0.82rem;
  letter-spacing: 0;
  text-transform: uppercase;
}
.detail-information-map-card p {
  color: var(--muted);
  font-size: 0.9rem;
  overflow-wrap: anywhere;
}
.detail-information-map-card a {
  color: var(--accent);
  text-decoration: none;
}
.detail-signal-briefing {
  background: var(--ink);
  color: var(--panel);
  margin: 28px 0;
  padding: 22px;
}
.detail-signal-briefing-header {
  display: grid;
  gap: 6px;
  margin-bottom: 18px;
}
.detail-signal-briefing-header p,
.detail-signal-briefing-header h2 {
  margin: 0;
}
.detail-signal-briefing-header p {
  color: var(--chrome);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.detail-signal-briefing-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.8rem, 3.4vw, 3.4rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.98;
  text-transform: none;
}
.detail-signal-briefing-grid {
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.detail-signal-briefing-card {
  background: #15181d;
  border: 1px solid rgba(244, 246, 248, 0.18);
  display: grid;
  gap: 10px;
  min-width: 0;
  padding: 16px;
}
.detail-signal-briefing-card h3,
.detail-signal-briefing-card p {
  margin: 0;
}
.detail-signal-briefing-card h3 {
  color: var(--panel);
  font-size: 0.78rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.detail-signal-briefing-card p {
  color: var(--steel);
  line-height: 1.5;
  overflow-wrap: anywhere;
}
.detail-signal-briefing-meta {
  color: var(--chrome);
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.detail-signal-briefing-ref {
  border: 1px solid rgba(244, 246, 248, 0.26);
  color: var(--panel);
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 700;
  margin: 0 6px 6px 0;
  padding: 6px 8px;
}
.detail-signal-briefing-cues {
  border-top: 1px solid rgba(244, 246, 248, 0.22);
  margin-top: 18px;
  padding-top: 18px;
}
.detail-signal-briefing-cues h3 {
  color: var(--panel);
  font-size: 0.78rem;
  letter-spacing: 0.12em;
  margin: 0 0 12px;
  text-transform: uppercase;
}
.detail-signal-briefing-cue-grid {
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.detail-signal-briefing-cue {
  background: #f4f6f8;
  color: var(--ink);
  display: grid;
  gap: 8px;
  min-width: 0;
  padding: 14px;
}
.detail-signal-briefing-cue h4,
.detail-signal-briefing-cue p {
  margin: 0;
}
.detail-signal-briefing-cue h4 {
  font-size: 0.82rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.detail-signal-briefing-cue p {
  color: var(--muted);
  line-height: 1.45;
}
.detail-signal-briefing-cue a {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  text-decoration: none;
  text-transform: uppercase;
}
.detail-panel {
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  margin: 34px 0;
  padding: 22px 0;
}
.detail-panel h2 { margin-top: 8px; }
.section-return {
  margin: 0 0 22px;
}
.section-return a {
  color: var(--accent);
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-decoration: none;
  text-transform: uppercase;
}
.evidence-item {
  padding: 14px 0;
  border-top: 1px solid var(--line);
}
.evidence-trail {
  display: grid;
  gap: 12px;
  margin-top: 24px;
}
.evidence-item--safe,
.evidence-item--retained {
  background: var(--panel);
  border: 1px solid var(--line);
  border-left: 3px solid var(--accent);
  padding: 14px;
}
.evidence-item--retained {
  border-left-color: var(--muted);
  color: var(--muted);
}
.evidence-label,
.evidence-retained-label {
  color: var(--accent);
  display: block;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  margin-bottom: 6px;
  text-transform: uppercase;
}
.evidence-retained-label {
  color: var(--muted);
}
.evidence-retained-title {
  display: block;
}
.continue-reading {
  border-top: 1px solid var(--ink);
  margin-top: 40px;
  padding-top: 28px;
}
.continue-reading-header {
  display: grid;
  gap: 8px;
  margin-bottom: 18px;
}
.continue-reading-header h2,
.continue-reading-header p {
  margin: 0;
}
.continue-reading-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 4.2vw, 4.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.94;
}
.continue-reading-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.continue-reading-card {
  background: var(--panel);
  min-width: 0;
}
.continue-reading-card a {
  color: var(--ink);
  display: grid;
  gap: 12px;
  min-height: 220px;
  padding: 18px;
  text-decoration: none;
}
.continue-reading-section {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  margin: 0;
  text-transform: uppercase;
}
.continue-reading-source {
  color: var(--muted);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  margin: 0;
  text-transform: uppercase;
}
.continue-reading-card h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.45rem, 2.4vw, 2.4rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.98;
  margin: 0;
}
.continue-reading-excerpt {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
}
.continue-reading-excerpt span {
  color: var(--ink);
}
[data-lang="zh"] { display: none; }
body.lang-zh [data-lang="en"] { display: none; }
body.lang-zh [data-lang="zh"] { display: inline; }
body.lang-zh p [data-lang="zh"] { display: inline; }
@media (min-width: 700px) {
  .daily-local-article-capsules-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .daily-local-article-reading-brief-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .daily-local-source-desk-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .daily-local-coverage-map-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .daily-local-theme-summary-strip-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 760px) {
  .site-header { min-height: 46vh; padding: 28px 20px; }
  .site-header-inner { grid-template-columns: 1fr; }
  .edition-status { grid-template-columns: 1fr; }
  .edition-status > div {
    border-right: 0;
    border-bottom: 1px solid var(--line);
    padding: 16px 20px;
  }
  .edition-status > div:last-child { border-bottom: 0; }
  main { padding: 24px 20px 56px; }
  .edition-rail-grid { grid-template-columns: 1fr; }
  .edition-brief-metrics { grid-template-columns: 1fr 1fr; }
  .signal-synthesis-header { grid-template-columns: 1fr; }
  .signal-synthesis-grid { grid-template-columns: 1fr; }
  .daily-edit-header { grid-template-columns: 1fr; }
  .daily-edit-grid { grid-template-columns: 1fr; }
  .daily-local-intelligence-header { grid-template-columns: 1fr; }
  .daily-local-intelligence-grid { grid-template-columns: 1fr; }
  .daily-local-key-signals-digest-header { grid-template-columns: 1fr; }
  .daily-local-key-signals-digest-grid { grid-template-columns: 1fr; }
  .daily-local-signal-momentum-header { grid-template-columns: 1fr; }
  .daily-local-signal-momentum-grid { grid-template-columns: 1fr; }
  .daily-local-heat-signals-header { grid-template-columns: 1fr; }
  .daily-local-heat-signals-grid { grid-template-columns: 1fr; }
  .daily-local-article-capsules-header { grid-template-columns: 1fr; }
  .daily-local-article-reading-brief-header { grid-template-columns: 1fr; }
  .daily-local-article-reading-brief-grid { grid-template-columns: 1fr; }
  .daily-local-source-desk-header { grid-template-columns: 1fr; }
  .daily-local-source-desk-grid { grid-template-columns: 1fr; }
  .daily-local-coverage-map-header { grid-template-columns: 1fr; }
  .daily-local-coverage-map-grid { grid-template-columns: 1fr; }
  .daily-local-theme-summary-strip-header { grid-template-columns: 1fr; }
  .daily-local-theme-summary-strip-grid { grid-template-columns: 1fr; }
  .daily-local-news-timeline-header { grid-template-columns: 1fr; }
  .daily-local-news-timeline-list { grid-template-columns: 1fr; }
  .daily-local-article-intelligence-brief-header { grid-template-columns: 1fr; }
  .daily-local-article-intelligence-brief-lanes { grid-template-columns: 1fr; }
  .daily-local-article-intelligence-brief-grid { grid-template-columns: 1fr; }
  .daily-local-synthesis-brief-header { grid-template-columns: 1fr; }
  .daily-local-synthesis-brief-grid { grid-template-columns: 1fr; }
  .daily-local-saved-text-takeaways-header { grid-template-columns: 1fr; }
  .daily-local-saved-text-takeaways-grid { grid-template-columns: 1fr; }
  .daily-local-brand-product-people-signal-digest-header { grid-template-columns: 1fr; }
  .daily-local-brand-product-people-signal-digest-grid { grid-template-columns: 1fr; }
  .daily-local-saved-article-organizer-header { grid-template-columns: 1fr; }
  .daily-local-saved-article-organizer-lanes { grid-template-columns: 1fr; }
  .daily-local-reading-itinerary-header { grid-template-columns: 1fr; }
  .daily-local-reading-itinerary-grid { grid-template-columns: 1fr; }
  .local-article-content-segment-deck-header { grid-template-columns: 1fr; }
  .local-article-content-segment-deck-grid { grid-template-columns: 1fr; }
  .local-article-body-organizer-header { grid-template-columns: 1fr; }
  .local-article-body-organizer-sections { grid-template-columns: 1fr; }
  .local-article-intelligence-brief-header { grid-template-columns: 1fr; }
  .local-article-intelligence-brief-lanes { grid-template-columns: 1fr; }
  .local-article-synthesis-brief-header { grid-template-columns: 1fr; }
  .local-article-synthesis-brief-grid { grid-template-columns: 1fr; }
  .local-article-body-section-marker { margin: 18px 0 10px; }
  .local-article-body-section-marker-header { align-items: flex-start; flex-direction: column; }
  .saved-article-coverage-header { grid-template-columns: 1fr; }
  .saved-article-coverage-grid { grid-template-columns: 1fr; }
  .saved-article-library-entry-header { grid-template-columns: 1fr; }
  .saved-article-library-source-grid { grid-template-columns: 1fr; }
  .saved-article-briefs-header { grid-template-columns: 1fr; }
  .saved-article-briefs-grid { grid-template-columns: 1fr; }
  .saved-article-content-organization-header { grid-template-columns: 1fr; }
  .saved-article-content-organization-grid { grid-template-columns: 1fr; }
  .saved-article-filing-inbox-header { grid-template-columns: 1fr; }
  .saved-article-filing-inbox-list { grid-template-columns: 1fr; }
  .saved-article-filing-inbox-item { grid-template-columns: 1fr; }
  .saved-article-evidence-board-header { grid-template-columns: 1fr; }
  .saved-article-evidence-board-cards { grid-template-columns: 1fr; }
  .editorial-brief-header { grid-template-columns: 1fr; }
  .editorial-brief-grid { grid-template-columns: 1fr; }
  .local-article-digest-grid { grid-template-columns: 1fr; }
  .briefing-topics-header { grid-template-columns: 1fr; }
  .briefing-topic-grid { grid-template-columns: 1fr; }
  .briefing-path-header { grid-template-columns: 1fr; }
  .briefing-path-grid { grid-template-columns: 1fr; }
  .lead-story-grid { grid-template-columns: 1fr; gap: 18px; }
  .section-block { grid-template-columns: 1fr; gap: 18px; }
  .story-grid { grid-template-columns: 1fr; }
  .detail-header { padding: 18px 20px; }
  .detail-signal-briefing-grid { grid-template-columns: 1fr; }
  .detail-signal-briefing-cue-grid { grid-template-columns: 1fr; }
  .continue-reading-grid { grid-template-columns: 1fr; }
  .local-article-paragraph-evidence-grid { grid-template-columns: 1fr; }
}
"""


def _render_edition_nav(edition: RowOneEdition) -> str:
    rows = "\n".join(_render_edition_nav_item(edition, section) for section in edition.sections)
    return f"""<nav class="edition-nav" aria-label="Edition contents">
  <p class="story-section">
    <span data-lang="en">Edition Contents</span>
    <span data-lang="zh">今日目录</span>
  </p>
  <div class="edition-rail">
    <div class="edition-rail-grid">{rows}</div>
  </div>
</nav>"""


def _render_edition_status(
    edition: RowOneEdition,
    readiness: RowOneReadiness | None = None,
) -> str:
    if readiness is None:
        readiness = build_row_one_readiness(edition)
    status_metrics = "\n  ".join(
        (
            _render_status_metric(
                "Generated",
                "生成时间",
                readiness.generated_at,
                readiness.generated_at,
            ),
            _render_status_metric(
                "Edition date",
                "刊期",
                readiness.edition_date,
                readiness.edition_date,
            ),
            _render_status_metric(
                "Stories",
                "故事",
                str(readiness.story_count),
                f"{readiness.story_count} 条",
            ),
            _render_status_metric(
                "Evidence links",
                "证据链接",
                str(readiness.safe_evidence_count),
                f"{readiness.safe_evidence_count} 条",
            ),
            _render_status_metric(
                "Empty sections",
                "空栏目",
                readiness.empty_sections.en,
                readiness.empty_sections.zh,
            ),
        )
    )
    return f"""<section class="edition-status" aria-label="Latest edition status">
  <div>
    <p class="story-section">
      <span data-lang="en">Latest Edition</span>
      <span data-lang="zh">今日状态</span>
    </p>
    <strong>
      <span data-lang="en">{_esc(readiness.readiness.en)}</span>
      <span data-lang="zh">{_esc(readiness.readiness.zh)}</span>
    </strong>
  </div>
  {status_metrics}
</section>"""


def _render_status_metric(label_en: str, label_zh: str, value_en: str, value_zh: str) -> str:
    return f"""<div class="edition-status-metric">
    <span class="edition-status-label">
      <span data-lang="en">{_esc(label_en)}</span>
      <span data-lang="zh">{_esc(label_zh)}</span>
    </span>
    <strong>
      <span data-lang="en">{_esc(value_en)}</span>
      <span data-lang="zh">{_esc(value_zh)}</span>
    </strong>
  </div>"""


def _render_edition_brief(
    app_payload: dict[str, object] | None,
    *,
    has_topics: bool,
    has_path: bool,
) -> str:
    brief = _app_payload_edition_brief(app_payload)
    if not brief:
        return ""
    title = _localized_from_payload(brief.get("title"))
    dek = _localized_from_payload(brief.get("dek"))
    metrics = _render_edition_brief_metrics(brief.get("metrics"))
    points = _render_edition_brief_points(brief.get("summary_points"))
    links = _render_edition_brief_links(
        brief.get("links"),
        has_topics=has_topics,
        has_path=has_path,
    )
    lead_headline = _esc(brief.get("lead_story_headline") or "")
    lead = f'<p class="edition-brief-lead">{lead_headline}</p>' if lead_headline else ""
    section_label = '<span data-lang="en">Daily Overview</span><span data-lang="zh">每日总览</span>'
    title_html = (
        f'<span data-lang="en">{_esc(title.en)}</span><span data-lang="zh">{_esc(title.zh)}</span>'
    )
    dek_html = (
        f'<span data-lang="en">{_esc(dek.en)}</span><span data-lang="zh">{_esc(dek.zh)}</span>'
    )
    return f"""<section class="edition-brief" aria-label="Edition brief">
  <div class="edition-brief-header">
    <p class="story-section">{section_label}</p>
    <h2>{title_html}</h2>
    <p>{dek_html}</p>
    {lead}
  </div>
  {metrics}
  {points}
  {links}
</section>"""


def _app_payload_edition_brief(app_payload: dict[str, object] | None) -> dict[str, object] | None:
    if app_payload is None:
        return None
    brief = app_payload.get("edition_brief")
    return brief if isinstance(brief, dict) else None


def _localized_from_payload(value: object) -> LocalizedText:
    if isinstance(value, dict):
        zh = value.get("zh")
        en = value.get("en")
        if isinstance(zh, str) and isinstance(en, str):
            return LocalizedText(zh=zh, en=en)
    return LocalizedText(zh="", en="")


def _render_edition_brief_metrics(value: object) -> str:
    if not isinstance(value, list):
        return ""
    cards = []
    for metric in value:
        if not isinstance(metric, dict):
            continue
        label = _localized_from_payload(metric.get("label"))
        cards.append(
            f"""<div class="edition-brief-metric">
      <strong>{_esc(metric.get("value", 0))}</strong>
      <span data-lang="en">{_esc(label.en)}</span>
      <span data-lang="zh">{_esc(label.zh)}</span>
    </div>"""
        )
    return f'<div class="edition-brief-metrics">{"".join(cards)}</div>' if cards else ""


def _render_edition_brief_points(value: object) -> str:
    if not isinstance(value, list):
        return ""
    items = []
    for point in value:
        text = _localized_from_payload(point)
        if text.en or text.zh:
            items.append(
                f'<li><span data-lang="en">{_esc(text.en)}</span>'
                f'<span data-lang="zh">{_esc(text.zh)}</span></li>'
            )
    return f'<ul class="edition-brief-points">{"".join(items)}</ul>' if items else ""


def _render_edition_brief_links(
    value: object,
    *,
    has_topics: bool,
    has_path: bool,
) -> str:
    if not isinstance(value, list):
        return ""
    links = []
    for link in value:
        if not isinstance(link, dict):
            continue
        href = _safe_edition_brief_href(link.get("href"), has_topics=has_topics, has_path=has_path)
        label = _localized_from_payload(link.get("label"))
        if href is None:
            if label.en or label.zh:
                links.append(
                    f'<span><span data-lang="en">{_esc(label.en)}</span>'
                    f'<span data-lang="zh">{_esc(label.zh)}</span></span>'
                )
            continue
        links.append(
            f'<a href="{_esc(href)}"><span data-lang="en">{_esc(label.en)}</span>'
            f'<span data-lang="zh">{_esc(label.zh)}</span></a>'
        )
    return f'<div class="edition-brief-links">{"".join(links)}</div>' if links else ""


def _safe_edition_brief_href(
    href: object,
    *,
    has_topics: bool,
    has_path: bool,
) -> str | None:
    if not isinstance(href, str):
        return None
    if href == "#briefing-topics":
        return href if has_topics else None
    if href == "#briefing-path":
        return href if has_path else None
    if _validated_detail_relative_path(href) is not None:
        return href
    return None


def _render_signal_synthesis(app_payload: dict[str, object] | None) -> str:
    synthesis = _app_payload_signal_synthesis(app_payload)
    if synthesis is None:
        return ""
    groups = _signal_synthesis_groups_from_payload(synthesis)
    rendered_groups = [_render_signal_synthesis_group(group) for group in groups]
    rendered_groups = [group for group in rendered_groups if group]
    if not rendered_groups:
        return ""
    title = _localized_from_payload(synthesis.get("title"))
    dek = _localized_from_payload(synthesis.get("dek"))
    boundaries = _localized_from_payload(synthesis.get("boundaries"))
    return f"""<section class="signal-synthesis" aria-label="Signal synthesis">
  <div class="signal-synthesis-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Signal Synthesis</span>
        <span data-lang="zh">今日信号整理</span>
      </p>
      <h2>
        <span data-lang="en">{_esc(title.en)}</span>
        <span data-lang="zh">{_esc(title.zh)}</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">{_esc(dek.en)}</span>
      <span data-lang="zh">{_esc(dek.zh)}</span>
    </p>
  </div>
  <p class="signal-synthesis-boundary">
    <span data-lang="en">{_esc(boundaries.en)}</span>
    <span data-lang="zh">{_esc(boundaries.zh)}</span>
  </p>
  <div class="signal-synthesis-grid">{"".join(rendered_groups)}</div>
</section>"""


def _app_payload_signal_synthesis(
    app_payload: dict[str, object] | None,
) -> dict[str, object] | None:
    if app_payload is None:
        return None
    synthesis = app_payload.get("signal_synthesis")
    return synthesis if isinstance(synthesis, dict) else None


def _signal_synthesis_groups_from_payload(
    synthesis: dict[str, object],
) -> list[dict[str, object]]:
    groups = synthesis.get("groups")
    if not isinstance(groups, list):
        return []
    return [group for group in groups if isinstance(group, dict)]


def _render_signal_synthesis_group(group: dict[str, object]) -> str:
    label = _localized_from_payload(group.get("label"))
    signals = group.get("signals")
    if not isinstance(signals, list):
        return ""
    cards = [
        _render_signal_synthesis_card(signal) for signal in signals[:3] if isinstance(signal, dict)
    ]
    cards = [card for card in cards if card]
    if not cards:
        return ""
    return f"""<article class="signal-synthesis-group">
  <p class="signal-synthesis-group-title">
    <span data-lang="en">{_esc(label.en)}</span>
    <span data-lang="zh">{_esc(label.zh)}</span>
  </p>
  {"".join(cards)}
</article>"""


def _render_signal_synthesis_card(signal: dict[str, object]) -> str:
    name = str(signal.get("name", "")).strip()
    if not name:
        return ""
    summary = _localized_from_payload(signal.get("summary"))
    href = _safe_signal_detail_href(signal.get("lead_story_href"))
    story_count = (
        int(signal.get("story_count", 0)) if isinstance(signal.get("story_count"), int) else 0
    )
    evidence_count = (
        int(signal.get("evidence_count", 0)) if isinstance(signal.get("evidence_count"), int) else 0
    )
    heat_delta = (
        int(signal.get("max_heat_delta", 0)) if isinstance(signal.get("max_heat_delta"), int) else 0
    )
    label = str(signal.get("label", "")).strip()
    meta = _signal_synthesis_meta_label(
        label=label,
        story_count=story_count,
        evidence_count=evidence_count,
        heat_delta=heat_delta,
    )
    body = f"""<h3>{_esc(name)}</h3>
  <p>
    <span data-lang="en">{_esc(summary.en)}</span>
    <span data-lang="zh">{_esc(summary.zh)}</span>
  </p>
  <div class="signal-synthesis-meta">{meta}</div>"""
    if href is None:
        return f'<div class="signal-synthesis-card">{body}</div>'
    return f'<a class="signal-synthesis-card" href="{_esc(href)}">{body}</a>'


def _render_daily_edit(app_payload: dict[str, object] | None) -> str:
    cards = _daily_edit_cards(app_payload)
    if not cards:
        return ""
    rendered_cards = "\n".join(_render_daily_edit_card(card) for card in cards)
    return f"""<section class="daily-edit" aria-label="Daily edit">
  <div class="daily-edit-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Daily Edit</span>
        <span data-lang="zh">今日编辑简报</span>
      </p>
      <h2>
        <span data-lang="en">What matters today</span>
        <span data-lang="zh">今天值得先看什么</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">A scan-first edit from existing ROW ONE signals.</span>
      <span data-lang="zh">基于现有 ROW ONE 信号整理的快速编辑简报。</span>
    </p>
  </div>
  <div class="daily-edit-grid">
{rendered_cards}
  </div>
</section>"""


def _daily_edit_cards(app_payload: dict[str, object] | None) -> list[dict[str, object]]:
    if app_payload is None:
        return []
    cards = [
        _daily_edit_what_to_know(app_payload),
        _daily_edit_signals_to_watch(app_payload),
        _daily_edit_read_next(app_payload),
        _daily_edit_evidence_note(app_payload),
    ]
    return [card for card in cards if card is not None][:DAILY_EDIT_MAX_CARDS]


def _daily_edit_what_to_know(app_payload: dict[str, object]) -> dict[str, object] | None:
    brief = _app_payload_edition_brief(app_payload)
    if brief is None:
        return None
    point = _first_localized_payload(brief.get("summary_points"))
    lead_headline = str(brief.get("lead_story_headline") or "").strip()
    if not (point.en or point.zh or lead_headline):
        return None
    if lead_headline and (point.en or point.zh):
        point = LocalizedText(
            en=f"{lead_headline}: {point.en}" if point.en else lead_headline,
            zh=f"{lead_headline}: {point.zh}" if point.zh else lead_headline,
        )
    elif not point.en and lead_headline:
        point = LocalizedText(en=lead_headline, zh=lead_headline)
    meta = []
    lead_story_id = str(brief.get("lead_story_id") or "").strip()
    if lead_story_id:
        meta.append(LocalizedText(en="Read first", zh="先读"))
    return _daily_edit_card(
        title=LocalizedText(en="What To Know", zh="今日重点"),
        body=point,
        href=_safe_daily_edit_href(brief.get("lead_story_href")),
        meta=meta,
    )


def _daily_edit_signals_to_watch(app_payload: dict[str, object]) -> dict[str, object] | None:
    synthesis = _app_payload_signal_synthesis(app_payload)
    if synthesis is not None:
        for signal in _daily_edit_signal_candidates(synthesis):
            card = _daily_edit_signal_card(signal)
            if card is not None:
                return card
    return _daily_edit_topic_fallback_card(app_payload) or _daily_edit_read_first_signal_card(
        app_payload
    )


def _daily_edit_signal_candidates(synthesis: dict[str, object]) -> list[dict[str, object]]:
    candidates: list[dict[str, object]] = []
    for group in _signal_synthesis_groups_from_payload(synthesis):
        signals = group.get("signals")
        if not isinstance(signals, list):
            continue
        for signal in signals:
            if isinstance(signal, dict):
                candidates.append(signal)
                if len(candidates) >= DAILY_EDIT_MAX_SIGNALS:
                    return candidates
    return candidates


def _daily_edit_signal_card(signal: dict[str, object]) -> dict[str, object] | None:
    name = str(signal.get("name") or "").strip()
    if not name:
        return None
    summary = _localized_from_payload(signal.get("summary"))
    if not (summary.en or summary.zh):
        summary = LocalizedText(en=name, zh=name)
    meta = [
        _daily_edit_count_meta(
            _int_or_zero(signal.get("story_count")),
            "story",
            "stories",
            "条故事",
        ),
        _daily_edit_count_meta(
            _int_or_zero(signal.get("evidence_count")),
            "evidence link",
            "evidence links",
            "条证据链接",
        ),
    ]
    heat_delta = _int_or_zero(signal.get("max_heat_delta"))
    if heat_delta > 0:
        meta.append(LocalizedText(en=f"+{heat_delta} heat", zh=f"+{heat_delta} 热度"))
    label = str(signal.get("label") or "").strip()
    if label:
        meta.insert(0, LocalizedText(en=label, zh=label))
    return _daily_edit_card(
        title=LocalizedText(en="Signals To Watch", zh="值得关注"),
        body=LocalizedText(
            en=f"{name}: {summary.en}" if summary.en else name,
            zh=f"{name}: {summary.zh}" if summary.zh else name,
        ),
        href=_safe_daily_edit_href(signal.get("lead_story_href")),
        meta=meta,
    )


def _daily_edit_topic_fallback_card(app_payload: dict[str, object]) -> dict[str, object] | None:
    for topic in _app_payload_briefing_topics(app_payload):
        title = _localized_topic_field(topic, "title")
        lead_story = _topic_lead_story(topic) or _topic_nested_lead_story(topic)
        headline = _topic_localized_card_text(lead_story, "headline")
        takeaway = _topic_localized_card_text(lead_story, "editorial_takeaway")
        body = takeaway if takeaway.en or takeaway.zh else headline
        if not (title.en or title.zh or body.en or body.zh):
            continue
        meta = [
            _daily_edit_count_meta(
                _int_or_zero(topic.get("story_count")),
                "story",
                "stories",
                "条故事",
            ),
            _daily_edit_count_meta(
                _int_or_zero(topic.get("evidence_count")),
                "evidence link",
                "evidence links",
                "条证据链接",
            ),
        ]
        heat_delta = _int_or_zero(topic.get("positive_heat_delta_sum"))
        if heat_delta > 0:
            meta.append(LocalizedText(en=f"+{heat_delta} heat", zh=f"+{heat_delta} 热度"))
        if body.en or body.zh:
            body = LocalizedText(
                en=f"{title.en}: {body.en}" if title.en and body.en else title.en or body.en,
                zh=f"{title.zh}: {body.zh}" if title.zh and body.zh else title.zh or body.zh,
            )
        else:
            body = title
        href = _safe_daily_edit_href(lead_story.get("detail_href")) if lead_story else None
        return _daily_edit_card(
            title=LocalizedText(en="Signals To Watch", zh="值得关注"),
            body=body,
            href=href,
            meta=meta,
        )
    return None


def _daily_edit_read_first_signal_card(app_payload: dict[str, object]) -> dict[str, object] | None:
    card = _daily_edit_read_first_card(app_payload)
    if card is None:
        return None
    headline = _topic_localized_card_text(card, "headline")
    takeaway = _topic_localized_card_text(card, "editorial_takeaway")
    body = takeaway if takeaway.en or takeaway.zh else headline
    if not (headline.en or headline.zh or body.en or body.zh):
        return None
    if headline.en or headline.zh:
        body = LocalizedText(
            en=(
                f"{headline.en}: {body.en}"
                if headline.en and body.en and body.en != headline.en
                else headline.en or body.en
            ),
            zh=(
                f"{headline.zh}: {body.zh}"
                if headline.zh and body.zh and body.zh != headline.zh
                else headline.zh or body.zh
            ),
        )
    return _daily_edit_card(
        title=LocalizedText(en="Signals To Watch", zh="值得关注"),
        body=body,
        href=_safe_daily_edit_href(card.get("detail_href")),
        meta=[
            _daily_edit_count_meta(
                _int_or_zero(card.get("evidence_count")),
                "evidence link",
                "evidence links",
                "条证据链接",
            )
        ],
    )


def _daily_edit_read_first_card(app_payload: dict[str, object]) -> dict[str, object] | None:
    blocks = _app_payload_digest_blocks(app_payload)
    read_first_block = next((block for block in blocks if block.get("key") == "read_first"), None)
    if read_first_block is None:
        return None
    cards = _block_cards(read_first_block, set())
    return cards[0] if cards else None


def _daily_edit_read_next(app_payload: dict[str, object]) -> dict[str, object] | None:
    blocks = _app_payload_digest_blocks(app_payload)
    excluded_story_ids = _read_first_story_ids(blocks)
    for key in ("key_takeaways", "signals_to_watch"):
        for block in blocks:
            if block.get("key") != key:
                continue
            for card in _block_cards(block, excluded_story_ids)[:DAILY_EDIT_MAX_PATH_ITEMS]:
                headline = _topic_localized_card_text(card, "headline")
                takeaway = _topic_localized_card_text(card, "editorial_takeaway")
                body = takeaway if takeaway.en or takeaway.zh else headline
                if not (headline.en or headline.zh or body.en or body.zh):
                    continue
                if headline.en or headline.zh:
                    body = LocalizedText(
                        en=(
                            f"{headline.en}: {body.en}"
                            if headline.en and body.en and body.en != headline.en
                            else headline.en or body.en
                        ),
                        zh=(
                            f"{headline.zh}: {body.zh}"
                            if headline.zh and body.zh and body.zh != headline.zh
                            else headline.zh or body.zh
                        ),
                    )
                return _daily_edit_card(
                    title=LocalizedText(en="Read Next", zh="阅读路径"),
                    body=body,
                    href=_safe_daily_edit_href(card.get("detail_href")),
                    meta=[LocalizedText(en="Local reading path", zh="本地阅读路径")],
                )
    card = _daily_edit_read_first_card(app_payload)
    if card is None:
        return None
    headline = _topic_localized_card_text(card, "headline")
    takeaway = _topic_localized_card_text(card, "editorial_takeaway")
    body = takeaway if takeaway.en or takeaway.zh else headline
    if not (headline.en or headline.zh or body.en or body.zh):
        return None
    if headline.en or headline.zh:
        body = LocalizedText(
            en=(
                f"{headline.en}: {body.en}"
                if headline.en and body.en and body.en != headline.en
                else headline.en or body.en
            ),
            zh=(
                f"{headline.zh}: {body.zh}"
                if headline.zh and body.zh and body.zh != headline.zh
                else headline.zh or body.zh
            ),
        )
    return _daily_edit_card(
        title=LocalizedText(en="Read Next", zh="阅读路径"),
        body=body,
        href=_safe_daily_edit_href(card.get("detail_href")),
        meta=[LocalizedText(en="Read first fallback", zh="先读兜底")],
    )


def _topic_nested_lead_story(topic: dict[str, object]) -> dict[str, object] | None:
    lead_story = topic.get("lead_story")
    return lead_story if isinstance(lead_story, dict) else None


def _daily_edit_evidence_note(app_payload: dict[str, object]) -> dict[str, object] | None:
    evidence_count = _daily_edit_evidence_count(app_payload)
    synthesis = _app_payload_signal_synthesis(app_payload)
    boundaries = (
        _localized_from_payload(synthesis.get("boundaries")) if synthesis is not None else None
    )
    if evidence_count == 0 and (boundaries is None or not (boundaries.en or boundaries.zh)):
        return None
    evidence_en = (
        "1 existing ROW ONE evidence link"
        if evidence_count == 1
        else f"{evidence_count} existing ROW ONE evidence links"
    )
    evidence_zh = f"{evidence_count} 条现有 ROW ONE 证据链接"
    boundary_en = boundaries.en if boundaries is not None and boundaries.en else evidence_en
    boundary_zh = boundaries.zh if boundaries is not None and boundaries.zh else evidence_zh
    return _daily_edit_card(
        title=LocalizedText(en="Evidence Note", zh="线索边界"),
        body=LocalizedText(
            en=(
                f"Based on {evidence_en}; {boundary_en}; "
                "review the underlying stories before acting."
            ),
            zh=f"基于{evidence_zh}；{boundary_zh}；行动前请复核底层故事。",
        ),
        href="#main-content",
        meta=[LocalizedText(en="Existing evidence only", zh="仅限现有证据")],
    )


def _daily_edit_evidence_count(app_payload: dict[str, object]) -> int:
    daily_digest = app_payload.get("daily_digest")
    if isinstance(daily_digest, dict):
        count = daily_digest.get("evidence_count")
        if isinstance(count, int):
            return count
    brief = _app_payload_edition_brief(app_payload)
    if brief is None:
        return 0
    metrics = brief.get("metrics")
    if not isinstance(metrics, list):
        return 0
    for metric in metrics:
        if not isinstance(metric, dict) or metric.get("key") != "evidence":
            continue
        return _int_or_zero(metric.get("value"))
    return 0


def _first_localized_payload(value: object) -> LocalizedText:
    if not isinstance(value, list):
        return LocalizedText(zh="", en="")
    for item in value:
        text = _localized_from_payload(item)
        if text.en or text.zh:
            return text
    return LocalizedText(zh="", en="")


def _daily_edit_count_meta(
    count: int,
    singular: str,
    plural: str,
    zh_suffix: str,
) -> LocalizedText:
    label = singular if count == 1 else plural
    return LocalizedText(en=f"{count} {label}", zh=f"{count} {zh_suffix}")


def _daily_edit_card(
    *,
    title: LocalizedText,
    body: LocalizedText,
    href: str | None,
    meta: list[LocalizedText],
) -> dict[str, object]:
    return {"title": title, "body": body, "href": href, "meta": meta}


def _render_daily_edit_card(card: dict[str, object]) -> str:
    title = card["title"]
    body = card["body"]
    if not isinstance(title, LocalizedText) or not isinstance(body, LocalizedText):
        return ""
    href = _safe_daily_edit_href(card.get("href")) or "#main-content"
    meta = card.get("meta")
    rendered_meta = ""
    if isinstance(meta, list):
        parts = [
            f'<span data-lang="en">{_esc(item.en)}</span>'
            f'<span data-lang="zh">{_esc(item.zh)}</span>'
            for item in meta
            if isinstance(item, LocalizedText) and (item.en or item.zh)
        ]
        if parts:
            rendered_meta = f'    <div class="daily-edit-card-meta">{"".join(parts)}</div>\n'
    return f"""    <a class="daily-edit-card" href="{_esc(href)}">
      <h3>
        <span data-lang="en">{_esc(title.en)}</span>
        <span data-lang="zh">{_esc(title.zh)}</span>
      </h3>
      <p>
        <span data-lang="en">{_esc(body.en)}</span>
        <span data-lang="zh">{_esc(body.zh)}</span>
      </p>
{rendered_meta}      <span class="daily-edit-link">
        <span data-lang="en">Open local context</span>
        <span data-lang="zh">打开本地上下文</span>
      </span>
    </a>"""


def _safe_daily_edit_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    if href in {"#main-content", "#briefing-topics", "#briefing-path"}:
        return href
    if _validated_detail_relative_path(href) is not None:
        return href
    return None


def _render_daily_local_intelligence(
    sections: Sequence[RowOneDailyLocalIntelligenceSection] | None,
) -> str:
    if not sections:
        return ""
    rendered_sections = [
        _render_daily_local_intelligence_section(section) for section in sections if section.items
    ]
    rendered_sections = [section for section in rendered_sections if section]
    if not rendered_sections:
        return ""
    return f"""<section class="daily-local-intelligence" aria-label="Daily local intelligence">
  <div class="daily-local-intelligence-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Daily Local Intelligence</span>
        <span data-lang="zh">每日本地情报</span>
      </p>
      <h2>
        <span data-lang="en">Daily Local Intelligence</span>
        <span data-lang="zh">每日本地情报</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">Source-backed fashion signals from saved local article bodies.</span>
      <span data-lang="zh">来自本地保存正文的时尚信号整理。</span>
    </p>
  </div>
  <div class="daily-local-intelligence-grid">{"".join(rendered_sections)}</div>
</section>"""


def _render_saved_article_coverage(coverage: RowOneSavedArticleCoverage | None) -> str:
    if coverage is None:
        return ""
    metrics = _render_saved_article_coverage_metrics(coverage)
    sources = _render_saved_article_coverage_sources(coverage)
    cards = "\n".join(_render_saved_article_coverage_card(item) for item in coverage.items)
    return f"""<section class="saved-article-coverage" aria-label="Saved article coverage">
  <div class="saved-article-coverage-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Saved Article Coverage</span>
        <span data-lang="zh">保存正文覆盖</span>
      </p>
      <h2>
        <span data-lang="en">Saved Article Coverage</span>
        <span data-lang="zh">保存正文覆盖</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">The local source set behind today's saved article pages.</span>
      <span data-lang="zh">今日保存正文页面背后的本地来源集合。</span>
    </p>
  </div>
  {metrics}
  {sources}
  <div class="saved-article-coverage-grid">{cards}</div>
</section>"""


def _render_saved_article_coverage_metrics(coverage: RowOneSavedArticleCoverage) -> str:
    metrics = [
        _render_saved_article_coverage_metric(
            _count_label(coverage.article_count, "saved article", "saved articles"),
            f"{coverage.article_count} 篇保存文章",
        ),
        _render_saved_article_coverage_metric(
            _count_label(
                coverage.saved_paragraph_count,
                "saved paragraph",
                "saved paragraphs",
            ),
            f"{coverage.saved_paragraph_count} 个保存段落",
        ),
        _render_saved_article_coverage_metric(
            _count_label(
                coverage.organized_section_count,
                "organized section",
                "organized sections",
            ),
            f"{coverage.organized_section_count} 个整理栏目",
        ),
        _render_saved_article_coverage_metric(
            _count_label(coverage.source_count, "source", "sources"),
            f"{coverage.source_count} 个来源",
        ),
    ]
    return '  <ul class="saved-article-coverage-metrics">\n' + "\n".join(metrics) + "\n  </ul>"


def _render_saved_article_coverage_metric(label_en: str, label_zh: str) -> str:
    return (
        "    <li>"
        f'<span data-lang="en">{_esc(label_en)}</span>'
        f'<span data-lang="zh">{_esc(label_zh)}</span>'
        "</li>"
    )


def _render_saved_article_coverage_sources(coverage: RowOneSavedArticleCoverage) -> str:
    if not coverage.sources:
        return ""
    source_items = []
    for source in coverage.sources:
        article_count_en = _count_label(source.article_count, "article", "articles")
        article_count_zh = f"{source.article_count} 篇文章"
        source_items.append(
            "    <li>"
            f'<span class="saved-article-coverage-source-name">{_esc(source.name)}</span>'
            f'<span data-lang="en">{_esc(article_count_en)}</span>'
            f'<span data-lang="zh">{_esc(article_count_zh)}</span>'
            "</li>"
        )
    sources = "\n".join(source_items)
    return (
        '  <ul class="saved-article-coverage-sources" aria-label="Saved article sources">\n'
        + sources
        + "\n  </ul>"
    )


def _render_saved_article_coverage_card(item: RowOneSavedArticleCoverageItem) -> str:
    href = _safe_saved_article_coverage_href(item.detail_path)
    if href is None:
        return ""
    paragraph_count_en = _count_label(
        item.saved_paragraph_count,
        "saved paragraph",
        "saved paragraphs",
    )
    paragraph_count_zh = f"{item.saved_paragraph_count} 个保存段落"
    section_count_en = _count_label(
        item.organized_section_count,
        "organized section",
        "organized sections",
    )
    section_count_zh = f"{item.organized_section_count} 个整理栏目"
    return f"""    <a class="saved-article-coverage-card" href="{_esc(href)}">
      <strong>
        <span data-lang="en">{_esc(item.title.en)}</span>
        <span data-lang="zh">{_esc(item.title.zh)}</span>
      </strong>
      <span>{_esc(item.source_name)}</span>
      <span>
        <span data-lang="en">{_esc(item.section_title.en)}</span>
        <span data-lang="zh">{_esc(item.section_title.zh)}</span>
      </span>
      <span>
        <span data-lang="en">{_esc(paragraph_count_en)}</span>
        <span data-lang="zh">{_esc(paragraph_count_zh)}</span>
      </span>
      <span>
        <span data-lang="en">{_esc(section_count_en)}</span>
        <span data-lang="zh">{_esc(section_count_zh)}</span>
      </span>
    </a>"""


def _safe_saved_article_coverage_href(href: object) -> str | None:
    return safe_row_one_detail_fragment_href(href, "local-article-digest")


def _has_saved_signal_index_entries(index: RowOneSavedSignalIndex | None) -> bool:
    return index is not None and bool(index.entries)


def _render_saved_article_library_entry(
    library: RowOneSavedArticleLibrary | None,
    *,
    saved_signal_index: RowOneSavedSignalIndex | None = None,
) -> str:
    if library is None:
        return ""
    has_saved_signal_index = _has_saved_signal_index_entries(saved_signal_index)
    dek_en = (
        "Browse saved local articles by signals or sources."
        if has_saved_signal_index
        else "Browse the current edition's saved local articles by source."
    )
    dek_zh = (
        "按信号或来源浏览本地保存文章。"
        if has_saved_signal_index
        else "按来源浏览当前版本的本地保存文章。"
    )
    return f"""<section class="saved-article-library-entry"
  aria-label="Daily saved article library">
  <div class="saved-article-library-entry-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Daily Saved Article Library</span>
        <span data-lang="zh">每日本地文章库</span>
      </p>
      <h2>
        <span data-lang="en">Daily Saved Article Library</span>
        <span data-lang="zh">每日本地文章库</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">{_esc(dek_en)}</span>
      <span data-lang="zh">{_esc(dek_zh)}</span>
    </p>
  </div>
  {_render_saved_article_library_metrics(library, css_class="saved-article-library-entry-metrics")}
  <a class="saved-article-library-entry-link" href="articles/index.html">
    <span data-lang="en">Open saved article library</span>
    <span data-lang="zh">打开本地文章库</span>
  </a>
</section>"""


def _render_saved_article_library_metrics(
    library: RowOneSavedArticleLibrary,
    *,
    css_class: str,
) -> str:
    metrics = [
        _render_saved_article_library_metric(
            _count_label(library.article_count, "saved article", "saved articles"),
            f"{library.article_count} 篇保存文章",
        ),
        _render_saved_article_library_metric(
            _count_label(library.source_count, "source", "sources"),
            f"{library.source_count} 个来源",
        ),
        _render_saved_article_library_metric(
            _count_label(
                library.saved_paragraph_count,
                "saved paragraph",
                "saved paragraphs",
            ),
            f"{library.saved_paragraph_count} 个保存段落",
        ),
        _render_saved_article_library_metric(
            _count_label(
                library.organized_section_count,
                "organized section",
                "organized sections",
            ),
            f"{library.organized_section_count} 个整理栏目",
        ),
    ]
    if library.extracted_article_count:
        metrics.append(
            _render_saved_article_library_metric(
                _count_label(
                    library.extracted_article_count,
                    "extracted text",
                    "extracted text",
                ),
                f"{library.extracted_article_count} 篇提取正文",
            )
        )
    if library.summary_fallback_article_count:
        metrics.append(
            _render_saved_article_library_metric(
                _count_label(
                    library.summary_fallback_article_count,
                    "summary fallback",
                    "summary fallback",
                ),
                f"{library.summary_fallback_article_count} 篇摘要兜底",
            )
        )
    if library.skipped_article_count:
        metrics.append(
            _render_saved_article_library_metric(
                _count_label(library.skipped_article_count, "skipped", "skipped"),
                f"{library.skipped_article_count} 篇跳过",
            )
        )
    return f'<ul class="{_esc(css_class)}">\n' + "\n".join(metrics) + "\n  </ul>"


def _render_saved_article_library_metric(label_en: str, label_zh: str) -> str:
    return (
        "    <li>"
        f'<span data-lang="en">{_esc(label_en)}</span>'
        f'<span data-lang="zh">{_esc(label_zh)}</span>'
        "</li>"
    )


def _render_saved_article_daily_summary(
    library: RowOneSavedArticleLibrary,
    *,
    source_routes: Sequence[_SavedArticleSourceRoute],
    signal_index_html: str,
    content_organization_html: str,
    reading_paths_html: str,
    theme_digest_html: str,
    reference_atlas_html: str,
    signal_facets_html: str,
    daily_signal_leaderboard_html: str,
    evidence_board_html: str,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str:
    has_source_grid = any(group.entries for group in library.groups)
    if library.article_count <= 0 or not has_source_grid:
        return ""
    links = [
        _render_saved_article_daily_summary_link(
            "#saved-article-theme-digest",
            "Theme Digest",
            "主题简报",
        )
        if theme_digest_html
        else "",
        _render_saved_article_daily_summary_link(
            "#saved-article-reference-atlas",
            "Reference Atlas",
            "引用图谱",
        )
        if reference_atlas_html
        else "",
        _render_saved_article_daily_summary_link(
            "#saved-article-signal-facets",
            "Signal Facets",
            "信号切面",
        )
        if signal_facets_html
        else "",
        _render_saved_article_daily_summary_link(
            "#saved-article-daily-signal-leaderboard",
            "Daily Signal Leaderboard",
            "每日信号榜",
        )
        if daily_signal_leaderboard_html
        else "",
        _render_saved_article_daily_summary_link(
            "#saved-signal-index",
            "Signal Index",
            "信号索引",
        )
        if signal_index_html
        else "",
        _render_saved_article_daily_summary_link(
            "#saved-article-reading-paths",
            "Reading Paths",
            "阅读路径",
        )
        if reading_paths_html
        else "",
        _render_saved_article_daily_summary_link(
            "#saved-article-evidence-board",
            "Evidence Board",
            "证据板",
        )
        if evidence_board_html
        else "",
        _render_saved_article_daily_summary_link(
            "#saved-article-content-organization",
            "Content Organization",
            "内容整理",
        )
        if content_organization_html
        else "",
        _render_saved_article_daily_summary_link(
            "#saved-article-library-grid",
            "Source Grid",
            "来源网格",
        )
        if has_source_grid
        else "",
    ]
    reading_href = _first_saved_article_daily_summary_reading_href(
        library,
        local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
    )
    if reading_href is not None:
        links.append(
            _render_saved_article_daily_summary_link(
                reading_href,
                "Start Reading",
                "开始阅读",
            )
        )
    links = [link for link in links if link]
    if not links:
        return ""
    surface_count = len(links) - (1 if reading_href is not None else 0)
    source_routes_html = _render_saved_article_source_routes(source_routes)
    metrics = (
        _render_saved_article_library_metric(
            _count_label(library.article_count, "saved local article", "saved local articles"),
            f"{library.article_count} 篇本地保存文章",
        )
        + "\n"
        + _render_saved_article_library_metric(
            _count_label(library.source_count, "source", "sources"),
            f"{library.source_count} 个来源",
        )
        + "\n"
        + _render_saved_article_library_metric(
            _count_label(surface_count, "available surface", "available surfaces"),
            f"{surface_count} 个可用导览入口",
        )
    )
    return f"""<section class="saved-article-daily-summary"
  aria-label="Saved article daily summary">
  <div class="saved-article-daily-summary-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Saved Article Daily Summary</span>
        <span data-lang="zh">保存文章每日导览</span>
      </p>
      <h2>
        <span data-lang="en">Saved Article Daily Summary</span>
        <span data-lang="zh">保存文章每日导览</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">A compact orientation layer for today's saved local article set.</span>
      <span data-lang="zh">面向今日本地保存文章集合的紧凑阅读导览。</span>
    </p>
  </div>
  <ul class="saved-article-daily-summary-metrics">
{metrics}
  </ul>
  {source_routes_html}
  <div class="saved-article-daily-summary-links">{"".join(links)}</div>
</section>"""


def _saved_article_source_routes(
    groups: Sequence[RowOneSavedArticleLibrarySourceGroup],
) -> list[_SavedArticleSourceRoute]:
    routes: list[_SavedArticleSourceRoute] = []
    seen_slugs: dict[str, int] = {}
    for group_index, group in enumerate(groups):
        if not group.entries:
            continue
        slug = _saved_article_source_route_slug(group.source_name)
        if slug is None:
            continue
        count = seen_slugs.get(slug, 0) + 1
        seen_slugs[slug] = count
        anchor_id = (
            f"saved-article-source-{slug}" if count == 1 else f"saved-article-source-{slug}-{count}"
        )
        routes.append(
            _SavedArticleSourceRoute(
                group_index=group_index,
                source_name=group.source_name.strip() or "Unknown source",
                anchor_id=anchor_id,
                article_count=group.article_count,
                saved_paragraph_count=group.saved_paragraph_count,
            )
        )
    return routes


def _saved_article_source_route_slug(source_name: str) -> str | None:
    slug = re.sub(r"[^a-z0-9]+", "-", source_name.strip().casefold()).strip("-")
    slug = slug[:64].strip("-")
    return slug or None


def _render_saved_article_source_routes(
    source_routes: Sequence[_SavedArticleSourceRoute],
) -> str:
    items = [
        _render_saved_article_source_route(route)
        for route in source_routes[:SAVED_ARTICLE_SOURCE_ROUTE_LIMIT]
    ]
    if not items:
        return ""
    route_count = len(items)
    route_count_en = _count_label(route_count, "source route", "source routes")
    route_count_zh = f"{route_count} 个来源入口"
    return f"""<div class="saved-article-source-routes" aria-label="Saved article source routes">
    <div class="saved-article-source-routes-header">
      <strong>
        <span data-lang="en">Saved Article Source Routes</span>
        <span data-lang="zh">来源导览</span>
      </strong>
      <span class="saved-article-source-routes-metrics">
        <span data-lang="en">{_esc(route_count_en)}</span>
        <span data-lang="zh">{_esc(route_count_zh)}</span>
      </span>
    </div>
    <ul class="saved-article-source-routes-list">{"".join(items)}</ul>
  </div>"""


def _render_saved_article_source_route(route: _SavedArticleSourceRoute) -> str:
    article_count_en = _count_label(route.article_count, "article", "articles")
    article_count_zh = f"{route.article_count} 篇文章"
    paragraph_count_en = _count_label(
        route.saved_paragraph_count,
        "saved paragraph",
        "saved paragraphs",
    )
    paragraph_count_zh = f"{route.saved_paragraph_count} 个保存段落"
    href = f"#{_esc(route.anchor_id)}"
    return f"""<li class="saved-article-source-routes-item">
        <a class="saved-article-source-route saved-article-source-routes-link" href="{href}">
          <span class="saved-article-source-routes-label">{_esc(route.source_name)}</span>
          <span class="saved-article-source-routes-meta">
            <span data-lang="en">{_esc(article_count_en)}, {_esc(paragraph_count_en)}</span>
            <span data-lang="zh">{_esc(article_count_zh)}，{_esc(paragraph_count_zh)}</span>
          </span>
        </a>
      </li>"""


def _render_saved_article_daily_summary_link(
    href: str,
    label_en: str,
    label_zh: str,
) -> str:
    return f"""<a class="saved-article-daily-summary-link" href="{_esc(href)}">
    <span data-lang="en">{_esc(label_en)}</span>
    <span data-lang="zh">{_esc(label_zh)}</span>
  </a>"""


def _saved_article_organization_jump_index_source_routes(
    source_routes: Sequence[_SavedArticleSourceRoute],
) -> tuple[RowOneSavedArticleOrganizationJumpIndexSourceRoute, ...]:
    return tuple(
        RowOneSavedArticleOrganizationJumpIndexSourceRoute(
            label=LocalizedText(en=route.source_name, zh=route.source_name),
            href=f"#{route.anchor_id}",
            article_count=route.article_count,
        )
        for route in source_routes
    )


def _saved_article_library_page_target_ids(
    *,
    source_routes: Sequence[_SavedArticleSourceRoute],
    content_organization_html: str,
    signal_facets_html: str,
    daily_signal_leaderboard_html: str,
) -> set[str]:
    target_ids = {route.anchor_id for route in source_routes}
    if content_organization_html:
        target_ids.add("saved-article-content-organization")
    if signal_facets_html:
        target_ids.add("saved-article-signal-facets")
    if daily_signal_leaderboard_html:
        target_ids.add("saved-article-daily-signal-leaderboard")
    return target_ids


def _render_saved_article_organization_jump_index(
    jump_index: RowOneSavedArticleOrganizationJumpIndex | None,
    *,
    target_ids: set[str],
) -> str:
    if jump_index is None or not jump_index.groups:
        return ""
    rendered_groups: list[str] = []
    rendered_item_count = 0
    for group in jump_index.groups:
        group_html, group_item_count = _render_saved_article_organization_jump_index_group(
            group,
            target_ids=target_ids,
        )
        if not group_html:
            continue
        rendered_groups.append(group_html)
        rendered_item_count += group_item_count
    groups = "\n".join(rendered_groups)
    if not groups:
        return ""
    rendered_group_count = len(rendered_groups)
    item_count_en = _count_label(rendered_item_count, "jump", "jumps")
    group_count_en = _count_label(rendered_group_count, "group", "groups")
    summary_en = f"{_esc(item_count_en)} across {_esc(group_count_en)} of local article surfaces."
    summary_zh = (
        f"{_esc(str(rendered_item_count))} 个跳转入口，覆盖 "
        f"{_esc(str(rendered_group_count))} 个本地文章分组。"
    )
    return f"""<section class="saved-article-organization-jump-index"
  id="saved-article-organization-jump-index"
  aria-label="Saved article organization jump index">
  <div class="saved-article-organization-jump-index-header">
    <p class="eyebrow">Organization Jump Index</p>
    <h2>
      <span data-lang="en">Saved Article Organization Jump Index</span>
      <span data-lang="zh">保存文章组织索引</span>
    </h2>
    <p>
      <span data-lang="en">{summary_en}</span>
      <span data-lang="zh">{summary_zh}</span>
    </p>
  </div>
  <div class="saved-article-organization-jump-index-grid">
{groups}
  </div>
</section>"""


def _render_saved_article_organization_jump_index_group(
    group: RowOneSavedArticleOrganizationJumpIndexGroup,
    *,
    target_ids: set[str],
) -> tuple[str, int]:
    rendered_items = tuple(
        item_html
        for item in group.items
        if (
            item_html := _render_saved_article_organization_jump_index_item(
                item,
                target_ids=target_ids,
            )
        )
    )
    items = "\n".join(rendered_items)
    if not items:
        return "", 0
    return (
        f"""    <div class="saved-article-organization-jump-index-group"
      aria-label="{_esc(group.title.en)}">
      <h3>
        <span data-lang="en">{_esc(group.title.en)}</span>
        <span data-lang="zh">{_esc(group.title.zh)}</span>
      </h3>
      <ul class="saved-article-organization-jump-index-items">
{items}
      </ul>
    </div>""",
        len(rendered_items),
    )


def _render_saved_article_organization_jump_index_item(
    item: RowOneSavedArticleOrganizationJumpIndexItem,
    *,
    target_ids: set[str],
) -> str:
    href = _saved_article_organization_jump_index_href(item.href, target_ids=target_ids)
    if href is None:
        return ""
    return f"""        <li class="saved-article-organization-jump-index-item">
          <a class="saved-article-organization-jump-index-link" href="{_esc(href)}">
            <span class="saved-article-organization-jump-index-label">
              <span data-lang="en">{_esc(item.label.en)}</span>
              <span data-lang="zh">{_esc(item.label.zh)}</span>
            </span>
            <span class="saved-article-organization-jump-index-count">
              <span data-lang="en">{_esc(item.count_label.en)}</span>
              <span data-lang="zh">{_esc(item.count_label.zh)}</span>
            </span>
          </a>
        </li>"""


def _saved_article_organization_jump_index_href(
    href: str,
    *,
    target_ids: set[str],
) -> str | None:
    if not href.startswith("#") or "://" in href or any(character.isspace() for character in href):
        return None
    target_id = href.removeprefix("#")
    if target_id not in target_ids:
        return None
    return href


def _render_saved_article_reading_queue(
    queue: RowOneSavedArticleReadingQueue | None,
) -> str:
    if queue is None or not queue.items:
        return ""
    rendered_items = tuple(
        item_html
        for item in queue.items
        if (item_html := _render_saved_article_reading_queue_item(item))
    )
    if not rendered_items:
        return ""
    items = "\n".join(rendered_items)
    item_count = len(rendered_items)
    item_count_en = _count_label(item_count, "article", "articles")
    summary_en = f"{_esc(item_count_en)} queued from saved local article bodies."
    summary_zh = f"{_esc(str(item_count))} 篇本地保存文章进入阅读队列。"
    return f"""<section class="saved-article-reading-queue"
  id="saved-article-reading-queue"
  aria-label="Saved article reading queue">
  <div class="saved-article-reading-queue-header">
    <p class="eyebrow">Reading Queue</p>
    <h2>
      <span data-lang="en">Saved Article Reading Queue</span>
      <span data-lang="zh">保存文章阅读队列</span>
    </h2>
    <p>
      <span data-lang="en">{summary_en}</span>
      <span data-lang="zh">{summary_zh}</span>
    </p>
  </div>
  <ol class="saved-article-reading-queue-list">
{items}
  </ol>
</section>"""


def _render_saved_article_reading_queue_item(
    item: RowOneSavedArticleReadingQueueItem,
) -> str:
    href = _saved_article_reading_queue_href(item.href)
    if href is None:
        return ""
    paragraph_count_en = _count_label(
        item.saved_paragraph_count,
        "saved paragraph",
        "saved paragraphs",
    )
    section_count_en = _count_label(
        item.organized_section_count,
        "organized section",
        "organized sections",
    )
    paragraph_count_zh = f"{item.saved_paragraph_count} 个保存段落"
    section_count_zh = f"{item.organized_section_count} 个整理分区"
    return f"""    <li class="saved-article-reading-queue-item">
      <div>
        <a class="saved-article-reading-queue-title" href="{_esc(href)}">
          <span data-lang="en">{_esc(item.title.en)}</span>
          <span data-lang="zh">{_esc(item.title.zh)}</span>
        </a>
        <div class="saved-article-reading-queue-meta">
          <span>{_esc(item.source_name)}</span>
          <span>
            <span data-lang="en">{_esc(item.body_source_label.en)}</span>
            <span data-lang="zh">{_esc(item.body_source_label.zh)}</span>
          </span>
          <span>
            <span data-lang="en">{_esc(paragraph_count_en)}</span>
            <span data-lang="zh">{_esc(paragraph_count_zh)}</span>
          </span>
          <span>
            <span data-lang="en">{_esc(section_count_en)}</span>
            <span data-lang="zh">{_esc(section_count_zh)}</span>
          </span>
        </div>
      </div>
      <a class="saved-article-reading-queue-action" href="{_esc(href)}">
        <span data-lang="en">Open</span>
        <span data-lang="zh">打开</span>
      </a>
    </li>"""


def _saved_article_reading_queue_href(href: str) -> str | None:
    if not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if href.startswith(("http:", "https:", "//", "javascript:")):
        return None
    if href.startswith("../details/"):
        detail_href = href.removeprefix("../")
        safe_href = safe_row_one_detail_fragment_href(detail_href, "local-article-digest")
        if safe_href is None or f"../{safe_href}" != href:
            return None
        return href
    if href.startswith(".") or href.startswith("/") or "/" in href:
        return None
    page_href, separator, fragment = href.partition("#")
    if not separator or fragment != "local-article-digest":
        return None
    if not page_href.endswith(".html"):
        return None
    if not safe_local_article_story_id(page_href.removesuffix(".html")):
        return None
    return href


def _render_saved_article_filing_inbox(
    inbox: RowOneSavedArticleFilingInbox | None,
) -> str:
    if inbox is None or not inbox.items:
        return ""
    rendered_items = tuple(
        item_html
        for item in inbox.items
        if (item_html := _render_saved_article_filing_inbox_item(item))
    )
    if not rendered_items:
        return ""
    article_count = len(rendered_items)
    total_unfiled = sum(item.unfiled_paragraph_count for item in inbox.items)
    article_count_en = _count_label(article_count, "article", "articles")
    unfiled_count_en = _count_label(
        total_unfiled,
        "unfiled paragraph",
        "unfiled paragraphs",
    )
    summary_en = (
        f"{_esc(article_count_en)} with {_esc(unfiled_count_en)} still outside "
        "organized content sections."
    )
    summary_zh = (
        f"{_esc(str(article_count))} 篇保存文章中有 {_esc(str(total_unfiled))} "
        "个段落尚未归入整理分区。"
    )
    return f"""<section class="saved-article-filing-inbox"
  id="saved-article-filing-inbox"
  aria-label="Saved article filing inbox">
  <div class="saved-article-filing-inbox-header">
    <p class="eyebrow">Filing Inbox</p>
    <h2>
      <span data-lang="en">Saved Article Filing Inbox</span>
      <span data-lang="zh">保存文章归档收件箱</span>
    </h2>
    <p>
      <span data-lang="en">{summary_en}</span>
      <span data-lang="zh">{summary_zh}</span>
    </p>
  </div>
  <div class="saved-article-filing-inbox-metrics">
    <span>
      <span data-lang="en">{_esc(article_count_en)}</span>
      <span data-lang="zh">{_esc(str(article_count))} 篇文章</span>
    </span>
    <span>
      <span data-lang="en">{_esc(unfiled_count_en)}</span>
      <span data-lang="zh">{_esc(str(total_unfiled))} 个未归档段落</span>
    </span>
  </div>
  <ol class="saved-article-filing-inbox-list">
{chr(10).join(rendered_items)}
  </ol>
</section>"""


def _render_saved_article_filing_inbox_item(
    item: RowOneSavedArticleFilingInboxItem,
) -> str:
    rendered_paragraphs = tuple(
        paragraph_html
        for paragraph in item.paragraphs
        if (paragraph_html := _render_saved_article_filing_inbox_paragraph(paragraph))
    )
    if not rendered_paragraphs:
        return ""
    paragraph_count_en = _count_label(
        item.saved_paragraph_count,
        "saved paragraph",
        "saved paragraphs",
    )
    section_count_en = _count_label(
        item.organized_section_count,
        "organized section",
        "organized sections",
    )
    unfiled_count_en = _count_label(
        item.unfiled_paragraph_count,
        "unfiled paragraph",
        "unfiled paragraphs",
    )
    return f"""    <li class="saved-article-filing-inbox-item">
      <div>
        <h3>
          <span data-lang="en">{_esc(item.title.en)}</span>
          <span data-lang="zh">{_esc(item.title.zh)}</span>
        </h3>
        <div class="saved-article-filing-inbox-meta">
          <span>{_esc(item.source_name)}</span>
          <span>
            <span data-lang="en">{_esc(item.body_source_label.en)}</span>
            <span data-lang="zh">{_esc(item.body_source_label.zh)}</span>
          </span>
          <span>
            <span data-lang="en">{_esc(paragraph_count_en)}</span>
            <span data-lang="zh">{_esc(str(item.saved_paragraph_count))} 个保存段落</span>
          </span>
          <span>
            <span data-lang="en">{_esc(section_count_en)}</span>
            <span data-lang="zh">{_esc(str(item.organized_section_count))} 个整理分区</span>
          </span>
          <span>
            <span data-lang="en">{_esc(unfiled_count_en)}</span>
            <span data-lang="zh">{_esc(str(item.unfiled_paragraph_count))} 个未归档段落</span>
          </span>
        </div>
      </div>
      <div class="saved-article-filing-inbox-paragraphs">
{chr(10).join(rendered_paragraphs)}
      </div>
    </li>"""


def _render_saved_article_filing_inbox_paragraph(
    paragraph: RowOneSavedArticleFilingInboxParagraph,
) -> str:
    href = _saved_article_filing_inbox_href(paragraph.href)
    if href is None:
        return ""
    return f"""        <a class="saved-article-filing-inbox-paragraph" href="{_esc(href)}">
          <span class="saved-article-filing-inbox-link">
            <span data-lang="en">{_esc(paragraph.label.en)}</span>
            <span data-lang="zh">{_esc(paragraph.label.zh)}</span>
          </span>
          <p>
            <span data-lang="en">{_esc(paragraph.excerpt.en)}</span>
            <span data-lang="zh">{_esc(paragraph.excerpt.zh)}</span>
          </p>
        </a>"""


def _saved_article_filing_inbox_href(href: str) -> str | None:
    if not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if href.startswith(("http:", "https:", "//", "javascript:", ".", "/")):
        return None
    if "/" in href or "\\" in href:
        return None
    page_href, separator, fragment = href.partition("#")
    if not separator:
        return None
    fragment_prefix = "local-article-paragraph-"
    if not fragment.startswith(fragment_prefix):
        return None
    paragraph_number = fragment.removeprefix(fragment_prefix)
    if not re.fullmatch(r"[1-9][0-9]*", paragraph_number):
        return None
    if not page_href.endswith(".html"):
        return None
    if not safe_local_article_story_id(page_href.removesuffix(".html")):
        return None
    return href


def _render_saved_article_read_next_clusters(
    clusters: RowOneSavedArticleReadNextClusters | None,
) -> str:
    if clusters is None or not clusters.clusters:
        return ""
    rendered_clusters = tuple(
        rendered
        for cluster in clusters.clusters
        if (rendered := _render_saved_article_read_next_cluster(cluster)) is not None
    )
    if not rendered_clusters:
        return ""
    cluster_count = len(rendered_clusters)
    item_count = sum(rendered.item_count for rendered in rendered_clusters)
    source_count = len(
        {
            " ".join(source_name.split()).casefold()
            for rendered in rendered_clusters
            for source_name in rendered.source_names
        }
    )
    evidence_count = sum(rendered.evidence_count for rendered in rendered_clusters)
    cluster_count_en = _count_label(cluster_count, "cluster", "clusters")
    item_count_en = _count_label(item_count, "saved article", "saved articles")
    summary_en = f"{_esc(cluster_count_en)} organizing {_esc(item_count_en)} for the next read."
    summary_zh = f"{_esc(str(cluster_count))} 个阅读集群整理 {_esc(str(item_count))} 篇保存文章。"
    metrics = _render_saved_article_read_next_cluster_metrics(
        item_count=item_count,
        source_count=source_count,
        evidence_count=evidence_count,
    )
    return f"""<section class="saved-article-read-next-clusters"
  id="saved-article-read-next-clusters"
  aria-label="Saved article read next clusters">
  <div class="saved-article-read-next-clusters-header">
    <p class="eyebrow">Read Next</p>
    <h2>
      <span data-lang="en">Saved Article Read Next Clusters</span>
      <span data-lang="zh">保存文章继续阅读集群</span>
    </h2>
    <p>
      <span data-lang="en">{summary_en}</span>
      <span data-lang="zh">{summary_zh}</span>
    </p>
  </div>
  {metrics}
  <div class="saved-article-read-next-clusters-grid">
{chr(10).join(rendered.html for rendered in rendered_clusters)}
  </div>
</section>"""


def _render_saved_article_read_next_cluster_metrics(
    *,
    item_count: int,
    source_count: int,
    evidence_count: int,
) -> str:
    article_count_en = _count_label(item_count, "saved article", "saved articles")
    source_count_en = _count_label(source_count, "source", "sources")
    evidence_count_en = _count_label(evidence_count, "evidence point", "evidence points")
    return f"""<div class="saved-article-read-next-clusters-metrics">
    <span>
      <span data-lang="en">{_esc(article_count_en)}</span>
      <span data-lang="zh">{_esc(str(item_count))} 篇保存文章</span>
    </span>
    <span>
      <span data-lang="en">{_esc(source_count_en)}</span>
      <span data-lang="zh">{_esc(str(source_count))} 个来源</span>
    </span>
    <span>
      <span data-lang="en">{_esc(evidence_count_en)}</span>
      <span data-lang="zh">{_esc(str(evidence_count))} 个证据点</span>
    </span>
  </div>"""


def _render_saved_article_read_next_cluster(
    cluster: RowOneSavedArticleReadNextCluster,
) -> _RenderedSavedArticleReadNextCluster | None:
    rendered_items: list[str] = []
    rendered_source_names: list[str] = []
    rendered_evidence_count = 0
    for item in cluster.items:
        item_html = _render_saved_article_read_next_cluster_item(item)
        if not item_html:
            continue
        rendered_items.append(item_html)
        rendered_source_names.append(item.source_name)
        rendered_evidence_count += item.evidence_count
    if not rendered_items:
        return None
    item_count_en = _count_label(len(rendered_items), "article", "articles")
    evidence_count_en = _count_label(
        rendered_evidence_count,
        "evidence point",
        "evidence points",
    )
    html = f"""    <article class="saved-article-read-next-clusters-cluster">
      <div>
        <h3>
          <span data-lang="en">{_esc(cluster.title.en)}</span>
          <span data-lang="zh">{_esc(cluster.title.zh)}</span>
        </h3>
        <p>
          <span data-lang="en">{_esc(cluster.dek.en)}</span>
          <span data-lang="zh">{_esc(cluster.dek.zh)}</span>
        </p>
        <div class="saved-article-read-next-clusters-meta">
          <span>{_esc(item_count_en)}</span>
          <span>{_esc(evidence_count_en)}</span>
        </div>
      </div>
{chr(10).join(rendered_items)}
    </article>"""
    return _RenderedSavedArticleReadNextCluster(
        html=html,
        item_count=len(rendered_items),
        source_names=tuple(rendered_source_names),
        evidence_count=rendered_evidence_count,
    )


def _render_saved_article_read_next_cluster_item(
    item: RowOneSavedArticleReadNextClusterItem,
) -> str:
    href = _saved_article_read_next_cluster_href(item.href)
    if href is None:
        return ""
    paragraph_count_en = _count_label(
        item.saved_paragraph_count,
        "saved paragraph",
        "saved paragraphs",
    )
    section_count_en = _count_label(
        item.organized_section_count,
        "organized section",
        "organized sections",
    )
    refs = _render_saved_article_read_next_cluster_refs(item.references)
    evidence_count_en = _count_label(
        item.evidence_count,
        "evidence point",
        "evidence points",
    )
    return f"""      <article class="saved-article-read-next-clusters-item">
        <div class="saved-article-read-next-clusters-meta">
          <span>{_esc(item.source_name)}</span>
          <span>
            <span data-lang="en">{_esc(item.section_label.en)}</span>
            <span data-lang="zh">{_esc(item.section_label.zh)}</span>
          </span>
          <span>
            <span data-lang="en">{_esc(item.body_source_label.en)}</span>
            <span data-lang="zh">{_esc(item.body_source_label.zh)}</span>
          </span>
        </div>
        <h4>
          <span data-lang="en">{_esc(item.title.en)}</span>
          <span data-lang="zh">{_esc(item.title.zh)}</span>
        </h4>
        <p class="saved-article-read-next-clusters-lead">
          <span data-lang="en">{_esc(item.lead.en)}</span>
          <span data-lang="zh">{_esc(item.lead.zh)}</span>
        </p>
        <div class="saved-article-read-next-clusters-meta">
          <span>{_esc(paragraph_count_en)}</span>
          <span>{_esc(section_count_en)}</span>
          <span>{_esc(evidence_count_en)}</span>
        </div>{refs}
        <a class="saved-article-read-next-clusters-action" href="{_esc(href)}">
          <span data-lang="en">Read locally</span>
          <span data-lang="zh">本地阅读</span>
        </a>
      </article>"""


def _render_saved_article_read_next_cluster_refs(
    references: Sequence[RowOneReference],
) -> str:
    def _chip_label(ref: RowOneReference) -> str:
        suffix = ref.label.strip() or ref.type.strip()
        return f"{ref.name.strip()} · {suffix}" if suffix else ref.name.strip()

    chips = "".join(
        f"<span>{_esc(_chip_label(ref))}</span>" for ref in references if ref.name.strip()
    )
    if not chips:
        return ""
    return f'\n        <div class="saved-article-read-next-clusters-refs">{chips}</div>'


def _saved_article_read_next_cluster_href(href: str) -> str | None:
    if not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if href.startswith(("http:", "https:", "//", "javascript:")):
        return None
    if href.startswith("../details/"):
        detail_href = href.removeprefix("../")
        digest_href = safe_row_one_detail_fragment_href(detail_href, "local-article-digest")
        if digest_href is not None and f"../{digest_href}" == href:
            return href
        path, separator, fragment = detail_href.partition("#")
        if not separator:
            return None
        if validated_row_one_detail_relative_path(path) is None:
            return None
        if _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment) is None:
            return None
        return href
    if href.startswith(".") or href.startswith("/") or "/" in href:
        return None
    page_href, separator, fragment = href.partition("#")
    if not separator or fragment != "local-article-digest":
        return None
    if not page_href.endswith(".html"):
        return None
    if not safe_local_article_story_id(page_href.removesuffix(".html")):
        return None
    return href


def _render_saved_article_local_reading_companion(
    companion: RowOneSavedArticleLocalReadingCompanion | None,
) -> str:
    if companion is None:
        return ""
    current = _render_saved_article_local_reading_companion_current(companion)
    related = _render_saved_article_local_reading_companion_related(companion.related_items)
    if not current and not related:
        return ""
    paragraph_count = _count_label(
        companion.saved_paragraph_count,
        "saved paragraph",
        "saved paragraphs",
    )
    section_count = _count_label(
        companion.organized_section_count,
        "organized section",
        "organized sections",
    )
    evidence_count = _count_label(
        companion.evidence_count,
        "evidence point",
        "evidence points",
    )
    return f"""    <section class="saved-article-local-reading-companion"
      aria-labelledby="saved-article-local-reading-companion-title">
      <div class="saved-article-local-reading-companion-header">
        <h2 id="saved-article-local-reading-companion-title">
          <span data-lang="en">Saved Article Local Reading Companion</span>
          <span data-lang="zh">保存文章本地伴读</span>
        </h2>
        <p>
          <span data-lang="en">A local-first guide for this saved article and what to read
          next in the same edition.</span>
          <span data-lang="zh">面向这篇保存文章与同日后续阅读的本地优先导读。</span>
        </p>
      </div>
      <div class="saved-article-local-reading-companion-metrics">
        <span>{_esc(paragraph_count)}</span>
        <span>{_esc(section_count)}</span>
        <span>{_esc(evidence_count)}</span>
      </div>
{current}
{related}
    </section>"""


def _render_saved_article_local_reading_companion_current(
    companion: RowOneSavedArticleLocalReadingCompanion,
) -> str:
    links = _render_saved_article_local_reading_companion_links(companion)
    filing_trail = _render_saved_article_local_reading_companion_filing_trail(
        companion.filing_links
    )
    refs = _render_saved_article_local_reading_companion_refs(companion.references)
    return f"""      <article class="saved-article-local-reading-companion-current">
        <div class="saved-article-local-reading-companion-meta">
          <span>{_esc(companion.source_name)}</span>
          <span>
            <span data-lang="en">{_esc(companion.group_title.en)}</span>
            <span data-lang="zh">{_esc(companion.group_title.zh)}</span>
          </span>
          <span>
            <span data-lang="en">{_esc(companion.body_source_label.en)}</span>
            <span data-lang="zh">{_esc(companion.body_source_label.zh)}</span>
          </span>
        </div>
        <h3>
          <span data-lang="en">{_esc(companion.current_title.en)}</span>
          <span data-lang="zh">{_esc(companion.current_title.zh)}</span>
        </h3>
        <p>
          <span data-lang="en">{_esc(companion.lead.en)}</span>
          <span data-lang="zh">{_esc(companion.lead.zh)}</span>
        </p>
{links}{filing_trail}{refs}
      </article>"""


def _render_saved_article_local_reading_companion_links(
    companion: RowOneSavedArticleLocalReadingCompanion,
) -> str:
    links: list[str] = []
    for link in companion.local_links:
        href = _saved_article_local_reading_companion_href(link.href)
        if href is None or not href.startswith("#"):
            continue
        links.append(
            f"""        <a href="{_esc(href)}">
          <span data-lang="en">{_esc(link.label.en)}</span>
          <span data-lang="zh">{_esc(link.label.zh)}</span>
        </a>"""
        )
    if not links:
        return ""
    return (
        '        <div class="saved-article-local-reading-companion-links">\n'
        + "\n".join(links)
        + "\n        </div>\n"
    )


def _render_saved_article_local_reading_companion_filing_trail(
    links: Sequence[RowOneSavedArticleLocalReadingCompanionTrailLink],
) -> str:
    rendered: list[str] = []
    for link in links:
        href = _saved_article_local_reading_companion_href(link.href)
        if href is None or not href.startswith("index.html#"):
            continue
        rendered.append(
            f"""          <a href="{_esc(href)}">
            <span data-lang="en">{_esc(link.label.en)}</span>
            <span data-lang="zh">{_esc(link.label.zh)}</span>
          </a>"""
        )
    if not rendered:
        return ""
    return (
        '        <div class="saved-article-local-reading-companion-filing-trail" '
        'aria-label="Saved article filing trail">\n'
        "          <strong>\n"
        '            <span data-lang="en">Filed In</span>\n'
        '            <span data-lang="zh">内容归档</span>\n'
        "          </strong>\n" + "\n".join(rendered) + "\n        </div>\n"
    )


def _render_saved_article_local_reading_companion_related(
    items: Sequence[RowOneSavedArticleLocalReadingCompanionItem],
) -> str:
    rendered = [
        item_html
        for item in items
        if (item_html := _render_saved_article_local_reading_companion_item(item))
    ]
    if not rendered:
        return ""
    return (
        '      <div class="saved-article-local-reading-companion-related">\n'
        + "\n".join(rendered)
        + "\n      </div>"
    )


def _render_saved_article_local_reading_companion_item(
    item: RowOneSavedArticleLocalReadingCompanionItem,
) -> str:
    href = _saved_article_local_reading_companion_href(item.href)
    if href is None or href.startswith("#"):
        return ""
    paragraph_count = _count_label(
        item.saved_paragraph_count,
        "saved paragraph",
        "saved paragraphs",
    )
    section_count = _count_label(
        item.organized_section_count,
        "organized section",
        "organized sections",
    )
    evidence_count = _count_label(item.evidence_count, "evidence point", "evidence points")
    refs = _render_saved_article_local_reading_companion_refs(item.references)
    return f"""        <article class="saved-article-local-reading-companion-item">
          <div class="saved-article-local-reading-companion-meta">
            <span>{_esc(item.source_name)}</span>
            <span>
              <span data-lang="en">{_esc(item.section_label.en)}</span>
              <span data-lang="zh">{_esc(item.section_label.zh)}</span>
            </span>
            <span>
              <span data-lang="en">{_esc(item.body_source_label.en)}</span>
              <span data-lang="zh">{_esc(item.body_source_label.zh)}</span>
            </span>
          </div>
          <h3>
            <span data-lang="en">{_esc(item.title.en)}</span>
            <span data-lang="zh">{_esc(item.title.zh)}</span>
          </h3>
          <p>
            <span data-lang="en">{_esc(item.lead.en)}</span>
            <span data-lang="zh">{_esc(item.lead.zh)}</span>
          </p>
          <div class="saved-article-local-reading-companion-meta">
            <span>{_esc(paragraph_count)}</span>
            <span>{_esc(section_count)}</span>
            <span>{_esc(evidence_count)}</span>
          </div>{refs}
          <a class="saved-article-local-reading-companion-action" href="{_esc(href)}">
            <span data-lang="en">Read next locally</span>
            <span data-lang="zh">继续本地阅读</span>
          </a>
        </article>"""


def _render_saved_article_local_reading_companion_refs(
    references: Sequence[RowOneReference],
) -> str:
    chips = "".join(
        f"<span>{_esc(_saved_article_local_reading_companion_ref_label(ref))}</span>"
        for ref in references
        if ref.name.strip()
    )
    if not chips:
        return ""
    return f'\n        <div class="saved-article-local-reading-companion-refs">{chips}</div>'


def _saved_article_local_reading_companion_ref_label(ref: RowOneReference) -> str:
    parts = [part.strip() for part in (ref.name, ref.type, ref.label) if part.strip()]
    return " / ".join(parts)


def _saved_article_local_reading_companion_href(href: str) -> str | None:
    if not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if href.startswith(("http:", "https:", "//", "javascript:")):
        return None
    if href.startswith("#"):
        fragment = href.removeprefix("#")
        if fragment in {
            "local-article-digest",
            "local-article-reader",
            "local-article-paragraph-evidence",
        }:
            return href
        if _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment) is not None:
            return href
        return None
    cross_surface_href = _saved_article_local_reading_companion_cross_surface_href(href)
    if cross_surface_href is not None:
        return cross_surface_href
    return _saved_article_read_next_cluster_href(href)


def _saved_article_local_reading_companion_cross_surface_href(href: str) -> str | None:
    page_href, separator, fragment = href.partition("#")
    if page_href != "index.html" or not separator or not fragment:
        return None
    if fragment.startswith(_SAVED_ARTICLE_LIBRARY_CARD_PREFIX):
        story_id = fragment.removeprefix(_SAVED_ARTICLE_LIBRARY_CARD_PREFIX)
        if safe_local_article_story_id(story_id):
            return href
        return None
    if fragment.startswith(_SAVED_ARTICLE_ORGANIZATION_GROUP_PREFIX):
        group_key = fragment.removeprefix(_SAVED_ARTICLE_ORGANIZATION_GROUP_PREFIX)
        if _SAVED_ARTICLE_ORGANIZATION_GROUP_KEY_RE.fullmatch(group_key) is not None:
            return href
    return None


def _render_saved_article_local_related_reads(
    related_reads: RowOneSavedArticleLocalRelatedReads | None,
) -> str:
    if related_reads is None or not related_reads.cards:
        return ""
    rendered_cards = [
        (card, card_html)
        for card in related_reads.cards
        if (card_html := _render_saved_article_local_related_read_card(card))
    ]
    if not rendered_cards:
        return ""
    renderable_cards = tuple(card for card, _card_html in rendered_cards)
    cards_html = "\n".join(card_html for _card, card_html in rendered_cards)
    connection_brief_cards = _saved_article_local_related_read_connection_brief_cards(
        renderable_cards
    )
    connection_brief = _render_saved_article_local_related_read_connection_brief(
        build_row_one_saved_article_local_related_read_connection_brief(connection_brief_cards)
    )
    lanes = build_row_one_saved_article_local_related_read_lanes(renderable_cards)
    lanes_html = _render_saved_article_local_related_read_lanes(lanes)
    if _saved_article_local_related_read_lane_card_count(lanes) != len(renderable_cards):
        lanes_html = ""
    body_html = (
        lanes_html
        or '      <div class="saved-article-local-related-reads-grid">\n'
        + cards_html
        + "\n      </div>"
    )
    return f"""    <section class="saved-article-local-related-reads"
      aria-labelledby="saved-article-local-related-reads-title">
      <div class="saved-article-local-related-reads-header">
        <h2 id="saved-article-local-related-reads-title">
          <span data-lang="en">{_esc(related_reads.title.en)}</span>
          <span data-lang="zh">{_esc(related_reads.title.zh)}</span>
        </h2>
        <p>
          <span data-lang="en">{_esc(related_reads.dek.en)}</span>
          <span data-lang="zh">{_esc(related_reads.dek.zh)}</span>
        </p>
      </div>
{connection_brief}
{body_html}
    </section>"""


def _saved_article_local_related_read_connection_brief_cards(
    cards: Sequence[RowOneSavedArticleLocalRelatedReadCard],
) -> tuple[RowOneSavedArticleLocalRelatedReadCard, ...]:
    return tuple(
        replace(
            card,
            evidence_bridges=tuple(
                bridge
                for bridge in card.evidence_bridges
                if _safe_saved_article_local_related_read_current_href(bridge.current_href)
                is not None
                and _safe_saved_article_local_related_read_href(
                    card.candidate_story_id,
                    bridge.candidate_href,
                )
                is not None
            ),
        )
        for card in cards
    )


def _render_saved_article_local_related_read_connection_brief(
    brief: RowOneSavedArticleLocalRelatedReadConnectionBrief | None,
) -> str:
    if brief is None:
        return ""
    metrics = "\n".join(
        (
            _render_saved_article_local_related_read_connection_metric(
                LocalizedText(
                    en=_count_label(brief.card_count, "local read", "local reads"),
                    zh=f"{brief.card_count} 篇本地阅读",
                ),
                LocalizedText(en="Next reads", zh="后续阅读"),
            ),
            _render_saved_article_local_related_read_connection_metric(
                LocalizedText(
                    en=_count_label(brief.source_count, "source", "sources"),
                    zh=f"{brief.source_count} 个来源",
                ),
                LocalizedText(en="Sources", zh="来源"),
            ),
            _render_saved_article_local_related_read_connection_metric(
                LocalizedText(
                    en=_count_label(brief.signal_count, "signal", "signals"),
                    zh=f"{brief.signal_count} 个信号",
                ),
                LocalizedText(en="Signals", zh="信号"),
            ),
            _render_saved_article_local_related_read_connection_metric(
                LocalizedText(
                    en=_count_label(
                        brief.evidence_bridge_count,
                        "bridge",
                        "bridges",
                    ),
                    zh=f"{brief.evidence_bridge_count} 条证据连接",
                ),
                LocalizedText(en="Evidence", zh="证据"),
            ),
        )
    )
    tags = _render_saved_article_local_related_read_connection_tags(brief)
    return f"""      <div class="saved-article-local-related-read-connection-brief">
        <div class="saved-article-local-related-read-connection-brief-copy">
          <h3>
            <span data-lang="en">{_esc(brief.title.en)}</span>
            <span data-lang="zh">{_esc(brief.title.zh)}</span>
          </h3>
          <p>
            <span data-lang="en">{_esc(brief.lead.en)}</span>
            <span data-lang="zh">{_esc(brief.lead.zh)}</span>
          </p>
        </div>
        <div class="saved-article-local-related-read-connection-brief-metrics">
{metrics}
        </div>
{tags}
      </div>"""


def _render_saved_article_local_related_read_connection_metric(
    value: LocalizedText,
    label: LocalizedText,
) -> str:
    return f"""          <span>
            <strong>
              <span data-lang="en">{_esc(value.en)}</span>
              <span data-lang="zh">{_esc(value.zh)}</span>
            </strong>
            <span data-lang="en">{_esc(label.en)}</span>
            <span data-lang="zh">{_esc(label.zh)}</span>
          </span>"""


def _render_saved_article_local_related_read_connection_tags(
    brief: RowOneSavedArticleLocalRelatedReadConnectionBrief,
) -> str:
    chips: list[str] = []
    for label in brief.lane_labels:
        chips.append(
            f"""          <span class="saved-article-local-related-read-connection-chip">
            <span data-lang="en">{_esc(label.en)}</span>
            <span data-lang="zh">{_esc(label.zh)}</span>
          </span>"""
        )
    for reference in brief.signal_references:
        if reference.name.strip():
            chips.append(
                f"""          <span class="saved-article-local-related-read-connection-chip">
            <span>{_esc(reference.name)}</span>
            <span>{_esc(reference.label)}</span>
          </span>"""
            )
    for source_name in brief.source_names:
        if source_name.strip():
            chips.append(
                f"""          <span class="saved-article-local-related-read-connection-chip">
            <span>{_esc(source_name)}</span>
          </span>"""
            )
    if not chips:
        return ""
    return (
        '        <div class="saved-article-local-related-read-connection-brief-tags">\n'
        + "\n".join(chips)
        + "\n        </div>"
    )


def _render_saved_article_local_related_read_lanes(
    lanes: Sequence[RowOneSavedArticleLocalRelatedReadLane],
) -> str:
    rendered = [
        lane_html
        for lane in lanes
        if (lane_html := _render_saved_article_local_related_read_lane(lane))
    ]
    if not rendered:
        return ""
    return (
        '      <div class="saved-article-local-related-read-lanes">\n'
        + "\n".join(rendered)
        + "\n      </div>"
    )


def _render_saved_article_local_related_read_lane(
    lane: RowOneSavedArticleLocalRelatedReadLane,
) -> str:
    cards = [
        card_html
        for card in lane.cards
        if (card_html := _render_saved_article_local_related_read_card(card))
    ]
    if not cards:
        return ""
    cards_html = "\n".join(cards)
    lane_key = _esc(lane.key)
    return f"""        <div class="saved-article-local-related-read-lane" data-lane="{lane_key}">
          <div class="saved-article-local-related-read-lane-header">
            <h3>
              <span data-lang="en">{_esc(lane.title.en)}</span>
              <span data-lang="zh">{_esc(lane.title.zh)}</span>
            </h3>
            <p>
              <span data-lang="en">{_esc(lane.dek.en)}</span>
              <span data-lang="zh">{_esc(lane.dek.zh)}</span>
            </p>
          </div>
          <div class="saved-article-local-related-reads-grid">
{cards_html}
          </div>
        </div>"""


def _saved_article_local_related_read_lane_card_count(
    lanes: Sequence[RowOneSavedArticleLocalRelatedReadLane],
) -> int:
    return sum(len(lane.cards) for lane in lanes)


def _render_saved_article_local_related_read_card(
    card: RowOneSavedArticleLocalRelatedReadCard,
) -> str:
    href = _safe_saved_article_local_related_read_href(
        card.candidate_story_id,
        card.href,
    )
    if href is None:
        return ""
    references = _render_saved_article_local_related_read_references(card)
    evidence_bridge = _render_saved_article_local_related_read_evidence_bridge(card)
    return f"""        <article class="saved-article-local-related-read-card">
          <div class="saved-article-local-related-read-meta">
            <span>{_esc(card.source_name)}</span>
            <span>
              <span data-lang="en">{_esc(card.reason.en)}</span>
              <span data-lang="zh">{_esc(card.reason.zh)}</span>
            </span>
          </div>
          <h3>
            <span data-lang="en">{_esc(card.title.en)}</span>
            <span data-lang="zh">{_esc(card.title.zh)}</span>
          </h3>
          <p>
            <span data-lang="en">{_esc(card.excerpt.en)}</span>
            <span data-lang="zh">{_esc(card.excerpt.zh)}</span>
          </p>
{references}
{evidence_bridge}
          <a class="saved-article-local-related-read-action" href="{_esc(href)}">
            <span data-lang="en">Read next locally</span>
            <span data-lang="zh">继续本地阅读</span>
          </a>
        </article>"""


def _render_saved_article_local_related_read_references(
    card: RowOneSavedArticleLocalRelatedReadCard,
) -> str:
    chips = [
        (
            '            <span class="saved-article-local-related-read-reference">'
            f"<span>{_esc(reference.name)}</span>"
            f"<span>{_esc(reference.label)}</span>"
            "</span>"
        )
        for reference in card.references
        if reference.name.strip()
    ]
    if not chips:
        return ""
    return (
        '          <div class="saved-article-local-related-read-references">\n'
        + "\n".join(chips)
        + "\n          </div>"
    )


def _render_saved_article_local_related_read_evidence_bridge(
    card: RowOneSavedArticleLocalRelatedReadCard,
) -> str:
    rows = [
        row
        for bridge in card.evidence_bridges
        if (row := _render_saved_article_local_related_read_evidence_bridge_row(card, bridge))
    ]
    if not rows:
        return ""
    return (
        '          <div class="saved-article-local-related-read-evidence-bridge">\n'
        '            <span class="saved-article-local-related-read-evidence-bridge-label">\n'
        '              <span data-lang="en">Evidence bridge</span>\n'
        '              <span data-lang="zh">证据连接</span>\n'
        "            </span>\n" + "\n".join(rows) + "\n          </div>"
    )


def _render_saved_article_local_related_read_evidence_bridge_row(
    card: RowOneSavedArticleLocalRelatedReadCard,
    bridge: RowOneSavedArticleLocalRelatedReadEvidenceBridge,
) -> str:
    current_href = _safe_saved_article_local_related_read_current_href(bridge.current_href)
    candidate_href = _safe_saved_article_local_related_read_href(
        card.candidate_story_id,
        bridge.candidate_href,
    )
    if current_href is None or candidate_href is None:
        return ""
    return f"""            <div class="saved-article-local-related-read-evidence-bridge-row">
              <span class="saved-article-local-related-read-evidence-bridge-ref">
                <span>{_esc(bridge.reference.name)}</span>
                <span>{_esc(bridge.reference.label)}</span>
              </span>
              <span class="saved-article-local-related-read-evidence-bridge-links">
                <a href="{_esc(current_href)}">
                  <span data-lang="en">{_esc(bridge.current_label.en)}</span>
                  <span data-lang="zh">{_esc(bridge.current_label.zh)}</span>
                </a>
                <span aria-hidden="true">-&gt;</span>
                <a href="{_esc(candidate_href)}">
                  <span data-lang="en">{_esc(bridge.candidate_label.en)}</span>
                  <span data-lang="zh">{_esc(bridge.candidate_label.zh)}</span>
                </a>
              </span>
            </div>"""


def _safe_saved_article_local_related_read_current_href(href: str) -> str | None:
    if not isinstance(href, str):
        return None
    if not href.startswith("#"):
        return None
    fragment = href.removeprefix("#")
    if _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment) is None:
        return None
    return href


def _safe_saved_article_local_related_read_href(story_id: str, href: str) -> str | None:
    if not isinstance(story_id, str) or not isinstance(href, str):
        return None
    if not safe_local_article_story_id(story_id):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if "://" in href or href.startswith(("http:", "https:", "//", "/", ".", "javascript:")):
        return None
    if "/" in href or "\\" in href or ".." in href:
        return None
    page_href, separator, fragment = href.partition("#")
    if not separator or page_href != f"{story_id}.html":
        return None
    if fragment == "local-article-digest":
        return href
    if _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment) is not None:
        return href
    return None


def _render_saved_article_local_section_binder(
    binder: RowOneSavedArticleLocalSectionBinder | None,
) -> str:
    if binder is None:
        return ""
    rows = [
        row_html
        for row in binder.rows
        if (row_html := _render_saved_article_local_section_binder_row(row))
    ]
    unfiled = _render_saved_article_local_section_binder_unfiled(binder.unfiled_paragraphs)
    if not rows and not unfiled:
        return ""
    row_count = _count_label(len(rows), "organized section", "organized sections")
    unfiled_count = _count_label(
        len(binder.unfiled_paragraphs),
        "unfiled paragraph",
        "unfiled paragraphs",
    )
    rows_html = "\n".join(rows)
    return f"""    <section class="saved-article-local-section-binder"
      aria-labelledby="saved-article-local-section-binder-title">
      <div class="saved-article-local-section-binder-header">
        <h2 id="saved-article-local-section-binder-title">
          <span data-lang="en">Saved Article Local Section Binder</span>
          <span data-lang="zh">保存文章栏目索引</span>
        </h2>
        <p>
          <span data-lang="en">A compact index of the organized local sections, cited
          references, and saved paragraphs inside this article.</span>
          <span data-lang="zh">这篇文章内部整理栏目、引用对象与保存段落的紧凑索引。</span>
        </p>
      </div>
      <div class="saved-article-local-section-binder-meta">
        <span>{_esc(binder.source_name)}</span>
        <span>
          <span data-lang="en">{_esc(binder.title.en)}</span>
          <span data-lang="zh">{_esc(binder.title.zh)}</span>
        </span>
        <span>{_esc(row_count)}</span>
        <span>{_esc(unfiled_count)}</span>
      </div>
      <div class="saved-article-local-section-binder-grid">
{rows_html}
{unfiled}
      </div>
    </section>"""


def _render_saved_article_local_section_binder_row(
    row: RowOneSavedArticleLocalSectionBinderRow,
) -> str:
    if _saved_article_local_section_binder_href(row.section_href) is None:
        return ""
    chips = _render_saved_article_local_section_binder_chips(row.item_labels)
    refs = _render_saved_article_local_section_binder_refs(row.references)
    paragraphs = _render_saved_article_local_section_binder_paragraphs(row.paragraphs)
    paragraph_count = _count_label(
        len(row.paragraphs),
        "cited paragraph",
        "cited paragraphs",
    )
    return f"""        <article class="saved-article-local-section-binder-row">
          <div class="saved-article-local-section-binder-meta">
            <span>{_esc(paragraph_count)}</span>
            <span>Section {_esc(str(row.section_position))}</span>
          </div>
          <h3>
            <span data-lang="en">{_esc(row.title.en)}</span>
            <span data-lang="zh">{_esc(row.title.zh)}</span>
          </h3>
          <a href="{_esc(row.section_href)}">
            <span data-lang="en">Jump to organized section</span>
            <span data-lang="zh">跳转到整理栏目</span>
          </a>
{chips}{refs}{paragraphs}
        </article>"""


def _render_saved_article_local_section_binder_chips(
    labels: Sequence[LocalizedText],
) -> str:
    chips = "".join(
        f"""<span>
              <span data-lang="en">{_esc(label.en)}</span>
              <span data-lang="zh">{_esc(label.zh)}</span>
            </span>"""
        for label in labels
        if label.en.strip() or label.zh.strip()
    )
    if not chips:
        return ""
    return f'          <div class="saved-article-local-section-binder-chips">{chips}</div>\n'


def _render_saved_article_local_section_binder_refs(
    references: Sequence[RowOneReference],
) -> str:
    chips = "".join(
        f"<span>{_esc(_saved_article_local_section_binder_ref_label(ref))}</span>"
        for ref in references
        if _saved_article_local_section_binder_ref_label(ref)
    )
    if not chips:
        return ""
    return f'          <div class="saved-article-local-section-binder-refs">{chips}</div>\n'


def _render_saved_article_local_section_binder_paragraphs(
    paragraphs: Sequence[RowOneSavedArticleLocalSectionBinderParagraph],
) -> str:
    links = [
        paragraph_html
        for paragraph in paragraphs
        if (paragraph_html := _render_saved_article_local_section_binder_paragraph(paragraph))
    ]
    if not links:
        return ""
    return (
        '          <div class="saved-article-local-section-binder-paragraphs">\n'
        + "\n".join(links)
        + "\n          </div>\n"
    )


def _render_saved_article_local_section_binder_unfiled(
    paragraphs: Sequence[RowOneSavedArticleLocalSectionBinderParagraph],
) -> str:
    rendered = _render_saved_article_local_section_binder_paragraphs(paragraphs)
    if not rendered:
        return ""
    return f"""        <aside class="saved-article-local-section-binder-unfiled">
          <p>
            <span data-lang="en">Unfiled saved paragraphs</span>
            <span data-lang="zh">未归档保存段落</span>
          </p>
{rendered}
        </aside>"""


def _render_saved_article_local_section_binder_paragraph(
    paragraph: RowOneSavedArticleLocalSectionBinderParagraph,
) -> str:
    href = _saved_article_local_section_binder_href(paragraph.href)
    if href is None:
        return ""
    return f"""            <a href="{_esc(href)}">
              <span data-lang="en">{_esc(paragraph.excerpt.en)}</span>
              <span data-lang="zh">{_esc(paragraph.excerpt.zh)}</span>
            </a>"""


def _saved_article_local_section_binder_ref_label(ref: RowOneReference) -> str:
    parts = [part.strip() for part in (ref.name, ref.type, ref.label) if part.strip()]
    return " / ".join(parts)


def _saved_article_local_section_binder_href(href: str) -> str | None:
    if not isinstance(href, str):
        return None
    if href != href.strip() or not href.startswith("#"):
        return None
    fragment = href.removeprefix("#")
    if _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment) is not None:
        return href
    if _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment) is not None:
        return href
    return None


def _render_saved_article_key_signals(
    key_signals: RowOneSavedArticleKeySignals | None,
) -> str:
    if key_signals is None:
        return ""
    groups = [
        group_html
        for group in key_signals.groups
        if (group_html := _render_saved_article_key_signal_group(group))
    ]
    if not groups:
        return ""
    group_count = _count_label(len(groups), "signal group", "signal groups")
    groups_html = "\n".join(groups)
    return f"""    <section class="saved-article-key-signals"
      aria-labelledby="saved-article-key-signals-title">
      <div class="saved-article-key-signals-header">
        <h2 id="saved-article-key-signals-title">
          <span data-lang="en">{_esc(key_signals.title.en)}</span>
          <span data-lang="zh">{_esc(key_signals.title.zh)}</span>
        </h2>
        <p>
          <span data-lang="en">The article's saved text organized into Why It Matters,
          Brands, Products, People, and Themes before the full read.</span>
          <span data-lang="zh">在阅读全文前，将已保存正文整理为为什么重要、品牌、产品、
          人物与主题信号。</span>
        </p>
      </div>
      <div class="saved-article-key-signals-meta">
        <span>{_esc(key_signals.source_name)}</span>
        <span>{_esc(group_count)}</span>
      </div>
      <div class="saved-article-key-signals-grid">
{groups_html}
      </div>
    </section>"""


def _render_saved_article_key_signal_group(
    group: RowOneSavedArticleKeySignalGroup,
) -> str:
    statement = _render_saved_article_key_signal_statement(group.statement)
    refs = _render_saved_article_key_signal_refs(group.references)
    themes = _render_saved_article_key_signal_themes(group.themes)
    evidence = _render_saved_article_key_signal_evidence(group.evidence)
    if not any((statement, refs, themes, evidence)):
        return ""
    meta = _render_saved_article_key_signal_meta(group)
    return f"""        <article class="saved-article-key-signal">
          <h3>
            <span data-lang="en">{_esc(group.title.en)}</span>
            <span data-lang="zh">{_esc(group.title.zh)}</span>
          </h3>
{meta}{statement}{refs}{themes}{evidence}
        </article>"""


def _render_saved_article_key_signal_meta(
    group: RowOneSavedArticleKeySignalGroup,
) -> str:
    labels = []
    if group.support_count:
        labels.append(_count_label(group.support_count, "support row", "support rows"))
    if group.reference_count:
        labels.append(_count_label(group.reference_count, "reference", "references"))
    if group.theme_count:
        labels.append(_count_label(group.theme_count, "theme", "themes"))
    if group.evidence_count:
        labels.append(_count_label(group.evidence_count, "evidence cue", "evidence cues"))
    if not labels:
        return ""
    chips = "".join(f"<span>{_esc(label)}</span>" for label in labels)
    return f'          <div class="saved-article-key-signals-meta">{chips}</div>\n'


def _render_saved_article_key_signal_statement(statement: LocalizedText | None) -> str:
    if statement is None or not (statement.en.strip() or statement.zh.strip()):
        return ""
    return f"""          <p class="saved-article-key-signal-statement">
            <span data-lang="en">{_esc(statement.en)}</span>
            <span data-lang="zh">{_esc(statement.zh)}</span>
          </p>
"""


def _render_saved_article_key_signal_refs(
    references: Sequence[RowOneSavedArticleKeySignalReference],
) -> str:
    chips = "".join(
        f'<span class="saved-article-key-signal-ref">{_esc(label)}</span>'
        for reference in references
        if (label := _saved_article_key_signal_ref_label(reference))
    )
    if not chips:
        return ""
    return f'          <div class="saved-article-key-signal-refs">{chips}</div>\n'


def _render_saved_article_key_signal_themes(
    themes: Sequence[RowOneSavedArticleKeySignalTheme],
) -> str:
    links = [
        theme_html
        for theme in themes
        if (theme_html := _render_saved_article_key_signal_theme(theme))
    ]
    if not links:
        return ""
    return (
        '          <div class="saved-article-key-signal-themes">\n'
        + "\n".join(links)
        + "\n          </div>\n"
    )


def _render_saved_article_key_signal_theme(
    theme: RowOneSavedArticleKeySignalTheme,
) -> str:
    href = _saved_article_key_signals_href(theme.href)
    if href is None:
        return ""
    return f"""            <a href="{_esc(href)}">
              <span data-lang="en">{_esc(theme.label.en)}</span>
              <span data-lang="zh">{_esc(theme.label.zh)}</span>
            </a>"""


def _render_saved_article_key_signal_evidence(
    evidence: Sequence[RowOneSavedArticleKeySignalEvidence],
) -> str:
    links = [
        evidence_html
        for item in evidence
        if (evidence_html := _render_saved_article_key_signal_evidence_item(item))
    ]
    if not links:
        return ""
    return (
        '          <div class="saved-article-key-signal-evidence">\n'
        + "\n".join(links)
        + "\n          </div>\n"
    )


def _render_saved_article_key_signal_evidence_item(
    evidence: RowOneSavedArticleKeySignalEvidence,
) -> str:
    href = _saved_article_key_signals_href(evidence.href)
    if href is None:
        return ""
    return f"""            <a href="{_esc(href)}">
              <span data-lang="en">{_esc(evidence.excerpt.en)}</span>
              <span data-lang="zh">{_esc(evidence.excerpt.zh)}</span>
            </a>"""


def _saved_article_key_signal_ref_label(
    reference: RowOneSavedArticleKeySignalReference,
) -> str:
    parts = [
        part.strip()
        for part in (reference.name, reference.reference_type, reference.label)
        if part.strip()
    ]
    return " / ".join(parts)


def _saved_article_key_signals_href(href: str) -> str | None:
    if not isinstance(href, str):
        return None
    if href != href.strip() or not href.startswith("#"):
        return None
    fragment = href.removeprefix("#")
    if _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment) is not None:
        return href
    if _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment) is not None:
        return href
    return None


@dataclass(frozen=True)
class _RenderedSavedArticleReadNextCluster:
    html: str
    item_count: int
    source_names: tuple[str, ...]
    evidence_count: int


def _first_saved_article_daily_summary_reading_href(
    library: RowOneSavedArticleLibrary,
    *,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str | None:
    for group in library.groups:
        for entry in group.entries:
            article_page_href = _saved_article_library_entry_article_page_href(
                entry,
                local_article_page_hrefs_by_detail_path,
            )
            if article_page_href is not None:
                return f"{article_page_href}#local-article-digest"
            safe_href = safe_row_one_detail_fragment_href(
                entry.digest_path,
                "local-article-digest",
            )
            if safe_href is not None:
                return _saved_article_library_page_href(safe_href)
    return None


def _render_saved_article_library_source(
    group: RowOneSavedArticleLibrarySourceGroup,
    *,
    snippets_by_detail_path: Mapping[
        str,
        Sequence[RowOneSavedArticleContentOrganizationCard],
    ]
    | None = None,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None = None,
    source_anchor_id: str | None = None,
) -> str:
    cards = "\n".join(
        _render_saved_article_library_card(
            entry,
            snippets_by_detail_path=snippets_by_detail_path,
            local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
        )
        for entry in group.entries
    )
    article_count_en = _count_label(group.article_count, "article", "articles")
    article_count_zh = f"{group.article_count} 篇文章"
    paragraph_count_en = _count_label(
        group.saved_paragraph_count,
        "saved paragraph",
        "saved paragraphs",
    )
    paragraph_count_zh = f"{group.saved_paragraph_count} 个保存段落"
    source_brief = _render_saved_article_source_brief(
        group,
        snippets_by_detail_path=snippets_by_detail_path,
        local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
    )
    source_id_attr = f' id="{_esc(source_anchor_id)}"' if source_anchor_id else ""
    return f"""    <section class="saved-article-library-source"{source_id_attr}>
      <div class="saved-article-library-source-header">
        <h2>{_esc(group.source_name)}</h2>
        <p>
          <span data-lang="en">{_esc(article_count_en)}, {_esc(paragraph_count_en)}</span>
          <span data-lang="zh">{_esc(article_count_zh)}，{_esc(paragraph_count_zh)}</span>
        </p>
      </div>
      {source_brief}
      <div class="saved-article-library-source-grid">{cards}</div>
    </section>"""


def _render_saved_article_library_card(
    entry: RowOneSavedArticleLibraryEntry,
    *,
    snippets_by_detail_path: Mapping[
        str,
        Sequence[RowOneSavedArticleContentOrganizationCard],
    ]
    | None = None,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None = None,
) -> str:
    refs = _render_saved_article_library_refs(entry.references)
    paragraphs = _render_saved_article_library_paragraphs(entry.paragraph_links)
    actions = _render_saved_article_library_actions(
        entry,
        local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
    )
    snippets = _render_saved_article_body_guide(
        _saved_article_library_entry_snippets(entry, snippets_by_detail_path)
    )
    paragraph_count_en = _count_label(
        entry.saved_paragraph_count,
        "saved paragraph",
        "saved paragraphs",
    )
    section_count_en = _count_label(
        entry.organized_section_count,
        "organized section",
        "organized sections",
    )
    card_anchor_id = _saved_article_library_card_anchor_id(entry)
    card_id_attr = f' id="{_esc(card_anchor_id)}"' if card_anchor_id else ""
    return f"""        <article class="saved-article-library-card"{card_id_attr}>
          <div class="saved-article-library-card-meta">
            <span>{_esc(entry.source_name)}</span>
            <span>
              <span data-lang="en">{_esc(entry.section_title.en)}</span>
              <span data-lang="zh">{_esc(entry.section_title.zh)}</span>
            </span>
          </div>
          <h3>
            <span data-lang="en">{_esc(entry.title.en)}</span>
            <span data-lang="zh">{_esc(entry.title.zh)}</span>
          </h3>
          <ul class="saved-article-library-card-counts">
            <li>
              <span data-lang="en">{_esc(paragraph_count_en)}</span>
              <span data-lang="zh">{_esc(f"{entry.saved_paragraph_count} 个保存段落")}</span>
            </li>
            <li>
              <span data-lang="en">{_esc(section_count_en)}</span>
              <span data-lang="zh">{_esc(f"{entry.organized_section_count} 个整理栏目")}</span>
            </li>
            {_render_saved_article_library_body_source_chip(entry)}
          </ul>
          {snippets}
          {refs}
          {paragraphs}
          {actions}
        </article>"""


def _saved_article_library_card_anchor_id(
    entry: RowOneSavedArticleLibraryEntry,
) -> str | None:
    safe_href = safe_row_one_detail_fragment_href(
        entry.digest_path,
        "local-article-digest",
    )
    if safe_href is None:
        return None
    path, _separator, _fragment = safe_href.partition("#")
    safe_path = validated_row_one_detail_relative_path(path)
    if safe_path is None:
        return None
    story_id = safe_path.stem
    if not safe_local_article_story_id(story_id):
        return None
    return f"{_SAVED_ARTICLE_LIBRARY_CARD_PREFIX}{story_id}"


def _saved_article_library_snippets_by_detail_path(
    organization: RowOneSavedArticleContentOrganization | None,
) -> dict[str, tuple[RowOneSavedArticleContentOrganizationCard, ...]]:
    if organization is None:
        return {}
    grouped: dict[str, list[RowOneSavedArticleContentOrganizationCard]] = {}
    seen: dict[str, set[tuple[str, str, str, str]]] = {}
    for group in organization.groups:
        for card in group.cards:
            href = _safe_saved_article_content_organization_href(card.detail_path)
            if href is None:
                continue
            detail_path = _saved_article_library_detail_path_key(href)
            if detail_path is None:
                continue
            if card.paragraph_indices and not _saved_article_body_guide_has_safe_evidence(card):
                continue
            dedupe_key = (
                href,
                " ".join(card.section_label.en.split()).casefold(),
                " ".join(card.lead.en.split()).casefold(),
                " ".join(card.lead.zh.split()).casefold(),
            )
            seen_for_detail = seen.setdefault(detail_path, set())
            if dedupe_key in seen_for_detail:
                continue
            seen_for_detail.add(dedupe_key)
            grouped.setdefault(detail_path, []).append(card)
    return {
        detail_path: tuple(cards[:SAVED_ARTICLE_BODY_GUIDE_ITEMS_PER_CARD])
        for detail_path, cards in grouped.items()
    }


def _saved_article_library_detail_path_key(href: str) -> str | None:
    path, separator, _fragment = href.partition("#")
    if not separator:
        return None
    safe_path = validated_row_one_detail_relative_path(path)
    if safe_path is None:
        return None
    return str(safe_path)


def _saved_article_library_entry_detail_path(
    entry: RowOneSavedArticleLibraryEntry,
) -> str | None:
    for href, fragment in (
        (entry.reader_path, "local-article-reader"),
        (entry.digest_path, "local-article-digest"),
        (entry.evidence_path, "local-article-paragraph-evidence"),
    ):
        safe_href = safe_row_one_detail_fragment_href(href, fragment)
        if safe_href is None:
            continue
        detail_path = _saved_article_library_detail_path_key(safe_href)
        if detail_path is not None:
            return detail_path
    return None


def _saved_article_library_entry_snippets(
    entry: RowOneSavedArticleLibraryEntry,
    snippets_by_detail_path: Mapping[
        str,
        Sequence[RowOneSavedArticleContentOrganizationCard],
    ]
    | None,
) -> Sequence[RowOneSavedArticleContentOrganizationCard]:
    if not snippets_by_detail_path:
        return ()
    detail_path = _saved_article_library_entry_detail_path(entry)
    if detail_path is None:
        return ()
    return snippets_by_detail_path.get(detail_path, ())


def _render_saved_article_source_brief(
    group: RowOneSavedArticleLibrarySourceGroup,
    *,
    snippets_by_detail_path: Mapping[
        str,
        Sequence[RowOneSavedArticleContentOrganizationCard],
    ]
    | None,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str:
    items = _saved_article_source_brief_items(
        group,
        snippets_by_detail_path=snippets_by_detail_path,
        local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
    )
    if not items:
        return ""
    article_count_en = _count_label(group.article_count, "saved article", "saved articles")
    paragraph_count_en = _count_label(
        group.saved_paragraph_count,
        "saved paragraph",
        "saved paragraphs",
    )
    section_count_en = _count_label(
        group.organized_section_count,
        "organized section",
        "organized sections",
    )
    metrics_en = f"{article_count_en} / {paragraph_count_en} / {section_count_en}"
    metrics_zh = (
        f"{group.article_count} 篇保存文章 / "
        f"{group.saved_paragraph_count} 个保存段落 / "
        f"{group.organized_section_count} 个整理栏目"
    )
    return (
        '<div class="saved-article-source-brief" aria-label="Saved article source brief">'
        '<div class="saved-article-source-brief-header">'
        "<strong>"
        '<span data-lang="en">Source Brief</span>'
        '<span data-lang="zh">来源简报</span>'
        "</strong>"
        '<span class="saved-article-source-brief-metrics">'
        f'<span data-lang="en">{_esc(metrics_en)}</span>'
        f'<span data-lang="zh">{_esc(metrics_zh)}</span>'
        "</span>"
        "</div>"
        '<ul class="saved-article-source-brief-list">' + "".join(items) + "</ul></div>"
    )


def _saved_article_source_brief_items(
    group: RowOneSavedArticleLibrarySourceGroup,
    *,
    snippets_by_detail_path: Mapping[
        str,
        Sequence[RowOneSavedArticleContentOrganizationCard],
    ]
    | None,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> list[str]:
    items: list[str] = []
    seen: set[tuple[str, str, str, str, str]] = set()
    pending_by_entry = [
        _saved_article_source_brief_entry_items(
            entry,
            snippets_by_detail_path=snippets_by_detail_path,
            local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
        )
        for entry in group.entries
    ]
    max_items_per_entry = max((len(entry_items) for entry_items in pending_by_entry), default=0)
    for item_index in range(max_items_per_entry):
        for entry_items in pending_by_entry:
            if item_index >= len(entry_items):
                continue
            item = entry_items[item_index]
            dedupe_key = _saved_article_source_brief_item_key(item)
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            items.append(_render_saved_article_source_brief_item(*item))
            if len(items) >= SAVED_ARTICLE_SOURCE_BRIEF_ITEMS_PER_SOURCE:
                return items
    return items


def _saved_article_source_brief_entry_items(
    entry: RowOneSavedArticleLibraryEntry,
    *,
    snippets_by_detail_path: Mapping[
        str,
        Sequence[RowOneSavedArticleContentOrganizationCard],
    ]
    | None,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> list[tuple[LocalizedText, LocalizedText, str]]:
    items: list[tuple[LocalizedText, LocalizedText, str]] = []
    for card in _saved_article_library_entry_snippets(entry, snippets_by_detail_path):
        href = _safe_saved_article_content_organization_href(card.detail_path)
        if href is None:
            continue
        href = _prefixed_saved_article_content_organization_href(href, "../")
        label = card.section_label
        body = LocalizedText(
            en=_local_article_digest_excerpt(card.lead.en),
            zh=_local_article_digest_excerpt(card.lead.zh),
        )
        if _saved_article_source_brief_text_is_empty(label, body):
            continue
        items.append((label, body, href))
    if items:
        return items

    fallback_href = _saved_article_source_brief_entry_href(
        entry,
        local_article_page_hrefs_by_detail_path,
    )
    if fallback_href is None:
        return []
    label = entry.section_title
    body = LocalizedText(
        en=_local_article_digest_excerpt(entry.title.en),
        zh=_local_article_digest_excerpt(entry.title.zh),
    )
    if _saved_article_source_brief_text_is_empty(label, body):
        return []
    return [(label, body, fallback_href)]


def _saved_article_source_brief_entry_href(
    entry: RowOneSavedArticleLibraryEntry,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str | None:
    article_page_href = _saved_article_library_entry_article_page_href(
        entry,
        local_article_page_hrefs_by_detail_path,
    )
    if article_page_href is not None:
        return f"{article_page_href}#local-article-digest"
    safe_href = safe_row_one_detail_fragment_href(
        entry.digest_path,
        "local-article-digest",
    )
    if safe_href is None:
        return None
    return _saved_article_library_page_href(safe_href)


def _saved_article_source_brief_text_is_empty(
    label: LocalizedText,
    body: LocalizedText,
) -> bool:
    del label
    return not (" ".join(str(body.en).split()) or " ".join(str(body.zh).split()))


def _saved_article_source_brief_item_key(
    item: tuple[LocalizedText, LocalizedText, str],
) -> tuple[str, str, str, str, str]:
    label, body, href = item
    return (
        href,
        " ".join(str(label.en).split()).casefold(),
        " ".join(str(label.zh).split()).casefold(),
        " ".join(str(body.en).split()).casefold(),
        " ".join(str(body.zh).split()).casefold(),
    )


def _render_saved_article_source_brief_item(
    label: LocalizedText,
    body: LocalizedText,
    href: str,
) -> str:
    return f"""<li class="saved-article-source-brief-item">
          <p class="saved-article-source-brief-label">
            <span data-lang="en">{_esc(label.en)}</span>
            <span data-lang="zh">{_esc(label.zh)}</span>
          </p>
          <p class="saved-article-source-brief-body">
            <span data-lang="en">{_esc(body.en)}</span>
            <span data-lang="zh">{_esc(body.zh)}</span>
          </p>
          <a class="saved-article-source-brief-link" href="{_esc(href)}">
            <span data-lang="en">Open contribution</span>
            <span data-lang="zh">打开来源贡献</span>
          </a>
        </li>"""


def _saved_article_body_guide_has_safe_evidence(
    card: RowOneSavedArticleContentOrganizationCard,
) -> bool:
    return any(
        _safe_saved_article_content_organization_evidence_href(
            card.detail_path,
            paragraph_index,
        )
        is not None
        for paragraph_index in card.paragraph_indices
    )


def _render_saved_article_body_guide(
    cards: Sequence[RowOneSavedArticleContentOrganizationCard],
) -> str:
    # Snippets are deduped and capped while the per-detail lookup is built.
    items = [_render_saved_article_body_guide_item(card) for card in cards]
    items = [item for item in items if item]
    if not items:
        return ""
    return (
        '<div class="saved-article-body-guide" aria-label="Saved article body guide">'
        '<div class="saved-article-body-guide-header">'
        '<span data-lang="en">What this article says</span>'
        '<span data-lang="zh">正文导读</span>'
        "</div>"
        '<ul class="saved-article-body-guide-list">' + "".join(items) + "</ul></div>"
    )


def _render_saved_article_body_guide_item(
    card: RowOneSavedArticleContentOrganizationCard,
) -> str:
    href = _safe_saved_article_content_organization_href(card.detail_path)
    if href is None:
        return ""
    href = _prefixed_saved_article_content_organization_href(href, "../")
    evidence = _render_saved_article_content_organization_evidence(
        card,
        href_prefix="../",
    )
    if card.paragraph_indices and not evidence:
        return ""
    # The evidence helper returns its own display-contents wrapper; this span
    # provides a library-card hook without changing shared evidence markup.
    evidence_block = (
        f'\n              <span class="saved-article-body-guide-evidence">{evidence}</span>'
        if evidence
        else ""
    )
    return f"""<li class="saved-article-body-guide-item">
              <p class="saved-article-body-guide-label">
                <span data-lang="en">{_esc(card.section_label.en)}</span>
                <span data-lang="zh">{_esc(card.section_label.zh)}</span>
              </p>
              <p class="saved-article-body-guide-body">
                <span data-lang="en">{_esc(_local_article_digest_excerpt(card.lead.en))}</span>
                <span data-lang="zh">{_esc(_local_article_digest_excerpt(card.lead.zh))}</span>
              </p>
              <a class="saved-article-body-guide-link" href="{_esc(href)}">
                <span data-lang="en">Open organized section</span>
                <span data-lang="zh">打开整理栏目</span>
              </a>{evidence_block}
            </li>"""


def _render_saved_article_reading_paths(
    reading_paths: RowOneSavedArticleReadingPaths | None,
    *,
    section_id: str | None = None,
) -> str:
    if reading_paths is None or not reading_paths.paths:
        return ""
    cards = [_render_saved_article_reading_path(path) for path in reading_paths.paths]
    cards = [card for card in cards if card]
    if not cards:
        return ""
    id_attr = f' id="{_esc(section_id)}"' if section_id else ""
    return f"""<section class="saved-article-reading-paths"{id_attr}
  aria-label="Saved article reading paths">
  <div class="saved-article-reading-paths-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Saved Article Reading Paths</span>
        <span data-lang="zh">保存文章阅读路径</span>
      </p>
      <h2>
        <span data-lang="en">Saved Article Reading Paths</span>
        <span data-lang="zh">保存文章阅读路径</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">Follow edited routes through today's saved local fashion text.</span>
      <span data-lang="zh">沿着编辑整理的路径阅读今天保存的本地时尚正文。</span>
    </p>
  </div>
  <div class="saved-article-reading-paths-grid">{"".join(cards)}</div>
</section>"""


def _render_saved_article_theme_digest(
    digest: RowOneSavedArticleThemeDigest | None,
    *,
    section_id: str | None = None,
) -> str:
    if digest is None or not digest.themes:
        return ""
    cards = [_render_saved_article_theme_digest_theme(theme) for theme in digest.themes]
    cards = [card for card in cards if card]
    if not cards:
        return ""
    theme_count_label = _count_label(digest.theme_count, "theme", "themes")
    item_count_label = _count_label(digest.item_count, "local lead", "local leads")
    source_count_label = _count_label(digest.source_count, "source", "sources")
    metrics = (
        "<li>"
        f'<span data-lang="en">{_esc(theme_count_label)}</span>'
        f'<span data-lang="zh">{_esc(f"{digest.theme_count} 个主题")}</span>'
        "</li>"
        "<li>"
        f'<span data-lang="en">{_esc(item_count_label)}</span>'
        f'<span data-lang="zh">{_esc(f"{digest.item_count} 条本地线索")}</span>'
        "</li>"
        "<li>"
        f'<span data-lang="en">{_esc(source_count_label)}</span>'
        f'<span data-lang="zh">{_esc(f"{digest.source_count} 个来源")}</span>'
        "</li>"
    )
    id_attr = f' id="{_esc(section_id)}"' if section_id else ""
    return f"""<section class="saved-article-theme-digest"{id_attr}
  aria-label="Saved article theme digest">
  <div class="saved-article-theme-digest-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Saved Article Theme Digest</span>
        <span data-lang="zh">保存文章主题简报</span>
      </p>
      <h2>
        <span data-lang="en">Saved Article Theme Digest</span>
        <span data-lang="zh">保存文章主题简报</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">Recurring themes from today's saved local fashion text.</span>
      <span data-lang="zh">从今天本地保存时尚正文中整理出的重复主题。</span>
    </p>
  </div>
  <ul class="saved-article-theme-digest-metrics">{metrics}</ul>
  <div class="saved-article-theme-digest-grid">{"".join(cards)}</div>
</section>"""


def _render_saved_article_theme_digest_theme(
    theme: RowOneSavedArticleThemeDigestTheme,
) -> str:
    items = [_render_saved_article_theme_digest_item(item) for item in theme.items]
    items = [item for item in items if item]
    if not items:
        return ""
    return f"""    <article class="saved-article-theme-digest-card">
      <div class="saved-article-theme-digest-card-header">
        <p class="saved-article-theme-digest-card-meta">
          <span data-lang="en">{_esc(_count_label(len(items), "lead", "leads"))}</span>
          <span data-lang="zh">{_esc(f"{len(items)} 条线索")}</span>
          <span data-lang="en">{_esc(_count_label(theme.source_count, "source", "sources"))}</span>
          <span data-lang="zh">{_esc(f"{theme.source_count} 个来源")}</span>
        </p>
        <h3>
          <span data-lang="en">{_esc(theme.title.en)}</span>
          <span data-lang="zh">{_esc(theme.title.zh)}</span>
        </h3>
        <p>
          <span data-lang="en">{_esc(theme.dek.en)}</span>
          <span data-lang="zh">{_esc(theme.dek.zh)}</span>
        </p>
      </div>
      <ol class="saved-article-theme-digest-items">{"".join(items)}</ol>
    </article>"""


def _render_saved_article_theme_digest_item(
    item: RowOneSavedArticleThemeDigestItem,
) -> str:
    href = _safe_saved_article_content_organization_href(item.detail_path)
    if href is None:
        return ""
    href = _prefixed_saved_article_content_organization_href(href, "../")
    refs = "".join(
        '<span class="saved-article-theme-digest-ref">'
        f"<span>{_esc(ref.name)}</span>"
        f"<span>{_esc(ref.label.strip() or ref.type)}</span>"
        "</span>"
        for ref in item.references[:LOCAL_ARTICLE_DIGEST_MAX_REFERENCES]
        if ref.name.strip()
    )
    refs_block = (
        f'\n          <div class="saved-article-theme-digest-refs">{refs}</div>' if refs else ""
    )
    evidence = _render_saved_article_theme_digest_evidence(item)
    evidence_block = (
        f'\n          <div class="saved-article-theme-digest-evidence">{evidence}</div>'
        if evidence
        else ""
    )
    return f"""        <li class="saved-article-theme-digest-item">
          <p class="saved-article-theme-digest-item-meta">
            <span>{_esc(item.source_name)}</span>
            <span data-lang="en">{_esc(item.section_label.en)}</span>
            <span data-lang="zh">{_esc(item.section_label.zh)}</span>
          </p>
          <h4>
            <span data-lang="en">{_esc(item.title.en)}</span>
            <span data-lang="zh">{_esc(item.title.zh)}</span>
          </h4>
          <p class="saved-article-theme-digest-lead">
            <span data-lang="en">{_esc(_local_article_digest_excerpt(item.lead.en))}</span>
            <span data-lang="zh">{_esc(_local_article_digest_excerpt(item.lead.zh))}</span>
          </p>{refs_block}
          <div class="saved-article-theme-digest-actions">
            <a class="saved-article-theme-digest-link" href="{_esc(href)}">
              <span data-lang="en">Open theme section</span>
              <span data-lang="zh">打开主题栏目</span>
            </a>
          </div>{evidence_block}
        </li>"""


def _render_saved_article_theme_digest_evidence(
    item: RowOneSavedArticleThemeDigestItem,
) -> str:
    card = RowOneSavedArticleContentOrganizationCard(
        title=item.title,
        source_name=item.source_name,
        section_title=item.section_title,
        section_label=item.section_label,
        lead=item.lead,
        detail_path=item.detail_path,
        paragraph_indices=item.paragraph_indices,
        references=item.references,
    )
    return _render_saved_article_content_organization_evidence(card, href_prefix="../")


def _render_saved_article_reference_atlas(
    atlas: RowOneSavedArticleReferenceAtlas | None,
    *,
    section_id: str | None = None,
) -> str:
    if atlas is None or not atlas.buckets:
        return ""
    buckets = [_render_saved_article_reference_atlas_bucket(bucket) for bucket in atlas.buckets]
    buckets = [bucket for bucket in buckets if bucket]
    if not buckets:
        return ""
    reference_count_label = _count_label(atlas.reference_count, "reference", "references")
    support_count_label = _count_label(atlas.support_count, "support", "supports")
    source_count_label = _count_label(atlas.source_count, "source", "sources")
    metrics = (
        "<li>"
        f'<span data-lang="en">{_esc(reference_count_label)}</span>'
        f'<span data-lang="zh">{_esc(f"{atlas.reference_count} 个引用")}</span>'
        "</li>"
        "<li>"
        f'<span data-lang="en">{_esc(support_count_label)}</span>'
        f'<span data-lang="zh">{_esc(f"{atlas.support_count} 条支撑")}</span>'
        "</li>"
        "<li>"
        f'<span data-lang="en">{_esc(source_count_label)}</span>'
        f'<span data-lang="zh">{_esc(f"{atlas.source_count} 个来源")}</span>'
        "</li>"
    )
    intro_en = (
        "Entities and items already referenced inside today's saved local article organization."
    )
    id_attr = f' id="{_esc(section_id)}"' if section_id else ""
    return f"""<section class="saved-article-reference-atlas"{id_attr}
  aria-label="Saved article reference atlas">
  <div class="saved-article-reference-atlas-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Saved Article Reference Atlas</span>
        <span data-lang="zh">保存文章引用图谱</span>
      </p>
      <h2>
        <span data-lang="en">Saved Article Reference Atlas</span>
        <span data-lang="zh">保存文章引用图谱</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">{_esc(intro_en)}</span>
      <span data-lang="zh">从今天本地保存文章整理中汇总已经出现的实体与单品引用。</span>
    </p>
  </div>
  <ul class="saved-article-reference-atlas-metrics">{metrics}</ul>
  <div class="saved-article-reference-atlas-grid">{"".join(buckets)}</div>
</section>"""


def _render_saved_article_reference_atlas_bucket(
    bucket: RowOneSavedArticleReferenceAtlasBucket,
) -> str:
    entries = [_render_saved_article_reference_atlas_entry(entry) for entry in bucket.references]
    entries = [entry for entry in entries if entry]
    if not entries:
        return ""
    reference_count_en = _count_label(bucket.reference_count, "reference", "references")
    support_count_en = _count_label(bucket.support_count, "support", "supports")
    source_count_en = _count_label(bucket.source_count, "source", "sources")
    return f"""    <article class="saved-article-reference-atlas-bucket">
      <div class="saved-article-reference-atlas-bucket-header">
        <p class="saved-article-reference-atlas-entry-meta">
          <span data-lang="en">{_esc(reference_count_en)}</span>
          <span data-lang="zh">{_esc(f"{bucket.reference_count} 个引用")}</span>
          <span data-lang="en">{_esc(support_count_en)}</span>
          <span data-lang="zh">{_esc(f"{bucket.support_count} 条支撑")}</span>
          <span data-lang="en">{_esc(source_count_en)}</span>
          <span data-lang="zh">{_esc(f"{bucket.source_count} 个来源")}</span>
        </p>
        <h3>
          <span data-lang="en">{_esc(bucket.title.en)}</span>
          <span data-lang="zh">{_esc(bucket.title.zh)}</span>
        </h3>
        <p>
          <span data-lang="en">{_esc(bucket.dek.en)}</span>
          <span data-lang="zh">{_esc(bucket.dek.zh)}</span>
        </p>
      </div>
      <ol class="saved-article-reference-atlas-list">{"".join(entries)}</ol>
    </article>"""


def _render_saved_article_reference_atlas_entry(
    entry: RowOneSavedArticleReferenceAtlasEntry,
) -> str:
    supports = [
        _render_saved_article_reference_atlas_support(support) for support in entry.supports
    ]
    supports = [support for support in supports if support]
    if not supports:
        return ""
    label = entry.label.strip() or entry.reference_type.strip()
    ref_chip = (
        f'<span class="saved-article-reference-atlas-ref"><span>{_esc(label)}</span></span>'
        if label
        else ""
    )
    support_count_en = _count_label(entry.support_count, "support", "supports")
    source_count_en = _count_label(entry.source_count, "source", "sources")
    return f"""        <li class="saved-article-reference-atlas-entry">
          <p class="saved-article-reference-atlas-entry-meta">
            <span data-lang="en">{_esc(support_count_en)}</span>
            <span data-lang="zh">{_esc(f"{entry.support_count} 条支撑")}</span>
            <span data-lang="en">{_esc(source_count_en)}</span>
            <span data-lang="zh">{_esc(f"{entry.source_count} 个来源")}</span>
          </p>
          <h4>{_esc(entry.name)}</h4>
          {ref_chip}
          {"".join(supports)}
        </li>"""


def _render_saved_article_reference_atlas_support(
    support: RowOneSavedArticleReferenceAtlasSupport,
) -> str:
    href = _safe_saved_article_content_organization_href(support.detail_path)
    if href is None:
        return ""
    href = _prefixed_saved_article_content_organization_href(href, "../")
    evidence = _render_saved_article_reference_atlas_evidence(support)
    evidence_block = (
        f'\n            <div class="saved-article-reference-atlas-evidence">{evidence}</div>'
        if evidence
        else ""
    )
    return f"""          <article class="saved-article-reference-atlas-support">
            <p class="saved-article-reference-atlas-support-meta">
              <span>{_esc(support.source_name)}</span>
              <span data-lang="en">{_esc(support.section_label.en)}</span>
              <span data-lang="zh">{_esc(support.section_label.zh)}</span>
            </p>
            <strong>
              <span data-lang="en">{_esc(support.title.en)}</span>
              <span data-lang="zh">{_esc(support.title.zh)}</span>
            </strong>
            <p class="saved-article-reference-atlas-lead">
              <span data-lang="en">{_esc(_local_article_digest_excerpt(support.lead.en))}</span>
              <span data-lang="zh">{_esc(_local_article_digest_excerpt(support.lead.zh))}</span>
            </p>
            <div class="saved-article-reference-atlas-actions">
              <a class="saved-article-reference-atlas-link" href="{_esc(href)}">
                <span data-lang="en">Open organized section</span>
                <span data-lang="zh">打开整理栏目</span>
              </a>
            </div>{evidence_block}
          </article>"""


def _render_saved_article_reference_atlas_evidence(
    support: RowOneSavedArticleReferenceAtlasSupport,
) -> str:
    card = RowOneSavedArticleContentOrganizationCard(
        title=support.title,
        source_name=support.source_name,
        section_title=support.section_title,
        section_label=support.section_label,
        lead=support.lead,
        detail_path=support.detail_path,
        paragraph_indices=support.paragraph_indices,
        references=(),
    )
    return _render_saved_article_content_organization_evidence(card, href_prefix="../")


def _render_saved_article_reading_path(path: RowOneSavedArticleReadingPath) -> str:
    steps: list[str] = []
    start_href = None
    for step in path.steps:
        safe_href = _safe_saved_article_content_organization_href(step.detail_path)
        if safe_href is None:
            continue
        if start_href is None:
            start_href = safe_href
        rendered_step = _render_saved_article_reading_path_step(len(steps) + 1, step)
        if rendered_step:
            steps.append(rendered_step)
    if not steps:
        return ""
    start_link = ""
    if start_href is not None:
        start_href = _prefixed_saved_article_content_organization_href(start_href, "../")
        start_link = f"""      <a class="saved-article-reading-path-link" href="{_esc(start_href)}">
        <span data-lang="en">Start path</span>
        <span data-lang="zh">开始阅读</span>
      </a>"""
    rendered_step_count = len(steps)
    return f"""    <article class="saved-article-reading-path-card">
      <div class="saved-article-reading-path-card-header">
        <p class="saved-article-reading-path-count">
          <span data-lang="en">{_esc(_count_label(rendered_step_count, "step", "steps"))}</span>
          <span data-lang="zh">{_esc(f"{rendered_step_count} 个步骤")}</span>
        </p>
        <h3>
          <span data-lang="en">{_esc(path.title.en)}</span>
          <span data-lang="zh">{_esc(path.title.zh)}</span>
        </h3>
        <p>
          <span data-lang="en">{_esc(path.dek.en)}</span>
          <span data-lang="zh">{_esc(path.dek.zh)}</span>
        </p>
      </div>
      <ol class="saved-article-reading-path-steps">{"".join(steps)}</ol>
{start_link}
    </article>"""


def _render_saved_article_reading_path_step(
    index: int,
    step: RowOneSavedArticleReadingPathStep,
) -> str:
    href = _safe_saved_article_content_organization_href(step.detail_path)
    if href is None:
        return ""
    href = _prefixed_saved_article_content_organization_href(href, "../")
    evidence = _render_saved_article_reading_path_evidence(step)
    evidence_block = (
        f'\n          <span class="saved-article-reading-path-evidence">{evidence}</span>'
        if evidence
        else ""
    )
    return f"""        <li class="saved-article-reading-path-step">
          <a class="saved-article-reading-path-step-link" href="{_esc(href)}">
            <span class="saved-article-reading-path-step-number">{_esc(str(index))}</span>
            <span class="saved-article-reading-path-step-copy">
              <span class="saved-article-reading-path-step-meta">
                <span>{_esc(step.source_name)}</span>
                <span data-lang="en">{_esc(step.section_label.en)}</span>
                <span data-lang="zh">{_esc(step.section_label.zh)}</span>
              </span>
              <strong>
                <span data-lang="en">{_esc(step.title.en)}</span>
                <span data-lang="zh">{_esc(step.title.zh)}</span>
              </strong>
              <span class="saved-article-reading-path-step-lead">
                <span data-lang="en">{_esc(_local_article_digest_excerpt(step.lead.en))}</span>
                <span data-lang="zh">{_esc(_local_article_digest_excerpt(step.lead.zh))}</span>
              </span>
            </span>
          </a>{evidence_block}
        </li>"""


def _render_saved_article_reading_path_evidence(
    step: RowOneSavedArticleReadingPathStep,
) -> str:
    card = RowOneSavedArticleContentOrganizationCard(
        title=step.title,
        source_name=step.source_name,
        section_title=step.section_title,
        section_label=step.section_label,
        lead=step.lead,
        detail_path=step.detail_path,
        paragraph_indices=step.paragraph_indices,
        references=step.references,
    )
    return _render_saved_article_content_organization_evidence(card, href_prefix="../")


def _render_saved_article_evidence_board(
    evidence_board: RowOneSavedArticleEvidenceBoard | None,
    *,
    section_id: str | None = None,
) -> str:
    if evidence_board is None or not evidence_board.groups:
        return ""
    groups = [_render_saved_article_evidence_board_group(group) for group in evidence_board.groups]
    groups = [group for group in groups if group]
    if not groups:
        return ""
    group_count_label = _count_label(evidence_board.group_count, "group", "groups")
    card_count_label = _count_label(evidence_board.card_count, "paragraph card", "paragraph cards")
    source_count_label = _count_label(evidence_board.source_count, "source", "sources")
    metrics = (
        "<li>"
        f'<span data-lang="en">{_esc(group_count_label)}</span>'
        f'<span data-lang="zh">{_esc(f"{evidence_board.group_count} 个分组")}</span>'
        "</li>"
        "<li>"
        f'<span data-lang="en">{_esc(card_count_label)}</span>'
        f'<span data-lang="zh">{_esc(f"{evidence_board.card_count} 张段落卡片")}</span>'
        "</li>"
        "<li>"
        f'<span data-lang="en">{_esc(source_count_label)}</span>'
        f'<span data-lang="zh">{_esc(f"{evidence_board.source_count} 个来源")}</span>'
        "</li>"
    )
    id_attr = f' id="{_esc(section_id)}"' if section_id else ""
    return f"""<section class="saved-article-evidence-board"{id_attr}
  aria-label="Saved article paragraph evidence board">
  <div class="saved-article-evidence-board-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Saved Article Paragraph Evidence Board</span>
        <span data-lang="zh">保存文章段落证据板</span>
      </p>
      <h2>
        <span data-lang="en">Saved Article Paragraph Evidence Board</span>
        <span data-lang="zh">保存文章段落证据板</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">Capped local excerpts that point back to saved article paragraphs.</span>
      <span data-lang="zh">限长展示的本地摘录，并回链到已保存文章段落。</span>
    </p>
  </div>
  <ul class="saved-article-evidence-board-metrics">{metrics}</ul>
  <div class="saved-article-evidence-board-grid">{"".join(groups)}</div>
</section>"""


def _render_saved_article_evidence_board_group(
    group: RowOneSavedArticleEvidenceBoardGroup,
) -> str:
    cards = [_render_saved_article_evidence_board_card(card) for card in group.cards]
    cards = [card for card in cards if card]
    if not cards:
        return ""
    rendered_card_count = len(cards)
    return f"""    <article class="saved-article-evidence-board-group">
      <div class="saved-article-evidence-board-group-header">
        <p class="saved-article-evidence-board-card-meta">
          <span data-lang="en">{_esc(_count_label(rendered_card_count, "card", "cards"))}</span>
          <span data-lang="zh">{_esc(f"{rendered_card_count} 张卡片")}</span>
          <span data-lang="en">{_esc(_count_label(group.source_count, "source", "sources"))}</span>
          <span data-lang="zh">{_esc(f"{group.source_count} 个来源")}</span>
        </p>
        <h3>
          <span data-lang="en">{_esc(group.title.en)}</span>
          <span data-lang="zh">{_esc(group.title.zh)}</span>
        </h3>
        <p>
          <span data-lang="en">{_esc(group.dek.en)}</span>
          <span data-lang="zh">{_esc(group.dek.zh)}</span>
        </p>
      </div>
      <div class="saved-article-evidence-board-cards">{"".join(cards)}</div>
    </article>"""


def _render_saved_article_evidence_board_card(
    card: RowOneSavedArticleEvidenceBoardCard,
) -> str:
    href = _safe_saved_article_evidence_board_href(card.href)
    if href is None:
        return ""
    href = _saved_article_library_page_href(href)
    refs = "".join(
        '<span class="saved-article-evidence-board-ref">'
        f"<span>{_esc(ref.name)}</span>"
        f"<span>{_esc(ref.label.strip() or ref.type)}</span>"
        "</span>"
        for ref in card.references
        if ref.name.strip()
    )
    refs_block = (
        f'\n        <div class="saved-article-evidence-board-refs">{refs}</div>' if refs else ""
    )
    paragraph_label = str(card.paragraph_number)
    return f"""        <article class="saved-article-evidence-board-card">
          <p class="saved-article-evidence-board-card-meta">
            <span>{_esc(card.source_name)}</span>
            <span data-lang="en">{_esc(card.section_label.en)}</span>
            <span data-lang="zh">{_esc(card.section_label.zh)}</span>
          </p>
          <h4>
            <span data-lang="en">{_esc(card.title.en)}</span>
            <span data-lang="zh">{_esc(card.title.zh)}</span>
          </h4>
          <p class="saved-article-evidence-board-paragraph">
            <span data-lang="en">Paragraph {_esc(paragraph_label)}</span>
            <span data-lang="zh">第 {_esc(paragraph_label)} 段</span>
          </p>
          <p class="saved-article-evidence-board-excerpt">
            <span data-lang="en">{_esc(card.excerpt.en)}</span>
            <span data-lang="zh">{_esc(card.excerpt.zh)}</span>
          </p>{refs_block}
          <div class="saved-article-evidence-board-actions">
            <a class="saved-article-evidence-board-link" href="{_esc(href)}">
              <span data-lang="en">Open saved paragraph</span>
              <span data-lang="zh">打开保存段落</span>
            </a>
          </div>
        </article>"""


def _safe_saved_article_evidence_board_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    path, separator, fragment = href.partition("#")
    if not separator:
        return None
    safe_path = validated_row_one_detail_relative_path(path)
    if safe_path is None:
        return None
    if _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment) is None:
        return None
    return f"{safe_path}#{fragment}"


def _saved_article_library_body_source_label(body_source: str) -> str:
    if body_source == "summary_fallback":
        return "ROW ONE summary fallback"
    if body_source == "skipped":
        return "Skipped"
    return "Extracted article text"


def _render_saved_article_library_body_source_chip(
    entry: RowOneSavedArticleLibraryEntry,
) -> str:
    return (
        '<li class="saved-article-library-text-source">'
        "<span>"
        '<span data-lang="en">Text source</span>'
        '<span data-lang="zh">正文来源</span>'
        "</span>"
        f"<span>{_esc(_saved_article_library_body_source_label(entry.body_source))}</span>"
        "</li>"
    )


def _render_saved_article_library_refs(refs: Sequence[RowOneReference]) -> str:
    if not refs:
        return ""
    chips = "".join(
        '<span class="saved-article-library-ref">'
        f"<span>{_esc(ref.name)}</span>"
        f"<span>{_esc(ref.label.strip() or ref.type)}</span>"
        "</span>"
        for ref in refs
    )
    return f"""<div class="saved-article-library-refs" aria-label="Article references">
            {chips}
          </div>"""


def _render_saved_article_library_paragraphs(
    paragraph_links: Sequence[RowOneSavedArticleLibraryParagraphLink],
) -> str:
    links = []
    for paragraph_link in paragraph_links:
        href = _safe_saved_article_library_paragraph_href(paragraph_link.href)
        if href is None:
            continue
        links.append(
            f"""<a href="{_esc(_saved_article_library_page_href(href))}">
              <span data-lang="en">{_esc(paragraph_link.label.en)}</span>
              <span data-lang="zh">{_esc(paragraph_link.label.zh)}</span>
            </a>"""
        )
    if not links:
        return ""
    return (
        '<div class="saved-article-library-paragraphs" aria-label="Saved paragraph links">'
        + "".join(links)
        + "</div>"
    )


def _render_saved_article_library_actions(
    entry: RowOneSavedArticleLibraryEntry,
    *,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None = None,
) -> str:
    actions = [
        (
            entry.digest_path,
            "local-article-digest",
            "Open digest",
            "打开整理摘要",
        ),
    ]
    if entry.paragraph_links:
        actions.append(
            (
                entry.evidence_path,
                "local-article-paragraph-evidence",
                "Open evidence",
                "打开段落线索",
            )
        )
    rendered = []
    article_page_href = _saved_article_library_entry_article_page_href(
        entry,
        local_article_page_hrefs_by_detail_path,
    )
    if article_page_href is not None:
        rendered.append(
            f"""<a class="saved-article-library-primary-action" href="{_esc(article_page_href)}">
              <span data-lang="en">Read local article</span>
              <span data-lang="zh">阅读本地正文</span>
            </a>"""
        )
    else:
        actions.insert(
            0,
            (
                entry.reader_path,
                "local-article-reader",
                "Read local article",
                "阅读本地正文",
            ),
        )
    for href, fragment, label_en, label_zh in actions:
        safe_href = safe_row_one_detail_fragment_href(href, fragment)
        if safe_href is None:
            continue
        rendered.append(
            f"""<a href="{_esc(_saved_article_library_page_href(safe_href))}">
              <span data-lang="en">{_esc(label_en)}</span>
              <span data-lang="zh">{_esc(label_zh)}</span>
            </a>"""
        )
    if not rendered:
        return ""
    return '<div class="saved-article-library-actions">' + "".join(rendered) + "</div>"


def _saved_article_library_entry_article_page_href(
    entry: RowOneSavedArticleLibraryEntry,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str | None:
    if not local_article_page_hrefs_by_detail_path:
        return None
    detail_path = _saved_article_library_entry_detail_path(entry)
    if detail_path is None:
        return None
    href = local_article_page_hrefs_by_detail_path.get(detail_path)
    if href is None:
        return None
    if href.startswith(".") or "/" in href or not href.endswith(".html"):
        return None
    if not safe_local_article_story_id(href.removesuffix(".html")):
        return None
    return href


def _safe_saved_article_library_paragraph_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    path, separator, fragment = href.partition("#")
    if not separator:
        return None
    safe_path = validated_row_one_detail_relative_path(path)
    if safe_path is None:
        return None
    if _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment) is None:
        return None
    return f"{safe_path}#{fragment}"


def _saved_article_library_page_href(href: str) -> str:
    return f"../{href}"


def _render_saved_article_signal_facets(
    facets: RowOneSavedArticleSignalFacets | None,
    *,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str:
    if facets is None or not facets.rows:
        return ""
    rows = "\n".join(
        _render_saved_article_signal_facet_row(
            row,
            local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
        )
        for row in facets.rows
    )
    row_count_en = _count_label(facets.row_count, "saved article", "saved articles")
    chip_count = facets.brand_count + facets.product_count + facets.theme_count
    chip_count_en = _count_label(chip_count, "signal chip", "signal chips")
    section_open = (
        '<section class="saved-article-signal-facets" '
        'id="saved-article-signal-facets" '
        'aria-label="Saved article signal facets">'
    )
    summary_en = (
        f"{_esc(row_count_en)} organized by brands, products, and themes "
        f"with {_esc(chip_count_en)}."
    )
    summary_zh = f"{_esc(str(facets.row_count))} 篇保存文章按品牌、产品与主题信号整理。"
    return f"""{section_open}
  <div class="saved-article-signal-facets-header">
    <p class="eyebrow">Signal Facets</p>
    <h2>
      <span data-lang="en">Saved Article Signal Facets</span>
      <span data-lang="zh">保存文章信号切面</span>
    </h2>
    <p>
      <span data-lang="en">{summary_en}</span>
      <span data-lang="zh">{summary_zh}</span>
    </p>
  </div>
  <div class="saved-article-signal-facets-grid">
{rows}
  </div>
</section>"""


def _render_saved_article_signal_facet_row(
    row: RowOneSavedArticleSignalFacetRow,
    *,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str:
    href = _saved_article_signal_facet_row_href(
        row,
        local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
    )
    safe_card_count_en = _count_label(row.safe_card_count, "safe card", "safe cards")
    return f"""    <article class="saved-article-signal-facets-row">
      <div class="saved-article-signal-facets-article">
        <a href="{_esc(href)}">
          <span data-lang="en">{_esc(row.title.en)}</span>
          <span data-lang="zh">{_esc(row.title.zh)}</span>
        </a>
        <span class="saved-article-signal-facets-source">{_esc(row.source_name)}</span>
        <span class="saved-article-signal-facets-metric">
          <span data-lang="en">{_esc(safe_card_count_en)}</span>
          <span data-lang="zh">{_esc(f"{row.safe_card_count} 个安全卡片")}</span>
        </span>
      </div>
      {_render_saved_article_signal_facet_column("Brands", "品牌", row.brands)}
      {_render_saved_article_signal_facet_column("Products", "产品", row.products)}
      {_render_saved_article_signal_facet_column("Themes", "主题", row.themes)}
    </article>"""


def _saved_article_signal_facet_row_href(
    row: RowOneSavedArticleSignalFacetRow,
    *,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str:
    if local_article_page_hrefs_by_detail_path:
        page_href = local_article_page_hrefs_by_detail_path.get(row.detail_path)
        if (
            page_href
            and not page_href.startswith(".")
            and "/" not in page_href
            and page_href.endswith(".html")
            and safe_local_article_story_id(page_href.removesuffix(".html"))
        ):
            return f"{page_href}#local-article-digest"
    return _saved_article_library_page_href(row.href)


def _render_saved_article_signal_facet_column(
    label_en: str,
    label_zh: str,
    chips: Sequence[RowOneSavedArticleSignalFacetChip],
) -> str:
    chip_html = "".join(_render_saved_article_signal_facet_chip(chip) for chip in chips)
    if not chip_html:
        chip_html = '<span class="saved-article-signal-facets-empty">-</span>'
    return f"""<div class="saved-article-signal-facets-column">
        <span class="saved-article-signal-facets-column-label">
          <span data-lang="en">{_esc(label_en)}</span>
          <span data-lang="zh">{_esc(label_zh)}</span>
        </span>
        <div class="saved-article-signal-facets-chips">{chip_html}</div>
      </div>"""


def _render_saved_article_signal_facet_chip(
    chip: RowOneSavedArticleSignalFacetChip,
) -> str:
    return (
        '<span class="saved-article-signal-facets-chip">'
        f'<span data-lang="en">{_esc(chip.label.en)}</span>'
        f'<span data-lang="zh">{_esc(chip.label.zh)}</span>'
        "</span>"
    )


def _render_saved_article_daily_signal_leaderboard(
    leaderboard: RowOneSavedArticleDailySignalLeaderboard | None,
    *,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str:
    if leaderboard is None or not leaderboard.buckets:
        return ""
    buckets = "\n".join(
        _render_saved_article_daily_signal_leaderboard_bucket(
            bucket,
            local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
        )
        for bucket in leaderboard.buckets
        if bucket.items
    )
    if not buckets:
        return ""
    item_count_en = _count_label(leaderboard.item_count, "signal", "signals")
    bucket_count_en = _count_label(leaderboard.bucket_count, "bucket", "buckets")
    summary_en = (
        f"{_esc(item_count_en)} across {_esc(bucket_count_en)}, "
        "aggregated from saved article signal facets."
    )
    summary_zh = (
        f"{_esc(str(leaderboard.item_count))} 个信号，按 "
        f"{_esc(str(leaderboard.bucket_count))} 个分组汇总。"
    )
    return f"""<section class="saved-article-daily-signal-leaderboard"
  id="saved-article-daily-signal-leaderboard"
  aria-label="Saved article daily signal leaderboard">
  <div class="saved-article-daily-signal-leaderboard-header">
    <p class="eyebrow">Daily Signal Leaderboard</p>
    <h2>
      <span data-lang="en">Daily Signal Leaderboard</span>
      <span data-lang="zh">每日信号榜</span>
    </h2>
    <p>
      <span data-lang="en">{summary_en}</span>
      <span data-lang="zh">{summary_zh}</span>
    </p>
  </div>
  <div class="saved-article-daily-signal-leaderboard-grid">
{buckets}
  </div>
</section>"""


def _render_saved_article_daily_signal_leaderboard_bucket(
    bucket: RowOneSavedArticleDailySignalLeaderboardBucket,
    *,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str:
    items = "\n".join(
        _render_saved_article_daily_signal_leaderboard_item(
            item,
            local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
        )
        for item in bucket.items
    )
    return f"""    <div class="saved-article-daily-signal-leaderboard-bucket"
      aria-label="{_esc(bucket.title.en)}">
      <h3>
        <span data-lang="en">{_esc(bucket.title.en)}</span>
        <span data-lang="zh">{_esc(bucket.title.zh)}</span>
      </h3>
{items}
    </div>"""


def _render_saved_article_daily_signal_leaderboard_item(
    item: RowOneSavedArticleDailySignalLeaderboardItem,
    *,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str:
    article_count_en = _count_label(item.article_count, "article", "articles")
    source_count_en = _count_label(item.source_count, "source", "sources")
    supports = "".join(
        _render_saved_article_daily_signal_leaderboard_support(
            support,
            local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
        )
        for support in item.supports
    )
    return f"""      <article class="saved-article-daily-signal-leaderboard-item">
        <div class="saved-article-daily-signal-leaderboard-label">
          <span data-lang="en">{_esc(item.label.en)}</span>
          <span data-lang="zh">{_esc(item.label.zh)}</span>
        </div>
        <div class="saved-article-daily-signal-leaderboard-metrics">
          <span data-lang="en">{_esc(article_count_en)}</span>
          <span data-lang="zh">{_esc(f"{item.article_count} 篇文章")}</span>
          <span data-lang="en">{_esc(source_count_en)}</span>
          <span data-lang="zh">{_esc(f"{item.source_count} 个来源")}</span>
        </div>
        <ul class="saved-article-daily-signal-leaderboard-supports">{supports}</ul>
      </article>"""


def _render_saved_article_daily_signal_leaderboard_support(
    support: RowOneSavedArticleDailySignalLeaderboardSupport,
    *,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str:
    href = _saved_article_daily_signal_leaderboard_support_href(
        support,
        local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
    )
    return f"""<li class="saved-article-daily-signal-leaderboard-support">
          <a href="{_esc(href)}">
            <span data-lang="en">{_esc(support.title.en)}</span>
            <span data-lang="zh">{_esc(support.title.zh)}</span>
          </a>
          <span>{_esc(support.source_name)}</span>
        </li>"""


def _saved_article_daily_signal_leaderboard_support_href(
    support: RowOneSavedArticleDailySignalLeaderboardSupport,
    *,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str:
    if local_article_page_hrefs_by_detail_path:
        page_href = local_article_page_hrefs_by_detail_path.get(support.detail_path)
        if (
            page_href
            and not page_href.startswith(".")
            and "/" not in page_href
            and page_href.endswith(".html")
            and safe_local_article_story_id(page_href.removesuffix(".html"))
        ):
            return f"{page_href}#local-article-digest"
    return _saved_article_library_page_href(support.href)


def _render_daily_local_signal_momentum(
    leaderboard: RowOneSavedArticleDailySignalLeaderboard | None,
    *,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str:
    if leaderboard is None or not leaderboard.buckets:
        return ""
    buckets = [
        bucket_html
        for bucket in leaderboard.buckets
        if (
            bucket_html := _render_daily_local_signal_momentum_bucket(
                bucket,
                local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
            )
        )
    ]
    if not buckets:
        return ""
    item_count_en = _count_label(leaderboard.item_count, "signal", "signals")
    bucket_count_en = _count_label(leaderboard.bucket_count, "bucket", "buckets")
    return f"""<section class="daily-local-signal-momentum"
  aria-label="Daily local signal momentum">
  <div class="daily-local-signal-momentum-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Daily Local Signal Momentum</span>
        <span data-lang="zh">每日本地信号动量</span>
      </p>
      <h2>
        <span data-lang="en">Today's strongest saved local signals</span>
        <span data-lang="zh">今日最集中的本地保存信号</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">
        Current-edition brand, product, and theme concentration from saved local articles.
      </span>
      <span data-lang="zh">
        基于当前版本已保存本地文章，汇总品牌、单品与主题的集中度。
      </span>
    </p>
  </div>
  <div class="daily-local-signal-momentum-metrics">
    <span>{_esc(item_count_en)}</span>
    <span>{_esc(bucket_count_en)}</span>
    <span data-lang="en">Current-edition support counts</span>
    <span data-lang="zh">当前版本支持计数</span>
  </div>
  <div class="daily-local-signal-momentum-grid">{"".join(buckets)}</div>
</section>"""


def _render_daily_local_signal_momentum_bucket(
    bucket: RowOneSavedArticleDailySignalLeaderboardBucket,
    *,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str:
    items = [
        item_html
        for item in bucket.items
        if (
            item_html := _render_daily_local_signal_momentum_item(
                item,
                local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
            )
        )
    ]
    if not items:
        return ""
    return f"""    <article class="daily-local-signal-momentum-bucket"
      aria-label="{_esc(bucket.title.en)}">
      <h3>
        <span data-lang="en">{_esc(bucket.title.en)}</span>
        <span data-lang="zh">{_esc(bucket.title.zh)}</span>
      </h3>
      {"".join(items)}
    </article>"""


def _render_daily_local_signal_momentum_item(
    item: RowOneSavedArticleDailySignalLeaderboardItem,
    *,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str:
    supports = [
        support_html
        for support in item.supports
        if (
            support_html := _render_daily_local_signal_momentum_support(
                support,
                local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
            )
        )
    ]
    if not supports:
        return ""
    article_count_en = _count_label(item.article_count, "article", "articles")
    source_count_en = _count_label(item.source_count, "source", "sources")
    return f"""      <div class="daily-local-signal-momentum-item">
        <div class="daily-local-signal-momentum-label">
          <span data-lang="en">{_esc(item.label.en)}</span>
          <span data-lang="zh">{_esc(item.label.zh)}</span>
        </div>
        <div class="daily-local-signal-momentum-counts">
          <span data-lang="en">{_esc(article_count_en)}</span>
          <span data-lang="zh">{_esc(f"{item.article_count} 篇文章")}</span>
          <span data-lang="en">{_esc(source_count_en)}</span>
          <span data-lang="zh">{_esc(f"{item.source_count} 个来源")}</span>
        </div>
        <ul class="daily-local-signal-momentum-supports">{"".join(supports)}</ul>
      </div>"""


def _render_daily_local_signal_momentum_support(
    support: RowOneSavedArticleDailySignalLeaderboardSupport,
    *,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str:
    href = _daily_local_signal_momentum_support_href(
        support,
        local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
    )
    if href is None:
        return ""
    return f"""<li class="daily-local-signal-momentum-support">
          <a href="{_esc(href)}">
            <span data-lang="en">{_esc(support.title.en)}</span>
            <span data-lang="zh">{_esc(support.title.zh)}</span>
          </a>
          <span>{_esc(support.source_name)}</span>
        </li>"""


def _daily_local_signal_momentum_support_href(
    support: RowOneSavedArticleDailySignalLeaderboardSupport,
    *,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str | None:
    if local_article_page_hrefs_by_detail_path:
        mapped_href = _safe_daily_local_signal_momentum_page_href(
            local_article_page_hrefs_by_detail_path.get(support.detail_path)
        )
        if mapped_href is not None:
            return f"articles/{mapped_href}#local-article-digest"
    return _safe_daily_local_signal_momentum_detail_href(support.href)


def _safe_daily_local_signal_momentum_page_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if href.startswith((".", "/", "//")):
        return None
    path = PurePosixPath(href)
    if (
        path.is_absolute()
        or len(path.parts) != 1
        or path.name in ("", ".", "..")
        or ".." in path.parts
        or not path.name.endswith(".html")
    ):
        return None
    story_id = path.name.removesuffix(".html")
    if not safe_local_article_story_id(story_id):
        return None
    return f"{story_id}.html"


def _safe_daily_local_signal_momentum_detail_href(href: object) -> str | None:
    return safe_row_one_detail_fragment_href(href, "local-article-digest")


def _render_daily_local_heat_signals(
    app_payload: dict[str, object] | None,
    *,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_hrefs_by_story_id: Mapping[str, str] | None,
) -> str:
    topics = _daily_local_heat_signal_topics(
        app_payload,
        local_articles_by_story_id=local_articles_by_story_id,
        article_hrefs_by_story_id=article_hrefs_by_story_id,
    )
    if not topics:
        return ""
    distinct_article_count = len({story.href for topic in topics for story in topic.stories})
    story_row_count = sum(len(topic.stories) for topic in topics)
    topic_count_en = _count_label(len(topics), "heated topic", "heated topics")
    article_count_en = _count_label(distinct_article_count, "local article", "local articles")
    story_row_count_en = _count_label(story_row_count, "story cue", "story cues")
    rendered_topics = "\n".join(_render_daily_local_heat_signal_topic(topic) for topic in topics)
    return f"""<section class="daily-local-heat-signals"
  aria-label="Daily local heat signals">
  <div class="daily-local-heat-signals-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Daily Local Heat Signals</span>
        <span data-lang="zh">每日本地热度信号</span>
      </p>
      <h2>
        <span data-lang="en">Brands and products heating up locally</span>
        <span data-lang="zh">本地正文里正在升温的品牌与单品</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">
        Current-edition heat sorted from saved local article text, limited to brands and products.
      </span>
      <span data-lang="zh">
        基于当前版本已保存本地正文排序，只展示品牌与单品热度。
      </span>
    </p>
  </div>
  <div class="daily-local-heat-signals-metrics">
    <span>{_esc(topic_count_en)}</span>
    <span>{_esc(article_count_en)}</span>
    <span>{_esc(story_row_count_en)}</span>
    <span data-lang="en">Saved local text only</span>
    <span data-lang="zh">仅限本地保存正文</span>
  </div>
  <div class="daily-local-heat-signals-grid">
{rendered_topics}
  </div>
</section>"""


def _daily_local_heat_signal_topics(
    app_payload: dict[str, object] | None,
    *,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_hrefs_by_story_id: Mapping[str, str] | None,
) -> list[_DailyLocalHeatSignalTopic]:
    payload = app_payload or {}
    if not isinstance(payload, dict):
        return []
    daily_digest = payload.get("daily_digest", {})
    if not isinstance(daily_digest, dict):
        return []
    raw_topics = daily_digest.get("briefing_topics", [])
    if not isinstance(raw_topics, list):
        return []
    rendered_topics = [
        topic
        for raw_topic in raw_topics
        if isinstance(raw_topic, dict)
        and (
            topic := _daily_local_heat_signal_topic_from_payload(
                raw_topic,
                local_articles_by_story_id=local_articles_by_story_id,
                article_hrefs_by_story_id=article_hrefs_by_story_id,
            )
        )
    ]
    rendered_topics.sort(key=_daily_local_heat_signal_topic_sort_key)
    return rendered_topics[:DAILY_LOCAL_HEAT_SIGNALS_MAX_TOPICS]


def _daily_local_heat_signal_topic_from_payload(
    topic: dict[str, object],
    *,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_hrefs_by_story_id: Mapping[str, str] | None,
) -> _DailyLocalHeatSignalTopic | None:
    topic_type = str(topic.get("topic_type", "")).strip().casefold()
    if topic_type not in {"brand", "product"}:
        return None
    positive_heat_delta_sum = _positive_int_value(topic.get("positive_heat_delta_sum"))
    max_heat_delta = _positive_int_value(topic.get("max_heat_delta"))
    if positive_heat_delta_sum <= 0 and max_heat_delta <= 0:
        return None
    title = _localized_topic_field(topic, "title")
    title = LocalizedText(
        en=normalize_row_one_paragraph(title.en),
        zh=normalize_row_one_paragraph(title.zh),
    )
    if not title.en and not title.zh:
        return None
    if not title.en:
        title = LocalizedText(en=title.zh, zh=title.zh)
    if not title.zh:
        title = LocalizedText(en=title.en, zh=title.en)
    label = _daily_local_heat_signal_topic_label(topic, topic_type)
    stories, local_article_count = _daily_local_heat_signal_story_rows(
        topic,
        fallback_title=title,
        local_articles_by_story_id=local_articles_by_story_id,
        article_hrefs_by_story_id=article_hrefs_by_story_id,
    )
    if not stories:
        return None
    return _DailyLocalHeatSignalTopic(
        title=title,
        label=label,
        subtype_label=_daily_local_heat_signal_subtype_label(topic.get("source_refs")),
        story_count=_nonnegative_int_value(topic.get("story_count")),
        evidence_count=_nonnegative_int_value(topic.get("evidence_count")),
        local_article_count=local_article_count,
        positive_heat_delta_sum=positive_heat_delta_sum,
        max_heat_delta=max_heat_delta,
        stories=tuple(stories),
    )


def _daily_local_heat_signal_topic_label(
    topic: dict[str, object],
    topic_type: str,
) -> LocalizedText:
    label = _localized_topic_field(topic, "label")
    label = LocalizedText(
        en=normalize_row_one_paragraph(label.en),
        zh=normalize_row_one_paragraph(label.zh),
    )
    if label.en or label.zh:
        return LocalizedText(en=label.en or label.zh, zh=label.zh or label.en)
    if topic_type == "brand":
        return LocalizedText(en="Brand", zh="品牌")
    return LocalizedText(en="Product", zh="单品")


def _daily_local_heat_signal_story_rows(
    topic: dict[str, object],
    *,
    fallback_title: LocalizedText,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_hrefs_by_story_id: Mapping[str, str] | None,
) -> tuple[list[_DailyLocalHeatSignalStory], int]:
    story_ids = topic.get("story_ids", [])
    if not isinstance(story_ids, list):
        return ([], 0)
    card_by_story_id = _daily_local_heat_signal_cards_by_story_id(topic.get("cards"))
    rows: list[_DailyLocalHeatSignalStory] = []
    local_article_count = 0
    seen_story_ids: set[str] = set()
    for story_id in story_ids:
        if not isinstance(story_id, str):
            continue
        if story_id in seen_story_ids or not safe_local_article_story_id(story_id):
            continue
        seen_story_ids.add(story_id)
        article = local_articles_by_story_id.get(story_id)
        if _usable_local_article_paragraph_count(article) <= 0:
            continue
        href = _daily_local_heat_signal_story_href(
            story_id,
            article_hrefs_by_story_id=article_hrefs_by_story_id,
        )
        if href is None:
            continue
        local_article_count += 1
        if len(rows) >= DAILY_LOCAL_HEAT_SIGNALS_MAX_STORIES:
            continue
        card = card_by_story_id.get(story_id)
        rows.append(
            _DailyLocalHeatSignalStory(
                title=_daily_local_heat_signal_story_title(card, fallback_title),
                source_name=_daily_local_heat_signal_story_source(card, article),
                href=href,
            )
        )
    return (rows, local_article_count)


def _daily_local_heat_signal_cards_by_story_id(value: object) -> dict[str, dict[str, object]]:
    if not isinstance(value, list):
        return {}
    cards: dict[str, dict[str, object]] = {}
    for card in value:
        if not isinstance(card, dict):
            continue
        story_id = card.get("id")
        if isinstance(story_id, str) and safe_local_article_story_id(story_id):
            cards.setdefault(story_id, card)
    return cards


def _daily_local_heat_signal_story_title(
    card: dict[str, object] | None,
    fallback_title: LocalizedText,
) -> LocalizedText:
    if card is None:
        return fallback_title
    headline = _localized_payload_text(card.get("headline"))
    headline = LocalizedText(
        en=normalize_row_one_paragraph(headline.en),
        zh=normalize_row_one_paragraph(headline.zh),
    )
    if headline.en or headline.zh:
        return LocalizedText(en=headline.en or headline.zh, zh=headline.zh or headline.en)
    return fallback_title


def _daily_local_heat_signal_story_source(
    card: dict[str, object] | None,
    article: RowOneLocalArticle | None,
) -> str:
    source_name = ""
    if card is not None:
        source_name = normalize_row_one_paragraph(str(card.get("source_name") or ""))
    if source_name:
        return source_name
    if article is not None:
        return normalize_row_one_paragraph(article.source_name)
    return ""


def _daily_local_heat_signal_story_href(
    story_id: str,
    *,
    article_hrefs_by_story_id: Mapping[str, str] | None,
) -> str | None:
    if article_hrefs_by_story_id is None:
        return None
    page_href = _safe_daily_local_heat_signals_page_href(article_hrefs_by_story_id.get(story_id))
    if page_href is None:
        return None
    if page_href.removesuffix(".html") != story_id:
        return None
    return f"articles/{page_href}#local-article-digest"


def _safe_daily_local_heat_signals_page_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if href.startswith((".", "/", "//")):
        return None
    path = PurePosixPath(href)
    if (
        path.is_absolute()
        or len(path.parts) != 1
        or path.name in ("", ".", "..")
        or ".." in path.parts
        or not path.name.endswith(".html")
    ):
        return None
    story_id = path.name.removesuffix(".html")
    if not safe_local_article_story_id(story_id):
        return None
    return f"{story_id}.html"


def _render_daily_local_article_capsules(
    edition: RowOneEdition,
    *,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_hrefs_by_story_id: Mapping[str, str] | None,
) -> str:
    capsules = _daily_local_article_capsules(
        edition,
        local_articles_by_story_id=local_articles_by_story_id,
        article_hrefs_by_story_id=article_hrefs_by_story_id,
    )
    if not capsules:
        return ""
    article_count_en = _count_label(len(capsules), "local article", "local articles")
    paragraph_count = sum(len(capsule.paragraphs) for capsule in capsules)
    paragraph_count_en = _count_label(paragraph_count, "paragraph cue", "paragraph cues")
    rendered_capsules = "\n".join(
        _render_daily_local_article_capsule(capsule) for capsule in capsules
    )
    return f"""<section class="daily-local-article-capsules"
  aria-label="Daily local article capsules">
  <div class="daily-local-article-capsules-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Daily Local Article Capsules</span>
        <span data-lang="zh">每日本地文章胶囊</span>
      </p>
      <h2>
        <span data-lang="en">Saved articles, edited into readable cards</span>
        <span data-lang="zh">把已保存文章整理成可读卡片</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">
        Compact same-site capsules built only from today's saved local article text.
      </span>
      <span data-lang="zh">
        仅基于今日已保存本地正文生成的站内速读卡片。
      </span>
    </p>
  </div>
  <div class="daily-local-article-capsules-metrics">
    <span>{_esc(article_count_en)}</span>
    <span>{_esc(paragraph_count_en)}</span>
    <span data-lang="en">Homepage only</span>
    <span data-lang="zh">仅首页展示</span>
  </div>
  <div class="daily-local-article-capsules-grid">
{rendered_capsules}
  </div>
</section>"""


def _daily_local_article_capsules(
    edition: RowOneEdition,
    *,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_hrefs_by_story_id: Mapping[str, str] | None,
) -> list[_DailyLocalArticleCapsule]:
    capsules: list[_DailyLocalArticleCapsule] = []
    for story in edition.stories:
        capsule = _daily_local_article_capsule_from_story(
            story,
            local_articles_by_story_id=local_articles_by_story_id,
            article_hrefs_by_story_id=article_hrefs_by_story_id,
        )
        if capsule is None:
            continue
        capsules.append(capsule)
        if len(capsules) >= DAILY_LOCAL_ARTICLE_CAPSULES_MAX_ITEMS:
            break
    return capsules


def _daily_local_article_capsule_from_story(
    story: RowOneStory,
    *,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_hrefs_by_story_id: Mapping[str, str] | None,
) -> _DailyLocalArticleCapsule | None:
    if not safe_local_article_story_id(story.id):
        return None
    article = local_articles_by_story_id.get(story.id)
    if article is None or _usable_local_article_paragraph_count(article) <= 0:
        return None
    href = _daily_local_article_capsule_href(
        story.id,
        article_hrefs_by_story_id,
        fragment="local-article-digest",
    )
    if href is None:
        return None
    paragraphs = _daily_local_article_capsule_paragraphs(
        article,
        story_id=story.id,
        article_hrefs_by_story_id=article_hrefs_by_story_id,
    )
    if not paragraphs:
        return None
    title = normalize_row_one_paragraph(story.headline) or normalize_row_one_paragraph(
        article.title
    )
    if not title:
        return None
    why_it_matters = LocalizedText(
        en=normalize_row_one_paragraph(story.why_it_matters.en),
        zh=normalize_row_one_paragraph(story.why_it_matters.zh),
    )
    return _DailyLocalArticleCapsule(
        title=LocalizedText(en=title, zh=title),
        article_title=normalize_row_one_paragraph(article.title or ""),
        source_name=normalize_row_one_paragraph(article.source_name or story.source_name),
        body_source=_local_article_body_source_label(article),
        why_it_matters=why_it_matters,
        href=href,
        paragraphs=paragraphs,
        references=_daily_local_article_capsule_references(story),
    )


def _daily_local_article_capsule_href(
    story_id: str,
    article_hrefs_by_story_id: Mapping[str, str] | None,
    *,
    fragment: str,
) -> str | None:
    if article_hrefs_by_story_id is None:
        return None
    page_href = _safe_daily_local_article_capsule_page_href(
        story_id,
        article_hrefs_by_story_id.get(story_id),
    )
    if page_href is None:
        return None
    return f"articles/{page_href}#{fragment}"


def _safe_daily_local_article_capsule_page_href(story_id: str, href: object) -> str | None:
    if not safe_local_article_story_id(story_id) or not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if href.startswith((".", "/", "//")):
        return None
    path = PurePosixPath(href)
    if (
        path.is_absolute()
        or len(path.parts) != 1
        or path.name in ("", ".", "..")
        or ".." in path.parts
        or not path.name.endswith(".html")
    ):
        return None
    mapped_story_id = path.name.removesuffix(".html")
    if mapped_story_id != story_id or not safe_local_article_story_id(mapped_story_id):
        return None
    return f"{mapped_story_id}.html"


def _daily_local_article_capsule_paragraphs(
    article: RowOneLocalArticle,
    *,
    story_id: str,
    article_hrefs_by_story_id: Mapping[str, str] | None,
) -> tuple[_DailyLocalArticleCapsuleParagraph, ...]:
    paragraphs: list[_DailyLocalArticleCapsuleParagraph] = []
    for paragraph_index, paragraph in enumerate(article.paragraphs):
        excerpt_en = _daily_local_article_capsule_excerpt(paragraph)
        if not excerpt_en:
            continue
        href = _daily_local_article_capsule_href(
            story_id,
            article_hrefs_by_story_id,
            fragment=_local_article_paragraph_anchor(paragraph_index),
        )
        if href is None:
            continue
        excerpt_zh = ""
        if paragraph_index < len(article.paragraphs_zh):
            excerpt_zh = _daily_local_article_capsule_excerpt(
                article.paragraphs_zh[paragraph_index]
            )
        paragraphs.append(
            _DailyLocalArticleCapsuleParagraph(
                index=paragraph_index,
                excerpt=LocalizedText(en=excerpt_en, zh=excerpt_zh),
                href=href,
            )
        )
        if len(paragraphs) >= DAILY_LOCAL_ARTICLE_CAPSULES_MAX_PARAGRAPHS:
            break
    return tuple(paragraphs)


def _daily_local_article_capsule_excerpt(text: str) -> str:
    normalized = normalize_row_one_paragraph(text)
    if len(normalized) <= DAILY_LOCAL_ARTICLE_CAPSULE_EXCERPT_CHARS:
        return normalized
    return normalized[:DAILY_LOCAL_ARTICLE_CAPSULE_EXCERPT_CHARS].rstrip() + "…"


def _daily_local_article_capsule_references(
    story: RowOneStory,
) -> tuple[RowOneReference, ...]:
    refs: list[RowOneReference] = []
    seen: set[tuple[str, str, str]] = set()
    for ref in [*story.entity_refs, *story.product_refs]:
        if len(refs) >= DAILY_LOCAL_ARTICLE_CAPSULES_MAX_REFS:
            break
        name = normalize_row_one_paragraph(ref.name)
        ref_type = normalize_row_one_paragraph(ref.type)
        label = normalize_row_one_paragraph(ref.label)
        if not name:
            continue
        key = (name.casefold(), ref_type.casefold(), label.casefold())
        if key in seen:
            continue
        seen.add(key)
        refs.append(RowOneReference(name=name, type=ref_type, label=label))
    return tuple(refs)


def _render_daily_local_article_capsule(capsule: _DailyLocalArticleCapsule) -> str:
    paragraphs = "\n".join(
        _render_daily_local_article_capsule_paragraph(paragraph) for paragraph in capsule.paragraphs
    )
    refs = "".join(_render_daily_local_article_capsule_ref(ref) for ref in capsule.references)
    refs_html = f'<div class="daily-local-article-capsule-refs">{refs}</div>' if refs else ""
    source_title = (
        f'<span class="daily-local-article-capsule-source-title">{_esc(capsule.source_name)}</span>'
        if capsule.source_name
        else ""
    )
    article_title = (
        '<span class="daily-local-article-capsule-article-title">'
        f"{_esc(capsule.article_title)}</span>"
        if capsule.article_title
        else ""
    )
    return f"""    <article class="daily-local-article-capsule">
      <div class="daily-local-article-capsule-header">
        <h3 class="daily-local-article-capsule-title">
          <a href="{_esc(capsule.href)}">
            <span data-lang="en">{_esc(capsule.title.en)}</span>
            <span data-lang="zh">{_esc(capsule.title.zh)}</span>
          </a>
        </h3>
        <div class="daily-local-article-capsule-meta">
          {article_title}
          {source_title}
          <span>{_esc(capsule.body_source)}</span>
        </div>
      </div>
      <p class="daily-local-article-capsule-why">
        <span data-lang="en">{_esc(capsule.why_it_matters.en)}</span>
        <span data-lang="zh">{_esc(capsule.why_it_matters.zh)}</span>
      </p>
      <div class="daily-local-article-capsule-paragraphs">
{paragraphs}
      </div>
      {refs_html}
      <a class="daily-local-article-capsule-link" href="{_esc(capsule.href)}">
        <span data-lang="en">Open local article</span>
        <span data-lang="zh">打开本地文章</span>
      </a>
    </article>"""


def _render_daily_local_article_capsule_paragraph(
    paragraph: _DailyLocalArticleCapsuleParagraph,
) -> str:
    label_en = f"Paragraph {paragraph.index + 1}"
    label_zh = f"段落 {paragraph.index + 1}"
    zh_excerpt = (
        f'<span data-lang="zh">{_esc(paragraph.excerpt.zh)}</span>' if paragraph.excerpt.zh else ""
    )
    return f"""        <a class="daily-local-article-capsule-paragraph"
          href="{_esc(paragraph.href)}">
          <span class="daily-local-article-capsule-paragraph-label">
            <span data-lang="en">{_esc(label_en)}</span>
            <span data-lang="zh">{_esc(label_zh)}</span>
          </span>
          <span data-lang="en">{_esc(paragraph.excerpt.en)}</span>
          {zh_excerpt}
        </a>"""


def _render_daily_local_article_capsule_ref(ref: RowOneReference) -> str:
    label = normalize_row_one_paragraph(ref.label) or normalize_row_one_paragraph(ref.type)
    label_html = f"<span>{_esc(label)}</span>" if label else ""
    return f'<span class="daily-local-article-capsule-ref">{_esc(ref.name)}{label_html}</span>'


def _render_daily_local_article_reading_brief(
    edition: RowOneEdition,
    *,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_hrefs_by_story_id: Mapping[str, str] | None,
) -> str:
    groups = _daily_local_article_reading_brief_groups(
        edition,
        local_articles_by_story_id=local_articles_by_story_id,
        article_hrefs_by_story_id=article_hrefs_by_story_id,
    )
    if not groups:
        return ""
    assert len(groups) <= DAILY_LOCAL_ARTICLE_READING_BRIEF_MAX_GROUPS
    item_count = sum(len(group.items) for group in groups)
    article_count_en = _count_label(item_count, "local article", "local articles")
    group_count_en = _count_label(len(groups), "reading lane", "reading lanes")
    rendered_groups = "\n".join(
        _render_daily_local_article_reading_brief_group(group) for group in groups
    )
    return f"""<section class="daily-local-article-reading-brief"
  aria-label="Daily local article reading brief">
  <div class="daily-local-article-reading-brief-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Daily Local Article Reading Brief</span>
        <span data-lang="zh">每日本地文章阅读简报</span>
      </p>
      <h2>
        <span data-lang="en">Start with the saved local articles worth reading first</span>
        <span data-lang="zh">从最值得先读的本地保存文章开始</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">
        A same-site reading order built only from today&apos;s downloaded article text.
      </span>
      <span data-lang="zh">
        仅基于今日已下载正文生成的站内阅读顺序。
      </span>
    </p>
  </div>
  <div class="daily-local-article-reading-brief-metrics">
    <span>{_esc(article_count_en)}</span>
    <span>{_esc(group_count_en)}</span>
    <span data-lang="en">Local text only</span>
    <span data-lang="zh">仅本地正文</span>
  </div>
  <div class="daily-local-article-reading-brief-grid">
{rendered_groups}
  </div>
</section>"""


def _daily_local_article_reading_brief_groups(
    edition: RowOneEdition,
    *,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_hrefs_by_story_id: Mapping[str, str] | None,
) -> tuple[_DailyLocalArticleReadingBriefGroup, ...]:
    group_specs = (
        (
            "read_first",
            LocalizedText(en="Read First", zh="先读这个"),
            LocalizedText(
                en="Start with the saved local articles that set the day's editorial context.",
                zh="先读建立当日编辑语境的已保存本地文章。",
            ),
        ),
        (
            "brand_watch",
            LocalizedText(en="Brand Watch", zh="品牌观察"),
            LocalizedText(
                en="Track the saved articles with brand, designer, or entity context.",
                zh="追踪含品牌、设计师或实体语境的已保存文章。",
            ),
        ),
        (
            "product_watch",
            LocalizedText(en="Product Watch", zh="单品观察"),
            LocalizedText(
                en="Scan the saved articles with bags, shoes, or other product signals.",
                zh="浏览含包袋、鞋履或其他单品信号的已保存文章。",
            ),
        ),
    )
    eligible_by_group: dict[str, list[_DailyLocalArticleReadingBriefItem]] = {
        key: [] for key, _, _ in group_specs
    }
    for story in edition.stories:
        article = local_articles_by_story_id.get(story.id)
        if article is None:
            continue
        item = _daily_local_article_reading_brief_item_from_story(
            story,
            article,
            article_hrefs_by_story_id=article_hrefs_by_story_id,
        )
        if item is None:
            continue
        for key in _daily_local_article_reading_brief_group_candidates(story, article):
            if key in eligible_by_group:
                eligible_by_group[key].append(item)

    groups: list[_DailyLocalArticleReadingBriefGroup] = []
    used_item_hrefs: set[str] = set()
    rendered_total = 0
    for group_index, (key, title, dek) in enumerate(group_specs):
        items: list[_DailyLocalArticleReadingBriefItem] = []
        for item in eligible_by_group[key]:
            if rendered_total >= DAILY_LOCAL_ARTICLE_READING_BRIEF_MAX_TOTAL_ITEMS:
                break
            if item.href in used_item_hrefs:
                continue
            later_group_count = sum(
                1
                for later_key, _, _ in group_specs[group_index + 1 :]
                if any(
                    later_item.href not in used_item_hrefs
                    for later_item in eligible_by_group[later_key]
                )
            )
            if (
                len(items) > 0
                and rendered_total + later_group_count
                >= DAILY_LOCAL_ARTICLE_READING_BRIEF_MAX_TOTAL_ITEMS
            ):
                continue
            items.append(item)
            used_item_hrefs.add(item.href)
            rendered_total += 1
            if len(items) >= DAILY_LOCAL_ARTICLE_READING_BRIEF_MAX_ITEMS_PER_GROUP:
                break
        if items:
            groups.append(
                _DailyLocalArticleReadingBriefGroup(
                    key=key,
                    title=title,
                    dek=dek,
                    items=tuple(items),
                )
            )
    return tuple(groups)


def _daily_local_article_reading_brief_group_candidates(
    story: RowOneStory,
    article: RowOneLocalArticle,
) -> tuple[str, ...]:
    candidates = ["read_first"]
    content_section_keys = {
        normalize_row_one_paragraph(section.key).casefold() for section in article.content_sections
    }
    if (
        story.entity_refs
        or story.designer_refs
        or "entities" in content_section_keys
        or "brand_signals" in content_section_keys
    ):
        candidates.append("brand_watch")
    if story.product_refs or "product_signals" in content_section_keys:
        candidates.append("product_watch")
    return tuple(candidates)


def _daily_local_article_reading_brief_item_from_story(
    story: RowOneStory,
    article: RowOneLocalArticle,
    *,
    article_hrefs_by_story_id: Mapping[str, str] | None,
) -> _DailyLocalArticleReadingBriefItem | None:
    if (
        not safe_local_article_story_id(story.id)
        or _usable_local_article_paragraph_count(article) <= 0
    ):
        return None
    href = _daily_local_article_reading_brief_href(
        story.id,
        article_hrefs_by_story_id,
        fragment="local-article-digest",
    )
    paragraph_index = _daily_local_article_reading_brief_first_paragraph_index(article)
    if paragraph_index is None:
        return None
    paragraph_excerpt_en = _daily_local_article_reading_brief_excerpt(
        article.paragraphs[paragraph_index]
    )
    paragraph_excerpt_zh = ""
    if paragraph_index < len(article.paragraphs_zh):
        paragraph_excerpt_zh = _daily_local_article_reading_brief_excerpt(
            article.paragraphs_zh[paragraph_index]
        )
    paragraph_href = _daily_local_article_reading_brief_href(
        story.id,
        article_hrefs_by_story_id,
        fragment=_local_article_paragraph_anchor(paragraph_index),
    )
    if href is None or paragraph_href is None:
        return None
    title_en = normalize_row_one_paragraph(story.headline)
    article_title = normalize_row_one_paragraph(article.title or "")
    title_zh = article_title or title_en
    if not title_en:
        return None
    reason = _daily_local_article_reading_brief_reason(story, article)
    if not reason.en and not reason.zh:
        return None
    return _DailyLocalArticleReadingBriefItem(
        title=LocalizedText(en=title_en, zh=title_zh),
        article_title=article_title,
        source_name=normalize_row_one_paragraph(article.source_name or story.source_name),
        body_source=_local_article_body_source_label(article),
        reason=reason,
        paragraph_excerpt=LocalizedText(
            en=paragraph_excerpt_en,
            zh=paragraph_excerpt_zh or paragraph_excerpt_en,
        ),
        paragraph_number=paragraph_index + 1,
        href=href,
        paragraph_href=paragraph_href,
        references=_daily_local_article_reading_brief_references(story),
    )


def _daily_local_article_reading_brief_href(
    story_id: str,
    article_hrefs_by_story_id: Mapping[str, str] | None,
    *,
    fragment: str,
) -> str | None:
    if article_hrefs_by_story_id is None:
        return None
    page_href = _safe_daily_local_article_reading_brief_page_href(
        story_id,
        article_hrefs_by_story_id.get(story_id),
    )
    if page_href is None:
        return None
    return f"articles/{page_href}#{fragment}"


def _safe_daily_local_article_reading_brief_page_href(
    story_id: str,
    href: object,
) -> str | None:
    if not safe_local_article_story_id(story_id) or not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if href.startswith((".", "/", "//")):
        return None
    path = PurePosixPath(href)
    if (
        path.is_absolute()
        or len(path.parts) != 1
        or path.name in ("", ".", "..")
        or ".." in path.parts
        or not path.name.endswith(".html")
    ):
        return None
    mapped_story_id = path.name.removesuffix(".html")
    if mapped_story_id != story_id or not safe_local_article_story_id(mapped_story_id):
        return None
    return f"{mapped_story_id}.html"


def _daily_local_article_reading_brief_reason(
    story: RowOneStory,
    article: RowOneLocalArticle,
) -> LocalizedText:
    for candidate in (
        story.why_it_matters,
        *(section.body for section in article.brief_sections),
    ):
        reason = LocalizedText(
            en=_daily_local_article_reading_brief_excerpt(candidate.en),
            zh=_daily_local_article_reading_brief_excerpt(candidate.zh),
        )
        if reason.en or reason.zh:
            return LocalizedText(en=reason.en or reason.zh, zh=reason.zh or reason.en)
    for section in article.content_sections:
        for item in section.items:
            if item.body is None:
                continue
            reason = LocalizedText(
                en=_daily_local_article_reading_brief_excerpt(item.body.en),
                zh=_daily_local_article_reading_brief_excerpt(item.body.zh),
            )
            if reason.en or reason.zh:
                return LocalizedText(en=reason.en or reason.zh, zh=reason.zh or reason.en)
    paragraph_index = _daily_local_article_reading_brief_first_paragraph_index(article)
    if paragraph_index is None:
        return LocalizedText(en="", zh="")
    excerpt_en = _daily_local_article_reading_brief_excerpt(article.paragraphs[paragraph_index])
    excerpt_zh = ""
    if paragraph_index < len(article.paragraphs_zh):
        excerpt_zh = _daily_local_article_reading_brief_excerpt(
            article.paragraphs_zh[paragraph_index]
        )
    return LocalizedText(en=excerpt_en, zh=excerpt_zh or excerpt_en)


def _daily_local_article_reading_brief_first_paragraph_index(
    article: RowOneLocalArticle,
) -> int | None:
    for paragraph_index, paragraph in enumerate(article.paragraphs):
        if normalize_row_one_paragraph(paragraph):
            return paragraph_index
    return None


def _daily_local_article_reading_brief_excerpt(text: str) -> str:
    normalized = normalize_row_one_paragraph(text)
    if len(normalized) <= DAILY_LOCAL_ARTICLE_READING_BRIEF_EXCERPT_CHARS:
        return normalized
    return normalized[:DAILY_LOCAL_ARTICLE_READING_BRIEF_EXCERPT_CHARS].rstrip() + "…"


def _daily_local_article_reading_brief_references(
    story: RowOneStory,
) -> tuple[_DailyLocalArticleReadingBriefReference, ...]:
    refs: list[_DailyLocalArticleReadingBriefReference] = []
    seen: set[tuple[str, str]] = set()
    for ref in [*story.entity_refs, *story.designer_refs, *story.product_refs]:
        if len(refs) >= DAILY_LOCAL_ARTICLE_READING_BRIEF_MAX_REFS:
            break
        name = normalize_row_one_paragraph(ref.name)
        label = normalize_row_one_paragraph(ref.label) or normalize_row_one_paragraph(ref.type)
        if not name:
            continue
        key = (name.casefold(), label.casefold())
        if key in seen:
            continue
        seen.add(key)
        refs.append(_DailyLocalArticleReadingBriefReference(name=name, label=label))
    return tuple(refs)


def _render_daily_local_article_reading_brief_group(
    group: _DailyLocalArticleReadingBriefGroup,
) -> str:
    items = "\n".join(_render_daily_local_article_reading_brief_item(item) for item in group.items)
    return f"""    <article class="daily-local-article-reading-brief-group">
      <div class="daily-local-article-reading-brief-group-header">
        <h3>
          <span data-lang="en">{_esc(group.title.en)}</span>
          <span data-lang="zh">{_esc(group.title.zh)}</span>
        </h3>
        <p>
          <span data-lang="en">{_esc(group.dek.en)}</span>
          <span data-lang="zh">{_esc(group.dek.zh)}</span>
        </p>
      </div>
      <div class="daily-local-article-reading-brief-items">
{items}
      </div>
    </article>"""


def _render_daily_local_article_reading_brief_item(
    item: _DailyLocalArticleReadingBriefItem,
) -> str:
    paragraph_label_en = f"Open paragraph {item.paragraph_number}"
    paragraph_label_zh = f"打开段落 {item.paragraph_number}"
    article_title = (
        '<span class="daily-local-article-reading-brief-article-title">'
        f"{_esc(item.article_title)}</span>"
        if item.article_title
        else ""
    )
    source_name = (
        f'<span class="daily-local-article-reading-brief-source">{_esc(item.source_name)}</span>'
        if item.source_name
        else ""
    )
    refs = "".join(_render_daily_local_article_reading_brief_ref(ref) for ref in item.references)
    refs_html = f'<div class="daily-local-article-reading-brief-refs">{refs}</div>' if refs else ""
    return f"""        <article class="daily-local-article-reading-brief-item">
          <h4 class="daily-local-article-reading-brief-title">
            <a href="{_esc(item.href)}">
              <span data-lang="en">{_esc(item.title.en)}</span>
              <span data-lang="zh">{_esc(item.title.zh)}</span>
            </a>
          </h4>
          <div class="daily-local-article-reading-brief-meta">
            {article_title}
            {source_name}
            <span>{_esc(item.body_source)}</span>
          </div>
          <p class="daily-local-article-reading-brief-reason">
            <span data-lang="en">{_esc(item.reason.en)}</span>
            <span data-lang="zh">{_esc(item.reason.zh)}</span>
          </p>
          <a class="daily-local-article-reading-brief-excerpt"
            href="{_esc(item.paragraph_href)}">
            <span data-lang="en">{_esc(item.paragraph_excerpt.en)}</span>
            <span data-lang="zh">{_esc(item.paragraph_excerpt.zh)}</span>
          </a>
          {refs_html}
          <div class="daily-local-article-reading-brief-actions">
            <a class="daily-local-article-reading-brief-action" href="{_esc(item.href)}">
              <span data-lang="en">Open digest</span>
              <span data-lang="zh">打开摘要</span>
            </a>
            <a class="daily-local-article-reading-brief-action" href="{_esc(item.paragraph_href)}">
              <span data-lang="en">{_esc(paragraph_label_en)}</span>
              <span data-lang="zh">{_esc(paragraph_label_zh)}</span>
            </a>
          </div>
        </article>"""


def _render_daily_local_article_reading_brief_ref(
    ref: _DailyLocalArticleReadingBriefReference,
) -> str:
    label_html = f"<span>{_esc(ref.label)}</span>" if ref.label else ""
    return (
        f'<span class="daily-local-article-reading-brief-ref">{_esc(ref.name)}{label_html}</span>'
    )


def _render_daily_local_source_desk(
    edition: RowOneEdition,
    *,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_hrefs_by_story_id: Mapping[str, str] | None,
) -> str:
    sources = _daily_local_source_desk_sources(
        edition,
        local_articles_by_story_id=local_articles_by_story_id,
        article_hrefs_by_story_id=article_hrefs_by_story_id,
    )
    if not sources:
        return ""
    assert len(sources) <= DAILY_LOCAL_SOURCE_DESK_MAX_SOURCES
    article_count = sum(source.article_count for source in sources)
    paragraph_count = sum(source.saved_paragraph_count for source in sources)
    rendered_sources = "\n".join(
        _render_daily_local_source_desk_source(source) for source in sources
    )
    return f"""<section class="daily-local-source-desk" aria-label="Daily local source desk">
  <div class="daily-local-source-desk-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Daily Local Source Desk</span>
        <span data-lang="zh">每日本地来源台</span>
      </p>
      <h2>
        <span data-lang="en">Which sources carried today&apos;s saved local articles</span>
        <span data-lang="zh">哪些来源承载了今天的本地保存文章</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">
        A source-by-source desk built only from current-edition downloaded local text.
      </span>
      <span data-lang="zh">
        仅基于当前版本已下载本地正文生成的来源视图。
      </span>
    </p>
  </div>
  <div class="daily-local-source-desk-metrics">
    <span>{_esc(_count_label(len(sources), "source", "sources"))}</span>
    <span>{_esc(_count_label(article_count, "local article", "local articles"))}</span>
    <span>{_esc(_count_label(paragraph_count, "saved paragraph", "saved paragraphs"))}</span>
    <span data-lang="en">Homepage only</span>
    <span data-lang="zh">仅首页展示</span>
  </div>
  <div class="daily-local-source-desk-grid">
{rendered_sources}
  </div>
</section>"""


def _daily_local_source_desk_sources(
    edition: RowOneEdition,
    *,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle] | None,
    article_hrefs_by_story_id: Mapping[str, str] | None,
) -> tuple[_DailyLocalSourceDeskSource, ...]:
    if not article_hrefs_by_story_id:
        return ()
    local_articles = local_articles_by_story_id or {}
    groups: dict[
        str,
        dict[
            str,
            object,
        ],
    ] = {}
    for story in edition.stories:
        if not safe_local_article_story_id(story.id):
            continue
        article = local_articles.get(story.id)
        if article is None or article.story_id != story.id:
            continue
        saved_paragraph_count = _usable_local_article_paragraph_count(article)
        if saved_paragraph_count <= 0:
            continue
        source_name = normalize_row_one_paragraph(article.source_name)
        if not source_name:
            continue
        href = _daily_local_source_desk_digest_href(
            story.id,
            article_hrefs_by_story_id.get(story.id),
        )
        paragraph_index = _daily_local_source_desk_first_paragraph_index(article)
        if paragraph_index is None:
            continue
        paragraph_href = _daily_local_source_desk_paragraph_href(
            story.id,
            article_hrefs_by_story_id.get(story.id),
            paragraph_index + 1,
        )
        if href is None or paragraph_href is None:
            continue

        group_key = source_name.casefold()
        group = groups.setdefault(
            group_key,
            {
                "source_name": source_name,
                "article_count": 0,
                "saved_paragraph_count": 0,
                "body_source_labels": [],
                "body_source_keys": set(),
                "references": [],
                "reference_keys": set(),
                "links": [],
            },
        )
        group["article_count"] = int(group["article_count"]) + 1
        group["saved_paragraph_count"] = int(group["saved_paragraph_count"]) + saved_paragraph_count

        body_source_label = row_one_body_source_label(article.body_source)
        body_source_key = (body_source_label.en.casefold(), body_source_label.zh.casefold())
        body_source_keys = group["body_source_keys"]
        body_source_labels = group["body_source_labels"]
        if isinstance(body_source_keys, set) and body_source_key not in body_source_keys:
            body_source_keys.add(body_source_key)
            if isinstance(body_source_labels, list):
                body_source_labels.append(body_source_label)

        references = group["references"]
        reference_keys = group["reference_keys"]
        if isinstance(references, list) and isinstance(reference_keys, set):
            for ref in [*story.entity_refs, *story.product_refs, *story.designer_refs]:
                if len(references) >= DAILY_LOCAL_SOURCE_DESK_MAX_REFS_PER_SOURCE:
                    break
                name = normalize_row_one_paragraph(ref.name)
                label = normalize_row_one_paragraph(ref.label) or normalize_row_one_paragraph(
                    ref.type
                )
                if not name:
                    continue
                key = (
                    name.casefold(),
                    normalize_row_one_paragraph(ref.type).casefold(),
                    normalize_row_one_paragraph(ref.label).casefold(),
                )
                if key in reference_keys:
                    continue
                reference_keys.add(key)
                references.append(_DailyLocalSourceDeskReference(name=name, label=label))

        links = group["links"]
        if isinstance(links, list) and len(links) < DAILY_LOCAL_SOURCE_DESK_MAX_LINKS_PER_SOURCE:
            links.append(
                _DailyLocalSourceDeskLink(
                    story_headline=normalize_row_one_paragraph(story.headline),
                    article_title=normalize_row_one_paragraph(article.title or "") or None,
                    href=href,
                    paragraph_href=paragraph_href,
                    paragraph_number=paragraph_index + 1,
                )
            )

    sources: list[_DailyLocalSourceDeskSource] = []
    for group in groups.values():
        source_name = str(group["source_name"])
        body_source_labels = tuple(group["body_source_labels"])
        references = tuple(group["references"])
        links = tuple(group["links"])
        if not source_name or not links:
            continue
        sources.append(
            _DailyLocalSourceDeskSource(
                source_name=source_name,
                article_count=int(group["article_count"]),
                saved_paragraph_count=int(group["saved_paragraph_count"]),
                body_source_labels=body_source_labels,
                references=references,
                links=links,
            )
        )
    sources.sort(
        key=lambda source: (
            -source.article_count,
            -source.saved_paragraph_count,
            source.source_name.casefold(),
            source.source_name,
        )
    )
    return tuple(sources[:DAILY_LOCAL_SOURCE_DESK_MAX_SOURCES])


def _daily_local_source_desk_first_paragraph_index(article: RowOneLocalArticle) -> int | None:
    for paragraph_index, paragraph in enumerate(article.paragraphs):
        if normalize_row_one_paragraph(paragraph):
            return paragraph_index
    return None


def _daily_local_source_desk_digest_href(
    story_id: str,
    href: object,
) -> str | None:
    page_href = _safe_daily_local_source_desk_page_href(story_id, href)
    if page_href is None:
        return None
    return f"articles/{page_href}#local-article-digest"


def _daily_local_source_desk_paragraph_href(
    story_id: str,
    href: object,
    paragraph_number: int,
) -> str | None:
    page_href = _safe_daily_local_source_desk_page_href(story_id, href)
    if page_href is None or paragraph_number < 1:
        return None
    return f"articles/{page_href}#local-article-paragraph-{paragraph_number}"


def _safe_daily_local_source_desk_page_href(
    story_id: str,
    href: object,
) -> str | None:
    if not safe_local_article_story_id(story_id) or not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if href.startswith((".", "/", "//")):
        return None
    path = PurePosixPath(href)
    if (
        path.is_absolute()
        or len(path.parts) != 1
        or path.name in ("", ".", "..")
        or ".." in path.parts
        or not path.name.endswith(".html")
    ):
        return None
    mapped_story_id = path.name.removesuffix(".html")
    if mapped_story_id != story_id or not safe_local_article_story_id(mapped_story_id):
        return None
    return f"{mapped_story_id}.html"


def _render_daily_local_source_desk_source(source: _DailyLocalSourceDeskSource) -> str:
    counts = (
        '<div class="daily-local-source-desk-counts">'
        f"<span>{_esc(_count_label(source.article_count, 'article', 'articles'))}</span>"
        f"<span>"
        f"{_esc(_count_label(source.saved_paragraph_count, 'paragraph', 'paragraphs'))}"
        f"</span>"
        "</div>"
    )
    body_sources = "".join(
        (
            '<span class="daily-local-source-desk-body-source">'
            f'<span data-lang="en">{_esc(label.en)}</span>'
            f'<span data-lang="zh">{_esc(label.zh)}</span>'
            "</span>"
        )
        for label in source.body_source_labels
    )
    body_sources_html = (
        f'<div class="daily-local-source-desk-body-sources">{body_sources}</div>'
        if body_sources
        else ""
    )
    refs = "".join(_render_daily_local_source_desk_ref(ref) for ref in source.references)
    refs_html = f'<div class="daily-local-source-desk-refs">{refs}</div>' if refs else ""
    links = "\n".join(_render_daily_local_source_desk_link(link) for link in source.links)
    return f"""    <article class="daily-local-source-desk-source">
      <div class="daily-local-source-desk-source-header">
        <h3 class="daily-local-source-desk-source-title">{_esc(source.source_name)}</h3>
        {counts}
      </div>
      {body_sources_html}
      {refs_html}
      <div class="daily-local-source-desk-links">
{links}
      </div>
    </article>"""


def _render_daily_local_source_desk_ref(ref: _DailyLocalSourceDeskReference) -> str:
    label_html = f"<span>{_esc(ref.label)}</span>" if ref.label else ""
    return f'<span class="daily-local-source-desk-ref">{_esc(ref.name)}{label_html}</span>'


def _render_daily_local_source_desk_link(link: _DailyLocalSourceDeskLink) -> str:
    title = link.article_title or link.story_headline
    article_title = (
        '<span class="daily-local-source-desk-link-article-title">'
        f"{_esc(link.article_title)}</span>"
        if link.article_title
        else ""
    )
    paragraph_label_en = f"Paragraph {link.paragraph_number}"
    paragraph_label_zh = f"段落 {link.paragraph_number}"
    return f"""        <article class="daily-local-source-desk-link">
          <a href="{_esc(link.href)}">
            <span>{_esc(title)}</span>
            {article_title}
          </a>
          <a class="daily-local-source-desk-paragraph-link" href="{_esc(link.paragraph_href)}">
            <span data-lang="en">{_esc(paragraph_label_en)}</span>
            <span data-lang="zh">{_esc(paragraph_label_zh)}</span>
          </a>
        </article>"""


def _render_daily_local_coverage_map(
    organization: RowOneSavedArticleContentOrganization | None,
    *,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    hrefs_by_detail_path: Mapping[str, str] | None,
) -> str:
    sources = _daily_local_coverage_map_sources(
        organization,
        local_articles_by_story_id=local_articles_by_story_id,
        hrefs_by_detail_path=hrefs_by_detail_path,
    )
    if not sources:
        return ""
    assert len(sources) <= DAILY_LOCAL_COVERAGE_MAP_MAX_SOURCES
    bucket_count = len(
        {
            (bucket.title.en.casefold(), bucket.title.zh.casefold())
            for source in sources
            for bucket in source.buckets
        }
    )
    article_count = sum(source.article_count for source in sources)
    paragraph_count = sum(source.saved_paragraph_count for source in sources)
    rendered_sources = "\n".join(
        _render_daily_local_coverage_map_source(source) for source in sources
    )
    return f"""<section class="daily-local-coverage-map" aria-label="Daily local coverage map">
  <div class="daily-local-coverage-map-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Daily Local Coverage Map</span>
        <span data-lang="zh">每日本地覆盖地图</span>
      </p>
      <h2>
        <span data-lang="en">Where saved sources support each editorial bucket</span>
        <span data-lang="zh">保存来源如何支撑每个编辑整理桶</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">
        A source-by-organization map built from already-downloaded local article text.
      </span>
      <span data-lang="zh">
        基于已下载本地正文生成的来源与内容整理交叉视图。
      </span>
    </p>
  </div>
  <div class="daily-local-coverage-map-metrics">
    <span>{_esc(_count_label(len(sources), "source", "sources"))}</span>
    <span>{_esc(_count_label(bucket_count, "bucket", "buckets"))}</span>
    <span>{_esc(_count_label(article_count, "local article", "local articles"))}</span>
    <span>{_esc(_count_label(paragraph_count, "saved paragraph", "saved paragraphs"))}</span>
    <span data-lang="en">Homepage only</span>
    <span data-lang="zh">仅首页展示</span>
  </div>
  <div class="daily-local-coverage-map-grid">
{rendered_sources}
  </div>
</section>"""


def _daily_local_coverage_map_sources(
    organization: RowOneSavedArticleContentOrganization | None,
    *,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle] | None,
    hrefs_by_detail_path: Mapping[str, str] | None,
) -> tuple[_DailyLocalCoverageMapSource, ...]:
    if organization is None or not local_articles_by_story_id or not hrefs_by_detail_path:
        return ()
    groups: dict[str, dict[str, object]] = {}
    for organization_group in organization.groups:
        bucket_title = _daily_local_coverage_map_title(organization_group.title)
        if not bucket_title.en and not bucket_title.zh:
            continue
        bucket_key = normalize_row_one_paragraph(organization_group.key).casefold()
        if not bucket_key:
            bucket_key = bucket_title.en.casefold() or bucket_title.zh.casefold()
        for card in organization_group.cards:
            source_name = normalize_row_one_paragraph(card.source_name)
            if not source_name:
                continue
            target = _daily_local_coverage_map_card_target(
                card,
                local_articles_by_story_id=local_articles_by_story_id,
                hrefs_by_detail_path=hrefs_by_detail_path,
            )
            if target is None:
                continue
            story_id, saved_paragraph_count, href = target
            group_key = source_name.casefold()
            source_group = groups.setdefault(
                group_key,
                {
                    "source_name": source_name,
                    "bucket_counts": {},
                    "bucket_titles": {},
                    "article_ids": set(),
                    "saved_paragraph_counts": {},
                    "references": [],
                    "reference_keys": set(),
                    "links": [],
                    "link_hrefs": set(),
                },
            )
            bucket_counts = source_group["bucket_counts"]
            bucket_titles = source_group["bucket_titles"]
            if isinstance(bucket_counts, dict) and isinstance(bucket_titles, dict):
                bucket_counts[bucket_key] = int(bucket_counts.get(bucket_key, 0)) + 1
                bucket_titles.setdefault(bucket_key, bucket_title)

            article_ids = source_group["article_ids"]
            saved_paragraph_counts = source_group["saved_paragraph_counts"]
            if isinstance(article_ids, set) and isinstance(saved_paragraph_counts, dict):
                article_ids.add(story_id)
                saved_paragraph_counts.setdefault(story_id, saved_paragraph_count)

            references = source_group["references"]
            reference_keys = source_group["reference_keys"]
            if isinstance(references, list) and isinstance(reference_keys, set):
                for ref in card.references:
                    if len(references) >= DAILY_LOCAL_COVERAGE_MAP_MAX_REFS_PER_SOURCE:
                        break
                    name = normalize_row_one_paragraph(ref.name)
                    ref_type = normalize_row_one_paragraph(ref.type)
                    label = normalize_row_one_paragraph(ref.label)
                    if not name:
                        continue
                    reference_key = (name.casefold(), ref_type.casefold(), label.casefold())
                    if reference_key in reference_keys:
                        continue
                    reference_keys.add(reference_key)
                    references.append(RowOneReference(name=name, type=ref_type, label=label))

            links = source_group["links"]
            link_hrefs = source_group["link_hrefs"]
            if (
                isinstance(links, list)
                and isinstance(link_hrefs, set)
                and len(links) < DAILY_LOCAL_COVERAGE_MAP_MAX_LINKS_PER_SOURCE
                and href not in link_hrefs
            ):
                link_hrefs.add(href)
                links.append(
                    _DailyLocalCoverageMapLink(
                        title=_daily_local_coverage_map_title(card.title),
                        source_name=source_name,
                        href=href,
                        bucket_title=bucket_title,
                    )
                )

    sources: list[_DailyLocalCoverageMapSource] = []
    for group in groups.values():
        source_name = str(group["source_name"])
        bucket_counts = group["bucket_counts"]
        bucket_titles = group["bucket_titles"]
        article_ids = group["article_ids"]
        saved_paragraph_counts = group["saved_paragraph_counts"]
        references = tuple(group["references"])
        links = tuple(group["links"])
        if (
            not source_name
            or not isinstance(bucket_counts, dict)
            or not isinstance(bucket_titles, dict)
            or not isinstance(article_ids, set)
            or not isinstance(saved_paragraph_counts, dict)
            or not links
        ):
            continue
        buckets = tuple(
            _DailyLocalCoverageMapBucket(
                title=bucket_titles[bucket_key],
                support_count=int(support_count),
            )
            for bucket_key, support_count in list(bucket_counts.items())[
                :DAILY_LOCAL_COVERAGE_MAP_MAX_BUCKETS_PER_SOURCE
            ]
            if bucket_key in bucket_titles and int(support_count) > 0
        )
        if not buckets:
            continue
        sources.append(
            _DailyLocalCoverageMapSource(
                source_name=source_name,
                bucket_count=len(bucket_counts),
                article_count=len(article_ids),
                card_count=sum(int(count) for count in bucket_counts.values()),
                saved_paragraph_count=sum(int(count) for count in saved_paragraph_counts.values()),
                buckets=buckets,
                references=references[:DAILY_LOCAL_COVERAGE_MAP_MAX_REFS_PER_SOURCE],
                links=links[:DAILY_LOCAL_COVERAGE_MAP_MAX_LINKS_PER_SOURCE],
            )
        )
    sources.sort(
        key=lambda source: (
            -source.bucket_count,
            -source.article_count,
            -source.saved_paragraph_count,
            source.source_name.casefold(),
            source.source_name,
        )
    )
    return tuple(sources[:DAILY_LOCAL_COVERAGE_MAP_MAX_SOURCES])


def _daily_local_coverage_map_title(title: LocalizedText) -> LocalizedText:
    return LocalizedText(
        en=normalize_row_one_paragraph(title.en),
        zh=normalize_row_one_paragraph(title.zh),
    )


def _daily_local_coverage_map_card_target(
    card: RowOneSavedArticleContentOrganizationCard,
    *,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    hrefs_by_detail_path: Mapping[str, str],
) -> tuple[str, int, str] | None:
    detail_path, _separator, fragment = card.detail_path.partition("#")
    safe_path = validated_row_one_detail_relative_path(detail_path)
    if safe_path is None:
        return None
    story_id = safe_path.name.removesuffix(".html")
    if not safe_local_article_story_id(story_id):
        return None
    article = local_articles_by_story_id.get(story_id)
    if article is None or article.story_id != story_id:
        return None
    saved_paragraph_count = _usable_local_article_paragraph_count(article)
    if saved_paragraph_count <= 0:
        return None
    page_href = _safe_daily_local_coverage_map_page_href(
        story_id,
        hrefs_by_detail_path.get(str(safe_path)),
    )
    if page_href is None:
        return None
    if _daily_local_coverage_map_content_section_fragment_is_rendered(fragment, article):
        return story_id, saved_paragraph_count, f"articles/{page_href}#{fragment}"
    paragraph_index = _daily_local_coverage_map_paragraph_index(card, article)
    if paragraph_index is None:
        return None
    return (
        story_id,
        saved_paragraph_count,
        f"articles/{page_href}#local-article-paragraph-{paragraph_index + 1}",
    )


def _safe_daily_local_coverage_map_page_href(
    story_id: str,
    href: object,
) -> str | None:
    return _safe_daily_local_source_desk_page_href(story_id, href)


def _daily_local_coverage_map_paragraph_index(
    card: RowOneSavedArticleContentOrganizationCard,
    article: RowOneLocalArticle,
) -> int | None:
    for paragraph_index in card.paragraph_indices:
        safe_index = _safe_saved_article_content_organization_paragraph_index(paragraph_index)
        if safe_index is None or safe_index >= len(article.paragraphs):
            continue
        if normalize_row_one_paragraph(article.paragraphs[safe_index]):
            return safe_index
    for paragraph_index, paragraph in enumerate(article.paragraphs):
        if normalize_row_one_paragraph(paragraph):
            return paragraph_index
    return None


def _daily_local_coverage_map_content_section_fragment_is_rendered(
    fragment: str,
    article: RowOneLocalArticle,
) -> bool:
    match = _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment)
    if match is None:
        return False
    position = int(fragment.rsplit("-", 1)[1])
    if position < 1 or position > len(article.content_sections):
        return False
    rendered_indices = _local_article_rendered_paragraph_indices(article)
    section = article.content_sections[position - 1]
    if section.body is not None:
        return True
    return any(
        _render_local_article_content_item(
            item,
            article=article,
            rendered_indices=rendered_indices,
        )
        for item in section.items
    )


def _render_daily_local_coverage_map_source(source: _DailyLocalCoverageMapSource) -> str:
    counts = (
        '<div class="daily-local-coverage-map-counts">'
        f"<span>{_esc(_count_label(source.bucket_count, 'bucket', 'buckets'))}</span>"
        f"<span>{_esc(_count_label(source.article_count, 'article', 'articles'))}</span>"
        f"<span>{_esc(_count_label(source.card_count, 'card', 'cards'))}</span>"
        f"<span>"
        f"{_esc(_count_label(source.saved_paragraph_count, 'paragraph', 'paragraphs'))}"
        f"</span>"
        "</div>"
    )
    buckets = "".join(_render_daily_local_coverage_map_bucket(bucket) for bucket in source.buckets)
    buckets_html = (
        f'<div class="daily-local-coverage-map-buckets">{buckets}</div>' if buckets else ""
    )
    refs = "".join(_render_daily_local_coverage_map_ref(ref) for ref in source.references)
    refs_html = f'<div class="daily-local-coverage-map-refs">{refs}</div>' if refs else ""
    links = "\n".join(_render_daily_local_coverage_map_link(link) for link in source.links)
    return f"""    <article class="daily-local-coverage-map-source">
      <div class="daily-local-coverage-map-source-header">
        <h3 class="daily-local-coverage-map-source-title">{_esc(source.source_name)}</h3>
        {counts}
      </div>
      {buckets_html}
      {refs_html}
      <div class="daily-local-coverage-map-links">
{links}
      </div>
    </article>"""


def _render_daily_local_coverage_map_bucket(bucket: _DailyLocalCoverageMapBucket) -> str:
    support_label = _count_label(bucket.support_count, "card", "cards")
    return (
        '<span class="daily-local-coverage-map-bucket">'
        f'<span data-lang="en">{_esc(bucket.title.en)}</span>'
        f'<span data-lang="zh">{_esc(bucket.title.zh)}</span>'
        f"<span>{_esc(support_label)}</span>"
        "</span>"
    )


def _render_daily_local_coverage_map_ref(ref: RowOneReference) -> str:
    label = normalize_row_one_paragraph(ref.label) or normalize_row_one_paragraph(ref.type)
    label_html = f"<span>{_esc(label)}</span>" if label else ""
    return f'<span class="daily-local-coverage-map-ref">{_esc(ref.name)}{label_html}</span>'


def _render_daily_local_coverage_map_link(link: _DailyLocalCoverageMapLink) -> str:
    title_en = link.title.en or link.title.zh
    title_zh = link.title.zh or link.title.en
    return f"""        <article class="daily-local-coverage-map-link">
          <a href="{_esc(link.href)}">
            <span data-lang="en">{_esc(title_en)}</span>
            <span data-lang="zh">{_esc(title_zh)}</span>
          </a>
          <span class="daily-local-coverage-map-link-bucket">
            <span data-lang="en">{_esc(link.bucket_title.en)}</span>
            <span data-lang="zh">{_esc(link.bucket_title.zh)}</span>
          </span>
        </article>"""


def _render_daily_local_theme_summary_strip(
    organization: RowOneSavedArticleContentOrganization | None,
    *,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    hrefs_by_detail_path: Mapping[str, str] | None,
) -> str:
    themes = _daily_local_theme_summary_strip_themes(
        organization,
        local_articles_by_story_id=local_articles_by_story_id,
        hrefs_by_detail_path=hrefs_by_detail_path,
    )
    if not themes:
        return ""
    assert len(themes) <= DAILY_LOCAL_THEME_SUMMARY_STRIP_MAX_THEMES
    article_count = sum(theme.article_count for theme in themes)
    card_count = sum(theme.card_count for theme in themes)
    paragraph_count = sum(theme.saved_paragraph_count for theme in themes)
    rendered_themes = "\n".join(
        _render_daily_local_theme_summary_strip_theme(theme) for theme in themes
    )
    return f"""<section class="daily-local-theme-summary-strip"
  aria-label="Daily local theme summary strip">
  <div class="daily-local-theme-summary-strip-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Daily Local Theme Summary Strip</span>
        <span data-lang="zh">每日本地主题摘要条</span>
      </p>
      <h2>
        <span data-lang="en">Theme-level takeaways from saved local text</span>
        <span data-lang="zh">从本地保存正文提炼主题级摘要</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">
        Compact theme cards built from existing organization groups, leads, references, and
        same-site local article anchors.
      </span>
      <span data-lang="zh">
        基于现有整理分组、摘要、引用和站内本地文章锚点生成的紧凑主题卡片。
      </span>
    </p>
  </div>
  <div class="daily-local-theme-summary-strip-metrics">
    <span>{_esc(_count_label(len(themes), "theme", "themes"))}</span>
    <span>{_esc(_count_label(card_count, "card", "cards"))}</span>
    <span>{_esc(_count_label(article_count, "local article", "local articles"))}</span>
    <span>{_esc(_count_label(paragraph_count, "saved paragraph", "saved paragraphs"))}</span>
    <span data-lang="en">Homepage only</span>
    <span data-lang="zh">仅首页展示</span>
  </div>
  <div class="daily-local-theme-summary-strip-grid">
{rendered_themes}
  </div>
</section>"""


def _daily_local_theme_summary_strip_themes(
    organization: RowOneSavedArticleContentOrganization | None,
    *,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle] | None,
    hrefs_by_detail_path: Mapping[str, str] | None,
) -> tuple[_DailyLocalThemeSummaryStripTheme, ...]:
    if organization is None or not local_articles_by_story_id or not hrefs_by_detail_path:
        return ()
    themes: list[_DailyLocalThemeSummaryStripTheme] = []
    for group_index, organization_group in enumerate(organization.groups):
        title = _daily_local_theme_summary_strip_text(organization_group.title)
        if not title.en and not title.zh:
            continue
        source_names: set[str] = set()
        article_ids: set[str] = set()
        saved_paragraph_counts: dict[str, int] = {}
        references: list[RowOneReference] = []
        reference_keys: set[tuple[str, str, str]] = set()
        links: list[_DailyLocalThemeSummaryStripLink] = []
        link_hrefs: set[str] = set()
        summary: LocalizedText | None = None
        card_count = 0

        for card in organization_group.cards:
            source_name = normalize_row_one_paragraph(card.source_name)
            if not source_name:
                continue
            target = _daily_local_theme_summary_strip_card_target(
                card,
                local_articles_by_story_id=local_articles_by_story_id,
                hrefs_by_detail_path=hrefs_by_detail_path,
            )
            if target is None:
                continue
            story_id, saved_paragraph_count, href = target
            card_count += 1
            source_names.add(source_name.casefold())
            article_ids.add(story_id)
            saved_paragraph_counts.setdefault(story_id, saved_paragraph_count)
            if summary is None:
                summary = _daily_local_theme_summary_strip_summary(
                    organization_group.dek,
                    card.lead,
                )
            for ref in card.references:
                if len(references) >= DAILY_LOCAL_THEME_SUMMARY_STRIP_MAX_REFS_PER_THEME:
                    break
                name = normalize_row_one_paragraph(ref.name)
                ref_type = normalize_row_one_paragraph(ref.type)
                label = normalize_row_one_paragraph(ref.label)
                if not name:
                    continue
                reference_key = (name.casefold(), ref_type.casefold(), label.casefold())
                if reference_key in reference_keys:
                    continue
                reference_keys.add(reference_key)
                references.append(RowOneReference(name=name, type=ref_type, label=label))
            if (
                len(links) < DAILY_LOCAL_THEME_SUMMARY_STRIP_MAX_LINKS_PER_THEME
                and href not in link_hrefs
            ):
                link_hrefs.add(href)
                links.append(
                    _DailyLocalThemeSummaryStripLink(
                        title=_daily_local_theme_summary_strip_text(card.title),
                        href=href,
                        source_name=source_name,
                    )
                )

        if card_count <= 0 or not links or summary is None:
            continue
        themes.append(
            _DailyLocalThemeSummaryStripTheme(
                title=title,
                summary=summary,
                card_count=card_count,
                source_count=len(source_names),
                article_count=len(article_ids),
                saved_paragraph_count=sum(int(count) for count in saved_paragraph_counts.values()),
                references=tuple(references),
                links=tuple(links),
                original_index=group_index,
            )
        )
    themes.sort(
        key=lambda theme: (
            -theme.card_count,
            -theme.article_count,
            -theme.saved_paragraph_count,
            theme.original_index,
        )
    )
    return tuple(themes[:DAILY_LOCAL_THEME_SUMMARY_STRIP_MAX_THEMES])


def _daily_local_theme_summary_strip_text(text: LocalizedText) -> LocalizedText:
    return LocalizedText(
        en=normalize_row_one_paragraph(text.en),
        zh=normalize_row_one_paragraph(text.zh),
    )


def _daily_local_theme_summary_strip_summary(
    group_dek: LocalizedText,
    card_lead: LocalizedText,
) -> LocalizedText:
    dek = _daily_local_theme_summary_strip_text(group_dek)
    lead = _daily_local_theme_summary_strip_text(card_lead)
    return LocalizedText(
        en=_daily_local_theme_summary_strip_excerpt(dek.en or lead.en or lead.zh),
        zh=_daily_local_theme_summary_strip_excerpt(dek.zh or lead.zh or lead.en),
    )


def _daily_local_theme_summary_strip_excerpt(text: str) -> str:
    return _meta_description(
        normalize_row_one_paragraph(text),
        limit=DAILY_LOCAL_THEME_SUMMARY_STRIP_SUMMARY_CHARS,
    )


def _daily_local_theme_summary_strip_card_target(
    card: RowOneSavedArticleContentOrganizationCard,
    *,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    hrefs_by_detail_path: Mapping[str, str],
) -> tuple[str, int, str] | None:
    return _daily_local_coverage_map_card_target(
        card,
        local_articles_by_story_id=local_articles_by_story_id,
        hrefs_by_detail_path=hrefs_by_detail_path,
    )


def _render_daily_local_theme_summary_strip_theme(
    theme: _DailyLocalThemeSummaryStripTheme,
) -> str:
    refs = "".join(_render_daily_local_theme_summary_strip_ref(ref) for ref in theme.references)
    refs_html = f'<div class="daily-local-theme-summary-strip-refs">{refs}</div>' if refs else ""
    links = "\n".join(_render_daily_local_theme_summary_strip_link(link) for link in theme.links)
    return f"""    <article class="daily-local-theme-summary-strip-theme">
      <div class="daily-local-theme-summary-strip-theme-header">
        <h3 class="daily-local-theme-summary-strip-title">
          <span data-lang="en">{_esc(theme.title.en)}</span>
          <span data-lang="zh">{_esc(theme.title.zh)}</span>
        </h3>
        <div class="daily-local-theme-summary-strip-meta">
          <span>{_esc(_count_label(theme.card_count, "card", "cards"))}</span>
          <span>{_esc(_count_label(theme.source_count, "source", "sources"))}</span>
          <span>{_esc(_count_label(theme.article_count, "article", "articles"))}</span>
          <span>{_esc(_count_label(theme.saved_paragraph_count, "paragraph", "paragraphs"))}</span>
        </div>
      </div>
      <p class="daily-local-theme-summary-strip-summary">
        <span data-lang="en">{_esc(theme.summary.en)}</span>
        <span data-lang="zh">{_esc(theme.summary.zh)}</span>
      </p>
      {refs_html}
      <div class="daily-local-theme-summary-strip-links">
{links}
      </div>
    </article>"""


def _render_daily_local_theme_summary_strip_ref(ref: RowOneReference) -> str:
    label = normalize_row_one_paragraph(ref.label) or normalize_row_one_paragraph(ref.type)
    label_html = f"<span>{_esc(label)}</span>" if label else ""
    return f'<span class="daily-local-theme-summary-strip-ref">{_esc(ref.name)}{label_html}</span>'


def _render_daily_local_theme_summary_strip_link(
    link: _DailyLocalThemeSummaryStripLink,
) -> str:
    title_en = link.title.en or link.title.zh
    title_zh = link.title.zh or link.title.en
    return f"""        <article class="daily-local-theme-summary-strip-link">
          <a href="{_esc(link.href)}">
            <span data-lang="en">{_esc(title_en)}</span>
            <span data-lang="zh">{_esc(title_zh)}</span>
          </a>
          <span class="daily-local-theme-summary-strip-source">{_esc(link.source_name)}</span>
        </article>"""


def _render_daily_local_news_timeline(
    timeline: RowOneDailyLocalNewsTimeline | None,
) -> str:
    if timeline is None or not timeline.items:
        return ""
    items = [
        item_html
        for item in timeline.items
        if (item_html := _render_daily_local_news_timeline_item(item))
    ]
    if not items:
        return ""
    title_en = normalize_row_one_paragraph(timeline.title.en) or "Daily Local News Timeline"
    title_zh = normalize_row_one_paragraph(timeline.title.zh) or "每日本地新闻时间线"
    dek_en = normalize_row_one_paragraph(timeline.dek.en)
    dek_zh = normalize_row_one_paragraph(timeline.dek.zh)
    return (
        '<section class="daily-local-news-timeline" '
        'aria-labelledby="daily-local-news-timeline-title">\n'
        f"""  <div class="daily-local-news-timeline-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Latest Saved Locally</span>
        <span data-lang="zh">最新本地保存</span>
      </p>
      <h2 id="daily-local-news-timeline-title">
        <span data-lang="en">{_esc(title_en)}</span>
        <span data-lang="zh">{_esc(title_zh)}</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">{_esc(dek_en or dek_zh)}</span>
      <span data-lang="zh">{_esc(dek_zh or dek_en)}</span>
    </p>
  </div>
  <div class="daily-local-news-timeline-meta">
    <span>{_esc(_count_label(len(items), "timed story", "timed stories"))}</span>
    <span>{_esc(_count_label(timeline.source_count, "source", "sources"))}</span>
    <span data-lang="en">Latest {_esc(timeline.latest_label.en)}</span>
    <span data-lang="zh">最新 {_esc(timeline.latest_label.zh)}</span>
  </div>
  <div class="daily-local-news-timeline-list">
{"".join(items)}
  </div>
</section>"""
    )


def _render_daily_local_news_timeline_item(
    item: RowOneDailyLocalNewsTimelineItem,
) -> str:
    href = _safe_daily_local_news_timeline_href(item.href)
    if href is None:
        return ""
    title_en = normalize_row_one_paragraph(item.title.en)
    title_zh = normalize_row_one_paragraph(item.title.zh)
    source_name = normalize_row_one_paragraph(item.source_name)
    excerpt_en = normalize_row_one_paragraph(item.excerpt.en)
    excerpt_zh = normalize_row_one_paragraph(item.excerpt.zh)
    published_en = normalize_row_one_paragraph(item.published_label.en)
    published_zh = normalize_row_one_paragraph(item.published_label.zh)
    if not title_en and not title_zh:
        return ""
    if not excerpt_en and not excerpt_zh:
        return ""
    if not published_en and not published_zh:
        return ""
    return f"""    <article class="daily-local-news-timeline-item">
      <div class="daily-local-news-timeline-date">
        <span data-lang="en">{_esc(published_en or published_zh)}</span>
        <span data-lang="zh">{_esc(published_zh or published_en)}</span>
      </div>
      <a class="daily-local-news-timeline-link" href="{_esc(href)}">
        <span data-lang="en">{_esc(title_en or title_zh)}</span>
        <span data-lang="zh">{_esc(title_zh or title_en)}</span>
      </a>
      <p class="daily-local-news-timeline-source">{_esc(source_name)}</p>
      <p class="daily-local-news-timeline-excerpt">
        <span data-lang="en">{_esc(excerpt_en or excerpt_zh)}</span>
        <span data-lang="zh">{_esc(excerpt_zh or excerpt_en)}</span>
      </p>
    </article>"""


def _safe_daily_local_news_timeline_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if "://" in href or "//" in href or href.startswith((".", "/", "//")):
        return None
    path, separator, fragment = href.partition("#")
    if not separator:
        return None
    route_path = PurePosixPath(path)
    if (
        route_path.is_absolute()
        or len(route_path.parts) != 2
        or route_path.parts[0] != "articles"
        or route_path.name in ("", ".", "..")
        or ".." in route_path.parts
        or not route_path.name.endswith(".html")
    ):
        return None
    story_id = route_path.name.removesuffix(".html")
    if not safe_local_article_story_id(story_id):
        return None
    if _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment) is None:
        return None
    return f"articles/{story_id}.html#{fragment}"


def _render_daily_local_article_intelligence_brief(
    brief: RowOneDailyLocalArticleIntelligenceBrief | None,
) -> str:
    if brief is None or not brief.articles:
        return ""
    rendered_articles = [
        article_html
        for article in brief.articles
        if (article_html := _render_daily_local_article_intelligence_article(article))
    ]
    if not rendered_articles:
        return ""
    lanes = [
        lane_html
        for lane in brief.lanes
        if (lane_html := _render_daily_local_article_intelligence_lane(lane))
    ]
    lanes_html = (
        '<div class="daily-local-article-intelligence-brief-lanes">' + "".join(lanes) + "</div>"
        if lanes
        else ""
    )
    source_names = {
        normalize_row_one_paragraph(article.source_name).casefold()
        for article in brief.articles
        if _safe_daily_local_article_intelligence_href(article.href) is not None
        and normalize_row_one_paragraph(article.source_name)
    }
    article_count = len(rendered_articles)
    source_count = len(source_names) or brief.source_count
    summary_en = (
        f"{_esc(_count_label(article_count, 'local article', 'local articles'))}, "
        f"{_esc(_count_label(source_count, 'source', 'sources'))}, "
        f"{_esc(_count_label(brief.signal_count, 'signal', 'signals'))}, and "
        f"{_esc(_count_label(brief.evidence_count, 'evidence link', 'evidence links'))} "
        "from today's saved local article briefs."
    )
    summary_zh = (
        f"{_esc(str(article_count))} 篇本地文章，{_esc(str(source_count))} 个来源，"
        f"{_esc(str(brief.signal_count))} 个信号，"
        f"{_esc(str(brief.evidence_count))} 条证据链接。"
    )
    return f"""<section class="daily-local-article-intelligence-brief"
  aria-label="Daily local article intelligence brief">
  <div class="daily-local-article-intelligence-brief-header">
    <div>
      <p class="story-section">
        <span data-lang="en">{_esc(brief.title.en)}</span>
        <span data-lang="zh">{_esc(brief.title.zh)}</span>
      </p>
      <h2>
        <span data-lang="en">The edited read from today's saved local articles</span>
        <span data-lang="zh">从今日保存本地文章提炼编辑阅读线索</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">{_esc(brief.opening_signal.en)}</span>
      <span data-lang="zh">{_esc(brief.opening_signal.zh)}</span>
    </p>
  </div>
  <div class="daily-local-article-intelligence-brief-metrics">
    <span>{_esc(_count_label(article_count, "local article", "local articles"))}</span>
    <span>{_esc(_count_label(source_count, "source", "sources"))}</span>
    <span>{_esc(_count_label(brief.signal_count, "signal", "signals"))}</span>
    <span>{_esc(_count_label(brief.evidence_count, "evidence link", "evidence links"))}</span>
    <span data-lang="en">Homepage only</span>
    <span data-lang="zh">仅首页展示</span>
  </div>
  <p class="daily-local-article-intelligence-brief-summary">
    <span data-lang="en">{summary_en}</span>
    <span data-lang="zh">{summary_zh}</span>
  </p>
  {lanes_html}
  <div class="daily-local-article-intelligence-brief-grid">
{"".join(rendered_articles)}
  </div>
</section>"""


def _render_daily_local_article_intelligence_lane(
    lane: RowOneDailyLocalArticleIntelligenceBriefLane,
) -> str:
    chips = [
        chip_html
        for chip in lane.chips
        if (chip_html := _render_daily_local_article_intelligence_chip(chip))
    ]
    if not chips:
        return ""
    return f"""    <article class="daily-local-article-intelligence-brief-lane">
      <div class="daily-local-article-intelligence-brief-lane-header">
        <h3>
          <span data-lang="en">{_esc(lane.title.en)}</span>
          <span data-lang="zh">{_esc(lane.title.zh)}</span>
        </h3>
        <span>{_esc(_count_label(lane.total_count, "signal", "signals"))}</span>
      </div>
      <div class="daily-local-article-intelligence-brief-chips">{"".join(chips)}</div>
    </article>"""


def _render_daily_local_article_intelligence_chip(
    chip: RowOneDailyLocalArticleIntelligenceBriefLaneChip,
) -> str:
    label_en = normalize_row_one_paragraph(chip.label.en)
    label_zh = normalize_row_one_paragraph(chip.label.zh)
    if not label_en and not label_zh:
        return ""
    return f"""<span class="daily-local-article-intelligence-brief-chip">
        <span data-lang="en">{_esc(label_en or label_zh)}</span>
        <span data-lang="zh">{_esc(label_zh or label_en)}</span>
        <span>{_esc(_count_label(chip.support_count, "article", "articles"))}</span>
      </span>"""


def _render_daily_local_article_intelligence_article(
    article: RowOneDailyLocalArticleIntelligenceBriefArticle,
) -> str:
    href = _safe_daily_local_article_intelligence_href(article.href)
    if href is None:
        return ""
    routes = [
        route_html
        for route in article.routes
        if (route_html := _render_daily_local_article_intelligence_route(route))
    ]
    if not routes:
        return ""
    title_en = normalize_row_one_paragraph(article.title.en)
    title_zh = normalize_row_one_paragraph(article.title.zh)
    source_name = normalize_row_one_paragraph(article.source_name)
    opening_en = normalize_row_one_paragraph(article.opening_signal.en)
    opening_zh = normalize_row_one_paragraph(article.opening_signal.zh)
    return f"""    <article class="daily-local-article-intelligence-brief-card">
      <a class="daily-local-article-intelligence-brief-card-title" href="{_esc(href)}">
        <span data-lang="en">{_esc(title_en or title_zh)}</span>
        <span data-lang="zh">{_esc(title_zh or title_en)}</span>
      </a>
      <div class="daily-local-article-intelligence-brief-card-meta">
        <span>{_esc(source_name)}</span>
        <span>{_esc(_count_label(article.evidence_count, "evidence link", "evidence links"))}</span>
      </div>
      <p>
        <span data-lang="en">{_esc(opening_en or opening_zh)}</span>
        <span data-lang="zh">{_esc(opening_zh or opening_en)}</span>
      </p>
      <div class="daily-local-article-intelligence-brief-routes">
{"".join(routes)}
      </div>
    </article>"""


def _render_daily_local_article_intelligence_route(
    route: RowOneDailyLocalArticleIntelligenceBriefRoute,
) -> str:
    href = _safe_daily_local_article_intelligence_href(route.href)
    if href is None:
        return ""
    label_en = normalize_row_one_paragraph(route.label.en)
    label_zh = normalize_row_one_paragraph(route.label.zh)
    if not label_en and not label_zh:
        return ""
    return f"""        <a class="daily-local-article-intelligence-brief-route" href="{_esc(href)}">
          <span data-lang="en">{_esc(label_en or label_zh)}</span>
          <span data-lang="zh">{_esc(label_zh or label_en)}</span>
        </a>"""


def _safe_daily_local_article_intelligence_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if "://" in href or href.startswith((".", "/", "//")) or "//" in href:
        return None
    path, separator, fragment = href.partition("#")
    if not separator:
        return None
    route_path = PurePosixPath(path)
    if (
        route_path.is_absolute()
        or len(route_path.parts) != 2
        or route_path.parts[0] != "articles"
        or route_path.name in ("", ".", "..")
        or ".." in route_path.parts
        or not route_path.name.endswith(".html")
    ):
        return None
    story_id = route_path.name.removesuffix(".html")
    if not safe_local_article_story_id(story_id):
        return None
    if (
        _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment) is None
        and _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment) is None
    ):
        return None
    return f"articles/{story_id}.html#{fragment}"


def _render_daily_local_synthesis_brief(
    brief: RowOneDailyLocalSynthesisBrief | None,
) -> str:
    if brief is None or not brief.cards:
        return ""
    rendered_cards = [
        card_html
        for card in brief.cards
        if (card_html := _render_daily_local_synthesis_brief_card(card))
    ]
    if not rendered_cards:
        return ""
    source_count = brief.source_count
    card_count = len(rendered_cards)
    title_en = normalize_row_one_paragraph(brief.title.en) or "Daily Local Synthesis Brief"
    title_zh = normalize_row_one_paragraph(brief.title.zh) or "每日本地综合简报"
    dek_en = normalize_row_one_paragraph(brief.dek.en)
    dek_zh = normalize_row_one_paragraph(brief.dek.zh)
    opening_en = normalize_row_one_paragraph(brief.opening_read.en)
    opening_zh = normalize_row_one_paragraph(brief.opening_read.zh)
    thesis_en = normalize_row_one_paragraph(brief.thesis.en)
    thesis_zh = normalize_row_one_paragraph(brief.thesis.zh)
    basis_en = normalize_row_one_paragraph(brief.basis_note.en)
    basis_zh = normalize_row_one_paragraph(brief.basis_note.zh)
    thesis_html = (
        f"""  <p class="daily-local-synthesis-brief-thesis">
    <span data-lang="en">{_esc(thesis_en or thesis_zh)}</span>
    <span data-lang="zh">{_esc(thesis_zh or thesis_en)}</span>
  </p>
"""
        if thesis_en or thesis_zh
        else ""
    )
    return (
        '<section class="daily-local-synthesis-brief" '
        'aria-labelledby="daily-local-synthesis-brief-title">'
        f"""
  <div class="daily-local-synthesis-brief-header">
    <div>
      <p class="story-section">
        <span data-lang="en">{_esc(title_en)}</span>
        <span data-lang="zh">{_esc(title_zh)}</span>
      </p>
      <h2 id="daily-local-synthesis-brief-title">
        <span data-lang="en">What today's saved articles add up to</span>
        <span data-lang="zh">今日保存文章共同指向什么</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">{_esc(dek_en or dek_zh)}</span>
      <span data-lang="zh">{_esc(dek_zh or dek_en)}</span>
    </p>
  </div>
  <div class="daily-local-synthesis-brief-metrics">
    <span>{_esc(_count_label(brief.article_count, "local article", "local articles"))}</span>
    <span>{_esc(_count_label(source_count, "source", "sources"))}</span>
    <span>{_esc(_count_label(card_count, "card", "cards"))}</span>
    <span data-lang="en">Homepage only</span>
    <span data-lang="zh">仅首页展示</span>
  </div>
  <p class="daily-local-synthesis-brief-opening">
    <span data-lang="en">{_esc(opening_en or opening_zh)}</span>
    <span data-lang="zh">{_esc(opening_zh or opening_en)}</span>
  </p>
{thesis_html}\
  <div class="daily-local-synthesis-brief-grid">
{"".join(rendered_cards)}
  </div>
  <p class="daily-local-synthesis-brief-basis">
    <span data-lang="en">{_esc(basis_en or basis_zh)}</span>
    <span data-lang="zh">{_esc(basis_zh or basis_en)}</span>
  </p>
</section>"""
    )


def _render_daily_local_synthesis_brief_card(
    card: RowOneDailyLocalSynthesisBriefCard,
) -> str:
    href = _safe_daily_local_synthesis_brief_href(card.href)
    if href is None:
        return ""
    title_en = normalize_row_one_paragraph(card.title.en)
    title_zh = normalize_row_one_paragraph(card.title.zh)
    source_name = normalize_row_one_paragraph(card.source_name)
    read_en = normalize_row_one_paragraph(card.read.en)
    read_zh = normalize_row_one_paragraph(card.read.zh)
    adds_en = normalize_row_one_paragraph(card.adds.en)
    adds_zh = normalize_row_one_paragraph(card.adds.zh)
    route_label_en = normalize_row_one_paragraph(card.route_label.en) or "Read the saved article"
    route_label_zh = normalize_row_one_paragraph(card.route_label.zh) or "阅读保存文章"
    evidence_links = [
        link_html
        for link in card.evidence_links
        if (link_html := _render_daily_local_synthesis_evidence_link(link))
    ]
    evidence_html = (
        f"""      <div class="daily-local-synthesis-brief-evidence-trail">
        <p>
          <span data-lang="en">Evidence Trail</span>
          <span data-lang="zh">证据线索</span>
        </p>
{"".join(evidence_links)}      </div>
"""
        if evidence_links
        else ""
    )
    return f"""    <article class="daily-local-synthesis-brief-card">
      <div class="daily-local-synthesis-brief-card-meta">
        <span>{_esc(source_name)}</span>
        <span data-lang="en">Article-backed</span>
        <span data-lang="zh">文章支持</span>
      </div>
      <h3>
        <span data-lang="en">{_esc(title_en or title_zh)}</span>
        <span data-lang="zh">{_esc(title_zh or title_en)}</span>
      </h3>
      <p>
        <span data-lang="en">{_esc(read_en or read_zh)}</span>
        <span data-lang="zh">{_esc(read_zh or read_en)}</span>
      </p>
      <p>
        <span data-lang="en">{_esc(adds_en or adds_zh)}</span>
        <span data-lang="zh">{_esc(adds_zh or adds_en)}</span>
      </p>
{evidence_html}\
      <a class="daily-local-synthesis-brief-route" href="{_esc(href)}">
        <span data-lang="en">{_esc(route_label_en)}</span>
        <span data-lang="zh">{_esc(route_label_zh)}</span>
      </a>
    </article>"""


def _render_daily_local_synthesis_evidence_link(
    link: RowOneDailyLocalSynthesisEvidenceLink,
) -> str:
    href = _safe_daily_local_synthesis_evidence_href(link.href)
    label_en = normalize_row_one_paragraph(link.label.en)
    label_zh = normalize_row_one_paragraph(link.label.zh)
    if href is None or not (label_en or label_zh):
        return ""
    support_en = normalize_row_one_paragraph(link.support.en) if link.support else ""
    support_zh = normalize_row_one_paragraph(link.support.zh) if link.support else ""
    support_html = (
        f"""        <span class="daily-local-synthesis-brief-evidence-support">
          <span data-lang="en">{_esc(support_en or support_zh)}</span>
          <span data-lang="zh">{_esc(support_zh or support_en)}</span>
        </span>
"""
        if support_en or support_zh
        else ""
    )
    return f"""      <a class="daily-local-synthesis-brief-evidence-link" href="{_esc(href)}">
        <span class="daily-local-synthesis-brief-evidence-label">
          <span data-lang="en">{_esc(label_en or label_zh)}</span>
          <span data-lang="zh">{_esc(label_zh or label_en)}</span>
        </span>
{support_html}      </a>
"""


def _safe_daily_local_synthesis_evidence_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if "://" in href or "//" in href or "?" in href or href.startswith((".", "/", "//")):
        return None
    path_text, separator, fragment = href.partition("#")
    if separator != "#":
        return None
    page_href = _safe_daily_local_synthesis_brief_href(path_text)
    if page_href is None:
        return None
    if (
        _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment) is None
        and _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment) is None
    ):
        return None
    return f"{page_href}#{fragment}"


def _safe_daily_local_synthesis_brief_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if (
        "://" in href
        or "//" in href
        or "?" in href
        or "#" in href
        or href.startswith((".", "/", "//"))
    ):
        return None
    path = PurePosixPath(href)
    if (
        path.is_absolute()
        or len(path.parts) != 1
        or path.name in ("", ".", "..", "index.html")
        or ".." in path.parts
        or not path.name.endswith(".html")
    ):
        return None
    story_id = path.name.removesuffix(".html")
    if not safe_local_article_story_id(story_id):
        return None
    return f"articles/{story_id}.html"


def _render_daily_local_saved_text_takeaways(
    takeaways: RowOneDailyLocalSavedTextTakeaways | None,
) -> str:
    if takeaways is None or not takeaways.lanes:
        return ""
    lanes = [
        lane_html
        for lane in takeaways.lanes
        if (lane_html := _render_daily_local_saved_text_takeaway_lane(lane))
    ]
    if not lanes:
        return ""
    title_en = normalize_row_one_paragraph(takeaways.title.en) or "Daily Saved Text Takeaways"
    title_zh = normalize_row_one_paragraph(takeaways.title.zh) or "每日保存正文要点"
    dek_en = normalize_row_one_paragraph(takeaways.dek.en)
    dek_zh = normalize_row_one_paragraph(takeaways.dek.zh)
    metrics = (
        _render_daily_local_saved_text_takeaway_metric(
            _count_label(takeaways.article_count, "article", "articles"),
            f"{takeaways.article_count} 篇文章",
        )
        + _render_daily_local_saved_text_takeaway_metric(
            _count_label(takeaways.source_count, "source", "sources"),
            f"{takeaways.source_count} 个来源",
        )
        + _render_daily_local_saved_text_takeaway_metric(
            _count_label(takeaways.card_count, "excerpt", "excerpts"),
            f"{takeaways.card_count} 条短摘",
        )
    )
    return f"""<section class="daily-local-saved-text-takeaways"
  aria-labelledby="daily-local-saved-text-takeaways-title">
  <div class="daily-local-saved-text-takeaways-header">
    <div>
      <p class="story-section">
        <span data-lang="en">{_esc(title_en)}</span>
        <span data-lang="zh">{_esc(title_zh)}</span>
      </p>
      <h2 id="daily-local-saved-text-takeaways-title">
        <span data-lang="en">Saved article text, sorted into daily takeaways</span>
        <span data-lang="zh">保存正文已整理成今日要点</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">{_esc(dek_en or dek_zh)}</span>
      <span data-lang="zh">{_esc(dek_zh or dek_en)}</span>
    </p>
  </div>
  <div class="daily-local-saved-text-takeaways-metrics">{metrics}</div>
  <div class="daily-local-saved-text-takeaways-grid">{"".join(lanes)}</div>
</section>"""


def _render_daily_local_saved_text_takeaway_metric(value_en: str, value_zh: str) -> str:
    return (
        "<span>"
        f'<span data-lang="en">{_esc(value_en)}</span>'
        f'<span data-lang="zh">{_esc(value_zh)}</span>'
        "</span>"
    )


def _render_daily_local_saved_text_takeaway_lane(
    lane: RowOneDailyLocalSavedTextTakeawayLane,
) -> str:
    cards = [
        card_html
        for card in lane.cards
        if (card_html := _render_daily_local_saved_text_takeaway_card(card))
    ]
    if not cards:
        return ""
    title_en = normalize_row_one_paragraph(lane.title.en)
    title_zh = normalize_row_one_paragraph(lane.title.zh)
    dek_en = normalize_row_one_paragraph(lane.dek.en)
    dek_zh = normalize_row_one_paragraph(lane.dek.zh)
    total_count = lane.total_count if lane.total_count > 0 else len(cards)
    return f"""    <article class="daily-local-saved-text-takeaways-lane">
      <div class="daily-local-saved-text-takeaways-lane-header">
        <h3>
          <span data-lang="en">{_esc(title_en or title_zh)}</span>
          <span data-lang="zh">{_esc(title_zh or title_en)}</span>
        </h3>
        <span class="daily-local-saved-text-takeaways-lane-count">
          <span data-lang="en">{_esc(_count_label(total_count, "excerpt", "excerpts"))}</span>
          <span data-lang="zh">{_esc(f"{total_count} 条短摘")}</span>
        </span>
        <p>
          <span data-lang="en">{_esc(dek_en or dek_zh)}</span>
          <span data-lang="zh">{_esc(dek_zh or dek_en)}</span>
        </p>
      </div>
      <div class="daily-local-saved-text-takeaways-cards">{"".join(cards)}</div>
    </article>"""


def _render_daily_local_saved_text_takeaway_card(
    card: RowOneDailyLocalSavedTextTakeawayCard,
) -> str:
    href = _safe_daily_local_saved_text_takeaway_href(card.href)
    if href is None:
        return ""
    title_en = normalize_row_one_paragraph(card.title.en)
    title_zh = normalize_row_one_paragraph(card.title.zh)
    source_name = normalize_row_one_paragraph(card.source_name)
    label_en = normalize_row_one_paragraph(card.label.en)
    label_zh = normalize_row_one_paragraph(card.label.zh)
    excerpt_en = normalize_row_one_paragraph(card.excerpt.en)
    excerpt_zh = normalize_row_one_paragraph(card.excerpt.zh)
    if not (title_en or title_zh) or not (excerpt_en or excerpt_zh):
        return ""
    return f"""        <article class="daily-local-saved-text-takeaways-card">
          <div class="daily-local-saved-text-takeaways-card-meta">
            <span>{_esc(source_name)}</span>
            <span>
              <span data-lang="en">{_esc(label_en or label_zh)}</span>
              <span data-lang="zh">{_esc(label_zh or label_en)}</span>
            </span>
          </div>
          <h4>
            <span data-lang="en">{_esc(title_en or title_zh)}</span>
            <span data-lang="zh">{_esc(title_zh or title_en)}</span>
          </h4>
          <p>
            <span data-lang="en">{_esc(excerpt_en or excerpt_zh)}</span>
            <span data-lang="zh">{_esc(excerpt_zh or excerpt_en)}</span>
          </p>
          <a class="daily-local-saved-text-takeaways-card-link" href="{_esc(href)}">
            <span data-lang="en">Open saved-text anchor</span>
            <span data-lang="zh">打开保存正文锚点</span>
          </a>
        </article>"""


def _safe_daily_local_saved_text_takeaway_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if "://" in href or "//" in href or "?" in href or href.startswith((".", "/", "//")):
        return None
    path, separator, fragment = href.partition("#")
    if not separator or not fragment:
        return None
    route_path = PurePosixPath(path)
    if (
        route_path.is_absolute()
        or len(route_path.parts) != 2
        or route_path.parts[0] != "articles"
        or route_path.name in ("", ".", "..")
        or ".." in route_path.parts
        or not route_path.name.endswith(".html")
    ):
        return None
    story_id = route_path.name.removesuffix(".html")
    if not safe_local_article_story_id(story_id):
        return None
    if (
        _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment) is None
        and _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment) is None
    ):
        return None
    return f"articles/{story_id}.html#{fragment}"


def _render_daily_local_brand_product_people_signal_digest(
    digest: RowOneDailyLocalBrandProductPeopleSignalDigest | None,
) -> str:
    if digest is None or not digest.buckets:
        return ""
    rendered_buckets = []
    for bucket_key in ("brands", "products", "people"):
        for bucket in digest.buckets:
            if bucket.key != bucket_key:
                continue
            rendered = _render_daily_local_brand_product_people_signal_digest_bucket(bucket)
            if rendered is not None:
                rendered_buckets.append(rendered)
                break
    if not rendered_buckets:
        return ""
    entity_count = sum(item_count for _bucket_html, item_count in rendered_buckets)
    buckets = "".join(bucket_html for bucket_html, _item_count in rendered_buckets)
    title_en = normalize_row_one_paragraph(digest.title.en)
    title_zh = normalize_row_one_paragraph(digest.title.zh)
    dek_en = normalize_row_one_paragraph(digest.dek.en)
    dek_zh = normalize_row_one_paragraph(digest.dek.zh)
    metrics = (
        _render_daily_local_brand_product_people_signal_digest_metric(
            _count_label(digest.article_count, "article", "articles"),
            f"{digest.article_count} 篇文章",
        )
        + _render_daily_local_brand_product_people_signal_digest_metric(
            _count_label(digest.source_count, "source", "sources"),
            f"{digest.source_count} 个来源",
        )
        + _render_daily_local_brand_product_people_signal_digest_metric(
            _count_label(entity_count, "entity", "entities"),
            f"{entity_count} 个实体",
        )
    )
    return f"""<section class="daily-local-brand-product-people-signal-digest"
  aria-labelledby="daily-local-brand-product-people-signal-digest-title">
  <div class="daily-local-brand-product-people-signal-digest-header">
    <div>
      <p class="story-section">
        <span data-lang="en">{_esc(title_en or title_zh)}</span>
        <span data-lang="zh">{_esc(title_zh or title_en)}</span>
      </p>
      <h2 id="daily-local-brand-product-people-signal-digest-title">
        <span data-lang="en">Brands, products, and people in saved local article text</span>
        <span data-lang="zh">保存本地文章正文中的品牌、单品与人物</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">{_esc(dek_en or dek_zh)}</span>
      <span data-lang="zh">{_esc(dek_zh or dek_en)}</span>
    </p>
  </div>
  <div class="daily-local-brand-product-people-signal-digest-metrics">{metrics}</div>
  <div class="daily-local-brand-product-people-signal-digest-grid">{buckets}</div>
</section>"""


def _render_daily_local_brand_product_people_signal_digest_metric(
    value_en: str,
    value_zh: str,
) -> str:
    return (
        "<span>"
        f'<span data-lang="en">{_esc(value_en)}</span>'
        f'<span data-lang="zh">{_esc(value_zh)}</span>'
        "</span>"
    )


def _render_daily_local_brand_product_people_signal_digest_bucket(
    bucket: RowOneDailyLocalBrandProductPeopleSignalDigestBucket,
) -> tuple[str, int] | None:
    items = []
    for item in bucket.items:
        item_html = _render_daily_local_brand_product_people_signal_digest_item(item)
        if not item_html:
            continue
        items.append(item_html)
        if len(items) >= DAILY_LOCAL_BRAND_PRODUCT_PEOPLE_SIGNAL_DIGEST_ITEM_LIMIT:
            break
    if not items:
        return None
    title_en = normalize_row_one_paragraph(bucket.title.en)
    title_zh = normalize_row_one_paragraph(bucket.title.zh)
    item_count = len(items)
    return (
        f"""    <article class="daily-local-brand-product-people-signal-digest-bucket">
      <div class="daily-local-brand-product-people-signal-digest-bucket-header">
        <h3>
          <span data-lang="en">{_esc(title_en or title_zh)}</span>
          <span data-lang="zh">{_esc(title_zh or title_en)}</span>
        </h3>
        <span>
          <span data-lang="en">{_esc(_count_label(item_count, "entity", "entities"))}</span>
          <span data-lang="zh">{_esc(f"{item_count} 个实体")}</span>
        </span>
      </div>
      <div class="daily-local-brand-product-people-signal-digest-items">{"".join(items)}</div>
    </article>""",
        item_count,
    )


def _render_daily_local_brand_product_people_signal_digest_item(
    item: RowOneDailyLocalBrandProductPeopleSignalDigestItem,
) -> str:
    supports = []
    for support in item.supports:
        support_html = _render_daily_local_brand_product_people_signal_digest_support(support)
        if not support_html:
            continue
        supports.append(support_html)
        if len(supports) >= DAILY_LOCAL_BRAND_PRODUCT_PEOPLE_SIGNAL_DIGEST_SUPPORT_LIMIT:
            break
    if not supports:
        return ""
    name_en = normalize_row_one_paragraph(item.name.en)
    name_zh = normalize_row_one_paragraph(item.name.zh)
    if not (name_en or name_zh):
        return ""
    reference_type = _daily_local_brand_product_people_signal_digest_type_label(item.reference_type)
    article_count_en = _count_label(item.article_count, "article", "articles")
    article_count_zh = f"{item.article_count} 篇文章"
    source_count_en = _count_label(item.source_count, "source", "sources")
    source_count_zh = f"{item.source_count} 个来源"
    supports_html = "".join(supports)
    return f"""        <article class="daily-local-brand-product-people-signal-digest-item">
          <div class="daily-local-brand-product-people-signal-digest-item-meta">
            <span>
              <span data-lang="en">{_esc(article_count_en)}</span>
              <span data-lang="zh">{_esc(article_count_zh)}</span>
            </span>
            <span>
              <span data-lang="en">{_esc(source_count_en)}</span>
              <span data-lang="zh">{_esc(source_count_zh)}</span>
            </span>
            <span>
              <span data-lang="en">{_esc(reference_type.en)}</span>
              <span data-lang="zh">{_esc(reference_type.zh)}</span>
            </span>
          </div>
          <h4>
            <span data-lang="en">{_esc(name_en or name_zh)}</span>
            <span data-lang="zh">{_esc(name_zh or name_en)}</span>
          </h4>
          <div class="daily-local-brand-product-people-signal-digest-supports">
{supports_html}
          </div>
        </article>"""


def _daily_local_brand_product_people_signal_digest_type_label(value: str) -> LocalizedText:
    normalized = normalize_row_one_paragraph(value)
    key = normalized.replace("_", " ").replace("-", " ").casefold()
    labels = {
        "brand": "品牌",
        "product": "单品",
        "person": "人物",
        "people": "人物",
        "designer": "设计师",
        "creative director": "创意总监",
        "bag": "手袋",
        "shoe": "鞋履",
        "sneaker": "运动鞋",
        "accessory": "配饰",
    }
    return LocalizedText(en=normalized or "reference", zh=labels.get(key, "引用"))


def _render_daily_local_brand_product_people_signal_digest_support(
    support: RowOneDailyLocalBrandProductPeopleSignalDigestSupport,
) -> str:
    href = _safe_daily_local_brand_product_people_signal_digest_href(support.href)
    if href is None:
        return ""
    title_en = normalize_row_one_paragraph(support.title.en)
    title_zh = normalize_row_one_paragraph(support.title.zh)
    label_en = normalize_row_one_paragraph(support.label.en)
    label_zh = normalize_row_one_paragraph(support.label.zh)
    excerpt_en = _truncate_daily_local_brand_product_people_signal_digest_excerpt(
        normalize_row_one_paragraph(support.excerpt.en)
    )
    excerpt_zh = _truncate_daily_local_brand_product_people_signal_digest_excerpt(
        normalize_row_one_paragraph(support.excerpt.zh)
    )
    if not (title_en or title_zh) or not (excerpt_en or excerpt_zh):
        return ""
    source_name = normalize_row_one_paragraph(support.source_name)
    source_en = source_name or "Saved local article"
    source_zh = source_name or "保存的本地文章"
    link_title_en = title_en or title_zh
    link_title_zh = title_zh or title_en
    return f"""            <article class="daily-local-brand-product-people-signal-digest-support">
              <div class="daily-local-brand-product-people-signal-digest-support-meta">
                <span>
                  <span data-lang="en">{_esc(source_en)}</span>
                  <span data-lang="zh">{_esc(source_zh)}</span>
                </span>
                <span>
                  <span data-lang="en">{_esc(label_en or label_zh)}</span>
                  <span data-lang="zh">{_esc(label_zh or label_en)}</span>
                </span>
              </div>
              <h5>
                <span data-lang="en">{_esc(title_en or title_zh)}</span>
                <span data-lang="zh">{_esc(title_zh or title_en)}</span>
              </h5>
              <p class="daily-local-brand-product-people-signal-digest-support-excerpt">
                <span data-lang="en">{_esc(excerpt_en or excerpt_zh)}</span>
                <span data-lang="zh">{_esc(excerpt_zh or excerpt_en)}</span>
              </p>
              <a class="daily-local-brand-product-people-signal-digest-link" href="{_esc(href)}">
                <span data-lang="en">Open saved evidence: {_esc(link_title_en)}</span>
                <span data-lang="zh">打开保存证据：{_esc(link_title_zh)}</span>
              </a>
            </article>"""


def _truncate_daily_local_brand_product_people_signal_digest_excerpt(value: str) -> str:
    if len(value) <= DAILY_LOCAL_BRAND_PRODUCT_PEOPLE_SIGNAL_DIGEST_EXCERPT_CHARS:
        return value
    return (
        f"{value[: DAILY_LOCAL_BRAND_PRODUCT_PEOPLE_SIGNAL_DIGEST_EXCERPT_CHARS - 3].rstrip()}..."
    )


def _safe_daily_local_brand_product_people_signal_digest_href(
    href: object,
) -> str | None:
    if not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if "//" in href or "://" in href or "?" in href or href.startswith((".", "/")):
        return None
    path, separator, fragment = href.partition("#")
    if separator != "#" or _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment) is None:
        return None
    route_path = PurePosixPath(path)
    if (
        route_path.is_absolute()
        or len(route_path.parts) != 2
        or route_path.parts[0] != "articles"
        or route_path.name in ("", ".", "..")
        or ".." in route_path.parts
        or not route_path.name.endswith(".html")
    ):
        return None
    story_id = route_path.name.removesuffix(".html")
    if not safe_local_article_story_id(story_id):
        return None
    return f"articles/{story_id}.html#{fragment}"


def _render_daily_local_saved_article_organizer(
    organizer: RowOneDailyLocalSavedArticleOrganizer | None,
) -> str:
    if organizer is None or not organizer.lanes:
        return ""
    lanes = [
        lane_html
        for lane in organizer.lanes
        if (lane_html := _render_daily_local_saved_article_organizer_lane(lane))
    ]
    if not lanes:
        return ""
    lane_count = len(lanes)
    safe_cards = _daily_local_saved_article_organizer_safe_cards(organizer)
    source_count = _daily_local_saved_article_organizer_source_count(safe_cards)
    reference_count = sum(len(card.references) for card in safe_cards)
    metrics = (
        _render_daily_local_saved_article_organizer_metric(
            _count_label(lane_count, "lane", "lanes"),
            f"{lane_count} 条阅读线",
        )
        + _render_daily_local_saved_article_organizer_metric(
            _count_label(len(safe_cards), "card", "cards"),
            f"{len(safe_cards)} 张卡片",
        )
        + _render_daily_local_saved_article_organizer_metric(
            _count_label(source_count, "source", "sources"),
            f"{source_count} 个来源",
        )
        + _render_daily_local_saved_article_organizer_metric(
            _count_label(reference_count, "reference", "references"),
            f"{reference_count} 个引用",
        )
    )
    title_en = (
        normalize_row_one_paragraph(organizer.title.en) or "Daily Local Saved Article Organizer"
    )
    title_zh = normalize_row_one_paragraph(organizer.title.zh) or "每日保存文章整理器"
    dek_en = normalize_row_one_paragraph(organizer.dek.en)
    dek_zh = normalize_row_one_paragraph(organizer.dek.zh)
    return f"""<section class="daily-local-saved-article-organizer"
  aria-label="Daily local saved article organizer">
  <div class="daily-local-saved-article-organizer-header">
    <div>
      <p class="story-section">
        <span data-lang="en">{_esc(title_en)}</span>
        <span data-lang="zh">{_esc(title_zh)}</span>
      </p>
      <h2>
        <span data-lang="en">Organized lanes from today's saved local articles</span>
        <span data-lang="zh">从今日保存本地文章整理阅读分栏</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">{_esc(dek_en or dek_zh)}</span>
      <span data-lang="zh">{_esc(dek_zh or dek_en)}</span>
    </p>
  </div>
  <div class="daily-local-saved-article-organizer-metrics">{metrics}</div>
  <div class="daily-local-saved-article-organizer-lanes">{"".join(lanes)}</div>
</section>"""


def _daily_local_saved_article_organizer_safe_cards(
    organizer: RowOneDailyLocalSavedArticleOrganizer,
) -> tuple[RowOneDailyLocalSavedArticleOrganizerCard, ...]:
    return tuple(
        card
        for lane in organizer.lanes
        for card in lane.cards
        if _safe_daily_local_saved_article_organizer_href(card.href) is not None
    )


def _daily_local_saved_article_organizer_source_count(
    cards: Sequence[RowOneDailyLocalSavedArticleOrganizerCard],
) -> int:
    source_names = {
        source_name.casefold()
        for card in cards
        if (source_name := normalize_row_one_paragraph(card.source_name))
    }
    return len(source_names)


def _render_daily_local_saved_article_organizer_metric(
    value_en: str,
    value_zh: str,
) -> str:
    return (
        "<span>"
        f'<span data-lang="en">{_esc(value_en)}</span>'
        f'<span data-lang="zh">{_esc(value_zh)}</span>'
        "</span>"
    )


def _render_daily_local_saved_article_organizer_lane(
    lane: RowOneDailyLocalSavedArticleOrganizerLane,
) -> str:
    cards = [
        card_html
        for card in lane.cards
        if (card_html := _render_daily_local_saved_article_organizer_card(card))
    ]
    if not cards:
        return ""
    title_en = normalize_row_one_paragraph(lane.title.en)
    title_zh = normalize_row_one_paragraph(lane.title.zh)
    dek_en = normalize_row_one_paragraph(lane.dek.en)
    dek_zh = normalize_row_one_paragraph(lane.dek.zh)
    rendered_count = len(cards)
    total_count = lane.total_count if lane.total_count > 0 else rendered_count
    return f"""    <article class="daily-local-saved-article-organizer-lane">
      <div class="daily-local-saved-article-organizer-lane-header">
        <h3>
          <span data-lang="en">{_esc(title_en or title_zh)}</span>
          <span data-lang="zh">{_esc(title_zh or title_en)}</span>
        </h3>
        <span class="daily-local-saved-article-organizer-lane-count">
          <span data-lang="en">{_esc(_count_label(total_count, "card", "cards"))}</span>
          <span data-lang="zh">{_esc(f"{total_count} 张卡片")}</span>
        </span>
        <p>
          <span data-lang="en">{_esc(dek_en or dek_zh)}</span>
          <span data-lang="zh">{_esc(dek_zh or dek_en)}</span>
        </p>
      </div>
      <div class="daily-local-saved-article-organizer-cards">{"".join(cards)}</div>
    </article>"""


def _render_daily_local_saved_article_organizer_card(
    card: RowOneDailyLocalSavedArticleOrganizerCard,
) -> str:
    href = _safe_daily_local_saved_article_organizer_href(card.href)
    if href is None:
        return ""
    title_en = normalize_row_one_paragraph(card.title.en)
    title_zh = normalize_row_one_paragraph(card.title.zh)
    source_name = normalize_row_one_paragraph(card.source_name)
    lane_label_en = normalize_row_one_paragraph(card.lane_label.en)
    lane_label_zh = normalize_row_one_paragraph(card.lane_label.zh)
    excerpt_en = normalize_row_one_paragraph(card.excerpt.en)
    excerpt_zh = normalize_row_one_paragraph(card.excerpt.zh)
    refs = "".join(_render_daily_local_saved_article_organizer_ref(ref) for ref in card.references)
    refs_html = (
        f'\n        <div class="daily-local-saved-article-organizer-refs">{refs}</div>'
        if refs
        else ""
    )
    return f"""        <article class="daily-local-saved-article-organizer-card">
          <div class="daily-local-saved-article-organizer-card-meta">
            <span>{_esc(source_name)}</span>
            <span>
              <span data-lang="en">{_esc(lane_label_en or lane_label_zh)}</span>
              <span data-lang="zh">{_esc(lane_label_zh or lane_label_en)}</span>
            </span>
          </div>
          <h4>
            <span data-lang="en">{_esc(title_en or title_zh)}</span>
            <span data-lang="zh">{_esc(title_zh or title_en)}</span>
          </h4>
          <p>
            <span data-lang="en">{_esc(excerpt_en or excerpt_zh)}</span>
            <span data-lang="zh">{_esc(excerpt_zh or excerpt_en)}</span>
          </p>{refs_html}
          <a class="daily-local-saved-article-organizer-card-link" href="{_esc(href)}">
            <span data-lang="en">Open saved article anchor</span>
            <span data-lang="zh">打开保存文章锚点</span>
          </a>
        </article>"""


def _render_daily_local_saved_article_organizer_ref(
    ref: RowOneDailyLocalSavedArticleOrganizerReference,
) -> str:
    name = normalize_row_one_paragraph(ref.name)
    if not name:
        return ""
    label = normalize_row_one_paragraph(ref.label)
    label_html = f"<span>{_esc(label)}</span>" if label else ""
    return (
        '<span class="daily-local-saved-article-organizer-ref">'
        f"<span>{_esc(name)}</span>{label_html}"
        "</span>"
    )


def _safe_daily_local_saved_article_organizer_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if "://" in href or href.startswith((".", "/", "//")) or "//" in href:
        return None
    path, separator, fragment = href.partition("#")
    if not separator or not fragment:
        return None
    route_path = PurePosixPath(path)
    if (
        route_path.is_absolute()
        or len(route_path.parts) != 2
        or route_path.parts[0] != "articles"
        or route_path.name in ("", ".", "..")
        or ".." in route_path.parts
        or not route_path.name.endswith(".html")
    ):
        return None
    story_id = route_path.name.removesuffix(".html")
    if not safe_local_article_story_id(story_id):
        return None
    section_match = _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment)
    paragraph_match = _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment)
    if section_match is None and paragraph_match is None:
        return None
    return f"articles/{story_id}.html#{fragment}"


def _render_daily_local_reading_itinerary(
    itinerary: RowOneDailyLocalReadingItinerary | None,
) -> str:
    if itinerary is None:
        return ""
    start_card = (
        _render_daily_local_reading_itinerary_card(itinerary.start_here, featured=True)
        if itinerary.start_here is not None
        else ""
    )
    skim_cards = [
        card_html
        for card in itinerary.skim_next
        if (card_html := _render_daily_local_reading_itinerary_card(card))
    ]
    if not start_card and not skim_cards:
        return ""
    evidence_chips = [
        chip_html
        for evidence in itinerary.evidence_trail
        if (chip_html := _render_daily_local_reading_itinerary_evidence(evidence))
    ]
    safe_cards = _daily_local_reading_itinerary_safe_cards(itinerary)
    source_count = _daily_local_reading_itinerary_source_count(safe_cards)
    selected_count = _daily_local_reading_itinerary_story_count(safe_cards)
    evidence_count = len(evidence_chips)
    metrics = (
        _render_daily_local_reading_itinerary_metric(
            _count_label(selected_count, "selected read", "selected reads"),
            f"{selected_count} 条选读",
        )
        + _render_daily_local_reading_itinerary_metric(
            _count_label(source_count, "source", "sources"),
            f"{source_count} 个来源",
        )
        + _render_daily_local_reading_itinerary_metric(
            _count_label(evidence_count, "evidence link", "evidence links"),
            f"{evidence_count} 条证据链接",
        )
    )
    title_en = normalize_row_one_paragraph(itinerary.title.en) or "Daily Local Reading Itinerary"
    title_zh = normalize_row_one_paragraph(itinerary.title.zh) or "每日本地阅读路径"
    dek_en = normalize_row_one_paragraph(itinerary.dek.en)
    dek_zh = normalize_row_one_paragraph(itinerary.dek.zh)
    skim_section = (
        f"""    <div class="daily-local-reading-itinerary-panel">
      <h3>
        <span data-lang="en">Skim Next</span>
        <span data-lang="zh">随后快读</span>
      </h3>
      <div class="daily-local-reading-itinerary-stack">{"".join(skim_cards)}</div>
    </div>"""
        if skim_cards
        else ""
    )
    evidence_section = (
        f"""    <div class="daily-local-reading-itinerary-panel">
      <h3>
        <span data-lang="en">Evidence Trail</span>
        <span data-lang="zh">证据路径</span>
      </h3>
      <div class="daily-local-reading-itinerary-evidence">{"".join(evidence_chips)}</div>
    </div>"""
        if evidence_chips
        else ""
    )
    return f"""<section class="daily-local-reading-itinerary"
  aria-label="Daily local reading itinerary">
  <div class="daily-local-reading-itinerary-header">
    <div>
      <p class="story-section">
        <span data-lang="en">{_esc(title_en)}</span>
        <span data-lang="zh">{_esc(title_zh)}</span>
      </p>
      <h2>
        <span data-lang="en">Start here, skim next, verify the trail</span>
        <span data-lang="zh">先读重点，再看线索，最后核验证据</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">{_esc(dek_en or dek_zh)}</span>
      <span data-lang="zh">{_esc(dek_zh or dek_en)}</span>
    </p>
  </div>
  <div class="daily-local-reading-itinerary-metrics">{metrics}</div>
  <div class="daily-local-reading-itinerary-grid">
    <div class="daily-local-reading-itinerary-panel">
      <h3>
        <span data-lang="en">Start Here</span>
        <span data-lang="zh">先读这篇</span>
      </h3>
      {start_card}
    </div>
{skim_section}
{evidence_section}
  </div>
</section>"""


def _daily_local_reading_itinerary_safe_cards(
    itinerary: RowOneDailyLocalReadingItinerary,
) -> tuple[RowOneDailyLocalReadingItineraryCard, ...]:
    cards = []
    if itinerary.start_here is not None:
        cards.append(itinerary.start_here)
    cards.extend(itinerary.skim_next)
    return tuple(
        card for card in cards if _safe_daily_local_reading_itinerary_href(card.href) is not None
    )


def _daily_local_reading_itinerary_source_count(
    cards: Sequence[RowOneDailyLocalReadingItineraryCard],
) -> int:
    source_names = {
        source_name.casefold()
        for card in cards
        if (source_name := normalize_row_one_paragraph(card.source_name))
    }
    return len(source_names)


def _daily_local_reading_itinerary_story_count(
    cards: Sequence[RowOneDailyLocalReadingItineraryCard],
) -> int:
    story_ids = {
        story_id
        for card in cards
        if (href := _safe_daily_local_reading_itinerary_href(card.href)) is not None
        and (story_id := PurePosixPath(href.partition("#")[0]).name.removesuffix(".html"))
    }
    return len(story_ids)


def _render_daily_local_reading_itinerary_metric(value_en: str, value_zh: str) -> str:
    return (
        "<span>"
        f'<span data-lang="en">{_esc(value_en)}</span>'
        f'<span data-lang="zh">{_esc(value_zh)}</span>'
        "</span>"
    )


def _render_daily_local_reading_itinerary_card(
    card: RowOneDailyLocalReadingItineraryCard | None,
    *,
    featured: bool = False,
) -> str:
    if card is None:
        return ""
    href = _safe_daily_local_reading_itinerary_href(card.href)
    if href is None:
        return ""
    title_en = normalize_row_one_paragraph(card.title.en)
    title_zh = normalize_row_one_paragraph(card.title.zh)
    source_name = normalize_row_one_paragraph(card.source_name)
    reason_en = normalize_row_one_paragraph(card.reason.en)
    reason_zh = normalize_row_one_paragraph(card.reason.zh)
    excerpt_en = normalize_row_one_paragraph(card.excerpt.en)
    excerpt_zh = normalize_row_one_paragraph(card.excerpt.zh)
    labels = "".join(_render_daily_local_reading_itinerary_label(label) for label in card.labels)
    labels_html = (
        f'\n        <div class="daily-local-reading-itinerary-labels">{labels}</div>'
        if labels
        else ""
    )
    class_name = "daily-local-reading-itinerary-card"
    if featured:
        class_name += " daily-local-reading-itinerary-start"
    return f"""        <article class="{class_name}">
          <div class="daily-local-reading-itinerary-card-meta">
            <span>{_esc(source_name)}</span>
            <span>
              <span data-lang="en">{_esc(reason_en or reason_zh)}</span>
              <span data-lang="zh">{_esc(reason_zh or reason_en)}</span>
            </span>
          </div>
          <h4>
            <span data-lang="en">{_esc(title_en or title_zh)}</span>
            <span data-lang="zh">{_esc(title_zh or title_en)}</span>
          </h4>
          <p>
            <span data-lang="en">{_esc(excerpt_en or excerpt_zh)}</span>
            <span data-lang="zh">{_esc(excerpt_zh or excerpt_en)}</span>
          </p>{labels_html}
          <a class="daily-local-reading-itinerary-card-link" href="{_esc(href)}">
            <span data-lang="en">Open saved article anchor</span>
            <span data-lang="zh">打开保存文章锚点</span>
          </a>
        </article>"""


def _render_daily_local_reading_itinerary_label(label: str) -> str:
    safe_label = normalize_row_one_paragraph(label)
    if not safe_label:
        return ""
    return f'<span class="daily-local-reading-itinerary-label">{_esc(safe_label)}</span>'


def _render_daily_local_reading_itinerary_evidence(
    evidence: RowOneDailyLocalReadingItineraryEvidence,
) -> str:
    href = _safe_daily_local_reading_itinerary_href(evidence.href)
    label = normalize_row_one_paragraph(evidence.label)
    if href is None or not label:
        return ""
    return f'<a class="daily-local-reading-itinerary-chip" href="{_esc(href)}">{_esc(label)}</a>'


def _safe_daily_local_reading_itinerary_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if "://" in href or href.startswith((".", "/", "//")) or "//" in href:
        return None
    path, separator, fragment = href.partition("#")
    if not separator or not fragment:
        return None
    route_path = PurePosixPath(path)
    if (
        route_path.is_absolute()
        or len(route_path.parts) != 2
        or route_path.parts[0] != "articles"
        or route_path.name in ("", ".", "..")
        or ".." in route_path.parts
        or not route_path.name.endswith(".html")
    ):
        return None
    story_id = route_path.name.removesuffix(".html")
    if not safe_local_article_story_id(story_id):
        return None
    if (
        _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment) is None
        and _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment) is None
    ):
        return None
    return f"articles/{story_id}.html#{fragment}"


def _localized_payload_text(value: object) -> LocalizedText:
    if isinstance(value, dict):
        zh = value.get("zh")
        en = value.get("en")
        zh_text = str(zh) if zh is not None else ""
        en_text = str(en) if en is not None else ""
        return LocalizedText(zh=zh_text, en=en_text)
    if value is None:
        return LocalizedText(zh="", en="")
    text = str(value)
    return LocalizedText(zh=text, en=text)


def _daily_local_heat_signal_subtype_label(source_refs: object) -> str | None:
    if not isinstance(source_refs, list):
        return None
    for source_ref in source_refs:
        if not isinstance(source_ref, dict):
            continue
        normalized_tokens: set[str] = set()
        for field in ("type", "label"):
            normalized = normalize_row_one_paragraph(str(source_ref.get(field) or "")).casefold()
            normalized_tokens.update(
                token for token in re.split(r"[^a-z0-9]+", normalized) if token
            )
        for token, label in (
            ("bag", "Bag"),
            ("handbag", "Bag"),
            ("sneaker", "Sneaker"),
            ("boot", "Boot"),
            ("flat", "Flat"),
            ("heel", "Heel"),
            ("sandal", "Sandal"),
            ("footwear", "Shoe"),
            ("shoe", "Shoe"),
        ):
            if token in normalized_tokens:
                return label
    return None


def _positive_int_value(value: object) -> int:
    if isinstance(value, int) and not isinstance(value, bool) and value > 0:
        return value
    return 0


def _nonnegative_int_value(value: object) -> int:
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    return 0


def _daily_local_heat_signal_topic_sort_key(
    topic: _DailyLocalHeatSignalTopic,
) -> tuple[object, ...]:
    return (
        -topic.positive_heat_delta_sum,
        -topic.max_heat_delta,
        -topic.local_article_count,
        -topic.evidence_count,
        topic.title.en.casefold(),
        topic.title.en,
    )


def _render_daily_local_heat_signal_topic(topic: _DailyLocalHeatSignalTopic) -> str:
    badges = _render_daily_local_heat_signal_topic_badges(topic)
    metrics = _render_daily_local_heat_signal_topic_metrics(topic)
    stories = "\n".join(_render_daily_local_heat_signal_story(story) for story in topic.stories)
    return f"""    <article class="daily-local-heat-signals-topic">
      <div class="daily-local-heat-signals-topic-header">
        <div>
          <p class="daily-local-heat-signals-topic-title">
            <span data-lang="en">{_esc(topic.title.en)}</span>
            <span data-lang="zh">{_esc(topic.title.zh)}</span>
          </p>
          {badges}
        </div>
        {metrics}
      </div>
      <ul class="daily-local-heat-signals-topic-stories">
{stories}
      </ul>
    </article>"""


def _render_daily_local_heat_signal_topic_badges(
    topic: _DailyLocalHeatSignalTopic,
) -> str:
    badges = [
        (
            "<span>"
            f'<span data-lang="en">{_esc(topic.label.en)}</span>'
            f'<span data-lang="zh">{_esc(topic.label.zh)}</span>'
            "</span>"
        )
    ]
    if topic.subtype_label is not None:
        badges.append(f"<span>{_esc(topic.subtype_label)}</span>")
    return '<div class="daily-local-heat-signals-topic-badges">' + "".join(badges) + "</div>"


def _render_daily_local_heat_signal_topic_metrics(
    topic: _DailyLocalHeatSignalTopic,
) -> str:
    story_count_en = _count_label(topic.story_count, "story", "stories")
    evidence_count_en = _count_label(topic.evidence_count, "evidence link", "evidence links")
    return f"""<div class="daily-local-heat-signals-topic-metrics">
          <span>+{topic.positive_heat_delta_sum}</span>
          <span data-lang="en">{_esc(story_count_en)}</span>
          <span data-lang="zh">{_esc(f"{topic.story_count} 条故事")}</span>
          <span data-lang="en">{_esc(evidence_count_en)}</span>
          <span data-lang="zh">{_esc(f"{topic.evidence_count} 条线索")}</span>
        </div>"""


def _render_daily_local_heat_signal_story(story: _DailyLocalHeatSignalStory) -> str:
    source = (
        f"<span>{_esc(story.source_name)}</span>"
        if story.source_name
        else (
            '<span data-lang="en">Saved local article</span>'
            '<span data-lang="zh">本地保存正文</span>'
        )
    )
    return f"""        <li class="daily-local-heat-signals-story">
          <a href="{_esc(story.href)}">
            <span data-lang="en">{_esc(story.title.en)}</span>
            <span data-lang="zh">{_esc(story.title.zh)}</span>
          </a>
          <span class="daily-local-heat-signals-story-meta">
            {source}
          </span>
        </li>"""


def _render_saved_signal_index(
    index: RowOneSavedSignalIndex | None,
    *,
    section_id: str | None = None,
) -> str:
    if not _has_saved_signal_index_entries(index):
        return ""
    cards = [_render_saved_signal_index_card(entry) for entry in index.entries]
    cards = [card for card in cards if card]
    if not cards:
        return ""
    id_attr = f' id="{_esc(section_id)}"' if section_id else ""
    return f"""<section class="saved-signal-index"{id_attr} aria-label="Saved signal index">
  <div class="saved-signal-index-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Saved Signal Index</span>
        <span data-lang="zh">本地信号索引</span>
      </p>
      <h2>
        <span data-lang="en">Saved Signal Index</span>
        <span data-lang="zh">本地信号索引</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">Browse the saved local article set by tracked fashion signals.</span>
      <span data-lang="zh">按已追踪的时尚信号浏览本地保存文章。</span>
    </p>
  </div>
  {_render_saved_signal_index_metrics(index)}
  <div class="saved-signal-index-grid">{"".join(cards)}</div>
</section>"""


def _render_saved_signal_index_metrics(index: RowOneSavedSignalIndex) -> str:
    metrics = [
        _render_saved_article_library_metric(
            _count_label(index.signal_count, "saved signal", "saved signals"),
            f"{index.signal_count} 个本地信号",
        ),
        _render_saved_article_library_metric(
            _count_label(
                index.supporting_article_count,
                "supporting article",
                "supporting articles",
            ),
            f"{index.supporting_article_count} 篇支撑文章",
        ),
        _render_saved_article_library_metric(
            _count_label(index.source_count, "source", "sources"),
            f"{index.source_count} 个来源",
        ),
        _render_saved_article_library_metric(
            _count_label(
                index.supporting_paragraph_count,
                "supporting paragraph",
                "supporting paragraphs",
            ),
            f"{index.supporting_paragraph_count} 个支撑段落",
        ),
    ]
    return '<ul class="saved-signal-index-metrics">\n' + "\n".join(metrics) + "\n  </ul>"


def _render_saved_signal_index_card(entry: RowOneSavedSignalIndexEntry) -> str:
    support = _render_saved_signal_index_support(entry.supports)
    article_count = _count_label(entry.article_count, "article", "articles")
    source_count = _count_label(entry.source_count, "source", "sources")
    paragraph_count = _count_label(
        entry.supporting_paragraph_count,
        "supporting paragraph",
        "supporting paragraphs",
    )
    return f"""    <article class="saved-signal-index-card">
      <div class="saved-signal-index-card-header">
        <div class="saved-signal-index-card-meta">
          <span>{_esc(entry.type)}</span>
          <span>{_esc(entry.label)}</span>
        </div>
        <h3>{_esc(entry.name)}</h3>
        <div class="saved-signal-index-card-meta">
          <span data-lang="en">{_esc(article_count)}</span>
          <span data-lang="zh">{_esc(f"{entry.article_count} 篇文章")}</span>
          <span data-lang="en">{_esc(source_count)}</span>
          <span data-lang="zh">{_esc(f"{entry.source_count} 个来源")}</span>
          <span data-lang="en">{_esc(paragraph_count)}</span>
          <span data-lang="zh">{_esc(f"{entry.supporting_paragraph_count} 个支撑段落")}</span>
        </div>
      </div>
      {support}
    </article>"""


def _render_saved_signal_index_support(
    supports: Sequence[RowOneSavedSignalIndexSupport],
) -> str:
    rows = [_render_saved_signal_index_support_row(support) for support in supports]
    rows = [row for row in rows if row]
    if not rows:
        return ""
    return '<div class="saved-signal-index-support">' + "".join(rows) + "</div>"


def _render_saved_signal_index_support_row(
    support: RowOneSavedSignalIndexSupport,
) -> str:
    actions = _render_saved_signal_actions(support)
    paragraphs = _render_saved_signal_paragraphs(support.paragraph_links)
    excerpt = _render_saved_signal_support_excerpt(support.excerpt)
    return f"""<div class="saved-signal-index-support-row">
        <strong>
          <span data-lang="en">{_esc(support.title.en)}</span>
          <span data-lang="zh">{_esc(support.title.zh)}</span>
        </strong>
        <div class="saved-signal-index-support-meta">
          <span>{_esc(support.source_name)}</span>
          <span>
            <span data-lang="en">{_esc(support.section_title.en)}</span>
            <span data-lang="zh">{_esc(support.section_title.zh)}</span>
          </span>
          <span>
            <span data-lang="en">{_esc(support.content_section_title.en)}</span>
            <span data-lang="zh">{_esc(support.content_section_title.zh)}</span>
          </span>
        </div>
        {excerpt}
        {actions}
        {paragraphs}
      </div>"""


def _render_saved_signal_support_excerpt(excerpt: LocalizedText | None) -> str:
    if excerpt is None:
        return ""
    return f"""<p class="saved-signal-index-support-excerpt">
          <span data-lang="en">{_esc(excerpt.en)}</span>
          <span data-lang="zh">{_esc(excerpt.zh)}</span>
        </p>"""


def _render_saved_signal_actions(support: RowOneSavedSignalIndexSupport) -> str:
    href = _safe_saved_signal_section_href(support.section_path)
    if href is None:
        return ""
    return f"""<div class="saved-signal-index-actions">
          <a href="{_esc(_saved_article_library_page_href(href))}">
            <span data-lang="en">Open organized section</span>
            <span data-lang="zh">打开整理栏目</span>
          </a>
        </div>"""


def _render_saved_signal_paragraphs(
    paragraph_links: Sequence[RowOneSavedSignalIndexParagraphLink],
) -> str:
    links = []
    for paragraph_link in paragraph_links:
        href = _safe_saved_signal_paragraph_href(paragraph_link.href)
        if href is None:
            continue
        links.append(
            f"""<a href="{_esc(_saved_article_library_page_href(href))}">
            <span data-lang="en">{_esc(paragraph_link.label.en)}</span>
            <span data-lang="zh">{_esc(paragraph_link.label.zh)}</span>
          </a>"""
        )
    if not links:
        return ""
    return '<div class="saved-signal-index-paragraphs">' + "".join(links) + "</div>"


def _safe_saved_signal_section_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    path, separator, fragment = href.partition("#")
    if not separator:
        return None
    safe_path = validated_row_one_detail_relative_path(path)
    if safe_path is None:
        return None
    if _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment) is None:
        return None
    return f"{safe_path}#{fragment}"


def _safe_saved_signal_paragraph_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    path, separator, fragment = href.partition("#")
    if not separator:
        return None
    safe_path = validated_row_one_detail_relative_path(path)
    if safe_path is None:
        return None
    if _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment) is None:
        return None
    return f"{safe_path}#{fragment}"


def _render_saved_article_briefs(briefs: RowOneSavedArticleBriefs | None) -> str:
    if briefs is None:
        return ""
    cards = [_render_saved_article_brief_card(item) for item in briefs.items]
    cards = [card for card in cards if card]
    if not cards:
        return ""
    return f"""<section class="saved-article-briefs" aria-label="Saved article briefs">
  <div class="saved-article-briefs-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Saved Article Briefs</span>
        <span data-lang="zh">保存正文简报</span>
      </p>
      <h2>
        <span data-lang="en">Saved Article Briefs</span>
        <span data-lang="zh">保存正文简报</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">Readable saved-article takeaways from today's local source bodies.</span>
      <span data-lang="zh">来自今日本地保存正文的可读文章要点。</span>
    </p>
  </div>
  <div class="saved-article-briefs-grid">{"".join(cards)}</div>
</section>"""


def _render_saved_article_brief_card(item: RowOneSavedArticleBriefItem) -> str:
    href = safe_row_one_detail_fragment_href(item.detail_path, "local-article-digest")
    if href is None:
        return ""
    people_brands = _render_saved_article_brief_chip_group(
        item.people_brands,
        heading_en="People & Brands",
        heading_zh="品牌与人物",
    )
    products = _render_saved_article_brief_chip_group(
        item.products,
        heading_en="Products",
        heading_zh="产品",
    )
    chip_groups = people_brands + products
    chip_group_block = (
        f'\n      <div class="saved-article-brief-chip-groups">{chip_groups}\n      </div>'
        if chip_groups
        else ""
    )
    return f"""    <a class="saved-article-brief-card" href="{_esc(href)}">
      <div class="saved-article-brief-meta">
        <span>{_esc(item.source_name)}</span>
        <span>
          <span data-lang="en">{_esc(item.section_title.en)}</span>
          <span data-lang="zh">{_esc(item.section_title.zh)}</span>
        </span>
      </div>
      <h3>
        <span data-lang="en">{_esc(item.title.en)}</span>
        <span data-lang="zh">{_esc(item.title.zh)}</span>
      </h3>
      <p class="saved-article-brief-body">
        <span data-lang="en">{_esc(_local_article_digest_excerpt(item.lead.en))}</span>
        <span data-lang="zh">{_esc(_local_article_digest_excerpt(item.lead.zh))}</span>
      </p>{chip_group_block}
    </a>"""


def _render_saved_article_brief_chip_group(
    refs: Sequence[RowOneReference],
    *,
    heading_en: str,
    heading_zh: str,
) -> str:
    if not refs:
        return ""
    chips = "".join(_render_saved_article_brief_chip(ref) for ref in refs)
    return f"""
        <div class="saved-article-brief-chip-group">
          <span class="saved-article-brief-chip-heading">
            <span data-lang="en">{_esc(heading_en)}</span>
            <span data-lang="zh">{_esc(heading_zh)}</span>
          </span>
          <span class="saved-article-brief-chip-list">{chips}</span>
        </div>"""


def _render_saved_article_brief_chip(ref: RowOneReference) -> str:
    label = ref.label.strip() or ref.type.strip()
    return (
        '<span class="saved-article-brief-chip">'
        f"<span>{_esc(ref.name)}</span>"
        f"<span>{_esc(label)}</span>"
        "</span>"
    )


def _render_daily_local_key_signals_digest(
    digest: RowOneDailyLocalKeySignalsDigest | None,
) -> str:
    if digest is None:
        return ""
    groups = [
        group_html
        for group in digest.groups
        if (group_html := _render_daily_local_key_signals_digest_group(group))
    ]
    if not groups:
        return ""
    metrics = _render_daily_local_key_signals_digest_metrics(digest, len(groups))
    return f"""<section class="daily-local-key-signals-digest"
  aria-label="Daily local key signals digest">
  <div class="daily-local-key-signals-digest-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Daily Local Key Signals Digest</span>
        <span data-lang="zh">每日本地关键信号摘要</span>
      </p>
      <h2>
        <span data-lang="en">{_esc(digest.title.en)}</span>
        <span data-lang="zh">{_esc(digest.title.zh)}</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">{_esc(digest.dek.en)}</span>
      <span data-lang="zh">{_esc(digest.dek.zh)}</span>
    </p>
  </div>
  {metrics}
  <div class="daily-local-key-signals-digest-grid">{"".join(groups)}</div>
</section>"""


def _render_daily_local_key_signals_digest_metrics(
    digest: RowOneDailyLocalKeySignalsDigest,
    rendered_group_count: int,
) -> str:
    total_signals = sum(group.total_count for group in digest.groups)
    metrics = (
        _count_label(digest.article_count, "article", "articles"),
        _count_label(rendered_group_count, "signal group", "signal groups"),
        _count_label(total_signals, "total signal", "total signals"),
    )
    return (
        '<div class="daily-local-key-signals-digest-metrics">'
        + "".join(f"<span>{_esc(metric)}</span>" for metric in metrics)
        + "</div>"
    )


def _render_daily_local_key_signals_digest_group(
    group: RowOneDailyLocalKeySignalsDigestGroup,
) -> str:
    entries = [
        entry_html
        for entry in group.entries
        if (entry_html := _render_daily_local_key_signals_digest_entry(entry))
    ]
    if not entries:
        return ""
    total = _count_label(group.total_count, "total signal", "total signals")
    return f"""    <article class="daily-local-key-signals-digest-group">
      <h3>
        <span data-lang="en">{_esc(group.title.en)}</span>
        <span data-lang="zh">{_esc(group.title.zh)}</span>
      </h3>
      <p class="daily-local-key-signals-digest-total">{_esc(total)}</p>
      {"".join(entries)}
    </article>"""


def _render_daily_local_key_signals_digest_entry(
    entry: RowOneDailyLocalKeySignalsDigestEntry,
) -> str:
    href = _safe_daily_local_key_signals_digest_href(entry.href)
    if href is None:
        return ""
    body = ""
    if entry.body is not None and (entry.body.en.strip() or entry.body.zh.strip()):
        body = f"""
        <p>
          <span data-lang="en">{_esc(entry.body.en)}</span>
          <span data-lang="zh">{_esc(entry.body.zh)}</span>
        </p>"""
    support_count = max(entry.support_count, 1)
    support_label = _count_label(
        support_count,
        "supporting article",
        "supporting articles",
    )
    source = entry.source_name.strip()
    source_meta = f"<span>{_esc(source)}</span>" if source else ""
    return f"""      <div class="daily-local-key-signals-digest-entry">
        <h4>
          <span data-lang="en">{_esc(entry.title.en)}</span>
          <span data-lang="zh">{_esc(entry.title.zh)}</span>
        </h4>{body}
        <div class="daily-local-key-signals-digest-meta">
          {source_meta}
          <span>{_esc(support_label)}</span>
        </div>
        <a class="daily-local-key-signals-digest-action" href="{_esc(href)}">
          <span data-lang="en">Open local signal</span>
          <span data-lang="zh">打开本地信号</span>
        </a>
      </div>"""


def _safe_daily_local_key_signals_digest_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if href.startswith(("/", ".", "//")):
        return None
    if href.lower().startswith(("http:", "https:", "javascript:", "data:")):
        return None
    path, separator, fragment = href.partition("#")
    if not separator:
        return None
    safe_path = PurePosixPath(path)
    if (
        safe_path.is_absolute()
        or len(safe_path.parts) != 2
        or safe_path.parts[0] != "articles"
        or safe_path.parts[1] in ("", ".", "..")
        or ".." in safe_path.parts
        or not safe_path.name.endswith(".html")
    ):
        return None
    story_id = safe_path.name.removesuffix(".html")
    if not safe_local_article_story_id(story_id):
        return None
    if fragment != "saved-article-key-signals-title" and not (
        _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment)
        or _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment)
    ):
        return None
    return f"articles/{story_id}.html#{fragment}"


def _render_saved_article_content_organization(
    organization: RowOneSavedArticleContentOrganization | None,
    *,
    href_prefix: str = "",
    section_id: str | None = None,
) -> str:
    if organization is None:
        return ""
    groups = [
        _render_saved_article_content_organization_group(group, href_prefix=href_prefix)
        for group in organization.groups
    ]
    groups = [group for group in groups if group]
    if not groups:
        return ""
    coverage_matrix = _render_saved_article_organization_coverage_matrix(
        organization,
        href_prefix=href_prefix,
    )
    id_attr = f' id="{_esc(section_id)}"' if section_id else ""
    return f"""<section class="saved-article-content-organization"{id_attr}
  aria-label="Saved article content organization">
  <div class="saved-article-content-organization-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Saved Article Content Organization</span>
        <span data-lang="zh">保存正文内容整理</span>
      </p>
      <h2>
        <span data-lang="en">Saved Article Content Organization</span>
        <span data-lang="zh">保存正文内容整理</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">Scan-first groupings from locally saved article bodies.</span>
      <span data-lang="zh">从本地保存正文中提炼的快速浏览分组。</span>
    </p>
  </div>
{coverage_matrix}
  <div class="saved-article-content-organization-groups">{"".join(groups)}</div>
</section>"""


@dataclass(frozen=True)
class _SavedArticleOrganizationCoverageRow:
    title: LocalizedText
    source_name: str
    href: str
    group_titles: tuple[LocalizedText, ...]
    section_count: int
    evidence_count: int
    references: tuple[RowOneReference, ...]


def _render_saved_article_organization_coverage_matrix(
    organization: RowOneSavedArticleContentOrganization | None,
    *,
    href_prefix: str = "",
) -> str:
    rows = _saved_article_organization_coverage_rows(organization)
    if not rows:
        return ""
    rendered_rows = "".join(
        _render_saved_article_organization_coverage_row(row, href_prefix=href_prefix)
        for row in rows[:SAVED_ARTICLE_ORGANIZATION_COVERAGE_MAX_ROWS]
    )
    dek_en = "Article-by-article coverage across existing saved organization groups."
    return f"""  <div class="saved-article-organization-coverage-matrix"
    role="region"
    aria-label="Saved article organization coverage matrix">
    <div class="saved-article-organization-coverage-header">
      <h3>
        <span data-lang="en">Organization Coverage Matrix</span>
        <span data-lang="zh">正文整理覆盖矩阵</span>
      </h3>
      <p>
        <span data-lang="en">{_esc(dek_en)}</span>
        <span data-lang="zh">按文章查看其覆盖了哪些已保存正文整理分组。</span>
      </p>
    </div>
    <div class="saved-article-organization-coverage-grid">{rendered_rows}</div>
  </div>"""


def _saved_article_organization_coverage_rows(
    organization: RowOneSavedArticleContentOrganization | None,
) -> tuple[_SavedArticleOrganizationCoverageRow, ...]:
    if organization is None:
        return ()
    rows: dict[str, dict[str, object]] = {}
    ordered_detail_paths: list[str] = []
    for group in organization.groups:
        for card in group.cards:
            href = _safe_saved_article_content_organization_href(card.detail_path)
            if href is None:
                continue
            detail_path = _saved_article_content_organization_detail_path_key(href)
            if not detail_path:
                continue
            if detail_path not in rows:
                rows[detail_path] = {
                    "title": card.title,
                    "source_name": normalize_row_one_paragraph(card.source_name),
                    "href": href,
                    "groups": {},
                    "section_count": 0,
                    "evidence": set(),
                    "refs": [],
                    "seen_refs": set(),
                }
                ordered_detail_paths.append(detail_path)
            row = rows[detail_path]
            groups = row["groups"]
            if isinstance(groups, dict):
                groups.setdefault(group.key, group.title)
            row["section_count"] = int(row["section_count"]) + 1
            evidence = row["evidence"]
            if isinstance(evidence, set):
                for raw_paragraph_index in card.paragraph_indices:
                    paragraph_index = _safe_saved_article_content_organization_paragraph_index(
                        raw_paragraph_index
                    )
                    if paragraph_index is None:
                        continue
                    evidence_href = _safe_saved_article_content_organization_evidence_href(
                        href,
                        paragraph_index,
                    )
                    if evidence_href is None:
                        continue
                    evidence.add(paragraph_index)
            refs = row["refs"]
            seen_refs = row["seen_refs"]
            if isinstance(refs, list) and isinstance(seen_refs, set):
                for ref in card.references:
                    if len(refs) >= SAVED_ARTICLE_ORGANIZATION_COVERAGE_MAX_REFS:
                        break
                    name = normalize_row_one_paragraph(ref.name)
                    ref_type = normalize_row_one_paragraph(ref.type)
                    label = normalize_row_one_paragraph(ref.label)
                    if not name:
                        continue
                    key = (name.casefold(), ref_type.casefold(), label.casefold())
                    if key in seen_refs:
                        continue
                    seen_refs.add(key)
                    refs.append(RowOneReference(name=name, type=ref_type, label=label))
                    if len(refs) >= SAVED_ARTICLE_ORGANIZATION_COVERAGE_MAX_REFS:
                        break

    rendered_rows: list[_SavedArticleOrganizationCoverageRow] = []
    for detail_path in ordered_detail_paths:
        row = rows[detail_path]
        group_titles = row["groups"]
        evidence = row["evidence"]
        references = row["refs"]
        if not isinstance(group_titles, dict):
            group_titles = {}
        if not isinstance(evidence, set):
            evidence = set()
        if not isinstance(references, list):
            references = []
        rendered_rows.append(
            _SavedArticleOrganizationCoverageRow(
                title=row["title"],
                source_name=str(row["source_name"]),
                href=str(row["href"]),
                group_titles=tuple(group_titles.values()),
                section_count=int(row["section_count"]),
                evidence_count=len(evidence),
                references=tuple(references[:SAVED_ARTICLE_ORGANIZATION_COVERAGE_MAX_REFS]),
            )
        )
    return tuple(rendered_rows)


def _render_saved_article_organization_coverage_row(
    row: _SavedArticleOrganizationCoverageRow,
    *,
    href_prefix: str = "",
) -> str:
    href = _prefixed_saved_article_content_organization_href(row.href, href_prefix)
    group_chips = "".join(
        '<span class="saved-article-organization-coverage-chip">'
        f'<span data-lang="en">{_esc(group_title.en)}</span>'
        f'<span data-lang="zh">{_esc(group_title.zh)}</span>'
        "</span>"
        for group_title in row.group_titles
    )
    ref_chips = "".join(
        '<span class="saved-article-organization-coverage-ref">'
        f"<span>{_esc(ref.name)}</span>"
        f"<span>{_esc(ref.label.strip() or ref.type.strip())}</span>"
        "</span>"
        for ref in row.references
    )
    section_label = _count_label(
        row.section_count,
        "organized section",
        "organized sections",
    )
    evidence_label = _count_label(
        row.evidence_count,
        "evidence paragraph",
        "evidence paragraphs",
    )
    return f"""      <article class="saved-article-organization-coverage-row">
        <div class="saved-article-organization-coverage-title">
          <h4>
            <span data-lang="en">{_esc(row.title.en)}</span>
            <span data-lang="zh">{_esc(row.title.zh)}</span>
          </h4>
          <p>{_esc(row.source_name)}</p>
          <a class="saved-article-organization-coverage-link" href="{_esc(href)}">
            <span data-lang="en">Open organized section</span>
            <span data-lang="zh">打开整理栏目</span>
          </a>
        </div>
        <div class="saved-article-organization-coverage-title">
          <div class="saved-article-organization-coverage-meta">
            <span data-lang="en">{_esc(section_label)}</span>
            <span data-lang="zh">{_esc(f"{row.section_count} 个整理栏目")}</span>
            <span data-lang="en">{_esc(evidence_label)}</span>
            <span data-lang="zh">{_esc(f"{row.evidence_count} 个证据段落")}</span>
          </div>
          <div class="saved-article-organization-coverage-chips">{group_chips}</div>
          <div class="saved-article-organization-coverage-refs">{ref_chips}</div>
        </div>
      </article>"""


def _render_saved_article_content_organization_group(
    group: RowOneSavedArticleContentOrganizationGroup,
    *,
    href_prefix: str = "",
) -> str:
    summary = _render_saved_article_content_organization_group_summary(group)
    cards = [
        _render_saved_article_content_organization_card(card, href_prefix=href_prefix)
        for card in group.cards
    ]
    cards = [card for card in cards if card]
    if not cards:
        return ""
    group_anchor_id = _saved_article_content_organization_group_anchor_id(group.key)
    group_id_attr = f' id="{_esc(group_anchor_id)}"' if group_anchor_id else ""
    return f"""    <article class="saved-article-content-organization-group"{group_id_attr}>
      <div class="saved-article-content-organization-group-header">
        <h3>
          <span data-lang="en">{_esc(group.title.en)}</span>
          <span data-lang="zh">{_esc(group.title.zh)}</span>
        </h3>
        <p>
          <span data-lang="en">{_esc(group.dek.en)}</span>
          <span data-lang="zh">{_esc(group.dek.zh)}</span>
        </p>
      </div>
{summary}
      <div class="saved-article-content-organization-grid">{"".join(cards)}</div>
    </article>"""


def _saved_article_content_organization_group_anchor_id(group_key: str) -> str | None:
    if not isinstance(group_key, str):
        return None
    if _SAVED_ARTICLE_ORGANIZATION_GROUP_KEY_RE.fullmatch(group_key) is None:
        return None
    return f"{_SAVED_ARTICLE_ORGANIZATION_GROUP_PREFIX}{group_key}"


def _render_saved_article_content_organization_group_summary(
    group: RowOneSavedArticleContentOrganizationGroup,
) -> str:
    safe_cards: list[tuple[RowOneSavedArticleContentOrganizationCard, str]] = []
    for card in group.cards:
        href = _safe_saved_article_content_organization_href(card.detail_path)
        if href is None:
            continue
        safe_cards.append((card, href))
    if not safe_cards:
        return ""

    source_names = {
        normalized_source.casefold()
        for card, _href in safe_cards
        if (normalized_source := normalize_row_one_paragraph(card.source_name))
    }
    detail_paths = {
        detail_path
        for _card, href in safe_cards
        if (detail_path := _saved_article_content_organization_detail_path_key(href))
    }
    evidence_keys: set[tuple[str, int]] = set()
    for card, href in safe_cards:
        detail_key = _saved_article_content_organization_detail_path_key(href)
        if not detail_key:
            continue
        for paragraph_index in card.paragraph_indices:
            if not isinstance(paragraph_index, int) or isinstance(paragraph_index, bool):
                continue
            if paragraph_index < 0:
                continue
            evidence_keys.add((detail_key, paragraph_index))

    metrics = "".join(
        (
            _render_saved_article_content_organization_summary_metric(
                _count_label(len(safe_cards), "saved card", "saved cards"),
                f"{len(safe_cards)} 张卡片",
            ),
            _render_saved_article_content_organization_summary_metric(
                _count_label(len(detail_paths), "saved article", "saved articles"),
                f"{len(detail_paths)} 篇文章",
            ),
            _render_saved_article_content_organization_summary_metric(
                _count_label(len(source_names), "source", "sources"),
                f"{len(source_names)} 个来源",
            ),
            _render_saved_article_content_organization_summary_metric(
                _count_label(
                    len(evidence_keys),
                    "evidence paragraph",
                    "evidence paragraphs",
                ),
                f"{len(evidence_keys)} 个证据段落",
            ),
        )
    )
    ref_block = _render_saved_article_content_organization_summary_refs(
        _saved_article_content_organization_summary_refs(safe_cards)
    )
    return f"""      <div class="saved-article-content-organization-summary">
        <div class="saved-article-content-organization-summary-metrics">{metrics}</div>
{ref_block}
      </div>"""


def _saved_article_content_organization_detail_path_key(href: str) -> str:
    path, _separator, _fragment = href.partition("#")
    safe_path = validated_row_one_detail_relative_path(path)
    return str(safe_path) if safe_path is not None else ""


def _render_saved_article_content_organization_summary_metric(
    value_en: str,
    value_zh: str,
) -> str:
    return (
        '<span class="saved-article-content-organization-summary-metric">'
        f'<span data-lang="en">{_esc(value_en)}</span>'
        f'<span data-lang="zh">{_esc(value_zh)}</span>'
        "</span>"
    )


def _saved_article_content_organization_summary_refs(
    safe_cards: Sequence[tuple[RowOneSavedArticleContentOrganizationCard, str]],
) -> list[RowOneReference]:
    refs: list[RowOneReference] = []
    seen: set[tuple[str, str, str]] = set()
    for card, _href in safe_cards:
        for ref in card.references:
            name = normalize_row_one_paragraph(ref.name)
            ref_type = normalize_row_one_paragraph(ref.type)
            label = normalize_row_one_paragraph(ref.label)
            if not name:
                continue
            key = (name.casefold(), ref_type.casefold(), label.casefold())
            if key in seen:
                continue
            seen.add(key)
            refs.append(RowOneReference(name=name, type=ref_type, label=label))
            if len(refs) >= SAVED_ARTICLE_CONTENT_ORGANIZATION_SUMMARY_MAX_REFS:
                return refs
    return refs


def _render_saved_article_content_organization_summary_refs(
    refs: Sequence[RowOneReference],
) -> str:
    if not refs:
        return ""
    chips = "".join(
        '<span class="saved-article-content-organization-summary-ref">'
        f"<span>{_esc(ref.name)}</span>"
        f"<span>{_esc(ref.label.strip() or ref.type.strip())}</span>"
        "</span>"
        for ref in refs
    )
    return f"""        <div class="saved-article-content-organization-summary-refs"
          aria-label="Saved article content organization group references">
{chips}
        </div>"""


def _render_saved_article_content_organization_card(
    card: RowOneSavedArticleContentOrganizationCard,
    *,
    href_prefix: str = "",
) -> str:
    href = _safe_saved_article_content_organization_href(card.detail_path)
    if href is None:
        return ""
    href = _prefixed_saved_article_content_organization_href(href, href_prefix)
    chips = _render_saved_article_content_organization_chips(card, href_prefix=href_prefix)
    chip_block = (
        f'\n      <div class="saved-article-content-organization-chips">{chips}</div>'
        if chips
        else ""
    )
    return f"""        <article class="saved-article-content-organization-card">
      <div class="saved-article-content-organization-meta">
        <span>{_esc(card.source_name)}</span>
        <span>
          <span data-lang="en">{_esc(card.section_title.en)}</span>
          <span data-lang="zh">{_esc(card.section_title.zh)}</span>
        </span>
        <span>
          <span data-lang="en">{_esc(card.section_label.en)}</span>
          <span data-lang="zh">{_esc(card.section_label.zh)}</span>
        </span>
      </div>
      <h4>
        <span data-lang="en">{_esc(card.title.en)}</span>
        <span data-lang="zh">{_esc(card.title.zh)}</span>
      </h4>
      <p class="saved-article-content-organization-lead">
        <span data-lang="en">{_esc(_local_article_digest_excerpt(card.lead.en))}</span>
        <span data-lang="zh">{_esc(_local_article_digest_excerpt(card.lead.zh))}</span>
      </p>{chip_block}
      <a class="saved-article-content-organization-card-link" href="{_esc(href)}">
        <span data-lang="en">Open organized section</span>
        <span data-lang="zh">打开整理栏目</span>
      </a>
    </article>"""


def _render_saved_article_content_organization_chips(
    card: RowOneSavedArticleContentOrganizationCard,
    *,
    href_prefix: str = "",
) -> str:
    chips = [_render_saved_article_content_organization_ref_chip(ref) for ref in card.references]
    if card.paragraph_indices:
        paragraph_count = len(card.paragraph_indices)
        paragraph_count_en = _count_label(paragraph_count, "paragraph", "paragraphs")
        chips.append(
            '<span class="saved-article-content-organization-chip">'
            f'<span data-lang="en">{_esc(paragraph_count_en)}</span>'
            f'<span data-lang="zh">{_esc(f"{paragraph_count} 个段落")}</span>'
            "</span>"
        )
    evidence = _render_saved_article_content_organization_evidence(
        card,
        href_prefix=href_prefix,
    )
    return "".join(chips) + evidence


def _render_saved_article_content_organization_evidence(
    card: RowOneSavedArticleContentOrganizationCard,
    *,
    href_prefix: str = "",
) -> str:
    links: list[str] = []
    seen: set[int] = set()
    for paragraph_index in card.paragraph_indices:
        if paragraph_index in seen:
            continue
        href = _safe_saved_article_content_organization_evidence_href(
            card.detail_path,
            paragraph_index,
        )
        if href is None:
            continue
        href = _prefixed_saved_article_content_organization_href(href, href_prefix)
        seen.add(paragraph_index)
        label_number = str(paragraph_index + 1)
        links.append(
            '<a class="saved-article-content-organization-evidence-link" '
            f'href="{_esc(href)}">'
            f'<span data-lang="en">Evidence paragraph {_esc(label_number)}</span>'
            f'<span data-lang="zh">证据段落 {_esc(label_number)}</span>'
            "</a>"
        )
        if len(links) >= SAVED_ARTICLE_CONTENT_ORGANIZATION_EVIDENCE_LINK_LIMIT:
            break
    if not links:
        return ""
    return '<span class="saved-article-content-organization-evidence">' + "".join(links) + "</span>"


def _render_saved_article_content_organization_ref_chip(ref: RowOneReference) -> str:
    label = ref.label.strip() or ref.type.strip()
    return (
        '<span class="saved-article-content-organization-chip">'
        f"<span>{_esc(ref.name)}</span>"
        f"<span>{_esc(label)}</span>"
        "</span>"
    )


def _safe_saved_article_content_organization_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    if "#" not in href:
        return None
    path, fragment = href.split("#", 1)
    if not _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment):
        return None
    safe_path = validated_row_one_detail_relative_path(path)
    if safe_path is None:
        return None
    return f"{safe_path}#{fragment}"


def _prefixed_saved_article_content_organization_href(href: str, href_prefix: str) -> str:
    if not href_prefix:
        return href
    return f"{href_prefix}{href}"


def _safe_saved_article_content_organization_evidence_href(
    detail_path: object,
    paragraph_index: object,
) -> str | None:
    safe_section_href = _safe_saved_article_content_organization_href(detail_path)
    if safe_section_href is None:
        return None
    safe_paragraph_index = _safe_saved_article_content_organization_paragraph_index(paragraph_index)
    if safe_paragraph_index is None:
        return None
    path, _, _fragment = safe_section_href.partition("#")
    safe_path = validated_row_one_detail_relative_path(path)
    if safe_path is None:
        return None
    paragraph_fragment = f"local-article-paragraph-{safe_paragraph_index + 1}"
    if not _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(paragraph_fragment):
        return None
    return f"{safe_path}#{paragraph_fragment}"


def _safe_saved_article_content_organization_paragraph_index(
    paragraph_index: object,
) -> int | None:
    if not isinstance(paragraph_index, int) or isinstance(paragraph_index, bool):
        return None
    if paragraph_index < 0:
        return None
    if paragraph_index > SAVED_ARTICLE_CONTENT_ORGANIZATION_MAX_PARAGRAPH_INDEX:
        return None
    return paragraph_index


def _render_editorial_brief(editorial_brief: _EditorialBrief | None) -> str:
    if editorial_brief is None:
        return ""
    cards: list[str] = []
    for item in editorial_brief.items:
        has_body = normalize_row_one_paragraph(item.body.en) or normalize_row_one_paragraph(
            item.body.zh
        )
        if not has_body:
            continue
        rendered = _render_editorial_brief_card(item)
        if rendered:
            cards.append(rendered)
        if len(cards) >= EDITORIAL_BRIEF_MAX_ITEMS:
            break
    if not cards:
        return ""
    return f"""<section class="editorial-brief" aria-label="Editorial brief">
  <div class="editorial-brief-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Editorial Brief</span>
        <span data-lang="zh">编辑正文</span>
      </p>
      <h2>
        <span data-lang="en">Today, in context</span>
        <span data-lang="zh">今天的语境整理</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">Short editorial reads assembled from local saved article text.</span>
      <span data-lang="zh">基于本地保存正文整理的短篇编辑解读。</span>
    </p>
  </div>
  <div class="editorial-brief-grid">
{"".join(cards)}
  </div>
</section>"""


def _render_editorial_brief_trail_item(label: LocalizedText, href: str | None) -> str:
    body = (
        f'<span data-lang="en">{_esc(label.en)}</span><span data-lang="zh">{_esc(label.zh)}</span>'
    )
    if href is None:
        return f'        <span class="editorial-brief-trail-item">{body}</span>'
    return f'        <a class="editorial-brief-trail-item" href="{_esc(href)}">{body}</a>'


def _render_editorial_brief_trail(
    items: Sequence[_EditorialBriefTrailItem],
) -> str:
    rendered_items: list[str] = []
    seen: set[tuple[str, str, str | None]] = set()
    for item in items:
        label = LocalizedText(
            en=_editorial_brief_display_text(item.label.en),
            zh=_editorial_brief_display_text(item.label.zh),
        )
        if not (label.en or label.zh):
            continue
        href = _safe_editorial_brief_href(item.href)
        key = (label.en.casefold(), label.zh.casefold(), href)
        if key in seen:
            continue
        seen.add(key)
        rendered_items.append(_render_editorial_brief_trail_item(label, href))
        if len(rendered_items) >= EDITORIAL_BRIEF_MAX_TRAIL_ITEMS:
            break
    if not rendered_items:
        return ""
    items_html = "\n".join(rendered_items)
    return f"""
      <div class="editorial-brief-trail" aria-label="Editorial source trail / 编辑来源线索">
{items_html}
      </div>"""


def _render_editorial_brief_card(item: _EditorialBriefItem) -> str:
    title = LocalizedText(
        en=_editorial_brief_display_text(item.title.en),
        zh=_editorial_brief_display_text(item.title.zh),
    )
    body = LocalizedText(
        en=_editorial_brief_body_excerpt(item.body.en),
        zh=_editorial_brief_body_excerpt(item.body.zh),
    )
    if not (body.en or body.zh):
        return ""
    meta = item.meta
    meta_block = ""
    if meta is not None:
        meta_text = LocalizedText(
            en=_editorial_brief_display_text(meta.en),
            zh=_editorial_brief_display_text(meta.zh),
        )
        if meta_text.en or meta_text.zh:
            meta_block = f"""
      <p class="editorial-brief-meta">
        <span data-lang="en">{_esc(meta_text.en)}</span>
        <span data-lang="zh">{_esc(meta_text.zh)}</span>
      </p>"""
    trail_block = _render_editorial_brief_trail(item.trail)
    action_block = ""
    href = _safe_editorial_brief_href(item.href)
    if href is not None:
        action_block = f"""
      <a class="editorial-brief-link" href="{_esc(href)}">
        <span data-lang="en">Read locally</span>
        <span data-lang="zh">本地阅读</span>
      </a>"""
    body_html = f"""      <h3>
        <span data-lang="en">{_esc(title.en)}</span>
        <span data-lang="zh">{_esc(title.zh)}</span>
      </h3>
      <p>
        <span data-lang="en">{_esc(body.en)}</span>
        <span data-lang="zh">{_esc(body.zh)}</span>
      </p>{meta_block}{trail_block}{action_block}"""
    return f"""    <article class="editorial-brief-card">
{body_html}
    </article>"""


def _editorial_brief_body_excerpt(value: str) -> str:
    text = _editorial_brief_display_text(value)
    if len(text) <= EDITORIAL_BRIEF_BODY_EXCERPT_CHARS:
        return text
    return text[:EDITORIAL_BRIEF_BODY_EXCERPT_CHARS].rstrip() + "…"


def _editorial_brief_display_text(value: str) -> str:
    return normalize_row_one_paragraph(value)


def _safe_editorial_brief_href(href: object) -> str | None:
    text = str(href or "").strip()
    if not text:
        return None
    path, separator, fragment = text.partition("#")
    safe_path = validated_row_one_detail_relative_path(path)
    if safe_path is None:
        return None
    if not separator:
        return str(safe_path)
    if _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(
        fragment
    ) or _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment):
        return f"{safe_path}#{fragment}"
    return None


def _count_label(count: int, singular: str, plural: str) -> str:
    return f"{count} {singular if count == 1 else plural}"


def _render_daily_local_intelligence_section(
    section: RowOneDailyLocalIntelligenceSection,
) -> str:
    cards = [_render_daily_local_intelligence_item(item) for item in section.items]
    cards = [card for card in cards if card]
    if not cards:
        return ""
    return f"""<article class="daily-local-intelligence-group">
  <p class="daily-local-intelligence-group-title">
    <span data-lang="en">{_esc(section.title.en)}</span>
    <span data-lang="zh">{_esc(section.title.zh)}</span>
  </p>
  <p>
    <span data-lang="en">{_esc(section.dek.en)}</span>
    <span data-lang="zh">{_esc(section.dek.zh)}</span>
  </p>
  {"".join(cards)}
</article>"""


def _render_daily_local_intelligence_item(item: RowOneDailyLocalIntelligenceItem) -> str:
    href = _safe_daily_local_intelligence_href(item.detail_path)
    meta = _daily_local_intelligence_meta(item)
    segments = _render_daily_local_intelligence_segments(item, detail_href=href)
    actions = _render_daily_local_intelligence_actions(item, detail_href=href)
    body = f"""<h3>
    <span data-lang="en">{_esc(item.title.en)}</span>
    <span data-lang="zh">{_esc(item.title.zh)}</span>
  </h3>
  <p>
    <span data-lang="en">{_esc(item.body.en)}</span>
    <span data-lang="zh">{_esc(item.body.zh)}</span>
  </p>
  {segments}
  <div class="daily-local-intelligence-meta">{meta}</div>
  {actions}"""
    return f'<div class="daily-local-intelligence-card">{body}</div>'


def _render_daily_local_intelligence_actions(
    item: RowOneDailyLocalIntelligenceItem,
    *,
    detail_href: str | None,
) -> str:
    if detail_href is None:
        return ""
    links = [(detail_href, "Open saved text", "打开本地正文")]
    for index in _daily_local_intelligence_paragraph_indices(item)[:3]:
        href = _daily_local_intelligence_paragraph_href(detail_href, index)
        if href is None:
            continue
        label = index + 1
        links.append((href, f"Evidence paragraph {label}", f"证据段落 {label}"))
    rendered = "".join(
        f'<a class="daily-local-intelligence-action" href="{_esc(href)}">'
        f'<span data-lang="en">{_esc(en)}</span>'
        f'<span data-lang="zh">{_esc(zh)}</span>'
        "</a>"
        for href, en, zh in links
    )
    if not rendered:
        return ""
    return f'<div class="daily-local-intelligence-actions">{rendered}</div>'


def _daily_local_intelligence_paragraph_indices(
    item: RowOneDailyLocalIntelligenceItem,
) -> list[int]:
    indices: list[int] = []
    seen: set[int] = set()
    for index in item.paragraph_indices:
        if index >= 0 and index not in seen:
            seen.add(index)
            indices.append(index)
    for segment in item.segments:
        for segment_item in segment.items:
            for index in segment_item.paragraph_indices:
                if index >= 0 and index not in seen:
                    seen.add(index)
                    indices.append(index)
    return indices


def _daily_local_intelligence_paragraph_href(
    detail_href: str,
    index: int,
) -> str | None:
    if index < 0:
        return None
    path = detail_href.split("#", 1)[0]
    return f"{path}#local-article-paragraph-{index + 1}"


def _render_daily_local_intelligence_segments(
    item: RowOneDailyLocalIntelligenceItem,
    *,
    detail_href: str | None,
) -> str:
    segments = [
        _render_daily_local_intelligence_segment(segment, detail_href=detail_href)
        for segment in item.segments
    ]
    rendered = [segment for segment in segments if segment]
    if not rendered:
        return ""
    return f'<div class="daily-local-intelligence-segments">{"".join(rendered)}</div>'


def _render_daily_local_intelligence_segment(
    segment: RowOneDailyLocalIntelligenceSegment,
    *,
    detail_href: str | None,
) -> str:
    items = [
        _render_daily_local_intelligence_segment_item(
            segment_item,
            detail_href=detail_href,
        )
        for segment_item in segment.items
    ]
    rendered_items = [item for item in items if item]
    if not rendered_items:
        return ""
    body = ""
    if segment.body is not None and (segment.body.en.strip() or segment.body.zh.strip()):
        body = f"""<p class="daily-local-intelligence-segment-body">
      <span data-lang="en">{_esc(segment.body.en)}</span>
      <span data-lang="zh">{_esc(segment.body.zh)}</span>
    </p>"""
    return f"""<div class="daily-local-intelligence-segment">
    <p class="daily-local-intelligence-segment-title">
      <span data-lang="en">{_esc(segment.title.en)}</span>
      <span data-lang="zh">{_esc(segment.title.zh)}</span>
    </p>
    {body}
    <div class="daily-local-intelligence-segment-items">{"".join(rendered_items)}</div>
  </div>"""


def _render_daily_local_intelligence_segment_item(
    segment_item: RowOneDailyLocalIntelligenceSegmentItem,
    *,
    detail_href: str | None,
) -> str:
    body = ""
    if segment_item.body is not None and (
        segment_item.body.en.strip() or segment_item.body.zh.strip()
    ):
        body = f"""<p class="daily-local-intelligence-segment-item-body">
      <span data-lang="en">{_esc(segment_item.body.en)}</span>
      <span data-lang="zh">{_esc(segment_item.body.zh)}</span>
    </p>"""
    meta = _render_daily_local_intelligence_segment_meta(
        segment_item,
        detail_href=detail_href,
    )
    if not body and not meta:
        return ""
    return f"""<div class="daily-local-intelligence-segment-item">
    <p class="daily-local-intelligence-segment-item-label">
      <span data-lang="en">{_esc(segment_item.label.en)}</span>
      <span data-lang="zh">{_esc(segment_item.label.zh)}</span>
    </p>
    {body}
    {meta}
  </div>"""


def _render_daily_local_intelligence_segment_meta(
    segment_item: RowOneDailyLocalIntelligenceSegmentItem,
    *,
    detail_href: str | None,
) -> str:
    parts: list[str] = []
    for ref in segment_item.references:
        ref_text = " / ".join(value for value in (ref.name, ref.type, ref.label) if value)
        parts.append(
            f"<span>"
            f'<span data-lang="en">{_esc(ref_text)}</span>'
            f'<span data-lang="zh">{_esc(ref_text)}</span>'
            f"</span>"
        )
    for index in _valid_daily_local_intelligence_paragraph_indices(segment_item.paragraph_indices):
        paragraph_label = index + 1
        href = (
            _daily_local_intelligence_paragraph_href(detail_href, index)
            if detail_href is not None
            else None
        )
        label = (
            f'<span data-lang="en">Paragraph {paragraph_label}</span>'
            f'<span data-lang="zh">段落 {paragraph_label}</span>'
        )
        if href is None:
            parts.append(f"<span>{label}</span>")
        else:
            parts.append(
                f'<a class="daily-local-intelligence-paragraph-link" href="{_esc(href)}">'
                f"{label}</a>"
            )
    if not parts:
        return ""
    rendered = "".join(parts)
    return f'<div class="daily-local-intelligence-segment-meta">{rendered}</div>'


def _valid_daily_local_intelligence_paragraph_indices(indices: Sequence[int]) -> list[int]:
    valid: list[int] = []
    seen: set[int] = set()
    for index in indices:
        if index < 0 or index in seen:
            continue
        seen.add(index)
        valid.append(index)
    return valid


def _daily_local_intelligence_meta(item: RowOneDailyLocalIntelligenceItem) -> str:
    parts: list[tuple[str, str]] = []
    if item.source_names:
        sources = ", ".join(item.source_names)
        parts.append((sources, sources))
    if item.article_count:
        parts.append(
            (
                "1 article" if item.article_count == 1 else f"{item.article_count} articles",
                f"{item.article_count} 篇本地正文",
            )
        )
    if item.story_count:
        parts.append(
            (
                "1 story" if item.story_count == 1 else f"{item.story_count} stories",
                f"{item.story_count} 条故事",
            )
        )
    if item.evidence_count:
        parts.append(
            (
                "1 evidence link"
                if item.evidence_count == 1
                else f"{item.evidence_count} evidence links",
                f"{item.evidence_count} 条证据链接",
            )
        )
    if isinstance(item.heat_delta, int) and item.heat_delta > 0:
        parts.append((f"+{item.heat_delta} local delta", f"+{item.heat_delta} 本地增量"))
    return "".join(
        f'<span data-lang="en">{_esc(en)}</span><span data-lang="zh">{_esc(zh)}</span>'
        for en, zh in parts
    )


def _signal_synthesis_meta_label(
    *,
    label: str,
    story_count: int,
    evidence_count: int,
    heat_delta: int,
) -> str:
    story_label_en = "1 story" if story_count == 1 else f"{story_count} stories"
    story_label_zh = f"{story_count} 条故事"
    evidence_label_en = (
        "1 evidence link" if evidence_count == 1 else f"{evidence_count} evidence links"
    )
    evidence_label_zh = f"{evidence_count} 条证据链接"
    heat_label_en = f"+{heat_delta} local delta"
    heat_label_zh = f"+{heat_delta} 本地增量"
    return (
        f'<span data-lang="en">{_esc(label)}</span>'
        f'<span data-lang="zh">{_esc(label)}</span>'
        f'<span data-lang="en">{_esc(story_label_en)}</span>'
        f'<span data-lang="zh">{_esc(story_label_zh)}</span>'
        f'<span data-lang="en">{_esc(evidence_label_en)}</span>'
        f'<span data-lang="zh">{_esc(evidence_label_zh)}</span>'
        f'<span data-lang="en">{_esc(heat_label_en)}</span>'
        f'<span data-lang="zh">{_esc(heat_label_zh)}</span>'
    )


def _safe_signal_detail_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    return href if _validated_detail_relative_path(href) is not None else None


def _safe_daily_local_intelligence_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    if "#" not in href:
        return href if _validated_detail_relative_path(href) is not None else None
    path, fragment = href.split("#", 1)
    if fragment != "local-article" and not _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment):
        return None
    return href if _validated_detail_relative_path(path) is not None else None


def _render_briefing_topics(app_payload: dict[str, object] | None) -> str:
    topics = _app_payload_briefing_topics(app_payload)[:4]
    if not topics:
        return ""
    topic_cards = "\n".join(_render_briefing_topic_card(topic) for topic in topics)
    return f"""<section id="briefing-topics" class="briefing-topics" aria-label="Briefing topics">
  <div class="briefing-topics-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Briefing Topics</span>
        <span data-lang="zh">今日主题</span>
      </p>
      <h2>
        <span data-lang="en">Organized Signals</span>
        <span data-lang="zh">整理后的时尚信号</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">Organized from explicit ROW ONE story references.</span>
      <span data-lang="zh">根据 ROW ONE 故事中的明确引用，整理品牌、单品、设计师与人物线索。</span>
    </p>
  </div>
  <div class="briefing-topic-grid">{topic_cards}</div>
</section>"""


def _render_briefing_topic_card(topic: dict[str, object]) -> str:
    title = _localized_topic_field(topic, "title")
    label = _localized_topic_field(topic, "label")
    topic_type = _esc(str(topic["topic_type"]))
    story_count = int(topic["story_count"])
    evidence_count = int(topic["evidence_count"])
    heat_delta = int(topic["positive_heat_delta_sum"])
    lead_story = _topic_lead_story(topic)
    href = (
        _safe_digest_detail_href(lead_story.get("detail_href")) if lead_story is not None else None
    )
    if href is None:
        href = "#main-content"
    headline = _topic_localized_card_text(lead_story, "headline") if lead_story else title
    summary = _topic_localized_card_text(lead_story, "editorial_takeaway") if lead_story else title
    story_label_en = "1 story" if story_count == 1 else f"{story_count} stories"
    story_label_zh = f"{story_count} 条故事"
    evidence_label_en = (
        "1 evidence link" if evidence_count == 1 else f"{evidence_count} evidence links"
    )
    evidence_label_zh = f"{evidence_count} 条证据链接"
    heat_label_en = f"+{heat_delta} heat" if heat_delta > 0 else "steady heat"
    heat_label_zh = f"+{heat_delta} 热度" if heat_delta > 0 else "热度平稳"
    return f"""<a class="briefing-topic-card briefing-topic-card--{topic_type}" href="{_esc(href)}">
  <span class="briefing-topic-label">
    <span data-lang="en">{_esc(label.en)}</span>
    <span data-lang="zh">{_esc(label.zh)}</span>
  </span>
  <h3>
    <span data-lang="en">{_esc(title.en)}</span>
    <span data-lang="zh">{_esc(title.zh)}</span>
  </h3>
  <p>
    <span data-lang="en">{_esc(headline.en)}</span>
    <span data-lang="zh">{_esc(headline.zh)}</span>
  </p>
  <p>
    <span data-lang="en">{_esc(summary.en)}</span>
    <span data-lang="zh">{_esc(summary.zh)}</span>
  </p>
  <span class="briefing-topic-meta">
    <span class="briefing-topic-count">
      <span data-lang="en">{_esc(story_label_en)}</span>
      <span data-lang="zh">{_esc(story_label_zh)}</span>
    </span>
    <span class="briefing-topic-count">
      <span data-lang="en">{_esc(evidence_label_en)}</span>
      <span data-lang="zh">{_esc(evidence_label_zh)}</span>
    </span>
    <span class="briefing-topic-count">
      <span data-lang="en">{_esc(heat_label_en)}</span>
      <span data-lang="zh">{_esc(heat_label_zh)}</span>
    </span>
  </span>
</a>"""


def _render_briefing_path(app_payload: dict[str, object] | None) -> str:
    blocks = _app_payload_digest_blocks(app_payload)
    excluded_story_ids = _read_first_story_ids(blocks)
    path_blocks = [
        block
        for block in blocks
        if block.get("key") in {"key_takeaways", "signals_to_watch"}
        and _block_cards(block, excluded_story_ids)
    ]
    if not path_blocks:
        return ""
    rendered_blocks = "\n".join(
        _render_briefing_path_block(block, excluded_story_ids) for block in path_blocks
    )
    return f"""<section id="briefing-path" class="briefing-path" aria-label="Briefing path">
  <div class="briefing-path-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Briefing Path</span>
        <span data-lang="zh">今日阅读路径</span>
      </p>
      <h2>
        <span data-lang="en">What to read next</span>
        <span data-lang="zh">接下来读什么</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">A compact reading path from existing daily digest blocks.</span>
      <span data-lang="zh">复用现有每日简报区块，整理后续阅读顺序。</span>
    </p>
  </div>
  <div class="briefing-path-grid">{rendered_blocks}</div>
</section>"""


def _render_briefing_path_block(
    block: dict[str, object],
    excluded_story_ids: set[str],
) -> str:
    title = _localized_topic_field(block, "title")
    dek = _localized_topic_field(block, "dek")
    cards = _block_cards(block, excluded_story_ids)[:5]
    rendered_cards = "\n".join(_render_briefing_path_card(card) for card in cards)
    return f"""<div class="briefing-path-block">
  <h3>
    <span data-lang="en">{_esc(title.en)}</span>
    <span data-lang="zh">{_esc(title.zh)}</span>
  </h3>
  <p>
    <span data-lang="en">{_esc(dek.en)}</span>
    <span data-lang="zh">{_esc(dek.zh)}</span>
  </p>
  {rendered_cards}
</div>"""


def _render_briefing_path_card(card: dict[str, object]) -> str:
    href = _safe_digest_detail_href(card.get("detail_href")) or "#main-content"
    headline = _topic_localized_card_text(card, "headline")
    takeaway = _topic_localized_card_text(card, "editorial_takeaway")
    source_name = _esc(str(card.get("source_name") or "ROW ONE"))
    published_date = _esc(str(card.get("published_date") or "Undated"))
    evidence_count = _int_or_zero(card.get("evidence_count"))
    heat_delta = _int_or_zero(card.get("heat_delta"))
    evidence_label_en = (
        "1 evidence link" if evidence_count == 1 else f"{evidence_count} evidence links"
    )
    evidence_label_zh = f"{evidence_count} 条证据链接"
    heat_label_en = f"{heat_delta} heat" if heat_delta > 0 else "steady heat"
    heat_label_zh = f"{heat_delta} 热度" if heat_delta > 0 else "热度平稳"
    return f"""<a class="briefing-path-card" href="{_esc(href)}">
    <span class="briefing-path-meta">
      <span>{source_name}</span>
      <span>{published_date}</span>
      <span data-lang="en">{_esc(evidence_label_en)}</span>
      <span data-lang="zh">{_esc(evidence_label_zh)}</span>
      <span data-lang="en">{_esc(heat_label_en)}</span>
      <span data-lang="zh">{_esc(heat_label_zh)}</span>
    </span>
    <h4>
      <span data-lang="en">{_esc(headline.en)}</span>
      <span data-lang="zh">{_esc(headline.zh)}</span>
    </h4>
    <p>
      <span data-lang="en">{_esc(takeaway.en)}</span>
      <span data-lang="zh">{_esc(takeaway.zh)}</span>
    </p>
  </a>"""


def _int_or_zero(value: object) -> int:
    if value is None:
        return 0
    return int(value)


def _safe_digest_detail_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    return href if _validated_detail_relative_path(href) is not None else None


def _app_payload_digest_blocks(
    app_payload: dict[str, object] | None,
) -> list[dict[str, object]]:
    if app_payload is None:
        return []
    daily_digest = app_payload.get("daily_digest")
    if not isinstance(daily_digest, dict):
        return []
    blocks = daily_digest.get("blocks")
    if not isinstance(blocks, list):
        return []
    return [block for block in blocks if isinstance(block, dict)]


def _read_first_story_ids(blocks: list[dict[str, object]]) -> set[str]:
    read_first_block = next((block for block in blocks if block.get("key") == "read_first"), None)
    if read_first_block is None:
        return set()
    story_ids = read_first_block.get("story_ids")
    if not isinstance(story_ids, list):
        return set()
    return {str(story_id) for story_id in story_ids}


def _block_cards(
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


def _app_payload_briefing_topics(
    app_payload: dict[str, object] | None,
) -> list[dict[str, object]]:
    if app_payload is None:
        return []
    daily_digest = app_payload.get("daily_digest")
    if not isinstance(daily_digest, dict):
        return []
    topics = daily_digest.get("briefing_topics")
    if not isinstance(topics, list):
        return []
    return [topic for topic in topics if isinstance(topic, dict)]


def _localized_topic_field(topic: dict[str, object], field: str) -> LocalizedText:
    value = topic.get(field)
    if value is None:
        return LocalizedText(zh="", en="")
    if isinstance(value, dict):
        zh = value.get("zh")
        en = value.get("en")
        return LocalizedText(
            zh=str(zh) if zh is not None else "",
            en=str(en) if en is not None else "",
        )
    text = str(value)
    return LocalizedText(zh=text, en=text)


def _topic_lead_story(topic: dict[str, object]) -> dict[str, object] | None:
    cards = topic.get("cards")
    if not isinstance(cards, list) or not cards:
        return None
    first = cards[0]
    return first if isinstance(first, dict) else None


def _topic_localized_card_text(
    card: dict[str, object] | None,
    field: str,
) -> LocalizedText:
    if card is None:
        return LocalizedText(zh="", en="")
    value = card.get(field)
    if isinstance(value, dict):
        return LocalizedText(zh=str(value["zh"]), en=str(value["en"]))
    text = str(value) if value is not None else ""
    return LocalizedText(zh=text, en=text)


def _render_edition_nav_item(
    edition: RowOneEdition,
    section: RowOneSection,
) -> str:
    story_count = len(edition.section_stories(section.key))
    count_en = "1 story" if story_count == 1 else f"{story_count} stories"
    count_zh = f"{story_count} 条"
    index = next(
        (
            position
            for position, candidate in enumerate(edition.sections, start=1)
            if candidate.key == section.key
        ),
        1,
    )
    return f"""<a class="edition-nav-item edition-rail-item" href="#{_esc(section.key)}">
  <span class="rail-item-index">{index:02d}</span>
  <span class="rail-item-copy">
    <span class="edition-nav-title rail-item-title">
      <span data-lang="en">{_esc(section.title.en)}</span>
      <span data-lang="zh">{_esc(section.title.zh)}</span>
    </span>
    <span class="edition-nav-count rail-item-count">
      <span data-lang="en">{_esc(count_en)}</span>
      <span data-lang="zh">{_esc(count_zh)}</span>
    </span>
    <span class="edition-nav-dek">
      <span data-lang="en">{_esc(section.dek.en)}</span>
      <span data-lang="zh">{_esc(section.dek.zh)}</span>
    </span>
  </span>
</a>"""


def _render_article_contents(*, include_local_article: bool = False) -> str:
    local_article_link = (
        """  <a href="#local-article">
    <span data-lang="en">Local Article</span>
    <span data-lang="zh">本地正文</span>
  </a>
"""
        if include_local_article
        else ""
    )
    return f"""<nav class="article-contents" aria-label="Article contents">
  <a href="#summary">
    <span data-lang="en">Summary</span>
    <span data-lang="zh">摘要</span>
  </a>
{local_article_link}  <a href="#why-it-matters">
    <span data-lang="en">Why It Matters</span>
    <span data-lang="zh">为什么重要</span>
  </a>
  <a href="#editorial-takeaway">
    <span data-lang="en">Editorial Takeaway</span>
    <span data-lang="zh">编辑判断</span>
  </a>
  <a href="#signal-context">
    <span data-lang="en">Signal Context</span>
    <span data-lang="zh">信号背景</span>
  </a>
  <a href="#reader-path">
    <span data-lang="en">Reader Path</span>
    <span data-lang="zh">阅读路径</span>
  </a>
  <a href="#evidence-trail">
    <span data-lang="en">Evidence Trail</span>
    <span data-lang="zh">证据链</span>
  </a>
</nav>"""


def _render_detail_continue_reading(edition: RowOneEdition, story: RowOneStory) -> str:
    cards = [
        _render_detail_continue_reading_card(edition, related)
        for related in _detail_continue_reading_stories(edition, story)
    ]
    cards = [card for card in cards if card]
    if not cards:
        return ""
    rendered_cards = "".join(cards)
    return f"""    <section id="continue-reading" class="continue-reading"
      aria-label="Continue reading">
      <div class="continue-reading-header">
        <p class="story-section">
          <span data-lang="en">Continue Reading</span>
          <span data-lang="zh">继续阅读</span>
        </p>
        <h2>
          <span data-lang="en">Continue Reading</span>
          <span data-lang="zh">继续阅读</span>
        </h2>
      </div>
      <div class="continue-reading-grid">{rendered_cards}</div>
    </section>"""


def _detail_continue_reading_stories(
    edition: RowOneEdition,
    story: RowOneStory,
) -> list[RowOneStory]:
    candidates = [
        candidate
        for candidate in edition.stories
        if candidate.id != story.id and candidate.section_key == story.section_key
    ]
    candidates.extend(
        candidate
        for candidate in edition.stories
        if candidate.id != story.id and candidate.section_key != story.section_key
    )
    selected: list[RowOneStory] = []
    seen_paths: set[str] = set()
    for candidate in candidates:
        href = _detail_continue_reading_href(candidate.detail_path)
        if href is None or href in seen_paths:
            continue
        seen_paths.add(href)
        selected.append(candidate)
        if len(selected) >= DETAIL_CONTINUE_READING_MAX_ITEMS:
            break
    return selected


def _render_detail_continue_reading_card(
    edition: RowOneEdition,
    story: RowOneStory,
) -> str:
    href = _detail_continue_reading_href(story.detail_path)
    if href is None:
        return ""
    section_title = _section_title(edition, story.section_key)
    excerpt_en = _detail_continue_reading_excerpt(story.summary.en or story.editorial_takeaway.en)
    excerpt_zh = _detail_continue_reading_excerpt(story.summary.zh or story.editorial_takeaway.zh)
    return f"""        <article class="continue-reading-card">
          <a href="{_esc(href)}">
            <p class="continue-reading-section">
              <span data-lang="en">{_esc(section_title.en)}</span>
              <span data-lang="zh">{_esc(section_title.zh)}</span>
            </p>
            <p class="continue-reading-source">{_esc(story.source_name)}</p>
            <h3>{_esc(story.headline)}</h3>
            <p class="continue-reading-excerpt">
              <span data-lang="en">{_esc(excerpt_en)}</span>
              <span data-lang="zh">{_esc(excerpt_zh)}</span>
            </p>
          </a>
        </article>"""


def _detail_continue_reading_href(detail_path: str) -> str | None:
    pure_path = validated_row_one_detail_relative_path(detail_path)
    if pure_path is None:
        return None
    return pure_path.name


def _detail_continue_reading_excerpt(text: str) -> str:
    return _meta_description(
        _display_summary_text(text),
        limit=DETAIL_CONTINUE_READING_EXCERPT_CHARS,
    )


def _render_local_article(
    article: RowOneLocalArticle | None,
    *,
    include_body_filing_cues: bool = False,
    body_section_markers: tuple[RowOneLocalArticleBodySectionMarker, ...] = (),
) -> str:
    if article is None:
        return ""
    paragraphs = _render_local_article_paragraphs(
        article,
        include_body_filing_cues=include_body_filing_cues,
        body_section_markers=body_section_markers,
    )
    if not paragraphs:
        return ""
    title = article.title or "Source article"
    provenance = _render_local_article_provenance(article)
    brief = _render_local_article_brief(article)
    digest = _render_local_article_digest(article)
    reader = _render_local_article_reader(article)
    rendered_indices = _local_article_rendered_paragraph_indices(article)
    paragraph_evidence = _render_local_article_paragraph_evidence(
        article,
        rendered_indices=rendered_indices,
    )
    article_map = _render_local_article_map(
        article,
        include_digest=bool(digest),
        include_reader=bool(reader),
        include_paragraph_evidence=bool(paragraph_evidence),
    )
    content_sections = _render_local_article_content_sections(
        article,
        rendered_indices=rendered_indices,
    )
    rendered_paragraphs = "\n".join(paragraphs)
    return f"""<section id="local-article" class="local-article">
      <h2>
        <span data-lang="en">Local Article</span>
        <span data-lang="zh">本地正文</span>
      </h2>
      <p class="local-article-source">
        <span data-lang="en">Saved from {_esc(article.source_name)}</span>
        <span data-lang="zh">本地保存自 {_esc(article.source_name)}</span>
      </p>
{provenance}
      <h3>{_esc(title)}</h3>
{article_map}
{paragraph_evidence}
{digest}
{reader}
{brief}
{content_sections}
      <div id="local-article-body" class="local-article-body">
{rendered_paragraphs}
      </div>
    </section>"""


def _render_local_article_provenance(article: RowOneLocalArticle) -> str:
    items = [
        _local_article_provenance_item("Source", "来源", article.source_name),
        _local_article_provenance_item(
            "Saved",
            "保存时间",
            _format_datetime(article.extracted_at),
        ),
        _local_article_provenance_item(
            "Text source",
            "正文来源",
            _local_article_body_source_label(article),
        ),
    ]
    if article.reason is not None and article.reason.strip():
        items.append(
            _local_article_provenance_item(
                "Fallback reason",
                "兜底原因",
                article.reason,
            )
        )
    if article.published_at is not None:
        items.append(
            _local_article_provenance_item(
                "Published",
                "发布时间",
                _format_datetime(article.published_at),
            )
        )
    items.extend(
        [
            _local_article_provenance_item(
                "Saved paragraphs",
                "保存段落",
                str(_local_article_saved_paragraph_count(article)),
            ),
            _local_article_provenance_item(
                "Organized sections",
                "整理栏目",
                str(len(article.content_sections)),
            ),
        ]
    )
    safe_url = _safe_external_url(article.url)
    if safe_url is not None:
        items.append(
            '<a class="local-article-provenance-item local-article-provenance-link" '
            f'href="{_esc(safe_url)}" target="_blank" rel="noopener">'
            '<span data-lang="en">Original URL</span>'
            '<span data-lang="zh">原文链接</span>'
            "</a>"
        )
    return f'      <div class="local-article-provenance">{"".join(items)}</div>'


def _local_article_body_source_label(article: RowOneLocalArticle) -> str:
    if article.body_source == "summary_fallback":
        return "ROW ONE summary fallback"
    if article.body_source == "skipped" or article.skipped:
        return "Skipped"
    return "Extracted article text"


def _local_article_provenance_item(label_en: str, label_zh: str, value: str) -> str:
    return (
        '<span class="local-article-provenance-item">'
        f'<span data-lang="en">{_esc(label_en)}</span>'
        f'<span data-lang="zh">{_esc(label_zh)}</span>'
        f'<span class="local-article-provenance-value">{_esc(value)}</span>'
        "</span>"
    )


def _local_article_saved_paragraph_count(article: RowOneLocalArticle) -> int:
    return sum(1 for paragraph in article.paragraphs if paragraph.strip())


def _render_local_article_information_panel(
    edition: RowOneEdition,
    story: RowOneStory,
    article: RowOneLocalArticle,
    section_title: LocalizedText,
) -> str:
    rendered_indices = _local_article_rendered_paragraph_indices(article)
    if not rendered_indices:
        return ""
    body_source = _local_article_body_source_label_localized(article)
    paragraph_count = len(rendered_indices)
    section_count = len(article.content_sections)
    metrics = "".join(
        (
            _render_local_article_information_metric(
                label_en="Source",
                label_zh="来源",
                value_en=article.source_name.strip() or "Unknown source",
                value_zh=article.source_name.strip() or "未知来源",
            ),
            _render_local_article_information_metric(
                label_en="Text source",
                label_zh="正文来源",
                value_en=body_source.en,
                value_zh=body_source.zh,
            ),
            _render_local_article_information_metric(
                label_en="Saved text",
                label_zh="保存正文",
                value_en=_local_article_information_count(
                    paragraph_count,
                    singular="paragraph",
                    plural="paragraphs",
                ),
                value_zh=f"{paragraph_count} 个保存段落",
            ),
            _render_local_article_information_metric(
                label_en="Article structure",
                label_zh="文章结构",
                value_en=_local_article_information_count(
                    section_count,
                    singular="organized section",
                    plural="organized sections",
                ),
                value_zh=f"{section_count} 个整理栏目",
            ),
        )
    )
    jumps = _render_local_article_information_jumps(
        article,
        rendered_indices=rendered_indices,
    )
    sections = _render_local_article_information_sections(
        article,
        rendered_indices=rendered_indices,
    )
    context_cues = _render_local_article_information_context_cues(
        article,
        rendered_indices=rendered_indices,
    )
    story_context = _meta_description(
        _display_summary_text(story.summary.en),
        limit=LOCAL_ARTICLE_INFORMATION_BODY_MAX_CHARS,
    )
    dek_en = (
        f"A scan-first organizer for the saved {edition.brand} article in "
        f"{section_title.en}: {story_context}"
    )
    dek_zh = f"面向保存正文的速览整理，来源栏目：{section_title.zh}。"
    return f"""    <section class="local-article-information"
      aria-labelledby="local-article-information-title">
      <div class="local-article-information-header">
        <h2 id="local-article-information-title">
          <span data-lang="en">Local Article Information</span>
          <span data-lang="zh">本地文章信息</span>
        </h2>
        <p>
          <span data-lang="en">{_esc(dek_en)}</span>
          <span data-lang="zh">{_esc(dek_zh)}</span>
        </p>
      </div>
      <div class="local-article-information-metrics">{metrics}</div>
{jumps}
{context_cues}
{sections}
    </section>"""


def _render_local_article_information_metric(
    *,
    label_en: str,
    label_zh: str,
    value_en: str,
    value_zh: str,
) -> str:
    return f"""        <span class="local-article-information-metric">
          <span data-lang="en">{_esc(label_en)}</span>
          <span data-lang="zh">{_esc(label_zh)}</span>
          <strong>
            <span data-lang="en">{_esc(value_en)}</span>
            <span data-lang="zh">{_esc(value_zh)}</span>
          </strong>
        </span>"""


def _local_article_information_count(count: int, *, singular: str, plural: str) -> str:
    label = singular if count == 1 else plural
    return f"{count} {label}"


def _local_article_body_source_label_localized(article: RowOneLocalArticle) -> LocalizedText:
    if article.body_source == "summary_fallback":
        return LocalizedText(en="ROW ONE summary fallback", zh="ROW ONE 摘要补全文")
    if article.body_source == "skipped" or article.skipped:
        return LocalizedText(en="Skipped", zh="已跳过")
    return LocalizedText(en="Extracted article", zh="抽取正文")


def _render_local_article_information_jumps(
    article: RowOneLocalArticle,
    *,
    rendered_indices: set[int],
) -> str:
    links: list[tuple[str, str, str]] = [
        ("#local-article", "Full local article", "完整本地正文"),
        ("#local-article-reader", "Saved text reader", "保存正文阅读"),
        ("#local-article-digest", "Saved text digest", "保存正文整理"),
    ]
    evidence_entries = _local_article_paragraph_evidence_entries(
        article,
        rendered_indices=rendered_indices,
    )
    if evidence_entries:
        links.append(("#local-article-paragraph-evidence", "Paragraph evidence", "段落证据"))
    for position, section in enumerate(
        article.content_sections[:LOCAL_ARTICLE_INFORMATION_MAX_SECTIONS],
        start=1,
    ):
        links.append(
            (
                f"#{_local_article_content_section_anchor(position)}",
                section.title.en,
                section.title.zh,
            )
        )
    for index in _local_article_information_referenced_paragraph_indices(
        article,
        rendered_indices=rendered_indices,
    )[:LOCAL_ARTICLE_INFORMATION_MAX_PARAGRAPH_LINKS]:
        links.append(
            (
                f"#{_local_article_paragraph_anchor(index)}",
                f"Paragraph {index + 1}",
                f"段落 {index + 1}",
            )
        )
    rendered = "\n".join(
        f'        <a href="{_esc(href)}"><span data-lang="en">{_esc(label_en)}</span>'
        f'<span data-lang="zh">{_esc(label_zh)}</span></a>'
        for href, label_en, label_zh in links
    )
    return f"""      <nav class="local-article-information-jumps"
        aria-label="Local article information jumps">
{rendered}
      </nav>"""


def _render_local_article_information_sections(
    article: RowOneLocalArticle,
    *,
    rendered_indices: set[int],
) -> str:
    cards: list[str] = []
    for position, section in enumerate(
        article.content_sections[:LOCAL_ARTICLE_INFORMATION_MAX_SECTIONS],
        start=1,
    ):
        cards.append(
            _render_local_article_information_section(
                section,
                position=position,
                rendered_indices=rendered_indices,
            )
        )
    if not cards:
        return ""
    return (
        '      <div class="local-article-information-grid">\n' + "\n".join(cards) + "\n      </div>"
    )


def _render_local_article_information_context_cues(
    article: RowOneLocalArticle,
    *,
    rendered_indices: set[int],
) -> str:
    contexts = _local_article_paragraph_contexts(article, rendered_indices=rendered_indices)
    rows: list[str] = []
    for paragraph_index in sorted(contexts)[:LOCAL_ARTICLE_INFORMATION_MAX_PARAGRAPH_LINKS]:
        paragraph = article.paragraphs[paragraph_index]
        excerpt_en = _local_article_information_excerpt(paragraph)
        excerpt_zh = excerpt_en
        if len(article.paragraphs_zh) == len(article.paragraphs):
            zh = article.paragraphs_zh[paragraph_index]
            if zh.strip():
                excerpt_zh = _local_article_information_excerpt(zh)
        href = f"#{_local_article_paragraph_anchor(paragraph_index)}"
        rows.append(
            f"""          <li>
            <a href="{_esc(href)}">
              <strong>
                <span data-lang="en">Paragraph {paragraph_index + 1}</span>
                <span data-lang="zh">段落 {paragraph_index + 1}</span>
              </strong>
              <span data-lang="en">{_esc(excerpt_en)}</span>
              <span data-lang="zh">{_esc(excerpt_zh)}</span>
            </a>
          </li>"""
        )
    if not rows:
        return ""
    rendered = "\n".join(rows)
    return f"""      <section class="local-article-information-context-cues"
        aria-label="Saved paragraph context cues">
        <h3>
          <span data-lang="en">Saved Paragraph Context Cues</span>
          <span data-lang="zh">保存段落上下文</span>
        </h3>
        <ul class="local-article-information-context-cue-list">
{rendered}
        </ul>
      </section>"""


def _render_local_article_information_section(
    section: RowOneLocalArticleContentSection,
    *,
    position: int,
    rendered_indices: set[int],
) -> str:
    href = f"#{_local_article_content_section_anchor(position)}"
    body = ""
    if section.body is not None and section.body.en.strip():
        body_en = _local_article_information_excerpt(section.body.en)
        body_zh = _local_article_information_excerpt(section.body.zh)
        body = (
            "          <p>"
            f'<span data-lang="en">{_esc(body_en)}</span>'
            f'<span data-lang="zh">{_esc(body_zh)}</span>'
            "</p>\n"
        )
    items = "\n".join(
        _render_local_article_information_item(
            item,
            rendered_indices=rendered_indices,
        )
        for item in section.items[:LOCAL_ARTICLE_INFORMATION_MAX_ITEMS_PER_SECTION]
    )
    item_list = (
        f'          <ul class="local-article-information-items">\n{items}\n          </ul>\n'
        if items
        else ""
    )
    references = _render_local_article_information_refs(section.items)
    paragraphs = _render_local_article_information_paragraph_links(
        _local_article_information_section_indices(section),
        rendered_indices=rendered_indices,
    )
    return f"""        <article class="local-article-information-card">
          <h3>
            <a href="{_esc(href)}">
              <span data-lang="en">{_esc(section.title.en)}</span>
              <span data-lang="zh">{_esc(section.title.zh)}</span>
            </a>
          </h3>
{body}{item_list}{references}{paragraphs}
        </article>"""


def _render_local_article_information_item(
    item: RowOneLocalArticleContentItem,
    *,
    rendered_indices: set[int],
) -> str:
    body = ""
    if item.body is not None and item.body.en.strip():
        body = (
            "              <p>"
            f'<span data-lang="en">{_esc(_local_article_information_excerpt(item.body.en))}</span>'
            f'<span data-lang="zh">{_esc(_local_article_information_excerpt(item.body.zh))}</span>'
            "</p>\n"
        )
    paragraphs = _render_local_article_information_paragraph_links(
        item.paragraph_indices,
        rendered_indices=rendered_indices,
    )
    return f"""            <li>
              <h4>
                <span data-lang="en">{_esc(item.label.en)}</span>
                <span data-lang="zh">{_esc(item.label.zh)}</span>
              </h4>
{body}{paragraphs}
            </li>"""


def _render_local_article_information_refs(
    items: Sequence[RowOneLocalArticleContentItem],
) -> str:
    refs = _local_article_information_refs(items)
    if not refs:
        return ""
    rendered = "\n".join(
        f'            <span class="local-article-information-ref">{_esc(ref.name)}'
        f" <span>{_esc(ref.type)} / {_esc(ref.label)}</span></span>"
        for ref in refs
    )
    return f"""          <div class="local-article-information-refs"
            aria-label="Local article references">
{rendered}
          </div>
"""


def _local_article_information_refs(
    items: Sequence[RowOneLocalArticleContentItem],
) -> list[RowOneReference]:
    refs: list[RowOneReference] = []
    seen: set[tuple[str, str, str]] = set()
    for item in items:
        for ref in item.references:
            normalized_name = normalize_row_one_paragraph(ref.name)
            normalized_type = normalize_row_one_paragraph(ref.type)
            normalized_label = normalize_row_one_paragraph(ref.label)
            if not normalized_name:
                continue
            key = (
                normalized_name.casefold(),
                normalized_type.casefold(),
                normalized_label.casefold(),
            )
            if key in seen:
                continue
            seen.add(key)
            refs.append(
                RowOneReference(
                    name=normalized_name,
                    type=normalized_type,
                    label=normalized_label,
                )
            )
            if len(refs) >= LOCAL_ARTICLE_INFORMATION_MAX_REFS:
                return refs
    return refs


def _render_local_article_information_paragraph_links(
    indices: Sequence[object],
    *,
    rendered_indices: set[int],
) -> str:
    valid_indices = _strict_valid_local_article_paragraph_indices(
        indices,
        rendered_indices,
    )[:LOCAL_ARTICLE_INFORMATION_MAX_PARAGRAPH_LINKS]
    if not valid_indices:
        return ""
    links = "\n".join(
        f'            <a href="#{_esc(_local_article_paragraph_anchor(index))}">'
        f'<span data-lang="en">Paragraph {index + 1}</span>'
        f'<span data-lang="zh">段落 {index + 1}</span></a>'
        for index in valid_indices
    )
    return f"""          <div class="local-article-information-paragraphs"
            aria-label="Local article paragraph links">
{links}
          </div>
"""


def _local_article_information_referenced_paragraph_indices(
    article: RowOneLocalArticle,
    *,
    rendered_indices: set[int],
) -> list[int]:
    indices: list[object] = []
    for section in article.content_sections:
        indices.extend(_local_article_information_section_indices(section))
    valid = _strict_valid_local_article_paragraph_indices(indices, rendered_indices)
    if valid:
        return valid
    return sorted(rendered_indices)


def _local_article_information_section_indices(
    section: RowOneLocalArticleContentSection,
) -> list[object]:
    indices: list[object] = []
    for item in section.items:
        indices.extend(item.paragraph_indices)
    return indices


def _local_article_information_excerpt(text: str) -> str:
    return _meta_description(
        normalize_row_one_paragraph(text),
        limit=LOCAL_ARTICLE_INFORMATION_BODY_MAX_CHARS,
    )


def _render_local_article_content_segment_deck(article: RowOneLocalArticle) -> str:
    rendered_indices = _local_article_rendered_paragraph_indices(article)
    if not rendered_indices:
        return ""
    cards: list[str] = []
    for position, section in enumerate(article.content_sections, start=1):
        if len(cards) >= LOCAL_ARTICLE_CONTENT_SEGMENT_DECK_MAX_SECTIONS:
            break
        card = _render_local_article_content_segment_deck_card(
            section,
            position=position,
            rendered_indices=rendered_indices,
        )
        if card:
            cards.append(card)
    if not cards:
        return ""
    body_source = _local_article_body_source_label_localized(article)
    source_name = normalize_row_one_paragraph(article.source_name) or "Unknown source"
    segment_count = len(cards)
    metrics = "".join(
        (
            f"<span>{_esc(_count_label(segment_count, 'segment', 'segments'))}</span>",
            f"<span>{_esc(source_name)}</span>",
            f'<span data-lang="en">{_esc(body_source.en)}</span>',
            f'<span data-lang="zh">{_esc(body_source.zh)}</span>',
        )
    )
    rendered_cards = "\n".join(cards)
    return f"""    <section class="local-article-content-segment-deck"
      aria-labelledby="local-article-content-segment-deck-title">
      <div class="local-article-content-segment-deck-header">
        <h2 id="local-article-content-segment-deck-title">
          <span data-lang="en">Local Article Content Segment Deck</span>
          <span data-lang="zh">本地文章内容段</span>
        </h2>
        <p>
          <span data-lang="en">
            Publish-page content cards from the saved local article structure.
          </span>
          <span data-lang="zh">
            基于本地保存文章结构生成的发布页内容卡片。
          </span>
        </p>
      </div>
      <div class="local-article-content-segment-deck-metrics">{metrics}</div>
      <div class="local-article-content-segment-deck-grid">
{rendered_cards}
      </div>
    </section>"""


def _render_local_article_content_segment_deck_card(
    section: RowOneLocalArticleContentSection,
    *,
    position: int,
    rendered_indices: set[int],
) -> str:
    title = _local_article_content_segment_deck_text(section.title)
    if not title.en and not title.zh:
        return ""
    section_href = f"#{_local_article_content_section_anchor(position)}"
    body = _render_local_article_content_segment_deck_body(section.body)
    items = [
        item_html
        for item in section.items[:LOCAL_ARTICLE_CONTENT_SEGMENT_DECK_MAX_ITEMS_PER_SECTION]
        if (
            item_html := _render_local_article_content_segment_deck_item(
                item,
                rendered_indices=rendered_indices,
            )
        )
    ]
    refs = _render_local_article_content_segment_deck_refs(section.items)
    paragraphs = (
        ""
        if items
        else _render_local_article_content_segment_deck_paragraph_links(
            _local_article_information_section_indices(section),
            rendered_indices=rendered_indices,
        )
    )
    if not body and not items and not refs and not paragraphs:
        return ""
    item_list = (
        '          <ul class="local-article-content-segment-deck-items">\n'
        + "\n".join(items)
        + "\n          </ul>\n"
        if items
        else ""
    )
    action_en = f"Open {title.en or title.zh}"
    action_zh = f"打开{title.zh or title.en}"
    return f"""        <article class="local-article-content-segment-deck-card">
          <h3>
            <span data-lang="en">{_esc(title.en or title.zh)}</span>
            <span data-lang="zh">{_esc(title.zh or title.en)}</span>
          </h3>
{body}{item_list}{refs}{paragraphs}
          <a class="local-article-content-segment-deck-action" href="{_esc(section_href)}">
            <span data-lang="en">{_esc(action_en)}</span>
            <span data-lang="zh">{_esc(action_zh)}</span>
          </a>
        </article>"""


def _render_local_article_content_segment_deck_item(
    item: RowOneLocalArticleContentItem,
    *,
    rendered_indices: set[int],
) -> str:
    label = _local_article_content_segment_deck_text(item.label)
    body = _render_local_article_content_segment_deck_body(item.body, indent=14)
    paragraphs = _render_local_article_content_segment_deck_paragraph_links(
        item.paragraph_indices,
        rendered_indices=rendered_indices,
        indent=14,
    )
    if not label.en and not label.zh and not body and not paragraphs:
        return ""
    heading = ""
    if label.en or label.zh:
        heading = (
            "              <h4>"
            f'<span data-lang="en">{_esc(label.en or label.zh)}</span>'
            f'<span data-lang="zh">{_esc(label.zh or label.en)}</span>'
            "</h4>\n"
        )
    return f"""            <li class="local-article-content-segment-deck-item">
{heading}{body}{paragraphs}
            </li>"""


def _render_local_article_content_segment_deck_body(
    text: LocalizedText | None,
    *,
    indent: int = 10,
) -> str:
    if text is None:
        return ""
    normalized = _local_article_content_segment_deck_text(text)
    if not normalized.en and not normalized.zh:
        return ""
    prefix = " " * indent
    en_excerpt = _local_article_content_segment_deck_excerpt(normalized.en or normalized.zh)
    zh_excerpt = _local_article_content_segment_deck_excerpt(normalized.zh or normalized.en)
    return (
        f"{prefix}<p>"
        f'<span data-lang="en">{_esc(en_excerpt)}</span>'
        f'<span data-lang="zh">{_esc(zh_excerpt)}</span>'
        "</p>\n"
    )


def _render_local_article_content_segment_deck_refs(
    items: Sequence[RowOneLocalArticleContentItem],
    *,
    indent: int = 10,
) -> str:
    refs = _local_article_content_segment_deck_refs(items)
    if not refs:
        return ""
    prefix = " " * indent
    rendered = "\n".join(
        f'{prefix}  <span class="local-article-content-segment-deck-ref">{_esc(ref.name)}'
        f" <span>{_esc(ref.type)} / {_esc(ref.label)}</span></span>"
        for ref in refs
    )
    return f"""{prefix}<div class="local-article-content-segment-deck-refs">
{rendered}
{prefix}</div>
"""


def _local_article_content_segment_deck_refs(
    items: Sequence[RowOneLocalArticleContentItem],
) -> list[RowOneReference]:
    refs: list[RowOneReference] = []
    seen: set[tuple[str, str, str]] = set()
    for item in items:
        for ref in item.references:
            name = normalize_row_one_paragraph(ref.name)
            ref_type = normalize_row_one_paragraph(ref.type)
            label = normalize_row_one_paragraph(ref.label)
            if not name:
                continue
            key = (name.casefold(), ref_type.casefold(), label.casefold())
            if key in seen:
                continue
            seen.add(key)
            refs.append(RowOneReference(name=name, type=ref_type, label=label))
            if len(refs) >= LOCAL_ARTICLE_CONTENT_SEGMENT_DECK_MAX_REFS_PER_SECTION:
                return refs
    return refs


def _render_local_article_content_segment_deck_paragraph_links(
    indices: Sequence[object],
    *,
    rendered_indices: set[int],
    indent: int = 10,
) -> str:
    valid_indices = _strict_valid_local_article_paragraph_indices(
        indices,
        rendered_indices,
    )[:LOCAL_ARTICLE_CONTENT_SEGMENT_DECK_MAX_PARAGRAPH_LINKS]
    if not valid_indices:
        return ""
    prefix = " " * indent
    links = "\n".join(
        f'{prefix}  <a href="#{_esc(_local_article_paragraph_anchor(index))}">'
        f'<span data-lang="en">Paragraph {index + 1}</span>'
        f'<span data-lang="zh">段落 {index + 1}</span></a>'
        for index in valid_indices
    )
    return f"""{prefix}<div class="local-article-content-segment-deck-paragraphs">
{links}
{prefix}</div>
"""


def _local_article_content_segment_deck_text(text: LocalizedText) -> LocalizedText:
    return LocalizedText(
        en=normalize_row_one_paragraph(text.en),
        zh=normalize_row_one_paragraph(text.zh),
    )


def _local_article_content_segment_deck_excerpt(text: str) -> str:
    return _meta_description(
        normalize_row_one_paragraph(text),
        limit=LOCAL_ARTICLE_CONTENT_SEGMENT_DECK_EXCERPT_CHARS,
    )


def _render_local_article_body_organizer(
    organizer: RowOneSavedArticleBodyOrganizer | None,
) -> str:
    if organizer is None or (not organizer.section_rows and not organizer.unfiled_paragraphs):
        return ""
    metrics = "".join(
        _render_local_article_body_organizer_metric(label)
        for label in (
            _count_label(
                organizer.saved_paragraph_count,
                "saved paragraph",
                "saved paragraphs",
            ),
            _count_label(
                organizer.filed_paragraph_count,
                "filed paragraph",
                "filed paragraphs",
            ),
            _count_label(
                organizer.unfiled_paragraph_count,
                "unfiled paragraph",
                "unfiled paragraphs",
            ),
            _count_label(
                organizer.organized_section_count,
                "organized section",
                "organized sections",
            ),
        )
    )
    route = _render_local_article_body_organizer_route(organizer.read_first_route)
    section_rows = "\n".join(
        _render_local_article_body_organizer_row(row) for row in organizer.section_rows
    )
    has_section_rows = bool(section_rows.strip())
    sections = (
        f"""      <div class="local-article-body-organizer-sections">
{section_rows}
      </div>
"""
        if has_section_rows
        else ""
    )
    unfiled = _render_local_article_body_organizer_unfiled(organizer.unfiled_paragraphs)
    return f"""    <section class="local-article-body-organizer"
      aria-labelledby="local-article-body-organizer-title">
      <div class="local-article-body-organizer-header">
        <h2 id="local-article-body-organizer-title">
          <span data-lang="en">Local Article Body Organizer</span>
          <span data-lang="zh">本地正文整理器</span>
        </h2>
        <p>
          <span data-lang="en">
            Filed and unfiled saved text from {_esc(organizer.source_name)}.
          </span>
          <span data-lang="zh">
            来自 {_esc(organizer.source_name)} 的已归档与未归档保存正文。
          </span>
        </p>
      </div>
      <div class="local-article-body-organizer-metrics">{metrics}</div>
      <p class="local-article-body-organizer-title">
        <span data-lang="en">{_esc(organizer.title.en)}</span>
        <span data-lang="zh">{_esc(organizer.title.zh)}</span>
      </p>
{route}{sections}{unfiled}
    </section>"""


def _render_local_article_body_organizer_metric(label: str) -> str:
    return f"<span>{_esc(label)}</span>"


def _render_local_article_body_organizer_route(
    paragraphs: Sequence[RowOneLocalArticleBodyOrganizerParagraph],
) -> str:
    links = "\n".join(
        rendered
        for paragraph in paragraphs
        if (rendered := _render_local_article_body_organizer_paragraph_chip(paragraph, indent=8))
    )
    if not links:
        return ""
    return f"""      <div class="local-article-body-organizer-route"
        aria-label="Body read-first route">
{links}
      </div>
"""


def _render_local_article_body_organizer_row(
    row: RowOneLocalArticleBodyOrganizerSectionRow,
) -> str:
    section_href = _safe_local_article_body_organizer_href(row.section_href)
    if section_href is None:
        return ""
    labels = "".join(
        f'          <span class="local-article-body-organizer-label">'
        f'<span data-lang="en">{_esc(label.en)}</span>'
        f'<span data-lang="zh">{_esc(label.zh)}</span></span>\n'
        for label in row.item_labels
    )
    label_block = (
        f"""        <div class="local-article-body-organizer-labels">
{labels}        </div>
"""
        if labels
        else ""
    )
    support = (
        f"""        <p>
          <span data-lang="en">{_esc(row.support.en)}</span>
          <span data-lang="zh">{_esc(row.support.zh)}</span>
        </p>
"""
        if row.support is not None
        else ""
    )
    paragraph_links = "\n".join(
        rendered
        for paragraph in row.paragraphs
        if (rendered := _render_local_article_body_organizer_paragraph_chip(paragraph, indent=10))
    )
    paragraphs = (
        f"""        <div class="local-article-body-organizer-paragraphs">
{paragraph_links}
        </div>
"""
        if paragraph_links
        else ""
    )
    return f"""        <article class="local-article-body-organizer-row">
          <h3>
            <a href="{_esc(section_href)}">
              <span data-lang="en">{_esc(row.title.en)}</span>
              <span data-lang="zh">{_esc(row.title.zh)}</span>
            </a>
          </h3>
{support}{label_block}{paragraphs}
        </article>"""


def _render_local_article_body_organizer_unfiled(
    paragraphs: Sequence[RowOneLocalArticleBodyOrganizerParagraph],
) -> str:
    links = "\n".join(
        rendered
        for paragraph in paragraphs
        if (rendered := _render_local_article_body_organizer_paragraph_chip(paragraph, indent=8))
    )
    if not links:
        return ""
    return f"""      <div class="local-article-body-organizer-unfiled">
        <h3>
          <span data-lang="en">Unfiled Paragraph Queue</span>
          <span data-lang="zh">未归档段落队列</span>
        </h3>
        <p>
          <span data-lang="en">Saved text not yet cited by an organized section.</span>
          <span data-lang="zh">尚未被整理栏目引用的保存正文。</span>
        </p>
        <div class="local-article-body-organizer-paragraphs">
{links}
        </div>
      </div>
"""


def _render_local_article_body_organizer_paragraph_chip(
    paragraph: RowOneLocalArticleBodyOrganizerParagraph,
    *,
    indent: int,
) -> str:
    href = _safe_local_article_body_organizer_href(paragraph.href)
    if href is None:
        return ""
    prefix = " " * indent
    return (
        f'{prefix}<a href="{_esc(href)}">'
        f'<span data-lang="en">{_esc(paragraph.label.en)}: {_esc(paragraph.excerpt.en)}</span>'
        f'<span data-lang="zh">{_esc(paragraph.label.zh)}：{_esc(paragraph.excerpt.zh)}</span></a>'
    )


def _safe_local_article_body_organizer_href(href: object) -> str | None:
    if not isinstance(href, str) or href != href.strip() or not href.startswith("#"):
        return None
    if any(character.isspace() for character in href):
        return None
    fragment = href[1:]
    if _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment) is not None:
        return href
    if _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment) is not None:
        return href
    return None


def _render_local_article_synthesis_brief(
    brief: RowOneLocalArticleSynthesisBrief | None,
    *,
    local_article: RowOneLocalArticle,
) -> str:
    if brief is None:
        return ""
    cards = "\n".join(
        (
            _render_local_article_synthesis_card(
                LocalizedText(en="The read", zh="阅读判断"),
                brief.lead,
            ),
            _render_local_article_synthesis_card(
                LocalizedText(en="What it sharpens", zh="它强化了什么"),
                brief.thesis,
            ),
            _render_local_article_synthesis_card(
                LocalizedText(en="What the article adds", zh="文章补充了什么"),
                brief.article_adds,
            ),
        )
    )
    anchors = "\n".join(
        rendered
        for anchor in brief.anchors
        if (
            rendered := _render_local_article_synthesis_anchor(
                anchor,
                local_article=local_article,
            )
        )
    )
    anchors_block = (
        f"""      <div class="local-article-synthesis-brief-anchors">
{anchors}
      </div>
"""
        if anchors
        else ""
    )
    return f"""    <section class="local-article-synthesis-brief"
      aria-labelledby="local-article-synthesis-brief-title">
      <div class="local-article-synthesis-brief-header">
        <h2 id="local-article-synthesis-brief-title">
          <span data-lang="en">{_esc(brief.title.en)}</span>
          <span data-lang="zh">{_esc(brief.title.zh)}</span>
        </h2>
        <p>
          <span data-lang="en">A compact synthesis from {_esc(brief.source_name)}.</span>
          <span data-lang="zh">来自 {_esc(brief.source_name)} 的综合判断。</span>
        </p>
      </div>
      <div class="local-article-synthesis-brief-grid">
{cards}
      </div>
      <p class="local-article-synthesis-brief-route">
        <span data-lang="en">{_esc(brief.reader_move.en)}</span>
        <span data-lang="zh">{_esc(brief.reader_move.zh)}</span>
      </p>
{anchors_block}      <p class="local-article-synthesis-brief-basis">
        <span data-lang="en">{_esc(brief.basis_note.en)}</span>
        <span data-lang="zh">{_esc(brief.basis_note.zh)}</span>
      </p>
    </section>"""


def _render_local_article_synthesis_card(
    title: LocalizedText,
    body: LocalizedText,
) -> str:
    return f"""        <article class="local-article-synthesis-brief-card">
          <h3>
            <span data-lang="en">{_esc(title.en)}</span>
            <span data-lang="zh">{_esc(title.zh)}</span>
          </h3>
          <p>
            <span data-lang="en">{_esc(body.en)}</span>
            <span data-lang="zh">{_esc(body.zh)}</span>
          </p>
        </article>"""


def _render_local_article_synthesis_anchor(
    anchor: RowOneLocalArticleSynthesisAnchor,
    *,
    local_article: RowOneLocalArticle,
) -> str:
    href = _safe_local_article_synthesis_href(anchor.href, local_article=local_article)
    if href is None:
        return ""
    support = ""
    if anchor.support is not None and (anchor.support.en or anchor.support.zh):
        support = (
            f'<span data-lang="en">{_esc(anchor.support.en)}</span>'
            f'<span data-lang="zh">{_esc(anchor.support.zh)}</span>'
        )
    return f"""        <a class="local-article-synthesis-brief-anchor" href="{_esc(href)}">
          <strong>
            <span data-lang="en">{_esc(anchor.label.en)}</span>
            <span data-lang="zh">{_esc(anchor.label.zh)}</span>
          </strong>
          {support}
        </a>"""


def _safe_local_article_synthesis_href(
    href: object,
    *,
    local_article: RowOneLocalArticle,
) -> str | None:
    href = _safe_local_article_intelligence_href(href)
    if href is None:
        return None
    fragment = href[1:]
    paragraph_match = _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment)
    if paragraph_match is not None:
        paragraph_number = int(fragment.rsplit("-", 1)[1])
        return (
            href
            if paragraph_number - 1 in _local_article_rendered_paragraph_indices(local_article)
            else None
        )
    section_match = _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment)
    if section_match is not None:
        section_number = int(fragment.rsplit("-", 1)[1])
        return href if 1 <= section_number <= len(local_article.content_sections) else None
    return None


def _render_local_article_intelligence_brief(
    brief: RowOneLocalArticleIntelligenceBrief | None,
) -> str:
    if brief is None or (
        not brief.opening_signal.en
        and not brief.opening_signal.zh
        and not brief.lanes
        and not brief.evidence
        and not brief.routes
    ):
        return ""
    lanes = "\n".join(
        rendered
        for lane in brief.lanes
        if (rendered := _render_local_article_intelligence_lane(lane))
    )
    evidence = "\n".join(
        rendered
        for item in brief.evidence
        if (rendered := _render_local_article_intelligence_evidence(item))
    )
    routes = "\n".join(
        rendered
        for route in brief.routes
        if (rendered := _render_local_article_intelligence_route(route))
    )
    lane_block = (
        f"""      <div class="local-article-intelligence-brief-lanes">
{lanes}
      </div>
"""
        if lanes
        else ""
    )
    evidence_block = (
        f"""      <div class="local-article-intelligence-brief-evidence"
        aria-label="Paragraph evidence trail">
{evidence}
      </div>
"""
        if evidence
        else ""
    )
    route_block = (
        f"""      <div class="local-article-intelligence-brief-route"
        aria-label="Local reader route">
{routes}
      </div>
"""
        if routes
        else ""
    )
    opening = ""
    if brief.opening_signal.en or brief.opening_signal.zh:
        opening = f"""      <p class="local-article-intelligence-brief-opening">
        <span data-lang="en">{_esc(brief.opening_signal.en or brief.opening_signal.zh)}</span>
        <span data-lang="zh">{_esc(brief.opening_signal.zh or brief.opening_signal.en)}</span>
      </p>
"""
    return f"""    <section class="local-article-intelligence-brief"
      aria-labelledby="local-article-intelligence-brief-title">
      <div class="local-article-intelligence-brief-header">
        <h2 id="local-article-intelligence-brief-title">
          <span data-lang="en">{_esc(brief.title.en)}</span>
          <span data-lang="zh">{_esc(brief.title.zh)}</span>
        </h2>
        <p>
          <span data-lang="en">
            Entity lanes, paragraph evidence, and local reading routes from
            {_esc(brief.source_name)}.
          </span>
          <span data-lang="zh">
            来自 {_esc(brief.source_name)} 的实体分道、段落证据与本地阅读路径。
          </span>
        </p>
      </div>
{opening}{lane_block}{evidence_block}{route_block}    </section>"""


def _render_local_article_intelligence_lane(
    lane: RowOneLocalArticleIntelligenceLane,
) -> str:
    chips = "\n".join(
        rendered
        for chip in lane.chips
        if (rendered := _render_local_article_intelligence_chip(chip))
    )
    if not chips:
        return ""
    total = _count_label(lane.total_count, "signal", "signals")
    return f"""        <article class="local-article-intelligence-brief-lane">
          <h3>
            <span data-lang="en">{_esc(lane.title.en)}</span>
            <span data-lang="zh">{_esc(lane.title.zh)}</span>
          </h3>
          <p>{_esc(total)}</p>
          <div>
{chips}
          </div>
        </article>"""


def _render_local_article_intelligence_chip(
    chip: RowOneLocalArticleIntelligenceChip,
) -> str:
    href = _safe_local_article_intelligence_href(chip.href)
    meta = f" <span>{_esc(chip.meta)}</span>" if chip.meta else ""
    label = (
        f'<span data-lang="en">{_esc(chip.label.en or chip.label.zh)}</span>'
        f'<span data-lang="zh">{_esc(chip.label.zh or chip.label.en)}</span>'
        f"{meta}"
    )
    if href is None:
        return f'            <span class="local-article-intelligence-brief-chip">{label}</span>'
    return (
        f'            <a class="local-article-intelligence-brief-chip" '
        f'href="{_esc(href)}">{label}</a>'
    )


def _render_local_article_intelligence_evidence(
    evidence: RowOneLocalArticleIntelligenceEvidence,
) -> str:
    href = _safe_local_article_intelligence_href(evidence.href)
    if href is None:
        return ""
    return f"""        <a href="{_esc(href)}">
          <strong>
            <span data-lang="en">{_esc(evidence.label.en)}</span>
            <span data-lang="zh">{_esc(evidence.label.zh)}</span>
          </strong>
          <span data-lang="en">{_esc(evidence.excerpt.en)}</span>
          <span data-lang="zh">{_esc(evidence.excerpt.zh)}</span>
        </a>"""


def _render_local_article_intelligence_route(
    route: RowOneLocalArticleIntelligenceRoute,
) -> str:
    href = _safe_local_article_intelligence_href(route.href)
    if href is None:
        return ""
    support = ""
    if route.support is not None and (route.support.en or route.support.zh):
        support = (
            f'<span data-lang="en">{_esc(route.support.en or route.support.zh)}</span>'
            f'<span data-lang="zh">{_esc(route.support.zh or route.support.en)}</span>'
        )
    return f"""        <a href="{_esc(href)}">
          <strong>
            <span data-lang="en">{_esc(route.label.en or route.label.zh)}</span>
            <span data-lang="zh">{_esc(route.label.zh or route.label.en)}</span>
          </strong>
          {support}
        </a>"""


def _safe_local_article_intelligence_href(href: object) -> str | None:
    if not isinstance(href, str) or href != href.strip() or not href.startswith("#"):
        return None
    if any(character.isspace() for character in href):
        return None
    fragment = href[1:]
    if _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment) is not None:
        return href
    if _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment) is not None:
        return href
    return None


def _format_datetime(value: datetime) -> str:
    return value.strftime("%b %d, %Y")


def _render_local_article_reader(article: RowOneLocalArticle) -> str:
    items = _local_article_reader_items(article)
    if not items:
        return ""
    count = len(items)
    paragraph_label = "paragraph" if count == 1 else "paragraphs"
    meta_en = f"{count} saved {paragraph_label} from {article.source_name}"
    meta_zh = f"来自 {article.source_name} 的 {count} 个保存段落"
    rendered_items = "\n".join(
        _render_local_article_reader_item(
            position=position,
            paragraph_index=paragraph_index,
            excerpt_en=excerpt_en,
            excerpt_zh=excerpt_zh,
        )
        for position, (paragraph_index, excerpt_en, excerpt_zh) in enumerate(
            items,
            start=1,
        )
    )
    return f"""      <div id="local-article-reader" class="local-article-reader">
        <h4>
          <span data-lang="en">Saved Text Reader</span>
          <span data-lang="zh">保存正文阅读</span>
        </h4>
        <p class="local-article-reader-meta">
          <span data-lang="en">{_esc(meta_en)}</span>
          <span data-lang="zh">{_esc(meta_zh)}</span>
        </p>
        <ol class="local-article-reader-list" aria-label="Saved text paragraphs">
{rendered_items}
        </ol>
      </div>"""


def _local_article_reader_items(article: RowOneLocalArticle) -> list[tuple[int, str, str | None]]:
    aligned_zh = (
        article.paragraphs_zh if len(article.paragraphs_zh) == len(article.paragraphs) else []
    )
    items: list[tuple[int, str, str | None]] = []
    for index, paragraph in enumerate(article.paragraphs):
        if not paragraph.strip():
            continue
        excerpt_en = _local_article_reader_excerpt(paragraph)
        excerpt_zh = None
        if aligned_zh:
            zh = aligned_zh[index]
            excerpt_zh = _local_article_reader_excerpt(zh) if zh.strip() else excerpt_en
        items.append((index, excerpt_en, excerpt_zh))
    return items


def _local_article_reader_excerpt(text: str) -> str:
    return _meta_description(
        normalize_row_one_paragraph(text),
        limit=LOCAL_ARTICLE_READER_EXCERPT_CHARS,
    )


def _render_local_article_reader_item(
    *,
    position: int,
    paragraph_index: int,
    excerpt_en: str,
    excerpt_zh: str | None,
) -> str:
    href = f"#{_local_article_paragraph_anchor(paragraph_index)}"
    number = f"{position:02d}"
    if excerpt_zh is None:
        excerpt = _esc(excerpt_en)
    else:
        excerpt = (
            f'<span data-lang="en">{_esc(excerpt_en)}</span>'
            f'<span data-lang="zh">{_esc(excerpt_zh)}</span>'
        )
    return f"""          <li>
            <a href="{_esc(href)}">
              <span class="local-article-reader-number">{_esc(number)}</span>
              <span class="local-article-reader-excerpt">{excerpt}</span>
            </a>
          </li>"""


def _render_local_article_digest(article: RowOneLocalArticle) -> str:
    if not _local_article_rendered_paragraph_indices(article):
        return ""
    cards = [
        card
        for card in (
            _render_local_article_digest_read_first(article),
            _render_local_article_digest_references(
                article,
                keys=("entities",),
                title_en="People & Brands",
                title_zh="品牌与人物",
            ),
            _render_local_article_digest_references(
                article,
                keys=("product_signals",),
                title_en="Products",
                title_zh="产品",
            ),
            _render_local_article_digest_source_map(article),
        )
        if card
    ]
    if not cards:
        return ""
    rendered_cards = "\n".join(cards)
    return (
        '      <div id="local-article-digest" class="local-article-digest" '
        'aria-label="Saved text digest">\n'
        f"""        <div class="local-article-digest-header">
          <h4>
            <span data-lang="en">Saved Text Digest</span>
            <span data-lang="zh">保存正文整理</span>
          </h4>
          <p>
            <span data-lang="en">A scan-first organization of the existing saved text.</span>
            <span data-lang="zh">基于现有保存正文的速览整理。</span>
          </p>
        </div>
        <div class="local-article-digest-grid">
{rendered_cards}
        </div>
      </div>"""
    )


def _render_local_article_digest_read_first(article: RowOneLocalArticle) -> str:
    takeaway = _local_article_digest_takeaway(article)
    if takeaway is None:
        return ""
    body_en, body_zh, paragraph_indices = takeaway
    rendered_indices = _local_article_rendered_paragraph_indices(article)
    links = _render_local_article_digest_paragraph_links(
        paragraph_indices,
        rendered_indices=rendered_indices,
    )
    body = (
        f'            <span data-lang="en">{_esc(_local_article_digest_excerpt(body_en))}</span>\n'
        f'            <span data-lang="zh">{_esc(_local_article_digest_excerpt(body_zh))}</span>'
        if body_zh is not None
        else f"            {_esc(_local_article_digest_excerpt(body_en))}"
    )
    return f"""          <article class="local-article-digest-card">
            <h4>
              <span data-lang="en">Read First</span>
              <span data-lang="zh">先读</span>
            </h4>
            <p>
{body}
            </p>
{links}
          </article>"""


def _local_article_digest_takeaway(
    article: RowOneLocalArticle,
) -> tuple[str, str | None, list[int]] | None:
    rendered_indices = _local_article_rendered_paragraph_indices(article)
    for section in article.content_sections:
        if section.key != "takeaways":
            continue
        for item in section.items:
            if item.body is None or not item.body.en.strip():
                continue
            return (
                item.body.en,
                item.body.zh if item.body.zh and item.body.zh.strip() else None,
                _valid_local_article_paragraph_indices(
                    item.paragraph_indices,
                    rendered_indices,
                ),
            )
    aligned_zh = (
        article.paragraphs_zh if len(article.paragraphs_zh) == len(article.paragraphs) else []
    )
    for index, paragraph in enumerate(article.paragraphs):
        if not paragraph.strip():
            continue
        zh = aligned_zh[index] if aligned_zh and aligned_zh[index].strip() else None
        return (paragraph, zh, [index])
    return None


def _render_local_article_digest_references(
    article: RowOneLocalArticle,
    *,
    keys: tuple[str, ...],
    title_en: str,
    title_zh: str,
) -> str:
    references: list[RowOneReference] = []
    seen: set[tuple[str, str, str]] = set()
    for section in article.content_sections:
        if section.key not in keys:
            continue
        for item in section.items:
            for ref in item.references:
                normalized_name = normalize_row_one_paragraph(ref.name)
                if not normalized_name:
                    continue
                dedupe_key = (
                    normalized_name.casefold(),
                    ref.type.strip().casefold(),
                    ref.label.strip().casefold(),
                )
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                references.append(ref)
                if len(references) >= LOCAL_ARTICLE_DIGEST_MAX_REFERENCES:
                    break
            if len(references) >= LOCAL_ARTICLE_DIGEST_MAX_REFERENCES:
                break
        if len(references) >= LOCAL_ARTICLE_DIGEST_MAX_REFERENCES:
            break
    if not references:
        return ""
    items = "\n".join(
        f'              <li><span class="local-article-digest-chip">{_esc(ref.name)}</span></li>'
        for ref in references
    )
    return f"""          <article class="local-article-digest-card">
            <h4>
              <span data-lang="en">{_esc(title_en)}</span>
              <span data-lang="zh">{_esc(title_zh)}</span>
            </h4>
            <ul class="local-article-digest-list">
{items}
            </ul>
          </article>"""


def _render_local_article_digest_source_map(article: RowOneLocalArticle) -> str:
    saved_count = _local_article_saved_paragraph_count(article)
    section_count = len(article.content_sections)
    saved_label = "paragraph" if saved_count == 1 else "paragraphs"
    section_label = "section" if section_count == 1 else "sections"
    saved_text_en = f"{saved_count} saved {saved_label}"
    saved_text_zh = f"{saved_count} 个保存段落"
    section_text_en = f"{section_count} organized {section_label}"
    section_text_zh = f"{section_count} 个整理栏目"
    return f"""          <article class="local-article-digest-card">
            <h4>
              <span data-lang="en">Source Map</span>
              <span data-lang="zh">来源结构</span>
            </h4>
            <p>{_esc(article.source_name)}</p>
            <ul class="local-article-digest-list">
{_render_local_article_digest_count_chip(saved_text_en, saved_text_zh)}
{_render_local_article_digest_count_chip(section_text_en, section_text_zh)}
            </ul>
          </article>"""


def _render_local_article_digest_count_chip(label_en: str, label_zh: str) -> str:
    return (
        '              <li><span class="local-article-digest-chip">'
        f'<span data-lang="en">{_esc(label_en)}</span>'
        f'<span data-lang="zh">{_esc(label_zh)}</span>'
        "</span></li>"
    )


def _render_local_article_digest_paragraph_links(
    indices: list[int],
    *,
    rendered_indices: set[int],
) -> str:
    valid_indices = _valid_local_article_paragraph_indices(indices, rendered_indices)
    if not valid_indices:
        return ""
    links: list[str] = []
    for index in valid_indices:
        href = f"#{_local_article_paragraph_anchor(index)}"
        links.append(
            "              "
            f'<li><a href="{_esc(href)}">'
            f'<span data-lang="en">Paragraph {index + 1}</span>'
            f'<span data-lang="zh">段落 {index + 1}</span>'
            "</a></li>"
        )
    rendered_links = "\n".join(links)
    return f"""            <ul class="local-article-digest-link-list">
{rendered_links}
            </ul>"""


def _local_article_digest_excerpt(text: str) -> str:
    return _meta_description(
        normalize_row_one_paragraph(text),
        limit=LOCAL_ARTICLE_DIGEST_EXCERPT_CHARS,
    )


def _render_local_article_map(
    article: RowOneLocalArticle,
    *,
    include_digest: bool = False,
    include_reader: bool = False,
    include_paragraph_evidence: bool = False,
) -> str:
    if not article.brief_sections and not article.content_sections:
        return ""
    links = []
    if article.brief_sections:
        links.append(
            '<a href="#local-article-brief">'
            '<span data-lang="en">Brief</span>'
            '<span data-lang="zh">本地简报</span>'
            "</a>"
        )
    if include_paragraph_evidence:
        links.append(
            '<a href="#local-article-paragraph-evidence">'
            '<span data-lang="en">Evidence</span>'
            '<span data-lang="zh">线索</span>'
            "</a>"
        )
    if include_digest:
        links.append(
            '<a href="#local-article-digest">'
            '<span data-lang="en">Digest</span>'
            '<span data-lang="zh">整理</span>'
            "</a>"
        )
    if include_reader:
        links.append(
            '<a href="#local-article-reader">'
            '<span data-lang="en">Reader</span>'
            '<span data-lang="zh">阅读</span>'
            "</a>"
        )
    for position, section in enumerate(article.content_sections, start=1):
        anchor = f"#{_local_article_content_section_anchor(position)}"
        links.append(
            f'<a href="{_esc(anchor)}">'
            f'<span data-lang="en">{_esc(section.title.en)}</span>'
            f'<span data-lang="zh">{_esc(section.title.zh)}</span>'
            "</a>"
        )
    links.append(
        '<a href="#local-article-body">'
        '<span data-lang="en">Saved text</span>'
        '<span data-lang="zh">保存正文</span>'
        "</a>"
    )
    return (
        '      <nav class="local-article-map" aria-label="ROW ONE local article map">\n'
        + "\n".join(f"        {link}" for link in links)
        + "\n      </nav>"
    )


def _render_local_article_brief(article: RowOneLocalArticle) -> str:
    cards = []
    for section in article.brief_sections:
        cards.append(
            f"""        <article class="local-article-brief-card">
          <h4>
            <span data-lang="en">{_esc(section.title.en)}</span>
            <span data-lang="zh">{_esc(section.title.zh)}</span>
          </h4>
          <p>
            <span data-lang="en">{_esc(section.body.en)}</span>
            <span data-lang="zh">{_esc(section.body.zh)}</span>
          </p>
        </article>"""
        )
    if not cards:
        return ""
    rendered_cards = "\n".join(cards)
    return (
        '      <div id="local-article-brief" class="local-article-brief" '
        'aria-label="ROW ONE brief">\n'
        f"{rendered_cards}\n"
        "      </div>"
    )


def _render_local_article_content_sections(
    article: RowOneLocalArticle,
    *,
    rendered_indices: set[int],
) -> str:
    rendered_sections = []
    for position, section in enumerate(article.content_sections, start=1):
        section_anchor = _local_article_content_section_anchor(position)
        section_parts = [
            f'        <article id="{_esc(section_anchor)}" class="local-article-content-card">',
            "          <h4>",
            f'            <span data-lang="en">{_esc(section.title.en)}</span>',
            f'            <span data-lang="zh">{_esc(section.title.zh)}</span>',
            "          </h4>",
        ]
        if section.body is not None:
            section_parts.extend(
                [
                    "          <p>",
                    f'            <span data-lang="en">{_esc(section.body.en)}</span>',
                    f'            <span data-lang="zh">{_esc(section.body.zh)}</span>',
                    "          </p>",
                ]
            )
        rendered_items = "\n".join(
            _render_local_article_content_item(
                item,
                article=article,
                rendered_indices=rendered_indices,
            )
            for item in section.items
        )
        if rendered_items:
            section_parts.extend(
                [
                    '          <ul class="local-article-content-items">',
                    rendered_items,
                    "          </ul>",
                ]
            )
        section_parts.append("        </article>")
        rendered_sections.append("\n".join(section_parts))
    if not rendered_sections:
        return ""
    rendered = "\n".join(rendered_sections)
    return (
        '      <div class="local-article-content-sections" '
        'aria-label="ROW ONE local article content">\n'
        f"{rendered}\n"
        "      </div>"
    )


def _render_local_article_content_item(
    item: RowOneLocalArticleContentItem,
    *,
    article: RowOneLocalArticle,
    rendered_indices: set[int],
) -> str:
    item_parts = [
        "            <li>",
        "              <strong>",
        f'                <span data-lang="en">{_esc(item.label.en)}</span>',
        f'                <span data-lang="zh">{_esc(item.label.zh)}</span>',
        "              </strong>",
    ]
    if item.body is not None:
        item_parts.extend(
            [
                "              <p>",
                f'                <span data-lang="en">{_esc(item.body.en)}</span>',
                f'                <span data-lang="zh">{_esc(item.body.zh)}</span>',
                "              </p>",
            ]
        )
    previews = _render_local_article_content_paragraph_previews(
        article,
        item,
        rendered_indices=rendered_indices,
    )
    if previews:
        item_parts.append(previews)
    paragraphs = _render_local_article_paragraph_links(
        item.paragraph_indices,
        rendered_indices=rendered_indices,
    )
    if paragraphs:
        item_parts.append(paragraphs)
    refs = _render_local_article_content_references(item.references)
    if refs:
        item_parts.append(refs)
    item_parts.append("            </li>")
    return "\n".join(item_parts)


def _render_local_article_content_paragraph_previews(
    article: RowOneLocalArticle,
    item: RowOneLocalArticleContentItem,
    *,
    rendered_indices: set[int],
) -> str:
    valid_indices = _valid_local_article_paragraph_indices(
        item.paragraph_indices,
        rendered_indices,
    )[:LOCAL_ARTICLE_CONTENT_PREVIEW_MAX_ITEMS]
    if not valid_indices:
        return ""
    aligned_zh = (
        article.paragraphs_zh if len(article.paragraphs_zh) == len(article.paragraphs) else []
    )
    previews: list[str] = []
    for index in valid_indices:
        en = _local_article_content_preview_excerpt(article.paragraphs[index])
        href = f"#{_local_article_paragraph_anchor(index)}"
        label_en = f"Saved paragraph {index + 1}"
        label_zh = f"保存段落 {index + 1}"
        if aligned_zh and aligned_zh[index].strip():
            zh = _local_article_content_preview_excerpt(aligned_zh[index])
            body = f'<span data-lang="en">{_esc(en)}</span><span data-lang="zh">{_esc(zh)}</span>'
        else:
            body = _esc(en)
        previews.append(
            "            "
            f'<li class="local-article-content-preview">'
            f'<a href="{_esc(href)}">'
            f'<span data-lang="en">{_esc(label_en)}</span>'
            f'<span data-lang="zh">{_esc(label_zh)}</span>'
            f"<span>{body}</span>"
            "</a></li>"
        )
    return (
        '          <ul class="local-article-content-previews" '
        'aria-label="Saved paragraph previews">\n' + "\n".join(previews) + "\n          </ul>"
    )


def _local_article_content_preview_excerpt(text: str) -> str:
    return _meta_description(
        normalize_row_one_paragraph(text),
        limit=LOCAL_ARTICLE_CONTENT_PREVIEW_EXCERPT_CHARS,
    )


def _local_article_paragraph_contexts(
    article: RowOneLocalArticle,
    *,
    rendered_indices: set[int] | None = None,
) -> dict[int, list[_LocalArticleParagraphContextCue]]:
    if rendered_indices is None:
        rendered_indices = _local_article_rendered_paragraph_indices(article)
    contexts: dict[int, list[_LocalArticleParagraphContextCue]] = {}
    seen_by_index: dict[int, set[tuple[str, str, str, str, str]]] = {}
    for section_position, section in enumerate(article.content_sections, start=1):
        section_anchor = _local_article_content_section_anchor(section_position)
        section_title_en = normalize_row_one_paragraph(section.title.en)
        section_title_zh = normalize_row_one_paragraph(section.title.zh)
        for item in section.items:
            item_label_en = normalize_row_one_paragraph(item.label.en)
            item_label_zh = normalize_row_one_paragraph(item.label.zh)
            if section_title_en and item_label_en:
                label_en = f"{section_title_en} - {item_label_en}"
            else:
                label_en = item_label_en or section_title_en
            if section_title_zh and item_label_zh:
                label_zh = f"{section_title_zh} - {item_label_zh}"
            else:
                label_zh = item_label_zh or section_title_zh or label_en
            if not label_en:
                continue
            label = LocalizedText(en=label_en, zh=label_zh)
            dedupe_key = (
                section_anchor,
                label.en.casefold(),
                label.zh.casefold(),
                item_label_en.casefold(),
                item_label_zh.casefold(),
            )
            for paragraph_index in _strict_valid_local_article_paragraph_indices(
                item.paragraph_indices,
                rendered_indices,
            ):
                seen = seen_by_index.setdefault(paragraph_index, set())
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                entries = contexts.setdefault(paragraph_index, [])
                if len(entries) < LOCAL_ARTICLE_PARAGRAPH_CONTEXT_LIMIT:
                    entries.append(
                        _LocalArticleParagraphContextCue(
                            anchor=section_anchor,
                            label=label,
                            excerpt=_local_article_paragraph_context_excerpt(
                                article,
                                paragraph_index,
                            ),
                        )
                    )
    return contexts


def _local_article_paragraph_context_excerpt(
    article: RowOneLocalArticle,
    paragraph_index: int,
) -> LocalizedText:
    excerpt_en = _local_article_information_excerpt(article.paragraphs[paragraph_index])
    excerpt_zh = excerpt_en
    if len(article.paragraphs_zh) == len(article.paragraphs):
        paragraph_zh = article.paragraphs_zh[paragraph_index]
        if paragraph_zh.strip():
            excerpt_zh = _local_article_information_excerpt(paragraph_zh)
    return LocalizedText(en=excerpt_en, zh=excerpt_zh)


def _render_local_article_paragraph_context(
    entries: Sequence[_LocalArticleParagraphContextCue],
) -> str:
    if not entries:
        return ""
    links = "".join(
        f'<a href="#{_esc(entry.anchor)}">'
        f'<span data-lang="en">{_esc(entry.label.en)}</span>'
        f'<span data-lang="zh">{_esc(entry.label.zh)}</span></a>'
        for entry in entries
    )
    return (
        '<span class="local-article-paragraph-context">'
        '<span class="local-article-paragraph-context-label">'
        '<span data-lang="en">Used in</span>'
        '<span data-lang="zh">用于</span>'
        "</span>"
        f'<span class="local-article-paragraph-context-links">{links}</span>'
        "</span>"
    )


def _local_article_body_filing_contexts(
    article: RowOneLocalArticle,
    *,
    rendered_indices: set[int] | None = None,
) -> dict[int, list[_LocalArticleParagraphContextCue]]:
    if rendered_indices is None:
        rendered_indices = _local_article_rendered_paragraph_indices(article)
    contexts: dict[int, list[_LocalArticleParagraphContextCue]] = {}
    seen_by_index: dict[int, set[tuple[str, str, str]]] = {}
    for section_position, section in enumerate(article.content_sections, start=1):
        section_anchor = _local_article_content_section_anchor(section_position)
        section_title_en = normalize_row_one_paragraph(section.title.en)
        section_title_zh = normalize_row_one_paragraph(section.title.zh)
        for item in section.items:
            item_label_en = normalize_row_one_paragraph(item.label.en)
            item_label_zh = normalize_row_one_paragraph(item.label.zh)
            label_en = item_label_en or section_title_en
            label_zh = item_label_zh or section_title_zh or label_en
            if not label_en:
                continue
            label = LocalizedText(en=label_en, zh=label_zh)
            dedupe_key = (
                section_anchor,
                label.en.casefold(),
                label.zh.casefold(),
            )
            for paragraph_index in _strict_valid_local_article_paragraph_indices(
                item.paragraph_indices,
                rendered_indices,
            ):
                seen = seen_by_index.setdefault(paragraph_index, set())
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                entries = contexts.setdefault(paragraph_index, [])
                if len(entries) < LOCAL_ARTICLE_BODY_FILING_CUES_MAX_CONTEXTS:
                    entries.append(
                        _LocalArticleParagraphContextCue(
                            anchor=section_anchor,
                            label=label,
                            excerpt=_local_article_paragraph_context_excerpt(
                                article,
                                paragraph_index,
                            ),
                        )
                    )
    return contexts


def _render_local_article_body_filing_cue(
    entries: Sequence[_LocalArticleParagraphContextCue],
) -> str:
    if not entries:
        return (
            '<span class="local-article-body-filing-cue">'
            '<span class="local-article-body-filing-cue-unfiled">'
            '<span data-lang="en">Unfiled saved paragraph</span>'
            '<span data-lang="zh">未归档保存段落</span>'
            "</span>"
            "</span>"
        )
    links = "".join(
        f'<a href="#{_esc(entry.anchor)}">'
        f'<span data-lang="en">{_esc(entry.label.en)}</span>'
        f'<span data-lang="zh">{_esc(entry.label.zh)}</span></a>'
        for entry in entries
    )
    return (
        '<span class="local-article-body-filing-cue">'
        '<span class="local-article-body-filing-cue-label">'
        '<span data-lang="en">Filed under</span>'
        '<span data-lang="zh">已归档到</span>'
        "</span>"
        f'<span class="local-article-body-filing-cue-links">{links}</span>'
        "</span>"
    )


def _render_local_article_body_section_marker(
    marker: RowOneLocalArticleBodySectionMarker,
) -> str:
    section_href = _safe_local_article_body_section_marker_href(marker.section_href)
    paragraph_href = _safe_local_article_body_section_marker_href(marker.paragraph_href)
    labels = "".join(
        f'<span class="local-article-body-section-marker-chip">'
        f'<span data-lang="en">{_esc(label.en or label.zh)}</span>'
        f'<span data-lang="zh">{_esc(label.zh or label.en)}</span>'
        "</span>"
        for label in marker.item_labels
        if label.en or label.zh
    )
    refs = "".join(
        rendered
        for reference in marker.references
        if (rendered := _render_local_article_body_section_marker_ref(reference))
    )
    chips = ""
    if labels or refs:
        chips = (
            f'        <div class="local-article-body-section-marker-chips">{labels}{refs}</div>\n'
        )
    actions: list[str] = []
    if section_href is not None:
        actions.append(
            f'<a href="{_esc(section_href)}">'
            '<span data-lang="en">View content segment</span>'
            '<span data-lang="zh">查看内容段</span></a>'
        )
    if paragraph_href is not None:
        actions.append(
            f'<a href="{_esc(paragraph_href)}">'
            '<span data-lang="en">Continue paragraph</span>'
            '<span data-lang="zh">继续阅读本段</span></a>'
        )
    actions_html = (
        f'        <div class="local-article-body-section-marker-actions">{"".join(actions)}</div>\n'
        if actions
        else ""
    )
    return f"""      <aside class="local-article-body-section-marker">
        <div class="local-article-body-section-marker-header">
          <span>
            <span data-lang="en">Section starts here</span>
            <span data-lang="zh">本节从这里开始</span>
          </span>
          <span>{_esc(str(marker.section_position).zfill(2))}</span>
        </div>
        <h4 class="local-article-body-section-marker-title">
          <span data-lang="en">{_esc(marker.title.en or marker.title.zh)}</span>
          <span data-lang="zh">{_esc(marker.title.zh or marker.title.en)}</span>
        </h4>
        <p class="local-article-body-section-marker-support">
          <span data-lang="en">{_esc(marker.support.en or marker.support.zh)}</span>
          <span data-lang="zh">{_esc(marker.support.zh or marker.support.en)}</span>
        </p>
{chips}{actions_html}      </aside>"""


def _render_local_article_body_section_marker_ref(ref: RowOneReference) -> str:
    name = normalize_row_one_paragraph(ref.name)
    if not name:
        return ""
    meta = " / ".join(
        value
        for value in (
            normalize_row_one_paragraph(ref.type),
            normalize_row_one_paragraph(ref.label),
        )
        if value
    )
    meta_html = f"<span>{_esc(meta)}</span>" if meta else ""
    return f'<span class="local-article-body-section-marker-ref">{_esc(name)}{meta_html}</span>'


def _safe_local_article_body_section_marker_href(href: object) -> str | None:
    if (
        not isinstance(href, str)
        or href != href.strip()
        or not href.startswith("#")
        or any(character.isspace() for character in href)
    ):
        return None
    fragment = href[1:]
    if (
        _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment) is None
        and _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment) is None
    ):
        return None
    return href


def _local_article_rendered_paragraph_indices(article: RowOneLocalArticle) -> set[int]:
    return {index for index, paragraph in enumerate(article.paragraphs) if paragraph.strip()}


def _local_article_paragraph_anchor(index: int) -> str:
    # paragraph_indices are zero-based; fragment IDs are one-based for readers.
    return f"local-article-paragraph-{index + 1}"


def _local_article_content_section_anchor(position: int) -> str:
    return f"local-article-content-section-{position}"


def _valid_local_article_paragraph_indices(
    indices: list[int],
    rendered_indices: set[int],
) -> list[int]:
    # Both inputs use original zero-based RowOneLocalArticle.paragraphs positions.
    valid: list[int] = []
    seen: set[int] = set()
    for index in indices:
        if index not in rendered_indices or index in seen:
            continue
        seen.add(index)
        valid.append(index)
    return valid


def _strict_valid_local_article_paragraph_indices(
    indices: Sequence[object],
    rendered_indices: set[int],
) -> list[int]:
    # Avoid bool/int coercion before building fragment links.
    valid: list[int] = []
    seen: set[int] = set()
    for index in indices:
        if not isinstance(index, int) or isinstance(index, bool):
            continue
        if index not in rendered_indices or index in seen:
            continue
        seen.add(index)
        valid.append(index)
    return valid


def _local_article_paragraph_evidence_entries(
    article: RowOneLocalArticle,
    *,
    rendered_indices: set[int],
) -> tuple[_LocalArticleParagraphEvidenceEntry, ...]:
    mapped: dict[int, list[_LocalArticleParagraphEvidenceItem]] = {}
    seen_items: dict[int, set[tuple[object, ...]]] = {}
    for section_position, section in enumerate(article.content_sections, start=1):
        for item in section.items:
            valid_indices = _strict_valid_local_article_paragraph_indices(
                item.paragraph_indices,
                rendered_indices,
            )
            if not valid_indices:
                continue
            evidence_item = _local_article_paragraph_evidence_item(
                section=section,
                section_position=section_position,
                item=item,
            )
            dedupe_key = _local_article_paragraph_evidence_item_key(evidence_item)
            for index in valid_indices:
                item_keys = seen_items.setdefault(index, set())
                if dedupe_key in item_keys:
                    continue
                item_keys.add(dedupe_key)
                mapped.setdefault(index, []).append(evidence_item)
    if not mapped:
        return ()

    aligned_zh = (
        article.paragraphs_zh if len(article.paragraphs_zh) == len(article.paragraphs) else []
    )
    entries: list[_LocalArticleParagraphEvidenceEntry] = []
    for index in sorted(mapped):
        excerpt_en = _local_article_paragraph_evidence_excerpt(article.paragraphs[index])
        excerpt_zh = (
            _local_article_paragraph_evidence_excerpt(aligned_zh[index])
            if aligned_zh and aligned_zh[index].strip()
            else excerpt_en
        )
        entries.append(
            _LocalArticleParagraphEvidenceEntry(
                paragraph_index=index,
                excerpt=LocalizedText(en=excerpt_en, zh=excerpt_zh),
                items=tuple(mapped[index][:LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_MAX_ITEMS]),
            )
        )
        if len(entries) >= LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_MAX_ROWS:
            break
    return tuple(entries)


def _local_article_paragraph_evidence_item(
    *,
    section: RowOneLocalArticleContentSection,
    section_position: int,
    item: RowOneLocalArticleContentItem,
) -> _LocalArticleParagraphEvidenceItem:
    refs: list[RowOneReference] = []
    seen_refs: set[tuple[str, str, str]] = set()
    for ref in item.references:
        dedupe_key = (
            normalize_row_one_paragraph(ref.name).casefold(),
            normalize_row_one_paragraph(ref.type).casefold(),
            normalize_row_one_paragraph(ref.label).casefold(),
        )
        if dedupe_key in seen_refs:
            continue
        seen_refs.add(dedupe_key)
        refs.append(ref)
        if len(refs) >= LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_MAX_REFS:
            break
    return _LocalArticleParagraphEvidenceItem(
        section_position=section_position,
        section_title=section.title,
        item_label=item.label,
        item_body=item.body,
        references=tuple(refs),
    )


def _local_article_paragraph_evidence_item_key(
    item: _LocalArticleParagraphEvidenceItem,
) -> tuple[object, ...]:
    return (
        item.section_position,
        normalize_row_one_paragraph(item.section_title.en).casefold(),
        normalize_row_one_paragraph(item.section_title.zh).casefold(),
        normalize_row_one_paragraph(item.item_label.en).casefold(),
        normalize_row_one_paragraph(item.item_label.zh).casefold(),
        normalize_row_one_paragraph(item.item_body.en).casefold() if item.item_body else "",
        normalize_row_one_paragraph(item.item_body.zh).casefold() if item.item_body else "",
        tuple(
            (
                normalize_row_one_paragraph(ref.name).casefold(),
                normalize_row_one_paragraph(ref.type).casefold(),
                normalize_row_one_paragraph(ref.label).casefold(),
            )
            for ref in item.references
        ),
    )


def _local_article_paragraph_evidence_excerpt(text: str) -> str:
    return _meta_description(
        normalize_row_one_paragraph(text),
        limit=LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_EXCERPT_CHARS,
    )


def _local_article_paragraph_evidence_body(text: str) -> str:
    return _meta_description(
        normalize_row_one_paragraph(text),
        limit=LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_BODY_CHARS,
    )


def _local_article_paragraph_evidence_body_text(body: LocalizedText) -> LocalizedText:
    en = _local_article_paragraph_evidence_body(body.en)
    zh = _local_article_paragraph_evidence_body(body.zh) if body.zh.strip() else en
    return LocalizedText(en=en, zh=zh)


def _render_local_article_paragraph_evidence(
    article: RowOneLocalArticle,
    *,
    rendered_indices: set[int],
) -> str:
    entries = _local_article_paragraph_evidence_entries(
        article,
        rendered_indices=rendered_indices,
    )
    if not entries:
        return ""
    rendered_entries = "\n".join(
        _render_local_article_paragraph_evidence_entry(entry) for entry in entries
    )
    return (
        '      <div id="local-article-paragraph-evidence" '
        'class="local-article-paragraph-evidence" '
        'aria-label="Saved paragraph evidence">\n'
        f"""        <div class="local-article-paragraph-evidence-header">
          <h4>
            <span data-lang="en">Saved Paragraph Evidence</span>
            <span data-lang="zh">本地段落线索</span>
          </h4>
          <p>
            <span data-lang="en">Saved paragraphs used by the organized ROW ONE reading path.</span>
            <span data-lang="zh">被 ROW ONE 正文整理引用的本地保存段落。</span>
          </p>
        </div>
        <div class="local-article-paragraph-evidence-grid">
{rendered_entries}
        </div>
      </div>"""
    )


def _render_local_article_paragraph_evidence_entry(
    entry: _LocalArticleParagraphEvidenceEntry,
) -> str:
    paragraph_number = entry.paragraph_index + 1
    paragraph_href = f"#{_local_article_paragraph_anchor(entry.paragraph_index)}"
    supports = "\n".join(
        _render_local_article_paragraph_evidence_support(item) for item in entry.items
    )
    return f"""          <article class="local-article-paragraph-evidence-row">
            <a class="local-article-paragraph-evidence-link" href="{_esc(paragraph_href)}">
              <span data-lang="en">Paragraph {paragraph_number}</span>
              <span data-lang="zh">段落 {paragraph_number}</span>
            </a>
            <p class="local-article-paragraph-evidence-excerpt">
              <span data-lang="en">{_esc(entry.excerpt.en)}</span>
              <span data-lang="zh">{_esc(entry.excerpt.zh)}</span>
            </p>
            <div class="local-article-paragraph-evidence-supports">
{supports}
            </div>
          </article>"""


def _render_local_article_paragraph_evidence_support(
    item: _LocalArticleParagraphEvidenceItem,
) -> str:
    section_href = f"#{_local_article_content_section_anchor(item.section_position)}"
    body = ""
    if item.item_body is not None:
        body_text = _local_article_paragraph_evidence_body_text(item.item_body)
        body = (
            "                <p>"
            f'<span data-lang="en">{_esc(body_text.en)}</span>'
            f'<span data-lang="zh">{_esc(body_text.zh)}</span>'
            "</p>\n"
        )
    refs = "".join(_render_local_article_paragraph_evidence_ref(ref) for ref in item.references)
    refs_html = f"                <div>{refs}</div>\n" if refs else ""
    return f"""              <div class="local-article-paragraph-evidence-support">
                <a href="{_esc(section_href)}">
                  <span data-lang="en">{_esc(item.section_title.en)}</span>
                  <span data-lang="zh">{_esc(item.section_title.zh)}</span>
                </a>
                <strong>
                  <span data-lang="en">{_esc(item.item_label.en)}</span>
                  <span data-lang="zh">{_esc(item.item_label.zh)}</span>
                </strong>
{body}{refs_html}              </div>"""


def _render_local_article_paragraph_evidence_ref(ref: RowOneReference) -> str:
    label = f"{ref.name} ({ref.type} / {ref.label})"
    return f'<span class="local-article-paragraph-evidence-ref">{_esc(label)}</span>'


def _render_local_article_paragraph_links(
    indices: list[int],
    *,
    rendered_indices: set[int],
) -> str:
    valid_indices = _valid_local_article_paragraph_indices(indices, rendered_indices)
    if not valid_indices:
        return ""
    en_links: list[str] = []
    zh_links: list[str] = []
    for index in valid_indices:
        href = f"#{_local_article_paragraph_anchor(index)}"
        en_links.append(f'<a href="{_esc(href)}">Paragraph {index + 1}</a>')
        zh_links.append(f'<a href="{_esc(href)}">段落 {index + 1}</a>')
    en = ", ".join(en_links)
    zh = "、".join(zh_links)
    css_class = "local-article-content-meta local-article-content-paragraph-links"
    return f"""              <p class="{css_class}">
                <span data-lang="en">{en}</span>
                <span data-lang="zh">{zh}</span>
              </p>"""


def _render_local_article_content_references(references: list[RowOneReference]) -> str:
    if not references:
        return ""
    en_refs = ", ".join(f"{ref.name} ({ref.type} / {ref.label})" for ref in references)
    zh_refs = "，".join(f"{ref.name}（{ref.type} / {ref.label}）" for ref in references)
    return f"""              <p class="local-article-content-meta">
                <span data-lang="en">Refs: {_esc(en_refs)}</span>
                <span data-lang="zh">引用：{_esc(zh_refs)}</span>
              </p>"""


def _render_local_article_paragraphs(
    article: RowOneLocalArticle,
    *,
    include_body_filing_cues: bool = False,
    body_section_markers: tuple[RowOneLocalArticleBodySectionMarker, ...] = (),
) -> list[str]:
    source_paragraphs = [paragraph for paragraph in article.paragraphs if paragraph.strip()]
    if not source_paragraphs:
        return []
    rendered_indices = _local_article_rendered_paragraph_indices(article)
    body_filing_contexts = (
        _local_article_body_filing_contexts(
            article,
            rendered_indices=rendered_indices,
        )
        if include_body_filing_cues
        else {}
    )
    markers_by_index: dict[int, list[str]] = {}
    if include_body_filing_cues:
        for marker in body_section_markers:
            if marker.paragraph_index not in rendered_indices:
                continue
            rendered_marker = _render_local_article_body_section_marker(marker)
            if rendered_marker:
                markers_by_index.setdefault(marker.paragraph_index, []).append(rendered_marker)
    if len(article.paragraphs_zh) != len(article.paragraphs):
        rendered: list[str] = []
        for index, paragraph in enumerate(article.paragraphs):
            if not paragraph.strip():
                continue
            anchor = _local_article_paragraph_anchor(index)
            filing_cue = (
                _render_local_article_body_filing_cue(body_filing_contexts.get(index, []))
                if include_body_filing_cues and index not in markers_by_index
                else ""
            )
            rendered.extend(markers_by_index.get(index, []))
            rendered.append(f'      <p id="{_esc(anchor)}">{filing_cue}{_esc(paragraph)}</p>')
        return rendered
    paragraph_contexts = _local_article_paragraph_contexts(
        article,
        rendered_indices=rendered_indices,
    )
    rendered: list[str] = []
    for index, (paragraph_en, paragraph_zh) in enumerate(
        zip(article.paragraphs, article.paragraphs_zh, strict=True)
    ):
        if not paragraph_en.strip():
            continue
        zh = paragraph_zh if paragraph_zh.strip() else paragraph_en
        anchor = _local_article_paragraph_anchor(index)
        filing_cue = (
            _render_local_article_body_filing_cue(body_filing_contexts.get(index, []))
            if include_body_filing_cues and index not in markers_by_index
            else ""
        )
        context = _render_local_article_paragraph_context(paragraph_contexts.get(index, []))
        rendered.extend(markers_by_index.get(index, []))
        rendered.append(
            f'      <p id="{_esc(anchor)}">'
            f"{filing_cue}"
            f"{context}"
            f'<span data-lang="en">{_esc(paragraph_en)}</span>'
            f'<span data-lang="zh">{_esc(zh)}</span>'
            "</p>"
        )
    return rendered


def _render_detail_signal_briefing(
    story: RowOneStory,
    local_article: RowOneLocalArticle | None,
) -> str:
    summary_en = _display_summary_text(story.summary.en)
    summary_zh = _display_summary_text(story.summary.zh)
    safe_evidence_count = _safe_evidence_count(story.evidence)
    evidence_label_en = (
        "1 safe evidence link"
        if safe_evidence_count == 1
        else f"{safe_evidence_count} safe evidence links"
    )
    evidence_label_zh = f"{safe_evidence_count} 条安全线索"
    references = _render_detail_signal_briefing_references(story, local_article)
    local_cues = _render_detail_signal_briefing_cues(local_article)
    return f"""<section class="detail-signal-briefing" aria-label="Signal briefing">
  <div class="detail-signal-briefing-header">
    <p>
      <span data-lang="en">Signal Briefing</span>
      <span data-lang="zh">信号简报</span>
    </p>
    <h2>
      <span data-lang="en">What To Know</span>
      <span data-lang="zh">重点整理</span>
    </h2>
  </div>
  <div class="detail-signal-briefing-grid">
    <article class="detail-signal-briefing-card">
      <h3>
        <span data-lang="en">Signal</span>
        <span data-lang="zh">信号</span>
      </h3>
      <p>
        <span data-lang="en">{_esc(summary_en)}</span>
        <span data-lang="zh">{_esc(summary_zh)}</span>
      </p>
      <p class="detail-signal-briefing-meta">
        <span>{_esc(story.source_name)}</span>
        <span data-lang="en">{_esc(evidence_label_en)}</span>
        <span data-lang="zh">{_esc(evidence_label_zh)}</span>
      </p>
    </article>
    <article class="detail-signal-briefing-card">
      <h3>
        <span data-lang="en">Context</span>
        <span data-lang="zh">背景</span>
      </h3>
      <p>
        <span data-lang="en">{_esc(story.signal_context.en)}</span>
        <span data-lang="zh">{_esc(story.signal_context.zh)}</span>
      </p>
    </article>
    <article class="detail-signal-briefing-card">
      <h3>
        <span data-lang="en">References</span>
        <span data-lang="zh">引用对象</span>
      </h3>
      {references}
    </article>
  </div>
{local_cues}
</section>"""


def _render_detail_signal_briefing_references(
    story: RowOneStory,
    local_article: RowOneLocalArticle | None,
) -> str:
    references = _detail_signal_briefing_references(story, local_article)
    if not references:
        return (
            '<p><span data-lang="en">No tracked references yet.</span>'
            '<span data-lang="zh">暂无跟踪引用对象。</span></p>'
        )
    return "\n      ".join(_render_detail_signal_briefing_ref(ref) for ref in references)


def _detail_signal_briefing_references(
    story: RowOneStory,
    local_article: RowOneLocalArticle | None,
) -> list[RowOneReference]:
    references: list[RowOneReference] = []
    seen: set[tuple[str, str, str]] = set()

    def add(ref: RowOneReference) -> None:
        if len(references) >= DETAIL_SIGNAL_BRIEFING_MAX_REFS:
            return
        normalized_name = normalize_row_one_paragraph(ref.name)
        if not normalized_name:
            return
        key = (
            normalized_name.casefold(),
            ref.type.strip().casefold(),
            ref.label.strip().casefold(),
        )
        if key in seen:
            return
        seen.add(key)
        references.append(ref)

    for ref in story.entity_refs:
        add(ref)
    for ref in story.designer_refs:
        add(ref)
    for ref in story.product_refs:
        add(ref)
    if local_article is not None:
        for section in local_article.content_sections:
            for item in section.items:
                for ref in item.references:
                    add(ref)
                    if len(references) >= DETAIL_SIGNAL_BRIEFING_MAX_REFS:
                        return references
    return references


def _render_detail_signal_briefing_ref(ref: RowOneReference) -> str:
    return f'<span class="detail-signal-briefing-ref">{_esc(ref.name)}</span>'


def _render_detail_signal_briefing_cues(article: RowOneLocalArticle | None) -> str:
    cues = _detail_signal_briefing_cues(article)
    if not cues:
        return ""
    rendered = "\n".join(_render_detail_signal_briefing_cue(cue) for cue in cues)
    return f"""  <div class="detail-signal-briefing-cues">
    <h3>
      <span data-lang="en">Local Article Cues</span>
      <span data-lang="zh">本地正文线索</span>
    </h3>
    <div class="detail-signal-briefing-cue-grid">
{rendered}
    </div>
  </div>"""


def _detail_signal_briefing_cues(
    article: RowOneLocalArticle | None,
) -> list[tuple[LocalizedText, LocalizedText, int | None]]:
    if article is None:
        return []
    rendered_indices = _local_article_rendered_paragraph_indices(article)
    content_cues: list[tuple[LocalizedText, LocalizedText, int | None]] = []
    for section in article.content_sections:
        body = section.body
        if body is None:
            body = next((item.body for item in section.items if item.body is not None), None)
        if body is None:
            continue
        content_cues.append(
            (
                section.title,
                body,
                _first_valid_local_article_paragraph_index(section, rendered_indices),
            )
        )
    cues: list[tuple[LocalizedText, LocalizedText, int | None]] = []
    max_brief_cues = DETAIL_SIGNAL_BRIEFING_MAX_CUES
    if content_cues:
        max_brief_cues -= 1
    for section in article.brief_sections:
        cues.append((section.title, section.body, None))
        if len(cues) >= max_brief_cues:
            break
    for cue in content_cues:
        cues.append(cue)
        if len(cues) >= DETAIL_SIGNAL_BRIEFING_MAX_CUES:
            break
    return cues


def _first_valid_local_article_paragraph_index(
    section: RowOneLocalArticleContentSection,
    rendered_indices: set[int],
) -> int | None:
    indices: list[int] = []
    for item in section.items:
        indices.extend(item.paragraph_indices)
    valid = _valid_local_article_paragraph_indices(indices, rendered_indices)
    return valid[0] if valid else None


def _render_detail_signal_briefing_cue(
    cue: tuple[LocalizedText, LocalizedText, int | None],
) -> str:
    title, body, paragraph_index = cue
    paragraph_link = ""
    if paragraph_index is not None:
        href = f"#{_local_article_paragraph_anchor(paragraph_index)}"
        paragraph_link = (
            f'      <a href="{_esc(href)}">'
            f'<span data-lang="en">Paragraph {paragraph_index + 1}</span>'
            f'<span data-lang="zh">段落 {paragraph_index + 1}</span>'
            "</a>\n"
        )
    return f"""      <article class="detail-signal-briefing-cue">
        <h4>
          <span data-lang="en">{_esc(title.en)}</span>
          <span data-lang="zh">{_esc(title.zh)}</span>
        </h4>
        <p>
          <span data-lang="en">{_esc(body.en)}</span>
          <span data-lang="zh">{_esc(body.zh)}</span>
        </p>
{paragraph_link}      </article>"""


def _render_detail_information_map(story: RowOneStory, section_title: LocalizedText) -> str:
    published = _published_label(story)
    safe_evidence_count = _safe_evidence_count(story.evidence)
    evidence_label_en = (
        f"{safe_evidence_count} evidence link"
        if safe_evidence_count == 1
        else f"{safe_evidence_count} evidence links"
    )
    evidence_label_zh = f"{safe_evidence_count} 条线索"
    heat_delta = f"{story.heat_delta:+d}" if isinstance(story.heat_delta, int) else "n/a"
    return f"""<section class="detail-information-map" aria-label="Detail information map">
  <div class="detail-information-map-header">
    <p>
      <span data-lang="en">Structured story scan</span>
      <span data-lang="zh">结构化故事速览</span>
    </p>
    <h2>
      <span data-lang="en">Detail Information Map</span>
      <span data-lang="zh">详情信息地图</span>
    </h2>
  </div>
  <div class="detail-information-map-grid">
    <article class="detail-information-map-card">
      <h3>
        <span data-lang="en">Story Context</span>
        <span data-lang="zh">故事背景</span>
      </h3>
      <p>
        <span data-lang="en">{_esc(section_title.en)}</span>
        <span data-lang="zh">{_esc(section_title.zh)}</span>
      </p>
      <p>{_esc(story.source_name)}</p>
      <p>
        <span data-lang="en">{_esc(published.en)}</span>
        <span data-lang="zh">{_esc(published.zh)}</span>
      </p>
    </article>
    <article class="detail-information-map-card">
      <h3>
        <span data-lang="en">Signal Shape</span>
        <span data-lang="zh">信号形态</span>
      </h3>
      <p>{_esc(_story_type_label(story))}</p>
      <p>{_esc(_joined_tags(story))}</p>
      <p>
        <span data-lang="en">Heat delta</span>
        <span data-lang="zh">热度变化</span>: {_esc(heat_delta)}
      </p>
    </article>
    <article class="detail-information-map-card">
      <h3>
        <span data-lang="en">Evidence</span>
        <span data-lang="zh">证据</span>
      </h3>
      <p>
        <span data-lang="en">{_esc(evidence_label_en)}</span>
        <span data-lang="zh">{_esc(evidence_label_zh)}</span>
      </p>
      <p>{_esc(story.source_name)}</p>
    </article>
    <article class="detail-information-map-card">
      <h3>
        <span data-lang="en">Read Order</span>
        <span data-lang="zh">阅读顺序</span>
      </h3>
      <p>
        <a href="#summary">
          <span data-lang="en">Summary</span>
          <span data-lang="zh">摘要</span>
        </a>
      </p>
      <p>
        <a href="#why-it-matters">
          <span data-lang="en">Why It Matters</span>
          <span data-lang="zh">为什么重要</span>
        </a>
      </p>
      <p>
        <a href="#signal-context">
          <span data-lang="en">Signal Context</span>
          <span data-lang="zh">信号背景</span>
        </a>
      </p>
      <p>
        <a href="#evidence-trail">
          <span data-lang="en">Evidence Trail</span>
          <span data-lang="zh">来源线索</span>
        </a>
      </p>
    </article>
  </div>
</section>"""


def row_one_js() -> str:
    return """(() => {
  const buttons = Array.from(document.querySelectorAll("[data-lang-toggle]"));
  const localizedImages = Array.from(document.querySelectorAll("img[data-alt-en]"));
  const storageKey = "row-one:language";
  const getStoredLang = () => {
    try {
      const stored = window.localStorage.getItem(storageKey);
      return stored === "zh" || stored === "en" ? stored : null;
    } catch {
      return null;
    }
  };
  const persistLang = (lang) => {
    try {
      window.localStorage.setItem(storageKey, lang);
    } catch {
      // Ignore unavailable storage; language toggles still work for this page view.
    }
  };
  const setLang = (lang, options = {}) => {
    document.body.classList.toggle("lang-zh", lang === "zh");
    document.documentElement.lang = lang === "zh" ? "zh-Hans" : "en";
    localizedImages.forEach((image) => {
      if (lang === "zh") {
        image.setAttribute("alt", image.dataset.altZh || image.dataset.altEn || "");
      } else {
        image.setAttribute("alt", image.dataset.altEn || "");
      }
    });
    buttons.forEach((button) => {
      button.setAttribute("aria-pressed", button.dataset.langToggle === lang ? "true" : "false");
    });
    if (options.persist !== false) {
      persistLang(lang);
    }
  };
  buttons.forEach((button) => {
    button.addEventListener("click", () => setLang(button.dataset.langToggle || "en"));
  });
  const initialLang = getStoredLang() || "en";
  setLang(initialLang, { persist: false });
})();
"""


def _meta_description(text: str, *, limit: int = 180) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "…"


def _display_summary_text(text: str) -> str:
    fallback = normalize_row_one_paragraph(text)
    cleaned = clean_row_one_text(protect_literal_angle_tokens(text))
    sentences = clean_row_one_sentences(cleaned, set())
    display_text = normalize_row_one_paragraph(" ".join(sentences))
    return restore_literal_angle_tokens(display_text) or fallback


def _render_meta_tags(*, title: str, description: str, page_type: str) -> str:
    safe_title = _esc(title)
    safe_description = _esc(_meta_description(description))
    safe_type = _esc(page_type)
    return f"""<meta name="description" content="{safe_description}">
<meta property="og:title" content="{safe_title}">
<meta property="og:description" content="{safe_description}">
<meta property="og:type" content="{safe_type}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{safe_title}">
<meta name="twitter:description" content="{safe_description}">"""


def _lead_story(edition: RowOneEdition) -> RowOneStory | None:
    top_stories = edition.section_stories("top_stories")
    if top_stories:
        return top_stories[0]
    return edition.stories[0] if edition.stories else None


def _render_lead_story(
    story: RowOneStory,
    section_title: LocalizedText,
    *,
    local_article: RowOneLocalArticle | None = None,
) -> str:
    detail_href = _internal_detail_href(story.detail_path)
    local_article_href = _local_article_href(story, local_article)
    lead_action_href = _esc(local_article_href) if local_article_href else detail_href
    lead_action_label = (
        LocalizedText(en="Read saved article", zh="阅读本地正文")
        if local_article_href
        else LocalizedText(en="Read the brief", zh="查看详情")
    )
    lead_action_class = (
        "lead-story-link local-read-action" if local_article_href else "lead-story-link"
    )
    local_read_path = _render_homepage_local_read_path(story, local_article)
    visual = _render_story_visual(story, section_title, context="lead-story-visual")
    summary_en = _display_summary_text(story.summary.en)
    summary_zh = _display_summary_text(story.summary.zh)
    return f"""<section class="lead-story" aria-label="Lead story">
  <p class="story-section">
    <span data-lang="en">Lead Story</span>
    <span data-lang="zh">今日头条</span>
  </p>
  <div class="lead-story-grid">
    {visual}
    <div>
      <h2><a href="{detail_href}">{_esc(story.headline)}</a></h2>
      {_render_story_orientation(story, section_title)}
    </div>
    <div>
      <p class="story-takeaway">
        <span data-lang="en">{_esc(story.editorial_takeaway.en)}</span>
        <span data-lang="zh">{_esc(story.editorial_takeaway.zh)}</span>
      </p>
      <p>
        <span data-lang="en">{_esc(summary_en)}</span>
        <span data-lang="zh">{_esc(summary_zh)}</span>
      </p>
      {local_read_path}
      <a class="{_esc(lead_action_class)}" href="{lead_action_href}">
        <span data-lang="en">{_esc(lead_action_label.en)}</span>
        <span data-lang="zh">{_esc(lead_action_label.zh)}</span>
      </a>
    </div>
  </div>
</section>"""


def _render_section(
    edition: RowOneEdition,
    section_key: RowOneSectionKey,
    *,
    local_articles_by_story_id: dict[str, RowOneLocalArticle] | None = None,
) -> str:
    section = next(section for section in edition.sections if section.key == section_key)
    stories = edition.section_stories(section_key)
    local_articles_by_story_id = local_articles_by_story_id or {}
    cards = "\n".join(
        _render_story_card(
            story,
            section.title,
            local_article=local_articles_by_story_id.get(story.id),
        )
        for story in stories
    )
    if not cards:
        cards = (
            '<p class="empty-state">'
            '<span data-lang="en">No stories in this section yet.</span>'
            '<span data-lang="zh">这个栏目暂无故事。</span>'
            "</p>"
        )
    return f"""<section class="section-block" id="{_esc(section.key)}">
  <div class="section-heading">
    <h2>
      <span data-lang="en">{_esc(section.title.en)}</span>
      <span data-lang="zh">{_esc(section.title.zh)}</span>
    </h2>
    <p>
      <span data-lang="en">{_esc(section.dek.en)}</span>
      <span data-lang="zh">{_esc(section.dek.zh)}</span>
    </p>
  </div>
  <div class="story-grid">{cards}</div>
</section>"""


def _render_story_card(
    story: RowOneStory,
    section_title: LocalizedText,
    *,
    local_article: RowOneLocalArticle | None = None,
) -> str:
    detail_href = _internal_detail_href(story.detail_path)
    local_article_href = _local_article_href(story, local_article)
    story_action_href = _esc(local_article_href) if local_article_href else detail_href
    story_action_label = (
        LocalizedText(en="Read saved article", zh="阅读本地正文")
        if local_article_href
        else LocalizedText(en="Read brief", zh="阅读简报")
    )
    story_action_class = (
        "story-detail-link local-read-action" if local_article_href else "story-detail-link"
    )
    local_read_path = _render_homepage_local_read_path(story, local_article)
    published = _published_label(story)
    evidence_count = sum(1 for link in story.evidence if _safe_external_url(link.url) is not None)
    source_name = _esc(story.source_name)
    evidence_label_en = "1 source" if evidence_count == 1 else f"{evidence_count} sources"
    evidence_label_zh = f"{evidence_count} 条来源"
    summary_en = _display_summary_text(story.summary.en)
    summary_zh = _display_summary_text(story.summary.zh)
    tags = "".join(f"<span>{_esc(tag)}</span>" for tag in story.tags)
    tags_block = f'\n  <p class="story-tag-list">{tags}</p>' if tags else ""
    return f"""<article class="story-card">
  {_render_story_visual(story, section_title, context="story-card-visual")}
  <div class="story-card-header">
    <span class="story-source">{source_name}</span>
    <span class="story-date">
      <span data-lang="en">{_esc(published.en)}</span>
      <span data-lang="zh">{_esc(published.zh)}</span>
    </span>
  </div>
  <div class="story-card-body">
    <h3><a href="{detail_href}">{_esc(story.headline)}</a></h3>
    {_render_story_orientation(story, section_title)}
    <p class="story-takeaway">
      <span data-lang="en">{_esc(story.editorial_takeaway.en)}</span>
      <span data-lang="zh">{_esc(story.editorial_takeaway.zh)}</span>
    </p>
    <p>
      <span data-lang="en">{_esc(summary_en)}</span>
      <span data-lang="zh">{_esc(summary_zh)}</span>
    </p>
    {local_read_path}
  </div>
  <div class="story-card-footer">
    <span class="story-evidence-count">
      <span data-lang="en">{_esc(evidence_label_en)}</span>
      <span data-lang="zh">{_esc(evidence_label_zh)}</span>
    </span>
    <a class="{_esc(story_action_class)}" href="{story_action_href}">
      <span data-lang="en">{_esc(story_action_label.en)}</span>
      <span data-lang="zh">{_esc(story_action_label.zh)}</span>
    </a>
  </div>{tags_block}
</article>"""


def _render_story_orientation(story: RowOneStory, section_title: LocalizedText) -> str:
    published = _published_label(story)
    evidence_count = sum(1 for link in story.evidence if _safe_external_url(link.url) is not None)
    evidence_en = "1 evidence link" if evidence_count == 1 else f"{evidence_count} evidence links"
    evidence_zh = f"{evidence_count} 条线索"
    en_parts = [
        section_title.en,
        story.source_name,
        published.en,
        evidence_en,
    ]
    en_text = " · ".join(en_parts)
    zh_text = " · ".join(
        (
            section_title.zh,
            story.source_name,
            published.zh,
            evidence_zh,
        )
    )
    return f"""<p class="story-orientation">
    <span data-lang="en">{_esc(en_text)}</span>
    <span data-lang="zh">{_esc(zh_text)}</span>
  </p>"""


def _render_story_visual(
    story: RowOneStory,
    section_title: LocalizedText,
    *,
    context: str,
) -> str:
    display = display_for_story(story)
    class_name = (
        f"story-visual story-visual--{display.variant} story-visual--{display.accent} {context}"
    )
    image = display.image
    image_src = safe_story_image_src(image.src) if image is not None else None
    if image is not None and image_src is not None:
        if context == "detail-visual" and image_src.startswith("assets/"):
            image_src = f"../{image_src}"
        return (
            f'<figure class="{_esc(class_name)}" data-display-variant="{_esc(display.variant)}">'
            f'<img src="{_esc(image_src)}" alt="{_esc(image.alt.en)}" '
            f'data-alt-en="{_esc(image.alt.en)}" data-alt-zh="{_esc(image.alt.zh)}">'
            "</figure>"
        )

    return f"""<figure class="{_esc(class_name)}" data-display-variant="{_esc(display.variant)}">
  <div class="story-visual-fallback">
    <div class="story-visual-mark">{_esc(_story_visual_initials(story))}</div>
    <div class="story-visual-meta">
      <span>{_esc(display.variant)}</span>
      <span data-lang="en">{_esc(section_title.en)}</span>
      <span data-lang="zh">{_esc(section_title.zh)}</span>
    </div>
  </div>
</figure>"""


def _story_visual_initials(story: RowOneStory) -> str:
    words = re.findall(r"[A-Za-z0-9]+", story.headline.upper())
    if not words:
        return "ROW ONE"
    return " ".join(words[:2])


def _published_label(story: RowOneStory) -> LocalizedText:
    if story.published_at is None:
        return LocalizedText(zh="时间未标注", en="Undated")
    return LocalizedText(
        zh=story.published_at.strftime("%Y-%m-%d"),
        en=story.published_at.strftime("%b %d, %Y"),
    )


def _story_type_label(story: RowOneStory) -> str:
    return story.story_type.replace("_", " ").title()


def _joined_tags(story: RowOneStory) -> str:
    return ", ".join(story.tags) if story.tags else "No tags"


def _safe_evidence_count(evidence: list[RowOneLink]) -> int:
    return sum(1 for link in evidence if _safe_external_url(link.url) is not None)


def _render_evidence(link: RowOneLink) -> str:
    safe_url = _safe_external_url(link.url)
    if safe_url is None:
        return f"""<div class="evidence-item evidence-item--retained">
  <span class="evidence-retained-label">
    <span data-lang="en">Retained source row</span>
    <span data-lang="zh">保留的来源行</span>
  </span>
  <span class="evidence-retained-title">{_esc(link.title)}</span>
  <p class="story-meta">{_esc(link.source_name)}</p>
</div>"""

    rendered = _external_link(link.url, link.title)
    return f"""<div class="evidence-item evidence-item--safe">
  <span class="evidence-label">
    <span data-lang="en">Source</span>
    <span data-lang="zh">来源</span>
  </span>
  {rendered}
  <p class="story-meta">{_esc(link.source_name)}</p>
</div>"""


def _source_action_link(url: str | None) -> str:
    safe_url = _safe_external_url(url)
    if safe_url is None:
        return ""
    return f"""<p class="source-action">
  <a class="source-action-link" href="{_esc(safe_url)}" target="_blank" rel="noopener">
    <span data-lang="en">Open Source Article</span>
    <span data-lang="zh">打开原文</span>
  </a>
</p>"""


def _external_link(url: str | None, text: str, *, css_class: str | None = None) -> str:
    css = f' class="{_esc(css_class)}"' if css_class else ""
    safe_url = _safe_external_url(url)
    if safe_url is None:
        return f"<span{css}>{_esc(text)}</span>"
    return f'<a{css} href="{_esc(safe_url)}" target="_blank" rel="noopener">{_esc(text)}</a>'


def _internal_detail_href(path: str) -> str:
    if _validated_detail_relative_path(path) is None:
        return "#"
    return _esc(path)


def _usable_local_article_paragraph_count(article: RowOneLocalArticle | None) -> int:
    if article is None:
        return 0
    return sum(1 for paragraph in article.paragraphs if normalize_row_one_paragraph(paragraph))


def _local_article_href(
    story: RowOneStory,
    article: RowOneLocalArticle | None,
) -> str | None:
    if _usable_local_article_paragraph_count(article) <= 0:
        return None
    detail_path = _validated_detail_relative_path(story.detail_path)
    if detail_path is None:
        return None
    return f"{detail_path}#local-article"


def _local_read_count_label(count: int) -> LocalizedText:
    paragraph_label = "paragraph" if count == 1 else "paragraphs"
    return LocalizedText(en=f"{count} saved {paragraph_label}", zh=f"{count} 个保存段落")


def _render_homepage_local_read_path(
    story: RowOneStory,
    article: RowOneLocalArticle | None,
) -> str:
    href = _local_article_href(story, article)
    count = _usable_local_article_paragraph_count(article)
    if href is None or count <= 0:
        return ""
    count_label = _local_read_count_label(count)
    return f"""<p class="local-read-path">
      <span class="local-read-path-badge">
        <span data-lang="en">Saved locally</span>
        <span data-lang="zh">本地已保存</span>
      </span>
      <span>
        <span data-lang="en">{_esc(count_label.en)}</span>
        <span data-lang="zh">{_esc(count_label.zh)}</span>
      </span>
    </p>"""


def _render_detail_local_read_path(local_article: RowOneLocalArticle | None) -> str:
    count = _usable_local_article_paragraph_count(local_article)
    if count <= 0:
        return ""
    count_label = _local_read_count_label(count)
    return f"""<p class="local-read-path detail-local-read-path">
  <span class="local-read-path-badge">
    <span data-lang="en">Saved locally</span>
    <span data-lang="zh">本地已保存</span>
  </span>
  <a class="local-read-action" href="#local-article">
    <span data-lang="en">Read saved article</span>
    <span data-lang="zh">阅读本地正文</span>
  </a>
  <span>
    <span data-lang="en">{_esc(count_label.en)}</span>
    <span data-lang="zh">{_esc(count_label.zh)}</span>
  </span>
</p>"""


def _validated_detail_relative_path(path: str) -> PurePosixPath | None:
    return validated_row_one_detail_relative_path(path)


def _safe_external_url(url: str | None) -> str | None:
    return safe_external_url(url)


def _section_title(edition: RowOneEdition, section_key: RowOneSectionKey):
    for section in edition.sections:
        if section.key == section_key:
            return section.title
    return type(edition.summary)(zh=section_key, en=section_key.replace("_", " ").title())


def _esc(value: object) -> str:
    return escape(str(value), quote=True) if value is not None else ""

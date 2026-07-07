from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
ROW_ONE_DOC = ROOT / "docs" / "row-one.md"
ARCHITECTURE_DOC = ROOT / "docs" / "architecture.md"
CLI_REFERENCE = ROOT / "docs" / "cli-reference.md"
FIRST_RUN_DOC = ROOT / "docs" / "first-run.md"
SCHEDULING_DOC = ROOT / "docs" / "scheduling.md"
UPLOAD_CHECKLIST = ROOT / "docs" / "github-upload-checklist.md"
STAGE_327_PLAN = (
    ROOT
    / "docs"
    / "superpowers"
    / "plans"
    / "2026-07-07-stage-327-row-one-saved-signal-index-plan.md"
)
STAGE_327_SPEC = (
    ROOT
    / "docs"
    / "superpowers"
    / "specs"
    / "2026-07-07-stage-327-row-one-saved-signal-index-design.md"
)
STAGE_328_PLAN = (
    ROOT
    / "docs"
    / "superpowers"
    / "plans"
    / "2026-07-07-stage-328-row-one-saved-signal-evidence-excerpts-plan.md"
)
STAGE_328_SPEC = (
    ROOT
    / "docs"
    / "superpowers"
    / "specs"
    / "2026-07-07-stage-328-row-one-saved-signal-evidence-excerpts-design.md"
)
STAGE_328_PLAN_BOUNDARY_DOCS = (
    STAGE_328_SPEC,
    STAGE_328_PLAN,
)
STAGE_327_PLAN_BOUNDARY_DOCS = (
    STAGE_327_SPEC,
    STAGE_327_PLAN,
    ROOT / "docs" / "reviews" / "claude-code-stage-327-plan-review-prompt.md",
    ROOT / "docs" / "reviews" / "opencode-stage-327-plan-review-prompt.md",
    ROOT / "docs" / "reviews" / "opencode-stage-327-plan-review.md",
    ROOT / "docs" / "reviews" / "opencode-stage-327-plan-rereview-prompt.md",
    ROOT / "docs" / "reviews" / "opencode-stage-327-plan-rereview.md",
)
STAGE_327_PLAN_REVIEW_PROMPTS = (
    ROOT / "docs" / "reviews" / "claude-code-stage-327-plan-review-prompt.md",
    ROOT / "docs" / "reviews" / "opencode-stage-327-plan-review-prompt.md",
)
STAGE_327_DRIFT_PHRASES = (
    "row-one-manifest/v2",
    "row-one-runtime/v2",
    "changes schemas",
    "writes a new json artifact",
    "adds a new json artifact",
    "data/saved-signal-index.json",
    "saved-signal-index.html",
    "new generated page",
    "new child page",
    "separate child page",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _without_fenced_code(text: str) -> str:
    return "".join(text.split("```")[::2])


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    assert marker in text
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def test_row_one_docs_keep_local_static_site_boundary() -> None:
    section = _section(_read(ROW_ONE_DOC), "Boundary")
    normalized = _normalized(section)

    for phrase in (
        "row one is a local static site generator",
        "built from existing fashion radar daily report data",
        "presentation-only",
        "does not collect sources",
        "does not run entity matching",
        "does not persist new scoring artifacts",
        "reuses the existing daily report and scoring logic",
        "does not call translation services",
        "does not call llms",
        "does not add paid apis",
        "does not deploy or publish the site",
        "provides no demand proof and no platform coverage verification",
    ):
        assert phrase in normalized


def test_row_one_docs_describe_generated_files_and_cleanup_boundary() -> None:
    section = _section(_read(ROW_ONE_DOC), "Generated Files")
    normalized = _normalized(section)

    for phrase in (
        "`index.html`",
        "`details/`",
        "`articles/index.html`",
        "`articles/`",
        "`assets/row-one.css`",
        "`assets/row-one.js`",
        "`data/edition.json`",
        "`.row-one-site` marker",
        "`data/runtime.json`",
        "`data/local-intelligence.json`",
        "publishable saved local articles for the daily saved article library",
        "remove only known row one generated children",
        "`assets/`, `data/`, and `articles/`",
        "they do not delete unrelated files in the output directory",
        "row-one refresh",
        "prunes older generated report artifacts",
        "`fashion-radar-yyyy-mm-dd.md`",
        "`fashion-radar-yyyy-mm-dd.json`",
        "`fashion-radar-yyyy-mm-dd.html`",
        "report artifact pruning remains separate from sqlite item retention",
        "default 1-day retention",
        "does not prune `collector_runs`",
        "`fashion-radar-yyyy-mm-dd.eml`",
    ):
        assert phrase in normalized


def test_row_one_docs_describe_refresh_sqlite_retention() -> None:
    docs = "\n".join(_normalized(_read(path)) for path in (README, ROW_ONE_DOC, FIRST_RUN_DOC))

    for phrase in (
        "`row-one refresh`",
        "sqlite item retention",
        "default 1-day retention",
        "`--retention-days`",
        "`--skip-data-retention`",
        "after the current site and reports are generated",
        "scoring window",
        "heat scores",
        "does not prune `collector_runs`",
        "does not prune `source_health`",
        "does not prune `entity_first_seen`",
        "does not prune config files",
        "does not prune generated site files",
        "does not change row one contracts",
        "does not change detail routes",
        "does not change schemas",
        "report artifact pruning remains separate",
    ):
        assert phrase in docs

    cli_reference = _normalized(_read(CLI_REFERENCE))
    for phrase in (
        "`row-one refresh`",
        "`--retention-days`",
        "`--skip-data-retention`",
        "sqlite retention",
        "default 1-day retention",
    ):
        assert phrase in cli_reference

    stale_docs = "\n".join(
        _normalized(_read(path)) for path in (README, ROW_ONE_DOC, FIRST_RUN_DOC, CLI_REFERENCE)
    )
    for stale_phrase in (
        "leaving sqlite/data retention to `clean-old-data`",
        "leaves sqlite retention entirely to `clean-old-data`",
        "leaves sqlite/data retention to `clean-old-data`",
    ):
        assert stale_phrase not in stale_docs


def test_row_one_docs_describe_saved_article_reader_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "row-one.md").read_text(encoding="utf-8")

    expected_phrases = [
        "saved text reader",
        "detail-page saved text reader",
        "uses existing `data/articles/<story-id>.json` sidecars",
        "does not change `row-one-app/v7`",
        "does not change `data/edition.json`",
        "does not change `row-one-manifest/v1`",
        "does not change `row-one-runtime/v1`",
        "does not change detail routes",
        "does not change paragraph anchors",
        "does not change schemas",
        "does not add source collection",
        "does not add scoring",
    ]
    for phrase in expected_phrases:
        assert phrase in readme
        assert phrase in docs


def test_row_one_docs_describe_saved_text_digest_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "row-one.md").read_text(encoding="utf-8")

    expected_phrases = [
        "saved text digest",
        "detail-page saved text digest",
        "uses existing `data/articles/<story-id>.json` sidecars",
        "does not change `row-one-app/v7`",
        "does not change `data/edition.json`",
        "does not change `row-one-manifest/v1`",
        "does not change `row-one-runtime/v1`",
        "does not change detail routes",
        "does not change paragraph anchors",
        "does not change schemas",
        "does not add source collection",
        "does not add scoring",
        "does not add llm calls",
    ]
    for phrase in expected_phrases:
        assert phrase in readme
        assert phrase in docs


def test_row_one_docs_describe_saved_article_coverage_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "row-one.md").read_text(encoding="utf-8")
    readme_stage_312 = readme[
        readme.index("Stage 312 adds homepage saved article coverage") : readme.index(
            "Stage 313 adds"
        )
    ]
    docs_stage_312 = docs[
        docs.index("Stage 312 adds homepage saved article coverage") : docs.index("Stage 313 adds")
    ]
    readme_stage_312_normalized = _normalized(readme_stage_312)
    docs_stage_312_normalized = _normalized(docs_stage_312)

    expected_phrases = [
        "saved article coverage",
        "homepage saved article coverage",
        "uses existing `data/articles/<story-id>.json` sidecars",
        "does not change `row-one-app/v7`",
        "does not change `data/edition.json`",
        "does not change `row-one-manifest/v1`",
        "does not change `row-one-runtime/v1`",
        "does not write a new json artifact",
        "does not change detail routes",
        "does not change paragraph anchors",
        "does not change schemas",
        "does not add source collection",
        "does not add scoring",
        "does not add llm calls",
    ]
    for phrase in expected_phrases:
        assert phrase in readme_stage_312_normalized
        assert phrase in docs_stage_312_normalized

    forbidden_phrases = [
        "row-one-app/v8",
        "row-one-manifest/v2",
        "row-one-runtime/v2",
        "changes schemas",
        "changes detail routes",
        "adds source collection",
        "adds scoring",
        "adds llm calls",
        "adds social connectors",
        "adds community connectors",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in readme_stage_312_normalized
        assert phrase not in docs_stage_312_normalized


def test_row_one_docs_describe_saved_article_briefs_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "row-one.md").read_text(encoding="utf-8")
    readme_stage_313 = readme[
        readme.index("Stage 313 adds homepage saved article briefs") : readme.index(
            "Stage 314 adds"
        )
    ]
    docs_stage_313 = docs[
        docs.index("Stage 313 adds homepage saved article briefs") : docs.index("Stage 314 adds")
    ]
    readme_stage_313_normalized = _normalized(readme_stage_313)
    docs_stage_313_normalized = _normalized(docs_stage_313)

    expected_phrases = [
        "saved article briefs",
        "homepage saved article briefs",
        "uses existing `data/articles/<story-id>.json` sidecars",
        "does not change `row-one-app/v7`",
        "does not change `data/edition.json`",
        "does not change `row-one-manifest/v1`",
        "does not change `row-one-runtime/v1`",
        "does not write a new json artifact",
        "does not change detail routes",
        "does not change paragraph anchors",
        "does not change schemas",
        "does not add source collection",
        "does not add scoring",
        "does not add llm calls",
    ]
    for phrase in expected_phrases:
        assert phrase in readme_stage_313_normalized
        assert phrase in docs_stage_313_normalized

    forbidden_phrases = [
        "row-one-app/v8",
        "row-one-manifest/v2",
        "row-one-runtime/v2",
        "changes schemas",
        "changes detail routes",
        "adds source collection",
        "adds scoring",
        "adds llm calls",
        "adds social connectors",
        "adds community connectors",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in readme_stage_313_normalized
        assert phrase not in docs_stage_313_normalized


def test_row_one_docs_describe_local_article_observability_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "row-one.md").read_text(encoding="utf-8")
    readme_stage_314 = readme[
        readme.index("Stage 314 adds local article observability") : readme.index("Stage 315 adds")
    ]
    docs_stage_314 = docs[
        docs.index("Stage 314 adds local article observability") : docs.index("Stage 315 adds")
    ]
    readme_stage_314_normalized = _normalized(readme_stage_314)
    docs_stage_314_normalized = _normalized(docs_stage_314)

    expected_phrases = [
        "local article observability",
        "saved local articles",
        "saved local paragraphs",
        "valid generated `data/articles/<story-id>.json` sidecars",
        "current render's local article metrics",
        "sidecars present on disk",
        "nonblank saved body indicator",
        "row-one status --json",
        "`row_one_article.enabled: true`",
        "optional article extraction dependency",
        "does not change `row-one-app/v7`",
        "does not write a new json artifact",
        "does not add source collection",
        "does not add scoring",
        "does not add llm calls",
    ]
    for phrase in expected_phrases:
        assert phrase in readme_stage_314_normalized
        assert phrase in docs_stage_314_normalized

    forbidden_phrases = [
        "row-one-app/v8",
        "row-one-manifest/v2",
        "row-one-runtime/v2",
        "changes schemas",
        "changes detail routes",
        "adds source collection",
        "adds scoring",
        "adds llm calls",
        "adds social connectors",
        "adds community connectors",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in readme_stage_314_normalized
        assert phrase not in docs_stage_314_normalized


def test_row_one_docs_describe_article_readiness_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "row-one.md").read_text(encoding="utf-8")
    readme_stage_315 = readme[
        readme.index("Stage 315 adds ROW ONE article readiness diagnostics") : readme.index(
            "Stage 316 adds"
        )
    ]
    docs_stage_315 = docs[
        docs.index("Stage 315 adds ROW ONE article readiness diagnostics") : docs.index(
            "Stage 316 adds"
        )
    ]
    readme_stage_315_normalized = _normalized(readme_stage_315)
    docs_stage_315_normalized = _normalized(docs_stage_315)

    expected_phrases = [
        "row one article readiness diagnostics",
        "`row-one article-readiness`",
        "selected `sources.yaml`",
        "saved local article sidecars",
        "saved local paragraphs",
        "current story source coverage",
        "older platformdirs config",
        "`row_one_article.enabled: true`",
        "does not change `row-one-app/v7`",
        "does not write a new generated json artifact",
        "does not add source collection",
        "does not fetch article pages",
        "does not add scoring",
        "does not add llm calls",
    ]
    for phrase in expected_phrases:
        assert phrase in readme_stage_315_normalized
        assert phrase in docs_stage_315_normalized

    forbidden_phrases = [
        "row-one-app/v8",
        "row-one-manifest/v2",
        "row-one-runtime/v2",
        "changes schemas",
        "changes detail routes",
        "adds source collection",
        "adds scoring",
        "adds llm calls",
        "adds social connectors",
        "adds community connectors",
        "adds compliance review",
        "adds compliance-review",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in readme_stage_315_normalized
        assert phrase not in docs_stage_315_normalized


def test_row_one_docs_describe_local_article_content_organization_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "row-one.md").read_text(encoding="utf-8")
    readme_stage_316 = readme[
        readme.index("Stage 316 adds local article content organization") : readme.index(
            "Stage 317 adds"
        )
    ]
    docs_stage_316 = docs[
        docs.index("Stage 316 adds local article content organization") : docs.index(
            "Stage 317 adds"
        )
    ]
    readme_stage_316_normalized = _normalized(readme_stage_316)
    docs_stage_316_normalized = _normalized(docs_stage_316)

    expected_phrases = [
        "local article content organization",
        "existing `data/articles/<story-id>.json` sidecars",
        "existing saved local paragraphs",
        "existing `content_sections`",
        "generated-site only",
        "does not change `row-one-app/v7`",
        "does not change `data/edition.json`",
        "does not change `row-one-manifest/v1`",
        "does not change `row-one-runtime/v1`",
        "does not change detail routes",
        "does not change paragraph anchors",
        "does not change schemas",
        "does not write a new json artifact",
        "does not add source collection",
        "does not fetch article pages",
        "does not add scoring",
        "does not add llm calls",
        "does not add connectors",
        "not a compliance review feature",
    ]
    for phrase in expected_phrases:
        assert phrase in readme_stage_316_normalized
        assert phrase in docs_stage_316_normalized

    forbidden_phrases = [
        "row-one-app/v8",
        "row-one-manifest/v2",
        "row-one-runtime/v2",
        "changes schemas",
        "adds source collection",
        "adds scoring",
        "adds llm calls",
        "adds social connectors",
        "adds community connectors",
        "adds compliance review",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in readme_stage_316_normalized
        assert phrase not in docs_stage_316_normalized


def test_row_one_docs_describe_detail_saved_paragraph_previews_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "row-one.md").read_text(encoding="utf-8")
    readme_stage_317 = readme[
        readme.index("Stage 317 adds detail saved paragraph previews") : readme.index(
            "Stage 318 adds"
        )
    ]
    docs_stage_317 = docs[
        docs.index("Stage 317 adds detail saved paragraph previews") : docs.index("Stage 318 adds")
    ]
    readme_stage_317_normalized = _normalized(readme_stage_317)
    docs_stage_317_normalized = _normalized(docs_stage_317)

    expected_phrases = [
        "detail saved paragraph previews",
        "generated-site only",
        "existing `data/articles/<story-id>.json` sidecars",
        "existing saved local paragraphs",
        "existing `content_sections`",
        "existing paragraph anchors",
        "does not change `row-one-app/v7`",
        "does not change `data/edition.json`",
        "does not change `row-one-manifest/v1`",
        "does not change `row-one-runtime/v1`",
        "does not change detail routes",
        "does not change paragraph anchors",
        "does not change schemas",
        "does not write a new json artifact",
        "does not add source collection",
        "does not fetch article pages",
        "does not add scoring",
        "does not add llm calls",
        "does not add connectors",
        "not a compliance review feature",
    ]
    for phrase in expected_phrases:
        assert phrase in readme_stage_317_normalized
        assert phrase in docs_stage_317_normalized

    forbidden_phrases = [
        "row-one-app/v8",
        "row-one-manifest/v2",
        "row-one-runtime/v2",
        "changes schemas",
        "adds source collection",
        "adds scoring",
        "adds llm calls",
        "adds social connectors",
        "adds community connectors",
        "adds compliance review",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in readme_stage_317_normalized
        assert phrase not in docs_stage_317_normalized


def test_row_one_docs_describe_detail_continue_reading_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "row-one.md").read_text(encoding="utf-8")
    readme_stage_318 = readme[
        readme.index("Stage 318 adds detail continue reading") : readme.index("Stage 319 adds")
    ]
    docs_stage_318 = docs[
        docs.index("Stage 318 adds detail continue reading") : docs.index("Stage 319 adds")
    ]
    readme_stage_318_normalized = _normalized(readme_stage_318)
    docs_stage_318_normalized = _normalized(docs_stage_318)

    expected_phrases = [
        "detail continue reading",
        "generated-site only",
        "same daily edition",
        "validated detail routes",
        "does not change `row-one-app/v7`",
        "does not change `data/edition.json`",
        "does not change `row-one-manifest/v1`",
        "does not change `row-one-runtime/v1`",
        "does not change schemas",
        "does not write a new json artifact",
        "does not add source collection",
        "does not fetch article pages",
        "does not add scoring",
        "does not add llm calls",
        "does not add connectors",
        "not a compliance review feature",
    ]
    for phrase in expected_phrases:
        assert phrase in readme_stage_318_normalized
        assert phrase in docs_stage_318_normalized

    forbidden_phrases = [
        "row-one-app/v8",
        "row-one-manifest/v2",
        "row-one-runtime/v2",
        "changes schemas",
        "adds source collection",
        "adds scoring",
        "adds llm calls",
        "adds social connectors",
        "adds community connectors",
        "adds compliance review",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in readme_stage_318_normalized
        assert phrase not in docs_stage_318_normalized


def test_row_one_docs_describe_detail_signal_briefing_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "row-one.md").read_text(encoding="utf-8")
    readme_stage_319 = readme[
        readme.index("Stage 319 adds detail signal briefing") : readme.index("Stage 320 adds")
    ]
    docs_stage_319 = docs[
        docs.index("Stage 319 adds detail signal briefing") : docs.index("Stage 320 adds")
    ]
    readme_stage_319_normalized = _normalized(readme_stage_319)
    docs_stage_319_normalized = _normalized(docs_stage_319)

    expected_phrases = [
        "detail signal briefing",
        "generated-site only",
        "existing story summary",
        "signal context",
        "safe evidence count",
        "existing story references",
        "existing saved local article sections",
        "signal briefing panel",
        "existing `data/articles/<story-id>.json` sidecars",
        "existing paragraph anchors",
        "does not change `row-one-app/v7`",
        "does not change `data/edition.json`",
        "does not change `row-one-manifest/v1`",
        "does not change `row-one-runtime/v1`",
        "does not change detail routes",
        "does not change paragraph anchors",
        "does not change schemas",
        "does not write a new json artifact",
        "does not add source collection",
        "does not fetch article pages",
        "does not add scoring",
        "does not add llm calls",
        "does not add connectors",
        "not a compliance review feature",
    ]
    for phrase in expected_phrases:
        assert phrase in readme_stage_319_normalized
        assert phrase in docs_stage_319_normalized

    forbidden_phrases = [
        "row-one-app/v8",
        "row-one-manifest/v2",
        "row-one-runtime/v2",
        "changes schemas",
        "adds source collection",
        "adds scoring",
        "adds llm calls",
        "adds social connectors",
        "adds community connectors",
        "adds compliance review",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in readme_stage_319_normalized
        assert phrase not in docs_stage_319_normalized


def test_row_one_docs_describe_homepage_daily_edit_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "row-one.md").read_text(encoding="utf-8")
    readme_stage_320 = readme[
        readme.index("Stage 320 adds homepage Daily Edit") : readme.index("Stage 321 adds")
    ]
    docs_stage_320 = docs[
        docs.index("Stage 320 adds homepage Daily Edit") : docs.index("Stage 321 adds")
    ]
    readme_stage_320_normalized = _normalized(readme_stage_320)
    docs_stage_320_normalized = _normalized(docs_stage_320)

    expected_phrases = [
        "homepage daily edit",
        "generated-site only",
        "scan-first editorial briefing",
        "existing `edition_brief`",
        "existing `signal_synthesis`",
        "existing `daily_digest.briefing_topics`",
        "existing `daily_digest.blocks`",
        "existing story directory",
        "safe internal detail links",
        "does not change `row-one-app/v7`",
        "does not change `data/edition.json`",
        "does not add `daily_edit`",
        "does not change `row-one-manifest/v1`",
        "does not change `row-one-runtime/v1`",
        "does not change schemas",
        "does not write a new json artifact",
        "does not add source collection",
        "does not fetch article pages",
        "does not add scoring",
        "does not add llm calls",
        "does not add connectors",
        "not a compliance review feature",
    ]
    for phrase in expected_phrases:
        assert phrase in readme_stage_320_normalized
        assert phrase in docs_stage_320_normalized

    forbidden_phrases = [
        "row-one-app/v8",
        "row-one-manifest/v2",
        "row-one-runtime/v2",
        "changes schemas",
        "adds source collection",
        "adds scoring",
        "adds llm calls",
        "adds social connectors",
        "adds community connectors",
        "adds compliance review",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in readme_stage_320_normalized
        assert phrase not in docs_stage_320_normalized


def test_row_one_docs_describe_homepage_editorial_brief_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "row-one.md").read_text(encoding="utf-8")
    readme_stage_321 = readme[
        readme.index("Stage 321 adds homepage Editorial Brief") : readme.index("Stage 310 adds")
    ]
    docs_stage_321 = docs[
        docs.index("Stage 321 adds homepage Editorial Brief") : docs.index("Stage 310 adds")
    ]
    readme_stage_321_normalized = _normalized(readme_stage_321)
    docs_stage_321_normalized = _normalized(docs_stage_321)

    expected_phrases = [
        "homepage editorial brief",
        "generated-site only",
        "existing story summaries",
        "existing story signal context",
        "existing saved local article brief sections",
        "existing `data/articles/<story-id>.json` sidecars",
        "existing paragraph anchors",
        "editorial brief / 编辑正文",
        "safe internal detail and paragraph links",
        "does not change `row-one-app/v7`",
        "does not change `data/edition.json`",
        "does not add `editorial_brief`",
        "does not change `row-one-manifest/v1`",
        "does not change `row-one-runtime/v1`",
        "does not change schemas",
        "does not write a new json artifact",
        "does not add source collection",
        "does not fetch article pages",
        "does not add scoring",
        "does not add llm calls",
        "does not add connectors",
        "not a compliance review feature",
    ]
    for phrase in expected_phrases:
        assert phrase in readme_stage_321_normalized
        assert phrase in docs_stage_321_normalized

    forbidden_phrases = [
        "row-one-app/v8",
        "row-one-manifest/v2",
        "row-one-runtime/v2",
        "changes schemas",
        "adds source collection",
        "adds scoring",
        "adds llm calls",
        "adds social connectors",
        "adds community connectors",
        "adds compliance review",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in readme_stage_321_normalized
        assert phrase not in docs_stage_321_normalized


def test_row_one_docs_describe_editorial_source_trail_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "row-one.md").read_text(encoding="utf-8")
    readme_stage_322 = readme[
        readme.index("Stage 322 adds Editorial Source Trail") : readme.index("Stage 321 adds")
    ]
    docs_stage_322 = docs[
        docs.index("Stage 322 adds Editorial Source Trail") : docs.index("Stage 321 adds")
    ]
    readme_stage_322_normalized = _normalized(readme_stage_322)
    docs_stage_322_normalized = _normalized(docs_stage_322)

    expected_phrases = [
        "editorial source trail",
        "existing homepage editorial brief cards",
        "generated-site only",
        "existing saved local article source names",
        "existing saved article titles",
        "existing brief sections",
        "existing content sections",
        "existing `data/articles/<story-id>.json` sidecars",
        "existing paragraph/content-section anchors",
        "compact bilingual provenance chips",
        "safe internal links",
        "does not change `row-one-app/v7`",
        "does not change `data/edition.json`",
        "does not add `editorial_source_trail`",
        "does not add `source_trail`",
        "does not change `row-one-manifest/v1`",
        "does not change `row-one-runtime/v1`",
        "does not change schemas",
        "does not write a new json artifact",
        "does not add source collection",
        "does not fetch article pages",
        "does not add scoring",
        "does not add llm calls",
        "does not add connectors",
        "not a compliance review feature",
    ]
    for phrase in expected_phrases:
        assert phrase in readme_stage_322_normalized
        assert phrase in docs_stage_322_normalized

    forbidden_phrases = [
        "row-one-app/v8",
        "row-one-manifest/v2",
        "row-one-runtime/v2",
        "adds source collection",
        "adds scoring",
        "adds llm calls",
        "adds connectors",
        "adds compliance review",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in readme_stage_322_normalized
        assert phrase not in docs_stage_322_normalized


def test_row_one_docs_describe_saved_signal_index_boundary() -> None:
    expected = _normalized(
        "Stage 327 adds a generated-site only ROW ONE Saved Signal Index inside "
        "`articles/index.html`; it organizes the current edition's saved local "
        "article references by signal and links back into existing detail-page "
        "local article anchors; it does not change row-one-app/v7, "
        "row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, "
        "source collection, fetching, matching, extraction, scoring, ranking, "
        "LLM, connector, scheduling, deployment, or compliance-review behavior."
    )

    for path in (README, ROW_ONE_DOC):
        normalized = _normalized(_read(path))
        assert expected in normalized

        stage = normalized[
            normalized.index("stage 327 adds a generated-site only row one") : normalized.index(
                "stage 326 adds a generated-site only row one"
            )
        ]
        for phrase in (
            "row-one-app/v8",
            *STAGE_327_DRIFT_PHRASES,
            "adds source collection",
            "adds fetching",
            "adds matching",
            "adds extraction",
            "adds scoring",
            "adds ranking",
            "adds llm calls",
            "adds connectors",
            "adds scheduling",
            "adds deployment behavior",
            "adds compliance review",
        ):
            assert phrase not in stage

    for path in STAGE_327_PLAN_BOUNDARY_DOCS:
        normalized = _normalized(_read(path))
        for phrase in STAGE_327_DRIFT_PHRASES:
            assert phrase not in normalized

    for path in STAGE_327_PLAN_REVIEW_PROMPTS:
        normalized = _normalized(_read(path))
        assert "the embedded `articles/index.html` approach is feasible" in normalized
        assert "no-child-page containment is adequately tested" in normalized
        assert "do not propose a separate generated child page for stage 327" in normalized
        assert "better scoped than creating" not in normalized
        assert "articles/entity-index.html" not in normalized


def test_row_one_docs_describe_saved_signal_evidence_excerpts_boundary() -> None:
    expected = _normalized(
        "Stage 328 adds generated-site only evidence excerpts to the existing "
        "ROW ONE Saved Signal Index inside `articles/index.html`; it shows "
        "capped snippets from existing saved local article item bodies or saved "
        "paragraphs and links back into existing detail-page local article "
        "anchors; it does not change row-one-app/v7, row-one-manifest/v1, "
        "row-one-runtime/v1, schemas, JSON artifacts, source collection, "
        "fetching, matching, extraction, scoring, ranking, LLM, connector, "
        "scheduling, deployment, market grouping, domestic/international "
        "classification, or compliance-review behavior."
    )

    for path in (README, ROW_ONE_DOC):
        normalized = _normalized(_read(path))
        assert expected in normalized
        stage_328_pos = normalized.index("stage 328 adds generated-site only evidence excerpts")
        stage_327_pos = normalized.index("stage 327 adds a generated-site only row one")
        assert stage_328_pos < stage_327_pos
        stage = normalized[stage_328_pos:stage_327_pos]
        for phrase in (
            "row-one-app/v8",
            "row-one-manifest/v2",
            "row-one-runtime/v2",
            "saved_signal_excerpt",
            "signal_excerpt",
            "saved-signal-excerpts.json",
            "saved-signal-excerpt.html",
            "adds source collection",
            "adds fetching",
            "adds extraction",
            "adds scoring",
            "adds ranking",
            "adds llm calls",
            "adds connectors",
            "adds scheduling",
            "adds deployment behavior",
            "adds market grouping",
            "adds domestic",
            "adds international",
            "adds compliance review",
        ):
            assert phrase not in stage

    for path in STAGE_328_PLAN_BOUNDARY_DOCS:
        normalized = _normalized(_without_fenced_code(_read(path)))
        for phrase in (
            "row-one-app/v8",
            "row-one-manifest/v2",
            "row-one-runtime/v2",
        ):
            assert phrase not in normalized


def test_row_one_docs_describe_ops_check_boundary() -> None:
    expected = _normalized(
        "Stage 329 adds `row-one ops-check` as a read-only local ROW ONE ops "
        "diagnostic for site freshness, server/port readiness, access URLs, "
        "and user systemd unit-file presence; it does not start servers, install "
        "or enable systemd units, kill processes, refresh or rebuild the site, "
        "write files, change row-one-app/v7, row-one-manifest/v1, "
        "row-one-runtime/v1, schemas, JSON artifacts, source collection, "
        "fetching, extraction, scoring, ranking, LLM, connector, deployment "
        "automation, market grouping, domestic/international classification, "
        "or compliance-review behavior."
    )
    for path in (README, ROW_ONE_DOC):
        normalized = _normalized(_read(path))
        assert expected in normalized
        for phrase in (
            "`ready` status requires generated site files",
            "fresh runtime metadata",
            "local server already serving row one",
            "expected user systemd unit files",
            "missing units keep the result in `attention`",
        ):
            assert phrase in normalized
        stage_329 = normalized[
            normalized.index("stage 329 adds `row-one ops-check`") : normalized.index(
                "stage 328 adds generated-site only evidence excerpts"
            )
        ]
        for phrase in (
            "starts servers",
            "installs systemd",
            "enables systemd",
            "kills processes",
            "refreshes the site",
            "rebuilds the site",
            "writes files",
            "row-one-app/v8",
            "row-one-manifest/v2",
            "row-one-runtime/v2",
            "adds deployment automation",
            "adds compliance review",
        ):
            assert phrase not in stage_329


def test_row_one_docs_describe_local_article_body_provenance_boundary() -> None:
    expected = _normalized(
        "Stage 331 documents local article body provenance for ROW ONE saved "
        "sidecar JSON and generated detail pages: `body_source` distinguishes "
        "`extracted`, `summary_fallback`, and `skipped`; `summary_fallback` "
        "means ROW ONE generated a publishable local article body from the story "
        "summary/editorial fallback when extraction was skipped, failed, or "
        "unusable. This is a sidecar/data detail-page provenance signal only; "
        "it does not change `data/edition.json`, does not change "
        "`row-one-runtime/v1`, and does not add compliance-review behavior."
    )

    for path in (README, ROW_ONE_DOC):
        normalized = _normalized(_read(path))
        assert expected in normalized
        stage_331_start = normalized.index("stage 331 documents local article body provenance")
        stage_331_end = normalized.index("stage 329 adds `row-one ops-check`")
        stage_331 = normalized[stage_331_start:stage_331_end]
        for phrase in (
            "local article body provenance",
            "`body_source`",
            "`extracted`",
            "`summary_fallback`",
            "`skipped`",
            "row one summary fallback",
            "does not change `data/edition.json`",
            "does not change `row-one-runtime/v1`",
            "does not add compliance-review behavior",
        ):
            assert phrase in stage_331

        for stale_phrase in (
            "every saved local article is extracted source text",
            "all saved local article paragraphs are extracted article text",
        ):
            assert stale_phrase not in normalized


def test_row_one_docs_describe_daily_saved_article_library_boundary() -> None:
    expected = _normalized(
        "Stage 326 adds a generated-site only ROW ONE daily saved article library at "
        "`articles/index.html`; it organizes the current edition's saved local "
        "articles by source and links back into existing detail-page local article "
        "anchors; it does not change row-one-app/v7, row-one-manifest/v1, "
        "row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, "
        "scoring, LLM, connector, scheduling, deployment, or compliance-review "
        "behavior."
    )

    for path in (README, ROW_ONE_DOC):
        normalized = _normalized(_read(path))
        assert expected in normalized

        stage = normalized[
            normalized.index("stage 326 adds a generated-site only row one") : normalized.index(
                "stage 324 adds paragraph evidence index"
            )
        ]
        for phrase in (
            "row-one-app/v8",
            "row-one-manifest/v2",
            "row-one-runtime/v2",
            "changes schemas",
            "adds source collection",
            "adds fetching",
            "adds scoring",
            "adds llm calls",
            "adds connectors",
            "adds scheduling",
            "adds deployment behavior",
            "adds compliance review",
        ):
            assert phrase not in stage


def test_row_one_docs_describe_stage_332_saved_article_library_content_groups_boundary() -> None:
    expected = _normalized(
        "Stage 332 adds generated-site only saved article content groups inside "
        "`articles/index.html`; it reuses existing saved local article sidecars and "
        "existing `content_sections` to organize the current edition's saved local "
        "articles by read-first, people/brands, products, and source structure, "
        "with links back to existing detail-page content-section and paragraph "
        "anchors; it does not change row-one-app/v7, row-one-manifest/v1, "
        "row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, "
        "matching, extraction, scoring, ranking, LLM, connector, scheduling, "
        "deployment, market grouping, domestic/international classification, or "
        "compliance-review behavior."
    )

    for path in (README, ROW_ONE_DOC):
        normalized = _normalized(_read(path))
        assert expected in normalized


def test_row_one_docs_describe_stage_334_saved_article_library_local_excerpt_boundary() -> None:
    expected = _normalized(
        "Stage 334 adds generated-site only organized local excerpts to saved "
        "article library cards inside `articles/index.html`; it reuses existing "
        "saved article content organization leads and existing detail-page "
        "content-section and paragraph anchors to show capped per-card read-first "
        "snippets from already-saved local text; it does not publish full articles "
        "on the library index, does not change row-one-app/v7, row-one-manifest/v1, "
        "row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, "
        "matching, extraction, scoring, ranking, LLM, connector, scheduling, "
        "deployment, market grouping, domestic/international classification, or "
        "compliance-review behavior."
    )

    for path in (README, ROW_ONE_DOC):
        normalized = _normalized(_read(path))
        assert expected in normalized
        stage = normalized[
            normalized.index(
                "stage 334 adds generated-site only organized local excerpts"
            ) : normalized.index(
                "stage 333 adds a generated-site only saved article library text-source map"
            )
        ]
        for stale_phrase in (
            "row-one-app/v8",
            "row-one-manifest/v2",
            "row-one-runtime/v2",
            "changes schemas",
            "writes `data/saved-article-library-local-excerpts.json`",
            "publishes full articles",
            "adds source collection",
            "adds fetching",
            "adds extraction",
            "adds scoring",
            "adds ranking",
            "adds llm calls",
            "adds connectors",
            "adds scheduling",
            "adds compliance review",
        ):
            assert stale_phrase not in stage


def test_row_one_docs_describe_stage_336_saved_article_theme_digest_boundary() -> None:
    expected = _normalized(
        "Stage 336 adds generated-site only Saved Article Theme Digest inside "
        "`articles/index.html`; it reuses existing saved local article sidecars, "
        "existing saved local paragraphs, existing saved article content "
        "organization, and existing detail-page "
        "`#local-article-content-section-N` and `#local-article-paragraph-N` "
        "anchors to summarize recurring themes from already-saved local text; "
        "it does not publish full articles on the library index, does not add "
        "LLM-generated summaries, does not change row-one-app/v7, "
        "row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, "
        "source collection, fetching, matching, extraction, scoring, ranking, "
        "LLM, connector, scheduling, deployment, market grouping, "
        "domestic/international classification, or compliance-review behavior."
    )

    for path in (README, ROW_ONE_DOC):
        normalized = _normalized(_read(path))
        assert expected in normalized
        stage = normalized[
            normalized.index(
                "stage 336 adds generated-site only saved article theme digest"
            ) : normalized.index("stage 335 adds generated-site only saved article reading paths")
        ]
        for stale_phrase in (
            "row-one-app/v8",
            "row-one-manifest/v2",
            "row-one-runtime/v2",
            "changes schemas",
            "writes `data/saved-article-theme-digest.json`",
            "writes a new json artifact",
            "publishes full articles",
            "adds source collection",
            "adds fetching",
            "adds extraction",
            "adds scoring",
            "adds ranking",
            "adds connectors",
            "adds scheduling",
            "adds compliance review",
        ):
            assert stale_phrase not in stage


def test_row_one_docs_describe_stage_337_saved_article_reference_atlas_boundary() -> None:
    expected = _normalized(
        "Stage 337 adds generated-site only Saved Article Reference Atlas inside "
        "`articles/index.html`; it reuses existing saved local article sidecars, "
        "existing saved article content organization references, and existing "
        "detail-page `#local-article-content-section-N` and "
        "`#local-article-paragraph-N` anchors to group saved local references "
        "by brands, people, products, and source context; it does not publish "
        "full articles on the library index, does not add outbound article "
        "URLs in the atlas, does not write "
        "`data/saved-article-reference-atlas.json`, does not add LLM-generated "
        "summaries, does not add trend scoring or heat ranking, does not change "
        "row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, "
        "JSON artifacts, source collection, fetching, matching, extraction, "
        "scoring, ranking, LLM, connector, scheduling, deployment, market "
        "grouping, domestic/international classification, or compliance-review "
        "behavior."
    )

    for path in (README, ROW_ONE_DOC):
        normalized = _normalized(_read(path))
        assert expected in normalized
        stage = normalized[
            normalized.index(
                "stage 337 adds generated-site only saved article reference atlas"
            ) : normalized.index("stage 336 adds generated-site only saved article theme digest")
        ]
        for stale_phrase in (
            "row-one-app/v8",
            "row-one-manifest/v2",
            "row-one-runtime/v2",
            "changes schemas",
            "writes `data/saved-article-reference-atlas.json`",
            "writes a new json artifact",
            "publishes full articles",
            "adds outbound article urls",
            "adds source collection",
            "adds fetching",
            "adds extraction",
            "adds trend scoring",
            "adds heat ranking",
            "adds connectors",
            "adds scheduling",
            "adds compliance review",
        ):
            assert stale_phrase not in stage


def test_row_one_docs_describe_stage_338_saved_article_paragraph_evidence_board_boundary() -> None:
    expected = _normalized(
        "Stage 338 adds generated-site only Saved Article Paragraph Evidence Board "
        "inside `articles/index.html`; it reuses existing saved local article "
        "sidecars, existing saved local paragraphs, existing saved article content "
        "organization paragraph indices, existing saved article library routes, "
        "and existing detail-page `#local-article-content-section-N` and "
        "`#local-article-paragraph-N` anchors to show capped local paragraph "
        "evidence excerpts behind saved article sections; it does not publish "
        "full articles on the library index, does not add outbound article URLs "
        "in the evidence board, does not write "
        "`data/saved-article-evidence-board.json`, does not add LLM-generated "
        "summaries, does not add extraction, ranking, trend scoring, or heat "
        "ranking, does not change row-one-app/v7, row-one-manifest/v1, "
        "row-one-runtime/v1, schemas, JSON artifacts, source collection, "
        "fetching, matching, extraction, scoring, ranking, LLM, connector, "
        "scheduling, deployment, market grouping, domestic/international "
        "classification, or compliance-review behavior."
    )

    for path in (README, ROW_ONE_DOC):
        normalized = _normalized(_read(path))
        assert expected in normalized
        stage_338_pos = normalized.index(
            "stage 338 adds generated-site only saved article paragraph evidence board"
        )
        stage_337_pos = normalized.index(
            "stage 337 adds generated-site only saved article reference atlas"
        )
        assert stage_338_pos < stage_337_pos
        stage = normalized[stage_338_pos:stage_337_pos]
        for stale_phrase in (
            "row-one-app/v8",
            "row-one-manifest/v2",
            "row-one-runtime/v2",
            "changes schemas",
            "writes `data/saved-article-evidence-board.json`",
            "writes a new json artifact",
            "publishes full articles",
            "adds outbound article urls",
            "adds source collection",
            "adds fetching",
            "adds matching",
            "adds extraction",
            "adds ranking",
            "adds trend scoring",
            "adds heat ranking",
            "adds connectors",
            "adds scheduling",
            "adds deployment behavior",
            "adds social",
            "adds community",
            "adds compliance review",
        ):
            assert stale_phrase not in stage


def test_row_one_docs_describe_stage_335_saved_article_reading_paths_boundary() -> None:
    expected = _normalized(
        "Stage 335 adds generated-site only Saved Article Reading Paths inside "
        "`articles/index.html`; it reuses existing saved article library cards, "
        "existing saved article content organization leads, existing detail-page "
        "content-section anchors, and existing paragraph anchors to show capped "
        "read-first paths through already-saved local text; it does not publish "
        "full articles on the library index, does not change row-one-app/v7, "
        "row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, "
        "source collection, fetching, matching, extraction, scoring, ranking, "
        "LLM, connector, scheduling, deployment, market grouping, "
        "domestic/international classification, or compliance-review behavior."
    )

    for path in (README, ROW_ONE_DOC):
        normalized = _normalized(_read(path))
        assert expected in normalized
        stage = normalized[
            normalized.index(
                "stage 335 adds generated-site only saved article reading paths"
            ) : normalized.index("stage 334 adds generated-site only organized local excerpts")
        ]
        for stale_phrase in (
            "row-one-app/v8",
            "row-one-manifest/v2",
            "row-one-runtime/v2",
            "changes schemas",
            "writes `data/saved-article-reading-paths.json`",
            "writes a new json artifact",
            "publishes full articles",
            "adds source collection",
            "adds fetching",
            "adds extraction",
            "adds scoring",
            "adds ranking",
            "adds llm calls",
            "adds connectors",
            "adds scheduling",
            "adds compliance review",
        ):
            assert stale_phrase not in stage


def test_row_one_docs_describe_stage_333_saved_article_library_text_source_boundary() -> None:
    expected = _normalized(
        "Stage 333 adds a generated-site only saved article library text-source "
        "map inside `articles/index.html`; it reuses existing saved local article "
        "`body_source` values to show included-library counts and per-card text "
        "source chips for extracted article text, ROW ONE summary fallback, and "
        "skipped saved bodies; it does not expose fallback reasons, does not "
        "change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, "
        "JSON artifacts, source collection, fetching, matching, extraction, "
        "scoring, ranking, LLM, connector, scheduling, deployment, market "
        "grouping, domestic/international classification, or compliance-review "
        "behavior."
    )

    for path in (README, ROW_ONE_DOC):
        normalized = _normalized(_read(path))
        assert expected in normalized
        stage = normalized[
            normalized.index(
                "stage 333 adds a generated-site only saved article library text-source map"
            ) : normalized.index("stage 332 adds generated-site only saved article content groups")
        ]
        for stale_phrase in (
            "row-one-app/v8",
            "row-one-manifest/v2",
            "row-one-runtime/v2",
            "changes schemas",
            "adds source collection",
            "adds fetching",
            "adds extraction",
            "adds scoring",
            "adds ranking",
            "adds llm calls",
            "adds connectors",
            "adds scheduling",
            "adds compliance review",
            "writes `data/saved-article-library.json`",
            "exposes fallback reasons",
        ):
            assert stale_phrase not in stage


def test_row_one_docs_describe_stage_324_paragraph_evidence_index_boundary() -> None:
    readme = _normalized(_read(README))
    docs = _normalized(_read(ROW_ONE_DOC))

    for content in (readme, docs):
        stage = content[
            content.index("stage 324 adds paragraph evidence index") : content.index(
                "stage 323 adds local-first reading"
            )
        ]
        for phrase in (
            "paragraph evidence index",
            "saved paragraph evidence",
            "`rowonelocalarticle.content_sections`",
            "`paragraph_indices`",
            "`references`",
            "`#local-article-paragraph-n`",
            "`#local-article-content-section-n`",
            "generated-site only",
            "does not change `row-one-app/v7`",
            "does not change `data/edition.json`",
            "does not change `row-one-manifest/v1`",
            "does not change `row-one-runtime/v1`",
            "does not change schemas",
            "does not write a new json artifact",
            "does not add source collection",
            "does not fetch article pages",
            "does not add extraction",
            "does not add scoring",
            "does not add ranking",
            "does not add connectors",
            "does not add llm calls",
            "does not add translation calls",
            "does not add image generation",
            "does not add scheduling",
            "does not add deployment behavior",
            "does not add compliance-review product features",
        ):
            assert phrase in stage
        for phrase in (
            "adds source collection",
            "adds article fetching",
            "adds extraction",
            "adds scoring",
            "adds ranking",
            "adds connectors",
            "adds llm calls",
            "adds scheduling",
            "adds deployment behavior",
            "adds compliance review",
        ):
            assert phrase not in stage


def test_row_one_docs_describe_local_first_reading_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "row-one.md").read_text(encoding="utf-8")
    readme_stage_323 = readme[
        readme.index("Stage 323 adds Local-First Reading") : readme.index("Stage 322 adds")
    ]
    docs_stage_323 = docs[
        docs.index("Stage 323 adds Local-First Reading") : docs.index("Stage 322 adds")
    ]
    readme_stage_323_normalized = _normalized(readme_stage_323)
    docs_stage_323_normalized = _normalized(docs_stage_323)

    expected_phrases = [
        "local-first reading",
        "generated-site only",
        "existing `data/articles/<story-id>.json` sidecars",
        "existing saved local paragraphs",
        "existing `#local-article`",
        "existing `#local-article-paragraph-n`",
        "safe internal links",
        "read saved article",
        "saved article content-organization cards",
        "does not change `row-one-app/v7`",
        "does not change `data/edition.json`",
        "does not change `row-one-manifest/v1`",
        "does not change `row-one-runtime/v1`",
        "does not add `local_first_read`",
        "does not add `local_read_path`",
        "does not add `saved_article_cta`",
        "does not add `evidence_paragraph_trail`",
        "does not change schemas",
        "does not write a new json artifact",
        "does not add source collection",
        "does not fetch article pages",
        "does not add scoring",
        "does not add llm calls",
        "does not add connectors",
        "not a compliance review feature",
    ]
    for phrase in expected_phrases:
        assert phrase in readme_stage_323_normalized
        assert phrase in docs_stage_323_normalized

    forbidden_phrases = [
        "row-one-app/v8",
        "row-one-manifest/v2",
        "row-one-runtime/v2",
        "changes schemas",
        "adds source collection",
        "adds scoring",
        "adds llm calls",
        "adds connectors",
        "adds compliance review",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in readme_stage_323_normalized
        assert phrase not in docs_stage_323_normalized


def test_row_one_docs_include_user_required_phrases() -> None:
    normalized = _normalized(_read(ROW_ONE_DOC))

    for phrase in (
        "row one",
        "row-one build",
        "row-one article-readiness",
        "article readiness",
        "row_one_article.enabled: true",
        "saved local articles",
        "saved local paragraphs",
        "older platformdirs config",
        "row-one refresh",
        "row-one preview",
        "row-one status",
        "row-one local-ops",
        "row-one install-local",
        "row-one serve",
        "row-one schedule",
        "04:00 local scheduling",
        "fixed ip:port",
        "latest-only cleanup",
        "ip:port local-network serving",
        "open from lan: http://<lan-ip>:8787",
        "fashion-radar row-one refresh",
        "fashion-radar row-one preview",
        "fashion-radar row-one status",
        "fashion-radar row-one install-local",
        "--latest-only",
        "prints snippets only",
        "does not install timers",
        "open design imagery is optional and not required for tests.",
    ):
        assert phrase in normalized


def test_row_one_docs_describe_editorial_synthesis_boundary() -> None:
    normalized = _normalized(_read(ROW_ONE_DOC))

    for phrase in (
        "editorial synthesis",
        "deterministic",
        "not translation",
        "not llm",
        "not new scoring",
        "not demand proof",
    ):
        assert phrase in normalized


def test_row_one_docs_describe_reader_orientation_boundary() -> None:
    normalized = _normalized(_read(ROW_ONE_DOC))

    for phrase in (
        "reader orientation",
        "edition contents",
        "section jump links",
        "story-card metadata",
        "back to section",
        "presentation-only",
    ):
        assert phrase in normalized


def test_row_one_docs_describe_display_media_readiness() -> None:
    normalized = _normalized(_read(ROW_ONE_DOC))

    for phrase in (
        "display/media readiness",
        "`display` object",
        "`display.image` is `null` until a safe image path is available",
        "safe `assets/...` image paths",
        "typographic fallback visual",
        "opendesign imagery is optional and not required for tests.",
        "open design imagery is optional and not required for tests.",
    ):
        assert phrase in normalized


def test_row_one_docs_describe_versioned_app_json_contract() -> None:
    normalized = _normalized(_read(ROW_ONE_DOC))
    architecture = _normalized(_read(ARCHITECTURE_DOC))

    for phrase in (
        "app json contract",
        "`data/edition.json` is the row-one-app/v7 app-facing contract",
        "`schemas/row-one-app.schema.json`",
        "section counts",
        "detail hrefs",
        "published dates",
        "evidence counts",
        "sanitized urls",
        "story_count",
        "evidence_count",
        "detail_href",
        "href",
    ):
        assert phrase in normalized
    assert "versioned app json" in architecture


def test_row_one_docs_describe_stage_271_app_content_organization() -> None:
    row_one = _normalized(_read(ROW_ONE_DOC))
    readme = _normalized(_read(README))

    for phrase in (
        "row-one-app/v7",
        "content_sections",
        "detail_sections",
        "evidence_summary",
        "section rails",
        "app clients render section rails",
        "app clients render section rails without scraping html",
        "content organization",
        "homepage rails",
        "detail-page rails",
        "active app version",
    ):
        assert phrase in row_one

    for phrase in (
        "row-one-app/v7",
        "content_sections",
        "detail_sections",
        "evidence_summary",
        "app clients can render section rails",
    ):
        assert phrase in readme

    assert "row-one-app/v1 app-facing contract" not in row_one
    assert "row-one-app/v1` json contract" not in row_one


def test_row_one_docs_describe_stage_286_edition_brief() -> None:
    row_one = _normalized(_read(ROW_ONE_DOC))
    readme = _normalized(_read(README))

    for phrase in (
        "edition_brief",
        "edition brief",
        "daily overview",
        "top-level `data/edition.json` field",
        (
            "same `edition_brief` object before `signal_synthesis`, the lead story, "
            "briefing topics, briefing path, and story rails"
        ),
        (
            "derived from existing row one story, content section, digest block, "
            "briefing topic, route, and safe evidence-count data"
        ),
        "empty editions keep `edition_brief` present",
        "lead fields are `null`",
        "links may be empty",
        "does not add source collection",
        "does not change matching, ranking, scoring, sorting, or story ids",
    ):
        assert phrase in row_one

    for phrase in (
        "edition_brief",
        "daily overview",
        (
            "derived from existing row one stories, content sections, "
            "digest blocks/topics, route data, and safe evidence counts"
        ),
        "not a collection or ranking layer",
    ):
        assert phrase in readme


def test_row_one_docs_describe_stage_295_edition_brief_content_organization() -> None:
    normalized = _normalized(_read(ROW_ONE_DOC))

    for phrase in (
        "edition_brief.summary_points",
        "read-first orientation",
        "active-section coverage",
        "explicit topic-mix counts",
        "brands, products, designers, and people",
        "positive heat-watch cues",
        "local raw mention deltas",
    ):
        assert phrase in normalized


def test_row_one_docs_describe_stage_287_signal_synthesis() -> None:
    row_one = _normalized(_read(ROW_ONE_DOC))
    readme = _normalized(_read(README))

    for phrase in (
        "signal_synthesis",
        "signal synthesis",
        "local observed",
        "review required",
        "top-level `data/edition.json` field",
        "derived from `daily_digest.briefing_topics`",
        "brand/product/designer/person summaries",
        "does not add collection",
        "does not change matching, ranking, scoring, sorting, or story ids",
    ):
        assert phrase in row_one

    synthesis_section = row_one.split(
        "`signal_synthesis` is a top-level `data/edition.json` field",
        1,
    )[1].split("##", 1)[0]
    assert "local observed" in synthesis_section
    assert "review required" in synthesis_section
    for forbidden in ("demand proof", "verified coverage", "platform heat", "globally trending"):
        assert forbidden not in synthesis_section

    for phrase in (
        "signal_synthesis",
        "local observed",
        "review required",
        "brand/product/designer/person signal summaries",
    ):
        assert phrase in readme


def test_row_one_docs_describe_stage_289_signal_story_refs() -> None:
    row_one = _normalized(_read(ROW_ONE_DOC))
    readme = _normalized(_read(README))

    for phrase in (
        "signal_synthesis.groups[].signals[].story_refs",
        "app-facing information organization index",
        "compact supporting story references inline",
        "derived from the same briefing topic source story data",
        "not a compliance review feature",
        "does not change collection, matching, ranking, scoring, sorting, or story ids",
    ):
        assert phrase in row_one
        assert phrase in readme


def test_row_one_docs_describe_card_synthesis_and_detail_information_map() -> None:
    row_one = _normalized(_read(ROW_ONE_DOC))
    readme = _normalized(_read(README))

    for phrase in (
        "why_it_matters",
        "signal_context",
        "detail information map",
        "derived from existing row one story data",
        "links only to existing detail-page anchors",
        "does not change collection, matching, scoring, ranking, or story ids",
    ):
        assert phrase in row_one

    for phrase in (
        "why_it_matters",
        "signal_context",
        "detail information map",
    ):
        assert phrase in readme


def test_row_one_docs_describe_stage_282_story_directory() -> None:
    row_one = _normalized(_read(ROW_ONE_DOC))
    readme = _normalized(_read(README))

    for phrase in (
        "story_directory",
        "app-facing route index",
        "derived only from the stories already present in the edition payload",
        "without scraping html",
        "does not collect sources",
        "does not change matching, scoring, sorting, or story ids",
        "does not introduce a separate story discovery layer",
    ):
        assert phrase in row_one

    for phrase in (
        "story_directory",
        "app-facing route index derived only from existing row one stories",
        "without html scraping",
        "does not change collection, matching, scoring, sorting, story ids",
    ):
        assert phrase in readme


def test_row_one_docs_describe_stage_275_daily_digest() -> None:
    row_one = _normalized(_read(ROW_ONE_DOC))
    readme = _normalized(_read(README))

    for phrase in (
        "daily_digest",
        "today's briefing",
        "read_first",
        "key_takeaways",
        "signals_to_watch",
        "positive local raw mention deltas",
        "app clients can render a daily briefing",
        "without scraping html",
        "does not add source collection",
        "does not prove demand",
    ):
        assert phrase in row_one

    for phrase in (
        "daily_digest",
        "app clients can render section rails and a daily briefing",
    ):
        assert phrase in readme


def test_row_one_docs_describe_stage_276_briefing_topics() -> None:
    row_one = _normalized(_read(ROW_ONE_DOC))
    readme = _normalized(_read(README))

    for phrase in (
        "daily_digest.briefing_topics",
        "app-ready briefing organization surface",
        "organized topic groups",
        "instead of a flat list of links",
        "topic labels",
        "story_ids",
        "cards",
        "without scraping html",
        "not a link list",
        "does not infer people from sections",
        "does not add source collection",
        "does not prove demand",
        "does not change matching, ranking, scoring, story ids",
    ):
        assert phrase in row_one

    for phrase in (
        "daily_digest.briefing_topics",
        "organized app-ready briefing instead of a flat list of links",
        "does not add source collection",
        "demand proof",
        "platform coverage verification",
    ):
        assert phrase in readme


def test_row_one_docs_describe_stage_277_homepage_briefing_topics() -> None:
    row_one = _normalized(_read(ROW_ONE_DOC))
    readme = _normalized(_read(README))

    for phrase in (
        "homepage briefing topics",
        "renders the first four `daily_digest.briefing_topics`",
        "same app payload written to `data/edition.json`",
        "presentation-only briefing topic index",
        "organized topic groups",
        "topic labels",
        "story_ids",
        "cards",
        "evidence link counts",
        "links to existing detail pages",
        "not a flat link list",
        "does not scrape html",
        "does not infer people from sections or tags",
        "row-one-app/v7 content organization",
        "does not change matching, ranking, scoring, story ids",
        "does not add source collection",
        "does not prove demand",
    ):
        assert phrase in row_one

    for phrase in (
        "row one homepage can render the first four daily_digest.briefing_topics",
        "same data/edition.json payload",
        "organized app-ready briefing instead of a flat list of links",
        "app clients still use data/edition.json without scraping html",
    ):
        assert phrase in readme


def test_row_one_docs_describe_stage_272_editorial_web_experience() -> None:
    row_one = _normalized(_read(ROW_ONE_DOC))
    readme = _normalized(_read(README))

    for phrase in (
        "editorial web experience",
        "professional static website",
        "edition rail",
        "article contents",
        "evidence trail",
        "retained source row",
        "uses existing row-one-app/v7 content organization",
    ):
        assert phrase in row_one

    for phrase in (
        "professional static website",
        "edition rail",
        "article contents",
    ):
        assert phrase in readme


def test_row_one_docs_describe_daily_readiness_preview() -> None:
    normalized = _normalized(_read(ROW_ONE_DOC))

    for phrase in (
        "daily readiness and preview",
        "latest edition status strip",
        "ready",
        "empty",
        "stories",
        "evidence links",
        "empty sections",
        "compact english status labels",
        "bilingual english/chinese labels",
        "`row-one preview`",
        "`row-one preview --dry-run-serve-url`",
        "preview prints the manifest path",
        "`data/manifest.json` output",
        "same local url message used by `row-one serve --dry-run`",
    ):
        assert phrase in normalized


def test_row_one_docs_describe_manifest_and_editorial_polish() -> None:
    row_one_doc = _read(ROW_ONE_DOC)
    readme = _read(ROOT / "README.md")
    first_run = _read(ROOT / "docs" / "first-run.md")
    checklist = _read(ROOT / "docs" / "github-upload-checklist.md")

    for phrase in (
        "`data/manifest.json`",
        "`row-one-manifest/v1`",
        "`schemas/row-one-manifest.schema.json`",
        "app discovery manifest",
        "lead story",
        "SEO/social metadata",
    ):
        assert phrase.lower() in row_one_doc.lower()

    assert "Inspect The Sample In ROW ONE".lower() in first_run.lower()
    assert 'row-one preview --config-dir "$PWD/configs"'.lower() in first_run.lower()
    assert "ROW ONE manifest".lower() in first_run.lower()
    assert "row-one serve --dry-run".lower() in first_run.lower()
    assert (
        "row-one serve --site-dir reports/row-one/site --host 127.0.0.1 --port 8787".lower()
        in first_run.lower()
    )
    assert "row-one status --site-dir reports/row-one/site".lower() in first_run.lower()
    assert "data/runtime.json" in first_run
    assert "127.0.0.1:8787" in first_run
    assert "0.0.0.0:8787" in first_run
    assert "04:00" in first_run
    assert "docs/row-one.md" in readme
    assert "ROW ONE local static site" in readme
    assert "ROW ONE manifest and serve dry-run".lower() in readme.lower()
    assert "data/manifest.json" in checklist
    assert "do not upload generated ROW ONE site artifacts".lower() in checklist.lower()


def test_row_one_cli_docs_list_build_preview_ops_check_serve_and_schedule_commands() -> None:
    normalized = _normalized(_read(CLI_REFERENCE))

    for phrase in (
        "`row-one build`",
        "`row-one preview`",
        "`row-one status`",
        "`row-one local-ops`",
        "`row-one install-local`",
        "`row-one ops-check`",
        "`row-one serve`",
        "`row-one schedule`",
        "`--output-dir`",
        "`--latest-only`",
        "`--site-dir`",
        "`--host`",
        "`--port`",
        "`--dry-run`",
        "`--unit-dir`",
    ):
        assert phrase in normalized


def test_row_one_docs_describe_local_systemd_install() -> None:
    normalized = _normalized(_read(ROW_ONE_DOC))

    for phrase in (
        "`row-one install-local`",
        "`row-one install-local --dry-run`",
        "user-level systemd units",
        "`row-one-refresh.service`",
        "`row-one-refresh.timer`",
        "`row-one-serve.service`",
        "`~/.config/systemd/user`",
        "`--force`",
        "existing unit files are not overwritten unless `--force` is passed",
        "`path` entry for `%h/.local/bin` and `%h/.cargo/bin`",
        "generate the site once before starting the serve unit",
        "systemctl --user daemon-reload",
        "systemctl --user enable --now row-one-refresh.timer",
        "systemctl --user enable --now row-one-serve.service",
        "the generated timer runs the single row one refresh command",
        "the generated serve service keeps the selected `--output-dir` available",
    ):
        assert phrase in normalized


def test_row_one_docs_describe_runtime_status_contract() -> None:
    row_one = _normalized(_read(ROW_ONE_DOC))
    cli = _normalized(_read(CLI_REFERENCE))
    first_run = _normalized(_read(ROOT / "docs" / "first-run.md"))

    for normalized in (row_one, cli, first_run):
        for phrase in (
            "`data/runtime.json`",
            "runtime status",
            "`row-one status`",
            "`data/edition.json`",
            "`data/manifest.json`",
            "04:00",
            "127.0.0.1:8787",
            "0.0.0.0:8787",
            "without rebuilding",
        ):
            assert phrase in normalized

    for phrase in (
        "row-one-runtime/v1",
        "fixed local serve port `8787`",
        "operator preflight checks",
        "`row-one status --json`",
        "`counts`",
        "`readiness`",
        "`refresh_time`",
        "`local_url`",
        "`lan_url_hint`",
        "`index_path`",
        "`edition_path`",
        "`site`",
        "`serve`",
        "`contracts`",
        "`refresh`",
        "additive cli projection",
        "local operational metadata only",
        "lightweight runtime contract check",
        "generated timestamps, counts, and readiness fields must agree",
    ):
        assert phrase in row_one

    for normalized in (row_one, cli, first_run):
        assert "not deep schema validation" not in normalized
        assert "does not validate cross-file agreement" not in normalized
        assert "read/parse check" not in normalized


def test_row_one_docs_describe_stage_308_site_integrity_preflight() -> None:
    docs = {
        "README.md": _normalized(_read(README)),
        "docs/row-one.md": _normalized(_read(ROW_ONE_DOC)),
        "docs/cli-reference.md": _normalized(_read(CLI_REFERENCE)),
    }

    for normalized in docs.values():
        for phrase in (
            "`row-one status --json`",
            "script-facing preflight surface",
            "stage 308 site integrity/preflight",
            "validates an already generated row one site before serving",
            "read-only",
            "does not rebuild",
            "write files",
            "start a server",
            "collect sources",
            "call external services",
            "deploy",
            "alter ranking/scoring/story ids",
            "validates `.row-one-site`",
            "`index.html`",
            "fixed json paths",
            "core assets",
            "current detail routes",
            "local image asset existence",
            "article sidecars",
            "local-intelligence detail paths",
            "paragraph anchors",
            "no schema/app contract change",
            "cli output only",
            "`data/edition.json` remains `row-one-app/v7`",
            "`data/manifest.json` remains `row-one-manifest/v1`",
            "`data/runtime.json` remains `row-one-runtime/v1`",
            "first-run smoke now performs a local http serve fetch",
            "not just `serve --dry-run`",
        ):
            assert phrase in normalized


def test_row_one_docs_reject_stage_308_schema_contract_drift() -> None:
    docs_text = "\n".join(
        _normalized(_read(path))
        for path in (
            README,
            ROW_ONE_DOC,
            CLI_REFERENCE,
            FIRST_RUN_DOC,
        )
        if path.exists()
    )

    for forbidden in (
        "row-one-app/v8",
        "row-one-manifest/v2",
        "row-one-runtime/v2",
        "introduces a new app contract",
        "introduces a new schema contract",
        "adds a top-level integrity field to data/edition.json",
        "schema migration",
        "writes data/status.json",
        "status starts the server",
        "status rebuilds the site",
        "status collects sources",
        "status deploys",
    ):
        assert forbidden not in docs_text


def test_row_one_scheduling_docs_describe_single_refresh_command() -> None:
    normalized = _normalized(_section(_read(SCHEDULING_DOC), "ROW ONE Daily Site"))

    for phrase in (
        "`row-one schedule`",
        "single local daily refresh command",
        "`fashion-radar row-one refresh`",
        "row one scheduled refresh runs the single refresh command.",
        "uv run fashion-radar row-one schedule",
        '--output-dir "$pwd/reports/row-one/site"',
    ):
        assert phrase in normalized

    for old_phrase in (
        "two-step refresh",
        "`fashion-radar run`",
        "`fashion-radar row-one build --latest-only`",
    ):
        assert old_phrase not in normalized


def test_row_one_docs_describe_local_ops_source_checkout_commands() -> None:
    row_one = _normalized(_read(ROW_ONE_DOC))
    readme = _normalized(_read(README))

    for phrase in (
        "source checkout commands",
        "`uv run fashion-radar row-one refresh`",
        "`uv run fashion-radar row-one preview`",
        "`uv run fashion-radar row-one status --site-dir reports/row-one/site --json`",
        "`uv run fashion-radar row-one serve`",
        "`row-one status --json` preflight",
        "copyable source-checkout command group",
        'as_of="$(date -u +%y-%m-%dt%h:%m:%sz)"',
        "cd /path/to/fashion-radar",
        "--config-dir configs --data-dir data --reports-dir reports",
        '--output-dir reports/row-one/site --as-of "$as_of"',
        "--host 0.0.0.0 --port 8787 --dry-run-serve-url",
        "does not install timers, build the site, start the server, or mutate files",
    ):
        assert phrase in row_one

    for phrase in (
        "uv run fashion-radar row-one preview",
        "uv run fashion-radar row-one status --site-dir reports/row-one/site --json",
        "uv run fashion-radar row-one serve",
        "`row-one status --json` preflight",
        "source-checkout command group",
    ):
        assert phrase in readme


def test_row_one_docs_describe_stage_281_homepage_briefing_path() -> None:
    row_one = _normalized(_read(ROW_ONE_DOC))
    readme = _normalized(_read(README))

    for phrase in (
        "homepage briefing path",
        "renders a compact briefing path from `daily_digest.blocks`",
        "`key_takeaways`",
        "`signals_to_watch`",
        "does not duplicate `read_first`",
        "links only to existing detail pages",
        "does not add source collection",
        "does not change matching, ranking, scoring, or story ids",
    ):
        assert phrase in row_one

    for phrase in (
        "homepage briefing path",
        "reuses `daily_digest.blocks`",
        "not a new data layer",
        "links to existing detail pages",
    ):
        assert phrase in readme


def test_row_one_upload_checklist_covers_subcommand_help() -> None:
    normalized = _normalized(_read(UPLOAD_CHECKLIST))

    for phrase in (
        "row-one build --help",
        "row-one refresh --help",
        "row-one preview --help",
        "row-one status --help",
        "row-one local-ops --help",
        "row-one install-local --help",
        "row-one serve --help",
        "row-one schedule --help",
        (
            "row-one build`, `row-one preview`, `row-one local-ops`, `row-one serve`, "
            "and `row-one schedule` subcommand help"
        ),
    ):
        assert phrase in normalized


def test_row_one_readme_and_architecture_are_discoverable_and_bounded() -> None:
    for path in (README, ARCHITECTURE_DOC):
        normalized = _normalized(_read(path))

        for phrase in (
            "row one",
            "local static site",
            "existing daily report data",
            "no new data acquisition",
            "no demand proof",
            "no platform coverage verification",
        ):
            assert phrase in normalized


def test_row_one_docs_describe_daily_local_intelligence() -> None:
    readme = _normalized(_read(README))
    row_one_docs = _normalized(_read(ROW_ONE_DOC))

    assert "daily local intelligence" in readme
    assert "compact content segments" in readme
    assert (
        "homepage daily local intelligence cards include local saved-text and paragraph "
        "drilldown links" in readme
    )
    assert "generated detail pages link content-section paragraph badges" in readme
    assert "anchored saved local paragraphs" in readme
    assert "when the referenced paragraph is available" in readme
    assert "reference cards can include saved-source paragraph excerpts" in readme
    assert "local article map" in readme
    assert "source-backed signal paragraphs" in readme
    assert "data/local-intelligence.json" in readme
    assert "row-one-app/v7 remains stable" in readme
    assert "source-backed reference excerpts" in row_one_docs
    assert "explicit brand, designer, person, bag, shoe, or product matches" in row_one_docs
    assert "paragraph target highlight" in row_one_docs


def test_row_one_docs_describe_newsroom_digest_polish_boundary() -> None:
    row_one = _normalized(_read(ROW_ONE_DOC))
    readme = _normalized(_read(README))

    for phrase in (
        "newsroom digest polish",
        "clusters duplicate saved local-article cards",
        "`data/local-intelligence.json`",
        "`strongest_reads`",
        "`heat_movers`",
        "evidence paragraph links",
        "local article provenance",
        "presentation and sidecar organization only",
        "does not change `row-one-app/v7`",
        "does not change `data/edition.json`",
        "does not change `row-one-manifest/v1`",
        "does not change `row-one-runtime/v1`",
        "does not add source collection",
        "does not add scoring",
    ):
        assert phrase in row_one

    for phrase in (
        "newsroom digest polish",
        "local article provenance",
        "does not change `row-one-app/v7`",
        "does not change `data/edition.json`",
        "does not change `row-one-manifest/v1`",
        "does not change `row-one-runtime/v1`",
        "does not change detail routes",
        "does not change paragraph anchors",
        "does not change schemas",
    ):
        assert phrase in readme

    for forbidden in (
        "row-one-app/v8",
        "adds local_intelligence to `data/edition.json`",
        "changes story ids",
        "changes detail routes",
        "changes paragraph anchors",
        "row-one status rebuilds",
        "row-one status collects",
        "row-one status fetches",
    ):
        assert forbidden not in row_one

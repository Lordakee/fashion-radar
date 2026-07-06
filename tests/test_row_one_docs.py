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


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


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
        "`assets/row-one.css`",
        "`assets/row-one.js`",
        "`data/edition.json`",
        "`.row-one-site` marker",
        "`data/runtime.json`",
        "`data/local-intelligence.json`",
        "remove only known row one generated children",
        "they do not delete unrelated files in the output directory",
        "row-one refresh",
        "prunes older generated report artifacts",
        "`fashion-radar-yyyy-mm-dd.md`",
        "`fashion-radar-yyyy-mm-dd.json`",
        "`fashion-radar-yyyy-mm-dd.html`",
        "does not prune sqlite data",
        "`fashion-radar-yyyy-mm-dd.eml`",
    ):
        assert phrase in normalized


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
            "Stage 310 adds"
        )
    ]
    docs_stage_316 = docs[
        docs.index("Stage 316 adds local article content organization") : docs.index(
            "Stage 310 adds"
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


def test_row_one_cli_docs_list_build_preview_serve_and_schedule_commands() -> None:
    normalized = _normalized(_read(CLI_REFERENCE))

    for phrase in (
        "`row-one build`",
        "`row-one preview`",
        "`row-one status`",
        "`row-one local-ops`",
        "`row-one install-local`",
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

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
ROW_ONE_DOC = ROOT / "docs" / "row-one.md"
ARCHITECTURE_DOC = ROOT / "docs" / "architecture.md"
CLI_REFERENCE = ROOT / "docs" / "cli-reference.md"
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
        "`--latest-only` removes only known row one generated children",
        "does not delete unrelated files in the output directory",
    ):
        assert phrase in normalized


def test_row_one_docs_include_user_required_phrases() -> None:
    normalized = _normalized(_read(ROW_ONE_DOC))

    for phrase in (
        "row one",
        "row-one build",
        "row-one refresh",
        "row-one preview",
        "row-one local-ops",
        "row-one serve",
        "row-one schedule",
        "04:00 local scheduling",
        "fixed ip:port",
        "latest-only cleanup",
        "ip:port local-network serving",
        "open from lan: http://<lan-ip>:8787",
        "fashion-radar row-one refresh",
        "fashion-radar row-one preview",
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
        "`data/edition.json` is the row-one-app/v1 app-facing contract",
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
        "`row-one local-ops`",
        "`row-one serve`",
        "`row-one schedule`",
        "`--output-dir`",
        "`--latest-only`",
        "`--site-dir`",
        "`--host`",
        "`--port`",
        "`--dry-run`",
    ):
        assert phrase in normalized


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


def test_row_one_upload_checklist_covers_subcommand_help() -> None:
    normalized = _normalized(_read(UPLOAD_CHECKLIST))

    for phrase in (
        "row-one build --help",
        "row-one preview --help",
        "row-one local-ops --help",
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

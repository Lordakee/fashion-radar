from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIRST_RUN_DOC = ROOT / "docs" / "first-run.md"
STAGE_391_MUTATION_FREE_CAVEAT = (
    "the mutation-free promise covers only the publisher-owned row one site output parent "
    "and publisher transaction artifacts. `row-one refresh` may already have collected, "
    "matched, and stored data and written the current dated report before site publication "
    "reaches the capability gate. the gate does not skip or roll back that completed source, "
    "sqlite, and report work."
)
STAGE_391_UNSUPPORTED_PLATFORM_CAVEAT = (
    "unsupported platforms fail before creating output or transaction artifacts. "
    + STAGE_391_MUTATION_FREE_CAVEAT
)


def _read_first_run_doc() -> str:
    return FIRST_RUN_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    assert marker in text
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def test_first_run_docs_keep_local_sample_boundary() -> None:
    boundary = _section(_read_first_run_doc(), "Boundary")
    normalized = _normalized(boundary)

    for phrase in (
        "first-run sample does not run live collection",
        "automated smoke does not run `collect`, `run`, or `dashboard`",
        "should not create files under repo `data/` or `reports/`",
        "does not perform browser automation, account login, cookies/sessions",
        "source/platform connectors, scraping, platform automation, monitoring",
        "scheduling, or external services",
        "candidate and trend outputs are local sample content checks from the checked-in example",
        "not proof of demand",
        "not platform coverage",
        "not source ranking",
    ):
        assert phrase in normalized


def test_first_run_docs_name_external_tool_smoke_contracts() -> None:
    installed_smoke = _section(_read_first_run_doc(), "Installed-Wheel Smoke")
    normalized = _normalized(installed_smoke)

    for phrase in (
        "automated first-run smoke also validates local external-tool json contracts",
        "`external-tool-adapters --format json` across all eight adapters",
        "`external-tool-template --adapter rednote_mcp --format json`",
        "`external-tool-workflow --adapter rednote_mcp --format json`",
        "`external-tool-readiness --adapter rednote_mcp --format json`",
        "do not run adapters or upstream external/community tools",
        "do not call platform apis",
        "do not perform source acquisition",
    ):
        assert phrase in normalized


def test_first_run_docs_describe_row_one_article_readiness_boundary() -> None:
    normalized = _normalized(_read_first_run_doc())

    for phrase in (
        "row-one article-readiness",
        "deterministic first-run smoke",
        "does not require saved article sidecars",
        "row_one_article.enabled: true",
        "optional article extraction dependency",
    ):
        assert phrase in normalized


def test_first_run_docs_describe_temporary_http_smoke() -> None:
    smoke = _section(_read_first_run_doc(), "Automated First-Run Smoke")
    normalized = _normalized(smoke)

    for phrase in (
        "it checks row one serve dry-run urls",
        "starts a temporary local http server",
        "fetches through that temporary local http server",
        "terminates the temporary local http server",
    ):
        assert phrase in normalized


def test_first_run_docs_describe_stage_391_recoverable_latest_only_publish() -> None:
    row_one = _section(_read_first_run_doc(), "Inspect The Sample In ROW ONE")
    normalized = _normalized(row_one)

    for phrase in (
        "row-one refresh",
        "row-one preview",
        "--latest-only",
        "failure-safe recoverable publish",
        "renders and validates a same-filesystem staging site before changing the live output",
        "recoverable latest-only publication requires safe directory-relative filesystem "
        "operations",
        "current standard windows python lacks the safe directory-handle capability for "
        "recoverable latest-only",
        "unsupported platforms fail before creating output or transaction artifacts",
        "`row one safe directory handles are unsupported on this platform`",
        "before creating the output parent, lock, journal, stage, backup, or owner marker",
        "before invoking render",
        "never falls back to delete-and-render",
        "feature-level boundary",
        "package remains os-independent",
        "ordinary non-latest build and preview rendering remains available",
        "`row-one refresh` is latest-only and therefore fails at this gate on unsupported "
        "platforms",
        "restores the previous output after a handled publish failure",
        "recovers an interrupted owned transaction before the next latest-only render",
        "the stable sibling lock file may remain after a successful refresh",
        "short live-path gap",
        "not fully atomic",
        "does not claim zero-downtime publication or power-loss durability",
    ):
        assert phrase in normalized

    assert (
        normalized.count("does not claim zero-downtime publication or power-loss durability") == 1
    )
    assert STAGE_391_UNSUPPORTED_PLATFORM_CAVEAT in normalized
    assert STAGE_391_MUTATION_FREE_CAVEAT in normalized
    assert normalized.count(STAGE_391_MUTATION_FREE_CAVEAT) == 1
    for redundant_phrase in (
        "does not promise zero downtime",
        "does not guarantee universal power-loss durability",
    ):
        assert redundant_phrase not in normalized


def test_first_run_reset_describes_managed_child_replacement_after_staged_validation() -> None:
    reset = _normalized(_section(_read_first_run_doc(), "Reset The Repo-Local Sample"))

    assert "replaces only managed generated children after staged validation" in reset
    assert "preserves unrelated top-level output children" in reset
    assert "latest-only site cleanup removes generated site output" not in reset

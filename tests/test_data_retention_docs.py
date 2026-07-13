from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_RETENTION_DOC = ROOT / "docs" / "data-retention.md"
README = ROOT / "README.md"
ROW_ONE_DOC = ROOT / "docs" / "row-one.md"
FIRST_RUN_DOC = ROOT / "docs" / "first-run.md"
CLI_REFERENCE = ROOT / "docs" / "cli-reference.md"


def _read_data_retention_doc() -> str:
    return DATA_RETENTION_DOC.read_text(encoding="utf-8")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def test_data_retention_docs_pin_cleanup_boundaries() -> None:
    text = _read_data_retention_doc()

    for phrase in (
        "Use `clean-old-data` to prune old collected items",
        "as_of - retention_days",
        "Rows in `items` with `collected_at` older than that cutoff are pruned.",
        "explicitly deletes related `item_entities` rows before deleting",
        "does not rely on SQLite foreign-key cascade behavior",
        "`--dry-run` reports how many item and item/entity rows would be deleted without",
        "The cleanup command does not prune:",
        "`collector_runs`",
        "`source_health`",
        "`entity_first_seen`",
        "generated Markdown, JSON, or HTML report files",
        "config files",
        "`entity_first_seen` is intentionally retained across item pruning",
        "Back up the SQLite database before aggressive cleanup",
    ):
        assert phrase in text


def test_data_retention_docs_describe_row_one_refresh_retention() -> None:
    text = _normalized(_read_data_retention_doc())

    for phrase in (
        "`clean-old-data` remains the standalone/manual cleanup command",
        "`row-one refresh` runs the same sqlite cleanup semantics",
        "default 1-day sqlite item retention",
        "after the current row one site and reports are generated",
        "`--retention-days`",
        "`--skip-data-retention`",
        "1-day retention is disk-friendly",
        "reduces multi-day item history",
        "scoring-window and heat-score comparisons",
        "does not prune `collector_runs`",
        "does not prune `source_health`",
        "does not prune `entity_first_seen`",
        "does not prune config files",
        "does not prune generated row one site files",
        "report artifact pruning remains separate",
    ):
        assert phrase in text


def test_docs_no_longer_say_row_one_leaves_sqlite_retention_to_clean_old_data() -> None:
    docs = "\n".join(
        _normalized(_read(path))
        for path in (README, ROW_ONE_DOC, FIRST_RUN_DOC, DATA_RETENTION_DOC, CLI_REFERENCE)
    )

    for stale_phrase in (
        "leaving sqlite/data retention to `clean-old-data`",
        "leaves sqlite retention entirely to `clean-old-data`",
        "leaves sqlite/data retention to `clean-old-data`",
    ):
        assert stale_phrase not in docs


def test_data_retention_docs_describe_post_artifact_refresh_failure() -> None:
    docs = {
        "README": _normalized(_read(README)),
        "ROW ONE": _normalized(_read(ROW_ONE_DOC)),
        "first-run": _normalized(_read(FIRST_RUN_DOC)),
        "CLI reference": _normalized(_read(CLI_REFERENCE)),
        "data retention": _normalized(_read(DATA_RETENTION_DOC)),
    }

    for name, text in docs.items():
        assert (
            "non-skipped sqlite retention failure returns a nonzero exit status after report "
            "and site output is written"
        ) in text, name

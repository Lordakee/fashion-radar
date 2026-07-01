from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_RETENTION_DOC = ROOT / "docs" / "data-retention.md"


def _read_data_retention_doc() -> str:
    return DATA_RETENTION_DOC.read_text(encoding="utf-8")


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

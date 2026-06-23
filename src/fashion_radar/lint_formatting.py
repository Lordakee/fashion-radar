from __future__ import annotations


def format_count_label(count: int, singular: str, plural: str) -> str:
    label = singular if count == 1 else plural
    return f"{count} {label}"


def format_finding_counts(error_count: int, warning_count: int, info_count: int) -> str:
    return (
        f"{format_count_label(error_count, 'error', 'errors')}, "
        f"{format_count_label(warning_count, 'warning', 'warnings')}, "
        f"{format_count_label(info_count, 'info', 'info')}"
    )

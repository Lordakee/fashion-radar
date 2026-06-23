import pytest

from fashion_radar.lint_formatting import format_count_label, format_finding_counts


@pytest.mark.parametrize(
    ("count", "expected"),
    [
        (0, "0 errors"),
        (1, "1 error"),
        (2, "2 errors"),
    ],
)
def test_format_count_label_uses_singular_only_for_one(count: int, expected: str) -> None:
    assert format_count_label(count, "error", "errors") == expected


def test_format_finding_counts_formats_zero_counts() -> None:
    assert format_finding_counts(0, 0, 0) == "0 errors, 0 warnings, 0 info"


def test_format_finding_counts_formats_singular_counts() -> None:
    assert format_finding_counts(1, 1, 1) == "1 error, 1 warning, 1 info"


def test_format_finding_counts_formats_plural_counts() -> None:
    assert format_finding_counts(2, 2, 2) == "2 errors, 2 warnings, 2 info"


def test_format_finding_counts_formats_mixed_counts() -> None:
    assert format_finding_counts(1, 0, 2) == "1 error, 0 warnings, 2 info"

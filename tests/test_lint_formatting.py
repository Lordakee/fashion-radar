import pytest

from fashion_radar.lint_formatting import format_count_label, format_finding_counts


@pytest.mark.parametrize(
    ("count", "singular", "plural", "expected"),
    [
        (0, "error", "errors", "0 errors"),
        (1, "error", "errors", "1 error"),
        (2, "error", "errors", "2 errors"),
        (1, "import-ready row", "import-ready rows", "1 import-ready row"),
        (2, "import-ready row", "import-ready rows", "2 import-ready rows"),
        (0, "valid file", "valid files", "0 valid files"),
        (2, "info", "info", "2 info"),
        (2, "analysis", "analyses", "2 analyses"),
    ],
)
def test_format_count_label_uses_supplied_label_for_count(
    count: int,
    singular: str,
    plural: str,
    expected: str,
) -> None:
    assert format_count_label(count, singular, plural) == expected


def test_format_finding_counts_formats_zero_counts() -> None:
    assert format_finding_counts(0, 0, 0) == "0 errors, 0 warnings, 0 info"


def test_format_finding_counts_formats_singular_counts() -> None:
    assert format_finding_counts(1, 1, 1) == "1 error, 1 warning, 1 info"


def test_format_finding_counts_formats_plural_counts() -> None:
    assert format_finding_counts(2, 2, 2) == "2 errors, 2 warnings, 2 info"


def test_format_finding_counts_formats_mixed_counts() -> None:
    assert format_finding_counts(1, 0, 2) == "1 error, 0 warnings, 2 info"

from fashion_radar.extract.text import alias_pattern, normalize_text


def test_normalize_text_case_and_spacing() -> None:
    assert normalize_text("  The   Row\nMargaux  ") == "the row margaux"


def test_alias_pattern_uses_word_boundaries() -> None:
    pattern = alias_pattern("row")

    assert pattern.search("front row seat")
    assert not pattern.search("rowing club")


def test_alias_pattern_handles_multi_word_alias() -> None:
    pattern = alias_pattern("The Row")

    assert pattern.search("Bella wore The Row Margaux.")
    assert not pattern.search("They stood in the row after the show.")

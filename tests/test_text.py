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
    assert pattern.search("Bella wore the\nrow Margaux.")
    assert not pattern.search("They saw Therewith on the runway.")


def test_alias_pattern_handles_category_phrase() -> None:
    pattern = alias_pattern("ballet flats")

    assert pattern.search("She wore Ballet Flats with socks.")
    assert pattern.search("She wore ballet\nflats with socks.")
    assert not pattern.search("The flats were ballet-inspired.")

from fashion_radar.extract.text import alias_pattern, normalize_text


def test_normalize_text_case_and_spacing() -> None:
    assert normalize_text("  The   Row\nMargaux  ") == "the row margaux"


def test_normalize_text_folds_latin_diacritics() -> None:
    assert normalize_text("Hermès Chloé Sézane Alaïa") == "hermes chloe sezane alaia"


def test_alias_pattern_uses_word_boundaries() -> None:
    pattern = alias_pattern("row")

    assert pattern.search("front row seat")
    assert not pattern.search("rowing club")


def test_alias_pattern_handles_multi_word_alias() -> None:
    pattern = alias_pattern("The Row")

    assert pattern.search("Bella wore The Row Margaux.")
    assert pattern.search("Bella wore the\nrow Margaux.")
    assert not pattern.search("They saw Therewith on the runway.")


def test_alias_pattern_matches_latin_diacritic_variants() -> None:
    hermes_pattern = alias_pattern("Hermes")
    chloe_pattern = alias_pattern("Chloé")
    edith_pattern = alias_pattern("Édith")

    assert hermes_pattern.search("Hermès Birkin bag")
    assert hermes_pattern.search("Hermes Birkin bag")
    assert chloe_pattern.search("Chloe runway bag")
    assert chloe_pattern.search("Chloé runway bag")
    assert edith_pattern.search("Edith Head costume archive")
    assert edith_pattern.search("ÉDITH Head costume archive")


def test_alias_pattern_handles_category_phrase() -> None:
    pattern = alias_pattern("ballet flats")

    assert pattern.search("She wore Ballet Flats with socks.")
    assert pattern.search("She wore ballet\nflats with socks.")
    assert not pattern.search("The flats were ballet-inspired.")

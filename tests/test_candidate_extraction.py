from fashion_radar.discovery.candidates import extract_candidate_phrases
from fashion_radar.settings import CandidateDiscoverySettings


def _keys(phrases):
    return {phrase.normalized_key for phrase in phrases}


def test_extracts_proper_name_and_product_phrases() -> None:
    phrases = extract_candidate_phrases(
        "Sandy Liang Mary Jane flats and Le Teckel bag searches rise.",
        source_name="Fashionista",
        known_keys=set(),
    )

    assert "sandy liang" in _keys(phrases)
    assert "mary jane flats" in _keys(phrases)
    assert "le teckel bag" in _keys(phrases)


def test_filters_known_entities_source_terms_and_generic_phrases() -> None:
    phrases = extract_candidate_phrases(
        "Fashionista reports The Row Margaux bag during Paris Fashion Week.",
        source_name="Fashionista",
        known_keys={"the row", "margaux", "paris fashion week"},
    )

    keys = _keys(phrases)
    assert "fashionista" not in keys
    assert "the row" not in keys
    assert "margaux" not in keys
    assert "paris fashion week" not in keys
    assert "the row margaux bag" not in keys
    assert "margaux bag" not in keys


def test_respects_max_phrase_words_and_chars() -> None:
    settings = CandidateDiscoverySettings(max_phrase_words=3, max_phrase_chars=24)
    phrases = extract_candidate_phrases(
        "The Very Long Designer Product Name handbag gains attention.",
        source_name="WWD",
        known_keys=set(),
        settings=settings,
    )

    assert all(len(phrase.phrase.split()) <= 3 for phrase in phrases)
    assert all(len(phrase.phrase) <= 24 for phrase in phrases)


def test_prefers_specific_spans_over_noisy_overlap() -> None:
    phrases = extract_candidate_phrases(
        "Sandy Liang Mary Jane flats and Le Teckel bag searches rise.",
        source_name="Fashionista",
        known_keys=set(),
    )

    keys = _keys(phrases)
    assert "sandy liang" in keys
    assert "mary jane flats" in keys
    assert "le teckel bag" in keys
    assert "sandy liang mary jane flats" not in keys


def test_known_entity_span_filter_handles_possessives_hyphens_and_ampersands() -> None:
    phrases = extract_candidate_phrases(
        (
            "The Row's Margaux bag and Tory Burch-Pierced mule appeared with "
            "Proenza Schouler & Birkenstock sandals."
        ),
        source_name="Fashionista",
        known_keys={
            "the row",
            "margaux",
            "tory burch",
            "proenza schouler birkenstock",
        },
    )

    keys = _keys(phrases)
    assert "the row margaux bag" not in keys
    assert "margaux bag" not in keys
    assert "tory burch pierced mule" not in keys
    assert "proenza schouler birkenstock sandals" not in keys


def test_single_token_phrases_can_be_extracted_for_later_aggregate_filtering() -> None:
    settings = CandidateDiscoverySettings(min_single_token_mentions=2)
    phrases = extract_candidate_phrases(
        "Tabis returned to the street-style cycle.",
        source_name="Fashionista",
        known_keys=set(),
        settings=settings,
    )

    assert "tabis" in _keys(phrases)

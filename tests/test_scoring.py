from yt_research_core.scoring import calc_engagement_score, is_relevant


def test_engagement_score_basic():
    assert calc_engagement_score(50000, 10000) == 5.0


def test_engagement_score_zero_subscribers():
    assert calc_engagement_score(100000, 0) == 0.0


def test_engagement_score_rounds_to_3():
    assert calc_engagement_score(10, 3) == 3.333


def test_is_relevant_matches_keyword():
    assert is_relevant("ボカロ新曲", "初音ミク", ["vocaloid", "ボカロ"]) is True


def test_is_relevant_case_insensitive():
    assert is_relevant("New VOCALOID song", "", ["vocaloid"]) is True


def test_is_relevant_no_match():
    assert is_relevant("NBA highlights", "basketball", ["ボカロ", "vocaloid"]) is False

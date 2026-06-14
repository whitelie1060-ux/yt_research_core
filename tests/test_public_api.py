import yt_research_core as y


def test_version_exposed():
    assert y.__version__ == "0.1.0"


def test_public_symbols_importable():
    for name in [
        "fetch_trending", "search_videos", "fetch_video_stats", "fetch_channel_stats_batch",
        "calc_engagement_score", "is_relevant",
        "load_json", "save_json", "add_to_history", "load_dotenv", "existing_video_ids",
        "setup_logger", "TrendingConfig", "SearchConfig",
        "collect_trending", "collect_search",
    ]:
        assert hasattr(y, name), f"missing public symbol: {name}"

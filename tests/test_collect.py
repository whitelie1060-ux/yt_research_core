from unittest.mock import patch
from yt_research_core.config import TrendingConfig, SearchConfig
from yt_research_core.collect import collect_trending, collect_search
from yt_research_core.io import load_json


def _trending_item(vid, title, ch, views):
    return {
        "id": vid,
        "snippet": {"title": title, "description": "", "channelId": ch,
                    "channelTitle": "CH", "publishedAt": "2026-01-01T00:00:00Z"},
        "statistics": {"viewCount": str(views)},
    }


def test_collect_trending_filters_scores_and_saves(tmp_path):
    cfg = TrendingConfig(api_key="K", categories=["10"], keywords=["ボカロ"],
                         data_dir=tmp_path, region="JP")
    items = [
        _trending_item("v1", "ボカロ新曲", "CH_A", 100000),     # 関連あり
        _trending_item("v2", "NBA highlights", "CH_B", 999999),  # 関連なし→除外
    ]
    with patch("yt_research_core.collect.fetch_trending", return_value=items), \
         patch("yt_research_core.collect.fetch_channel_stats_batch",
               return_value={"CH_A": {"subscriberCount": "10000"}}), \
         patch("yt_research_core.collect.time.sleep", return_value=None):
        result = collect_trending(cfg)

    saved = load_json(str(next(tmp_path.glob("trending_*.json"))))
    assert result["success"] == 1
    assert len(saved) == 1
    v = saved[0]
    assert v["video_id"] == "v1"
    assert v["subscriber_count"] == 10000
    assert v["engagement_score"] == 10.0   # 100000 / 10000
    assert v["source"] == "trending"
    assert v["processed"] is False


def test_collect_trending_skips_existing(tmp_path):
    (tmp_path / "trending_20260101.json").write_text(
        '[{"video_id": "v1"}]', encoding="utf-8")
    cfg = TrendingConfig(api_key="K", categories=["10"], keywords=["ボカロ"], data_dir=tmp_path)
    items = [_trending_item("v1", "ボカロ新曲", "CH_A", 100000)]
    with patch("yt_research_core.collect.fetch_trending", return_value=items), \
         patch("yt_research_core.collect.fetch_channel_stats_batch", return_value={}), \
         patch("yt_research_core.collect.time.sleep", return_value=None):
        result = collect_trending(cfg)
    assert result["success"] == 0


def test_collect_search_filters_by_min_views_and_saves(tmp_path):
    cfg = SearchConfig(api_key="K", queries=["ボカロ"], min_views=10000, data_dir=tmp_path)
    search_items = [{"id": {"videoId": "v1"}}, {"id": {"videoId": "v2"}}]
    stats_map = {
        "v1": {"snippet": {"title": "曲A", "channelId": "CH_A", "channelTitle": "CH",
                           "publishedAt": "2026-01-01T00:00:00Z"},
               "statistics": {"viewCount": "50000"}},
        "v2": {"snippet": {"title": "曲B", "channelId": "CH_B", "channelTitle": "CH",
                           "publishedAt": "2026-01-01T00:00:00Z"},
               "statistics": {"viewCount": "500"}},  # MIN_VIEWS未満→除外
    }
    with patch("yt_research_core.collect.search_videos", return_value=search_items), \
         patch("yt_research_core.collect.fetch_video_stats", return_value=stats_map), \
         patch("yt_research_core.collect.fetch_channel_stats_batch",
               return_value={"CH_A": {"subscriberCount": "5000"}}), \
         patch("yt_research_core.collect.time.sleep", return_value=None):
        result = collect_search(cfg)

    saved = load_json(str(next(tmp_path.glob("search_*.json"))))
    assert result["collected"] == 1
    assert [v["video_id"] for v in saved] == ["v1"]
    assert saved[0]["engagement_score"] == 10.0  # 50000 / 5000
    assert saved[0]["search_query"] == "ボカロ"
    assert saved[0]["source"] == "search"

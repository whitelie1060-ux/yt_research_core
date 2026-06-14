from unittest.mock import patch, MagicMock
import requests
from yt_research_core.youtube import (
    fetch_trending, fetch_channel_stats_batch, fetch_video_stats,
)


def _resp(json_data, status=200):
    r = MagicMock()
    r.status_code = status
    r.json.return_value = json_data
    r.raise_for_status.return_value = None
    return r


def test_fetch_trending_returns_items():
    with patch("yt_research_core.youtube.requests.get",
               return_value=_resp({"items": [{"id": "v1"}]})):
        items = fetch_trending("10", api_key="K")
    assert items == [{"id": "v1"}]


def test_fetch_trending_quota_exceeded_returns_empty():
    with patch("yt_research_core.youtube.requests.get",
               return_value=_resp({}, status=403)):
        items = fetch_trending("10", api_key="K")
    assert items == []


def test_batch_channel_stats_maps_correctly():
    resp = _resp({"items": [
        {"id": "CH_A", "statistics": {"subscriberCount": "10000"}},
        {"id": "CH_B", "statistics": {"subscriberCount": "50000"}},
    ]})
    with patch("yt_research_core.youtube.requests.get", return_value=resp):
        result = fetch_channel_stats_batch(["CH_A", "CH_B"], api_key="K")
    assert result["CH_A"]["subscriberCount"] == "10000"
    assert result["CH_B"]["subscriberCount"] == "50000"


def test_batch_channel_stats_empty_input():
    assert fetch_channel_stats_batch([], api_key="K") == {}


def test_batch_channel_stats_api_error_returns_empty():
    resp = MagicMock()
    resp.raise_for_status.side_effect = requests.exceptions.RequestException("Quota")
    with patch("yt_research_core.youtube.requests.get", return_value=resp):
        assert fetch_channel_stats_batch(["CH_A"], api_key="K") == {}


def test_fetch_video_stats_maps_by_id():
    resp = _resp({"items": [{"id": "v1", "snippet": {}, "statistics": {}}]})
    with patch("yt_research_core.youtube.requests.get", return_value=resp):
        out = fetch_video_stats(["v1"], api_key="K")
    assert "v1" in out


def test_fetch_video_stats_empty_input():
    assert fetch_video_stats([], api_key="K") == {}

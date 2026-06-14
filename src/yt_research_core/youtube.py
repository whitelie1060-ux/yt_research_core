"""YouTube Data API v3 クライアント（ブランド非依存・api_keyは引数で受ける）。"""
import requests

API_BASE = "https://www.googleapis.com/youtube/v3"
DEFAULT_TIMEOUT = 10


def fetch_trending(category_id, *, api_key, region="JP", max_results=50, logger=None) -> list[dict]:
    """急上昇動画を取得。quota超過(403)時は空リストを返して安全に終了。"""
    params = {
        "part": "snippet,statistics,contentDetails",
        "chart": "mostPopular",
        "regionCode": region,
        "videoCategoryId": category_id,
        "maxResults": max_results,
        "key": api_key,
    }
    r = requests.get(f"{API_BASE}/videos", params=params, timeout=DEFAULT_TIMEOUT)
    if r.status_code == 403:
        if logger:
            logger.warning("YouTube API quota超過。処理を中断します。")
        return []
    r.raise_for_status()
    return r.json().get("items", [])


def search_videos(query, *, api_key, published_after, region="JP",
                  max_results=20, order="viewCount") -> list[dict]:
    """キーワードで動画を検索（search.list）。items（id.videoId含む）を返す。"""
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "regionCode": region,
        "relevanceLanguage": "ja",
        "publishedAfter": published_after,
        "maxResults": max_results,
        "order": order,
        "key": api_key,
    }
    r = requests.get(f"{API_BASE}/search", params=params, timeout=DEFAULT_TIMEOUT)
    r.raise_for_status()
    return r.json().get("items", [])


def fetch_video_stats(video_ids, *, api_key) -> dict[str, dict]:
    """動画統計+snippetを一括取得し {video_id: item} で返す。"""
    if not video_ids:
        return {}
    params = {
        "part": "statistics,snippet",
        "id": ",".join(video_ids),
        "key": api_key,
    }
    r = requests.get(f"{API_BASE}/videos", params=params, timeout=DEFAULT_TIMEOUT)
    r.raise_for_status()
    return {item["id"]: item for item in r.json().get("items", [])}


def fetch_channel_stats_batch(channel_ids, *, api_key, logger=None) -> dict[str, dict]:
    """複数チャンネルの統計を一括取得（最大50件/リクエスト）。失敗バッチはスキップ。"""
    if not channel_ids:
        return {}
    result: dict[str, dict] = {}
    for i in range(0, len(channel_ids), 50):
        batch = channel_ids[i:i + 50]
        params = {"part": "statistics", "id": ",".join(batch), "key": api_key}
        try:
            r = requests.get(f"{API_BASE}/channels", params=params, timeout=DEFAULT_TIMEOUT)
            r.raise_for_status()
            for item in r.json().get("items", []):
                result[item["id"]] = item.get("statistics", {})
        except requests.exceptions.RequestException as e:
            if logger:
                logger.warning("チャンネル統計バッチ取得失敗: %s", e)
    return result

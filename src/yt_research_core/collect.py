"""設定駆動の高レベル収集ランナー（旧 fetch_*.py の main 相当）。"""
import time
from datetime import datetime, timedelta
from pathlib import Path

from .youtube import (
    fetch_trending, search_videos, fetch_video_stats, fetch_channel_stats_batch,
)
from .scoring import calc_engagement_score, is_relevant
from .io import save_json, existing_video_ids
from .logging import setup_logger


def collect_trending(config) -> dict:
    """急上昇収集 → フィルタ → バッチ統計 → スコア → data_dir/trending_YYYYMMDD.json 保存。"""
    logger = config.logger or setup_logger("yt_research_core.collect_trending")
    data_dir = Path(config.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    output_file = data_dir / f"trending_{today}.json"
    existing = existing_video_ids(data_dir, "trending_*.json")

    all_videos: list[dict] = []
    for cat_id in config.categories:
        items = fetch_trending(cat_id, api_key=config.api_key,
                               region=config.region, logger=logger)
        logger.info("カテゴリ %s: %d 件取得", cat_id, len(items))

        filtered: list[dict] = []
        for item in items:
            video_id = item["id"]
            if video_id in existing:
                continue
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            title = snippet.get("title", "")
            description = snippet.get("description", "")[:500]
            if not is_relevant(title, description, config.keywords):
                continue
            filtered.append({
                "video_id": video_id,
                "title": title,
                "channel_id": snippet.get("channelId", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "published": snippet.get("publishedAt", "")[:10],
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "view_count": int(stats.get("viewCount", 0)),
                "category_id": cat_id,
                "source": "trending",
                "processed": False,
            })

        channel_ids = list({v["channel_id"] for v in filtered if v["channel_id"]})
        channel_stats = fetch_channel_stats_batch(channel_ids, api_key=config.api_key, logger=logger)
        for video in filtered:
            ch = channel_stats.get(video["channel_id"], {})
            subs = int(ch.get("subscriberCount", 0))
            video["subscriber_count"] = subs
            video["engagement_score"] = calc_engagement_score(video["view_count"], subs)

        all_videos.extend(filtered)
        time.sleep(0.5)

    all_videos.sort(key=lambda x: x["engagement_score"], reverse=True)
    save_json(str(output_file), all_videos)
    logger.info("%d 件を保存: %s", len(all_videos), output_file)
    return {"success": len(all_videos), "skipped": len(existing)}


def collect_search(config) -> dict:
    """キーワード検索収集 → MIN_VIEWS絞り込み → バッチ統計 → スコア → search_YYYYMMDD.json 保存。"""
    logger = config.logger or setup_logger("yt_research_core.collect_search")
    data_dir = Path(config.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    output_file = data_dir / f"search_{today}.json"
    existing = existing_video_ids(data_dir, "*.json")
    published_after = (datetime.now() - timedelta(days=config.months_back * 30)).strftime("%Y-%m-%dT00:00:00Z")

    all_videos: list[dict] = []
    seen_ids: set[str] = set()

    for query in config.queries:
        logger.info("検索: 「%s」", query)
        try:
            items = search_videos(query, api_key=config.api_key,
                                  published_after=published_after, region=config.region)
            video_ids = [i["id"]["videoId"] for i in items if i.get("id", {}).get("videoId")]
            if not video_ids:
                continue

            stats_map = fetch_video_stats(video_ids, api_key=config.api_key)
            time.sleep(0.3)

            filtered: list[dict] = []
            for video_id in video_ids:
                if video_id in existing or video_id in seen_ids:
                    continue
                item = stats_map.get(video_id)
                if not item:
                    continue
                stats = item.get("statistics", {})
                view_count = int(stats.get("viewCount", 0))
                if view_count < config.min_views:
                    continue
                filtered.append({
                    "video_id": video_id,
                    "snippet": item.get("snippet", {}),
                    "view_count": view_count,
                })

            ch_ids = list({v["snippet"].get("channelId", "") for v in filtered if v["snippet"].get("channelId")})
            channel_stats = fetch_channel_stats_batch(ch_ids, api_key=config.api_key, logger=logger)

            for v in filtered:
                snippet = v["snippet"]
                channel_id = snippet.get("channelId", "")
                subs = int(channel_stats.get(channel_id, {}).get("subscriberCount", 0))
                all_videos.append({
                    "video_id": v["video_id"],
                    "title": snippet.get("title", ""),
                    "channel_id": channel_id,
                    "channel_title": snippet.get("channelTitle", ""),
                    "published": snippet.get("publishedAt", "")[:10],
                    "url": f"https://www.youtube.com/watch?v={v['video_id']}",
                    "view_count": v["view_count"],
                    "subscriber_count": subs,
                    "engagement_score": calc_engagement_score(v["view_count"], subs),
                    "search_query": query,
                    "source": "search",
                    "processed": False,
                })
                seen_ids.add(v["video_id"])
        except Exception as e:
            logger.warning("エラー (%s): %s", query, e)
            continue
        time.sleep(0.5)

    all_videos.sort(key=lambda x: x["engagement_score"], reverse=True)
    save_json(str(output_file), all_videos)
    logger.info("%d 件を保存: %s", len(all_videos), output_file)
    return {"collected": len(all_videos), "skipped": len(existing)}

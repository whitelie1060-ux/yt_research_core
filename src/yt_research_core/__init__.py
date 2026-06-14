"""yt_research_core — YouTubeリサーチ・パイプライン共通エンジン。"""
from .youtube import (
    fetch_trending, search_videos, fetch_video_stats, fetch_channel_stats_batch,
)
from .scoring import calc_engagement_score, is_relevant
from .io import load_json, save_json, add_to_history, load_dotenv, existing_video_ids
from .logging import setup_logger
from .config import TrendingConfig, SearchConfig
from .collect import collect_trending, collect_search

__version__ = "0.1.0"

__all__ = [
    "fetch_trending", "search_videos", "fetch_video_stats", "fetch_channel_stats_batch",
    "calc_engagement_score", "is_relevant",
    "load_json", "save_json", "add_to_history", "load_dotenv", "existing_video_ids",
    "setup_logger", "TrendingConfig", "SearchConfig",
    "collect_trending", "collect_search",
]

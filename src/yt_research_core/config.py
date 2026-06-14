"""ブランド固有設定を渡すための設定オブジェクト。"""
from dataclasses import dataclass
from logging import Logger
from pathlib import Path
from typing import Optional


@dataclass
class TrendingConfig:
    api_key: str
    categories: list[str]
    keywords: list[str]
    data_dir: Path
    region: str = "JP"
    logger: Optional[Logger] = None


@dataclass
class SearchConfig:
    api_key: str
    queries: list[str]
    min_views: int
    data_dir: Path
    region: str = "JP"
    months_back: int = 3
    logger: Optional[Logger] = None

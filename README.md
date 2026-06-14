# yt-research-core

YouTubeリサーチ・パイプライン共通エンジン。急上昇/検索の取得、チャンネル統計のバッチ取得、
エンゲージメントスコアリング、JSON I/O、ロガーを提供する。ブランド設定・APIキー・出力先は含まない。

## インストール

```bash
pip install "yt-research-core @ git+https://github.com/whitelie1060-ux/yt_research_core.git@v0.1.0"
```

## 使い方

```python
from pathlib import Path
from yt_research_core import collect_trending, TrendingConfig

collect_trending(TrendingConfig(
    api_key="...",
    categories=["10", "24"],
    keywords=["ボカロ", "vocaloid"],
    data_dir=Path("data"),
))
```

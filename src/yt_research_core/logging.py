"""ファイル+コンソールのデュアル出力ロガー（ブランド非依存）。

注: モジュール名は logging.py だが、Python3 は絶対import既定のため
内部の `import logging` は標準ライブラリを指す（本モジュールではない）。
"""
import logging
from datetime import datetime
from pathlib import Path


def setup_logger(name: str, log_dir="logs") -> logging.Logger:
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"pipeline_{datetime.now().strftime('%Y%m%d')}.log"

    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

        fh = logging.FileHandler(log_file)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        logger.addHandler(sh)

    return logger

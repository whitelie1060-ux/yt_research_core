"""JSON I/O・.env読込・既存動画ID収集（ブランド非依存）。"""
import json
import os
from pathlib import Path


def load_json(path: str) -> list | dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: list | dict) -> None:
    """JSONを保存（末尾改行1つ付き）。"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def add_to_history(history_path: str, entry: dict) -> None:
    history = load_json(history_path)
    history.append(entry)
    save_json(history_path, history)


def load_dotenv(env_path) -> None:
    """.env を読み込んで環境変数へ。既存の変数は上書きしない。"""
    env_path = Path(env_path)
    if not env_path.exists():
        return
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def existing_video_ids(data_dir, pattern: str = "*.json") -> set[str]:
    """data_dir 内の pattern に一致するJSON群から video_id を集めた set を返す。
    壊れたJSONは無視する。重複排除（差分更新）用。"""
    ids: set[str] = set()
    for f in Path(data_dir).glob(pattern):
        try:
            for v in json.loads(f.read_text(encoding="utf-8")):
                vid = v.get("video_id", "")
                if vid:
                    ids.add(vid)
        except Exception:
            pass
    return ids

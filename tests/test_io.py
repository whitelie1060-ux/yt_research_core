import json
from yt_research_core.io import (
    load_json, save_json, add_to_history, load_dotenv, existing_video_ids,
)


def test_save_load_roundtrip(tmp_path):
    data = [{"id": 1, "title": "テスト"}, {"id": 2, "title": "test"}]
    p = tmp_path / "d.json"
    save_json(str(p), data)
    assert load_json(str(p)) == data


def test_save_json_trailing_single_newline(tmp_path):
    p = tmp_path / "d.json"
    save_json(str(p), {"k": "v"})
    content = p.read_text(encoding="utf-8")
    assert content.endswith("\n")
    assert not content.endswith("\n\n")


def test_add_to_history_appends(tmp_path):
    p = tmp_path / "h.json"
    save_json(str(p), [{"type": "old"}])
    add_to_history(str(p), {"type": "new"})
    loaded = load_json(str(p))
    assert [e["type"] for e in loaded] == ["old", "new"]


def test_existing_video_ids_collects_from_matching_files(tmp_path):
    save_json(str(tmp_path / "trending_20260101.json"), [{"video_id": "A"}, {"video_id": "B"}])
    save_json(str(tmp_path / "trending_20260102.json"), [{"video_id": "B"}, {"video_id": "C"}])
    save_json(str(tmp_path / "search_20260101.json"), [{"video_id": "Z"}])
    ids = existing_video_ids(tmp_path, "trending_*.json")
    assert ids == {"A", "B", "C"}


def test_existing_video_ids_ignores_broken_json(tmp_path):
    (tmp_path / "trending_bad.json").write_text("{not json", encoding="utf-8")
    save_json(str(tmp_path / "trending_ok.json"), [{"video_id": "A"}])
    assert existing_video_ids(tmp_path, "trending_*.json") == {"A"}


def test_load_dotenv_sets_missing_only(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text('FOO="bar"\n# comment\nBAZ=qux\n', encoding="utf-8")
    monkeypatch.delenv("FOO", raising=False)
    monkeypatch.setenv("BAZ", "already")
    load_dotenv(env)
    import os
    assert os.environ["FOO"] == "bar"
    assert os.environ["BAZ"] == "already"  # 既存は上書きしない

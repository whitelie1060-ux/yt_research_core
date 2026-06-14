"""エンゲージメントスコアリングと関連度判定（ブランド非依存）。"""


def calc_engagement_score(view_count: int, subscriber_count: int) -> float:
    """登録者数に対する再生率スコア。subscriber_count が 0 のとき 0.0 を返す。"""
    if subscriber_count == 0:
        return 0.0
    return round(view_count / subscriber_count, 3)


def is_relevant(title: str, description: str, keywords: list[str]) -> bool:
    """title+description に keywords のいずれかが（大文字小文字を無視して）含まれるか。"""
    text = (title + description).lower()
    return any(kw.lower() in text for kw in keywords)

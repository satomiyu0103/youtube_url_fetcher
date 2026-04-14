import pandas as pd
from pathlib import Path

# COLUMNS はこのファイルが唯一の定義元。fetcher.py はここから import する。
COLUMNS = ["video_id", "title", "url", "description", "upload_date", "channel_name", "fetched_at"]


def load(csv_path: Path) -> pd.DataFrame:
    """履歴CSVを読み込む。ファイルがない・壊れている場合は空のDataFrameを返す。"""
    if not csv_path.exists():
        return pd.DataFrame(columns=COLUMNS)
    try:
        df = pd.read_csv(csv_path, dtype={"video_id": str})
        # カラム構造が壊れている場合は空として扱い、誤った初回判定を防ぐ
        if "video_id" not in df.columns:
            return pd.DataFrame(columns=COLUMNS)
        return df
    except Exception:
        return pd.DataFrame(columns=COLUMNS)


def filter_new(latest: pd.DataFrame, history: pd.DataFrame) -> pd.DataFrame:
    """履歴に存在しない動画だけを返す。"""
    if history.empty:
        return latest
    return latest[~latest["video_id"].isin(history["video_id"])]


def append(new_videos: pd.DataFrame, csv_path: Path) -> None:
    """新規動画を履歴CSVに追記する。既存データとの重複は自動排除する。"""
    if new_videos.empty:
        return
    # 既存データを再確認して二重追記を防ぐ（直接呼び出しや将来の呼び出し元対策）
    existing = load(csv_path)
    safe = new_videos[~new_videos["video_id"].isin(existing["video_id"])]
    if safe.empty:
        return
    header = not csv_path.exists()
    safe.to_csv(csv_path, mode="a", header=header, index=False, encoding="utf-8")

import pandas as pd
from pathlib import Path

COLUMNS = ["video_id", "title", "url", "description", "upload_date", "channel_name", "fetched_at"]


def load(csv_path: Path) -> pd.DataFrame:
    """履歴CSVを読み込む。ファイルがなければ空のDataFrameを返す。"""
    if csv_path.exists():
        return pd.read_csv(csv_path, dtype={"video_id": str})
    return pd.DataFrame(columns=COLUMNS)


def filter_new(latest: pd.DataFrame, history: pd.DataFrame) -> pd.DataFrame:
    """履歴に存在しない動画だけを返す。"""
    if history.empty:
        return latest
    return latest[~latest["video_id"].isin(history["video_id"])]


def append(new_videos: pd.DataFrame, csv_path: Path) -> None:
    """新規動画を履歴CSVに追記する。"""
    if new_videos.empty:
        return
    header = not csv_path.exists()
    new_videos.to_csv(csv_path, mode="a", header=header, index=False, encoding="utf-8")

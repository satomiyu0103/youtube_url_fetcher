import yt_dlp
import pandas as pd
from datetime import datetime

COLUMNS = ["video_id", "title", "url", "description", "upload_date", "channel_name", "fetched_at"]


def fetch(channel_url: str, count: int) -> pd.DataFrame:
    """チャンネルの動画情報を取得する。count=0 で全件取得。"""
    opts = {
        "skip_download": True,
        "extract_flat": False,
        "quiet": True,
        "ignoreerrors": True,
        "http_headers": {"Accept-Language": "ja-JP"},
    }
    if count > 0:
        opts["playlistend"] = count

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)
    except Exception as e:
        print(f"取得失敗: {channel_url} — {e}")
        return pd.DataFrame(columns=COLUMNS)

    rows = []
    for entry in info.get("entries", []):
        if not entry:
            continue
        video_id = entry.get("id", "")
        rows.append({
            "video_id":     video_id,
            "title":        entry.get("title", ""),
            "url":          f"https://www.youtube.com/watch?v={video_id}",
            "description":  entry.get("description", ""),
            "upload_date":  entry.get("upload_date", ""),
            "channel_name": entry.get("channel", ""),
            "fetched_at":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

    return pd.DataFrame(rows, columns=COLUMNS)

import yt_dlp
import pandas as pd
from datetime import datetime


def fetch_latest_videos(channel_url, num_videos):
    """
    指定されたチャンネルから最新動画リストを取得し、DataFrameで返す関数
    """

    # yt-dlpのオプション設定
    ydl_opts = {
        "skip_download": True,  # 動画の実態はダウンロードしない
        "extract_flat": False,  # 動画の中身はダウンロードせず情報だけ取得
        # "playlistend": num_videos,  # 取得件数制限
        "quiet": True,  # ログを静かにする
        "ignoreerrors": True,  # エラーがあっても止まらない
        "http_headers": {
            "Accept-Language": "ja-JP",
        },
        # "sleep_interval": 1,
    }

    if num_videos > 0:
        ydl_opts["playlistend"] = num_videos
    else:
        print("♾️ 全件取得モードで実行します（時間がかかります）...")

    print(f"📡 取得開始: {channel_url}")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)

            if "entries" not in info:
                print(f"⚠️ 動画が見つかりませんでした: {channel_url}")
                return pd.DataFrame()  # 空の表を返す

            video_list = []
            for entry in info["entries"]:
                # entryがNoneの場合(削除された動画など)をスキップ
                if not entry:
                    continue

                # 必要な情報だけを辞書にしてリストに追加
                video_data = {
                    "video_id": entry.get("id"),
                    "title": entry.get("title"),
                    "url": entry.get("url") or entry.get("original_url"),
                    "upload_date": entry.get("upload_date"),  # YYYYMMDD形式
                    "channel_name": entry.get("channel", "Unknown"),
                    "fetched_at": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),  # 取得日時
                }

                # 完全なURLを生成 (https://www.youtube.com/watch?v=...)
                if video_data["video_id"] and "http" not in str(video_data["url"]):
                    video_data["url"] = (
                        f"https://www.youtube.com/watch?v={video_data['video_id']}"
                    )

                video_list.append(video_data)

            # リストをDataFrame（表）に変換
            df = pd.DataFrame(video_list)
            return df

    except Exception as e:
        print(f"❌ 取得エラー: {channel_url}\n{e}")
        return pd.DataFrame()  # エラー時も空の表を返して処理を止めない


# --- 動作テスト用ブロック ---
# このファイルを直接実行したときだけ動くコード
if __name__ == "__main__":
    # テスト用URL
    # test_url = "https://www.youtube.com/@GoogleJapan/videos"
    test_url = "https://www.youtube.com/@RPACommunity/videos"
    print("--- テスト実行 ---")
    df_result = fetch_latest_videos(test_url, 3)
    print(df_result[["title", "upload_date", "video_id"]])

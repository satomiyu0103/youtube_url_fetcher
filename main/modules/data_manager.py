import pandas as pd
import os


def load_history(csv_path):
    """
    過去の履歴CSVを読み込む。ファイルがない場合は空のDataFrameを返す。
    """
    if os.path.exists(csv_path):
        try:
            # IDは文字列として読み込む（0落ち防止）
            return pd.read_csv(csv_path, dtype={"video_id": str})
        except Exception:
            return pd.DataFrame(
                columns=["video_id", "title", "url", "upload_date", "fetched_at"]
            )
    else:
        return pd.DataFrame(
            columns=["video_id", "title", "url", "upload_date", "fetched_at"]
        )


def extract_new_videos(latest_df, history_df):
    """
    最新リスト(latest_df)の中から、履歴(history_df)に存在しない動画IDだけを抽出する
    """
    if latest_df.empty:
        return pd.DataFrame()

    if history_df.empty:
        return latest_df  # 履歴がなければ全て新規

    # video_id が history_df に含まれていない行だけを残す
    # (isin の否定 ~ を使う)
    new_videos = latest_df[~latest_df["video_id"].isin(history_df["video_id"])]

    return new_videos


def save_to_history(new_df, csv_path):
    """
    新規データを履歴CSVに追記保存する
    """
    if new_df.empty:
        return

    # ファイルが存在するか確認（ヘッダーの有無を決めるため）
    file_exists = os.path.exists(csv_path)

    # 追記モード('a')で保存。ヘッダーはファイルが新規の時だけ書き込む
    new_df.to_csv(
        csv_path, mode="a", header=not file_exists, index=False, encoding="utf-8"
    )

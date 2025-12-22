import sys
from pathlib import Path

# モジュールの場所をPythonに教える（同じフォルダ内のmodulesを読み込むため）
sys.path.append(str(Path(__file__).resolve().parent))

# 自作モジュールのインポート
import config
from modules import get_url, data_manager, write_new_list, error_log


def main():
    print("🚀 YouTube動画チェックを開始します...")
    print(f"📁 データ保存先: {config.DATA_DIR}")

    try:
        # 1. 全対象チャンネルから最新動画を取得して結合
        all_latest_videos = []

        for channel_url in config.TARGET_CHANNELS:
            df = get_url.fetch_latest_videos(channel_url, config.FETCH_COUNT)
            if not df.empty:
                all_latest_videos.append(df)

        if not all_latest_videos:
            print("⚠️ 動画情報を取得できませんでした。終了します。")
            return

        # 複数のチャンネルの結果を1つの表にまとめる
        import pandas as pd

        latest_df = pd.concat(all_latest_videos, ignore_index=True)

        # 2. 過去データ(CSV)を読み込む
        history_df = data_manager.load_history(config.CSV_PATH)
        print(f"📚 過去の履歴: {len(history_df)}件")

        # 3. 新規動画のみを抽出（差分チェック）
        new_videos = data_manager.extract_new_videos(latest_df, history_df)

        # 4. 結果の処理
        if not new_videos.empty:
            print(f"✨ 新規動画を {len(new_videos)} 件発見しました！")

            # CSVに追記保存
            data_manager.save_to_history(new_videos, config.CSV_PATH)

            # テキストファイル作成（NotebookLM用）
            write_new_list.create_output(new_videos, config.TXT_PATH)

            print(f"✅ 更新リストを作成しました: {config.TXT_PATH}")
        else:
            print("💤 新しい動画はありませんでした。")
            # 更新がない場合も、その旨をファイルに残すと分かりやすい
            write_new_list.create_output(new_videos, config.TXT_PATH)

    except Exception as e:
        print(f"❌ 予期せぬエラーが発生しました: {e}")
        error_log.record_error(e, config.LOG_PATH)

    print("🏁 処理終了")


if __name__ == "__main__":
    main()

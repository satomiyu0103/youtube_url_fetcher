import sys
import logging
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

import config
from modules import fetcher, history, output

logging.basicConfig(
    filename=config.LOG_PATH,
    level=logging.ERROR,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def process_channel(name: str, url: str) -> None:
    csv_path = config.DATA_DIR / f"history_{name}.csv"
    txt_path = config.DATA_DIR / f"latest_update_{name}.txt"

    hist = history.load(csv_path)
    is_first_run = hist.empty
    count = 0 if is_first_run else config.FETCH_COUNT

    print(f"\n[{name}] {'初回: 全件取得' if is_first_run else f'差分チェック: 最新{count}件'}")

    latest = fetcher.fetch(url, count)
    if latest.empty:
        print(f"[{name}] 動画の取得に失敗しました。スキップします。")
        return

    new_videos = history.filter_new(latest, hist)
    print(f"[{name}] 新規: {len(new_videos)}件 / 取得: {len(latest)}件")

    history.append(new_videos, csv_path)
    output.write(new_videos, txt_path)


def main():
    print(f"YouTube URL Fetcher を開始します")
    print(f"データ保存先: {config.DATA_DIR}")

    for name, url in config.CHANNELS.items():
        try:
            process_channel(name, url)
        except Exception as e:
            print(f"[{name}] エラー: {e}")
            logging.error(f"[{name}] {e}")

    print("\n完了しました。")


if __name__ == "__main__":
    main()

    print("🏁 処理終了")


if __name__ == "__main__":
    main()
